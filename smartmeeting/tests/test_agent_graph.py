import pytest
from unittest.mock import patch, MagicMock
from smartmeeting.agent.graph import build_agent_graph
from smartmeeting.agent import create_graph


class TestAgentGraph:
    """Test cases for agent graph module"""

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_build_agent_graph(self, mock_saver, mock_state_graph):
        """Test building the agent graph"""
        # Setup mocks
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder

        mock_checkpointer = MagicMock()
        mock_saver.return_value = mock_checkpointer

        mock_compiled_graph = MagicMock()
        mock_graph_builder.compile.return_value = mock_compiled_graph

        # Test graph building
        result = build_agent_graph()

        # Verify result
        assert result == mock_compiled_graph

        # Verify StateGraph was created
        mock_state_graph.assert_called_once()

        # Verify nodes were added
        mock_graph_builder.add_node.assert_any_call(
            "llm_call", mock_graph_builder.add_node.call_args_list[0][0][1]
        )
        mock_graph_builder.add_node.assert_any_call(
            "interrupt_handler", mock_graph_builder.add_node.call_args_list[1][0][1]
        )

        # Verify edges were added
        mock_graph_builder.add_edge.assert_called()
        mock_graph_builder.add_conditional_edges.assert_called()

        # Verify graph was compiled with checkpointer
        mock_graph_builder.compile.assert_called_once_with(
            checkpointer=mock_checkpointer
        )

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_build_agent_graph_node_verification(self, mock_saver, mock_state_graph):
        """Test that all required nodes are added to the graph"""
        # Setup mocks
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder

        mock_checkpointer = MagicMock()
        mock_saver.return_value = mock_checkpointer

        mock_compiled_graph = MagicMock()
        mock_graph_builder.compile.return_value = mock_compiled_graph

        # Test graph building
        build_agent_graph()

        # Verify all required nodes were added
        add_node_calls = mock_graph_builder.add_node.call_args_list
        node_names = [call[0][0] for call in add_node_calls]

        assert "llm_call" in node_names
        assert "interrupt_handler" in node_names
        assert len(node_names) == 2

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_build_agent_graph_edge_verification(self, mock_saver, mock_state_graph):
        """Test that all required edges are added to the graph"""
        # Setup mocks
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder

        mock_checkpointer = MagicMock()
        mock_saver.return_value = mock_checkpointer

        mock_compiled_graph = MagicMock()
        mock_graph_builder.compile.return_value = mock_compiled_graph

        # Test graph building
        build_agent_graph()

        # Verify edges were added
        mock_graph_builder.add_edge.assert_called()
        mock_graph_builder.add_conditional_edges.assert_called()

        # Verify conditional edges configuration
        conditional_edges_call = mock_graph_builder.add_conditional_edges.call_args
        assert conditional_edges_call[0][0] == "llm_call"  # Source node
        assert conditional_edges_call[0][2] == {
            "interrupt_handler": "interrupt_handler",
            "__end__": "__end__",
        }

    @patch("smartmeeting.agent.graph.build_agent_graph")
    def test_create_graph_default(self, mock_build_graph):
        """Test create_graph function with default parameters"""
        # Setup mock
        mock_graph = MagicMock()
        mock_build_graph.return_value = mock_graph

        # Test with no checkpointer
        result = create_graph()

        # Verify result
        assert result == mock_graph

        # Verify build_agent_graph was called
        mock_build_graph.assert_called_once()

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_create_graph_with_checkpointer(self, mock_saver, mock_state_graph):
        """Test create_graph function with custom checkpointer"""
        # Setup mocks
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder

        mock_checkpointer = MagicMock()
        mock_compiled_graph = MagicMock()
        mock_graph_builder.compile.return_value = mock_compiled_graph

        # Test with custom checkpointer
        custom_checkpointer = MagicMock()
        result = create_graph(checkpointer=custom_checkpointer)

        # Verify result
        assert result == mock_compiled_graph

        # Verify graph was compiled with custom checkpointer
        mock_graph_builder.compile.assert_called_once_with(
            checkpointer=custom_checkpointer
        )

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_create_graph_with_checkpointer_node_verification(
        self, mock_saver, mock_state_graph
    ):
        """Test that create_graph with checkpointer adds all required nodes"""
        # Setup mocks
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder

        mock_checkpointer = MagicMock()
        mock_compiled_graph = MagicMock()
        mock_graph_builder.compile.return_value = mock_compiled_graph

        # Test with custom checkpointer
        custom_checkpointer = MagicMock()
        create_graph(checkpointer=custom_checkpointer)

        # Verify all required nodes were added
        add_node_calls = mock_graph_builder.add_node.call_args_list
        node_names = [call[0][0] for call in add_node_calls]

        assert "llm_call" in node_names
        assert "interrupt_handler" in node_names
        assert len(node_names) == 2

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_create_graph_with_checkpointer_edge_verification(
        self, mock_saver, mock_state_graph
    ):
        """Test that create_graph with checkpointer adds all required edges"""
        # Setup mocks
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder

        mock_checkpointer = MagicMock()
        mock_compiled_graph = MagicMock()
        mock_graph_builder.compile.return_value = mock_compiled_graph

        # Test with custom checkpointer
        custom_checkpointer = MagicMock()
        create_graph(checkpointer=custom_checkpointer)

        # Verify edges were added
        mock_graph_builder.add_edge.assert_called()
        mock_graph_builder.add_conditional_edges.assert_called()

        # Verify conditional edges configuration
        conditional_edges_call = mock_graph_builder.add_conditional_edges.call_args
        assert conditional_edges_call[0][0] == "llm_call"  # Source node
        assert conditional_edges_call[0][2] == {
            "interrupt_handler": "interrupt_handler",
            "__end__": "__end__",
        }

    def test_build_agent_graph_imports(self):
        """Test that all required imports are available"""
        # Test that we can import the required modules
        from smartmeeting.agent.graph import StateGraph, START, END
        from smartmeeting.agent.graph import InMemorySaver
        from smartmeeting.agent.state import AgentState
        from smartmeeting.agent.nodes import (
            llm_call,
            interrupt_handler,
            should_continue,
        )

        # If we get here, imports are working
        assert True

    @patch("smartmeeting.agent.graph.StateGraph")
    @patch("smartmeeting.agent.graph.InMemorySaver")
    def test_build_agent_graph_error_handling(self, mock_saver, mock_state_graph):
        """Test error handling in graph building"""
        # Setup mock to raise exception
        mock_graph_builder = MagicMock()
        mock_state_graph.return_value = mock_graph_builder
        mock_graph_builder.add_node.side_effect = Exception("Node addition failed")

        # Test that exception is propagated
        with pytest.raises(Exception, match="Node addition failed"):
            build_agent_graph()
