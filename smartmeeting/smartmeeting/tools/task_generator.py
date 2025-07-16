"""
Task Generator Module
Contains functions for converting action items from meeting minutes to specific tasks
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from smartmeeting.tools.llm import setup_chat_llm


def generate_tasks_from_action_items(
    action_items: List[str],
    meeting_title: str,
    meeting_id: str,
    attendees: Optional[List[str]] = None,
    meeting_data: Optional[Dict[str, Any]] = None,
    users_df=None,
) -> List[Dict[str, Any]]:
    """
    Generate specific tasks from action items using LLM

    Args:
        action_items: List of action items from meeting minutes
        meeting_title: Title of the meeting
        meeting_id: ID of the meeting
        attendees: List of meeting attendees
        meeting_data: Meeting data for getting organizer information

    Returns:
        List of validated task dictionaries
    """
    if not action_items:
        return []

    # 获取默认负责人（会议组织者）
    default_assignee = "未分配"
    if meeting_data:
        default_assignee = get_meeting_organizer(meeting_data)
    elif attendees and len(attendees) > 0:
        default_assignee = attendees[0]

    client = setup_chat_llm()
    if not client:
        print("LLM not available, using fallback task generation")
        fallback_tasks = _generate_fallback_tasks(
            action_items, meeting_title, meeting_id, attendees
        )
        # 校验并修复fallback任务
        return validate_tasks_batch(
            fallback_tasks, meeting_title, meeting_id, default_assignee, users_df
        )

    try:
        # Prepare the prompt
        prompt = _create_task_generation_prompt(action_items, meeting_title, attendees)

        # Call LLM
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的任务管理助手，负责将会议中的行动项转换为具体的、可执行的任务。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        # Parse the response
        content = response.choices[0].message.content
        tasks = _parse_llm_response(content, meeting_id)

        # 校验并修复生成的任务
        validated_tasks = validate_tasks_batch(
            tasks, meeting_title, meeting_id, default_assignee, users_df
        )

        return validated_tasks

    except Exception as e:
        print(f"Error generating tasks with LLM: {e}")
        fallback_tasks = _generate_fallback_tasks(
            action_items, meeting_title, meeting_id, attendees
        )
        # 校验并修复fallback任务
        return validate_tasks_batch(
            fallback_tasks, meeting_title, meeting_id, default_assignee, users_df
        )


def _create_task_generation_prompt(
    action_items: List[str], meeting_title: str, attendees: Optional[List[str]] = None
) -> str:
    """Create the prompt for task generation"""

    attendees_text = ""
    if attendees:
        attendees_text = f"\n与会人员: {', '.join(attendees)}"

    action_items_text = "\n".join([f"- {item}" for item in action_items])

    prompt = f"""
请将以下会议中的行动项转换为具体的、可执行的任务列表。

会议标题: {meeting_title}{attendees_text}

行动项:
{action_items_text}

请为每个行动项生成一个具体的任务，包含以下信息：
1. 任务名称：具体、明确的任务标题
2. 负责人：从与会人员中选择合适的人选，如果没有明确指定，请根据任务性质合理分配
3. 截止日期：根据任务复杂度和紧急程度设定合理的截止日期（如果无法确定，默认为7天后）
4. 优先级：高、中、低（如果无法确定，默认为中）
5. 任务描述：详细的任务说明

请以JSON格式返回，格式如下：
[
    {{
        "title": "任务名称",
        "description": "任务描述",
        "assignee_name": "负责人姓名",
        "priority": "高/中/低",
        "deadline_days": 7,
        "estimated_hours": 8
    }}
]

注意：
- 任务名称要具体明确
- 负责人必须是与会人员之一
- 截止日期用天数表示（从今天开始计算）
- 优先级根据任务重要性和紧急程度确定
- 预估工时根据任务复杂度确定
"""

    return prompt


def _parse_llm_response(content: str, meeting_id: str) -> List[Dict[str, Any]]:
    """Parse LLM response and convert to task format"""
    try:
        # Extract JSON from response
        start_idx = content.find("[")
        end_idx = content.rfind("]") + 1

        if start_idx == -1 or end_idx == 0:
            print("No valid JSON found in LLM response")
            return []

        json_str = content[start_idx:end_idx]
        tasks_data = json.loads(json_str)

        # Convert to task format
        tasks = []
        for task_data in tasks_data:
            task = {
                "title": task_data.get("title", "未命名任务"),
                "description": task_data.get("description", ""),
                "assignee_name": task_data.get("assignee_name", "未分配"),
                "priority": task_data.get("priority", "中"),
                "deadline_days": task_data.get("deadline_days", 7),
                "estimated_hours": task_data.get("estimated_hours", 8),
                "status": "待处理",
                "booking_id": meeting_id,
                "created_datetime": datetime.now(),
                "updated_datetime": datetime.now(),
            }
            tasks.append(task)

        return tasks

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from LLM response: {e}")
        return []
    except Exception as e:
        print(f"Error processing LLM response: {e}")
        return []


def _generate_fallback_tasks(
    action_items: List[str],
    meeting_title: str,
    meeting_id: str,
    attendees: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Generate fallback tasks when LLM is not available"""
    tasks = []

    # Default assignee
    assignee = "未分配"
    if attendees and len(attendees) > 0:
        assignee = attendees[0]

    for i, action_item in enumerate(action_items):
        # Calculate deadline (7 days from now)
        deadline_date = datetime.now() + timedelta(days=7)

        task = {
            "title": f"{action_item[:30]}{'...' if len(action_item) > 30 else ''}",
            "description": action_item,
            "assignee_name": assignee,
            "priority": "中",
            "deadline_days": 7,
            "estimated_hours": 8,
            "status": "待处理",
            "booking_id": meeting_id,
            "created_datetime": datetime.now(),
            "updated_datetime": datetime.now(),
        }
        tasks.append(task)

    return tasks


