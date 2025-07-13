"""
Booking Page Module
Contains the booking page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


class BookingPage:
    """Smart booking page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """Smart booking page implementation with enhanced functionality"""
        self.ui.create_header("智能预定")

        # Enhanced booking statistics
        col1, col2, col3, col4 = st.columns(4)

        dashboard_data = self.data_manager.get_dashboard_data()

        with col1:
            self.ui.create_metric_card(
                "今日会议", str(dashboard_data["meetings_today"])
            )

        with col2:
            self.ui.create_metric_card(
                "可用会议室", str(dashboard_data["available_rooms"])
            )

        with col3:
            self.ui.create_metric_card(
                "总会议数", str(dashboard_data["total_meetings"])
            )

        with col4:
            self.ui.create_metric_card(
                "平均时长", f"{dashboard_data['avg_meeting_duration']:.0f}分钟"
            )

        # Room recommendations with real data
        st.markdown("---")
        st.markdown("### 会议室推荐")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### 会议日历")

            # Generate real calendar data from meetings
            meetings_df = self.data_manager.get_dataframe("meetings")
            rooms_df = self.data_manager.get_dataframe("rooms")

            # Create calendar view for today
            today = datetime.now().date()
            today_meetings = meetings_df[
                pd.to_datetime(meetings_df["start_time"]).dt.date == today
            ]

            if len(today_meetings) > 0:
                calendar_data = []
                time_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

                for time_slot in time_slots:
                    row = {"时间": time_slot}
                    for _, room in rooms_df.head(3).iterrows():
                        # Check if room is booked at this time
                        slot_time = datetime.strptime(
                            f"{today} {time_slot}", "%Y-%m-%d %H:%M"
                        )
                        room_meetings = today_meetings[
                            today_meetings["room_id"] == room["id"]
                        ]

                        is_booked = False
                        for _, meeting in room_meetings.iterrows():
                            meeting_start = pd.to_datetime(meeting["start_time"])
                            meeting_end = pd.to_datetime(meeting["end_time"])
                            if meeting_start <= slot_time < meeting_end:
                                is_booked = True
                                break

                        row[room["name"]] = "已预订" if is_booked else "可用"

                    calendar_data.append(row)

                calendar_df = pd.DataFrame(calendar_data)
                st.dataframe(calendar_df, use_container_width=True)
            else:
                st.info("今日暂无会议安排")

        with col2:
            st.markdown("#### 推荐会议室")

            # Room recommendations based on availability
            available_rooms = rooms_df[rooms_df["status"] == "可用"].head(3)

            for _, room in available_rooms.iterrows():
                self.ui.create_room_card(room.to_dict())

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"预定 {room['name']}", key=f"book_{room['id']}"):
                        st.session_state.booking_form_data["selected_room"] = room[
                            "name"
                        ]
                        st.success(f"已选择 {room['name']}")
                with col2:
                    if st.button(f"详情", key=f"details_{room['id']}"):
                        st.info(
                            f"会议室详情: {room['name']} - 容量{room['capacity']}人 - 设备: {room['equipment']}"
                        )

        # Enhanced booking form with session state
        st.markdown("---")
        st.markdown("### 预定确认")

        with st.form("booking_form"):
            col1, col2 = st.columns(2)

            with col1:
                meeting_title = st.text_input(
                    "会议主题",
                    placeholder="请输入会议主题",
                    value=st.session_state.booking_form_data.get("title", ""),
                )
                meeting_date = st.date_input(
                    "会议日期",
                    value=st.session_state.booking_form_data.get(
                        "date", datetime.now().date()
                    ),
                )
                meeting_time = st.time_input(
                    "会议时间",
                    value=st.session_state.booking_form_data.get(
                        "time", datetime.now().time()
                    ),
                )

            with col2:
                participants = st.number_input(
                    "参与人数",
                    min_value=1,
                    max_value=50,
                    value=st.session_state.booking_form_data.get("participants", 10),
                )
                room_selection = st.selectbox(
                    "选择会议室",
                    rooms_df["name"].tolist(),
                    index=(
                        rooms_df["name"]
                        .tolist()
                        .index(
                            st.session_state.booking_form_data.get(
                                "selected_room", rooms_df["name"].iloc[0]
                            )
                        )
                        if st.session_state.booking_form_data.get("selected_room")
                        in rooms_df["name"].tolist()
                        else 0
                    ),
                )
                meeting_type = st.selectbox(
                    "会议类型",
                    ["项目讨论", "产品评审", "技术分享", "团队会议", "客户会议"],
                    index=[
                        "项目讨论",
                        "产品评审",
                        "技术分享",
                        "团队会议",
                        "客户会议",
                    ].index(st.session_state.booking_form_data.get("type", "项目讨论")),
                )

            meeting_description = st.text_area(
                "会议描述",
                placeholder="请输入会议描述",
                value=st.session_state.booking_form_data.get("description", ""),
            )

            col1, col2, col3 = st.columns(3)
            with col2:
                if st.form_submit_button("确认预定", type="primary"):
                    if meeting_title and room_selection:
                        # Create new meeting
                        selected_room = rooms_df[
                            rooms_df["name"] == room_selection
                        ].iloc[0]

                        new_meeting = {
                            "title": meeting_title,
                            "room_id": selected_room["id"],
                            "organizer_id": self.auth_manager.get_user_id(),
                            "start_time": datetime.combine(meeting_date, meeting_time),
                            "end_time": datetime.combine(meeting_date, meeting_time)
                            + timedelta(hours=1),
                            "duration": 60,
                            "participants": participants,
                            "type": meeting_type,
                            "status": "已确认",
                            "description": meeting_description,
                        }

                        self.data_manager.add_meeting(new_meeting)
                        st.success("预定成功！")

                        # Clear form data
                        st.session_state.booking_form_data = {}
                        st.rerun()
                    else:
                        st.error("请填写完整信息")

        # Recent bookings
        st.markdown("---")
        st.markdown("### 我的预定")

        current_user_meetings = self.data_manager.get_dataframe("meetings")
        current_user_meetings = current_user_meetings[
            current_user_meetings["organizer_id"] == self.auth_manager.get_user_id()
        ].tail(5)

        if len(current_user_meetings) > 0:
            for _, meeting in current_user_meetings.iterrows():
                with st.expander(f"{meeting['title']} - {meeting['start_time']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**状态：** {meeting['status']}")
                        st.write(f"**类型：** {meeting['type']}")
                    with col2:
                        st.write(f"**参与人数：** {meeting['participants']}")
                        st.write(f"**时长：** {meeting['duration']}分钟")
                    with col3:
                        if st.button("取消预定", key=f"cancel_{meeting['id']}"):
                            self.data_manager.update_meeting_status(
                                meeting["id"], "已取消"
                            )
                            st.success("预定已取消")
                            st.rerun()
        else:
            st.info("暂无预定记录")