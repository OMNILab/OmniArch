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

    def show(self):
        """Task board page implementation with enhanced functionality"""
        self.ui.create_header("任务看板")

        tasks_df = self.data_manager.get_dataframe("tasks")
        users_df = self.data_manager.get_dataframe("users")
        minutes_df = self.data_manager.get_dataframe("minutes")

        # 将选择关联会议、选择部门、创建任务按钮放在同一行
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            # Get unique meeting titles from minutes
            meeting_options = (
                ["全部会议"] + list(minutes_df["title"].unique())
                if len(minutes_df) > 0
                else ["全部会议"]
            )
            selected_meeting = st.selectbox("会议", meeting_options)

        with col2:
            # Enhanced department filter - 提前显示部门选择
            departments = ["全部"] + list(tasks_df["department"].unique())
            selected_dept = st.selectbox("部门", departments, key="dept_filter")

        with col3:
            st.markdown("")
            st.markdown("")
            if st.button("创建任务", type="primary", key="create_task_btn"):
                st.session_state.show_task_dialog = True

        # Task creation dialog
        if st.session_state.get("show_task_dialog", False):
            with st.container():
                st.markdown("### 创建任务")
                st.markdown("为关联的会议纪要添加新任务")

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
                            value=st.session_state.task_form_data.get(
                                "description", ""
                            ),
                        )
                        # Auto-select meeting if filtered
                        if selected_meeting != "全部会议":
                            st.info(f"关联会议: {selected_meeting}")

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
                            if task_title and task_description:
                                assignee_id = users_df[
                                    users_df["name"] == task_assignee
                                ].iloc[0]["id"]
                                assignee_dept = users_df[
                                    users_df["name"] == task_assignee
                                ].iloc[0]["department"]

                                # Get minute_id for the selected meeting
                                minute_id = None
                                if selected_meeting != "全部会议":
                                    minute_id = (
                                        minutes_df[
                                            minutes_df["title"] == selected_meeting
                                        ]["id"].iloc[0]
                                        if len(
                                            minutes_df[
                                                minutes_df["title"] == selected_meeting
                                            ]
                                        )
                                        > 0
                                        else None
                                    )

                                new_task = {
                                    "title": task_title,
                                    "description": task_description,
                                    "assignee_id": assignee_id,
                                    "department": assignee_dept,
                                    "priority": task_priority,
                                    "status": "草稿",
                                    "deadline": task_deadline,
                                    "minute_id": minute_id,
                                }

                                self.data_manager.add_task(new_task)
                                st.success("任务创建成功！")

                                # Clear form data and close dialog
                                st.session_state.task_form_data = {}
                                st.session_state.show_task_dialog = False
                                st.rerun()
                            else:
                                st.error("请填写完整信息")

                    with col2:
                        if st.form_submit_button("取消", type="secondary"):
                            st.session_state.show_task_dialog = False
                            st.session_state.task_form_data = {}
                            st.rerun()

        # Apply meeting filter
        if selected_meeting != "全部会议":
            # Map minute_id to meeting title for filtering
            # First, get the minute_id for the selected meeting
            selected_minute_id = (
                minutes_df[minutes_df["title"] == selected_meeting]["id"].iloc[0]
                if len(minutes_df[minutes_df["title"] == selected_meeting]) > 0
                else None
            )

            if selected_minute_id is not None:
                filtered_tasks = tasks_df[tasks_df["minute_id"] == selected_minute_id]
            else:
                filtered_tasks = tasks_df
        else:
            filtered_tasks = tasks_df

        # Apply department filter
        if selected_dept != "全部":
            filtered_tasks = filtered_tasks[
                filtered_tasks["department"] == selected_dept
            ]

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
            else:
                st.info("暂无部门任务数据")

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
            else:
                st.info("暂无任务状态数据")

        # Interactive Gantt chart task board
        st.markdown("---")
        st.markdown("### 任务进展")

        # Create Gantt chart data
        if len(filtered_tasks) > 0:
            # Prepare data for Gantt chart
            gantt_data = []
            for _, task in filtered_tasks.iterrows():
                assignee = (
                    users_df[users_df["id"] == task["assignee_id"]]["name"].iloc[0]
                    if len(users_df[users_df["id"] == task["assignee_id"]]) > 0
                    else "未分配"
                )

                # Calculate task duration (7 days default)
                start_date = task.get("created_datetime", datetime.now())
                if isinstance(start_date, str):
                    start_date = pd.to_datetime(start_date)
                end_date = task.get("deadline", start_date + timedelta(days=7))
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(end_date)

                gantt_data.append(
                    {
                        "Task": task["title"],
                        "Assignee": assignee,
                        "Status": task["status"],
                        "Priority": task["priority"],
                        "Start": start_date,
                        "Finish": end_date,
                        "Task_ID": task["id"],
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
                height=400,  # Control height
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(size=10),
                xaxis_title="时间",
                yaxis_title="任务",
                showlegend=True,
            )

            # Make chart responsive
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

            # Task details table below Gantt chart
            st.markdown("---")
            st.markdown("### 任务列表")

            # Create a compact table view
            display_data = []
            for _, task in filtered_tasks.iterrows():
                assignee = (
                    users_df[users_df["id"] == task["assignee_id"]]["name"].iloc[0]
                    if len(users_df[users_df["id"] == task["assignee_id"]]) > 0
                    else "未分配"
                )

                # Map minute_id to meeting title for display
                related_meeting = "无"
                if pd.notna(task.get("minute_id")) and task["minute_id"]:
                    meeting_match = minutes_df[minutes_df["id"] == task["minute_id"]]
                    if len(meeting_match) > 0:
                        related_meeting = meeting_match.iloc[0]["title"]

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
