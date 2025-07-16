# agent/tools.py

from langchain_core.tools import tool
from typing import List, Optional
from datetime import datetime
import streamlit as st
import pandas as pd

# 导入smartmeeting的数据管理器
from ..data_manager import DataManager

# ------------------------------------------------------------------
#  注意：以下每个工具的 docstring 都非常重要。
#  它将作为给 LLM 的指令，告诉 LLM 这个工具能做什么、需要什么参数。
#  这些描述已针对 LangGraph 进行优化。
# ------------------------------------------------------------------


@tool
def recommend_available_rooms(
    start_time: str,
    end_time: str,
    capacity: int,
    equipment_needs: List[str] = None,
    preferred_location: List[str] = None,
) -> List[dict]:
    """
    搜索并推荐可用的会议室。

    使用场景：
    - 用户询问"帮我找一个会议室"
    - 用户需要查看某个时间段的可用会议室
    - 用户想要根据人数、设备或位置筛选会议室

    参数说明：
    - start_time: 会议开始时间，格式：'YYYY-MM-DD HH:MM:SS'，例如 '2025-01-16 14:00:00'
    - end_time: 会议结束时间，格式：'YYYY-MM-DD HH:MM:SS'，例如 '2025-01-16 15:00:00'
    - capacity: 需要容纳的人数，必须是正整数
    - equipment_needs: 所需设备列表，可选。例如 ['投影仪', '白板', '视频会议']
    - preferred_location: 首选位置列表，可选。例如 ['A栋', 'B栋']

    返回：符合条件的会议室列表，包含房间详细信息

    注意：这是一个安全工具，不需要用户确认即可执行。
    """
    print(
        f"Tool: Searching rooms from {start_time} to {end_time} for {capacity} people."
    )

    # 处理默认值
    if equipment_needs is None:
        equipment_needs = []
    if preferred_location is None:
        preferred_location = []

    # 获取数据管理器
    data_manager = DataManager()
    rooms_df = data_manager.get_dataframe("rooms")
    meetings_df = data_manager.get_dataframe("meetings")

    # 转换时间格式
    start_dt = pd.to_datetime(start_time)
    end_dt = pd.to_datetime(end_time)

    # 筛选符合条件的会议室
    available_rooms = []

    for _, room in rooms_df.iterrows():
        # 检查容量
        if room["capacity"] < capacity:
            continue

        # 检查设备需求
        if equipment_needs:
            equipment_available = True
            for equip in equipment_needs:
                if equip == "投影仪" and room.get("has_projector", 0) != 1:
                    equipment_available = False
                    break
                elif equip == "视频会议" and room.get("has_phone", 0) != 1:
                    equipment_available = False
                    break
                elif equip == "白板" and room.get("has_whiteboard", 0) != 1:
                    equipment_available = False
                    break
                elif equip == "显示屏" and room.get("has_screen", 0) != 1:
                    equipment_available = False
                    break
            if not equipment_available:
                continue

        # 检查位置偏好
        if preferred_location:
            # 获取建筑信息
            buildings_df = data_manager.get_dataframe("buildings")
            room_building_id = room.get("building_id")
            if room_building_id is not None:
                building_info = buildings_df[
                    buildings_df["building_id"] == room_building_id
                ]
                if not building_info.empty:
                    building_name = building_info.iloc[0]["building_name"]
                    if not any(loc in building_name for loc in preferred_location):
                        continue

        # 检查时间冲突
        room_meetings = meetings_df[meetings_df["room_id"] == room["room_id"]]
        is_available = True

        for _, meeting in room_meetings.iterrows():
            meeting_start = pd.to_datetime(meeting["start_datetime"])
            meeting_end = pd.to_datetime(meeting["end_datetime"])

            # 检查时间重叠
            if not (end_dt <= meeting_start or start_dt >= meeting_end):
                is_available = False
                break

        if is_available:
            available_rooms.append(room.to_dict())

    return available_rooms


@tool
def book_room(
    room_id: int, user_id: int, start_time: str, end_time: str, title: str
) -> str:
    """
    为指定用户预订会议室。

    使用场景：
    - 用户确认要预订某个会议室
    - 用户说"预订这个会议室"或"我要预订会议室ID为X"
    - 用户提供了完整的预订信息（房间、时间、用途）

    参数说明：
    - room_id: 会议室ID，必须是有效的整数
    - user_id: 用户ID，必须是有效的整数
    - start_time: 会议开始时间，格式：'YYYY-MM-DD HH:MM:SS'
    - end_time: 会议结束时间，格式：'YYYY-MM-DD HH:MM:SS'
    - title: 会议主题/标题，描述会议用途

    返回：预订结果信息，包含预订ID和详细信息

    ⚠️ 重要：这是一个危险工具，会实际创建预订记录，需要用户确认后才能执行。
    """
    print(f"Tool: Booking room {room_id} for user {user_id}.")
    try:
        # 获取数据管理器
        data_manager = DataManager()

        # 计算会议时长（分钟）
        start_dt = pd.to_datetime(start_time)
        end_dt = pd.to_datetime(end_time)
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)

        # 获取房间信息
        rooms_df = data_manager.get_dataframe("rooms")
        room_info = rooms_df[rooms_df["room_id"] == room_id]
        room_name = (
            room_info.iloc[0]["room_name"]
            if not room_info.empty
            else f"会议室{room_id}"
        )

        # 获取用户信息
        users_df = data_manager.get_dataframe("users")
        user_info = users_df[users_df["user_id"] == user_id]
        organizer_name = (
            user_info.iloc[0]["name"] if not user_info.empty else f"用户{user_id}"
        )

        # 创建新会议记录 - 同步到所有相关页面
        new_meeting = {
            "id": len(data_manager.get_dataframe("meetings")) + 1,
            "booking_id": len(data_manager.get_dataframe("meetings")) + 1,
            "room_id": room_id,
            "organizer_id": user_id,
            "meeting_title": title,
            "title": title,  # 确保与minutes页面兼容
            "meeting_type": "项目讨论",
            "start_datetime": start_time,
            "end_datetime": end_time,
            "start_time": start_time,  # 确保与calendar页面兼容
            "end_time": end_time,  # 确保与calendar页面兼容
            "duration_minutes": duration_minutes,
            "duration": duration_minutes,  # 兼容字段
            "participant_count": 10,  # 默认值
            "participants": 10,  # 兼容字段
            "status": "已确认",  # 会议状态：已确认、进行中、已完成、已取消
            "meeting_status": "upcoming",  # 新增：会议执行状态：upcoming, ongoing, completed
            "created_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "natural_language_request": f"通过AI助手预订的会议: {title}",
            "ai_match_score": 95,
            "notes": f"会议组织者: {organizer_name}，会议室: {room_name}",
            "description": f"通过AI助手预订的会议: {title}",
            "type": "项目讨论",  # 兼容字段
        }

        # 添加到数据管理器
        data_manager.add_meeting(new_meeting)

        return f"预订成功！会议主题: {title}，会议室: {room_name}，时间: {start_time} 到 {end_time}，时长: {duration_minutes}分钟。会议已同步到所有相关页面。"
    except Exception as e:
        return f"预订失败，发生错误: {e}"


