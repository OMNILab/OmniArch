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

        # 初始化用户信息到session state
        if "user_id" not in st.session_state or "username" not in st.session_state:
            current_user = self.auth_manager.get_current_user()
            if current_user:
                st.session_state.user_id = current_user.get("id", 1)
                st.session_state.username = current_user.get("name", "用户")
            else:
                st.session_state.user_id = 1
                st.session_state.username = "用户"

        # 初始化工具状态容器
        if "tool_status_containers" not in st.session_state:
            st.session_state.tool_status_containers = {}

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

            # 检查是否有中断
            if current_state.next and len(current_state.next) > 0:
                messages = current_state.values.get("messages", [])
                if messages:
                    last_message = messages[-1]

                    if isinstance(last_message, AIMessage) and last_message.tool_calls:
                        tool_call = last_message.tool_calls[0]
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        # 创建确认卡片
                        with st.status(
                            f"⚠️ 需要确认: {tool_name}", state="running", expanded=True
                        ):
                            st.markdown("### 🛠️ 待执行操作")

                            # 根据不同工具显示不同的详情
                            if tool_name == "book_room":
                                self.render_booking_confirmation(tool_args)
                            elif tool_name == "cancel_bookings":
                                self.render_cancellation_confirmation(tool_args)
                            elif tool_name == "alter_booking":
                                self.render_alteration_confirmation(tool_args)
                            else:
                                st.json(tool_args)

                            # 确认按钮
                            col1, col2 = st.columns(2)

                            with col1:
                                if st.button(
                                    "✅ 批准执行",
                                    use_container_width=True,
                                    type="primary",
                                ):
                                    # 创建streaming展示容器
                                    streaming_container = st.empty()

                                    with streaming_container.container():
                                        st.markdown("### 🔄 执行过程")
                                        progress_placeholder = st.empty()
                                        response_placeholder = st.empty()

                                        try:
                                            progress_text = ""
                                            final_response = ""

                                            # 使用正确的streaming方式 - 修复：resume应该接受列表
                                            for chunk in graph.stream(
                                                Command(resume=[{"type": "accept"}]),
                                                config,
                                                stream_mode="updates",
                                            ):
                                                # chunk的格式是 {node_name: node_data}
                                                for (
                                                    node_name,
                                                    node_data,
                                                ) in chunk.items():
                                                    progress_text += f"📍 **{node_name}**: 处理中...\n"
                                                    progress_placeholder.markdown(
                                                        progress_text
                                                    )

                                                    # 如果node_data包含messages，提取AI响应
                                                    if (
                                                        isinstance(node_data, dict)
                                                        and "messages" in node_data
                                                    ):
                                                        messages = node_data["messages"]
                                                        if messages:
                                                            for message in messages:
                                                                if (
                                                                    isinstance(
                                                                        message,
                                                                        AIMessage,
                                                                    )
                                                                    and message.content
                                                                ):
                                                                    final_response = (
                                                                        message.content
                                                                    )
                                                                    response_placeholder.markdown(
                                                                        f"**🤖 AI响应**:\n{final_response}"
                                                                    )

                                            st.success("✅ 操作已完成")
                                            st.rerun()

                                        except Exception as e:
                                            st.error(f"❌ 执行失败: {e}")

                            with col2:
                                if st.button("❌ 拒绝操作", use_container_width=True):
                                    # 创建streaming展示容器
                                    streaming_container = st.empty()

                                    with streaming_container.container():
                                        st.markdown("### 🚫 取消过程")
                                        progress_placeholder = st.empty()
                                        response_placeholder = st.empty()

                                        try:
                                            progress_text = ""
                                            final_response = ""

                                            # 使用正确的streaming方式 - 修复：resume应该接受列表
                                            for chunk in graph.stream(
                                                Command(resume=[{"type": "ignore"}]),
                                                config,
                                                stream_mode="updates",
                                            ):
                                                # chunk的格式是 {node_name: node_data}
                                                for (
                                                    node_name,
                                                    node_data,
                                                ) in chunk.items():
                                                    progress_text += f"📍 **{node_name}**: 处理中...\n"
                                                    progress_placeholder.markdown(
                                                        progress_text
                                                    )

                                                    # 如果node_data包含messages，提取AI响应
                                                    if (
                                                        isinstance(node_data, dict)
                                                        and "messages" in node_data
                                                    ):
                                                        messages = node_data["messages"]
                                                        if messages:
                                                            for message in messages:
                                                                if (
                                                                    isinstance(
                                                                        message,
                                                                        AIMessage,
                                                                    )
                                                                    and message.content
                                                                ):
                                                                    final_response = (
                                                                        message.content
                                                                    )
                                                                    response_placeholder.markdown(
                                                                        f"**🤖 AI响应**:\n{final_response}"
                                                                    )

                                            st.warning("🚫 操作已取消")
                                            st.rerun()

                                        except Exception as e:
                                            st.error(f"❌ 取消失败: {e}")

        except Exception as e:
            st.error(f"❌ 检查中断状态失败: {e}")

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

    def process_stream_events(self, events):
        """处理流式事件"""
        ai_placeholder = st.empty()
        full_response = ""

        for chunk in events:
            # LangGraph流式 输出格式是 {node_name: node_data}
            for node_name, node_data in chunk.items():
                if isinstance(node_data, dict) and "messages" in node_data:
                    messages = node_data["messages"]
                    for message in messages:
                        if isinstance(message, AIMessage):
                            if message.tool_calls:
                                # 为工具调用创建状态容器
                                for tool_call in message.tool_calls:
                                    tool_call_id = tool_call["id"]
                                    tool_name = tool_call["name"]

                                    if (
                                        tool_call_id
                                        not in st.session_state.tool_status_containers
                                    ):
                                        status_container = st.status(
                                            f"🔧 执行工具: {tool_name}",
                                            state="running",
                                            expanded=True,
                                        )
                                        st.session_state.tool_status_containers[
                                            tool_call_id
                                        ] = status_container

                                        with status_container:
                                            st.json(tool_call["args"])
                            else:
                                # 累积AI回复文本
                                full_response += message.content
                                ai_placeholder.markdown(full_response + "▌")

                        elif isinstance(message, ToolMessage):
                            tool_call_id = message.tool_call_id
                            if tool_call_id in st.session_state.tool_status_containers:
                                status_container = (
                                    st.session_state.tool_status_containers[
                                        tool_call_id
                                    ]
                                )
                                status_container.update(state="complete")

                                with status_container:
                                    st.success("✅ 工具执行完成")
                                    if message.content:
                                        st.text(message.content)

        # 显示最终回复
        if full_response:
            ai_placeholder.markdown(full_response)

        # 清空工具状态容器
        st.session_state.tool_status_containers = {}

    def handle_user_input(self):
        """处理用户输入"""
        if user_input := st.chat_input("请输入您的需求..."):
            # 立即显示用户消息
            with st.chat_message("human"):
                st.markdown(user_input)

            # 处理AI回复
            with st.chat_message("assistant"):
                graph = st.session_state.graph
                config = self.get_config()

                try:
                    with st.spinner("🤔 AI正在思考..."):
                        # 构建输入状态，包含用户信息
                        input_state = {
                            "messages": [HumanMessage(content=user_input)],
                            "current_user_id": st.session_state.user_id,
                            "current_username": st.session_state.username,
                        }

                        # 使用流式调用
                        events = graph.stream(
                            input_state, config, stream_mode="updates"
                        )
                        self.process_stream_events(events)

                    # 刷新页面以显示可能的新中断
                    st.rerun()

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
        self.render_hitl_confirmation()

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
