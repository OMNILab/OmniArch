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

    # Main application layout
    current_user = auth_manager.get_current_user()

    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"欢迎，{current_user['name']}")
        st.markdown(f"角色：{current_user['role']}")

        st.markdown("---")

        # Initialize session state for current page if not exists
        if "current_page" not in st.session_state:
            st.session_state.current_page = "智能预定"

        # Navigation buttons
        if st.button("🏢 智能预定", use_container_width=True):
            st.session_state.current_page = "智能预定"

        if st.button("📝 会议纪要", use_container_width=True):
            st.session_state.current_page = "会议纪要"

        if st.button("📋 任务看板", use_container_width=True):
            st.session_state.current_page = "任务看板"

        if st.button("📊 数据面板", use_container_width=True):
            st.session_state.current_page = "数据面板"

        if st.button("🤖 智能分析", use_container_width=True):
            st.session_state.current_page = "智能分析"

        if st.button("⚙️ 系统设置", use_container_width=True):
            st.session_state.current_page = "系统设置"

        st.markdown("---")

        if st.button("退出登录"):
            auth_manager.logout()
            st.rerun()

    # Main content area
    page = st.session_state.current_page

    if page == "智能预定":
        pages.show_booking_page()
    elif page == "会议纪要":
        pages.show_minutes_page()
    elif page == "任务看板":
        pages.show_tasks_page()
    elif page == "数据面板":
        pages.show_dashboard_page()
    elif page == "智能分析":
        pages.show_analysis_page()
    elif page == "系统设置":
        pages.show_settings_page()


if __name__ == "__main__":
    main()
