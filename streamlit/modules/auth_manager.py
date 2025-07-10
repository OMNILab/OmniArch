"""
Authentication Manager Module
Handles user authentication and session management
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
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'mock_data' not in st.session_state:
            st.session_state.mock_data = self.data_manager.get_data()
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate user login
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        # For demo purposes, accept any username/password
        # In real implementation, this would validate against database
        
        # Find user by username
        users = self.data_manager.get_dataframe('users')
        user = users[users['username'] == username]
        
        if len(user) == 0:
            # Create demo user if not found
            demo_user = {
                'id': len(users) + 1,
                'username': username,
                'name': f"Demo User ({username})",
                'email': f"{username}@company.com",
                'department': '研发部',
                'role': '会议组织者',
                'created_at': '2024-01-01'
            }
            self.data_manager.mock_data['users'].append(demo_user)
            user_data = demo_user
        else:
            user_data = user.iloc[0].to_dict()
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.current_user = user_data
        
        return True
    
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.authenticated
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user data"""
        return st.session_state.current_user
    
    def get_user_role(self) -> str:
        """Get current user's role"""
        if st.session_state.current_user:
            return st.session_state.current_user.get('role', '会议参与者')
        return '会议参与者'
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.get_user_role() == '系统管理员'
    
    def require_auth(self):
        """Decorator to require authentication for pages"""
        if not self.is_authenticated():
            st.error("请先登录")
            st.stop() 