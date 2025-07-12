"""
Unit tests for AuthManager module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import os
import sys

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from auth_manager import AuthManager


class MockDataManager:
    """Mock DataManager for testing"""
    
    def __init__(self):
        self.users_data = pd.DataFrame([
            {
                'id': 1,
                'username': 'admin',
                'name': 'Admin User',
                'email': 'admin@company.com',
                'department': '研发部',
                'role': '系统管理员'
            },
            {
                'id': 2,
                'username': 'organizer',
                'name': 'Meeting Organizer',
                'email': 'organizer@company.com',
                'department': '产品部',
                'role': '会议组织者'
            },
            {
                'id': 3,
                'username': 'participant',
                'name': 'Participant User',
                'email': 'participant@company.com',
                'department': '测试部',
                'role': '会议参与者'
            }
        ])
        
    def get_dataframe(self, data_type):
        """Mock get_dataframe method"""
        if data_type == 'users':
            return self.users_data
        return pd.DataFrame()


class TestAuthManager(unittest.TestCase):
    """Test cases for AuthManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock streamlit session state
        self.mock_session_state = {}
        
        # Patch streamlit session state
        self.session_state_patcher = patch('streamlit.session_state', self.mock_session_state)
        self.mock_st = self.session_state_patcher.start()
        
        # Create mock data manager
        self.mock_data_manager = MockDataManager()
        
        # Mock the mock_data in session state for user creation
        self.mock_session_state['mock_data'] = {'users': []}
        
    def tearDown(self):
        """Clean up after each test method"""
        self.session_state_patcher.stop()
        
    def test_init(self):
        """Test AuthManager initialization"""
        auth = AuthManager(self.mock_data_manager)
        
        # Check if session state variables are initialized
        self.assertFalse(self.mock_session_state['authenticated'])
        self.assertIsNone(self.mock_session_state['current_user'])
        self.assertEqual(self.mock_session_state['login_attempts'], 0)
        
    def test_login_existing_user(self):
        """Test login with existing user"""
        auth = AuthManager(self.mock_data_manager)
        
        # Test login with existing user
        result = auth.login('admin', 'password')
        
        self.assertTrue(result)
        self.assertTrue(self.mock_session_state['authenticated'])
        self.assertIsNotNone(self.mock_session_state['current_user'])
        self.assertEqual(self.mock_session_state['current_user']['username'], 'admin')
        self.assertEqual(self.mock_session_state['current_user']['role'], '系统管理员')
        self.assertEqual(self.mock_session_state['login_attempts'], 1)
        
    def test_login_new_user(self):
        """Test login with new user (creates demo user)"""
        auth = AuthManager(self.mock_data_manager)
        
        # Test login with non-existing user
        result = auth.login('newuser', 'password')
        
        self.assertTrue(result)
        self.assertTrue(self.mock_session_state['authenticated'])
        self.assertIsNotNone(self.mock_session_state['current_user'])
        self.assertEqual(self.mock_session_state['current_user']['username'], 'newuser')
        self.assertEqual(self.mock_session_state['current_user']['name'], 'Demo User (newuser)')
        self.assertEqual(self.mock_session_state['current_user']['department'], '研发部')
        
        # Check if user was added to mock data
        self.assertEqual(len(self.mock_session_state['mock_data']['users']), 1)
        
    def test_logout(self):
        """Test user logout"""
        auth = AuthManager(self.mock_data_manager)
        
        # First login
        auth.login('admin', 'password')
        self.assertTrue(self.mock_session_state['authenticated'])
        
        # Set some user preferences
        self.mock_session_state['user_preferences'] = {'theme': 'dark'}
        
        # Then logout
        auth.logout()
        
        self.assertFalse(self.mock_session_state['authenticated'])
        self.assertIsNone(self.mock_session_state['current_user'])
        self.assertEqual(self.mock_session_state['login_attempts'], 0)
        self.assertNotIn('user_preferences', self.mock_session_state)
        
    def test_is_authenticated(self):
        """Test authentication status check"""
        auth = AuthManager(self.mock_data_manager)
        
        # Initially not authenticated
        self.assertFalse(auth.is_authenticated())
        
        # After login
        auth.login('admin', 'password')
        self.assertTrue(auth.is_authenticated())
        
        # After logout
        auth.logout()
        self.assertFalse(auth.is_authenticated())
        
    def test_get_current_user(self):
        """Test getting current user data"""
        auth = AuthManager(self.mock_data_manager)
        
        # No user logged in
        self.assertIsNone(auth.get_current_user())
        
        # User logged in
        auth.login('organizer', 'password')
        user = auth.get_current_user()
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'organizer')
        
    def test_get_user_role(self):
        """Test getting user role"""
        auth = AuthManager(self.mock_data_manager)
        
        # No user logged in
        self.assertEqual(auth.get_user_role(), '会议参与者')
        
        # Admin user
        auth.login('admin', 'password')
        self.assertEqual(auth.get_user_role(), '系统管理员')
        
        # Organizer user
        auth.logout()
        auth.login('organizer', 'password')
        self.assertEqual(auth.get_user_role(), '会议组织者')
        
    def test_get_user_department(self):
        """Test getting user department"""
        auth = AuthManager(self.mock_data_manager)
        
        # No user logged in
        self.assertEqual(auth.get_user_department(), '未分配')
        
        # User logged in
        auth.login('admin', 'password')
        self.assertEqual(auth.get_user_department(), '研发部')
        
    def test_get_user_id(self):
        """Test getting user ID"""
        auth = AuthManager(self.mock_data_manager)
        
        # No user logged in
        self.assertEqual(auth.get_user_id(), 0)
        
        # User logged in
        auth.login('admin', 'password')
        self.assertEqual(auth.get_user_id(), 1)
        
    def test_is_admin(self):
        """Test admin role check"""
        auth = AuthManager(self.mock_data_manager)
        
        # No user logged in
        self.assertFalse(auth.is_admin())
        
        # Admin user
        auth.login('admin', 'password')
        self.assertTrue(auth.is_admin())
        
        # Non-admin user
        auth.logout()
        auth.login('participant', 'password')
        self.assertFalse(auth.is_admin())
        
    def test_is_organizer(self):
        """Test organizer role check"""
        auth = AuthManager(self.mock_data_manager)
        
        # No user logged in
        self.assertFalse(auth.is_organizer())
        
        # Organizer user
        auth.login('organizer', 'password')
        self.assertTrue(auth.is_organizer())
        
        # Non-organizer user
        auth.logout()
        auth.login('participant', 'password')
        self.assertFalse(auth.is_organizer())
        
    def test_require_auth_authenticated(self):
        """Test require_auth with authenticated user"""
        auth = AuthManager(self.mock_data_manager)
        auth.login('admin', 'password')
        
        # Should not raise any exception
        try:
            auth.require_auth()
        except SystemExit:
            self.fail("require_auth raised SystemExit unexpectedly")
            
    def test_require_auth_not_authenticated(self):
        """Test require_auth without authentication"""
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.stop') as mock_stop:
            
            auth = AuthManager(self.mock_data_manager)
            auth.require_auth()
            
            mock_error.assert_called_once_with("请先登录")
            mock_stop.assert_called_once()
            
    def test_require_admin_as_admin(self):
        """Test require_admin with admin user"""
        auth = AuthManager(self.mock_data_manager)
        auth.login('admin', 'password')
        
        # Should not raise any exception
        try:
            auth.require_admin()
        except SystemExit:
            self.fail("require_admin raised SystemExit unexpectedly")
            
    def test_require_admin_not_authenticated(self):
        """Test require_admin without authentication"""
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.stop') as mock_stop:
            
            auth = AuthManager(self.mock_data_manager)
            auth.require_admin()
            
            mock_error.assert_called_once_with("请先登录")
            mock_stop.assert_called_once()
            
    def test_require_admin_not_admin(self):
        """Test require_admin with non-admin user"""
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.stop') as mock_stop:
            
            auth = AuthManager(self.mock_data_manager)
            auth.login('participant', 'password')
            auth.require_admin()
            
            mock_error.assert_called_once_with("您没有权限访问此页面")
            mock_stop.assert_called_once()
            
    def test_get_user_preferences_default(self):
        """Test getting default user preferences"""
        auth = AuthManager(self.mock_data_manager)
        
        preferences = auth.get_user_preferences()
        
        expected_preferences = {
            'theme': 'light',
            'language': 'zh_CN',
            'notifications': True,
            'auto_save': True
        }
        
        self.assertEqual(preferences, expected_preferences)
        self.assertIn('user_preferences', self.mock_session_state)
        
    def test_update_user_preference(self):
        """Test updating user preferences"""
        auth = AuthManager(self.mock_data_manager)
        
        # Update a preference
        auth.update_user_preference('theme', 'dark')
        
        preferences = auth.get_user_preferences()
        self.assertEqual(preferences['theme'], 'dark')
        
        # Update another preference
        auth.update_user_preference('notifications', False)
        preferences = auth.get_user_preferences()
        self.assertEqual(preferences['notifications'], False)
        self.assertEqual(preferences['theme'], 'dark')  # Previous change should persist
        
    def test_get_login_history(self):
        """Test getting login history"""
        auth = AuthManager(self.mock_data_manager)
        
        # Initial state
        history = auth.get_login_history()
        self.assertEqual(history['login_attempts'], 0)
        self.assertIsNone(history['current_user'])
        self.assertIsNone(history['login_time'])
        
        # After login
        auth.login('admin', 'password')
        history = auth.get_login_history()
        self.assertEqual(history['login_attempts'], 1)
        self.assertIsNotNone(history['current_user'])
        
    def test_multiple_login_attempts(self):
        """Test multiple login attempts increment counter"""
        auth = AuthManager(self.mock_data_manager)
        
        # Multiple login attempts
        auth.login('user1', 'pass1')
        auth.login('user2', 'pass2')
        auth.login('user3', 'pass3')
        
        self.assertEqual(self.mock_session_state['login_attempts'], 3)
        
        # Reset after logout
        auth.logout()
        self.assertEqual(self.mock_session_state['login_attempts'], 0)


if __name__ == '__main__':
    unittest.main()