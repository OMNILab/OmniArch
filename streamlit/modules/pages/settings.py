"""
Settings Page Module
Contains the settings page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
import json


class SettingsPage:
    """System settings page implementation"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """System settings page implementation"""
        self.ui.create_header("系统设置")

        # Check admin privileges
        self.auth_manager.require_admin()

        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["用户管理", "组织架构管理", "系统配置", "数据管理"]
        )

        with tab1:
            st.markdown("### 用户管理")

            users_df = self.data_manager.get_dataframe("users")

            # User management interface
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### 用户列表")

                # Enhanced user table with actions
                if len(users_df) > 0:
                    gb = GridOptionsBuilder.from_dataframe(
                        users_df[["username", "name", "department", "role", "email"]]
                    )
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_side_bar()
                    gb.configure_selection("multiple", use_checkbox=True)
                    grid_options = gb.build()

                    grid_response = AgGrid(
                        users_df[["username", "name", "department", "role", "email"]],
                        gridOptions=grid_options,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        height=400,
                    )
                else:
                    st.info("暂无用户数据")

            with col2:
                st.markdown("#### 用户统计")

                if len(users_df) > 0:
                    # User statistics
                    role_counts = users_df["role"].value_counts()
                    dept_counts = users_df["department"].value_counts()

                    st.metric("总用户数", len(users_df))
                    st.metric(
                        "管理员数", len(users_df[users_df["role"] == "系统管理员"])
                    )
                    st.metric(
                        "组织者数", len(users_df[users_df["role"] == "会议组织者"])
                    )

                    # Role distribution
                    fig = px.pie(
                        values=role_counts.values,
                        names=role_counts.index,
                        title="用户角色分布",
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 组织架构管理")

            users_df = self.data_manager.get_dataframe("users")

            if len(users_df) > 0:
                # Organization data
                org_data = (
                    users_df.groupby("department")
                    .agg({"id": "count", "name": "first"})
                    .reset_index()
                )
                org_data.columns = ["部门", "人数", "示例成员"]
                org_data["状态"] = "正常"

                st.dataframe(org_data, use_container_width=True)

                # Department statistics
                fig = px.bar(
                    org_data,
                    x="部门",
                    y="人数",
                    title="各部门人数统计",
                    color="人数",
                    color_continuous_scale="viridis",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无组织架构数据")

        with tab3:
            st.markdown("### 系统配置")

            # User preferences
            preferences = self.auth_manager.get_user_preferences()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 界面设置")

                theme = st.selectbox(
                    "主题",
                    ["light", "dark"],
                    index=0 if preferences.get("theme") == "light" else 1,
                )

                language = st.selectbox(
                    "语言",
                    ["zh_CN", "en_US"],
                    index=0 if preferences.get("language") == "zh_CN" else 1,
                )

                if st.button("保存界面设置"):
                    self.auth_manager.update_user_preference("theme", theme)
                    self.auth_manager.update_user_preference("language", language)
                    st.success("设置已保存")

            with col2:
                st.markdown("#### 功能设置")

                notifications = st.checkbox(
                    "启用通知", value=preferences.get("notifications", True)
                )

                auto_save = st.checkbox(
                    "自动保存", value=preferences.get("auto_save", True)
                )

                if st.button("保存功能设置"):
                    self.auth_manager.update_user_preference(
                        "notifications", notifications
                    )
                    self.auth_manager.update_user_preference("auto_save", auto_save)
                    st.success("设置已保存")

        with tab4:
            st.markdown("### 数据管理")

            dashboard_data = self.data_manager.get_dashboard_data()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 数据统计")

                st.metric("会议数据", dashboard_data["total_meetings"])
                st.metric("任务数据", dashboard_data["total_tasks"])
                st.metric("用户数据", dashboard_data["total_users"])
                st.metric("会议室数据", dashboard_data["total_rooms"])

            with col2:
                st.markdown("#### 数据操作")

                st.warning("⚠️ 以下操作将影响所有数据")

                if st.button("重置所有数据", type="secondary"):
                    if st.button("确认重置所有数据", key="admin_reset"):
                        self.data_manager.reset_to_default()
                        st.success("所有数据已重置")
                        st.rerun()

                if st.button("导出系统数据", type="primary"):
                    # Export all data as JSON
                    all_data = self.data_manager.get_data()
                    json_data = json.dumps(
                        all_data, default=str, ensure_ascii=False, indent=2
                    )

                    st.download_button(
                        label="下载系统数据",
                        data=json_data,
                        file_name="system_data.json",
                        mime="application/json",
                    )