"""
AI Booking Page Module
Contains the AI-powered booking page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import uuid
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from smartmeeting.agent import create_graph
from smartmeeting.data_manager import DataManager


class BookingPage:
    """AI-powered booking page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def check_login(self):
        """检查用户登录状态"""
        if not self.auth_manager.is_authenticated():
            st.warning("⚠️ 请先登录以访问此页面")
            st.stop()

    def initialize_graph(self):
        """初始化或获取缓存的图实例"""
        if "graph" not in st.session_state:
            try:
                # 使用内存存储器以在页面刷新间保持状态
                memory = InMemorySaver()
                st.session_state.graph = create_graph(checkpointer=memory)
                st.success("✅ AI助手已就绪")
            except Exception as e:
                st.error(f"❌ 初始化AI助手失败: {e}")
                st.stop()

        if "thread_id" not in st.session_state:
            st.session_state.thread_id = str(uuid.uuid4())

    def get_config(self):
        """获取图配置"""
        return {"configurable": {"thread_id": st.session_state.thread_id}}

    def render_message(self, message):
        """渲染单条消息"""
        if isinstance(message, HumanMessage):
            with st.chat_message("human"):
                st.markdown(message.content)

        elif isinstance(message, AIMessage):
            # 跳过包含tool_calls的AIMessage，因为它们会被st.status显示
            if not message.tool_calls:
                with st.chat_message("assistant"):
                    st.markdown(message.content)

    def render_message_history(self):
        """渲染历史消息"""
        graph = st.session_state.graph
        config = self.get_config()

        try:
            current_state = graph.get_state(config)
            messages = current_state.values.get("messages", [])

            for message in messages:
                self.render_message(message)

        except Exception as e:
            st.error(f"❌ 获取消息历史失败: {e}")

    def render_hitl_confirmation(self):
        """渲染人工介入确认卡片"""
        graph = st.session_state.graph
        config = self.get_config()

        try:
            current_state = graph.get_state(config)

            # 优先检测 action_request（LangGraph中断机制）
            action_req = current_state.values.get("action_request")
            if action_req:
                tool_name = action_req.get("action")
                tool_args = action_req.get("args", {})
                confirmation_container = st.container()
                with confirmation_container:
                    with st.status(
                        f"⚠️ 需要确认: {tool_name}",
                        state="running",
                        expanded=True,
                    ):
                        st.markdown("### 🛠️ 待执行操作")
                        if tool_name == "book_room":
                            self.render_booking_confirmation(tool_args)
                        elif tool_name == "cancel_bookings":
                            self.render_cancellation_confirmation(tool_args)
                        elif tool_name == "alter_booking":
                            self.render_alteration_confirmation(tool_args)
                        else:
                            st.json(tool_args)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(
                                "✅ 批准执行",
                                use_container_width=True,
                                type="primary",
                                key="approve_action_actionreq",
                            ):
                                self.execute_tool_action(graph, config, "accept")
                        with col2:
                            if st.button(
                                "❌ 拒绝操作",
                                use_container_width=True,
                                key="reject_action_actionreq",
                            ):
                                self.execute_tool_action(graph, config, "ignore")
                return  # 已渲染，无需继续

            # 检测 interrupts 字段
            interrupts = current_state.values.get("interrupts")
            if interrupts:
                # 处理中断逻辑
                for interrupt in interrupts:
                    if interrupt.get("type") == "tool_call":
                        tool_name = interrupt.get("tool_name")
                        tool_args = interrupt.get("tool_args", {})
                        confirmation_container = st.container()
                        with confirmation_container:
                            with st.status(
                                f"⚠️ 需要确认: {tool_name}",
                                state="running",
                                expanded=True,
                            ):
                                st.markdown("### 🛠️ 待执行操作")
                                if tool_name == "book_room":
                                    self.render_booking_confirmation(tool_args)
                                elif tool_name == "cancel_bookings":
                                    self.render_cancellation_confirmation(tool_args)
                                elif tool_name == "alter_booking":
                                    self.render_alteration_confirmation(tool_args)
                                else:
                                    st.json(tool_args)
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(
                                        "✅ 批准执行",
                                        use_container_width=True,
                                        type="primary",
                                        key="approve_action_interrupt",
                                    ):
                                        self.execute_tool_action(
                                            graph, config, "accept"
                                        )
                                with col2:
                                    if st.button(
                                        "❌ 拒绝操作",
                                        use_container_width=True,
                                        key="reject_action_interrupt",
                                    ):
                                        self.execute_tool_action(
                                            graph, config, "ignore"
                                        )
                        return True  # 已渲染，无需继续

            # 检测最新的确认消息
            messages = current_state.values.get("messages", [])
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, AIMessage) and last_message.content:
                    # 检查是否包含确认提示的关键词
                    confirmation_keywords = [
                        "请确认以上信息是否正确",
                        "请确认以上信息",
                        "请确认",
                        "确认无误",
                        "我将再次确认",
                        "请确认您的需求",
                    ]

                    if any(
                        keyword in last_message.content
                        for keyword in confirmation_keywords
                    ):
                        # 从消息内容中提取预订信息
                        booking_info = self.extract_booking_info_from_message(
                            last_message.content
                        )
                        if booking_info:
                            confirmation_container = st.container()
                            with confirmation_container:
                                with st.status(
                                    "⚠️ 需要确认: 会议室预订",
                                    state="running",
                                    expanded=True,
                                ):
                                    st.markdown("### 🛠️ 待执行操作")
                                    self.render_booking_confirmation_from_text(
                                        booking_info
                                    )
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button(
                                            "✅ 确认预订",
                                            use_container_width=True,
                                            type="primary",
                                            key="approve_booking_text",
                                        ):
                                            self.execute_booking_confirmation(
                                                graph, config, booking_info
                                            )
                                    with col2:
                                        if st.button(
                                            "❌ 取消预订",
                                            use_container_width=True,
                                            key="reject_booking_text",
                                        ):
                                            self.execute_booking_cancellation(
                                                graph, config
                                            )
                            return  # 已渲染，无需继续

            # 兼容原有tool_calls逻辑
            if current_state.next and len(current_state.next) > 0:
                messages = current_state.values.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        tool_call = last_message.tool_calls[0]
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        confirmation_container = st.container()
                        with confirmation_container:
                            with st.status(
                                f"⚠️ 需要确认: {tool_name}",
                                state="running",
                                expanded=True,
                            ):
                                st.markdown("### 🛠️ 待执行操作")
                                if tool_name == "book_room":
                                    self.render_booking_confirmation(tool_args)
                                elif tool_name == "cancel_bookings":
                                    self.render_cancellation_confirmation(tool_args)
                                elif tool_name == "alter_booking":
                                    self.render_alteration_confirmation(tool_args)
                                else:
                                    st.json(tool_args)
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(
                                        "✅ 批准执行",
                                        use_container_width=True,
                                        type="primary",
                                        key="approve_action_toolcall",
                                    ):
                                        self.execute_tool_action(
                                            graph, config, "accept"
                                        )
                                with col2:
                                    if st.button(
                                        "❌ 拒绝操作",
                                        use_container_width=True,
                                        key="reject_action_toolcall",
                                    ):
                                        self.execute_tool_action(
                                            graph, config, "ignore"
                                        )
                        return  # 已渲染，无需继续

                        # 检查最新消息是否有待处理的tool_calls（即使没有next状态）
            messages = current_state.values.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    tool_call = last_message.tool_calls[0]
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    confirmation_container = st.container()
                    with confirmation_container:
                        with st.status(
                            f"⚠️ 需要确认: {tool_name}",
                            state="running",
                            expanded=True,
                        ):
                            st.markdown("### 🛠️ 待执行操作")
                            if tool_name == "book_room":
                                self.render_booking_confirmation(tool_args)
                            elif tool_name == "cancel_bookings":
                                self.render_cancellation_confirmation(tool_args)
                            elif tool_name == "alter_booking":
                                self.render_alteration_confirmation(tool_args)
                            else:
                                st.json(tool_args)
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(
                                    "✅ 批准执行",
                                    use_container_width=True,
                                    type="primary",
                                    key="approve_action_toolcall_no_next",
                                ):
                                    self.execute_tool_action(graph, config, "accept")
                            with col2:
                                if st.button(
                                    "❌ 拒绝操作",
                                    use_container_width=True,
                                    key="reject_action_toolcall_no_next",
                                ):
                                    self.execute_tool_action(graph, config, "ignore")
                    return True  # 已渲染，无需继续

            # 最终检查：遍历所有消息查找待处理的tool_calls
            messages = current_state.values.get("messages", [])
            for i, message in enumerate(reversed(messages)):  # 从最新消息开始检查
                if hasattr(message, "tool_calls") and message.tool_calls:
                    tool_call = message.tool_calls[0]
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    confirmation_container = st.container()
                    with confirmation_container:
                        with st.status(
                            f"⚠️ 需要确认: {tool_name}",
                            state="running",
                            expanded=True,
                        ):
                            st.markdown("### 🛠️ 待执行操作")
                            if tool_name == "book_room":
                                self.render_booking_confirmation(tool_args)
                            elif tool_name == "cancel_bookings":
                                self.render_cancellation_confirmation(tool_args)
                            elif tool_name == "alter_booking":
                                self.render_alteration_confirmation(tool_args)
                            else:
                                st.json(tool_args)
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(
                                    "✅ 批准执行",
                                    use_container_width=True,
                                    type="primary",
                                    key=f"approve_action_toolcall_msg_{i}",
                                ):
                                    self.execute_tool_action(graph, config, "accept")
                            with col2:
                                if st.button(
                                    "❌ 拒绝操作",
                                    use_container_width=True,
                                    key=f"reject_action_toolcall_msg_{i}",
                                ):
                                    self.execute_tool_action(graph, config, "ignore")
                    return True  # 已渲染，无需继续

            return False
        except Exception as e:
            st.error(f"❌ 检查中断状态失败: {e}")
            st.write(f"异常详情: {str(e)}")
            return False

    def execute_tool_action(self, graph, config, action_type):
        """执行工具操作"""
        streaming_container = st.empty()

        with streaming_container.container():
            st.markdown(
                "### 🔄 执行过程" if action_type == "accept" else "### 🚫 取消过程"
            )
            progress_placeholder = st.empty()
            response_placeholder = st.empty()

            try:
                final_response = ""
                processing_nodes = set()  # 跟踪正在处理的节点

                # 使用正确的streaming方式
                for chunk in graph.stream(
                    Command(resume=[{"type": action_type}]),
                    config,
                    stream_mode="updates",
                ):
                    # chunk的格式是 {node_name: node_data}
                    for node_name, node_data in chunk.items():
                        # 只在节点开始处理时显示进度，避免重复
                        if node_name not in processing_nodes:
                            processing_nodes.add(node_name)
                            progress_placeholder.markdown(
                                f"📍 **{node_name}**: 处理中..."
                            )

                        # 如果node_data包含messages，提取AI响应
                        if isinstance(node_data, dict) and "messages" in node_data:
                            messages = node_data["messages"]
                            if messages:
                                for message in messages:
                                    if (
                                        isinstance(message, AIMessage)
                                        and message.content
                                    ):
                                        final_response = message.content
                                        # 清除进度显示，显示最终响应
                                        progress_placeholder.empty()
                                        response_placeholder.markdown(
                                            f"**🤖 AI响应**:\n{final_response}"
                                        )

                if action_type == "accept":
                    st.success("✅ 操作已完成")
                else:
                    st.warning("🚫 操作已取消")
                st.rerun()

            except Exception as e:
                st.error(f"❌ 执行失败: {e}")

    def render_booking_confirmation(self, tool_args):
        """渲染预订确认详情"""
        st.markdown("**📅 会议室预订**")

        # 获取房间详情
        room_id = tool_args.get("room_id")
        if room_id:
            rooms_df = self.data_manager.get_dataframe("rooms")
            room = rooms_df[rooms_df["id"] == room_id]
            if not room.empty:
                room = room.iloc[0]
                st.markdown(
                    f"🏢 **会议室**: {room['name']} ({room.get('building', '未知')}-{room.get('floor', '未知')}楼)"
                )
                st.markdown(f"👥 **容量**: {room['capacity']}人")
                if room.get("equipment"):
                    st.markdown(f"🔧 **设备**: {room['equipment']}")
            else:
                st.markdown(f"🏢 **会议室ID**: {room_id}")

        # 其他预订信息
        if "start_time" in tool_args:
            st.markdown(f"⏰ **开始时间**: {tool_args['start_time']}")
        if "end_time" in tool_args:
            st.markdown(f"⏰ **结束时间**: {tool_args['end_time']}")
        if "title" in tool_args:
            st.markdown(f"📝 **会议标题**: {tool_args['title']}")

    def render_cancellation_confirmation(self, tool_args):
        """渲染取消确认详情"""
        st.markdown("**🗑️ 取消预订**")

        if "booking_ids" in tool_args:
            booking_ids = tool_args["booking_ids"]
            if isinstance(booking_ids, list):
                st.markdown(
                    f"📋 **待取消的预订ID**: {', '.join(map(str, booking_ids))}"
                )
            else:
                st.markdown(f"📋 **待取消的预订ID**: {booking_ids}")

        st.warning("⚠️ 此操作不可撤销")

    def render_alteration_confirmation(self, tool_args):
        """渲染修改确认详情"""
        st.markdown("**✏️ 修改预订**")

        if "booking_id" in tool_args:
            st.markdown(f"📋 **预订ID**: {tool_args['booking_id']}")

        st.markdown("**📝 修改内容**:")
        for key, value in tool_args.items():
            if key != "booking_id" and value is not None:
                if key == "new_room_id":
                    st.markdown(f"- **新会议室ID**: {value}")
                elif key == "new_start_time":
                    st.markdown(f"- **新开始时间**: {value}")
                elif key == "new_end_time":
                    st.markdown(f"- **新结束时间**: {value}")

    def extract_booking_info_from_message(self, message_content):
        """从确认消息中提取预订信息"""
        import re

        booking_info = {}

        # 提取会议室名称
        room_match = re.search(r"会议室[：:]\s*([^\n]+)", message_content)
        if room_match:
            booking_info["room_name"] = room_match.group(1).strip()

        # 提取时间段
        time_match = re.search(r"时间段[：:]\s*([^\n]+)", message_content)
        if time_match:
            booking_info["time_range"] = time_match.group(1).strip()

        # 提取会议主题
        title_match = re.search(r"会议主题[：:]\s*([^\n]+)", message_content)
        if title_match:
            booking_info["title"] = title_match.group(1).strip()

        # 如果没有找到标准格式，尝试其他模式
        if not booking_info.get("room_name"):
            # 尝试匹配 "C102会议室" 这样的格式
            room_match = re.search(r"([A-Z]\d+会议室)", message_content)
            if room_match:
                booking_info["room_name"] = room_match.group(1)

        if not booking_info.get("time_range"):
            # 尝试匹配日期时间格式
            time_match = re.search(
                r"(\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}\s*-\s*\d{2}:\d{2})",
                message_content,
            )
            if time_match:
                booking_info["time_range"] = time_match.group(1)

        if not booking_info.get("title"):
            # 尝试匹配会议主题
            title_match = re.search(r"主题[：:]\s*([^\n]+)", message_content)
            if title_match:
                booking_info["title"] = title_match.group(1).strip()

        return booking_info if booking_info else None

    def render_booking_confirmation_from_text(self, booking_info):
        """从文本信息渲染预订确认详情"""
        st.markdown("**📅 会议室预订**")

        if booking_info.get("room_name"):
            st.markdown(f"🏢 **会议室**: {booking_info['room_name']}")

        if booking_info.get("time_range"):
            st.markdown(f"⏰ **时间段**: {booking_info['time_range']}")

        if booking_info.get("title"):
            st.markdown(f"📝 **会议主题**: {booking_info['title']}")

    def execute_booking_confirmation(self, graph, config, booking_info):
        """执行预订确认"""
        # 根据提取的信息构造预订参数
        room_name = booking_info.get("room_name", "")

        # 从房间名称获取房间ID
        rooms_df = self.data_manager.get_dataframe("rooms")
        room = rooms_df[rooms_df["name"] == room_name]

        if room.empty:
            st.error(f"❌ 未找到会议室: {room_name}")
            return

        room_id = room.iloc[0]["id"]

        # 解析时间范围
        time_range = booking_info.get("time_range", "")
        start_time, end_time = self.parse_time_range(time_range)

        # 构造预订参数
        booking_args = {
            "room_id": room_id,
            "user_id": 1,  # 默认用户ID
            "start_time": start_time,
            "end_time": end_time,
            "title": booking_info.get("title", "会议"),
        }

        # 执行预订
        try:
            # 直接调用数据管理器进行预订
            result = self.data_manager.book_room(**booking_args)
            if result:
                st.success("✅ 预订成功！")
                st.rerun()
            else:
                st.error("❌ 预订失败")
        except Exception as e:
            st.error(f"❌ 预订失败: {e}")

    def execute_booking_cancellation(self, graph, config):
        """执行预订取消"""
        st.info("🚫 预订已取消")
        st.rerun()

    def parse_time_range(self, time_range):
        """解析时间范围字符串"""
        import re
        from datetime import datetime

        # 匹配 "2025年07月17日 11:00 - 12:00" 格式
        pattern = r"(\d{4})年(\d{2})月(\d{2})日\s+(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})"
        match = re.search(pattern, time_range)

        if match:
            year, month, day, start_hour, start_min, end_hour, end_min = match.groups()
            start_time = f"{year}-{month}-{day} {start_hour}:{start_min}:00"
            end_time = f"{year}-{month}-{day} {end_hour}:{end_min}:00"
            return start_time, end_time

        # 如果解析失败，返回默认值
        return "2025-07-17 11:00:00", "2025-07-17 12:00:00"

    def handle_user_input(self):
        """处理用户输入"""
        if prompt := st.chat_input("请输入您的需求..."):
            # 添加用户消息到聊天
            with st.chat_message("human"):
                st.markdown(prompt)

            # 获取图实例和配置
            graph = st.session_state.graph
            config = self.get_config()

            # 设置用户信息
            current_user = self.auth_manager.get_current_user()
            user_id = current_user.get("id", 1) if current_user else 1
            username = current_user.get("name", "用户") if current_user else "用户"

            # 创建streaming展示容器
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                progress_placeholder = st.empty()

                try:
                    final_response = ""
                    processing_nodes = set()  # 跟踪正在处理的节点

                    # 使用streaming方式处理用户输入
                    for chunk in graph.stream(
                        {"messages": [HumanMessage(content=prompt)]},
                        config,
                        stream_mode="updates",
                    ):
                        # chunk的格式是 {node_name: node_data}
                        for node_name, node_data in chunk.items():
                            # 只在节点开始处理时显示进度，避免重复
                            if node_name not in processing_nodes:
                                processing_nodes.add(node_name)
                                progress_placeholder.markdown(
                                    f"📍 **{node_name}**: 处理中..."
                                )

                            # 如果node_data包含messages，提取AI响应
                            if isinstance(node_data, dict) and "messages" in node_data:
                                messages = node_data["messages"]
                                if messages:
                                    for message in messages:
                                        if (
                                            isinstance(message, AIMessage)
                                            and message.content
                                        ):
                                            final_response = message.content
                                            # 清除进度显示，显示最终响应
                                            progress_placeholder.empty()
                                            message_placeholder.markdown(final_response)

                    # 最终显示
                    if final_response:
                        message_placeholder.markdown(final_response)
                    else:
                        # 如果没有最终响应，清除进度显示
                        progress_placeholder.empty()

                except Exception as e:
                    st.error(f"❌ 处理失败: {e}")

    def show(self):
        """AI-powered booking page implementation"""
        self.ui.create_header("🤖 AI会议预订助手")

        # 检查登录状态
        self.check_login()

        # 初始化图
        self.initialize_graph()

        # 渲染人工介入确认 - 优先检查并显示
        confirmation_shown = self.render_hitl_confirmation()

        # 渲染历史消息
        self.render_message_history()

        # 处理用户输入
        self.handle_user_input()

        # 侧边栏功能说明
        st.sidebar.markdown("### 🛠️ 功能说明")
        st.sidebar.markdown(
            """
        **安全工具** (无需确认):
        - 🔍 查找可用会议室
        - 📋 查看我的预订
        
        **危险工具** (需要确认):
        - 📅 预订会议室
        - ❌ 取消预订
        - ✏️ 修改预订
        """
        )

        if st.sidebar.button("🔄 重置对话"):
            if "graph" in st.session_state:
                del st.session_state.graph
            if "thread_id" in st.session_state:
                del st.session_state.thread_id
            st.rerun()
