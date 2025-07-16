import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from smartmeeting.agent.nodes import llm_call, interrupt_handler, should_continue
from smartmeeting.agent.state import AgentState


class TestAgentNodes:
    """Test cases for agent nodes"""

    def setup_method(self):
        """Setup test data for each test method"""
        self.base_state = AgentState(
            messages=[], current_user_id=123, current_username="test_user"
        )

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    def test_llm_call_basic(self, mock_get_prompt, mock_llm):
        """Test basic LLM call node"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"
        mock_response = AIMessage(content="Hello!")
        mock_llm.invoke.return_value = mock_response

        # Add a user message to state
        state = self.base_state.copy()
        state["messages"] = [HumanMessage(content="Hi")]

        # Test LLM call
        result = llm_call(state)

        # Verify result
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0] == mock_response

        # Verify LLM was called with correct messages
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        assert len(call_args) == 2  # System message + user message
        assert call_args[0]["role"] == "system"
        assert call_args[0]["content"] == "Test system prompt"

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    def test_llm_call_with_tool_calls(self, mock_get_prompt, mock_llm):
        """Test LLM call with tool calls in response"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"
        mock_response = AIMessage(
            content="I'll help you book a room",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "recommend_available_rooms",
                    "args": {
                        "start_time": "2025-01-16 14:00:00",
                        "end_time": "2025-01-16 15:00:00",
                        "capacity": 5,
                    },
                }
            ],
        )
        mock_llm.invoke.return_value = mock_response

        # Test LLM call
        result = llm_call(state=self.base_state)

        # Verify result
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0] == mock_response
        assert len(result["messages"][0].tool_calls) == 1

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    def test_llm_call_default_user_info(self, mock_get_prompt, mock_llm):
        """Test LLM call with default user info when not provided"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"
        mock_response = AIMessage(content="Hello!")
        mock_llm.invoke.return_value = mock_response

        # State without user info
        state = AgentState(messages=[], current_user_id=None, current_username=None)

        # Test LLM call
        result = llm_call(state)

        # Verify that default values are used
        mock_get_prompt.assert_called_with(1, "用户")  # Default values

    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    def test_interrupt_handler_safe_tool(self, mock_hitl_tools, mock_tools_by_name):
        """Test interrupt handler with safe tool"""
        # Setup mocks
        mock_hitl_tools.__contains__.return_value = False  # Safe tool
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "Room found: 会议室A"
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Create state with tool call
        state = self.base_state.copy()
        state["messages"] = [
            AIMessage(
                content="I'll search for rooms",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "recommend_available_rooms",
                        "args": {
                            "start_time": "2025-01-16 14:00:00",
                            "end_time": "2025-01-16 15:00:00",
                            "capacity": 5,
                        },
                    }
                ],
            )
        ]

        # Test interrupt handler
        result = interrupt_handler(state)

        # Should return Command to continue to llm_call
        assert isinstance(result, Command)
        assert result.goto == "llm_call"
        assert "messages" in result.update

        # Verify tool was executed
        mock_tool.invoke.assert_called_once()

    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_interrupt_handler_dangerous_tool_accept(
        self, mock_interrupt, mock_hitl_tools, mock_tools_by_name
    ):
        """Test interrupt handler with dangerous tool - user accepts"""
        # Setup mocks
        mock_hitl_tools.__contains__.return_value = True  # Dangerous tool
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "Booking successful"
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Mock interrupt response - user accepts
        mock_interrupt.return_value = [{"type": "accept"}]

        # Create state with dangerous tool call
        state = self.base_state.copy()
        state["messages"] = [
            AIMessage(
                content="I'll book the room",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "book_room",
                        "args": {
                            "room_id": 1,
                            "user_id": 123,
                            "start_time": "2025-01-16 14:00:00",
                            "end_time": "2025-01-16 15:00:00",
                            "title": "Test",
                        },
                    }
                ],
            )
        ]

        # Test interrupt handler
        result = interrupt_handler(state)

        # Should return Command to continue to llm_call
        assert isinstance(result, Command)
        assert result.goto == "llm_call"

        # Verify tool was executed after user acceptance
        mock_tool.invoke.assert_called_once()

    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_interrupt_handler_dangerous_tool_ignore(
        self, mock_interrupt, mock_hitl_tools, mock_tools_by_name
    ):
        """Test interrupt handler with dangerous tool - user ignores"""
        # Setup mocks
        mock_hitl_tools.__contains__.return_value = True  # Dangerous tool
        mock_tool = MagicMock()
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Mock interrupt response - user ignores
        mock_interrupt.return_value = [{"type": "ignore"}]

        # Create state with dangerous tool call
        state = self.base_state.copy()
        state["messages"] = [
            AIMessage(
                content="I'll book the room",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "book_room",
                        "args": {
                            "room_id": 1,
                            "user_id": 123,
                            "start_time": "2025-01-16 14:00:00",
                            "end_time": "2025-01-16 15:00:00",
                            "title": "Test",
                        },
                    }
                ],
            )
        ]

        # Test interrupt handler
        result = interrupt_handler(state)

        # Should return Command to end
        assert isinstance(result, Command)
        assert result.goto == "__end__"

        # Verify tool was NOT executed
        mock_tool.invoke.assert_not_called()

    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_interrupt_handler_dangerous_tool_edit(
        self, mock_interrupt, mock_hitl_tools, mock_tools_by_name
    ):
        """Test interrupt handler with dangerous tool - user edits"""
        # Setup mocks
        mock_hitl_tools.__contains__.return_value = True  # Dangerous tool
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "Booking successful with edited params"
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Mock interrupt response - user edits
        edited_args = {
            "room_id": 2,
            "user_id": 123,
            "start_time": "2025-01-16 15:00:00",
            "end_time": "2025-01-16 16:00:00",
            "title": "Edited Test",
        }
        mock_interrupt.return_value = [{"type": "edit", "args": {"args": edited_args}}]

        # Create state with dangerous tool call
        state = self.base_state.copy()
        state["messages"] = [
            AIMessage(
                content="I'll book the room",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "book_room",
                        "args": {
                            "room_id": 1,
                            "user_id": 123,
                            "start_time": "2025-01-16 14:00:00",
                            "end_time": "2025-01-16 15:00:00",
                            "title": "Test",
                        },
                    }
                ],
            )
        ]

        # Test interrupt handler
        result = interrupt_handler(state)

        # Should return Command to continue to llm_call
        assert isinstance(result, Command)
        assert result.goto == "llm_call"

        # Verify tool was executed with edited args
        mock_tool.invoke.assert_called_once_with(edited_args)

    def test_should_continue_with_tool_calls(self):
        """Test should_continue when message has tool calls"""
        # Create state with tool calls
        state = self.base_state.copy()
        state["messages"] = [
            AIMessage(
                content="I'll help you",
                tool_calls=[{"id": "call_1", "name": "test_tool", "args": {}}],
            )
        ]

        result = should_continue(state)

        # Should continue to interrupt handler
        assert result == "interrupt_handler"

    def test_should_continue_without_tool_calls(self):
        """Test should_continue when message has no tool calls"""
        # Create state without tool calls
        state = self.base_state.copy()
        state["messages"] = [AIMessage(content="Hello, how can I help you?")]

        result = should_continue(state)

        # Should end
        assert result == "__end__"

    def test_should_continue_empty_messages(self):
        """Test should_continue with empty messages"""
        # Create state with empty messages
        state = self.base_state.copy()
        state["messages"] = []

        # This should raise an error since we're trying to access the last message
        with pytest.raises(IndexError):
            should_continue(state)

    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_interrupt_handler_unknown_response_type(
        self, mock_interrupt, mock_hitl_tools, mock_tools_by_name
    ):
        """Test interrupt handler with unknown response type"""
        # Setup mocks
        mock_hitl_tools.__contains__.return_value = True  # Dangerous tool
        mock_tools_by_name.__getitem__.return_value = MagicMock()

        # Mock interrupt response - unknown type
        mock_interrupt.return_value = [{"type": "unknown_type"}]

        # Create state with dangerous tool call
        state = self.base_state.copy()
        state["messages"] = [
            AIMessage(
                content="I'll book the room",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "book_room",
                        "args": {
                            "room_id": 1,
                            "user_id": 123,
                            "start_time": "2025-01-16 14:00:00",
                            "end_time": "2025-01-16 15:00:00",
                            "title": "Test",
                        },
                    }
                ],
            )
        ]

        # Test interrupt handler - should raise ValueError
        with pytest.raises(ValueError, match="未知的响应类型"):
            interrupt_handler(state)
