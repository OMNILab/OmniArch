"""
Smart Meeting System - Modular Version
Main application file that uses modular components
"""

import streamlit as st
from modules.data_manager import DataManager
from modules.auth_manager import AuthManager
from modules.ui_components import UIComponents
from modules.pages import Pages

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
        initial_sidebar_state="expanded"
    )
    
    # Check authentication
    if not auth_manager.is_authenticated():
        pages.show_login_page()
        return
    
    # Main application layout
    current_user = auth_manager.get_current_user()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 智慧会议系统")
        st.markdown(f"欢迎，{current_user['name']}")
        st.markdown(f"角色：{current_user['role']}")
        st.markdown("---")
        
        # Navigation menu
        page = st.selectbox(
            "选择功能模块",
            [
                "智能预定",
                "会议纪要", 
                "任务看板",
                "数据面板",
                "智能数据分析",
                "系统设置"
            ]
        )
        
        st.markdown("---")
        
        if st.button("退出登录"):
            auth_manager.logout()
            st.rerun()
    
    # Main content area
    if page == "智能预定":
        pages.show_booking_page()
    elif page == "会议纪要":
        pages.show_minutes_page()
    elif page == "任务看板":
        pages.show_tasks_page()
    elif page == "数据面板":
        pages.show_dashboard_page()
    elif page == "智能数据分析":
        pages.show_pandasai_demo()
    elif page == "系统设置":
        pages.show_settings_page()

if __name__ == "__main__":
    main() 