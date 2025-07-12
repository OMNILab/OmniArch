"""
Pages Module
Contains all page implementations for the smart meeting system with enhanced functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from modules.ui_components import UIComponents
import json


class Pages:
    """Contains all page implementations with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components
        self._init_page_state()

    def _init_page_state(self):
        """Initialize page-specific session state"""
        if "booking_form_data" not in st.session_state:
            st.session_state.booking_form_data = {}
        if "task_form_data" not in st.session_state:
            st.session_state.task_form_data = {}
        if "minute_form_data" not in st.session_state:
            st.session_state.minute_form_data = {}
        if "selected_meetings" not in st.session_state:
            st.session_state.selected_meetings = []
        if "selected_tasks" not in st.session_state:
            st.session_state.selected_tasks = []

    def show_login_page(self):
        """Login page implementation"""
        st.markdown('<h1 class="main-header">智慧会议系统</h1>', unsafe_allow_html=True)

        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 用户登录")

            # Show login attempts if any
            if st.session_state.get("login_attempts", 0) > 0:
                st.info(f"登录尝试次数: {st.session_state.login_attempts}")

            with st.form("login_form"):
                username = st.text_input("用户名", placeholder="请输入用户名")
                password = st.text_input(
                    "密码", type="password", placeholder="请输入密码"
                )

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("登录", type="primary")
                with col2:
                    if st.form_submit_button("重置"):
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Demo users help
            st.markdown(
                """
            **演示用户提示：**
            - 输入任意用户名和密码即可登录
            - 系统会自动创建演示用户
            - 数据仅在当前会话中保存
            """
            )

            # Handle login outside form
            if submitted:
                if username and password:
                    if self.auth_manager.login(username, password):
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("登录失败，请检查用户名和密码")
                else:
                    st.warning("请输入用户名和密码")

    def show_booking_page(self):
        """Smart booking page implementation with enhanced functionality"""
        self.ui.create_header("智能预定")

        # Enhanced booking statistics
        col1, col2, col3, col4 = st.columns(4)

        dashboard_data = self.data_manager.get_dashboard_data()

        with col1:
            self.ui.create_metric_card(
                "今日会议", str(dashboard_data["meetings_today"])
            )

        with col2:
            self.ui.create_metric_card(
                "可用会议室", str(dashboard_data["available_rooms"])
            )

        with col3:
            self.ui.create_metric_card(
                "总会议数", str(dashboard_data["total_meetings"])
            )

        with col4:
            self.ui.create_metric_card(
                "平均时长", f"{dashboard_data['avg_meeting_duration']:.0f}分钟"
            )

        # Room recommendations with real data
        st.markdown("---")
        st.markdown("### 会议室推荐")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### 会议日历")

            # Generate real calendar data from meetings
            meetings_df = self.data_manager.get_dataframe("meetings")
            rooms_df = self.data_manager.get_dataframe("rooms")

            # Create calendar view for today
            today = datetime.now().date()
            today_meetings = meetings_df[
                pd.to_datetime(meetings_df["start_time"]).dt.date == today
            ]

            if len(today_meetings) > 0:
                calendar_data = []
                time_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

                for time_slot in time_slots:
                    row = {"时间": time_slot}
                    for _, room in rooms_df.head(3).iterrows():
                        # Check if room is booked at this time
                        slot_time = datetime.strptime(
                            f"{today} {time_slot}", "%Y-%m-%d %H:%M"
                        )
                        room_meetings = today_meetings[
                            today_meetings["room_id"] == room["id"]
                        ]

                        is_booked = False
                        for _, meeting in room_meetings.iterrows():
                            meeting_start = pd.to_datetime(meeting["start_time"])
                            meeting_end = pd.to_datetime(meeting["end_time"])
                            if meeting_start <= slot_time < meeting_end:
                                is_booked = True
                                break

                        row[room["name"]] = "已预订" if is_booked else "可用"

                    calendar_data.append(row)

                calendar_df = pd.DataFrame(calendar_data)
                st.dataframe(calendar_df, use_container_width=True)
            else:
                st.info("今日暂无会议安排")

        with col2:
            st.markdown("#### 推荐会议室")

            # Room recommendations based on availability
            available_rooms = rooms_df[rooms_df["status"] == "可用"].head(3)

            for _, room in available_rooms.iterrows():
                self.ui.create_room_card(room.to_dict())

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"预定 {room['name']}", key=f"book_{room['id']}"):
                        st.session_state.booking_form_data["selected_room"] = room[
                            "name"
                        ]
                        st.success(f"已选择 {room['name']}")
                with col2:
                    if st.button(f"详情", key=f"details_{room['id']}"):
                        st.info(
                            f"会议室详情: {room['name']} - 容量{room['capacity']}人 - 设备: {room['equipment']}"
                        )

        # Enhanced booking form with session state
        st.markdown("---")
        st.markdown("### 预定确认")

        with st.form("booking_form"):
            col1, col2 = st.columns(2)

            with col1:
                meeting_title = st.text_input(
                    "会议主题",
                    placeholder="请输入会议主题",
                    value=st.session_state.booking_form_data.get("title", ""),
                )
                meeting_date = st.date_input(
                    "会议日期",
                    value=st.session_state.booking_form_data.get(
                        "date", datetime.now().date()
                    ),
                )
                meeting_time = st.time_input(
                    "会议时间",
                    value=st.session_state.booking_form_data.get(
                        "time", datetime.now().time()
                    ),
                )

            with col2:
                participants = st.number_input(
                    "参与人数",
                    min_value=1,
                    max_value=50,
                    value=st.session_state.booking_form_data.get("participants", 10),
                )
                room_selection = st.selectbox(
                    "选择会议室",
                    rooms_df["name"].tolist(),
                    index=(
                        rooms_df["name"]
                        .tolist()
                        .index(
                            st.session_state.booking_form_data.get(
                                "selected_room", rooms_df["name"].iloc[0]
                            )
                        )
                        if st.session_state.booking_form_data.get("selected_room")
                        in rooms_df["name"].tolist()
                        else 0
                    ),
                )
                meeting_type = st.selectbox(
                    "会议类型",
                    ["项目讨论", "产品评审", "技术分享", "团队会议", "客户会议"],
                    index=[
                        "项目讨论",
                        "产品评审",
                        "技术分享",
                        "团队会议",
                        "客户会议",
                    ].index(st.session_state.booking_form_data.get("type", "项目讨论")),
                )

            meeting_description = st.text_area(
                "会议描述",
                placeholder="请输入会议描述",
                value=st.session_state.booking_form_data.get("description", ""),
            )

            col1, col2, col3 = st.columns(3)
            with col2:
                if st.form_submit_button("确认预定", type="primary"):
                    if meeting_title and room_selection:
                        # Create new meeting
                        selected_room = rooms_df[
                            rooms_df["name"] == room_selection
                        ].iloc[0]

                        new_meeting = {
                            "title": meeting_title,
                            "room_id": selected_room["id"],
                            "organizer_id": self.auth_manager.get_user_id(),
                            "start_time": datetime.combine(meeting_date, meeting_time),
                            "end_time": datetime.combine(meeting_date, meeting_time)
                            + timedelta(hours=1),
                            "duration": 60,
                            "participants": participants,
                            "type": meeting_type,
                            "status": "已确认",
                            "description": meeting_description,
                        }

                        self.data_manager.add_meeting(new_meeting)
                        st.success("预定成功！")

                        # Clear form data
                        st.session_state.booking_form_data = {}
                        st.rerun()
                    else:
                        st.error("请填写完整信息")

        # Recent bookings
        st.markdown("---")
        st.markdown("### 我的预定")

        current_user_meetings = self.data_manager.get_dataframe("meetings")
        current_user_meetings = current_user_meetings[
            current_user_meetings["organizer_id"] == self.auth_manager.get_user_id()
        ].tail(5)

        if len(current_user_meetings) > 0:
            for _, meeting in current_user_meetings.iterrows():
                with st.expander(f"{meeting['title']} - {meeting['start_time']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**状态：** {meeting['status']}")
                        st.write(f"**类型：** {meeting['type']}")
                    with col2:
                        st.write(f"**参与人数：** {meeting['participants']}")
                        st.write(f"**时长：** {meeting['duration']}分钟")
                    with col3:
                        if st.button("取消预定", key=f"cancel_{meeting['id']}"):
                            self.data_manager.update_meeting_status(
                                meeting["id"], "已取消"
                            )
                            st.success("预定已取消")
                            st.rerun()
        else:
            st.info("暂无预定记录")

    def show_minutes_page(self):
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

    def show_tasks_page(self):
        """Task board page implementation with enhanced functionality"""
        self.ui.create_header("任务看板")

        # Enhanced task statistics
        col1, col2, col3, col4 = st.columns(4)

        tasks_df = self.data_manager.get_dataframe("tasks")
        users_df = self.data_manager.get_dataframe("users")

        with col1:
            self.ui.create_metric_card("总任务数", str(len(tasks_df)))

        with col2:
            completed_tasks = len(tasks_df[tasks_df["status"] == "完成"])
            self.ui.create_metric_card("已完成", str(completed_tasks))

        with col3:
            in_progress = len(tasks_df[tasks_df["status"] == "进行中"])
            self.ui.create_metric_card("进行中", str(in_progress))

        with col4:
            pending = len(tasks_df[tasks_df["status"] == "草稿"])
            self.ui.create_metric_card("待处理", str(pending))

        # Enhanced task creation
        st.markdown("---")
        st.markdown("### 创建任务")

        with st.form("task_form"):
            col1, col2 = st.columns(2)

            with col1:
                task_title = st.text_input(
                    "任务标题",
                    placeholder="请输入任务标题",
                    value=st.session_state.task_form_data.get("title", ""),
                )
                task_description = st.text_area(
                    "任务描述",
                    placeholder="请输入任务描述",
                    value=st.session_state.task_form_data.get("description", ""),
                )

            with col2:
                task_assignee = st.selectbox(
                    "分配给",
                    users_df["name"].tolist(),
                    index=(
                        users_df["name"]
                        .tolist()
                        .index(
                            st.session_state.task_form_data.get(
                                "assignee", users_df["name"].iloc[0]
                            )
                        )
                        if st.session_state.task_form_data.get("assignee")
                        in users_df["name"].tolist()
                        else 0
                    ),
                )
                task_priority = st.selectbox(
                    "优先级",
                    ["高", "中", "低"],
                    index=["高", "中", "低"].index(
                        st.session_state.task_form_data.get("priority", "中")
                    ),
                )
                task_deadline = st.date_input(
                    "截止日期",
                    value=st.session_state.task_form_data.get(
                        "deadline", datetime.now().date() + timedelta(days=7)
                    ),
                )

            if st.form_submit_button("创建任务", type="primary"):
                if task_title and task_description:
                    assignee_id = users_df[users_df["name"] == task_assignee].iloc[0][
                        "id"
                    ]
                    assignee_dept = users_df[users_df["name"] == task_assignee].iloc[0][
                        "department"
                    ]

                    new_task = {
                        "title": task_title,
                        "description": task_description,
                        "assignee_id": assignee_id,
                        "department": assignee_dept,
                        "priority": task_priority,
                        "status": "草稿",
                        "deadline": task_deadline,
                    }

                    self.data_manager.add_task(new_task)
                    st.success("任务创建成功！")

                    # Clear form data
                    st.session_state.task_form_data = {}
                    st.rerun()
                else:
                    st.error("请填写完整信息")

        # Task board view with enhanced functionality
        st.markdown("---")
        st.markdown("### 任务看板")

        # Enhanced department filter
        departments = ["全部"] + list(tasks_df["department"].unique())
        selected_dept = st.selectbox("选择部门", departments)

        if selected_dept != "全部":
            filtered_tasks = tasks_df[tasks_df["department"] == selected_dept]
        else:
            filtered_tasks = tasks_df

        # Task status columns
        status_columns = ["草稿", "确认", "进行中", "完成"]
        cols = st.columns(len(status_columns))

        for i, status in enumerate(status_columns):
            with cols[i]:
                st.markdown(f"#### {status}")

                status_tasks = filtered_tasks[filtered_tasks["status"] == status]

                for _, task in status_tasks.iterrows():
                    assignee = (
                        users_df[users_df["id"] == task["assignee_id"]]["name"].iloc[0]
                        if len(users_df[users_df["id"] == task["assignee_id"]]) > 0
                        else "未分配"
                    )

                    with st.container():
                        st.markdown(f"**{task['title']}**")
                        st.write(f"负责人: {assignee}")
                        st.write(f"优先级: {task['priority']}")
                        st.write(f"截止: {task['deadline']}")

                        # Status update buttons
                        next_status = None
                        if status == "草稿":
                            next_status = "确认"
                        elif status == "确认":
                            next_status = "进行中"
                        elif status == "进行中":
                            next_status = "完成"

                        if next_status:
                            if st.button(
                                f"→ {next_status}", key=f"update_{task['id']}_{status}"
                            ):
                                self.data_manager.update_task_status(
                                    task["id"], next_status
                                )
                                st.success(f"任务状态已更新为 {next_status}")
                                st.rerun()

                        st.markdown("---")

        # Enhanced task statistics chart
        st.markdown("---")
        st.markdown("### 任务统计")

        col1, col2 = st.columns(2)

        with col1:
            dept_task_counts = filtered_tasks["department"].value_counts()

            if len(dept_task_counts) > 0:
                fig = px.bar(
                    x=dept_task_counts.index,
                    y=dept_task_counts.values,
                    title="各部门任务数量",
                    labels={"x": "部门", "y": "任务数量"},
                    color=dept_task_counts.values,
                    color_continuous_scale="viridis",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12),
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Status distribution pie chart
            status_counts = filtered_tasks["status"].value_counts()

            if len(status_counts) > 0:
                fig2 = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="任务状态分布",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig2.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12),
                )

                st.plotly_chart(fig2, use_container_width=True)

    def show_dashboard_page(self):
        """Data dashboard page implementation with enhanced real-time data"""
        self.ui.create_header("数据面板")

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "开始日期", value=datetime.now() - timedelta(days=30)
            )

        with col2:
            end_date = st.date_input("结束日期", value=datetime.now())

        # Enhanced overall overview with real data
        st.markdown("### 整体概览")

        dashboard_data = self.data_manager.get_dashboard_data()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            self.ui.create_metric_card(
                "总会议数", str(dashboard_data["total_meetings"])
            )

        with col2:
            self.ui.create_metric_card(
                "平均时长", f"{dashboard_data['avg_meeting_duration']:.0f}分钟"
            )

        with col3:
            self.ui.create_metric_card(
                "已完成任务", str(dashboard_data["completed_tasks"])
            )

        with col4:
            self.ui.create_metric_card(
                "可用会议室", str(dashboard_data["available_rooms"])
            )

        # Real-time data refresh
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("刷新数据", type="primary"):
                st.rerun()

        # Enhanced room usage charts with real data
        st.markdown("---")
        st.markdown("### 会议室使用分析")

        col1, col2 = st.columns(2)

        meetings_df = self.data_manager.get_dataframe("meetings")
        rooms_df = self.data_manager.get_dataframe("rooms")

        with col1:
            st.markdown("#### 会议室使用频率")

            # Room usage analysis
            if len(meetings_df) > 0:
                room_usage = (
                    meetings_df.groupby("room_id")
                    .size()
                    .reset_index(name="usage_count")
                )
                room_usage = room_usage.merge(
                    rooms_df[["id", "name"]], left_on="room_id", right_on="id"
                )

                fig = px.bar(
                    room_usage,
                    x="name",
                    y="usage_count",
                    title="会议室使用频率",
                    labels={"name": "会议室", "usage_count": "使用次数"},
                    color="usage_count",
                    color_continuous_scale="viridis",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12),
                    xaxis_tickangle=-45,
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无会议数据")

        with col2:
            st.markdown("#### 会议时长分布")

            if len(meetings_df) > 0:
                duration_bins = [0, 30, 60, 90, 120, 150, 180]
                duration_labels = [
                    "0-30min",
                    "30-60min",
                    "60-90min",
                    "90-120min",
                    "120-150min",
                    "150-180min",
                ]

                meetings_df["duration_bin"] = pd.cut(
                    meetings_df["duration"], bins=duration_bins, labels=duration_labels
                )
                duration_dist = meetings_df["duration_bin"].value_counts().sort_index()

                fig = px.pie(
                    values=duration_dist.values,
                    names=duration_dist.index,
                    title="会议时长分布",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12),
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无会议数据")

        # Enhanced department usage analysis
        st.markdown("---")
        st.markdown("### 部门使用概览")

        # Real department data analysis
        users_df = self.data_manager.get_dataframe("users")
        tasks_df = self.data_manager.get_dataframe("tasks")

        if len(users_df) > 0 and len(tasks_df) > 0:
            dept_usage = (
                tasks_df.groupby("department")
                .agg({"id": "count", "status": lambda x: (x == "完成").sum()})
                .reset_index()
            )
            dept_usage.columns = ["department", "total_tasks", "completed_tasks"]

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    dept_usage,
                    x="department",
                    y="total_tasks",
                    title="各部门任务数量",
                    labels={"department": "部门", "total_tasks": "任务数量"},
                    color="total_tasks",
                    color_continuous_scale="plasma",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(
                    dept_usage,
                    x="department",
                    y="completed_tasks",
                    title="各部门完成任务数",
                    labels={"department": "部门", "completed_tasks": "完成数量"},
                    color="completed_tasks",
                    color_continuous_scale="inferno",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无部门数据")

        # Data export functionality
        st.markdown("---")
        st.markdown("### 数据导出")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("导出会议数据 (CSV)", type="primary"):
                csv_data = meetings_df.to_csv(index=False)
                st.download_button(
                    label="下载会议数据",
                    data=csv_data,
                    file_name="meetings_data.csv",
                    mime="text/csv",
                )

        with col2:
            if st.button("导出任务数据 (CSV)", type="primary"):
                csv_data = tasks_df.to_csv(index=False)
                st.download_button(
                    label="下载任务数据",
                    data=csv_data,
                    file_name="tasks_data.csv",
                    mime="text/csv",
                )

        with col3:
            if st.button("重置数据", type="secondary"):
                if st.button("确认重置", key="confirm_reset"):
                    self.data_manager.reset_to_default()
                    st.rerun()

    def show_settings_page(self):
        """System settings page implementation"""
        self.ui.create_header("系统设置")

        # Check admin privileges
        self.auth_manager.require_admin()

        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["用户管理", "组织架构管理", "系统配置", "数据管理"]
        )

        with tab1:
            st.markdown("### 用户管理")

            users_df = self.data_manager.get_dataframe("users")

            # User management interface
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### 用户列表")

                # Enhanced user table with actions
                if len(users_df) > 0:
                    gb = GridOptionsBuilder.from_dataframe(
                        users_df[["username", "name", "department", "role", "email"]]
                    )
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_side_bar()
                    gb.configure_selection("multiple", use_checkbox=True)
                    grid_options = gb.build()

                    grid_response = AgGrid(
                        users_df[["username", "name", "department", "role", "email"]],
                        gridOptions=grid_options,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        height=400,
                    )
                else:
                    st.info("暂无用户数据")

            with col2:
                st.markdown("#### 用户统计")

                if len(users_df) > 0:
                    # User statistics
                    role_counts = users_df["role"].value_counts()
                    dept_counts = users_df["department"].value_counts()

                    st.metric("总用户数", len(users_df))
                    st.metric(
                        "管理员数", len(users_df[users_df["role"] == "系统管理员"])
                    )
                    st.metric(
                        "组织者数", len(users_df[users_df["role"] == "会议组织者"])
                    )

                    # Role distribution
                    fig = px.pie(
                        values=role_counts.values,
                        names=role_counts.index,
                        title="用户角色分布",
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 组织架构管理")

            users_df = self.data_manager.get_dataframe("users")

            if len(users_df) > 0:
                # Organization data
                org_data = (
                    users_df.groupby("department")
                    .agg({"id": "count", "name": "first"})
                    .reset_index()
                )
                org_data.columns = ["部门", "人数", "示例成员"]
                org_data["状态"] = "正常"

                st.dataframe(org_data, use_container_width=True)

                # Department statistics
                fig = px.bar(
                    org_data,
                    x="部门",
                    y="人数",
                    title="各部门人数统计",
                    color="人数",
                    color_continuous_scale="viridis",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无组织架构数据")

        with tab3:
            st.markdown("### 系统配置")

            # User preferences
            preferences = self.auth_manager.get_user_preferences()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 界面设置")

                theme = st.selectbox(
                    "主题",
                    ["light", "dark"],
                    index=0 if preferences.get("theme") == "light" else 1,
                )

                language = st.selectbox(
                    "语言",
                    ["zh_CN", "en_US"],
                    index=0 if preferences.get("language") == "zh_CN" else 1,
                )

                if st.button("保存界面设置"):
                    self.auth_manager.update_user_preference("theme", theme)
                    self.auth_manager.update_user_preference("language", language)
                    st.success("设置已保存")

            with col2:
                st.markdown("#### 功能设置")

                notifications = st.checkbox(
                    "启用通知", value=preferences.get("notifications", True)
                )

                auto_save = st.checkbox(
                    "自动保存", value=preferences.get("auto_save", True)
                )

                if st.button("保存功能设置"):
                    self.auth_manager.update_user_preference(
                        "notifications", notifications
                    )
                    self.auth_manager.update_user_preference("auto_save", auto_save)
                    st.success("设置已保存")

        with tab4:
            st.markdown("### 数据管理")

            dashboard_data = self.data_manager.get_dashboard_data()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 数据统计")

                st.metric("会议数据", dashboard_data["total_meetings"])
                st.metric("任务数据", dashboard_data["total_tasks"])
                st.metric("用户数据", dashboard_data["total_users"])
                st.metric("会议室数据", dashboard_data["total_rooms"])

            with col2:
                st.markdown("#### 数据操作")

                st.warning("⚠️ 以下操作将影响所有数据")

                if st.button("重置所有数据", type="secondary"):
                    if st.button("确认重置所有数据", key="admin_reset"):
                        self.data_manager.reset_to_default()
                        st.success("所有数据已重置")
                        st.rerun()

                if st.button("导出系统数据", type="primary"):
                    # Export all data as JSON
                    all_data = self.data_manager.get_data()
                    json_data = json.dumps(
                        all_data, default=str, ensure_ascii=False, indent=2
                    )

                    st.download_button(
                        label="下载系统数据",
                        data=json_data,
                        file_name="system_data.json",
                        mime="application/json",
                    )

    def show_pandasai_demo(self):
        """PandasAI demo page implementation with enhanced functionality"""
        self.ui.create_header("智能数据分析")

        st.markdown("### 数据分析工具")

        # Data source selection
        data_sources = ["会议数据", "任务数据", "用户数据", "会议室数据"]
        selected_source = st.selectbox("选择数据源", data_sources)

        # Get selected data
        if selected_source == "会议数据":
            sample_data = self.data_manager.get_dataframe("meetings")
        elif selected_source == "任务数据":
            sample_data = self.data_manager.get_dataframe("tasks")
        elif selected_source == "用户数据":
            sample_data = self.data_manager.get_dataframe("users")
        else:
            sample_data = self.data_manager.get_dataframe("rooms")

        if len(sample_data) > 0:
            st.markdown(f"#### {selected_source}")

            # Show data preview
            with st.expander("数据预览"):
                st.dataframe(sample_data.head(10), use_container_width=True)

            # Natural language query
            st.markdown("#### 自然语言查询")

            query = st.text_input(
                "请输入您的问题", placeholder="例如：显示数据的基本统计信息", value=""
            )

            if st.button("分析", type="primary"):
                if query:
                    with st.spinner("正在分析..."):
                        import time

                        time.sleep(1)  # Simulate processing

                        # Mock AI response based on query
                        if "统计" in query or "概览" in query:
                            st.success("分析完成！")
                            st.markdown("#### 数据统计结果")

                            # Show basic statistics
                            numeric_cols = sample_data.select_dtypes(
                                include=["number"]
                            ).columns
                            if len(numeric_cols) > 0:
                                st.dataframe(sample_data[numeric_cols].describe())

                            # Show value counts for categorical columns
                            categorical_cols = sample_data.select_dtypes(
                                include=["object"]
                            ).columns[:3]
                            if len(categorical_cols) > 0:
                                for col in categorical_cols:
                                    if col in sample_data.columns:
                                        st.markdown(f"**{col} 分布:**")
                                        value_counts = sample_data[col].value_counts()

                                        fig = px.bar(
                                            x=value_counts.index,
                                            y=value_counts.values,
                                            title=f"{col} 分布",
                                            labels={"x": col, "y": "数量"},
                                        )
                                        fig.update_layout(height=300)
                                        st.plotly_chart(fig, use_container_width=True)

                        elif "图表" in query or "可视化" in query:
                            st.success("分析完成！")
                            st.markdown("#### 数据可视化")

                            # Create visualization based on data type
                            if selected_source == "会议数据":
                                # Meeting duration distribution
                                fig = px.histogram(
                                    sample_data,
                                    x="duration",
                                    title="会议时长分布",
                                    nbins=20,
                                )
                                st.plotly_chart(fig, use_container_width=True)

                                # Meeting types
                                if "type" in sample_data.columns:
                                    type_counts = sample_data["type"].value_counts()
                                    fig = px.pie(
                                        values=type_counts.values,
                                        names=type_counts.index,
                                        title="会议类型分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif selected_source == "任务数据":
                                # Task status distribution
                                if "status" in sample_data.columns:
                                    status_counts = sample_data["status"].value_counts()
                                    fig = px.bar(
                                        x=status_counts.index,
                                        y=status_counts.values,
                                        title="任务状态分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                # Priority distribution
                                if "priority" in sample_data.columns:
                                    priority_counts = sample_data[
                                        "priority"
                                    ].value_counts()
                                    fig = px.pie(
                                        values=priority_counts.values,
                                        names=priority_counts.index,
                                        title="优先级分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif selected_source == "用户数据":
                                # Department distribution
                                if "department" in sample_data.columns:
                                    dept_counts = sample_data[
                                        "department"
                                    ].value_counts()
                                    fig = px.bar(
                                        x=dept_counts.index,
                                        y=dept_counts.values,
                                        title="部门人数分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                # Role distribution
                                if "role" in sample_data.columns:
                                    role_counts = sample_data["role"].value_counts()
                                    fig = px.pie(
                                        values=role_counts.values,
                                        names=role_counts.index,
                                        title="角色分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            else:  # Room data
                                # Capacity distribution
                                if "capacity" in sample_data.columns:
                                    fig = px.histogram(
                                        sample_data,
                                        x="capacity",
                                        title="会议室容量分布",
                                        nbins=10,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                # Room status
                                if "status" in sample_data.columns:
                                    status_counts = sample_data["status"].value_counts()
                                    fig = px.pie(
                                        values=status_counts.values,
                                        names=status_counts.index,
                                        title="会议室状态分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                        else:
                            st.success("分析完成！")
                            st.info("请尝试更具体的查询，如'显示统计信息'或'生成图表'")

                            # Show basic info
                            st.markdown("#### 数据基本信息")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("总记录数", len(sample_data))

                            with col2:
                                st.metric("字段数", len(sample_data.columns))

                            with col3:
                                if (
                                    len(
                                        sample_data.select_dtypes(
                                            include=["number"]
                                        ).columns
                                    )
                                    > 0
                                ):
                                    st.metric(
                                        "数值字段",
                                        len(
                                            sample_data.select_dtypes(
                                                include=["number"]
                                            ).columns
                                        ),
                                    )
                                else:
                                    st.metric("数值字段", 0)
                else:
                    st.warning("请输入查询内容")
        else:
            st.info(f"暂无{selected_source}，请先创建一些数据")

        # Quick analysis buttons
        st.markdown("---")
        st.markdown("### 快速分析")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("数据概览", type="secondary"):
                if len(sample_data) > 0:
                    st.markdown("#### 数据概览")
                    st.write(f"**数据集:** {selected_source}")
                    st.write(f"**记录数:** {len(sample_data)}")
                    st.write(f"**字段数:** {len(sample_data.columns)}")
                    st.write(f"**字段列表:** {', '.join(sample_data.columns.tolist())}")

        with col2:
            if st.button("基础统计", type="secondary"):
                if len(sample_data) > 0:
                    numeric_cols = sample_data.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) > 0:
                        st.markdown("#### 基础统计")
                        st.dataframe(sample_data[numeric_cols].describe())
                    else:
                        st.info("没有数值型数据")

        with col3:
            if st.button("数据导出", type="secondary"):
                if len(sample_data) > 0:
                    csv_data = sample_data.to_csv(index=False)
                    st.download_button(
                        label="下载数据",
                        data=csv_data,
                        file_name=f"{selected_source}.csv",
                        mime="text/csv",
                    )
