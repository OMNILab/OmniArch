from .graph import build_agent_graph


def create_graph(checkpointer=None):
    """
    创建并返回编译好的 Agent 图，供 Streamlit 使用

    Args:
        checkpointer: 可选的检查点保存器，如果提供则使用，否则使用默认的InMemorySaver

    Returns:
        编译好的 LangGraph
    """
    if checkpointer is None:
        return build_agent_graph()
    else:
        # 如果提供了外部checkpointer，需要修改build_agent_graph函数
        from langgraph.graph import StateGraph, START, END
        from .state import AgentState
        from .nodes import llm_call, interrupt_handler, should_continue

        # 构建 Agent 图
        agent_builder = StateGraph(AgentState)

        # 添加节点
        agent_builder.add_node("llm_call", llm_call)
        agent_builder.add_node("interrupt_handler", interrupt_handler)

        # 添加边
        agent_builder.add_edge(START, "llm_call")
        agent_builder.add_conditional_edges(
            "llm_call",
            should_continue,
            {
                "interrupt_handler": "interrupt_handler",
                "__end__": "__end__",
            },
        )

        # 编译图
        graph = agent_builder.compile(checkpointer=checkpointer)
        return graph
