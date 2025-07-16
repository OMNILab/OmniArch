"""
Simple smoke tests for the agent module to verify basic functionality
"""


def test_agent_imports():
    """Test that all agent modules can be imported successfully"""
    try:
        from smartmeeting.agent import create_graph
        from smartmeeting.agent.state import AgentState
        from smartmeeting.agent.config import get_llm, get_tools, get_system_prompt
        from smartmeeting.agent.tools import recommend_available_rooms, book_room
        from smartmeeting.agent.nodes import (
            llm_call,
            interrupt_handler,
            should_continue,
        )
        from smartmeeting.agent.graph import build_agent_graph

        assert True, "All imports successful"
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_agent_state_creation():
    """Test basic AgentState creation"""
    from smartmeeting.agent.state import AgentState

    state = AgentState(messages=[], current_user_id=1, current_username="test")

    assert state["current_user_id"] == 1
    assert state["current_username"] == "test"
    assert state["messages"] == []


def test_agent_config_functions():
    """Test that config functions return expected types"""
    from smartmeeting.agent.config import get_tools, get_hitl_tools, get_system_prompt

    # Test tools list
    tools = get_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0

    # Test HITL tools
    hitl_tools = get_hitl_tools()
    assert isinstance(hitl_tools, list)
    assert len(hitl_tools) > 0

    # Test system prompt
    prompt = get_system_prompt(1, "test_user")
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_agent_tools_exist():
    """Test that all expected tools are available"""
    from smartmeeting.agent.tools import (
        recommend_available_rooms,
        book_room,
        lookup_user_bookings,
        cancel_bookings,
        alter_booking,
    )

    # Verify all tools are callable
    assert callable(recommend_available_rooms)
    assert callable(book_room)
    assert callable(lookup_user_bookings)
    assert callable(cancel_bookings)
    assert callable(alter_booking)


def test_agent_graph_creation():
    """Test that agent graph can be created"""
    from smartmeeting.agent import create_graph

    try:
        graph = create_graph()
        assert graph is not None
        assert hasattr(graph, "invoke")
        assert callable(graph.invoke)
    except Exception as e:
        # Graph creation might fail due to missing API keys, but should not crash
        assert "DASHSCOPE_API_KEY" in str(e) or "API key" in str(e)


def test_agent_module_structure():
    """Test that agent module has expected structure"""
    import smartmeeting.agent

    # Check that main functions exist
    assert hasattr(smartmeeting.agent, "create_graph")
    assert callable(smartmeeting.agent.create_graph)

    # Check that submodules exist
    assert hasattr(smartmeeting.agent, "state")
    assert hasattr(smartmeeting.agent, "config")
    assert hasattr(smartmeeting.agent, "tools")
    assert hasattr(smartmeeting.agent, "nodes")
    assert hasattr(smartmeeting.agent, "graph")


if __name__ == "__main__":
    # Run simple tests
    print("🧪 Running agent module smoke tests...")

    tests = [
        test_agent_imports,
        test_agent_state_creation,
        test_agent_config_functions,
        test_agent_tools_exist,
        test_agent_graph_creation,
        test_agent_module_structure,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All smoke tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
