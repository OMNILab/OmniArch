"""
Enhanced Data Manager Module
Loads mock data from CSV files with session state integration for the smart meeting system
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import random
import streamlit as st


class DataManager:
    """Enhanced data manager that loads data from CSV files and manages session state"""

    def __init__(self):
        self.csv_path = os.path.join(os.path.dirname(__file__), "../mock")
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state with mock data if not already present"""
        if "mock_data" not in st.session_state:
            st.session_state.mock_data = {}

            # Try to load from CSV first, fall back to generated data
            if self._csv_files_exist():
                print("Loading data from CSV files")
                self._load_from_csv()
            else:
                raise FileNotFoundError("CSV files not found")

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
            # Join with departments to get department names
            if "department_id" in users_df.columns:
                users_df = users_df.merge(
                    departments_df[["department_id", "department_name"]],
                    on="department_id",
                    how="left",
                )
                users_df = users_df.rename(columns={"department_name": "department"})
            # Convert datetime columns
            if "created_date" in users_df.columns:
                users_df["created_date"] = pd.to_datetime(
                    users_df["created_date"], errors="coerce"
                )
            if "last_login" in users_df.columns:
                users_df["last_login"] = pd.to_datetime(
                    users_df["last_login"], errors="coerce"
                )
            st.session_state.mock_data["users"] = users_df.to_dict("records")

            # Load bookings data
            bookings_df = pd.read_csv(os.path.join(self.csv_path, "bookings.csv"))
            # Convert datetime columns
            if "start_datetime" in bookings_df.columns:
                bookings_df["start_datetime"] = pd.to_datetime(
                    bookings_df["start_datetime"], errors="coerce"
                )
            if "end_datetime" in bookings_df.columns:
                bookings_df["end_datetime"] = pd.to_datetime(
                    bookings_df["end_datetime"], errors="coerce"
                )
            if "created_datetime" in bookings_df.columns:
                bookings_df["created_datetime"] = pd.to_datetime(
                    bookings_df["created_datetime"], errors="coerce"
                )
            st.session_state.mock_data["meetings"] = bookings_df.to_dict("records")

            # Load meeting minutes data
            minutes_df = pd.read_csv(os.path.join(self.csv_path, "meeting_minutes.csv"))
            if "created_datetime" in minutes_df.columns:
                minutes_df["created_datetime"] = pd.to_datetime(
                    minutes_df["created_datetime"], errors="coerce"
                )
            if "updated_datetime" in minutes_df.columns:
                minutes_df["updated_datetime"] = pd.to_datetime(
                    minutes_df["updated_datetime"], errors="coerce"
                )
            st.session_state.mock_data["minutes"] = minutes_df.to_dict("records")

            # Load tasks data
            tasks_df = pd.read_csv(os.path.join(self.csv_path, "tasks.csv"))
            # Join with departments to get department names
            if "department_id" in tasks_df.columns:
                tasks_df = tasks_df.merge(
                    departments_df[["department_id", "department_name"]],
                    on="department_id",
                    how="left",
                )
                tasks_df = tasks_df.rename(columns={"department_name": "department"})
            if "deadline" in tasks_df.columns:
                tasks_df["deadline"] = pd.to_datetime(
                    tasks_df["deadline"], errors="coerce"
                )
            if "created_datetime" in tasks_df.columns:
                tasks_df["created_datetime"] = pd.to_datetime(
                    tasks_df["created_datetime"], errors="coerce"
                )
            if "updated_datetime" in tasks_df.columns:
                tasks_df["updated_datetime"] = pd.to_datetime(
                    tasks_df["updated_datetime"], errors="coerce"
                )
            st.session_state.mock_data["tasks"] = tasks_df.to_dict("records")

            # Load booking statistics data
            statistics_df = pd.read_csv(
                os.path.join(self.csv_path, "booking_statistics.csv")
            )
            # Join with departments to get department names for department statistics
            if "department_id" in statistics_df.columns:
                # Filter out empty department_id values for joining
                dept_stats_df = statistics_df[
                    statistics_df["department_id"].notna()
                    & (statistics_df["department_id"] != "")
                ]
                if len(dept_stats_df) > 0:
                    dept_stats_df = dept_stats_df.merge(
                        departments_df[["department_id", "department_name"]],
                        on="department_id",
                        how="left",
                    )
                    dept_stats_df = dept_stats_df.rename(
                        columns={"department_name": "department"}
                    )
                    # Update the original dataframe with department names
                    statistics_df = statistics_df.merge(
                        dept_stats_df[["stat_id", "department"]],
                        on="stat_id",
                        how="left",
                    )
            if "created_date" in statistics_df.columns:
                statistics_df["created_date"] = pd.to_datetime(
                    statistics_df["created_date"], errors="coerce"
                )
            st.session_state.mock_data["statistics"] = statistics_df.to_dict("records")

            # Load user requirements data
            requirements_df = pd.read_csv(
                os.path.join(self.csv_path, "user_requirements.csv")
            )
            if "created_datetime" in requirements_df.columns:
                requirements_df["created_datetime"] = pd.to_datetime(
                    requirements_df["created_datetime"], errors="coerce"
                )
            if "parsed_datetime" in requirements_df.columns:
                requirements_df["parsed_datetime"] = pd.to_datetime(
                    requirements_df["parsed_datetime"], errors="coerce"
                )
            st.session_state.mock_data["requirements"] = requirements_df.to_dict(
                "records"
            )

        except Exception as e:
            raise Exception(f"Error loading CSV files: {e}") from e

    def get_data(self):
        """Get all mock data from session state"""
        return st.session_state.mock_data

    def get_dataframe(self, data_type):
        """Get specific data as pandas DataFrame from session state"""
        if data_type in st.session_state.mock_data:
            df = pd.DataFrame(st.session_state.mock_data[data_type])
            return df
        return pd.DataFrame()

    def add_meeting(self, meeting_data):
        """Add a new meeting to session state"""
        meeting_data["booking_id"] = len(st.session_state.mock_data["meetings"]) + 1
        meeting_data["created_datetime"] = datetime.now()
        st.session_state.mock_data["meetings"].append(meeting_data)

    def add_task(self, task_data):
        """Add a new task to session state"""
        task_data["task_id"] = len(st.session_state.mock_data["tasks"]) + 1
        task_data["created_datetime"] = datetime.now()
        st.session_state.mock_data["tasks"].append(task_data)

    def add_minute(self, minute_data):
        """Add a new minute to session state"""
        # Use minute_id to match CSV structure
        minute_data["minute_id"] = len(st.session_state.mock_data["minutes"]) + 1
        minute_data["created_datetime"] = datetime.now()
        minute_data["updated_datetime"] = datetime.now()
        st.session_state.mock_data["minutes"].append(minute_data)

    def update_task_status(self, task_id, new_status):
        """Update task status in session state"""
        for task in st.session_state.mock_data["tasks"]:
            if task.get("task_id") == task_id:
                task["status"] = new_status
                task["updated_datetime"] = datetime.now()
                break

    def update_meeting_status(self, meeting_id, new_status):
        """Update meeting status in session state"""
        for meeting in st.session_state.mock_data["meetings"]:
            if meeting["booking_id"] == meeting_id:
                meeting["meeting_status"] = new_status
                meeting["updated_datetime"] = datetime.now()
                break

    def update_minute_status(self, minute_id, new_status):
        """Update minute status in session state"""
        for minute in st.session_state.mock_data["minutes"]:
            # Check both 'id' and 'minute_id' fields for compatibility
            minute_identifier = minute.get("minute_id")
            if minute_identifier == minute_id:
                minute["status"] = new_status
                minute["updated_datetime"] = datetime.now()
                break

    def delete_minute(self, minute_id):
        """Delete a minute from session state"""
        for i, minute in enumerate(st.session_state.mock_data["minutes"]):
            # Check both 'id' and 'minute_id' fields for compatibility
            minute_identifier = minute.get("minute_id")
            if minute_identifier == minute_id:
                deleted_minute = st.session_state.mock_data["minutes"].pop(i)
                return deleted_minute
        return None

    def get_meeting_by_id(self, meeting_id):
        """Get meeting by ID from session state"""
        for meeting in st.session_state.mock_data["meetings"]:
            if meeting["booking_id"] == meeting_id:
                return meeting
        return None

    def get_task_by_id(self, task_id):
        """Get task by ID from session state"""
        for task in st.session_state.mock_data["tasks"]:
            if task["task_id"] == task_id:
                return task
        return None

    def get_minute_by_id(self, minute_id):
        """Get minute by ID from session state"""
        for minute in st.session_state.mock_data["minutes"]:
            # Check both 'id' and 'minute_id' fields for compatibility
            minute_identifier = minute.get("minute_id")
            if minute_identifier == minute_id:
                return minute
        return None

    def reset_to_default(self):
        """Reset all data to default mock state"""
        st.session_state.mock_data = {}
        if self._csv_files_exist():
            self._load_from_csv()
        else:
            raise FileNotFoundError("CSV files not found")
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
                        pd.to_datetime(meetings_df["start_datetime"]).dt.date
                        == datetime.now().date()
                    ]
                )
                if len(meetings_df) > 0 and "start_datetime" in meetings_df.columns
                else 0
            ),
            "completed_tasks": (
                len(tasks_df[tasks_df["status"] == "完成"]) if len(tasks_df) > 0 else 0
            ),
            "available_rooms": (
                len(rooms_df[rooms_df["status"] == "可用"]) if len(rooms_df) > 0 else 0
            ),
            "avg_meeting_duration": (
                meetings_df["duration_minutes"].mean()
                if len(meetings_df) > 0 and "duration_minutes" in meetings_df.columns
                else 0
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
            if (
                "投影仪" in equipment_needed
                and "has_projector" in suitable_rooms.columns
            ):
                suitable_rooms = suitable_rooms[suitable_rooms["has_projector"] == 1]
            if (
                "视频会议设备" in equipment_needed
                and "has_phone" in suitable_rooms.columns
            ):
                suitable_rooms = suitable_rooms[suitable_rooms["has_phone"] == 1]
            if (
                "白板" in equipment_needed
                and "has_whiteboard" in suitable_rooms.columns
            ):
                suitable_rooms = suitable_rooms[suitable_rooms["has_whiteboard"] == 1]
            if "显示屏" in equipment_needed and "has_screen" in suitable_rooms.columns:
                suitable_rooms = suitable_rooms[suitable_rooms["has_screen"] == 1]

        # Filter by location if specified
        if location_preference and "building_id" in suitable_rooms.columns:
            suitable_rooms = suitable_rooms[
                suitable_rooms["building_id"] == location_preference
            ]

        return suitable_rooms.to_dict("records") if len(suitable_rooms) > 0 else []

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

    def update_meeting_statuses(self):
        """自动更新会议状态基于当前时间"""
        current_time = datetime.now()

        for meeting in st.session_state.mock_data["meetings"]:
            start_time = pd.to_datetime(meeting.get("start_datetime"), errors="coerce")
            end_time = pd.to_datetime(meeting.get("end_datetime"), errors="coerce")

            if pd.notna(start_time) and pd.notna(end_time):
                if current_time < start_time:
                    meeting["meeting_status"] = "upcoming"
                elif start_time <= current_time <= end_time:
                    meeting["meeting_status"] = "ongoing"
                else:
                    meeting["meeting_status"] = "completed"

    def get_upcoming_meetings(self, limit=10):
        """获取即将到来的会议列表"""
        self.update_meeting_statuses()
        meetings_df = self.get_dataframe("meetings")

        if len(meetings_df) == 0:
            return []

        # 筛选即将到来的会议
        upcoming_meetings = meetings_df[meetings_df["meeting_status"] == "upcoming"]

        # 按开始时间排序
        if len(upcoming_meetings) > 0 and "start_datetime" in upcoming_meetings.columns:
            upcoming_meetings = upcoming_meetings.sort_values("start_datetime")

        return (
            upcoming_meetings.head(limit).to_dict("records")
            if len(upcoming_meetings) > 0
            else []
        )

    def get_ongoing_meetings(self):
        """获取正在进行的会议列表"""
        self.update_meeting_statuses()
        meetings_df = self.get_dataframe("meetings")

        if len(meetings_df) == 0:
            return []

        ongoing_meetings = meetings_df[meetings_df["meeting_status"] == "ongoing"]
        return ongoing_meetings.to_dict("records") if len(ongoing_meetings) > 0 else []

    def get_completed_meetings(self, limit=10):
        """获取已完成的会议列表"""
        self.update_meeting_statuses()
        meetings_df = self.get_dataframe("meetings")

        if len(meetings_df) == 0:
            return []

        # 筛选已完成的会议
        completed_meetings = meetings_df[meetings_df["meeting_status"] == "completed"]

        # 按开始时间倒序排序
        if (
            len(completed_meetings) > 0
            and "start_datetime" in completed_meetings.columns
        ):
            completed_meetings = completed_meetings.sort_values(
                "start_datetime", ascending=False
            )

        return (
            completed_meetings.head(limit).to_dict("records")
            if len(completed_meetings) > 0
            else []
        )
