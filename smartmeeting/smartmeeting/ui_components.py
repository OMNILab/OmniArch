"""
UI Components Module
Handles common UI elements and styling for the smart meeting system
"""

import streamlit as st


class UIComponents:
    """Common UI components and styling utilities"""

    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling"""
        st.markdown(
            """
        <style>
        /* Modern theme styling */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 5rem;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            background: white;
            padding: 2.5rem 2rem 2rem 2rem;
            margin-left: -2rem;
            margin-right: -2rem;
            width: calc(100% + 4rem);
            box-sizing: border-box;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            text-align: center;
            transition: transform 0.2s ease-in-out;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }
        
        .metric-card h3 {
            color: #6b7280;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .metric-card h2 {
            color: #1f2937;
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }

        .task-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #3b82f6;
            margin-bottom: 1rem;
            transition: all 0.2s ease-in-out;
        }
        
        .task-card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            transform: translateY(-1px);
        }
        
        .room-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
            transition: all 0.2s ease-in-out;
        }
        
        .room-card:hover {
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .status-available {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .status-occupied {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        .status-maintenance {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .priority-high {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        .priority-medium {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .priority-low {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        /* Form styling */
        .stForm {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #f3f4f6;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Chart styling */
        .js-plotly-plot {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Page content spacing for fixed header */
        .main .block-container {
            padding-top: 3rem;
        }
        
        /* Ensure header spans full width */
        .main-header {
            box-sizing: border-box;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
                padding: 1.5rem 0.5rem 1rem 0.5rem;
            }
            
            .metric-card {
                padding: 1rem;
            }
            
            .metric-card h2 {
                font-size: 1.5rem;
            }
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_header(title: str):
        """Create a styled header"""
        st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)

    @staticmethod
    def create_metric_card(title: str, value: str):
        """Create a metric card"""
        st.markdown(
            f"""
        <div class="metric-card">
            <h3>{title}</h3>
            <h2>{value}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_status_badge(status: str, status_type: str = "status"):
        """Create a status badge"""
        if status_type == "status":
            if status == "可用":
                css_class = "status-available"
            elif status == "已预订":
                css_class = "status-occupied"
            else:
                css_class = "status-maintenance"
        elif status_type == "priority":
            if status == "高":
                css_class = "priority-high"
            elif status == "中":
                css_class = "priority-medium"
            else:
                css_class = "priority-low"
        else:
            css_class = "status-available"

        st.markdown(
            f'<span class="status-badge {css_class}">{status}</span>',
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_room_card(room_data: dict):
        """Create a room recommendation card"""
        # Get values with fallbacks for missing keys
        name = room_data.get("name", "Unknown Room")
        capacity = room_data.get("capacity", "N/A")
        equipment = room_data.get("equipment", "No equipment info")
        floor = room_data.get("floor", "N/A")
        status = room_data.get("status", "Unknown")

        st.markdown(
            f"""
        <div class="room-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">{name}</h4>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 0.9rem; color: #6b7280;">容量: {capacity}人</span>
                <span style="font-size: 0.9rem; color: #6b7280;">{equipment}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #6b7280;">{floor}</span>
                <span class="status-badge status-available">{status}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_task_card(task_data: dict, assignee_name: str):
        """Create a task card"""
        priority_colors = {"高": "#d62728", "中": "#ff7f0e", "低": "#2ca02c"}
        priority_color = priority_colors.get(task_data["priority"], "#666")

        status_colors = {
            "完成": "#2ca02c",
            "进行中": "#ff7f0e",
            "确认": "#1f77b4",
            "草稿": "#666",
        }
        status_color = status_colors.get(task_data["status"], "#666")

        st.markdown(
            f"""
        <div class="task-card" style="border-left-color: {priority_color};">
            <h5 style="margin: 0 0 0.5rem 0; color: {priority_color};">{task_data['title']}</h5>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 0.9rem; color: #666;">负责人: {assignee_name}</span>
                <span style="background: {status_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">{task_data['status']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #666;">截止: {task_data['deadline'].strftime('%m-%d')}</span>
                <span style="background: {priority_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">{task_data['priority']}</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def show_meeting_status(data_manager, limit=5):
        """Display meeting status information (upcoming and ongoing meetings)

        Args:
            data_manager: DataManager instance to get meeting data
            limit: Maximum number of upcoming meetings to display
        """
        import pandas as pd

        # 获取即将到来的会议
        upcoming_meetings = data_manager.get_upcoming_meetings(limit=limit)
        ongoing_meetings = data_manager.get_ongoing_meetings()

        if upcoming_meetings or ongoing_meetings:
            # 显示正在进行的会议
            if ongoing_meetings:
                st.markdown("#### 🔄 正在进行的会议")
                for meeting in ongoing_meetings:
                    title = meeting.get("meeting_title", "未命名会议")
                    start_time = meeting.get("start_datetime", "未知时间")
                    room_id = meeting.get("room_id", "未知")

                    # 获取房间名称
                    rooms_df = data_manager.get_dataframe("rooms")
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
                    rooms_df = data_manager.get_dataframe("rooms")
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
