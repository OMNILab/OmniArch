"""
Smart Meeting System - Modular Version
Main application file that uses modular components
"""

import streamlit as st
from smartmeeting.data_manager import DataManager
from smartmeeting.auth_manager import AuthManager
from smartmeeting.ui_components import UIComponents
from smartmeeting.pages_manager import Pages


def main():
    """Main application function"""

    # Initialize components
    data_manager = DataManager()
    auth_manager = AuthManager(data_manager)
    ui_components = UIComponents()
    pages = Pages(data_manager, auth_manager, ui_components)

    # Apply custom CSS
    ui_components.apply_custom_css()

    # Configure page
    st.set_page_config(
        page_title="智慧会议系统",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Check authentication
    if not auth_manager.is_authenticated():
        pages.show_login_page()
        return

    # 新增：会议状态通知系统
    def show_meeting_notifications():
        """显示会议状态通知"""
        # 更新会议状态
        data_manager.update_meeting_statuses()

        # 获取即将到来的会议（1小时内）
        upcoming_meetings = data_manager.get_upcoming_meetings(limit=10)
        ongoing_meetings = data_manager.get_ongoing_meetings()

        notifications = []

        # 检查即将到来的会议（1小时内）
        import pandas as pd

        current_time = pd.Timestamp.now()

        for meeting in upcoming_meetings:
            start_time = pd.to_datetime(meeting.get("start_datetime"), errors="coerce")
            if pd.notna(start_time):
                time_diff = start_time - current_time
                hours_until = time_diff.total_seconds() / 3600

                if 0 < hours_until <= 1:  # 1小时内
                    title = meeting.get("meeting_title", "未命名会议")
                    room_id = meeting.get("room_id", "未知")

                    # 获取房间名称
                    rooms_df = data_manager.get_dataframe("rooms")
                    room_info = rooms_df[rooms_df["room_id"] == room_id]
                    room_name = (
                        room_info.iloc[0]["room_name"]
                        if not room_info.empty
                        else f"会议室{room_id}"
                    )

                    minutes_until = int(hours_until * 60)
                    notifications.append(
                        {
                            "type": "warning",
                            "message": f"⚠️ 会议即将开始：{title} - {room_name} (还有{minutes_until}分钟)",
                        }
                    )

        # 检查正在进行的会议
        for meeting in ongoing_meetings:
            title = meeting.get("meeting_title", "未命名会议")
            room_id = meeting.get("room_id", "未知")

            # 获取房间名称
            rooms_df = data_manager.get_dataframe("rooms")
            room_info = rooms_df[rooms_df["room_id"] == room_id]
            room_name = (
                room_info.iloc[0]["room_name"]
                if not room_info.empty
                else f"会议室{room_id}"
            )

            notifications.append(
                {"type": "info", "message": f"🔄 会议进行中：{title} - {room_name}"}
            )

        # 显示通知
        if notifications:
            st.markdown("### 🔔 会议通知")
            for notification in notifications[:3]:  # 最多显示3个通知
                if notification["type"] == "warning":
                    st.warning(notification["message"])
                elif notification["type"] == "info":
                    st.info(notification["message"])

    # 显示会议通知
    show_meeting_notifications()

    # Main application layout
    current_user = auth_manager.get_current_user()

    # Sidebar navigation
    with st.sidebar:
        # Enhanced user information display
        st.markdown("### 👤 用户信息")
        if current_user:
            user_id = current_user.get("id", 0)
            username = current_user.get("name", "用户")
            role = current_user.get("role", "会议参与者")
            department = current_user.get("department", "未分配")
            email = current_user.get("email", "")

            # Create a nice info box for user details
            user_info = f"""
            **👤 用户**: {username}  
            **🆔 ID**: {user_id}  
            **🎭 角色**: {role}  
            **🏢 部门**: {department}
            """
            if email:
                user_info += f"**📧 邮箱**: {email}"

            st.info(user_info)
        else:
            st.warning("未获取到用户信息")

        # 退出登录按钮 - 放在用户信息下方
        if st.button("🚪 退出登录", use_container_width=True, type="secondary"):
            auth_manager.logout()
            st.rerun()

        st.markdown("---")

        # Initialize session state for current page if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = "智能预定"

        # Navigation buttons
        if st.button("🏢 智能预定", use_container_width=True):
            st.session_state.current_page = "智能预定"

        if st.button("🗓️ 会议室日历", use_container_width=True):
            st.session_state.current_page = "会议室日历"

        if st.button("📝 会议纪要", use_container_width=True):
            st.session_state.current_page = "会议纪要"

        if st.button("📋 任务看板", use_container_width=True):
            st.session_state.current_page = "任务看板"

        if st.button("📊 会议统计", use_container_width=True):
            st.session_state.current_page = "会议统计"

        # if st.button("🤖 智能分析", use_container_width=True):
        #     st.session_state.current_page = "智能分析"

        if st.button("⚙️ 系统设置", use_container_width=True):
            st.session_state.current_page = "系统设置"

    # Main content area
    page = st.session_state.current_page

    if page == "智能预定":
        pages.show_booking_page()
    elif page == "会议室日历":
        pages.show_calendar_page()
    elif page == "会议纪要":
        pages.show_minutes_page()
    elif page == "任务看板":
        pages.show_tasks_page()
    elif page == "会议统计":
        pages.show_dashboard_page()
    # elif page == "智能分析":
    #     pages.show_analysis_page()
    elif page == "系统设置":
        pages.show_settings_page()


if __name__ == "__main__":
    main()