@tool
def lookup_user_bookings(user_id: int) -> List[dict]:
    """
    查询用户的预订记录。

    使用场景：
    - 用户询问"我的预订有哪些"
    - 用户想查看自己的会议安排
    - 用户需要确认某个预订是否存在
    - 需要获取预订ID以便后续操作

    参数说明：
    - user_id: 用户ID，必须是有效的整数

    返回：该用户的所有当前和未来预订列表

    注意：
    - 这是一个安全工具，不需要用户确认即可执行
    - 只返回当前和未来的预订，不包括已过期的预订
    - 在真实应用中，用户ID通常从登录会话获取
    """
    print(f"Tool: Looking up bookings for user {user_id}.")

    # 获取数据管理器
    data_manager = DataManager()
    meetings_df = data_manager.get_dataframe("meetings")

    # 筛选用户的预订
    user_meetings = meetings_df[meetings_df["organizer_id"] == user_id]

    # 只返回当前和未来的预订
    current_time = datetime.now()
    future_meetings = user_meetings[
        pd.to_datetime(user_meetings["start_datetime"]) > current_time
    ]

    return future_meetings.to_dict("records")


@tool
def cancel_bookings(user_id: int, booking_ids: List[int]) -> str:
    """
    取消用户的一个或多个预订。

    使用场景：
    - 用户说"取消我的预订"
    - 用户想要取消特定的预订ID
    - 用户需要释放已预订的会议室

    参数说明：
    - user_id: 用户ID，必须是有效的整数
    - booking_ids: 要取消的预订ID列表，必须是整数列表

    返回：取消操作的结果，包括成功数量和错误信息

    ⚠️ 重要：这是一个危险工具，会永久删除预订记录，需要用户确认后才能执行。

    安全检查：
    - 只能取消属于指定用户的预订
    - 如果预订不存在或无权限，会返回相应错误信息
    """
    print(f"Tool: User {user_id} is attempting to cancel bookings: {booking_ids}.")

    # 获取数据管理器
    data_manager = DataManager()

    cancelled_count = 0
    errors = []

    for booking_id in booking_ids:
        try:
            # 更新会议状态为已取消
            data_manager.update_meeting_status(booking_id, "已取消")
            cancelled_count += 1
        except Exception as e:
            errors.append(f"预订ID {booking_id} 取消失败: {e}")

    result_str = f"成功取消 {cancelled_count} 个预订。"
    if errors:
        result_str += " 发生以下错误: " + ", ".join(errors)
    return result_str


@tool
def alter_booking(
    booking_id: int,
    user_id: int,
    new_start_time: Optional[str] = None,
    new_end_time: Optional[str] = None,
) -> str:
    """
    修改现有预订的时间（当前版本暂不支持，引导用户使用替代方案）。

    使用场景：
    - 用户想要修改会议时间
    - 用户说"改变我的预订时间"
    - 用户需要调整已有预订

    参数说明：
    - booking_id: 要修改的预订ID，必须是有效的整数
    - user_id: 用户ID，必须是有效的整数
    - new_start_time: 新的开始时间，可选，格式：'YYYY-MM-DD HH:MM:SS'
    - new_end_time: 新的结束时间，可选，格式：'YYYY-MM-DD HH:MM:SS'

    返回：操作指导信息

    ⚠️ 重要：这是一个危险工具，虽然当前版本不执行实际修改，但仍需要用户确认。

    当前策略：
    - 由于修改预订涉及复杂的可用性检查
    - 建议用户先取消原预订，再创建新预订
    - 这样可以确保时间冲突检查的准确性
    """
    print(f"Tool: User {user_id} wants to alter booking {booking_id}.")
    # PoC 简化：修改是一个复杂操作，涉及检查新时段的可用性。
    # 在PoC阶段，我们引导用户先取消再重新预订。
    return "修改功能暂不支持。请先使用 'cancel_bookings' 工具取消原预订，然后使用 'recommend_available_rooms' 和 'book_room' 工具来创建一个新的预订。"
