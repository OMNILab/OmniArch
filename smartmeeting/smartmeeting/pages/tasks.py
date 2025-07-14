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
