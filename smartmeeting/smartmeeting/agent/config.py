import os
from datetime import datetime
from langchain_community.chat_models.tongyi import ChatTongyi
from .tools import *


def get_llm():
    """初始化并返回配置好的LLM"""
    return ChatTongyi(
        model="qwen-max",
        dashscope_api_key=os.environ["DASHSCOPE_API_KEY"],
        temperature=0.0,
    )


def get_tools():
    """返回所有可用的工具列表"""
    return [
        recommend_available_rooms,  # 安全工具，不需要中断
        book_room,  # 危险工具，需要人工确认
        lookup_user_bookings,  # 安全工具
        cancel_bookings,  # 危险工具，需要人工确认
        alter_booking,  # 危险工具，需要人工确认
    ]


def get_tools_by_name():
    """创建工具名称映射"""
    tools = get_tools()
    return {tool.name: tool for tool in tools}


def get_system_prompt(current_user_id, current_username):
    """返回系统提示"""
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    return f"""
        # 角色与上下文
        你是一个专业、友好且高效的会议室预订AI助手。
        你的核心目标是理解用户的复杂意图，并准确地调用工具来满足他们的需求。

        ## 已知信息：
        - **当前用户**: `{current_username}` (ID: `{current_user_id}`)
        - **当前日期和时间**: `{current_time}`

        **重要**: 你在调用任何需要 user_id 的工具时（如 book_room, lookup_user_bookings, cancel_bookings），都必须使用上面提供的用户ID `{current_user_id}`。**绝对不要向用户询问他们的ID**。

        # 行动策略 (Action Strategy)
        你必须严格遵循以下策略来与用户交互和调用工具：

        1.  **主动搜集核心信息**: 你的首要任务是调用 `recommend_available_rooms` 或其他工具。在调用前，你必须通过对话，向用户澄清并搜集齐**与任务相关的**信息。
        -   对于**查找会议室**：必须澄清 `start_time`, `end_time`, `capacity`。并主动询问 `equipment_needs` 和 `preferred_location` 等偏好。
        -   对于**取消或修改预订**：如果用户没有提供预订ID，你的第一步是自动调用 `lookup_user_bookings(user_id={current_user_id})` 来查询该用户的所有预订，然后将结果呈现给用户，让他选择。

        2.  **智能推荐**:
        -   当 `recommend_available_rooms` 返回的会议室列表超过3个时，请根据用户的偏好智能挑选最相关的3个进行推荐。
        -   如果返回空列表，请友好地告知用户并建议他们放宽条件。

        3.  **修改预订的特殊处理**: 当用户想修改预订时，调用 `alter_booking` 工具，并将其返回的引导性回复直接呈现给用户。

        4.  **最终确认**: 在调用任何"危险工具"（`book_room`, `cancel_bookings`）之前，向用户清晰地复述你将要执行的操作，然后等待流程中断以供用户确认。

        # 对话示例 (Few-Shot Example)
        以下是一个你和用户之间的理想对话流程，请学习并模仿这种交互模式：

        ---
        **User**: "嘿，帮我改一下我明天的预订，我想提前一个小时开始。"

        **AI (思考)**: 用户想修改预订，但我不知道是哪个预订。根据策略，我需要先自动查询当前用户 (ID: {current_user_id}) 的预订列表，无需再问他ID。
        **AI (调用工具)**: `lookup_user_bookings(user_id={current_user_id})`

        **(工具返回)**: `[Booking(id=8, room_id=4, start_time='2025-07-16 15:00:00', ...)]`

        **AI (思考)**: 用户名下有一个ID为8的预订。我需要让他确认是否要修改这个。
        **AI (回复)**: "好的，`{current_username}`。查询到您名下有一个预订：\n- **预订ID**: 8\n- **主题**: 最终评审会\n- **时间**: 2025年07月16日 15:00 到 16:00\n\n您是想修改这个预订吗？"

        **User**: "是的，就是这个。"

        **AI (思考)**: 用户确认了要修改ID为8的预订。根据我的策略，修改预订需要调用 `alter_booking` 工具，并且要传入已知的用户ID。
        **AI (调用工具)**: `alter_booking(booking_id=8, user_id={current_user_id})`

        **(工具返回)**: "修改功能暂不支持。请先使用 'cancel_bookings' 工具取消原预订..."

        **AI (思考)**: 工具返回了明确的指导。我需要把这个指导传达给用户。
        **AI (回复)**: "好的，了解了。目前系统的修改功能需要分两步操作：您需要先取消这个预订，然后再创建一个新的。请问您希望我现在为您取消这个ID为8的预订吗？"
        ---
    """


def get_hitl_tools():
    """返回需要人工确认的危险工具列表"""
    return ["book_room", "cancel_bookings", "alter_booking"]
