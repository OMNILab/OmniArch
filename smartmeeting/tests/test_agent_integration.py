import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from smartmeeting.agent import create_graph
from smartmeeting.agent.state import AgentState


class TestAgentIntegration:
    """Integration tests for the complete agent workflow"""

    def setup_method(self):
        """Setup test data for each test method"""
        self.base_state = AgentState(
            messages=[], current_user_id=123, current_username="test_user"
        )

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    def test_agent_simple_conversation(
        self, mock_hitl_tools, mock_tools_by_name, mock_get_prompt, mock_llm
    ):
        """Test simple conversation without tool calls"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"
        mock_response = AIMessage(
            content="Hello! How can I help you book a meeting room?"
        )
        mock_llm.invoke.return_value = mock_response

        # Create graph
        graph = create_graph()

        # Add user message
        state = self.base_state.copy()
        state["messages"] = [HumanMessage(content="Hi")]

        # Run graph
        result = graph.invoke(state)

        # Verify result
        assert "messages" in result
        assert len(result["messages"]) >= 1

        # Verify LLM was called
        mock_llm.invoke.assert_called_once()

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_agent_with_safe_tool_call(
        self,
        mock_interrupt,
        mock_hitl_tools,
        mock_tools_by_name,
        mock_get_prompt,
        mock_llm,
    ):
        """Test agent workflow with safe tool call"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"

        # First call: LLM decides to use safe tool
        first_response = AIMessage(
            content="I'll search for available rooms",
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

        # Second call: LLM responds to tool result
        second_response = AIMessage(content="I found some rooms for you!")

        mock_llm.invoke.side_effect = [first_response, second_response]

        # Setup safe tool
        mock_hitl_tools.__contains__.return_value = False  # Safe tool
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "Found 2 available rooms"
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Create graph
        graph = create_graph()

        # Add user message
        state = self.base_state.copy()
        state["messages"] = [
            HumanMessage(content="I need a room for 5 people tomorrow at 2pm")
        ]

        # Run graph
        result = graph.invoke(state)

        # Verify result
        assert "messages" in result
        assert len(result["messages"]) >= 2

        # Verify tool was executed
        mock_tool.invoke.assert_called_once()

        # Verify LLM was called twice
        assert mock_llm.invoke.call_count == 2

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_agent_with_dangerous_tool_call_accept(
        self,
        mock_interrupt,
        mock_hitl_tools,
        mock_tools_by_name,
        mock_get_prompt,
        mock_llm,
    ):
        """Test agent workflow with dangerous tool call that user accepts"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"

        # First call: LLM decides to use dangerous tool
        first_response = AIMessage(
            content="I'll book the room for you",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "book_room",
                    "args": {
                        "room_id": 1,
                        "user_id": 123,
                        "start_time": "2025-01-16 14:00:00",
                        "end_time": "2025-01-16 15:00:00",
                        "title": "Test Meeting",
                    },
                }
            ],
        )

        # Second call: LLM responds to tool result
        second_response = AIMessage(content="Great! I've booked the room for you.")

        mock_llm.invoke.side_effect = [first_response, second_response]

        # Setup dangerous tool
        mock_hitl_tools.__contains__.return_value = True  # Dangerous tool
        mock_tool = MagicMock()
        mock_tool.invoke.return_value = "Booking successful"
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Mock interrupt response - user accepts
        mock_interrupt.return_value = [{"type": "accept"}]

        # Create graph
        graph = create_graph()

        # Add user message
        state = self.base_state.copy()
        state["messages"] = [HumanMessage(content="Book room 1 for me tomorrow at 2pm")]

        # Run graph
        result = graph.invoke(state)

        # Verify result
        assert "messages" in result
        assert len(result["messages"]) >= 2

        # Verify tool was executed after user acceptance
        mock_tool.invoke.assert_called_once()

        # Verify interrupt was called
        mock_interrupt.assert_called_once()

        # Verify LLM was called twice
        assert mock_llm.invoke.call_count == 2

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    @patch("smartmeeting.agent.nodes.interrupt")
    def test_agent_with_dangerous_tool_call_ignore(
        self,
        mock_interrupt,
        mock_hitl_tools,
        mock_tools_by_name,
        mock_get_prompt,
        mock_llm,
    ):
        """Test agent workflow with dangerous tool call that user ignores"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"

        # First call: LLM decides to use dangerous tool
        first_response = AIMessage(
            content="I'll book the room for you",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "book_room",
                    "args": {
                        "room_id": 1,
                        "user_id": 123,
                        "start_time": "2025-01-16 14:00:00",
                        "end_time": "2025-01-16 15:00:00",
                        "title": "Test Meeting",
                    },
                }
            ],
        )

        mock_llm.invoke.return_value = first_response

        # Setup dangerous tool
        mock_hitl_tools.__contains__.return_value = True  # Dangerous tool
        mock_tool = MagicMock()
        mock_tools_by_name.__getitem__.return_value = mock_tool

        # Mock interrupt response - user ignores
        mock_interrupt.return_value = [{"type": "ignore"}]

        # Create graph
        graph = create_graph()

        # Add user message
        state = self.base_state.copy()
        state["messages"] = [HumanMessage(content="Book room 1 for me tomorrow at 2pm")]

        # Run graph
        result = graph.invoke(state)

        # Verify result
        assert "messages" in result

        # Verify tool was NOT executed
        mock_tool.invoke.assert_not_called()

        # Verify interrupt was called
        mock_interrupt.assert_called_once()

        # Verify LLM was called once (no second call since user ignored)
        assert mock_llm.invoke.call_count == 1

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    def test_agent_state_persistence(self, mock_get_prompt, mock_llm):
        """Test that agent state is properly maintained across calls"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"
        mock_response = AIMessage(content="Hello!")
        mock_llm.invoke.return_value = mock_response

        # Create graph
        graph = create_graph()

        # Initial state
        state = self.base_state.copy()
        state["messages"] = [HumanMessage(content="Hi")]

        # First invocation
        result1 = graph.invoke(state)

        # Second invocation with same state
        result2 = graph.invoke(state)

        # Verify both results are consistent
        assert "messages" in result1
        assert "messages" in result2
        assert len(result1["messages"]) == len(result2["messages"])

        # Verify LLM was called twice
        assert mock_llm.invoke.call_count == 2

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    def test_agent_user_info_integration(self, mock_get_prompt, mock_llm):
        """Test that user information is properly integrated into the workflow"""
        # Setup mocks
        mock_get_prompt.return_value = "Test system prompt"
        mock_response = AIMessage(content="Hello!")
        mock_llm.invoke.return_value = mock_response

        # Create graph
        graph = create_graph()

        # State with user info
        state = AgentState(
            messages=[HumanMessage(content="Hi")],
            current_user_id=456,
            current_username="john_doe",
        )

        # Run graph
        result = graph.invoke(state)

        # Verify system prompt was called with correct user info
        mock_get_prompt.assert_called_with(456, "john_doe")

        # Verify result
        assert "messages" in result

    def test_agent_graph_structure(self):
        """Test that the agent graph has the correct structure"""
        # Create graph
        graph = create_graph()

        # Verify graph is callable
        assert callable(graph.invoke)

        # Verify graph has expected attributes
        assert hasattr(graph, "invoke")

    @patch("smartmeeting.agent.nodes.llm_with_tools")
    @patch("smartmeeting.agent.nodes.get_system_prompt")
    @patch("smartmeeting.agent.nodes.tools_by_name")
    @patch("smartmeeting.agent.nodes.hitl_tools")
    def test_agent_error_handling(
        self, mock_hitl_tools, mock_tools_by_name, mock_get_prompt, mock_llm
    ):
        """Test agent error handling"""
        # Setup mocks to raise exception
        mock_get_prompt.return_value = "Test system prompt"
        mock_llm.invoke.side_effect = Exception("LLM service unavailable")

        # Create graph
        graph = create_graph()

        # Add user message
        state = self.base_state.copy()
        state["messages"] = [HumanMessage(content="Hi")]

        # Test that exception is propagated
        with pytest.raises(Exception, match="LLM service unavailable"):
            graph.invoke(state)
