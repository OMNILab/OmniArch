"""
Settings Page Module
Contains the settings page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
import json
from datetime import datetime


class SettingsPage:
    """System settings page implementation"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """System settings page implementation"""
        self.ui.create_header("系统设置")

        # Get current user info for permission control
        current_user = self.auth_manager.get_current_user()
        is_admin = current_user and current_user.get("role") == "系统管理员"

        # 显示用户信息卡片
        if current_user:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.container():
                    st.markdown(
                        """
                    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;">
                        <h4 style="margin: 0; color: #1f77b4;">👤 当前用户信息</h4>
                        <p style="margin: 0.5rem 0; font-size: 1.1rem;"><strong>{}</strong> ({})</p>
                        <p style="margin: 0; color: #666;">部门：{} | 角色：{}</p>
                    </div>
                    """.format(
                            current_user.get("name", "未知"),
                            current_user.get("username", "未知"),
                            current_user.get("department", "未知"),
                            current_user.get("role", "未知"),
                        ),
                        unsafe_allow_html=True,
                    )

        # Settings tabs - 根据用户权限显示不同标签页
        if is_admin:
            tab1, tab2, tab3, tab4 = st.tabs(
                ["👥 用户管理", "🏢 组织架构管理", "⚙️ 系统配置", "💾 数据管理"]
            )
        else:
            tab1, tab2, tab3 = st.tabs(["👥 用户查看", "🏢 组织架构查看", "⚙️ 个人设置"])

        with tab1:
            users_df = self.data_manager.get_dataframe("users")

            # 第一部分：用户查看（统计卡片）
            st.markdown("#### 📊 用户概览")
            if len(users_df) > 0:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "总用户数", len(users_df), help="系统中注册的所有用户数量"
                    )

                with col2:
                    admin_count = len(users_df[users_df["role"] == "系统管理员"])
                    st.metric(
                        "管理员数", admin_count, help="具有系统管理员权限的用户数量"
                    )

                with col3:
                    organizer_count = len(users_df[users_df["role"] == "会议组织者"])
                    st.metric(
                        "组织者数", organizer_count, help="具有会议组织者权限的用户数量"
                    )

                with col4:
                    dept_count = len(users_df["department"].unique())
                    st.metric("部门数", dept_count, help="系统中的部门数量")
            else:
                st.info("暂无用户数据")

            st.markdown("---")

            # 第二部分：用户信息（详细列表）
            st.markdown("#### 📋 用户信息")
            if len(users_df) > 0:
                # 添加搜索和筛选功能
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    search_term = st.text_input(
                        "🔍 搜索用户",
                        placeholder="输入用户名、姓名或邮箱",
                        help="支持模糊搜索",
                    )

                with col2:
                    role_filter = st.selectbox(
                        "👤 角色筛选",
                        ["全部角色"] + list(users_df["role"].unique()),
                        help="按用户角色筛选",
                    )

                with col3:
                    dept_filter = st.selectbox(
                        "🏢 部门筛选",
                        ["全部部门"] + list(users_df["department"].unique()),
                        help="按部门筛选",
                    )

                # 应用筛选
                filtered_df = users_df.copy()
                if search_term:
                    mask = (
                        filtered_df["username"].str.contains(
                            search_term, case=False, na=False
                        )
                        | filtered_df["name"].str.contains(
                            search_term, case=False, na=False
                        )
                        | filtered_df["email"].str.contains(
                            search_term, case=False, na=False
                        )
                    )
                    filtered_df = filtered_df[mask]

                if role_filter != "全部角色":
                    filtered_df = filtered_df[filtered_df["role"] == role_filter]

                if dept_filter != "全部部门":
                    filtered_df = filtered_df[filtered_df["department"] == dept_filter]

                # 显示筛选结果统计
                if len(filtered_df) != len(users_df):
                    st.info(
                        f"📈 筛选结果：显示 {len(filtered_df)} / {len(users_df)} 个用户"
                    )

                # Enhanced user table with actions
                gb = GridOptionsBuilder.from_dataframe(
                    filtered_df[["username", "name", "department", "role", "email"]]
                )
                gb.configure_pagination(paginationAutoPageSize=True)
                gb.configure_side_bar()
                if is_admin:
                    gb.configure_selection("multiple", use_checkbox=True)
                grid_options = gb.build()

                grid_response = AgGrid(
                    filtered_df[["username", "name", "department", "role", "email"]],
                    gridOptions=grid_options,
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    fit_columns_on_grid_load=True,
                    theme="streamlit",
                    height=400,
                )
            else:
                st.info("暂无用户数据")

            st.markdown("---")

            # 第三部分：用户统计图表
            st.markdown("#### 📈 用户统计图表")
            if len(users_df) > 0:
                col1, col2 = st.columns(2)

                with col1:
                    # User statistics
                    role_counts = users_df["role"].value_counts()
                    dept_counts = users_df["department"].value_counts()

                    # Role distribution
                    fig = px.pie(
                        values=role_counts.values,
                        names=role_counts.index,
                        title="用户角色分布",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                    )
                    fig.update_layout(
                        height=350,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=12),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Department distribution
                    if len(dept_counts) > 0:
                        fig2 = px.bar(
                            x=dept_counts.index,
                            y=dept_counts.values,
                            title="各部门用户数量",
                            labels={"x": "部门", "y": "用户数量"},
                            color=dept_counts.values,
                            color_continuous_scale="viridis",
                            text=dept_counts.values,
                        )
                        fig2.update_layout(
                            height=350,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(size=12),
                            xaxis_tickangle=-45,
                        )
                        fig2.update_traces(textposition="outside")
                        st.plotly_chart(fig2, use_container_width=True)

                # 添加更多统计图表
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    # 用户注册趋势（按部门）
                    dept_trend = (
                        users_df.groupby("department").size().reset_index(name="count")
                    )
                    fig3 = px.treemap(
                        dept_trend,
                        path=["department"],
                        values="count",
                        title="部门用户分布树形图",
                        color="count",
                        color_continuous_scale="plasma",
                    )
                    fig3.update_layout(
                        height=300,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig3, use_container_width=True)

                with col2:
                    # 角色分布条形图
                    role_bar = px.bar(
                        x=role_counts.index,
                        y=role_counts.values,
                        title="用户角色分布（条形图）",
                        labels={"x": "角色", "y": "用户数量"},
                        color=role_counts.values,
                        color_continuous_scale="inferno",
                        text=role_counts.values,
                    )
                    role_bar.update_layout(
                        height=300,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=12),
                    )
                    role_bar.update_traces(textposition="outside")
                    st.plotly_chart(role_bar, use_container_width=True)
            else:
                st.info("暂无用户数据")

        with tab2:
            # 页面标题和描述
            if is_admin:
                st.markdown("### 🏢 组织架构管理")
                st.markdown("查看和管理组织架构信息，了解各部门人员分布")
            else:
                st.markdown("### 🏢 组织架构查看")
                st.markdown("查看组织架构信息和各部门人员分布")

            users_df = self.data_manager.get_dataframe("users")

            if len(users_df) > 0:
                # 组织架构统计卡片
                # Join with departments to get department names
                departments_df = self.data_manager.get_dataframe("departments")
                if len(departments_df) > 0:
                    users_with_dept = users_df.merge(
                        departments_df[["department_id", "department_name"]],
                        left_on="department_id",
                        right_on="department_id",
                    )

                    org_data = (
                        users_with_dept.groupby("department_name")
                        .agg({"user_id": "count", "name": "first"})
                        .reset_index()
                    )
                    org_data.columns = ["部门", "人数", "示例成员"]
                    org_data["状态"] = "正常"
                else:
                    # Fallback if departments data is not available
                    org_data = (
                        users_df.groupby("department_id")
                        .agg({"user_id": "count", "name": "first"})
                        .reset_index()
                    )
                    org_data.columns = ["部门", "人数", "示例成员"]
                    org_data["状态"] = "正常"

                # 显示统计信息
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("总部门数", len(org_data), help="系统中的部门总数")

                with col2:
                    total_users = org_data["人数"].sum()
                    st.metric("总人数", total_users, help="所有部门的总人数")

                with col3:
                    avg_dept_size = round(total_users / len(org_data), 1)
                    st.metric("平均部门人数", avg_dept_size, help="每个部门的平均人数")

                st.markdown("---")

                # 组织架构数据展示
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("#### 📊 部门人员统计表")
                    st.dataframe(org_data, use_container_width=True, height=400)

                with col2:
                    st.markdown("#### 📈 部门人数分布图")

                    # Department statistics
                    fig = px.bar(
                        org_data,
                        x="部门",
                        y="人数",
                        title="各部门人数统计",
                        color="人数",
                        color_continuous_scale="viridis",
                        text="人数",
                    )
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=12),
                        xaxis_tickangle=-45,
                        height=400,
                    )
                    fig.update_traces(textposition="outside")
                    st.plotly_chart(fig, use_container_width=True)

                # 部门详情展示
                st.markdown("---")
                st.markdown("#### 🏢 部门详细信息")

                for _, dept in org_data.iterrows():
                    with st.expander(f"📁 {dept['部门']} ({dept['人数']}人)"):
                        if len(departments_df) > 0:
                            # Get department_id from department_name
                            dept_info = departments_df[
                                departments_df["department_name"] == dept["部门"]
                            ]
                            if not dept_info.empty:
                                dept_id = dept_info.iloc[0]["department_id"]
                                dept_users = users_df[
                                    users_df["department_id"] == dept_id
                                ]
                            else:
                                dept_users = pd.DataFrame()
                        else:
                            # Fallback: try to match by department_id if it's numeric
                            try:
                                dept_id = int(dept["部门"])
                                dept_users = users_df[
                                    users_df["department_id"] == dept_id
                                ]
                            except (ValueError, TypeError):
                                dept_users = pd.DataFrame()

                        if len(dept_users) > 0:
                            # 显示部门成员
                            member_data = dept_users[["name", "role", "email"]].copy()
                            member_data.columns = ["姓名", "角色", "邮箱"]
                            st.dataframe(member_data, use_container_width=True)
                        else:
                            st.info("该部门暂无成员")
            else:
                st.info("暂无组织架构数据")

        with tab3:
            # 页面标题和描述
            if is_admin:
                st.markdown("### ⚙️ 系统配置")
                st.markdown("配置系统全局设置，包括界面主题、语言和功能选项")
            else:
                st.markdown("### ⚙️ 个人设置")
                st.markdown("个性化您的使用体验，设置界面主题、语言和个人偏好")

            # User preferences
            preferences = self.auth_manager.get_user_preferences()

            # 设置分类展示
            col1, col2 = st.columns([1, 1])

            with col1:
                # 界面设置卡片
                with st.container():
                    st.markdown(
                        """
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;">
                        <h4 style="margin: 0 0 1rem 0; color: #007bff;">🎨 界面设置</h4>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    theme = st.selectbox(
                        "主题模式",
                        ["light", "dark"],
                        index=0 if preferences.get("theme") == "light" else 1,
                        help="选择您喜欢的界面主题",
                    )

                    language = st.selectbox(
                        "界面语言",
                        ["zh_CN", "en_US"],
                        index=0 if preferences.get("language") == "zh_CN" else 1,
                        help="选择界面显示语言",
                    )

                    if st.button(
                        "💾 保存界面设置", type="primary", use_container_width=True
                    ):
                        self.auth_manager.update_user_preference("theme", theme)
                        self.auth_manager.update_user_preference("language", language)
                        st.success("✅ 界面设置已保存")

            with col2:
                # 功能设置卡片
                with st.container():
                    st.markdown(
                        """
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #28a745;">
                        <h4 style="margin: 0 0 1rem 0; color: #28a745;">🔧 功能设置</h4>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    notifications = st.checkbox(
                        "🔔 启用通知",
                        value=preferences.get("notifications", True),
                        help="是否接收系统通知和提醒",
                    )

                    auto_save = st.checkbox(
                        "💾 自动保存",
                        value=preferences.get("auto_save", True),
                        help="是否自动保存表单数据",
                    )

                    if st.button(
                        "💾 保存功能设置", type="primary", use_container_width=True
                    ):
                        self.auth_manager.update_user_preference(
                            "notifications", notifications
                        )
                        self.auth_manager.update_user_preference("auto_save", auto_save)
                        st.success("✅ 功能设置已保存")

            # 设置预览
            st.markdown("---")
            st.markdown("#### 👀 设置预览")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.info(f"**当前主题**: {theme}")

            with col2:
                st.info(f"**当前语言**: {language}")

            with col3:
                status = "启用" if notifications else "禁用"
                st.info(f"**通知状态**: {status}")

            # 设置说明
            st.markdown("---")
            st.markdown("#### 📖 设置说明")

            with st.expander("ℹ️ 查看设置说明"):
                st.markdown(
                    """
                **界面设置说明：**
                - **主题模式**: 选择浅色或深色主题，适应不同的使用环境
                - **界面语言**: 选择中文或英文界面，支持国际化使用
                
                **功能设置说明：**
                - **启用通知**: 开启后可以接收会议提醒、任务更新等通知
                - **自动保存**: 开启后系统会自动保存您的操作，防止数据丢失
                
                **注意事项：**
                - 设置修改后立即生效
                - 个人设置仅影响当前用户
                - 管理员可以修改系统全局设置
                """
                )

        # 第四个标签页只对管理员显示
        if is_admin:
            with tab4:
                st.markdown("### 💾 数据管理")
                st.markdown("管理系统数据，包括数据统计、备份和重置操作")

                dashboard_data = self.data_manager.get_dashboard_data()

                # 数据统计卡片
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "📊 会议数据",
                        dashboard_data["total_meetings"],
                        help="系统中的会议记录总数",
                    )

                with col2:
                    st.metric(
                        "📋 任务数据",
                        dashboard_data["total_tasks"],
                        help="系统中的任务记录总数",
                    )

                with col3:
                    st.metric(
                        "👥 用户数据",
                        dashboard_data["total_users"],
                        help="系统中的用户记录总数",
                    )

                with col4:
                    st.metric(
                        "🏢 会议室数据",
                        dashboard_data["total_rooms"],
                        help="系统中的会议室记录总数",
                    )

                st.markdown("---")

                # 数据操作区域
                col1, col2 = st.columns([1, 1])

                with col1:
                    # 数据导出
                    with st.container():
                        st.markdown(
                            """
                        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #17a2b8;">
                            <h4 style="margin: 0 0 1rem 0; color: #17a2b8;">📤 数据导出</h4>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        st.markdown("**导出系统数据**")
                        st.markdown("将系统所有数据导出为JSON格式，用于备份或迁移")

                        if st.button(
                            "📤 导出系统数据", type="primary", use_container_width=True
                        ):
                            # Export all data as JSON
                            all_data = self.data_manager.get_data()
                            json_data = json.dumps(
                                all_data, default=str, ensure_ascii=False, indent=2
                            )

                            st.download_button(
                                label="💾 下载系统数据",
                                data=json_data,
                                file_name=f"system_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True,
                            )

                with col2:
                    # 数据重置
                    with st.container():
                        st.markdown(
                            """
                        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #dc3545;">
                            <h4 style="margin: 0 0 1rem 0; color: #dc3545;">⚠️ 数据重置</h4>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        st.markdown("**重置系统数据**")
                        st.markdown(
                            "⚠️ **危险操作**：此操作将删除所有数据并恢复到默认状态"
                        )

                        # 使用确认对话框
                        if st.button(
                            "🗑️ 重置所有数据", type="secondary", use_container_width=True
                        ):
                            st.warning("⚠️ 您即将重置所有系统数据！")

                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button(
                                    "✅ 确认重置", key="confirm_reset", type="primary"
                                ):
                                    self.data_manager.reset_to_default()
                                    st.success("✅ 所有数据已重置")
                                    st.rerun()

                            with col_b:
                                if st.button("❌ 取消", key="cancel_reset"):
                                    st.rerun()

                # 数据管理说明
                st.markdown("---")
                st.markdown("#### 📖 数据管理说明")

                with st.expander("ℹ️ 查看数据管理说明"):
                    st.markdown(
                        """
                    **数据导出功能：**
                    - 导出格式：JSON格式，包含所有系统数据
                    - 文件命名：自动添加时间戳，便于区分不同版本
                    - 用途：数据备份、系统迁移、数据分析
                    
                    **数据重置功能：**
                    - ⚠️ **危险操作**：此操作不可逆，请谨慎使用
                    - 影响范围：删除所有会议、任务、用户、会议室数据
                    - 恢复状态：系统将恢复到初始默认状态
                    - 建议：重置前请先导出数据作为备份
                    
                    **注意事项：**
                    - 只有系统管理员可以执行数据管理操作
                    - 建议定期导出数据作为备份
                    - 重置操作需要二次确认，防止误操作
                    """
                    )

        # 侧边栏功能说明
        st.sidebar.markdown("### ⚙️ 功能说明")
        st.sidebar.markdown(
            """
        **👤 用户管理**:
        - 查看用户列表和统计
        - 管理员可添加/编辑用户
        - 用户角色和权限管理
        
        **🏢 组织架构**:
        - 部门人员分布统计
        - 组织架构可视化
        - 部门详细信息查看
        
        **⚙️ 系统设置**:
        - 界面主题和语言设置
        - 功能开关配置
        - 数据管理和备份
        """
        )
