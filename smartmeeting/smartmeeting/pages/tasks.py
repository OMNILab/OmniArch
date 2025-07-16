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
            # Get unique meeting titles from minutes and meetings
            minutes_df = self.data_manager.get_dataframe("minutes")
            meetings_df = self.data_manager.get_dataframe("meetings")

            # 合并会议数据，优先使用meetings数据
            meeting_options = ["全部会议"]
            meeting_status_info = ["all"]  # 存储会议状态信息

            # 从meetings数据中获取会议列表，按开始时间逆序排列
            if len(meetings_df) > 0:
                title_col = (
                    "meeting_title"
                    if "meeting_title" in meetings_df.columns
                    else "title"
                )
                time_col = (
                    "start_datetime"
                    if "start_datetime" in meetings_df.columns
                    else "start_time"
                )

                # 按开始时间逆序排序
                meetings_df_sorted = meetings_df.sort_values(time_col, ascending=False)

                for _, row in meetings_df_sorted.iterrows():
                    title = row.get(title_col, "未命名会议")
                    start_time = row.get(time_col, "未知时间")
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

            # 如果没有meetings数据，从minutes数据中获取
            elif len(minutes_df) > 0:
                # 按创建时间逆序排序
                minutes_df_sorted = minutes_df.sort_values(
                    "created_datetime", ascending=False
                )
                for _, row in minutes_df_sorted.iterrows():
                    title = row.get("title", "未命名会议")
                    meeting_options.append(title)
                    meeting_status_info.append(
                        "completed"
                    )  # minutes中的会议通常是已完成的

            selected_meeting = st.selectbox("会议", meeting_options)
            selected_meeting_status = (
                meeting_status_info[meeting_options.index(selected_meeting)]
                if selected_meeting in meeting_options
                else "all"
            )

            # 显示会议状态警告
            if selected_meeting != "全部会议":
                if selected_meeting_status == "upcoming":
                    st.warning("⚠️ 该会议还未进行，任务可能需要等待会议结束后才能执行")
                elif selected_meeting_status == "ongoing":
                    st.info("🔄 该会议正在进行中，可以创建实时任务")
                elif selected_meeting_status == "completed":
                    st.success("✅ 该会议已完成，可以基于会议结果创建任务")

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

                                # Get meeting association for the selected meeting
                                minute_id = None
                                booking_id = None
                                if selected_meeting != "全部会议":
                                    # 从选中的会议选项中提取会议标题
                                    selected_meeting_title = (
                                        selected_meeting.split(" - ")[0].split(" ", 1)[
                                            1
                                        ]
                                        if " - " in selected_meeting
                                        else selected_meeting
                                    )

                                    # 首先尝试从meetings数据中查找
                                    title_col = (
                                        "meeting_title"
                                        if "meeting_title" in meetings_df.columns
                                        else "title"
                                    )
                                    meeting_match = meetings_df[
                                        meetings_df[title_col] == selected_meeting_title
                                    ]

                                    if len(meeting_match) > 0:
                                        # 找到对应的booking_id
                                        booking_id = meeting_match.iloc[0]["id"]
                                    else:
                                        # 如果meetings中没有找到，尝试从minutes中查找
                                        minute_match = minutes_df[
                                            minutes_df["title"]
                                            == selected_meeting_title
                                        ]
                                        if len(minute_match) > 0:
                                            minute_id = minute_match.iloc[0]["id"]

                                new_task = {
                                    "title": task_title,
                                    "description": task_description,
                                    "assignee_id": assignee_id,
                                    "department": assignee_dept,
                                    "priority": task_priority,
                                    "status": "草稿",
                                    "deadline": task_deadline,
                                    "minute_id": minute_id,
                                    "booking_id": booking_id,
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
            # 从选中的会议选项中提取会议标题
            selected_meeting_title = (
                selected_meeting.split(" - ")[0].split(" ", 1)[1]
                if " - " in selected_meeting
                else selected_meeting
            )

            # 初始化过滤后的任务
            filtered_tasks = pd.DataFrame()

            # 首先尝试从meetings数据中查找（通过booking_id关联）
            title_col = (
                "meeting_title" if "meeting_title" in meetings_df.columns else "title"
            )
            meeting_match = meetings_df[
                meetings_df[title_col] == selected_meeting_title
            ]

            if len(meeting_match) > 0:
                # 找到对应的booking_id
                selected_booking_id = meeting_match.iloc[0]["id"]
                # 使用booking_id进行过滤
                booking_tasks = tasks_df[tasks_df["booking_id"] == selected_booking_id]
                filtered_tasks = pd.concat(
                    [filtered_tasks, booking_tasks], ignore_index=True
                )

                # 调试信息
                st.info(
                    f"🔍 调试信息: 找到会议 '{selected_meeting_title}' (ID: {selected_booking_id})，通过booking_id找到 {len(booking_tasks)} 个任务"
                )

            # 同时尝试从minutes数据中查找（通过minute_id关联）
            minutes_title_col = (
                "meeting_title" if "meeting_title" in minutes_df.columns else "title"
            )
            minute_match = minutes_df[
                minutes_df[minutes_title_col] == selected_meeting_title
            ]

            if len(minute_match) > 0:
                selected_minute_id = minute_match.iloc[0]["id"]
                minute_tasks = tasks_df[tasks_df["minute_id"] == selected_minute_id]
                filtered_tasks = pd.concat(
                    [filtered_tasks, minute_tasks], ignore_index=True
                )

                # 调试信息
                st.info(f"🔍 调试信息: 通过minute_id找到 {len(minute_tasks)} 个任务")

            # 如果都没有找到任务，尝试模糊匹配
            if len(filtered_tasks) == 0:
                # 尝试在任务描述中搜索会议标题关键词
                keyword_tasks = tasks_df[
                    tasks_df["title"].str.contains(
                        selected_meeting_title, case=False, na=False
                    )
                    | tasks_df["description"].str.contains(
                        selected_meeting_title, case=False, na=False
                    )
                ]

                if len(keyword_tasks) > 0:
                    filtered_tasks = keyword_tasks
                    st.info(
                        f"🔍 调试信息: 通过关键词匹配找到 {len(keyword_tasks)} 个任务"
                    )
                else:
                    # 显示所有任务供调试
                    st.warning(f"⚠️ 未找到会议 '{selected_meeting_title}' 相关的任务")
                    st.info(f"🔍 调试信息: 当前所有任务数量: {len(tasks_df)}")
                    st.info(
                        f"🔍 调试信息: 有booking_id的任务数量: {len(tasks_df[tasks_df['booking_id'].notna()])}"
                    )
                    st.info(
                        f"🔍 调试信息: 有minute_id的任务数量: {len(tasks_df[tasks_df['minute_id'].notna()])}"
                    )
            else:
                # 去重，因为同一个任务可能同时有booking_id和minute_id
                filtered_tasks = filtered_tasks.drop_duplicates(subset=["id"])
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
            if len(filtered_tasks) > 0:
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
            # Status distribution pie chart
            if len(filtered_tasks) > 0:
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

                # 首先尝试使用booking_id查找会议
                if pd.notna(task.get("booking_id")) and task["booking_id"]:
                    meeting_match = meetings_df[meetings_df["id"] == task["booking_id"]]
                    if len(meeting_match) > 0:
                        title_col = (
                            "meeting_title"
                            if "meeting_title" in meetings_df.columns
                            else "title"
                        )
                        related_meeting = meeting_match.iloc[0][title_col]

                # 如果booking_id没有找到，尝试使用minute_id
                if (
                    related_meeting == "无"
                    and pd.notna(task.get("minute_id"))
                    and task["minute_id"]
                ):
                    # 首先尝试从meetings数据中查找
                    meeting_match = meetings_df[meetings_df["id"] == task["minute_id"]]
                    if len(meeting_match) > 0:
                        title_col = (
                            "meeting_title"
                            if "meeting_title" in meetings_df.columns
                            else "title"
                        )
                        related_meeting = meeting_match.iloc[0][title_col]
                    else:
                        # 如果meetings中没有找到，从minutes中查找
                        meeting_match = minutes_df[
                            minutes_df["id"] == task["minute_id"]
                        ]
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

        # 侧边栏功能说明
        st.sidebar.markdown("### 📋 功能说明")
        st.sidebar.markdown(
            """
        **📊 任务管理**:
        - 查看所有任务进展
        - 按会议、部门筛选
        - 甘特图时间线显示
        - 任务状态统计
        
        **🎯 任务状态**:
        - 草稿：待确认
        - 确认：已确认
        - 进行中：执行中
        - 完成：已完成
        """
        )
