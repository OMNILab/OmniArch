"""
Unit tests for DataManager module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import os
from datetime import datetime, timedelta
import tempfile
import sys

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from data_manager import DataManager


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock streamlit session state
        self.mock_session_state = {}
        
        # Patch streamlit session state
        self.session_state_patcher = patch('streamlit.session_state', self.mock_session_state)
        self.mock_st = self.session_state_patcher.start()
        
        # Mock streamlit success function
        self.success_patcher = patch('streamlit.success')
        self.mock_success = self.success_patcher.start()
        
    def tearDown(self):
        """Clean up after each test method"""
        self.session_state_patcher.stop()
        self.success_patcher.stop()
        
    def test_init_with_csv(self):
        """Test DataManager initialization with CSV enabled"""
        with patch.object(DataManager, '_csv_files_exist', return_value=True), \
             patch.object(DataManager, '_load_from_csv') as mock_load_csv:
            
            dm = DataManager(use_csv=True)
            
            self.assertTrue(dm.use_csv)
            self.assertEqual(dm.csv_path, "streamlit/mock")
            mock_load_csv.assert_called_once()
            self.assertIn('mock_data', self.mock_session_state)
            
    def test_init_without_csv(self):
        """Test DataManager initialization without CSV"""
        with patch.object(DataManager, '_generate_mock_data') as mock_generate:
            
            dm = DataManager(use_csv=False)
            
            self.assertFalse(dm.use_csv)
            mock_generate.assert_called_once()
            
    def test_csv_files_exist_all_present(self):
        """Test CSV files existence check when all files are present"""
        with patch('os.path.exists', return_value=True):
            dm = DataManager(use_csv=False)
            self.assertTrue(dm._csv_files_exist())
            
    def test_csv_files_exist_missing_files(self):
        """Test CSV files existence check when files are missing"""
        with patch('os.path.exists', return_value=False):
            dm = DataManager(use_csv=False)
            self.assertFalse(dm._csv_files_exist())
            
    def test_load_from_csv_success(self):
        """Test successful CSV loading"""
        # Create mock CSV data
        mock_buildings = pd.DataFrame([
            {'id': 1, 'name': 'Building A', 'address': 'Test Address'}
        ])
        mock_rooms = pd.DataFrame([
            {'id': 1, 'room_name': 'Room A', 'capacity': 10}
        ])
        mock_users = pd.DataFrame([
            {'id': 1, 'username': 'testuser', 'name': 'Test User'}
        ])
        
        with patch('pandas.read_csv') as mock_read_csv:
            # Configure mock to return different dataframes based on filename
            def csv_side_effect(filepath):
                if 'buildings.csv' in filepath:
                    return mock_buildings
                elif 'meeting_rooms.csv' in filepath:
                    return mock_rooms
                elif 'users.csv' in filepath:
                    return mock_users
                else:
                    # Return empty dataframe for other files
                    return pd.DataFrame()
                    
            mock_read_csv.side_effect = csv_side_effect
            
            dm = DataManager(use_csv=False)
            dm._load_from_csv()
            
            # Verify session state was populated
            self.assertIn('buildings', self.mock_session_state['mock_data'])
            self.assertIn('rooms', self.mock_session_state['mock_data'])
            self.assertIn('users', self.mock_session_state['mock_data'])
            
    def test_load_from_csv_error_fallback(self):
        """Test CSV loading error fallback to generated data"""
        with patch('pandas.read_csv', side_effect=Exception("File not found")), \
             patch.object(DataManager, '_generate_mock_data') as mock_generate:
            
            dm = DataManager(use_csv=False)
            dm._load_from_csv()
            
            mock_generate.assert_called_once()
            
    def test_generate_mock_data(self):
        """Test mock data generation"""
        dm = DataManager(use_csv=False)
        dm._generate_mock_data()
        
        # Verify all data types are generated
        expected_keys = ['users', 'rooms', 'meetings', 'tasks', 'minutes']
        for key in expected_keys:
            self.assertIn(key, self.mock_session_state['mock_data'])
            self.assertIsInstance(self.mock_session_state['mock_data'][key], list)
            self.assertGreater(len(self.mock_session_state['mock_data'][key]), 0)
            
    def test_get_dataframe_meetings(self):
        """Test getting meetings dataframe with column mapping"""
        # Set up mock data
        self.mock_session_state['mock_data'] = {
            'meetings': [
                {
                    'id': 1,
                    'start_datetime': '2024-01-01 10:00:00',
                    'end_datetime': '2024-01-01 11:00:00',
                    'duration_minutes': 60
                }
            ]
        }
        
        dm = DataManager(use_csv=False)
        df = dm.get_dataframe('meetings')
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        # Check column mapping
        self.assertIn('start_time', df.columns)
        self.assertIn('end_time', df.columns)
        self.assertIn('duration', df.columns)
        
    def test_get_dataframe_empty(self):
        """Test getting dataframe for non-existent data type"""
        dm = DataManager(use_csv=False)
        df = dm.get_dataframe('nonexistent')
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)
        
    def test_add_meeting(self):
        """Test adding a new meeting"""
        self.mock_session_state['mock_data'] = {'meetings': []}
        
        dm = DataManager(use_csv=False)
        meeting_data = {
            'title': 'Test Meeting',
            'room_id': 1,
            'organizer_id': 1
        }
        
        dm.add_meeting(meeting_data)
        
        self.assertEqual(len(self.mock_session_state['mock_data']['meetings']), 1)
        added_meeting = self.mock_session_state['mock_data']['meetings'][0]
        self.assertEqual(added_meeting['title'], 'Test Meeting')
        self.assertEqual(added_meeting['id'], 1)
        self.assertEqual(added_meeting['booking_id'], 1)
        self.assertIn('created_at', added_meeting)
        
    def test_add_task(self):
        """Test adding a new task"""
        self.mock_session_state['mock_data'] = {'tasks': []}
        
        dm = DataManager(use_csv=False)
        task_data = {
            'title': 'Test Task',
            'assignee_id': 1,
            'priority': 'High'
        }
        
        dm.add_task(task_data)
        
        self.assertEqual(len(self.mock_session_state['mock_data']['tasks']), 1)
        added_task = self.mock_session_state['mock_data']['tasks'][0]
        self.assertEqual(added_task['title'], 'Test Task')
        self.assertEqual(added_task['id'], 1)
        self.assertEqual(added_task['task_id'], 1)
        
    def test_update_task_status(self):
        """Test updating task status"""
        self.mock_session_state['mock_data'] = {
            'tasks': [
                {'id': 1, 'task_id': 1, 'status': 'In Progress'},
                {'id': 2, 'task_id': 2, 'status': 'Pending'}
            ]
        }
        
        dm = DataManager(use_csv=False)
        dm.update_task_status(1, 'Completed')
        
        updated_task = self.mock_session_state['mock_data']['tasks'][0]
        self.assertEqual(updated_task['status'], 'Completed')
        self.assertIn('updated_at', updated_task)
        
    def test_get_meeting_by_id(self):
        """Test getting meeting by ID"""
        self.mock_session_state['mock_data'] = {
            'meetings': [
                {'id': 1, 'title': 'Meeting 1'},
                {'id': 2, 'title': 'Meeting 2'}
            ]
        }
        
        dm = DataManager(use_csv=False)
        meeting = dm.get_meeting_by_id(1)
        
        self.assertIsNotNone(meeting)
        self.assertEqual(meeting['title'], 'Meeting 1')
        
        # Test non-existent meeting
        meeting = dm.get_meeting_by_id(999)
        self.assertIsNone(meeting)
        
    def test_get_dashboard_data(self):
        """Test getting dashboard data"""
        # Set up mock data
        self.mock_session_state['mock_data'] = {
            'meetings': [
                {
                    'id': 1,
                    'start_time': datetime.now(),
                    'duration': 60
                }
            ],
            'tasks': [
                {'id': 1, 'status': 'Completed'},
                {'id': 2, 'status': 'In Progress'}
            ],
            'rooms': [
                {'id': 1, 'status': 'Available'},
                {'id': 2, 'status': 'Occupied'}
            ],
            'users': [
                {'id': 1, 'name': 'User 1'}
            ]
        }
        
        dm = DataManager(use_csv=False)
        dashboard_data = dm.get_dashboard_data()
        
        self.assertEqual(dashboard_data['total_meetings'], 1)
        self.assertEqual(dashboard_data['total_tasks'], 2)
        self.assertEqual(dashboard_data['total_rooms'], 2)
        self.assertEqual(dashboard_data['total_users'], 1)
        self.assertEqual(dashboard_data['completed_tasks'], 1)
        
    def test_get_room_recommendations(self):
        """Test getting room recommendations"""
        self.mock_session_state['mock_data'] = {
            'rooms': [
                {
                    'id': 1,
                    'capacity': 10,
                    'status': 'Available',
                    'has_projector': 1
                },
                {
                    'id': 2,
                    'capacity': 5,
                    'status': 'Available',
                    'has_projector': 0
                },
                {
                    'id': 3,
                    'capacity': 15,
                    'status': 'Occupied'
                }
            ]
        }
        
        dm = DataManager(use_csv=False)
        
        # Test basic capacity requirement
        recommendations = dm.get_room_recommendations(capacity=8)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], 1)
        
        # Test with equipment requirement
        recommendations = dm.get_room_recommendations(capacity=5, equipment_needed=['投影仪'])
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], 1)
        
    def test_reset_to_default(self):
        """Test resetting data to default state"""
        with patch.object(DataManager, '_csv_files_exist', return_value=False), \
             patch.object(DataManager, '_generate_mock_data') as mock_generate:
            
            dm = DataManager(use_csv=False)
            dm.reset_to_default()
            
            # Should call generate mock data and show success message
            self.assertEqual(mock_generate.call_count, 2)  # Once in init, once in reset
            self.mock_success.assert_called_once()


if __name__ == '__main__':
    unittest.main()