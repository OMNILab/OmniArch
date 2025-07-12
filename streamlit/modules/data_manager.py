"""
Enhanced Data Manager Module
Loads mock data from CSV files with session state integration for the smart meeting system
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from faker import Faker
import random
import streamlit as st


class DataManager:
    """Enhanced data manager that loads data from CSV files and manages session state"""

    def __init__(self, use_csv=True):
        self.fake = Faker("zh_CN")
        self.use_csv = use_csv
        self.csv_path = "streamlit/mock"
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state with mock data if not already present"""
        if "mock_data" not in st.session_state:
            st.session_state.mock_data = {}

            # Try to load from CSV first, fall back to generated data
            if self.use_csv and self._csv_files_exist():
                self._load_from_csv()
            else:
                self._generate_mock_data()

    def _csv_files_exist(self):
        """Check if CSV files exist"""
        required_files = [
            "buildings.csv",
            "meeting_rooms.csv",
            "departments.csv",
            "users.csv",
            "bookings.csv",
            "meeting_minutes.csv",
            "tasks.csv",
            "booking_statistics.csv",
            "user_requirements.csv",
        ]

        for file in required_files:
            file_path = os.path.join(self.csv_path, file)
            if not os.path.exists(file_path):
                return False
        return True

    def _load_from_csv(self):
        """Load data from CSV files into session state"""
        try:
            # Load buildings data
            buildings_df = pd.read_csv(os.path.join(self.csv_path, "buildings.csv"))
            st.session_state.mock_data["buildings"] = buildings_df.to_dict("records")

            # Load meeting rooms data
            rooms_df = pd.read_csv(os.path.join(self.csv_path, "meeting_rooms.csv"))
            st.session_state.mock_data["rooms"] = rooms_df.to_dict("records")

            # Load departments data
            departments_df = pd.read_csv(os.path.join(self.csv_path, "departments.csv"))
            st.session_state.mock_data["departments"] = departments_df.to_dict(
                "records"
            )

            # Load users data
            users_df = pd.read_csv(os.path.join(self.csv_path, "users.csv"))
            st.session_state.mock_data["users"] = users_df.to_dict("records")

            # Load bookings data
            bookings_df = pd.read_csv(os.path.join(self.csv_path, "bookings.csv"))
            # Convert datetime columns
            bookings_df["start_datetime"] = pd.to_datetime(
                bookings_df["start_datetime"]
            )
            bookings_df["end_datetime"] = pd.to_datetime(bookings_df["end_datetime"])
            bookings_df["created_datetime"] = pd.to_datetime(
                bookings_df["created_datetime"]
            )
            st.session_state.mock_data["meetings"] = bookings_df.to_dict("records")

            # Load meeting minutes data
            minutes_df = pd.read_csv(os.path.join(self.csv_path, "meeting_minutes.csv"))
            minutes_df["created_datetime"] = pd.to_datetime(
                minutes_df["created_datetime"]
            )
            minutes_df["updated_datetime"] = pd.to_datetime(
                minutes_df["updated_datetime"]
            )
            st.session_state.mock_data["minutes"] = minutes_df.to_dict("records")

            # Load tasks data
            tasks_df = pd.read_csv(os.path.join(self.csv_path, "tasks.csv"))
            tasks_df["deadline"] = pd.to_datetime(tasks_df["deadline"])
            tasks_df["created_datetime"] = pd.to_datetime(tasks_df["created_datetime"])
            tasks_df["updated_datetime"] = pd.to_datetime(tasks_df["updated_datetime"])
            st.session_state.mock_data["tasks"] = tasks_df.to_dict("records")

            # Load booking statistics data
            statistics_df = pd.read_csv(
                os.path.join(self.csv_path, "booking_statistics.csv")
            )
            statistics_df["created_date"] = pd.to_datetime(
                statistics_df["created_date"]
            )
            st.session_state.mock_data["statistics"] = statistics_df.to_dict("records")

            # Load user requirements data
            requirements_df = pd.read_csv(
                os.path.join(self.csv_path, "user_requirements.csv")
            )
            requirements_df["created_datetime"] = pd.to_datetime(
                requirements_df["created_datetime"]
            )
            # Handle nullable datetime columns
            requirements_df["parsed_datetime"] = pd.to_datetime(
                requirements_df["parsed_datetime"], errors="coerce"
            )
            st.session_state.mock_data["requirements"] = requirements_df.to_dict(
                "records"
            )

        except Exception as e:
            print(f"Error loading CSV files: {e}")
            print("Falling back to generated mock data...")
            self._generate_mock_data()

    def _generate_mock_data(self):
        """Generate mock data (fallback method)"""
        self._generate_users()
        self._generate_rooms()
        self._generate_meetings()
        self._generate_tasks()
        self._generate_minutes()

    def _generate_users(self):
        """Generate mock user data"""
        users = []
        departments = ["研发部", "测试部", "市场部", "产品部", "运营部"]
        roles = ["会议组织者", "会议参与者", "系统管理员"]

        for i in range(20):
            user = {
                "id": i + 1,
                "user_id": i + 1,
                "username": self.fake.user_name(),
                "name": self.fake.name(),
                "email": self.fake.email(),
                "department": random.choice(departments),
                "role": random.choice(roles),
                "created_at": self.fake.date_time_this_year(),
            }
            users.append(user)

        st.session_state.mock_data["users"] = users

    def _generate_rooms(self):
        """Generate mock room data"""
        rooms = []
        room_types = ["会议室", "培训室", "视频会议室", "小型会议室"]
        floors = ["3楼", "4楼", "5楼", "6楼"]

        for i in range(8):
            room = {
                "id": i + 1,
                "room_id": i + 1,
                "name": f"{random.choice(floors)}{chr(65 + i)}会议室",
                "room_name": f"{random.choice(floors)}{chr(65 + i)}会议室",
                "capacity": random.choice([6, 8, 12, 15, 20, 25, 30, 40]),
                "type": random.choice(room_types),
                "room_type": random.choice(room_types),
                "equipment": random.choice(
                    ["投影仪", "视频会议设备", "白板", "音响设备"]
                ),
                "floor": random.choice(floors),
                "status": random.choice(["可用", "维护中", "已预订"]),
            }
            rooms.append(room)

        st.session_state.mock_data["rooms"] = rooms

    def _generate_meetings(self):
        """Generate mock meeting data"""
        meetings = []
        meeting_types = ["项目讨论", "产品评审", "技术分享", "团队会议", "客户会议"]

        for i in range(50):
            start_time = self.fake.date_time_this_month()
            duration = random.choice([30, 60, 90, 120, 180])

            meeting = {
                "id": i + 1,
                "booking_id": i + 1,
                "title": f"{random.choice(meeting_types)} - {self.fake.sentence(nb_words=3)}",
                "meeting_title": f"{random.choice(meeting_types)} - {self.fake.sentence(nb_words=3)}",
                "room_id": random.randint(1, 8),
                "organizer_id": random.randint(1, 20),
                "start_time": start_time,
                "start_datetime": start_time,
                "end_time": start_time + timedelta(minutes=duration),
                "end_datetime": start_time + timedelta(minutes=duration),
                "duration": duration,
                "duration_minutes": duration,
                "participants": random.randint(3, 15),
                "participant_count": random.randint(3, 15),
                "type": random.choice(meeting_types),
                "meeting_type": random.choice(meeting_types),
                "status": random.choice(["已确认", "待确认", "已取消"]),
                "description": self.fake.text(max_nb_chars=200),
            }
            meetings.append(meeting)

        st.session_state.mock_data["meetings"] = meetings

    def _generate_tasks(self):
        """Generate mock task data"""
        tasks = []
        task_types = ["准备材料", "跟进进度", "编写报告", "协调资源", "技术调研"]
        priorities = ["高", "中", "低"]
        statuses = ["草稿", "确认", "进行中", "完成"]

        for i in range(30):
            task = {
                "id": i + 1,
                "task_id": i + 1,
                "title": f"{random.choice(task_types)} - {self.fake.sentence(nb_words=4)}",
                "description": self.fake.text(max_nb_chars=150),
                "assignee_id": random.randint(1, 20),
                "department": random.choice(
                    ["研发部", "测试部", "市场部", "产品部", "运营部"]
                ),
                "priority": random.choice(priorities),
                "status": random.choice(statuses),
                "deadline": self.fake.date_between(start_date="-30d", end_date="+30d"),
                "created_at": self.fake.date_time_this_month(),
                "meeting_id": random.randint(1, 50) if random.random() > 0.3 else None,
            }
            tasks.append(task)

        st.session_state.mock_data["tasks"] = tasks

    def _generate_minutes(self):
        """Generate mock meeting minutes data"""
        minutes = []

        for i in range(25):
            minute = {
                "id": i + 1,
                "minute_id": i + 1,
                "meeting_id": i + 1,
                "booking_id": i + 1,
                "title": f"会议纪要 - {self.fake.sentence(nb_words=3)}",
                "meeting_title": f"会议纪要 - {self.fake.sentence(nb_words=3)}",
                "summary": self.fake.text(max_nb_chars=300),
                "decisions": [
                    self.fake.sentence() for _ in range(random.randint(2, 5))
                ],
                "action_items": [
                    self.fake.sentence() for _ in range(random.randint(3, 8))
                ],
                "participants": [
                    self.fake.name() for _ in range(random.randint(5, 12))
                ],
                "created_at": self.fake.date_time_this_month(),
                "updated_at": self.fake.date_time_this_month(),
                "status": random.choice(["草稿", "已确认", "已发布"]),
            }
            minutes.append(minute)

        st.session_state.mock_data["minutes"] = minutes

    def get_data(self):
        """Get all mock data from session state"""
        return st.session_state.mock_data

    def get_dataframe(self, data_type):
        """Get specific data as pandas DataFrame from session state with CSV compatibility"""
        if data_type in st.session_state.mock_data:
            df = pd.DataFrame(st.session_state.mock_data[data_type])

            # Convert datetime columns for consistency
            if data_type == "meetings":
                datetime_cols = ["start_datetime", "end_datetime", "created_datetime"]
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors="coerce")

                # Ensure legacy column names exist
                if "start_datetime" in df.columns and "start_time" not in df.columns:
                    df["start_time"] = df["start_datetime"]
                if "end_datetime" in df.columns and "end_time" not in df.columns:
                    df["end_time"] = df["end_datetime"]
                if "duration_minutes" in df.columns and "duration" not in df.columns:
                    df["duration"] = df["duration_minutes"]
                if (
                    "participant_count" in df.columns
                    and "participants" not in df.columns
                ):
                    df["participants"] = df["participant_count"]

            elif data_type == "tasks":
                datetime_cols = ["deadline", "created_datetime", "updated_datetime"]
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors="coerce")

                # Ensure legacy column names exist
                if "created_datetime" in df.columns and "created_at" not in df.columns:
                    df["created_at"] = df["created_datetime"]
                if "department_id" in df.columns and "department" not in df.columns:
                    # Map department_id to department name
                    dept_mapping = {
                        1: "研发部",
                        2: "测试部",
                        3: "架构部",
                        4: "产品部",
                        5: "运营部",
                        6: "设计部",
                        7: "市场部",
                        8: "销售部",
                        9: "人事部",
                        10: "财务部",
                    }
                    df["department"] = df["department_id"].map(dept_mapping)

            elif data_type == "minutes":
                datetime_cols = ["created_datetime", "updated_datetime"]
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors="coerce")

                # Ensure legacy column names exist
                if "created_datetime" in df.columns and "created_at" not in df.columns:
                    df["created_at"] = df["created_datetime"]
                if "updated_datetime" in df.columns and "updated_at" not in df.columns:
                    df["updated_at"] = df["updated_datetime"]
                if "minute_id" in df.columns and "id" not in df.columns:
                    df["id"] = df["minute_id"]
                if "booking_id" in df.columns and "meeting_id" not in df.columns:
                    df["meeting_id"] = df["booking_id"]

            elif data_type == "users":
                datetime_cols = ["created_date", "last_login"]
                for col in datetime_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors="coerce")

                # Ensure legacy column names exist
                if "created_date" in df.columns and "created_at" not in df.columns:
                    df["created_at"] = df["created_date"]
                if "user_id" in df.columns and "id" not in df.columns:
                    df["id"] = df["user_id"]
                if "department_id" in df.columns and "department" not in df.columns:
                    # Map department_id to department name
                    dept_mapping = {
                        1: "研发部",
                        2: "测试部",
                        3: "架构部",
                        4: "产品部",
                        5: "运营部",
                        6: "设计部",
                        7: "市场部",
                        8: "销售部",
                        9: "人事部",
                        10: "财务部",
                    }
                    df["department"] = df["department_id"].map(dept_mapping)

            elif data_type == "rooms":
                # Ensure legacy column names exist
                if "room_id" in df.columns and "id" not in df.columns:
                    df["id"] = df["room_id"]
                if "room_name" in df.columns and "name" not in df.columns:
                    df["name"] = df["room_name"]
                if "room_type" in df.columns and "type" not in df.columns:
                    df["type"] = df["room_type"]

            return df
        return pd.DataFrame()

    def add_meeting(self, meeting_data):
        """Add a new meeting to session state"""
        meeting_data["id"] = len(st.session_state.mock_data["meetings"]) + 1
        meeting_data["booking_id"] = meeting_data["id"]
        meeting_data["created_at"] = datetime.now()
        st.session_state.mock_data["meetings"].append(meeting_data)

    def add_task(self, task_data):
        """Add a new task to session state"""
        task_data["id"] = len(st.session_state.mock_data["tasks"]) + 1
        task_data["task_id"] = task_data["id"]
        task_data["created_at"] = datetime.now()
        st.session_state.mock_data["tasks"].append(task_data)

    def add_minute(self, minute_data):
        """Add a new minute to session state"""
        minute_data["id"] = len(st.session_state.mock_data["minutes"]) + 1
        minute_data["created_at"] = datetime.now()
        minute_data["updated_at"] = datetime.now()
        st.session_state.mock_data["minutes"].append(minute_data)

    def update_task_status(self, task_id, new_status):
        """Update task status in session state"""
        for task in st.session_state.mock_data["tasks"]:
            if task.get("id") == task_id or task.get("task_id") == task_id:
                task["status"] = new_status
                task["updated_at"] = datetime.now()
                break

    def update_meeting_status(self, meeting_id, new_status):
        """Update meeting status in session state"""
        for meeting in st.session_state.mock_data["meetings"]:
            if meeting["id"] == meeting_id:
                meeting["status"] = new_status
                meeting["updated_at"] = datetime.now()
                break

    def update_minute_status(self, minute_id, new_status):
        """Update minute status in session state"""
        for minute in st.session_state.mock_data["minutes"]:
            if minute["id"] == minute_id:
                minute["status"] = new_status
                minute["updated_at"] = datetime.now()
                break

    def get_meeting_by_id(self, meeting_id):
        """Get meeting by ID from session state"""
        for meeting in st.session_state.mock_data["meetings"]:
            if meeting["id"] == meeting_id:
                return meeting
        return None

    def get_task_by_id(self, task_id):
        """Get task by ID from session state"""
        for task in st.session_state.mock_data["tasks"]:
            if task["id"] == task_id:
                return task
        return None

    def get_minute_by_id(self, minute_id):
        """Get minute by ID from session state"""
        for minute in st.session_state.mock_data["minutes"]:
            if minute["id"] == minute_id:
                return minute
        return None

    def reset_to_default(self):
        """Reset all data to default mock state"""
        st.session_state.mock_data = {}
        # Try to load from CSV first, fall back to generated data
        if self.use_csv and self._csv_files_exist():
            self._load_from_csv()
        else:
            self._generate_mock_data()
        st.success("数据已重置为默认状态")

    def get_dashboard_data(self):
        """Get aggregated data for dashboard"""
        meetings_df = self.get_dataframe("meetings")
        tasks_df = self.get_dataframe("tasks")
        rooms_df = self.get_dataframe("rooms")
        users_df = self.get_dataframe("users")

        return {
            "total_meetings": len(meetings_df),
            "total_tasks": len(tasks_df),
            "total_rooms": len(rooms_df),
            "total_users": len(users_df),
            "meetings_today": (
                len(
                    meetings_df[
                        pd.to_datetime(meetings_df["start_time"]).dt.date
                        == datetime.now().date()
                    ]
                )
                if len(meetings_df) > 0
                else 0
            ),
            "completed_tasks": len(tasks_df[tasks_df["status"] == "完成"]),
            "available_rooms": len(rooms_df[rooms_df["status"] == "可用"]),
            "avg_meeting_duration": (
                meetings_df["duration"].mean() if len(meetings_df) > 0 else 0
            ),
        }

    def get_room_recommendations(
        self, capacity, equipment_needed=None, location_preference=None
    ):
        """Get room recommendations based on requirements"""
        rooms_df = self.get_dataframe("rooms")

        # Filter by capacity and availability
        suitable_rooms = rooms_df[
            (rooms_df["capacity"] >= capacity) & (rooms_df["status"] == "可用")
        ]

        # Filter by equipment if specified
        if equipment_needed:
            if "投影仪" in equipment_needed:
                suitable_rooms = suitable_rooms[
                    suitable_rooms.get("has_projector", 0) == 1
                ]
            if "视频会议设备" in equipment_needed:
                suitable_rooms = suitable_rooms[suitable_rooms.get("has_phone", 0) == 1]
            if "白板" in equipment_needed:
                suitable_rooms = suitable_rooms[
                    suitable_rooms.get("has_whiteboard", 0) == 1
                ]
            if "显示屏" in equipment_needed:
                suitable_rooms = suitable_rooms[
                    suitable_rooms.get("has_screen", 0) == 1
                ]

        # Filter by location if specified
        if location_preference:
            suitable_rooms = suitable_rooms[
                suitable_rooms.get("building_id", 0) == location_preference
            ]

        return suitable_rooms.to_dict("records")

    def get_booking_statistics(self, stat_type=None, period=None):
        """Get booking statistics"""
        if "statistics" not in st.session_state.mock_data:
            return []

        stats = st.session_state.mock_data["statistics"]

        if stat_type:
            stats = [s for s in stats if s["stat_type"] == stat_type]

        if period:
            stats = [s for s in stats if s["stat_period"] == period]

        return stats

    def get_user_requirements(self, user_id=None, status=None):
        """Get user requirements"""
        if "requirements" not in st.session_state.mock_data:
            return []

        requirements = st.session_state.mock_data["requirements"]

        if user_id:
            requirements = [r for r in requirements if r["user_id"] == user_id]

        if status:
            requirements = [r for r in requirements if r["status"] == status]

        return requirements
