"""
Dashboard Page Module
Contains the dashboard page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


class DashboardPage:
    """Data dashboard page implementation with enhanced real-time data"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """Data dashboard page implementation with enhanced real-time data"""
        self.ui.create_header("会议统计")

        # 日期选择器 - 实现联动功能
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "开始日期",
                value=datetime.now().date() - timedelta(days=30),
                max_value=datetime.now().date(),
                key="start_date",
            )

        with col2:
            # 结束日期不能小于开始日期
            min_end_date = start_date if start_date else datetime.now().date()
            end_date = st.date_input(
                "结束日期",
                value=datetime.now().date(),
                min_value=min_end_date,
                max_value=datetime.now().date(),
                key="end_date",
            )

            # 验证日期范围
            if start_date and end_date and end_date < start_date:
                st.error("结束日期不能小于开始日期")
                st.stop()

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
                "今日会议", str(dashboard_data["meetings_today"])
            )

        with col3:
            self.ui.create_metric_card(
                "完成任务", str(dashboard_data["completed_tasks"])
            )

        with col4:
            self.ui.create_metric_card(
                "可用会议室", str(dashboard_data["available_rooms"])
            )

        # 新增：即将到来的会议状态
        st.markdown("---")
        st.markdown("### 📅 即将到来的会议")

        # 获取即将到来的会议
        upcoming_meetings = self.data_manager.get_upcoming_meetings(limit=5)
        ongoing_meetings = self.data_manager.get_ongoing_meetings()

        if upcoming_meetings or ongoing_meetings:
            # 显示正在进行的会议
            if ongoing_meetings:
                st.markdown("#### 🔄 正在进行的会议")
                for meeting in ongoing_meetings:
                    title = meeting.get("meeting_title", "未命名会议")
                    start_time = meeting.get("start_datetime", "未知时间")
                    room_id = meeting.get("room_id", "未知")

                    # 获取房间名称
                    rooms_df = self.data_manager.get_dataframe("rooms")
                    room_info = rooms_df[rooms_df["room_id"] == room_id]
                    room_name = (
                        room_info.iloc[0]["room_name"]
                        if not room_info.empty
                        else f"会议室{room_id}"
                    )

                    st.info(f"**{title}** - {room_name} - {start_time}")

            # 显示即将到来的会议
            if upcoming_meetings:
                st.markdown("#### 🕐 即将到来的会议")
                for meeting in upcoming_meetings:
                    title = meeting.get("meeting_title", "未命名会议")
                    start_time = meeting.get("start_datetime", "未知时间")
                    room_id = meeting.get("room_id", "未知")

                    # 获取房间名称
                    rooms_df = self.data_manager.get_dataframe("rooms")
                    room_info = rooms_df[rooms_df["room_id"] == room_id]
                    room_name = (
                        room_info.iloc[0]["room_name"]
                        if not room_info.empty
                        else f"会议室{room_id}"
                    )

                    # 计算距离会议开始的时间
                    start_dt = pd.to_datetime(start_time)
                    current_time = pd.Timestamp.now()
                    time_diff = start_dt - current_time

                    if time_diff.total_seconds() > 0:
                        hours = int(time_diff.total_seconds() // 3600)
                        minutes = int((time_diff.total_seconds() % 3600) // 60)

                        if hours > 24:
                            days = hours // 24
                            remaining_hours = hours % 24
                            time_until = f"{days}天{remaining_hours}小时"
                        elif hours > 0:
                            time_until = f"{hours}小时{minutes}分钟"
                        else:
                            time_until = f"{minutes}分钟"

                        st.warning(
                            f"**{title}** - {room_name} - {start_time} (还有{time_until})"
                        )
                    else:
                        st.warning(
                            f"**{title}** - {room_name} - {start_time} (即将开始)"
                        )
        else:
            st.info("📝 暂无即将到来的会议")

        # Enhanced room usage charts with real data
        st.markdown("---")
        st.markdown("### 会议室使用分析")

        col1, col2 = st.columns(2)

        meetings_df = self.data_manager.get_dataframe("meetings")
        rooms_df = self.data_manager.get_dataframe("rooms")

        with col1:
            # Room usage analysis
            if len(meetings_df) > 0:
                room_usage = (
                    meetings_df.groupby("room_id")
                    .size()
                    .reset_index(name="usage_count")
                )
                room_usage = room_usage.merge(
                    rooms_df[["room_id", "room_name"]],
                    left_on="room_id",
                    right_on="room_id",
                )

                fig = px.bar(
                    room_usage,
                    x="room_name",
                    y="usage_count",
                    title="会议室使用频率",
                    labels={"room_name": "会议室", "usage_count": "使用次数"},
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
            if len(meetings_df) > 0 and "duration_minutes" in meetings_df.columns:
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
                    meetings_df["duration_minutes"],
                    bins=duration_bins,
                    labels=duration_labels,
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
        departments_df = self.data_manager.get_dataframe("departments")

        if len(users_df) > 0 and len(tasks_df) > 0 and len(departments_df) > 0:
            # Join tasks with departments to get department names
            dept_usage = (
                tasks_df.groupby("department_id")
                .agg({"task_id": "count", "status": lambda x: (x == "完成").sum()})
                .reset_index()
            )
            dept_usage.columns = ["department_id", "total_tasks", "completed_tasks"]

            # Join with departments to get department names
            dept_usage = dept_usage.merge(
                departments_df[["department_id", "department_name"]],
                left_on="department_id",
                right_on="department_id",
            )
            dept_usage = dept_usage[
                ["department_name", "total_tasks", "completed_tasks"]
            ]
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

        # 侧边栏功能说明
        st.sidebar.markdown("### 📊 功能说明")
        st.sidebar.markdown(
            """
        **📈 数据统计**:
        - 整体概览数据
        - 会议室使用分析
        - 会议时长分布
        - 部门使用统计
        
        **📅 时间筛选**:
        - 选择时间范围
        - 查看历史数据
        - 导出数据报告
        """
        )
