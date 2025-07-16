from typing import Literal
from langgraph.types import interrupt, Command
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from .state import AgentState
from .config import (
    get_llm,
    get_tools,
    get_system_prompt,
    get_hitl_tools,
    get_tools_by_name,
)
import streamlit as st

# 获取配置（除了系统提示，它需要用户信息）
llm = get_llm()
tools = get_tools()
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")
hitl_tools = get_hitl_tools()
tools_by_name = get_tools_by_name()


def llm_call(state: AgentState) -> dict:
    """LLM 调用节点 - 生成工具调用"""
    print("---NODE: LLM CALL---")

    # 获取用户信息，如果没有则使用默认值
    current_user_id = state.get("current_user_id", 1)
    current_username = state.get("current_username", "用户")

    # 动态生成系统提示
    system_prompt = get_system_prompt(current_user_id, current_username)

    messages = [{"role": "system", "content": system_prompt}] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


def interrupt_handler(state: AgentState) -> Command[Literal["llm_call", "__end__"]]:
    """中断处理器 - 检查工具调用并决定是否需要人工干预"""
    print("---NODE: INTERRUPT HANDLER---")

    # 存储结果
    result = []
    goto = "llm_call"  # 默认返回 LLM 调用

    # 获取最后一条消息中的工具调用
    last_message = state["messages"][-1]

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]

        # 如果是安全工具，直接执行
        if tool_name not in hitl_tools:
            print(f"✅ 安全工具 '{tool_name}' - 直接执行")
            tool = tools_by_name[tool_name]
            observation = tool.invoke(tool_call["args"])
            result.append(
                {
                    "role": "tool",
                    "content": str(observation),
                    "tool_call_id": tool_call["id"],
                }
            )
            continue

        # 危险工具需要人工确认
        print(f"⚠️ 危险工具 '{tool_name}' - 需要人工确认")

        # 创建中断请求
        request = {
            "action_request": {"action": tool_name, "args": tool_call["args"]},
            "config": {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True,
            },
            "description": f"**工具**: {tool_name}\n**参数**: {tool_call['args']}\n\n请确认是否执行此操作。",
        }

        # 发送中断并等待响应
        response = interrupt([request])[0]
        st.write(response)
        # 处理响应
        if response["type"] == "accept":
            print("✅ 用户确认执行")
            tool = tools_by_name[tool_name]
            observation = tool.invoke(tool_call["args"])
            result.append(
                {
                    "role": "tool",
                    "content": str(observation),
                    "tool_call_id": tool_call["id"],
                }
            )

        elif response["type"] == "edit":
            print("✏️ 用户编辑参数")
            tool = tools_by_name[tool_name]
            edited_args = response["args"]["args"]

            # 更新工具调用参数
            updated_tool_calls = [
                tc for tc in last_message.tool_calls if tc["id"] != tool_call["id"]
            ] + [
                {
                    "type": "tool_call",
                    "name": tool_name,
                    "args": edited_args,
                    "id": tool_call["id"],
                }
            ]

            # 更新消息
            result.append(
                last_message.model_copy(update={"tool_calls": updated_tool_calls})
            )

            # 执行编辑后的工具
            observation = tool.invoke(edited_args)
            result.append(
                {
                    "role": "tool",
                    "content": observation,
                    "tool_call_id": tool_call["id"],
                }
            )

        elif response["type"] == "ignore":
            print("🚫 用户取消操作")
            result.append(
                {
                    "role": "tool",
                    "content": f"用户取消了 {tool_name} 操作。",
                    "tool_call_id": tool_call["id"],
                }
            )
            goto = "__end__"

        elif response["type"] == "response":
            print("💬 用户提供反馈")
            user_feedback = response["args"]
            result.append(
                {
                    "role": "tool",
                    "content": f"用户反馈：{user_feedback}。请根据反馈调整操作。",
                    "tool_call_id": tool_call["id"],
                }
            )

        else:
            raise ValueError(f"未知的响应类型: {response['type']}")

    return Command(goto=goto, update={"messages": result})


def should_continue(state: AgentState) -> Literal["interrupt_handler", "__end__"]:
    """决定是否继续到中断处理器或结束"""
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "interrupt_handler"
    else:
        return "__end__"
