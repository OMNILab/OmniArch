"""
会议室日历页面模块
显示会议室预订情况的可视化日历
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar


class CalendarPage:
    """会议室日历页面实现"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def check_login(self):
        """检查用户登录状态"""
        if not self.auth_manager.is_authenticated():
            st.warning("⚠️ 请先登录以访问此页面")
            st.stop()

    def load_calendar_data(self):
        """加载日历数据"""
        try:
            # 获取当前月份的预订数据
            now = datetime.now()
            current_year = now.year
            current_month = now.month

            # 获取所有会议室和预订数据
            rooms_df = self.data_manager.get_dataframe("rooms")
            bookings_df = self.data_manager.get_dataframe("meetings")

            # 过滤当前月份的预订
            if not bookings_df.empty and "start_datetime" in bookings_df.columns:
                bookings_df["start_datetime"] = pd.to_datetime(
                    bookings_df["start_datetime"]
                )
                current_month_bookings = bookings_df[
                    (bookings_df["start_datetime"].dt.year == current_year)
                    & (bookings_df["start_datetime"].dt.month == current_month)
                ]
            else:
                current_month_bookings = pd.DataFrame()

            return rooms_df, current_month_bookings

        except Exception as e:
            st.error(f"❌ 加载数据失败: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def create_room_filter(self, all_rooms):
        """创建会议室筛选器"""
        # 创建房间显示名称列表
        room_options = []
        room_info_map = {}

        for _, room in all_rooms.iterrows():
            building_name = self._get_building_name(room.get("building_id", 1))
            room_display_name = f"{building_name}-{room.get('floor', '未知')}楼 {room.get('room_name', room.get('name', '未知'))}"
            room_options.append(room_display_name)
            room_info_map[room_display_name] = {
                "room_id": room.get("room_id", room.get("id")),
                "capacity": room.get("capacity", "未知"),
                "equipment": room.get("equipment_notes", room.get("equipment", "")),
                "building_name": building_name,
                "floor": room.get("floor", "未知"),
            }

        # 使用容器创建更好的布局
        with st.container():
            st.markdown("### 🔍 会议室筛选")

            # 创建两列布局
            col1, col2 = st.columns([1, 2])

            with col1:
                show_all = st.checkbox(
                    "📋 显示所有会议室", value=True, help="勾选后默认选择所有会议室"
                )

            with col2:
                if show_all:
                    selected_rooms = st.multiselect(
                        "选择要显示的会议室",
                        options=room_options,
                        default=room_options,
                        help="可以选择一个或多个会议室进行查看",
                        placeholder="请选择会议室...",
                    )
                else:
                    selected_rooms = st.multiselect(
                        "选择要显示的会议室",
                        options=room_options,
                        help="可以选择一个或多个会议室进行查看",
                        placeholder="请选择会议室...",
                    )

        # 转换为房间ID列表
        selected_room_ids = []
        room_name_map = {}

        for room_display_name in selected_rooms:
            if room_display_name in room_info_map:
                room_id = room_info_map[room_display_name]["room_id"]
                selected_room_ids.append(room_id)
                room_name_map[room_id] = room_display_name

        return selected_room_ids, room_name_map

    def _get_building_name(self, building_id):
        """获取建筑名称"""
        try:
            buildings_df = self.data_manager.get_dataframe("buildings")
            building = buildings_df[buildings_df["building_id"] == building_id]
            if not building.empty:
                return building.iloc[0].get("building_name", "未知建筑")
            return "未知建筑"
        except:
            return "未知建筑"

    def format_calendar_events(self, bookings, selected_room_ids, room_name_map):
        """将预订数据转换为日历事件格式"""
        calendar_events = []

        # 定义颜色列表，为不同房间分配不同颜色
        colors = [
            "#FF6B6B",  # 红色
            "#4ECDC4",  # 青色
            "#45B7D1",  # 蓝色
            "#96CEB4",  # 绿色
            "#FFEAA7",  # 黄色
            "#DDA0DD",  # 紫色
            "#98D8C8",  # 薄荷绿
            "#F7DC6F",  # 金色
        ]

        room_color_map = {}
        color_index = 0

        for _, booking in bookings.iterrows():
            room_id = booking.get("room_id")
            if room_id in selected_room_ids:
                # 为每个房间分配颜色
                if room_id not in room_color_map:
                    room_color_map[room_id] = colors[color_index % len(colors)]
                    color_index += 1

                room_name = room_name_map.get(room_id, f"房间{room_id}")
                title = booking.get("meeting_title", "未知会议")
                start_time = booking.get("start_datetime")
                end_time = booking.get("end_datetime")

                # 确保时间格式正确
                if pd.notna(start_time) and pd.notna(end_time):
                    event = {
                        "title": f"[{room_name}] {title}",
                        "start": (
                            start_time.isoformat()
                            if hasattr(start_time, "isoformat")
                            else str(start_time)
                        ),
                        "end": (
                            end_time.isoformat()
                            if hasattr(end_time, "isoformat")
                            else str(end_time)
                        ),
                        "backgroundColor": room_color_map[room_id],
                        "borderColor": room_color_map[room_id],
                        "textColor": "#FFFFFF",
                    }
                    calendar_events.append(event)

        return calendar_events

    def render_calendar(self, calendar_events):
        """渲染日历组件"""
        # 使用容器创建更好的布局
        with st.container():
            st.markdown("### 📅 会议室日历")

            # 添加日历说明
            if calendar_events:
                st.info(
                    f"📊 当前显示 {len(calendar_events)} 个预订事件，不同颜色代表不同会议室"
                )
            else:
                st.info("📝 当前时间段内暂无预订事件")

            # 日历选项配置
            calendar_options = {
                "editable": False,
                "selectable": True,
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay",
                },
                "initialView": "timeGridWeek",  # 默认周视图
                "height": 650,
                "slotMinTime": "08:00:00",
                "slotMaxTime": "20:00:00",
                "locale": "zh-cn",
                "timeZone": "Asia/Shanghai",
                "businessHours": {
                    "startTime": "09:00",
                    "endTime": "18:00",
                    "daysOfWeek": [1, 2, 3, 4, 5],  # 周一到周五
                },
            }

            # 渲染日历
            calendar_result = calendar(
                events=calendar_events,
                options=calendar_options,
                custom_css="""
                .fc-event-title {
                    font-weight: bold;
                }
                .fc-event-time {
                    font-style: italic;
                }
                .fc-event {
                    border-radius: 4px;
                    margin: 1px;
                }
                """,
            )

            # 显示点击事件信息（如果有）
            if calendar_result.get("eventClick"):
                event_data = calendar_result["eventClick"]["event"]
                st.success(f"📋 预订详情: {event_data.get('title', '未知')}")

    def render_statistics(self, bookings, selected_room_ids, room_name_map):
        """渲染统计信息"""
        # 过滤选中房间的预订
        filtered_bookings = bookings[bookings["room_id"].isin(selected_room_ids)]

        # 使用容器创建更好的布局
        with st.container():
            st.markdown("### 📊 统计概览")

            # 创建四列布局
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                self.ui.create_metric_card("📅 总预订数", str(len(filtered_bookings)))

            with col2:
                self.ui.create_metric_card("🏢 选中房间", str(len(selected_room_ids)))

            with col3:
                # 计算今天的预订
                today = datetime.now().date()
                if (
                    not filtered_bookings.empty
                    and "start_datetime" in filtered_bookings.columns
                ):
                    today_bookings = filtered_bookings[
                        filtered_bookings["start_datetime"].dt.date == today
                    ]
                    self.ui.create_metric_card("📋 今日预订", str(len(today_bookings)))
                else:
                    self.ui.create_metric_card("📋 今日预订", "0")

            with col4:
                # 计算本周的预订
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                if (
                    not filtered_bookings.empty
                    and "start_datetime" in filtered_bookings.columns
                ):
                    week_bookings = filtered_bookings[
                        (filtered_bookings["start_datetime"].dt.date >= week_start)
                        & (filtered_bookings["start_datetime"].dt.date <= week_end)
                    ]
                    self.ui.create_metric_card("📈 本周预订", str(len(week_bookings)))
                else:
                    self.ui.create_metric_card("📈 本周预订", "0")

    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            # 日历信息
            st.markdown("### 📅 日历说明")
            st.markdown(
                """
            **🎨 颜色说明**  
            不同颜色代表不同会议室的预订
            
            **📊 视图切换**  
            支持月视图、周视图、日视图
            
            **🔍 筛选功能**  
            可选择显示特定会议室
            """
            )

            st.markdown("### 💡 使用技巧")
            st.markdown(
                """
            **📱 操作指南**
            - 点击事件查看详情
            - 拖拽切换视图
            - 筛选特定会议室
            
            **🎯 快速操作**
            - 使用筛选器快速定位
            - 切换视图查看不同时间范围
            - 点击今日按钮回到当前时间
            """
            )

    def show(self):
        """显示会议室日历页面"""
        self.ui.create_header("🗓️ 会议室日历")

        # 检查登录状态
        self.check_login()

        # 渲染侧边栏
        self.render_sidebar()

        # 加载数据
        with st.spinner("📊 正在加载数据..."):
            all_rooms, all_bookings = self.load_calendar_data()

        if all_rooms.empty:
            st.warning("⚠️ 未找到会议室数据")
            return

        # 创建筛选器
        selected_room_ids, room_name_map = self.create_room_filter(all_rooms)

        if not selected_room_ids:
            st.info("📝 请选择至少一个会议室来查看日历")
            return

        # 渲染统计信息（移到顶部）
        self.render_statistics(all_bookings, selected_room_ids, room_name_map)

        st.markdown("---")

        # 格式化日历事件
        calendar_events = self.format_calendar_events(
            all_bookings, selected_room_ids, room_name_map
        )

        # 渲染日历
        self.render_calendar(calendar_events)

        st.markdown("---")

        # 显示房间列表
        st.markdown("### 🏢 会议室详情")

        # 使用网格布局显示会议室信息
        cols = st.columns(3)
        for idx, room_id in enumerate(selected_room_ids):
            room = all_rooms[all_rooms["room_id"] == room_id]
            if not room.empty:
                room = room.iloc[0]
                col_idx = idx % 3

                with cols[col_idx]:
                    # 创建会议室卡片
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="background: white; 
                                        padding: 1.5rem; 
                                        border-radius: 12px; 
                                        border: 1px solid #e5e7eb; 
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                        margin-bottom: 1rem;">
                                <h4 style="color: #1f2937; margin-bottom: 0.5rem;">
                                    {room.get('room_name', room.get('name', '未知'))}
                                </h4>
                                <div style="color: #6b7280; font-size: 0.9rem; line-height: 1.4;">
                                    <div style="margin-bottom: 0.3rem;">
                                        📍 {self._get_building_name(room.get("building_id", 1))}-{room.get('floor', '未知')}楼
                                    </div>
                                    <div style="margin-bottom: 0.3rem;">
                                        👥 容量: {room.get('capacity', '未知')}人
                                    </div>
                                    <div>
                                        🔧 {room.get('equipment_notes', room.get('equipment', '无特殊设备'))}
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
