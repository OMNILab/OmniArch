"""
Meeting Minutes Generator Tool
Contains functions for generating meeting minutes from text content
"""

import pandas as pd
import streamlit as st
import json
import re
from datetime import datetime
from .text_utils import extract_list_from_text, normalize_text_separators


def generate_minutes_from_text(text, meeting_title, meeting_datetime=None):
    """
    Generate meeting minutes from text with robust fallback mechanisms.
    Always returns a valid meeting minute dict, even if LLM fails.

    Args:
        text (str): The text content to generate minutes from
        meeting_title (str): The title of the meeting
        meeting_datetime (datetime, optional): The meeting datetime

    Returns:
        dict: A complete meeting minute dictionary
    """
    # Initialize default values
    default_minute = {
        "summary": "",
        "key_decisions": "",
        "action_items": "",
        "attendees": "",
        "status": "草稿",
        "duration_minutes": 60,
        "transcript_available": 1,
        "meeting_title": "",
        "title": "",
        "created_datetime": None,
        "updated_datetime": None,
        "original_text": text,  # Store the original transcript text
    }

    # Set title with fallback logic
    fallback_title = "未命名纪要"
    default_minute["title"] = (
        meeting_title.strip()
        if meeting_title and meeting_title.strip()
        else fallback_title
    )
    default_minute["meeting_title"] = default_minute["title"]

    # Set timestamps
    if meeting_datetime is not None:
        default_minute["created_datetime"] = meeting_datetime
        default_minute["updated_datetime"] = meeting_datetime
    else:
        current_time = pd.Timestamp.now()
        default_minute["created_datetime"] = current_time
        default_minute["updated_datetime"] = current_time

    # Try to use LLM for enhanced processing
    try:
        from smartmeeting.tools.llm import setup_chat_llm

        chat_llm = setup_chat_llm()
        if chat_llm is not None:
            # Enhanced prompt for better extraction
            prompt = (
                f"请分析以下会议录音转写文本，提取关键信息并生成结构化的会议纪要。\n\n"
                f"转写文本：{text}\n\n"
                f"请以JSON格式返回以下信息：\n"
                f"{{\n"
                f'  "summary": "会议主要内容摘要（100字以内）",\n'
                f'  "key_decisions": "重要决策事项（用分号分隔，如无决策可写\'无\'）",\n'
                f'  "action_items": "需要执行的任务或行动项（用分号分隔，如无行动项可写\'无\'）",\n'
                f'  "attendees": "与会人员名单（用分号分隔，从文本中提取人名）",\n'
                f'  "meeting_title": "会议标题（从文本中提取或推断）",\n'
                f'  "duration_minutes": 60\n'
                f"}}\n\n"
                f"注意：\n"
                f"1. 只返回JSON格式，不要其他内容\n"
                f"2. 如果某项信息无法从文本中提取，使用合理的默认值\n"
                f"3. 确保JSON格式正确，可以被解析\n"
                f"4. 决策事项和行动项可以使用分号分隔"
                f"5. 决策事项和行动项要有意义、可执行的具体任务，不要无意义的内容"
            )

            # Call LLM with timeout and error handling
            try:
                response = chat_llm.chat.completions.create(
                    model="qwen-plus",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000,
                    timeout=30,
                )

                llm_response = response.choices[0].message.content.strip()

                # Try to extract JSON from response
                json_match = re.search(r"\{.*\}", llm_response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())

                    # Update default minute with LLM results
                    default_minute.update(
                        {
                            "summary": parsed_data.get("summary", "").strip(),
                            "key_decisions": parsed_data.get(
                                "key_decisions", ""
                            ).strip(),
                            "action_items": parsed_data.get("action_items", "").strip(),
                            "attendees": parsed_data.get("attendees", "").strip(),
                            "duration_minutes": parsed_data.get("duration_minutes", 60),
                        }
                    )

                    # Update meeting title if LLM provided one
                    llm_title = parsed_data.get("meeting_title", "").strip()
                    if llm_title and llm_title != "未命名纪要":
                        default_minute["meeting_title"] = llm_title
                        if (
                            not default_minute["title"]
                            or default_minute["title"] == "未命名纪要"
                        ):
                            default_minute["title"] = llm_title

                    st.success("✓ 使用AI智能分析生成会议纪要")

            except Exception as llm_error:
                st.warning(f"AI分析失败，使用基础模式生成纪要: {str(llm_error)}")

    except Exception as e:
        st.warning(f"无法连接AI服务，使用基础模式生成纪要: {str(e)}")

    # Fallback processing: extract basic information from text
    if not default_minute["summary"]:
        # Generate a basic summary from the first few sentences
        sentences = text.split("。")[:3]
        summary = "。".join([s.strip() for s in sentences if s.strip()])[:200]
        if summary:
            default_minute["summary"] = summary + "..."

    if not default_minute["attendees"]:
        # Extract potential attendees from text
        # Look for patterns like "我叫XXX" or "我是XXX"
        name_patterns = [
            r"我叫([^，。\s]+)",
            r"我是([^，。\s]+)",
            r"大家好，我是([^，。\s]+)",
            r"大家好，我叫([^，。\s]+)",
        ]

        attendees = set()
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            attendees.update(matches)

        if attendees:
            default_minute["attendees"] = ";".join(sorted(attendees))

    if not default_minute["key_decisions"]:
        # Look for decision-related keywords
        decision_keywords = ["决定", "决策", "确定", "同意", "通过", "批准", "确认"]
        decision_sentences = []
        for sentence in text.split("。"):
            if any(keyword in sentence for keyword in decision_keywords):
                decision_sentences.append(sentence.strip())

        if decision_sentences:
            # Use the text utility to normalize separators
            default_minute["key_decisions"] = normalize_text_separators(
                ";".join(decision_sentences[:3])
            )

    if not default_minute["action_items"]:
        # Look for action-related keywords
        action_keywords = ["需要", "应该", "必须", "计划", "安排", "准备", "完成"]
        action_sentences = []
        for sentence in text.split("。"):
            if any(keyword in sentence for keyword in action_keywords):
                action_sentences.append(sentence.strip())

        if action_sentences:
            # Use the text utility to normalize separators
            default_minute["action_items"] = normalize_text_separators(
                ";".join(action_sentences[:3])
            )

    # Ensure all required fields have values
    default_minute["summary"] = (
        default_minute["summary"] or "会议内容已转写，请查看详细记录。"
    )
    default_minute["key_decisions"] = default_minute["key_decisions"] or "无"
    default_minute["action_items"] = default_minute["action_items"] or "无"
    default_minute["attendees"] = default_minute["attendees"] or "未识别"

    # Convert to proper data types
    try:
        default_minute["duration_minutes"] = int(default_minute["duration_minutes"])
    except (ValueError, TypeError):
        default_minute["duration_minutes"] = 60

    # Debug output
    print("生成纪要标题：", default_minute["title"])
    print("纪要结构：", default_minute)

    return default_minute
