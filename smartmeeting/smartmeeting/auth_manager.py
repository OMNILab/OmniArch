"""
Authentication Manager Module
Handles user authentication and session management with enhanced session state

⚠️  TEMPORARY TESTING MODE: Authentication is currently disabled for quick testing.
    To re-enable authentication, uncomment the line in is_authenticated() method.
"""

import streamlit as st
from typing import Optional, Dict, Any


class AuthManager:
    """Manages user authentication and session state"""

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state variables"""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "current_user" not in st.session_state:
            st.session_state.current_user = None
        if "login_attempts" not in st.session_state:
            st.session_state.login_attempts = 0

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user login

        Args:
            username: User's username
            password: User's password

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Increment login attempts
        st.session_state.login_attempts += 1

        # Check for default admin credentials
        if username == "admin" and password == "admin123":
            # Set up admin user
            admin_user = {
                "id": 1,
                "username": "admin",
                "name": "系统管理员",
                "email": "admin@company.com",
                "department": "IT部",
                "role": "系统管理员",
                "created_at": "2024-01-01",
                "last_login": st.session_state.get("current_time", "2024-01-01"),
            }

            # Set session state
            st.session_state.authenticated = True
            st.session_state.current_user = admin_user
            st.session_state.login_time = st.session_state.get(
                "current_time", "2024-01-01"
            )

            return True

        # Invalid credentials
        return False

    def logout(self):
        """Logout current user and clear session state"""
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.login_attempts = 0
        # Clear any user-specific session data
        if "user_preferences" in st.session_state:
            del st.session_state["user_preferences"]

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        # Temporarily disable authentication for testing
        # TODO: Re-enable authentication by uncommenting the line below
        return st.session_state.authenticated

        # Auto-authenticate with demo user for testing
        if not st.session_state.authenticated:
            # Set up demo user automatically
            demo_user = {
                "id": 1,
                "username": "demo_user",
                "name": "Demo User (测试用户)",
                "email": "demo@company.com",
                "department": "研发部",
                "role": "会议组织者",
                "created_at": "2024-01-01",
                "last_login": "2024-01-01",
            }
            st.session_state.authenticated = True
            st.session_state.current_user = demo_user

        return True

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user data"""
        return st.session_state.current_user

    def get_user_role(self) -> str:
        """Get current user's role"""
        if st.session_state.current_user:
            return st.session_state.current_user.get("role", "会议参与者")
        return "会议参与者"

    def get_user_department(self) -> str:
        """Get current user's department"""
        if st.session_state.current_user:
            return st.session_state.current_user.get("department", "未分配")
        return "未分配"

    def get_user_id(self) -> int:
        """Get current user's ID"""
        if st.session_state.current_user:
            return st.session_state.current_user.get("id", 0)
        return 0

    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.get_user_role() == "系统管理员"

    def is_organizer(self) -> bool:
        """Check if current user is meeting organizer"""
        return self.get_user_role() == "会议组织者"

    def require_auth(self):
        """Decorator to require authentication for pages"""
        if not self.is_authenticated():
            st.error("请先登录")
            st.stop()

    def require_admin(self):
        """Decorator to require admin privileges"""
        if not self.is_authenticated():
            st.error("请先登录")
            st.stop()
        if not self.is_admin():
            st.error("您没有权限访问此页面")
            st.stop()

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from session state"""
        if "user_preferences" not in st.session_state:
            st.session_state.user_preferences = {
                "theme": "light",
                "language": "zh_CN",
                "notifications": True,
                "auto_save": True,
            }
        return st.session_state.user_preferences

    def update_user_preference(self, key: str, value: Any):
        """Update user preference in session state"""
        preferences = self.get_user_preferences()
        preferences[key] = value
        st.session_state.user_preferences = preferences

    def get_login_history(self) -> Dict[str, Any]:
        """Get login history for current session"""
        return {
            "login_attempts": st.session_state.get("login_attempts", 0),
            "login_time": st.session_state.get("login_time", None),
            "current_user": st.session_state.get("current_user", None),
        }
