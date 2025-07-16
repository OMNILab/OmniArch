from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import AgentState
from .nodes import llm_call, interrupt_handler, should_continue


def build_agent_graph():
    """构建并返回编译好的 Agent 图"""

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

    # 从 interrupt_handler 返回到 llm_call 以继续对话
    # 这个边由 Command 的 goto 参数控制，无需显式添加

    # 编译图
    checkpointer = InMemorySaver()
    graph = agent_builder.compile(checkpointer=checkpointer)

    print("✅ Agent 图编译完成！")
    print("🔧 采用基于 Command 和 interrupt 的 HITL 模式")
    print("⚠️  危险工具: book_room, cancel_bookings, alter_booking")
    print("✅ 安全工具: recommend_available_rooms, lookup_user_bookings")

    return graph
