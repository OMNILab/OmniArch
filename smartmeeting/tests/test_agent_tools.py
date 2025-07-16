import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
from smartmeeting.agent.tools import (
    recommend_available_rooms,
    book_room,
    lookup_user_bookings,
    cancel_bookings,
    alter_booking,
)


class TestAgentTools:
    """Test cases for agent tools"""

    def setup_method(self):
        """Setup test data for each test method"""
        # Mock room data
        self.mock_rooms_data = [
            {
                "id": 1,
                "name": "会议室A",
                "capacity": 10,
                "building": "A栋",
                "equipment": "投影仪,白板",
                "status": "可用",
            },
            {
                "id": 2,
                "name": "会议室B",
                "capacity": 20,
                "building": "B栋",
                "equipment": "投影仪,视频会议",
                "status": "可用",
            },
            {
                "id": 3,
                "name": "会议室C",
                "capacity": 5,
                "building": "A栋",
                "equipment": "白板",
                "status": "可用",
            },
        ]

        # Mock meetings data
        self.mock_meetings_data = [
            {
                "id": 1,
                "room_id": 1,
                "organizer_id": 1,
                "start_time": "2025-01-16 14:00:00",
                "end_time": "2025-01-16 15:00:00",
                "title": "项目讨论",
            }
        ]

        # Create mock DataManager
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.get_dataframe.return_value = pd.DataFrame()

    @patch("smartmeeting.agent.tools.DataManager")
    def test_recommend_available_rooms_basic(self, mock_data_manager_class):
        """Test basic room recommendation without filters"""
        # Setup mock
        mock_data_manager_class.return_value = self.mock_data_manager
        self.mock_data_manager.get_dataframe.side_effect = [
            pd.DataFrame(self.mock_rooms_data),
            pd.DataFrame(self.mock_meetings_data),
        ]

        # Test parameters
        start_time = "2025-01-16 16:00:00"
        end_time = "2025-01-16 17:00:00"
        capacity = 8

        result = recommend_available_rooms(start_time, end_time, capacity)

        # Verify results
        assert isinstance(result, list)
        assert len(result) == 2  # Should find rooms A and B (capacity >= 8)

        # Check that returned rooms have sufficient capacity
        for room in result:
            assert room["capacity"] >= capacity

    @patch("smartmeeting.agent.tools.DataManager")
    def test_recommend_available_rooms_with_equipment_filter(
        self, mock_data_manager_class
    ):
        """Test room recommendation with equipment filter"""
        # Setup mock
        mock_data_manager_class.return_value = self.mock_data_manager
        self.mock_data_manager.get_dataframe.side_effect = [
            pd.DataFrame(self.mock_rooms_data),
            pd.DataFrame(self.mock_meetings_data),
        ]

        # Test with equipment filter
        start_time = "2025-01-16 16:00:00"
        end_time = "2025-01-16 17:00:00"
        capacity = 5
        equipment_needs = ["投影仪"]

        result = recommend_available_rooms(
            start_time, end_time, capacity, equipment_needs=equipment_needs
        )

        # Should only return rooms with projector
        assert len(result) == 2  # Rooms A and B have projectors
        for room in result:
            assert "投影仪" in room["equipment"]

    @patch("smartmeeting.agent.tools.DataManager")
    def test_recommend_available_rooms_with_location_filter(
        self, mock_data_manager_class
    ):
        """Test room recommendation with location filter"""
        # Setup mock
        mock_data_manager_class.return_value = self.mock_data_manager
        self.mock_data_manager.get_dataframe.side_effect = [
            pd.DataFrame(self.mock_rooms_data),
            pd.DataFrame(self.mock_meetings_data),
        ]

        # Test with location filter
        start_time = "2025-01-16 16:00:00"
        end_time = "2025-01-16 17:00:00"
        capacity = 5
        preferred_location = ["A栋"]

        result = recommend_available_rooms(
            start_time, end_time, capacity, preferred_location=preferred_location
        )

        # Should only return rooms in A栋
        assert len(result) == 2  # Rooms A and C are in A栋
        for room in result:
            assert "A栋" in room["building"]

    @patch("smartmeeting.agent.tools.DataManager")
    def test_recommend_available_rooms_time_conflict(self, mock_data_manager_class):
        """Test room recommendation with time conflict"""
        # Setup mock with conflicting meeting
        mock_data_manager_class.return_value = self.mock_data_manager
        self.mock_data_manager.get_dataframe.side_effect = [
            pd.DataFrame(self.mock_rooms_data),
            pd.DataFrame(self.mock_meetings_data),
        ]

        # Test with conflicting time
        start_time = "2025-01-16 14:30:00"  # Conflicts with existing meeting
        end_time = "2025-01-16 15:30:00"
        capacity = 5

        result = recommend_available_rooms(start_time, end_time, capacity)

        # Should not return room 1 (has conflict)
        room_ids = [room["room_id"] for room in result]
        assert 1 not in room_ids

    @patch("smartmeeting.agent.tools.DataManager")
    def test_book_room_success(self, mock_data_manager_class):
        """Test successful room booking"""
        # Setup mock
        mock_data_manager_class.return_value = self.mock_data_manager

        # Test booking
        room_id = 1
        user_id = 123
        start_time = "2025-01-16 16:00:00"
        end_time = "2025-01-16 17:00:00"
        title = "测试会议"

        result = book_room(room_id, user_id, start_time, end_time, title)

        # Verify result
        assert "预订成功" in result
        assert title in result
        assert str(room_id) in result

        # Verify that add_meeting was called
        self.mock_data_manager.add_meeting.assert_called_once()
        call_args = self.mock_data_manager.add_meeting.call_args[0][0]
        assert call_args["title"] == title
        assert call_args["room_id"] == room_id
        assert call_args["organizer_id"] == user_id
        assert call_args["start_time"] == start_time
        assert call_args["end_time"] == end_time

    @patch("smartmeeting.agent.tools.DataManager")
    def test_book_room_failure(self, mock_data_manager_class):
        """Test room booking failure"""
        # Setup mock to raise exception
        mock_data_manager_class.return_value = self.mock_data_manager
        self.mock_data_manager.add_meeting.side_effect = Exception("Database error")

        # Test booking
        result = book_room(
            1, 123, "2025-01-16 16:00:00", "2025-01-16 17:00:00", "测试会议"
        )

        # Verify error message
        assert "预订失败" in result
        assert "Database error" in result

    @patch("smartmeeting.agent.tools.DataManager")
    def test_lookup_user_bookings(self, mock_data_manager_class):
        """Test user bookings lookup"""
        # Setup mock
        mock_data_manager_class.return_value = self.mock_data_manager

        # Create future meetings for user
        future_meetings = [
            {
                "id": 1,
                "room_id": 1,
                "organizer_id": 123,
                "start_time": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "end_time": (datetime.now() + timedelta(days=1, hours=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "title": "未来会议1",
            },
            {
                "id": 2,
                "room_id": 2,
                "organizer_id": 123,
                "start_time": (datetime.now() + timedelta(days=2)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "end_time": (datetime.now() + timedelta(days=2, hours=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "title": "未来会议2",
            },
        ]

        all_meetings = future_meetings + [
            {
                "id": 3,
                "room_id": 1,
                "organizer_id": 123,
                "start_time": (datetime.now() - timedelta(days=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "end_time": (datetime.now() - timedelta(days=1, hours=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "title": "过去会议",
            }
        ]

        self.mock_data_manager.get_dataframe.return_value = pd.DataFrame(all_meetings)

        # Test lookup
        user_id = 123
        result = lookup_user_bookings(user_id)

        # Should only return future meetings
        assert len(result) == 2
        for booking in result:
            assert booking["organizer_id"] == user_id
            assert "未来会议" in booking["title"]

    @patch("smartmeeting.agent.tools.DataManager")
    def test_cancel_bookings_success(self, mock_data_manager_class):
        """Test successful booking cancellation"""
        # Setup mock
        mock_data_manager_class.return_value = self.mock_data_manager

        # Test cancellation
        user_id = 123
        booking_ids = [1, 2]

        result = cancel_bookings(user_id, booking_ids)

        # Verify result
        assert "成功取消 2 个预订" in result

        # Verify that update_meeting_status was called for each booking
        assert self.mock_data_manager.update_meeting_status.call_count == 2
        calls = self.mock_data_manager.update_meeting_status.call_args_list
        assert calls[0][0][0] == 1  # First booking ID
        assert calls[0][0][1] == "已取消"  # Status
        assert calls[1][0][0] == 2  # Second booking ID
        assert calls[1][0][1] == "已取消"  # Status

    @patch("smartmeeting.agent.tools.DataManager")
    def test_cancel_bookings_partial_failure(self, mock_data_manager_class):
        """Test booking cancellation with partial failure"""
        # Setup mock to fail on second booking
        mock_data_manager_class.return_value = self.mock_data_manager
        self.mock_data_manager.update_meeting_status.side_effect = [
            None,  # First call succeeds
            Exception("Booking not found"),  # Second call fails
        ]

        # Test cancellation
        user_id = 123
        booking_ids = [1, 2]

        result = cancel_bookings(user_id, booking_ids)

        # Verify result
        assert "成功取消 1 个预订" in result
        assert "预订ID 2 取消失败" in result

    def test_alter_booking(self):
        """Test booking alteration (currently returns guidance message)"""
        booking_id = 1
        user_id = 123
        new_start_time = "2025-01-16 17:00:00"
        new_end_time = "2025-01-16 18:00:00"

        result = alter_booking(booking_id, user_id, new_start_time, new_end_time)

        # Should return guidance message
        assert "修改功能暂不支持" in result
        assert "cancel_bookings" in result
        assert "recommend_available_rooms" in result
        assert "book_room" in result

    def test_recommend_available_rooms_default_parameters(self):
        """Test room recommendation with default parameters"""
        with patch("smartmeeting.agent.tools.DataManager") as mock_data_manager_class:
            mock_data_manager_class.return_value = self.mock_data_manager
            self.mock_data_manager.get_dataframe.side_effect = [
                pd.DataFrame(self.mock_rooms_data),
                pd.DataFrame([]),  # No existing meetings
            ]

            # Test with None values for optional parameters
            result = recommend_available_rooms(
                "2025-01-16 16:00:00",
                "2025-01-16 17:00:00",
                5,
                equipment_needs=None,
                preferred_location=None,
            )

            # Should work without errors
            assert isinstance(result, list)