def extract_action_items_from_minutes(minutes_data: Dict[str, Any]) -> List[str]:
    """Extract action items from minutes data"""
    action_items = []

    # Try to get action items from different possible fields
    action_items_text = minutes_data.get("action_items", "")

    if action_items_text:
        # Split by common delimiters
        if isinstance(action_items_text, str):
            # Split by semicolon, newline, or bullet points
            items = (
                action_items_text.replace(";", "\n")
                .replace("•", "")
                .replace("-", "")
                .split("\n")
            )
            for item in items:
                item = item.strip()
                if item and len(item) > 2:  # Filter out empty or very short items
                    action_items.append(item)

    return action_items


def extract_attendees_from_minutes(minutes_data: Dict[str, Any]) -> List[str]:
    """Extract attendees from minutes data"""
    attendees = []

    attendees_text = minutes_data.get("attendees", "")

    if attendees_text:
        if isinstance(attendees_text, str):
            # Split by common delimiters
            attendee_list = (
                attendees_text.replace(";", ",").replace("，", ",").split(",")
            )
            for attendee in attendee_list:
                attendee = attendee.strip()
                if attendee and len(attendee) > 1:
                    attendees.append(attendee)

    return attendees


def validate_and_fix_task(
    task: Dict[str, Any],
    meeting_title: str,
    meeting_id: str,
    default_assignee: str = "未分配",
    users_df=None,
) -> Dict[str, Any]:
    """
    校验并修复任务字段，确保包含必需字段并设置合理的默认值

    Args:
        task: 原始任务数据
        meeting_title: 会议标题
        meeting_id: 会议ID
        default_assignee: 默认负责人（通常是会议组织者）

    Returns:
        校验并修复后的任务数据
    """
    from datetime import datetime, timedelta

    # 必需字段校验和修复
    validated_task = task.copy()

    # 1. 任务名称 - 必需字段
    if not validated_task.get("title") or not validated_task["title"].strip():
        validated_task["title"] = f"来自{meeting_title}的任务"

    # 2. 负责人处理 - 转换为assignee_id和department_id
    assignee_name = validated_task.get("assignee_name", default_assignee)
    if not assignee_name or not assignee_name.strip():
        assignee_name = default_assignee

    # 设置assignee_id和department_id
    assignee_id = 1  # 默认值
    department_id = 1  # 默认值

    if users_df is not None and len(users_df) > 0:
        # 尝试从用户数据中查找对应的ID
        user_match = users_df[users_df["name"] == assignee_name]
        if len(user_match) > 0:
            assignee_id = user_match.iloc[0]["user_id"]
            department_id = user_match.iloc[0]["department_id"]

    validated_task["assignee_id"] = assignee_id
    validated_task["department_id"] = department_id

    # 3. 截止日期 - 必需字段，如果无法获取则默认为7天
    deadline_days = validated_task.get("deadline_days", 7)
    if not isinstance(deadline_days, (int, float)) or deadline_days <= 0:
        deadline_days = 7
    validated_task["deadline_days"] = deadline_days

    # 计算实际截止日期（保持与现有数据结构一致）
    deadline_date = datetime.now() + timedelta(days=deadline_days)
    validated_task["deadline"] = deadline_date.strftime("%Y-%m-%d")

    # 4. 关联会议 - 必需字段
    if not validated_task.get("booking_id"):
        validated_task["booking_id"] = meeting_id

    # 5. 优先级 - 如果无法获取则默认为中
    priority = validated_task.get("priority", "中")
    if priority not in ["高", "中", "低"]:
        priority = "中"
    validated_task["priority"] = priority

    # 6. 其他字段的默认值设置
    if not validated_task.get("description"):
        validated_task["description"] = validated_task["title"]

    if not validated_task.get("status"):
        validated_task["status"] = "待处理"

    if not validated_task.get("estimated_hours"):
        validated_task["estimated_hours"] = 8

    # 7. 时间戳字段
    current_time = datetime.now()
    if not validated_task.get("created_datetime"):
        validated_task["created_datetime"] = current_time
    if not validated_task.get("updated_datetime"):
        validated_task["updated_datetime"] = current_time

    # 8. 移除不需要的字段，保持与现有数据结构一致
    if "assignee_name" in validated_task:
        del validated_task["assignee_name"]

    return validated_task


def validate_tasks_batch(
    tasks: List[Dict[str, Any]],
    meeting_title: str,
    meeting_id: str,
    default_assignee: str = "未分配",
    users_df=None,
) -> List[Dict[str, Any]]:
    """
    批量校验和修复任务列表

    Args:
        tasks: 原始任务列表
        meeting_title: 会议标题
        meeting_id: 会议ID
        default_assignee: 默认负责人
        users_df: 用户数据，用于获取assignee_id和department_id

    Returns:
        校验并修复后的任务列表
    """
    validated_tasks = []

    for task in tasks:
        validated_task = validate_and_fix_task(
            task, meeting_title, meeting_id, default_assignee, users_df
        )
        validated_tasks.append(validated_task)

    return validated_tasks


def get_meeting_organizer(meeting_data: Dict[str, Any]) -> str:
    """
    从会议数据中获取会议组织者

    Args:
        meeting_data: 会议数据

    Returns:
        会议组织者姓名
    """
    # 尝试从不同字段获取组织者信息
    organizer = (
        meeting_data.get("organizer")
        or meeting_data.get("organizer_name")
        or meeting_data.get("created_by")
        or meeting_data.get("host")
        or "未分配"
    )

    return organizer if organizer and organizer.strip() else "未分配"
