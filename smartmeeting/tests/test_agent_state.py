import pytest
from typing import List, Optional
from smartmeeting.agent.state import AgentState


class TestAgentState:
    """Test cases for AgentState TypedDict"""

    def test_agent_state_creation(self):
        """Test creating a valid AgentState"""
        state = AgentState(messages=[], current_user_id=1, current_username="test_user")

        assert state["messages"] == []
        assert state["current_user_id"] == 1
        assert state["current_username"] == "test_user"

    def test_agent_state_with_none_values(self):
        """Test creating AgentState with None values for optional fields"""
        state = AgentState(messages=[], current_user_id=None, current_username=None)

        assert state["messages"] == []
        assert state["current_user_id"] is None
        assert state["current_username"] is None

    def test_agent_state_with_messages(self):
        """Test AgentState with actual messages"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        state = AgentState(
            messages=messages, current_user_id=1, current_username="test_user"
        )

        assert state["messages"] == messages
        assert len(state["messages"]) == 2

    def test_agent_state_type_annotations(self):
        """Test that AgentState has correct type annotations"""
        from typing import get_type_hints

        hints = get_type_hints(AgentState)

        assert "messages" in hints
        assert "current_user_id" in hints
        assert "current_username" in hints

        # Check that current_user_id and current_username are Optional
        assert str(hints["current_user_id"]).startswith("Optional")
        assert str(hints["current_username"]).startswith("Optional")
