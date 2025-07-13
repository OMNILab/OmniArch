"""
PandasAI Demo Page Module
Contains the PandasAI demo page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


class PandasAIDemoPage:
    """PandasAI demo page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """PandasAI demo page implementation with enhanced functionality"""
        self.ui.create_header("智能分析")

        st.markdown("### 数据分析工具")

        # Data source selection
        data_sources = ["会议数据", "任务数据", "用户数据", "会议室数据"]
        selected_source = st.selectbox("选择数据源", data_sources)

        # Get selected data
        if selected_source == "会议数据":
            sample_data = self.data_manager.get_dataframe("meetings")
        elif selected_source == "任务数据":
            sample_data = self.data_manager.get_dataframe("tasks")
        elif selected_source == "用户数据":
            sample_data = self.data_manager.get_dataframe("users")
        else:
            sample_data = self.data_manager.get_dataframe("rooms")

        if len(sample_data) > 0:
            st.markdown(f"#### {selected_source}")

            # Show data preview
            with st.expander("数据预览"):
                st.dataframe(sample_data.head(10), use_container_width=True)

            # Natural language query
            st.markdown("#### 自然语言查询")

            query = st.text_input(
                "请输入您的问题", placeholder="例如：显示数据的基本统计信息", value=""
            )

            if st.button("分析", type="primary"):
                if query:
                    with st.spinner("正在分析..."):
                        import time

                        time.sleep(1)  # Simulate processing

                        # Mock AI response based on query
                        if "统计" in query or "概览" in query:
                            st.success("分析完成！")
                            st.markdown("#### 数据统计结果")

                            # Show basic statistics
                            numeric_cols = sample_data.select_dtypes(
                                include=["number"]
                            ).columns
                            if len(numeric_cols) > 0:
                                st.dataframe(sample_data[numeric_cols].describe())

                            # Show value counts for categorical columns
                            categorical_cols = sample_data.select_dtypes(
                                include=["object"]
                            ).columns[:3]
                            if len(categorical_cols) > 0:
                                for col in categorical_cols:
                                    if col in sample_data.columns:
                                        st.markdown(f"**{col} 分布:**")
                                        value_counts = sample_data[col].value_counts()

                                        fig = px.bar(
                                            x=value_counts.index,
                                            y=value_counts.values,
                                            title=f"{col} 分布",
                                            labels={"x": col, "y": "数量"},
                                        )
                                        fig.update_layout(height=300)
                                        st.plotly_chart(fig, use_container_width=True)

                        elif "图表" in query or "可视化" in query:
                            st.success("分析完成！")
                            st.markdown("#### 数据可视化")

                            # Create visualization based on data type
                            if selected_source == "会议数据":
                                # Meeting duration distribution
                                fig = px.histogram(
                                    sample_data,
                                    x="duration",
                                    title="会议时长分布",
                                    nbins=20,
                                )
                                st.plotly_chart(fig, use_container_width=True)

                                # Meeting types
                                if "type" in sample_data.columns:
                                    type_counts = sample_data["type"].value_counts()
                                    fig = px.pie(
                                        values=type_counts.values,
                                        names=type_counts.index,
                                        title="会议类型分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif selected_source == "任务数据":
                                # Task status distribution
                                if "status" in sample_data.columns:
                                    status_counts = sample_data["status"].value_counts()
                                    fig = px.bar(
                                        x=status_counts.index,
                                        y=status_counts.values,
                                        title="任务状态分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                # Priority distribution
                                if "priority" in sample_data.columns:
                                    priority_counts = sample_data[
                                        "priority"
                                    ].value_counts()
                                    fig = px.pie(
                                        values=priority_counts.values,
                                        names=priority_counts.index,
                                        title="优先级分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            elif selected_source == "用户数据":
                                # Department distribution
                                if "department" in sample_data.columns:
                                    dept_counts = sample_data[
                                        "department"
                                    ].value_counts()
                                    fig = px.bar(
                                        x=dept_counts.index,
                                        y=dept_counts.values,
                                        title="部门人数分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                # Role distribution
                                if "role" in sample_data.columns:
                                    role_counts = sample_data["role"].value_counts()
                                    fig = px.pie(
                                        values=role_counts.values,
                                        names=role_counts.index,
                                        title="角色分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                            else:  # Room data
                                # Capacity distribution
                                if "capacity" in sample_data.columns:
                                    fig = px.histogram(
                                        sample_data,
                                        x="capacity",
                                        title="会议室容量分布",
                                        nbins=10,
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                # Room status
                                if "status" in sample_data.columns:
                                    status_counts = sample_data["status"].value_counts()
                                    fig = px.pie(
                                        values=status_counts.values,
                                        names=status_counts.index,
                                        title="会议室状态分布",
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                        else:
                            st.success("分析完成！")
                            st.info("请尝试更具体的查询，如'显示统计信息'或'生成图表'")

                            # Show basic info
                            st.markdown("#### 数据基本信息")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("总记录数", len(sample_data))

                            with col2:
                                st.metric("字段数", len(sample_data.columns))

                            with col3:
                                if (
                                    len(
                                        sample_data.select_dtypes(
                                            include=["number"]
                                        ).columns
                                    )
                                    > 0
                                ):
                                    st.metric(
                                        "数值字段",
                                        len(
                                            sample_data.select_dtypes(
                                                include=["number"]
                                            ).columns
                                        ),
                                    )
                                else:
                                    st.metric("数值字段", 0)
                else:
                    st.warning("请输入查询内容")
        else:
            st.info(f"暂无{selected_source}，请先创建一些数据")

        # Quick analysis buttons
        st.markdown("---")
        st.markdown("### 快速分析")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("数据概览", type="secondary"):
                if len(sample_data) > 0:
                    st.markdown("#### 数据概览")
                    st.write(f"**数据集:** {selected_source}")
                    st.write(f"**记录数:** {len(sample_data)}")
                    st.write(f"**字段数:** {len(sample_data.columns)}")
                    st.write(f"**字段列表:** {', '.join(sample_data.columns.tolist())}")

        with col2:
            if st.button("基础统计", type="secondary"):
                if len(sample_data) > 0:
                    numeric_cols = sample_data.select_dtypes(include=["number"]).columns
                    if len(numeric_cols) > 0:
                        st.markdown("#### 基础统计")
                        st.dataframe(sample_data[numeric_cols].describe())
                    else:
                        st.info("没有数值型数据")

        with col3:
            if st.button("数据导出", type="secondary"):
                if len(sample_data) > 0:
                    csv_data = sample_data.to_csv(index=False)
                    st.download_button(
                        label="下载数据",
                        data=csv_data,
                        file_name=f"{selected_source}.csv",
                        mime="text/csv",
                    )