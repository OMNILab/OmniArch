"""
Minutes Page Module
Contains the minutes page implementation for the smart meeting system
"""

import streamlit as st


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

        # Select meeting for minutes
        meetings_df = self.data_manager.get_dataframe("meetings")
        meeting_options = [
            f"{row['title']} - {row['start_time']}" for _, row in meetings_df.iterrows()
        ]

        if len(meeting_options) > 0:
            selected_meeting_option = st.selectbox("选择会议", meeting_options)
            selected_meeting_id = meetings_df.iloc[
                meeting_options.index(selected_meeting_option)
            ]["id"]
        else:
            st.warning("暂无会议记录")
            selected_meeting_id = None

        col1, col2 = st.columns(2)

        with col1:
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

        with col2:
            uploaded_text = st.file_uploader(
                "上传文本文件", type=["txt", "docx", "pdf"]
            )
            if uploaded_text:
                st.success(f"已上传: {uploaded_text.name}")
                if st.button("生成纪要", type="primary"):
                    with st.spinner("正在生成会议纪要..."):
                        import time

                        time.sleep(2)  # Simulate processing
                        st.success("纪要生成完成！")
                        st.session_state.minute_form_data["auto_generated"] = True

        # Manual minutes creation
        st.markdown("---")
        st.markdown("### 手动创建纪要")

        with st.form("minutes_form"):
            minutes_title = st.text_input(
                "纪要标题",
                placeholder="请输入纪要标题",
                value=st.session_state.minute_form_data.get("title", ""),
            )

            minutes_summary = st.text_area(
                "会议摘要",
                placeholder="请输入会议摘要",
                value=st.session_state.minute_form_data.get("summary", ""),
                height=100,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 决策事项")
                decisions = st.text_area(
                    "决策事项（每行一项）",
                    placeholder="请输入决策事项，每行一项",
                    value=st.session_state.minute_form_data.get("decisions", ""),
                    height=100,
                )

            with col2:
                st.markdown("#### 行动项")
                action_items = st.text_area(
                    "行动项（每行一项）",
                    placeholder="请输入行动项，每行一项",
                    value=st.session_state.minute_form_data.get("action_items", ""),
                    height=100,
                )

            if st.form_submit_button("保存纪要", type="primary"):
                if minutes_title and minutes_summary and selected_meeting_id:
                    new_minute = {
                        "meeting_id": selected_meeting_id,
                        "title": minutes_title,
                        "summary": minutes_summary,
                        "decisions": decisions.split("\n") if decisions else [],
                        "action_items": (
                            action_items.split("\n") if action_items else []
                        ),
                        "participants": [],
                        "status": "草稿",
                    }

                    self.data_manager.add_minute(new_minute)
                    st.success("纪要保存成功！")

                    # Clear form data
                    st.session_state.minute_form_data = {}
                    st.rerun()
                else:
                    st.error("请填写完整信息")

        # Minutes list
        st.markdown("---")
        st.markdown("### 纪要列表")

        if len(minutes_df) > 0:
            for _, minute in minutes_df.iterrows():
                with st.expander(f"{minute['title']} - {minute['status']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### 会议摘要")
                        st.write(minute["summary"])

                        if minute["decisions"]:
                            st.markdown("#### 决策事项")
                            for i, decision in enumerate(minute["decisions"], 1):
                                st.markdown(f"{i}. {decision}")

                    with col2:
                        if minute["action_items"]:
                            st.markdown("#### 行动项")
                            for i, action in enumerate(minute["action_items"], 1):
                                st.markdown(f"{i}. {action}")

                        st.markdown("#### 操作")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("确认", key=f"confirm_{minute['id']}"):
                                self.data_manager.update_minute_status(
                                    minute["id"], "已确认"
                                )
                                st.success("纪要已确认")
                                st.rerun()
                        with col2:
                            if st.button("发布", key=f"publish_{minute['id']}"):
                                self.data_manager.update_minute_status(
                                    minute["id"], "已发布"
                                )
                                st.success("纪要已发布")
                                st.rerun()
                        with col3:
                            if st.button("删除", key=f"delete_{minute['id']}"):
                                st.warning("删除功能暂未实现")
        else:
            st.info("暂无会议纪要")