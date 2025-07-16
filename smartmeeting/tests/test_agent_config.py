import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from smartmeeting.agent.config import (
    get_llm,
    get_tools,
    get_tools_by_name,
    get_system_prompt,
    get_hitl_tools,
)


class TestAgentConfig:
    """Test cases for agent configuration module"""

    @patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test_key"})
    def test_get_llm(self):
        """Test LLM initialization"""
        with patch("smartmeeting.agent.config.ChatTongyi") as mock_chat_tongyi:
            mock_llm = MagicMock()
            mock_chat_tongyi.return_value = mock_llm

            llm = get_llm()

            mock_chat_tongyi.assert_called_once_with(
                model="qwen-max", dashscope_api_key="test_key", temperature=0.0
            )
            assert llm == mock_llm

    def test_get_llm_missing_api_key(self):
        """Test LLM initialization with missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyError):
                get_llm()

    def test_get_tools(self):
        """Test tools list generation"""
        tools = get_tools()

        # Check that we get a list of tools
        assert isinstance(tools, list)
        assert len(tools) >= 4  # Should have at least 4 tools

        # Check that all tools have names
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "recommend_available_rooms",
            "book_room",
            "lookup_user_bookings",
            "cancel_bookings",
            "alter_booking",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_get_tools_by_name(self):
        """Test tools by name mapping"""
        tools_by_name = get_tools_by_name()

        assert isinstance(tools_by_name, dict)

        # Check that all expected tools are present
        expected_tools = [
            "recommend_available_rooms",
            "book_room",
            "lookup_user_bookings",
            "cancel_bookings",
            "alter_booking",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools_by_name
            assert hasattr(tools_by_name[tool_name], "name")
            assert tools_by_name[tool_name].name == tool_name

    def test_get_system_prompt(self):
        """Test system prompt generation"""
        user_id = 123
        username = "test_user"

        prompt = get_system_prompt(user_id, username)

        # Check that prompt contains expected elements
        assert isinstance(prompt, str)
        assert str(user_id) in prompt
        assert username in prompt
        assert "会议室预订AI助手" in prompt
        assert "当前用户" in prompt
        assert "当前日期和时间" in prompt

    def test_get_system_prompt_with_special_characters(self):
        """Test system prompt with special characters in username"""
        user_id = 456
        username = "test_user@company.com"

        prompt = get_system_prompt(user_id, username)

        assert str(user_id) in prompt
        assert username in prompt

    def test_get_hitl_tools(self):
        """Test HITL tools list"""
        hitl_tools = get_hitl_tools()

        assert isinstance(hitl_tools, list)
        expected_dangerous_tools = ["book_room", "cancel_bookings", "alter_booking"]

        for tool in expected_dangerous_tools:
            assert tool in hitl_tools

    def test_system_prompt_current_time(self):
        """Test that system prompt includes current time"""
        prompt = get_system_prompt(1, "test")

        # Check that current date format is included
        current_year = str(datetime.now().year)
        assert current_year in prompt

        # Check for time format pattern
        assert "年" in prompt
        assert "月" in prompt
        assert "日" in prompt
