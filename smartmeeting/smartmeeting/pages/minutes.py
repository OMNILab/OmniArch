"""
Minutes Page Module
Contains the minutes page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from smartmeeting.tools import (
    generate_minutes_from_text,
    transcribe_file,
    extract_transcription_text,
    extract_list_from_text,
    extract_text_from_file,
    get_supported_file_types,
    validate_file_size,
    get_file_info,
)
from smartmeeting.tools.task_generator import (
    generate_tasks_from_action_items,
    extract_action_items_from_minutes,
    extract_attendees_from_minutes,
)


class MinutesPage:
    """Meeting minutes page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def _find_existing_minutes(self, booking_id):
        """Find existing minutes for a meeting"""
        minutes_df = self.data_manager.get_dataframe("minutes")
        if "booking_id" in minutes_df.columns:
            existing_minutes = minutes_df[minutes_df["booking_id"] == booking_id]
        else:
            existing_minutes = pd.DataFrame()
        return existing_minutes.iloc[0] if len(existing_minutes) > 0 else None

    def _update_existing_minutes(self, booking_id, new_minutes_data):
        """Update existing minutes for a meeting"""
        minutes_data = self.data_manager.get_data()
        minutes_list = minutes_data["minutes"]

        for i, minute in enumerate(minutes_list):
            if minute.get("booking_id") == booking_id:
                # Update the existing minutes
                minutes_list[i].update(new_minutes_data)
                minutes_list[i]["updated_datetime"] = datetime.now()
                return True

        return False

    def _get_status_color(self, status):
        """Get color for different status types"""
        status_colors = {
            "草稿": "🔵",  # Blue circle for draft
            "已确认": "🟡",  # Yellow circle for confirmed
            "已发布": "🟢",  # Green circle for published
            "未知状态": "⚪",  # White circle for unknown
        }
        return status_colors.get(status, "⚪")

    def _get_status_style(self, status):
        """Get CSS style for status background color"""
        status_styles = {
            "草稿": "background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 8px; border-radius: 4px;",
            "已确认": "background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 8px; border-radius: 4px;",
            "已发布": "background-color: #e8f5e8; border-left: 4px solid #4caf50; padding: 8px; border-radius: 4px;",
            "未知状态": "background-color: #f5f5f5; border-left: 4px solid #9e9e9e; padding: 8px; border-radius: 4px;",
        }
        return status_styles.get(status, status_styles["未知状态"])

    def show(self):
        """Meeting minutes page implementation with enhanced functionality"""
        self.ui.create_header("会议纪要")

        # Minutes statistics
        st.markdown("### 纪要概览")
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
            meeting_options = []
            meeting_status_info = []  # 存储会议状态信息

            # 按开始时间逆序排序
            if "start_datetime" in meetings_df.columns:
                # 确保时间列是datetime类型，避免混合类型比较错误
                try:
                    meetings_df_copy = meetings_df.copy()
                    meetings_df_copy["start_datetime"] = pd.to_datetime(
                        meetings_df_copy["start_datetime"], errors="coerce"
                    )
                    meetings_df_sorted = meetings_df_copy.sort_values(
                        "start_datetime", ascending=False
                    )
                except Exception as e:
                    # 如果转换失败，使用原始数据不排序
                    print(f"Warning: Could not sort by start_datetime: {e}")
                    meetings_df_sorted = meetings_df
            else:
                meetings_df_sorted = meetings_df

            for _, row in meetings_df_sorted.iterrows():
                title = row.get("meeting_title", "未命名会议")
                start_time = row.get("start_datetime", "未知时间")
                meeting_status = row.get("meeting_status", "upcoming")

                # Format datetime if it's a datetime object
                if pd.notna(start_time):
                    if hasattr(start_time, "strftime"):
                        start_time = start_time.strftime("%Y-%m-%d %H:%M")
                    else:
                        start_time = str(start_time)
                else:
                    start_time = "未知时间"

                # 根据会议状态添加标识
                status_icon = (
                    "🕐"
                    if meeting_status == "upcoming"
                    else "🔄" if meeting_status == "ongoing" else "✅"
                )
                status_text = (
                    "未进行"
                    if meeting_status == "upcoming"
                    else "进行中" if meeting_status == "ongoing" else "已完成"
                )

                meeting_options.append(
                    f"{status_icon} {title} - {start_time} ({status_text})"
                )
                meeting_status_info.append(meeting_status)

            if len(meeting_options) > 0:
                selected_meeting_option = st.selectbox("选择会议", meeting_options)
                selected_index = meeting_options.index(selected_meeting_option)
                selected_meeting_id = meetings_df_sorted.iloc[selected_index][
                    "booking_id"
                ]
                selected_meeting_title = meetings_df_sorted.iloc[selected_index][
                    "meeting_title"
                ]
                selected_meeting_status = meeting_status_info[selected_index]

                # 显示会议状态警告
                if selected_meeting_status == "upcoming":
                    st.warning("⚠️ 该会议还未进行，建议在会议结束后再生成纪要")
                elif selected_meeting_status == "ongoing":
                    st.info("🔄 该会议正在进行中，可以实时生成纪要")
                else:
                    pass
            else:
                st.warning("暂无会议记录")
                selected_meeting_id = None
                selected_meeting_title = None
                selected_meeting_status = None
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
            # Fallback: use auto-generated title if empty
            if new_meeting_title and new_meeting_title.strip():
                selected_meeting_title = new_meeting_title.strip()
            else:
                selected_meeting_title = (
                    f"会议纪要_{new_meeting_datetime.strftime('%Y%m%d_%H%M')}"
                )

        # File upload section with tabs
        st.markdown("#### 上传会议材料")

        # Create tabs for different upload methods
        tab1, tab2 = st.tabs(["📄 文本文件", "🎵 音频文件"])

        with tab1:
            st.markdown(
                "支持上传会议记录、会议笔记等文本文件，系统将自动分析并生成结构化会议纪要。支持纯文本文件 (.txt)，Markdown (.md) • Word文档 (.docx) • PDF文档 (.pdf)。最大 10MB。"
            )

            # Get supported file types
            supported_types = get_supported_file_types()
            file_extensions = list(supported_types.keys())

            uploaded_text = st.file_uploader(
                "选择文件",
                type=file_extensions,
                key="text_uploader",
                help="支持 TXT、Markdown、DOCX、PDF 格式",
            )

            if uploaded_text:
                # Validate file size
                if not validate_file_size(uploaded_text, max_size_mb=10):
                    st.stop()

                # Get file information
                file_info = get_file_info(uploaded_text)

                # Display file information
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**文件名**: {file_info['name']}")
                with col2:
                    st.info(f"**文件类型**: {file_info['type']}")
                with col3:
                    st.info(f"**文件大小**: {file_info['size_mb']:.1f}MB")

                # Extract text content
                with st.spinner("正在解析文件内容..."):
                    content = extract_text_from_file(uploaded_text)

                if content:
                    st.success(f"✅ 文件解析成功！提取到 {len(content)} 个字符")

                    # Show content preview
                    with st.expander("📄 查看文件内容预览", expanded=False):
                        preview_length = min(500, len(content))
                        st.text_area(
                            "文件内容预览",
                            value=content[:preview_length]
                            + ("..." if len(content) > preview_length else ""),
                            height=200,
                            disabled=True,
                            key="content_preview",
                        )

                    if st.button("生成纪要", type="primary", key="generate_from_text"):
                        with st.spinner("正在生成会议纪要..."):
                            try:
                                # if selected_meeting_title is empty, use first 8 chars of content
                                meeting_title_to_use = selected_meeting_title
                                if (
                                    not meeting_title_to_use
                                    or not meeting_title_to_use.strip()
                                ):
                                    meeting_title_to_use = (
                                        content[:8].strip() or "未命名纪要"
                                    )

                                # Generate meeting minutes using pandasai
                                generated_minute = generate_minutes_from_text(
                                    content,
                                    meeting_title_to_use,
                                    (
                                        new_meeting_datetime
                                        if "new_meeting_datetime" in locals()
                                        else None
                                    ),
                                )

                                if generated_minute:
                                    # Check if we're updating an existing meeting
                                    if (
                                        meeting_mode == "选择已有会议"
                                        and selected_meeting_id
                                    ):
                                        # Try to update existing minutes
                                        if self._update_existing_minutes(
                                            selected_meeting_id, generated_minute
                                        ):
                                            st.success("会议纪要已更新！")
                                        else:
                                            # If no existing minutes found, add new one with booking_id
                                            generated_minute["booking_id"] = (
                                                selected_meeting_id
                                            )
                                            self.data_manager.add_minute(
                                                generated_minute
                                            )
                                            st.success("会议纪要生成完成并已保存！")
                                    else:
                                        # Add new minutes
                                        self.data_manager.add_minute(generated_minute)
                                        st.success("会议纪要生成完成并已保存！")

                                    # 立即刷新 minutes_df，以便展示时不依赖过期状态
                                    minutes_df = self.data_manager.get_dataframe(
                                        "minutes"
                                    )
                                    st.rerun()
                                else:
                                    st.error("会议纪要生成失败，请重试")
                            except Exception as e:
                                st.error(f"生成会议纪要时出错: {str(e)}")
                else:
                    st.error("❌ 文件内容提取失败，请检查文件格式是否正确")

        with tab2:
            st.markdown("**选择音频文件**")
            st.markdown("选择的音频文件，系统将自动转写语音内容并生成会议纪要。")

            # Audio file selection dropdown
            audio_files = {
                "全景视频会议": "http://116.62.193.164:9380/public/omniarch/sample1_8k_15min.mp4",
                "招聘会议": "http://116.62.193.164:9380/public/omniarch/sample2_8k_15min.mp4",
                "经营分析会议": "http://116.62.193.164:9380/public/omniarch/sample3_8k_15min.mp4",
                "股东电话会会议": "http://116.62.193.164:9380/public/omniarch/sample4_8k_15min.mp4",
            }

            selected_audio = st.selectbox(
                "选择音频文件",
                ["请选择音频文件"] + list(audio_files.keys()),
                key="audio_selector",
            )

            if selected_audio != "请选择音频文件":
                # Get the audio file URL
                audio_url = audio_files[selected_audio]

                # Create audio player with custom styling
                st.markdown(
                    """
                <style>
                .audio-player {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    padding: 10px;
                    margin: 10px 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .audio-player audio {
                    width: 100%;
                    height: 30px;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )

                # Use Streamlit's native audio component for better compatibility
                st.audio(audio_url, format="video/mp4")

                st.markdown(
                    """
                <div class="audio-player">
                    <p style="color: white; margin-top: 10px; font-size: 12px;">
                        💡 提示：您可以先预览音频内容，确认无误后再进行转写
                    </p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if st.button("生成会议纪要", type="primary", key="start_transcription"):
                    with st.spinner("正在转写音频文件..."):
                        try:
                            file_link = audio_files[selected_audio]

                            # Call the transcription function
                            result = transcribe_file(
                                os.getenv("ALIYUN_AK_ID"),
                                os.getenv("ALIYUN_AK_SECRET"),
                                os.getenv("NLS_APP_KEY"),
                                file_link,
                            )

                            if result:
                                # Extract the transcription text from the result
                                transcription_text = extract_transcription_text(result)

                                if transcription_text:
                                    st.success("音频转写完成！")

                                    # Show transcription preview
                                    with st.expander("查看转写结果"):
                                        st.text_area(
                                            "转写文本",
                                            transcription_text,
                                            height=200,
                                        )

                                    # Fallback: if selected_meeting_title is empty, use first 8 chars of transcription_text
                                    meeting_title_to_use = selected_meeting_title
                                    if (
                                        not meeting_title_to_use
                                        or not meeting_title_to_use.strip()
                                    ):
                                        meeting_title_to_use = (
                                            transcription_text[:8].strip()
                                            or "未命名纪要"
                                        )

                                    # Generate minutes from transcription
                                    generated_minute = generate_minutes_from_text(
                                        transcription_text,
                                        meeting_title_to_use,
                                        (
                                            new_meeting_datetime
                                            if "new_meeting_datetime" in locals()
                                            else None
                                        ),
                                    )

                                    # Debug: Show generated minute result
                                    st.write("生成的纪要数据:", generated_minute)

                                    if generated_minute:
                                        # Check if we're updating an existing meeting
                                        if (
                                            meeting_mode == "选择已有会议"
                                            and selected_meeting_id
                                        ):
                                            # Try to update existing minutes
                                            if self._update_existing_minutes(
                                                selected_meeting_id,
                                                generated_minute,
                                            ):
                                                st.success("会议纪要已更新！")
                                            else:
                                                # If no existing minutes found, add new one with booking_id
                                                generated_minute["booking_id"] = (
                                                    selected_meeting_id
                                                )
                                                self.data_manager.add_minute(
                                                    generated_minute
                                                )
                                                st.success("会议纪要生成完成并已保存！")
                                        else:
                                            # Add new minutes
                                            self.data_manager.add_minute(
                                                generated_minute
                                            )
                                            st.success("会议纪要生成完成并已保存！")

                                        # 立即刷新 minutes_df，以便展示时不依赖过期状态
                                        minutes_df = self.data_manager.get_dataframe(
                                            "minutes"
                                        )
                                        st.rerun()
                                    else:
                                        st.error("生成会议纪要失败，请重试")
                                else:
                                    st.error("转写结果为空，请重试")
                            else:
                                st.error("音频转写失败，请重试")

                        except Exception as e:
                            st.error(f"转写过程中出错: {str(e)}")

        # Minutes list with enhanced features
        st.markdown("---")
        st.markdown("### 纪要列表")

        # Status legend
        st.markdown("#### 📊 状态说明")
        legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)

        with legend_col1:
            st.markdown("🔵 **草稿** - 待确认的会议纪要")
        with legend_col2:
            st.markdown("🟡 **已确认** - 已确认的会议纪要")
        with legend_col3:
            st.markdown("🟢 **已发布** - 已发布的会议纪要")
        with legend_col4:
            st.markdown("⚪ **未知** - 状态未知的会议纪要")

        st.markdown("---")

        if len(minutes_df) > 0:
            # Sort by meeting time (descending)
            try:
                minutes_df_copy = minutes_df.copy()
                minutes_df_copy["created_datetime"] = pd.to_datetime(
                    minutes_df_copy["created_datetime"], errors="coerce"
                )
                minutes_df = minutes_df_copy.sort_values(
                    "created_datetime", ascending=False
                )
            except Exception as e:
                # 如果转换失败，使用原始数据不排序
                print(f"Warning: Could not sort minutes by created_datetime: {e}")
                # Keep original order

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
                    raw_title = minute.get("meeting_title")
                    title = (
                        str(raw_title).strip() if pd.notna(raw_title) else "未命名纪要"
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

                    # Get status color and style
                    status_color = self._get_status_color(status)
                    status_style = self._get_status_style(status)

                    # Create expander with color-coded status
                    expander_title = (
                        f"{status_color} {title} - {status} ({display_time})"
                    )

                    with st.expander(expander_title):
                        # Apply status-based styling to the content
                        st.markdown(
                            f"""
                        <div style="{status_style}">
                        <h4>📋 会议信息</h4>
                        <p><strong>状态:</strong> {status}</p>
                        <p><strong>创建时间:</strong> {display_time}</p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        # 上部内容：会议摘要、与会人员、决策事项、行动项
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 会议摘要")
                            st.write(minute.get("summary", "(无摘要)"))

                            # 显示与会人信息
                            attendees = extract_list_from_text(
                                minute.get("attendees", ""), default_value="未识别"
                            )
                            if attendees and attendees != ["未识别"]:
                                st.markdown("#### 与会人员")
                                for attendee in attendees:
                                    st.markdown(f"• {attendee}")

                            # 显示会议纪要全文（默认收起）
                            original_text = minute.get("original_text", "")
                            if original_text:
                                with st.expander("📄 查看会议纪要全文", expanded=False):
                                    st.text_area(
                                        "会议纪要全文",
                                        value=original_text,
                                        height=300,
                                        disabled=True,
                                        key=f"full_text_{minute_id}_{idx}",
                                    )

                        with col2:
                            # Use the text utility to extract and display decisions
                            decisions = extract_list_from_text(
                                minute.get("key_decisions")
                                or minute.get("decisions", ""),
                                default_value="无",
                            )
                            if decisions and decisions != ["无"]:
                                st.markdown("#### 决策事项")
                                for i, decision in enumerate(decisions, 1):
                                    st.markdown(f"{i}. {decision}")

                            # Use the text utility to extract and display action items
                            action_items = extract_list_from_text(
                                minute.get("action_items", ""), default_value="无"
                            )
                            if action_items and action_items != ["无"]:
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
                                    # 自动生成任务并同步到任务看板
                                    action_items = extract_action_items_from_minutes(
                                        minute
                                    )
                                    attendees = extract_attendees_from_minutes(minute)
                                    meeting_title = (
                                        minute.get("meeting_title")
                                        or minute.get("title")
                                        or ""
                                    )
                                    meeting_id = (
                                        minute.get("booking_id")
                                        or minute.get("meeting_id")
                                        or actual_id
                                    )

                                    # 获取会议数据以获取组织者信息
                                    meeting_data = None
                                    if meeting_id:
                                        meeting_data = (
                                            self.data_manager.get_meeting_by_id(
                                                meeting_id
                                            )
                                        )

                                    # 获取用户数据用于任务校验
                                    users_df = self.data_manager.get_dataframe("users")

                                    tasks = generate_tasks_from_action_items(
                                        action_items,
                                        meeting_title,
                                        meeting_id,
                                        attendees,
                                        meeting_data,
                                        users_df,
                                    )
                                    for task in tasks:
                                        self.data_manager.add_task(task)
                                    if tasks:
                                        st.success(
                                            f"已自动生成{len(tasks)}条任务并同步到任务看板！"
                                        )
                                    st.success("纪要已发布")
                                    st.rerun()
                                else:
                                    st.error("无法更新纪要状态：ID无效")

                        with bcol3:
                            # Check if this minute is in delete confirmation state
                            delete_key = f"delete_confirm_{minute_id}_{idx}"
                            if (
                                delete_key in st.session_state
                                and st.session_state[delete_key]
                            ):
                                # Show confirmation dialog
                                st.warning("⚠️ 您即将删除此会议纪要，此操作不可恢复！")

                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.button(
                                        "✅ 确认删除",
                                        key=f"confirm_delete_{minute_id}_{idx}",
                                        type="primary",
                                    ):
                                        actual_id = minute.get("id") or minute.get(
                                            "minute_id"
                                        )
                                        if actual_id and pd.notna(actual_id):
                                            deleted_minute = (
                                                self.data_manager.delete_minute(
                                                    actual_id
                                                )
                                            )
                                            if deleted_minute:
                                                st.success("✅ 会议纪要已删除")
                                                # Clear the delete confirmation state
                                                if delete_key in st.session_state:
                                                    del st.session_state[delete_key]
                                                st.rerun()
                                            else:
                                                st.error(
                                                    "❌ 删除失败：未找到指定的会议纪要"
                                                )
                                        else:
                                            st.error("无法删除纪要：ID无效")

                                with col_b:
                                    if st.button(
                                        "❌ 取消",
                                        key=f"cancel_delete_{minute_id}_{idx}",
                                    ):
                                        # Clear the delete confirmation state
                                        if delete_key in st.session_state:
                                            del st.session_state[delete_key]
                                        st.rerun()
                            else:
                                # Show delete button
                                if st.button("删除", key=f"delete_{minute_id}_{idx}"):
                                    # Set the delete confirmation state
                                    st.session_state[delete_key] = True
                                    st.rerun()
            else:
                st.info("没有找到符合条件的会议纪要")
        else:
            st.info("暂无会议纪要")

        # 侧边栏功能说明
        st.sidebar.markdown("### 📝 功能说明")
        st.sidebar.markdown(
            """
        **📋 会议纪要管理**:
        - 查看所有会议纪要
        - 按状态、与会人筛选
        - 确认和发布纪要
        - 查看详细内容
        
        **🎨 状态说明**:
        - 草稿：待完善
        - 已确认：内容已确认
        - 已发布：正式发布
        """
        )
