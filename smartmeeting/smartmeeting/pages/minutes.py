"""
Minutes Page Module
Contains the minutes page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd


class MinutesPage:
    """Meeting minutes page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """Meeting minutes page implementation with enhanced functionality"""
        self.ui.create_header("会议纪要")

        # Minutes statistics
        col1, col2, col3, col4 = st.columns(4)

        minutes_df = self.data_manager.get_dataframe("minutes")

        with col1:
            self.ui.create_metric_card("总纪要数", str(len(minutes_df)))

        with col2:
            confirmed_minutes = len(minutes_df[minutes_df["status"] == "已确认"])
            self.ui.create_metric_card("已确认", str(confirmed_minutes))

        with col3:
            draft_minutes = len(minutes_df[minutes_df["status"] == "草稿"])
            self.ui.create_metric_card("草稿", str(draft_minutes))

        with col4:
            published_minutes = len(minutes_df[minutes_df["status"] == "已发布"])
            self.ui.create_metric_card("已发布", str(published_minutes))

        # Upload and transcription
        st.markdown("---")
        st.markdown("### 创建会议纪要")

        # Meeting selection or creation
        meeting_mode = st.radio(
            "选择模式", ["创建新会议", "选择已有会议"], horizontal=True
        )

        if meeting_mode == "选择已有会议":
            # Select existing meeting for minutes
            meetings_df = self.data_manager.get_dataframe("meetings")
            meeting_options = [
                f"{row['title']} - {row['start_time']}"
                for _, row in meetings_df.iterrows()
            ]

            if len(meeting_options) > 0:
                selected_meeting_option = st.selectbox("选择会议", meeting_options)
                selected_meeting_id = meetings_df.iloc[
                    meeting_options.index(selected_meeting_option)
                ]["id"]
                selected_meeting_title = meetings_df.iloc[
                    meeting_options.index(selected_meeting_option)
                ]["title"]
            else:
                st.warning("暂无会议记录")
                selected_meeting_id = None
                selected_meeting_title = None
        else:
            # Create new meeting
            col1, col2 = st.columns(2)
            with col1:
                new_meeting_title = st.text_input(
                    "会议标题", placeholder="请输入会议标题"
                )
            with col2:
                col_date, col_time = st.columns(2)
                with col_date:
                    new_meeting_date = st.date_input(
                        "会议日期", value=pd.Timestamp.now().date()
                    )
                with col_time:
                    new_meeting_time = st.time_input(
                        "会议时间", value=pd.Timestamp.now().time()
                    )

            # Combine date and time
            new_meeting_datetime = pd.Timestamp.combine(
                new_meeting_date, new_meeting_time
            )

            selected_meeting_id = None
            selected_meeting_title = new_meeting_title if new_meeting_title else None

        # File upload section
        st.markdown("#### 上传会议材料")
        col1, col2 = st.columns(2)

        with col1:
            uploaded_text = st.file_uploader(
                "上传文本文件", type=["txt", "docx", "pdf"]
            )
            if uploaded_text:
                st.success(f"已上传: {uploaded_text.name}")
                if st.button("生成纪要", type="primary"):
                    with st.spinner("正在生成会议纪要..."):
                        try:
                            # Read the uploaded text file
                            if uploaded_text.name.endswith(".txt"):
                                content = uploaded_text.read().decode("utf-8")
                            else:
                                # For other file types, we'll need to implement proper parsing
                                st.error("目前仅支持txt文件格式")
                                return

                            # Generate meeting minutes using pandasai
                            generated_minute = self._generate_minutes_from_text(
                                content,
                                selected_meeting_title,
                                (
                                    new_meeting_datetime
                                    if "new_meeting_datetime" in locals()
                                    else None
                                ),
                            )

                            if generated_minute:
                                # Add to data manager
                                self.data_manager.add_minute(generated_minute)
                                # 立即刷新 minutes_df，以便展示时不依赖过期状态
                                minutes_df = self.data_manager.get_dataframe("minutes")
                                st.success("会议纪要生成完成并已保存！")
                                st.rerun()
                            else:
                                st.error("生成会议纪要失败，请重试")

                        except Exception as e:
                            st.error(f"处理文件时出错: {str(e)}")

        with col2:
            uploaded_audio = st.file_uploader(
                "上传音频文件", type=["mp3", "wav", "m4a"]
            )
            if uploaded_audio:
                st.success(f"已上传: {uploaded_audio.name}")
                if st.button("开始转写", type="primary"):
                    with st.spinner("正在转写音频..."):
                        import time

                        time.sleep(2)  # Simulate processing
                        st.success("转写完成！")
                        st.session_state.minute_form_data["transcription"] = (
                            "这是转写后的会议内容示例..."
                        )

        # Show current meeting info
        if selected_meeting_title:
            st.info(f"当前会议: {selected_meeting_title}")
        elif meeting_mode == "创建新会议" and new_meeting_title:
            st.info(f"新会议: {new_meeting_title}")
        else:
            st.warning("请选择会议或输入会议标题")

        # Minutes list with enhanced features
        st.markdown("---")
        st.markdown("### 纪要列表")

        if len(minutes_df) > 0:
            # Sort by meeting time (descending)
            minutes_df = minutes_df.sort_values("created_datetime", ascending=False)

            # Filtering options and pagination in one row
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                # Status filter
                status_options = ["全部"] + list(minutes_df["status"].unique())
                selected_status = st.selectbox("按状态筛选", status_options)

            with col2:
                # Attendee filter
                all_attendees = set()
                for attendees_str in minutes_df["attendees"].dropna():
                    if isinstance(attendees_str, str):
                        attendees_list = attendees_str.split(";")
                        all_attendees.update(attendees_list)

                attendee_options = ["全部"] + sorted(list(all_attendees))
                selected_attendee = st.selectbox("按与会人筛选", attendee_options)

            with col3:
                # Search by title
                search_title = st.text_input(
                    "按标题搜索", placeholder="输入会议标题关键词"
                )

            with col4:
                # Pagination
                items_per_page = 5
                # Apply filters first to get total items for pagination
                filtered_df = minutes_df.copy()

                if selected_status != "全部":
                    filtered_df = filtered_df[filtered_df["status"] == selected_status]

                if selected_attendee != "全部":
                    filtered_df = filtered_df[
                        filtered_df["attendees"].str.contains(
                            selected_attendee, na=False
                        )
                    ]

                if search_title:
                    filtered_df = filtered_df[
                        filtered_df["title"].str.contains(
                            search_title, na=False, case=False
                        )
                    ]

                total_items = len(filtered_df)
                total_pages = (total_items + items_per_page - 1) // items_per_page

                if total_pages > 1:
                    current_page = st.selectbox(
                        f"页码 ({total_pages}页)",
                        range(1, total_pages + 1),
                        key="minutes_page",
                    )
                else:
                    current_page = 1

            # Calculate start and end indices
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)

            # Display pagination info
            if total_items > 0:
                st.info(f"显示第 {start_idx + 1}-{end_idx} 条，共 {total_items} 条纪要")

            # Display filtered and paginated minutes
            if len(filtered_df) > 0:
                for idx in range(start_idx, end_idx):
                    minute = filtered_df.iloc[idx]

                    # Title fallback and sanitization
                    raw_title = (
                        minute.get("title")
                        or minute.get("meeting_title")
                        or f"未命名纪要 {idx + 1}"
                    )
                    title = (
                        str(raw_title).strip()
                        if pd.notna(raw_title)
                        else f"未命名纪要 {idx + 1}"
                    )

                    # Status fallback
                    status = minute.get("status", "未知状态")
                    created_time = minute.get("created_datetime", "未知时间")

                    # Format datetime
                    if pd.notna(created_time):
                        if isinstance(created_time, str):
                            display_time = created_time
                        elif hasattr(created_time, "strftime"):
                            display_time = created_time.strftime("%Y-%m-%d %H:%M")
                        else:
                            display_time = str(created_time)
                    else:
                        display_time = "未知时间"

                    # Safe ID for component keys and operation
                    raw_id = minute.get("id") or minute.get("minute_id") or f"nan_{idx}"
                    minute_id = str(raw_id) if pd.notna(raw_id) else f"nan_{idx}"

                    with st.expander(f"{title} - {status} ({display_time})"):
                        # 上部内容：会议摘要、与会人员、决策事项、行动项
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 会议摘要")
                            st.write(minute.get("summary", "(无摘要)"))

                            # 显示与会人信息
                            attendees = minute.get("attendees", "")
                            if attendees:
                                st.markdown("#### 与会人员")
                                if isinstance(attendees, str):
                                    # 如果是字符串，按分号分割
                                    attendee_list = [
                                        a.strip()
                                        for a in attendees.split(";")
                                        if a.strip()
                                    ]
                                    for attendee in attendee_list:
                                        st.markdown(f"• {attendee}")
                                elif isinstance(attendees, list):
                                    # 如果是列表，直接显示
                                    for attendee in attendees:
                                        st.markdown(f"• {attendee}")

                        with col2:
                            decisions = minute.get("decisions", [])
                            if decisions:
                                st.markdown("#### 决策事项")
                                for i, decision in enumerate(decisions, 1):
                                    st.markdown(f"{i}. {decision}")

                            action_items = minute.get("action_items", [])
                            if action_items:
                                st.markdown("#### 行动项")
                                for i, action in enumerate(action_items, 1):
                                    st.markdown(f"{i}. {action}")

                        # 分隔线
                        st.markdown("---")

                        # 底部操作按钮
                        bcol1, bcol2, bcol3 = st.columns(3)

                        with bcol1:
                            if st.button("确认", key=f"confirm_{minute_id}_{idx}"):
                                actual_id = minute.get("id") or minute.get("minute_id")
                                if actual_id and pd.notna(actual_id):
                                    self.data_manager.update_minute_status(
                                        actual_id, "已确认"
                                    )
                                    st.success("纪要已确认")
                                    st.rerun()
                                else:
                                    st.error("无法更新纪要状态：ID无效")

                        with bcol2:
                            if st.button("发布", key=f"publish_{minute_id}_{idx}"):
                                actual_id = minute.get("id") or minute.get("minute_id")
                                if actual_id and pd.notna(actual_id):
                                    self.data_manager.update_minute_status(
                                        actual_id, "已发布"
                                    )
                                    st.success("纪要已发布")
                                    st.rerun()
                                else:
                                    st.error("无法更新纪要状态：ID无效")

                        with bcol3:
                            if st.button("删除", key=f"delete_{minute_id}_{idx}"):
                                st.warning("删除功能暂未实现")
            else:
                st.info("没有找到符合条件的会议纪要")
        else:
            st.info("暂无会议纪要")

    def _generate_minutes_from_text(self, text, meeting_title, meeting_datetime=None):
        """
        Use pandasai LLM to generate meeting minutes from uploaded text.
        Returns a dict matching the meeting_minutes.csv/data_manager format.
        """
        import pandas as pd
        import streamlit as st
        from smartmeeting.llm import setup_pandasai_llm, create_pandasai_agent

        # Prepare the input as a DataFrame for pandasai
        df = pd.DataFrame({"content": [text]})

        # Setup LLM and Agent
        llm = setup_pandasai_llm()
        if llm is None:
            st.error("未能初始化大模型接口，无法生成纪要。请检查API KEY配置。")
            return None

        try:
            # Use direct LLM call instead of pandasai agent to avoid SQL constraints
            from smartmeeting.llm import setup_chat_llm
            import openai

            chat_llm = setup_chat_llm()
            if chat_llm is None:
                st.error("未能初始化聊天模型接口，无法生成纪要。")
                return None

            # Define the prompt for LLM
            prompt = (
                f"请将以下会议原始文本内容，提取并结构化为会议纪要。"
                f"文本内容：{text}\n\n"
                f"请提取以下信息并以JSON格式返回：\n"
                f"- summary: 会议摘要\n"
                f"- key_decisions: 决策事项（用分号分隔）\n"
                f"- action_items: 行动项（用分号分隔）\n"
                f"- attendees: 与会人（用分号分隔）\n"
                f"- meeting_title: 会议标题（如果文本中未明确提及可留空）\n"
                f"- duration_minutes: 会议时长（分钟数，若无法确定可填60）\n"
                f"注意：不要解析会议日期和时间，这些将由用户提供。"
                f"请只返回JSON格式数据，不要其他内容。"
            )

            # Call LLM directly
            response = chat_llm.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            # Parse LLM response
            llm_response = response.choices[0].message.content.strip()

            import json
            import re

            # Find JSON in the response
            json_match = re.search(r"\{.*\}", llm_response, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                st.error("无法解析LLM返回的JSON数据")
                return None

            # Create DataFrame from parsed data
            result_df = pd.DataFrame(
                [
                    {
                        "summary": parsed_data.get("summary", ""),
                        "key_decisions": parsed_data.get("key_decisions", ""),
                        "action_items": parsed_data.get("action_items", ""),
                        "attendees": parsed_data.get("attendees", ""),
                        "status": "草稿",
                        "duration_minutes": parsed_data.get("duration_minutes", 60),
                        "transcript_available": 1,
                        "meeting_title": parsed_data.get("meeting_title", ""),
                    }
                ]
            )

            # Take the first row
            row = result_df.iloc[0].to_dict()

            # 🧠 修复逻辑：title 设为 meeting_title > LLM 生成 > fallback
            fallback_title = "未命名纪要"
            row["title"] = (
                meeting_title.strip()
                if meeting_title and meeting_title.strip()
                else row.get("meeting_title", "").strip() or fallback_title
            )

            # 确保 meeting_title 也同步写入
            if not row.get("meeting_title") or not row["meeting_title"].strip():
                row["meeting_title"] = row["title"]

            # Set timestamps
            if meeting_datetime is not None:
                row["created_datetime"] = meeting_datetime
                row["updated_datetime"] = meeting_datetime
            else:
                current_time = pd.Timestamp.now()
                row["created_datetime"] = current_time
                row["updated_datetime"] = current_time

            # Default values
            row.setdefault("status", "草稿")
            row.setdefault("duration_minutes", 60)
            row.setdefault("transcript_available", 1)

            # ✅ 调试输出（可选）
            print("生成纪要标题：", row["title"])
            print("纪要结构：", row)

            return row

        except Exception as e:
            st.error(f"调用大模型生成纪要失败: {e}")
            return None
