"""
Tasks Page Module
Contains the tasks page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


class TasksPage:
    """Task board page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def _get_related_meeting_title(self, task, meetings_df, minutes_df):
        """Get related meeting title for a task"""
        related_meeting = "无"

        # Try booking_id first
        if pd.notna(task.get("booking_id")) and task["booking_id"] is not None:
            meeting_match = meetings_df[meetings_df["booking_id"] == task["booking_id"]]
            if len(meeting_match) > 0:
                related_meeting = meeting_match.iloc[0]["meeting_title"]

        # Try minute_id if booking_id not found
        if (
            related_meeting == "无"
            and pd.notna(task.get("minute_id"))
            and task["minute_id"] is not None
        ):
            # Try meetings first
            meeting_match = meetings_df[meetings_df["booking_id"] == task["minute_id"]]
            if len(meeting_match) > 0:
                related_meeting = meeting_match.iloc[0]["meeting_title"]
            else:
                # Try minutes
                meeting_match = minutes_df[minutes_df["minute_id"] == task["minute_id"]]
                if len(meeting_match) > 0:
                    related_meeting = meeting_match.iloc[0]["title"]

        return related_meeting

    def show(self):
        """Task board page implementation with enhanced functionality"""
        self.ui.create_header("任务看板")

        tasks_df = self.data_manager.get_dataframe("tasks")
        users_df = self.data_manager.get_dataframe("users")
        meetings_df = self.data_manager.get_dataframe("meetings")
        minutes_df = self.data_manager.get_dataframe("minutes")

        # Create filter controls
        col1, col2, col3 = st.columns([1, 1, 1])

        # 准备会议过滤器数据
        meetings_options = ["全部"]
        meetings_list = []
        if len(meetings_df) > 0:
            # 创建会议列表，包含开始时间信息
            for _, meeting in meetings_df.iterrows():
                title = meeting.get("meeting_title", "未命名会议")
                start_time = meeting.get("start_datetime", "")
                meeting_status = meeting.get("meeting_status", "upcoming")

                # 处理时间格式
                if start_time:
                    if hasattr(start_time, "strftime"):
                        start_time_dt = start_time
                        start_time_str = start_time.strftime("%m-%d %H:%M")
                    else:
                        try:
                            start_time_dt = pd.to_datetime(start_time)
                            start_time_str = start_time_dt.strftime("%m-%d %H:%M")
                        except:
                            start_time_dt = pd.Timestamp.min
                            start_time_str = str(start_time)[:10]
                else:
                    start_time_dt = pd.Timestamp.min
                    start_time_str = "时间未知"

                # 根据会议状态添加标识（与会议纪要保持一致）
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

                meetings_list.append(
                    {
                        "title": title,
                        "start_time": start_time_dt,
                        "display_text": f"{status_icon} {title} ({start_time_str}) - {status_text}",
                        "meeting_id": meeting.get("booking_id", meeting.get("id")),
                        "meeting_status": meeting_status,
                    }
                )

            # 按开始时间逆序排列（最新的在前面）
            meetings_list.sort(key=lambda x: x["start_time"], reverse=True)

            # 添加到选项列表
            for meeting_info in meetings_list:
                meetings_options.append(meeting_info["display_text"])

        with col1:
            # 会议过滤器
            selected_meeting = st.selectbox(
                "会议", meetings_options, key="meeting_filter"
            )

        with col2:
            departments = (
                ["全部"] + list(tasks_df["department"].unique())
                if len(tasks_df) > 0
                else ["全部"]
            )
            selected_dept = st.selectbox("部门", departments, key="dept_filter")

        with col3:
            st.markdown("")
            st.markdown("")
            if st.button("创建任务", type="primary", key="create_task_btn"):
                st.session_state.show_task_dialog = True

        # Task creation dialog
        if st.session_state.get("show_task_dialog", False):
            self._show_task_creation_dialog(meetings_df, minutes_df, users_df)

        # Apply filters
        filtered_tasks = tasks_df

        # Apply meeting filter
        if selected_meeting != "全部":
            # 从选中的会议选项中提取会议标题（去除状态图标）
            # 格式: "🕐 会议标题 (时间) - 状态"
            meeting_title = selected_meeting.split(" (")[0]
            if (
                meeting_title.startswith("🕐 ")
                or meeting_title.startswith("🔄 ")
                or meeting_title.startswith("✅ ")
            ):
                meeting_title = meeting_title[2:]  # 移除状态图标

            # 查找对应的会议ID
            selected_meeting_id = None
            for meeting_info in meetings_list:
                if meeting_info["title"] == meeting_title:
                    selected_meeting_id = meeting_info["meeting_id"]
                    break

            if selected_meeting_id:
                # 过滤与选中会议相关的任务
                meeting_related_tasks = filtered_tasks[
                    (filtered_tasks["booking_id"] == selected_meeting_id)
                    | (filtered_tasks["minute_id"] == selected_meeting_id)
                ]
                filtered_tasks = meeting_related_tasks

        # Apply department filter
        if selected_dept != "全部":
            filtered_tasks = filtered_tasks[
                filtered_tasks["department"] == selected_dept
            ]

        # Show statistics
        st.markdown("---")
        st.markdown("### 任务统计")
        self._show_task_statistics(filtered_tasks)

        # Show task progress
        self._show_task_progress(filtered_tasks, users_df, meetings_df, minutes_df)

        # Show sidebar help
        self._show_sidebar_help()

    def _show_task_creation_dialog(self, meetings_df, minutes_df, users_df):
        """Show task creation dialog"""
        with st.container():
            st.markdown("### 创建任务")
            st.markdown("创建新任务")

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

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("创建任务", type="primary"):
                        self._create_task(
                            task_title,
                            task_description,
                            task_assignee,
                            task_priority,
                            task_deadline,
                            meetings_df,
                            minutes_df,
                            users_df,
                        )

                with col2:
                    if st.form_submit_button("取消", type="secondary"):
                        st.session_state.show_task_dialog = False
                        st.session_state.task_form_data = {}
                        st.rerun()

    def _create_task(
        self,
        task_title,
        task_description,
        task_assignee,
        task_priority,
        task_deadline,
        meetings_df,
        minutes_df,
        users_df,
    ):
        """Create a new task"""
        if task_title and task_description:
            assignee_id = users_df[users_df["name"] == task_assignee].iloc[0]["user_id"]
            assignee_dept_id = users_df[users_df["name"] == task_assignee].iloc[0][
                "department_id"
            ]

            new_task = {
                "title": task_title,
                "description": task_description,
                "assignee_id": assignee_id,
                "department_id": assignee_dept_id,
                "priority": task_priority,
                "status": "草稿",
                "deadline": task_deadline,
                "minute_id": None,
                "booking_id": None,
            }

            self.data_manager.add_task(new_task)
            st.success("任务创建成功！")

            # Clear form data and close dialog
            st.session_state.task_form_data = {}
            st.session_state.show_task_dialog = False
            st.rerun()
        else:
            st.error("请填写完整信息")

    def _show_task_statistics(self, filtered_tasks):
        """Show task statistics charts"""
        col1, col2 = st.columns(2)

        with col1:
            if len(filtered_tasks) > 0 and "department" in filtered_tasks.columns:
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
                else:
                    st.info("暂无部门任务数据")
            else:
                st.info("暂无部门任务数据")

        with col2:
            if len(filtered_tasks) > 0 and "status" in filtered_tasks.columns:
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
                else:
                    st.info("暂无任务状态数据")
            else:
                st.info("暂无任务状态数据")

    def _show_task_progress(self, filtered_tasks, users_df, meetings_df, minutes_df):
        """Show task progress with Gantt chart and task list"""
        st.markdown("---")
        st.markdown("### 任务进展")

        if len(filtered_tasks) > 0:
            # Prepare Gantt chart data
            gantt_data = []
            for _, task in filtered_tasks.iterrows():
                assignee = (
                    users_df[users_df["user_id"] == task["assignee_id"]]["name"].iloc[0]
                    if len(users_df[users_df["user_id"] == task["assignee_id"]]) > 0
                    else "未分配"
                )

                # Calculate task duration
                start_date = task.get("created_datetime", datetime.now())
                if isinstance(start_date, str):
                    start_date = pd.to_datetime(start_date)

                end_date = task.get("deadline")
                if end_date is None:
                    end_date = start_date + timedelta(days=7)
                elif isinstance(end_date, str):
                    end_date = pd.to_datetime(end_date)

                gantt_data.append(
                    {
                        "Task": task["title"],
                        "Assignee": assignee,
                        "Status": task["status"],
                        "Priority": task["priority"],
                        "Start": start_date,
                        "Finish": end_date,
                        "Task_ID": task["task_id"],
                    }
                )

            gantt_df = pd.DataFrame(gantt_data)

            # Create interactive Gantt chart
            fig = px.timeline(
                gantt_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Status",
                hover_data=["Assignee", "Priority", "Status"],
                title="",
                color_discrete_map={
                    "草稿": "#FF6B6B",
                    "确认": "#4ECDC4",
                    "进行中": "#45B7D1",
                    "完成": "#96CEB4",
                },
            )

            fig.update_layout(
                height=400,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(size=10),
                xaxis_title="时间",
                yaxis_title="任务",
                showlegend=True,
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(count=7, label="1周", step="day", stepmode="backward"),
                            dict(
                                count=30, label="1月", step="day", stepmode="backward"
                            ),
                            dict(
                                count=90, label="3月", step="day", stepmode="backward"
                            ),
                            dict(step="all", label="全部"),
                        ]
                    )
                ),
            )

            st.plotly_chart(fig, use_container_width=True, height=400)

            # Task details table
            st.markdown("---")
            st.markdown("### 任务列表")

            display_data = []
            for _, task in filtered_tasks.iterrows():
                assignee = (
                    users_df[users_df["user_id"] == task["assignee_id"]]["name"].iloc[0]
                    if len(users_df[users_df["user_id"] == task["assignee_id"]]) > 0
                    else "未分配"
                )

                related_meeting = self._get_related_meeting_title(
                    task, meetings_df, minutes_df
                )

                display_data.append(
                    {
                        "任务": task["title"],
                        "负责人": assignee,
                        "状态": task["status"],
                        "优先级": task["priority"],
                        "截止日期": task["deadline"],
                        "关联会议": related_meeting,
                    }
                )

            display_df = pd.DataFrame(display_data)
            st.dataframe(display_df, use_container_width=True, height=300)
        else:
            st.info("没有找到符合条件的任务")

    def _show_sidebar_help(self):
        """Show sidebar help information"""
        st.sidebar.markdown("### 📋 功能说明")
        st.sidebar.markdown(
            """
        **📊 任务管理**:
        - 查看所有任务进展
        - 按会议和部门筛选
        - 甘特图时间线显示
        - 任务状态统计
        
        **🔍 筛选功能**:
        - 会议筛选：显示特定会议的任务
        - 部门筛选：显示特定部门的任务
        - 组合筛选：同时按会议和部门筛选
        
        **📅 会议状态**:
        - 实时显示正在进行的会议
        - 即将到来的会议提醒
        - 会议时间倒计时
        
        **🎯 任务状态**:
        - 草稿：待确认
        - 确认：已确认
        - 进行中：执行中
        - 完成：已完成
        """
        )
