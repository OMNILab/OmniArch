"""
Data Manager Module
Handles mock data generation and memory-based storage using session state
"""

import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import random
import streamlit as st

class DataManager:
    """Manages mock data generation and session state storage"""
    
    def __init__(self):
        self.fake = Faker('zh_CN')
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state with mock data if not already present"""
        if 'mock_data' not in st.session_state:
            st.session_state.mock_data = {}
            self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate comprehensive mock data for the application"""
        self._generate_users()
        self._generate_rooms()
        self._generate_meetings()
        self._generate_tasks()
        self._generate_minutes()
    
    def _generate_users(self):
        """Generate mock user data"""
        users = []
        departments = ['研发部', '测试部', '市场部', '产品部', '运营部']
        roles = ['会议组织者', '会议参与者', '系统管理员']
        
        for i in range(20):
            user = {
                'id': i + 1,
                'username': self.fake.user_name(),
                'name': self.fake.name(),
                'email': self.fake.email(),
                'department': random.choice(departments),
                'role': random.choice(roles),
                'created_at': self.fake.date_time_this_year()
            }
            users.append(user)
        
        st.session_state.mock_data['users'] = users
    
    def _generate_rooms(self):
        """Generate mock room data"""
        rooms = []
        room_types = ['会议室', '培训室', '视频会议室', '小型会议室']
        floors = ['3楼', '4楼', '5楼', '6楼']
        
        for i in range(8):
            room = {
                'id': i + 1,
                'name': f"{random.choice(floors)}{chr(65 + i)}会议室",
                'capacity': random.choice([6, 8, 12, 15, 20, 25, 30, 40]),
                'type': random.choice(room_types),
                'equipment': random.choice(['投影仪', '视频会议设备', '白板', '音响设备']),
                'floor': random.choice(floors),
                'status': random.choice(['可用', '维护中', '已预订'])
            }
            rooms.append(room)
        
        st.session_state.mock_data['rooms'] = rooms
    
    def _generate_meetings(self):
        """Generate mock meeting data"""
        meetings = []
        meeting_types = ['项目讨论', '产品评审', '技术分享', '团队会议', '客户会议']
        
        for i in range(50):
            start_time = self.fake.date_time_this_month()
            duration = random.choice([30, 60, 90, 120, 180])
            
            meeting = {
                'id': i + 1,
                'title': f"{random.choice(meeting_types)} - {self.fake.sentence(nb_words=3)}",
                'room_id': random.randint(1, 8),
                'organizer_id': random.randint(1, 20),
                'start_time': start_time,
                'end_time': start_time + timedelta(minutes=duration),
                'duration': duration,
                'participants': random.randint(3, 15),
                'type': random.choice(meeting_types),
                'status': random.choice(['已确认', '待确认', '已取消']),
                'description': self.fake.text(max_nb_chars=200)
            }
            meetings.append(meeting)
        
        st.session_state.mock_data['meetings'] = meetings
    
    def _generate_tasks(self):
        """Generate mock task data"""
        tasks = []
        task_types = ['准备材料', '跟进进度', '编写报告', '协调资源', '技术调研']
        priorities = ['高', '中', '低']
        statuses = ['草稿', '确认', '进行中', '完成']
        
        for i in range(30):
            task = {
                'id': i + 1,
                'title': f"{random.choice(task_types)} - {self.fake.sentence(nb_words=4)}",
                'description': self.fake.text(max_nb_chars=150),
                'assignee_id': random.randint(1, 20),
                'department': random.choice(['研发部', '测试部', '市场部', '产品部', '运营部']),
                'priority': random.choice(priorities),
                'status': random.choice(statuses),
                'deadline': self.fake.date_between(start_date='-30d', end_date='+30d'),
                'created_at': self.fake.date_time_this_month(),
                'meeting_id': random.randint(1, 50) if random.random() > 0.3 else None
            }
            tasks.append(task)
        
        st.session_state.mock_data['tasks'] = tasks
    
    def _generate_minutes(self):
        """Generate mock meeting minutes data"""
        minutes = []
        
        for i in range(25):
            minute = {
                'id': i + 1,
                'meeting_id': i + 1,
                'title': f"会议纪要 - {self.fake.sentence(nb_words=3)}",
                'summary': self.fake.text(max_nb_chars=300),
                'decisions': [self.fake.sentence() for _ in range(random.randint(2, 5))],
                'action_items': [self.fake.sentence() for _ in range(random.randint(3, 8))],
                'participants': [self.fake.name() for _ in range(random.randint(5, 12))],
                'created_at': self.fake.date_time_this_month(),
                'updated_at': self.fake.date_time_this_month(),
                'status': random.choice(['草稿', '已确认', '已发布'])
            }
            minutes.append(minute)
        
        st.session_state.mock_data['minutes'] = minutes
    
    def get_data(self):
        """Get all mock data from session state"""
        return st.session_state.mock_data
    
    def get_dataframe(self, data_type):
        """Get specific data as pandas DataFrame from session state"""
        if data_type in st.session_state.mock_data:
            return pd.DataFrame(st.session_state.mock_data[data_type])
        return pd.DataFrame()
    
    def add_meeting(self, meeting_data):
        """Add a new meeting to session state"""
        meeting_data['id'] = len(st.session_state.mock_data['meetings']) + 1
        meeting_data['created_at'] = datetime.now()
        st.session_state.mock_data['meetings'].append(meeting_data)
    
    def add_task(self, task_data):
        """Add a new task to session state"""
        task_data['id'] = len(st.session_state.mock_data['tasks']) + 1
        task_data['created_at'] = datetime.now()
        st.session_state.mock_data['tasks'].append(task_data)
    
    def add_minute(self, minute_data):
        """Add a new minute to session state"""
        minute_data['id'] = len(st.session_state.mock_data['minutes']) + 1
        minute_data['created_at'] = datetime.now()
        minute_data['updated_at'] = datetime.now()
        st.session_state.mock_data['minutes'].append(minute_data)
    
    def update_task_status(self, task_id, new_status):
        """Update task status in session state"""
        for task in st.session_state.mock_data['tasks']:
            if task['id'] == task_id:
                task['status'] = new_status
                task['updated_at'] = datetime.now()
                break
    
    def update_meeting_status(self, meeting_id, new_status):
        """Update meeting status in session state"""
        for meeting in st.session_state.mock_data['meetings']:
            if meeting['id'] == meeting_id:
                meeting['status'] = new_status
                meeting['updated_at'] = datetime.now()
                break
    
    def update_minute_status(self, minute_id, new_status):
        """Update minute status in session state"""
        for minute in st.session_state.mock_data['minutes']:
            if minute['id'] == minute_id:
                minute['status'] = new_status
                minute['updated_at'] = datetime.now()
                break
    
    def get_meeting_by_id(self, meeting_id):
        """Get meeting by ID from session state"""
        for meeting in st.session_state.mock_data['meetings']:
            if meeting['id'] == meeting_id:
                return meeting
        return None
    
    def get_task_by_id(self, task_id):
        """Get task by ID from session state"""
        for task in st.session_state.mock_data['tasks']:
            if task['id'] == task_id:
                return task
        return None
    
    def get_minute_by_id(self, minute_id):
        """Get minute by ID from session state"""
        for minute in st.session_state.mock_data['minutes']:
            if minute['id'] == minute_id:
                return minute
        return None
    
    def reset_to_default(self):
        """Reset all data to default mock state"""
        st.session_state.mock_data = {}
        self._generate_mock_data()
        st.success("数据已重置为默认状态")
    
    def get_dashboard_data(self):
        """Get aggregated data for dashboard"""
        meetings_df = self.get_dataframe('meetings')
        tasks_df = self.get_dataframe('tasks')
        rooms_df = self.get_dataframe('rooms')
        users_df = self.get_dataframe('users')
        
        return {
            'total_meetings': len(meetings_df),
            'total_tasks': len(tasks_df),
            'total_rooms': len(rooms_df),
            'total_users': len(users_df),
            'meetings_today': len(meetings_df[pd.to_datetime(meetings_df['start_time']).dt.date == datetime.now().date()]),
            'completed_tasks': len(tasks_df[tasks_df['status'] == '完成']),
            'available_rooms': len(rooms_df[rooms_df['status'] == '可用']),
            'avg_meeting_duration': meetings_df['duration'].mean() if len(meetings_df) > 0 else 0
        } 