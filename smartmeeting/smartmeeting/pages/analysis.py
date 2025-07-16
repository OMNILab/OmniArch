"""
PandasAI Demo Page Module
Contains the PandasAI demo page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
import json
import os
import logging
import time
from typing import Optional, Dict, Any, Callable
from smartmeeting.tools import setup_pandasai_llm, create_pandasai_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Localization dictionary for easy text management
TEXTS = {
    "header": "智能分析",
    "ai_enabled": "✅ AI 分析已启用",
    "ai_init_failed": "❌ AI Agent初始化失败，请重试",
    "no_data": "📭 暂无数据，请先创建一些数据",
    "data_overview": "#### 📊 数据概览",
    "data_preview": "#### 📋 数据预览",
    "analysis_query": "#### 🤖 智能分析查询",
    "select_query": "请选择...",
    "built_in_query": "**📝 内置查询（推荐）**",
    "custom_query": "**✏️ 自定义查询**",
    "query_placeholder": "例如：分析会议时长分布、统计任务完成率、查看用户活跃度等",
    "query_help": "用自然语言描述您想要的分析内容",
    "start_analysis": "🚀 开始分析",
    "no_query": "⚠️ 请选择内置查询或输入自定义查询",
    "analysis_running": "⚠️ 分析正在进行中，请稍候...",
    "ai_analyzing": "🤖 AI正在分析数据...",
    "ai_executing": "🤖 正在执行AI分析...",
    "generating_visuals": "🤖 正在生成可视化...",
    "analysis_complete": "✅ AI 分析完成！",
    "analysis_failed": "❌ AI 分析失败，请重试",
    "ai_not_initialized": "❌ AI Agent未初始化，请联系管理员",
    "error_occurred": "❌ 分析过程中出现错误: {error}",
    "fallback_info": "创建基础可视化图表...",
    "no_visualizable_cols": "数据中没有可用的数值或分类字段来创建图表",
}


class AnalysisPage:
    """PandasAI demo page implementation with enhanced functionality for smart meeting system analysis"""

    def __init__(self, data_manager, auth_manager, ui_components):
        """Initialize the AnalysisPage with required components.

        Args:
            data_manager: Data manager instance for accessing data sources.
            auth_manager: Authentication manager instance.
            ui_components: UI components for rendering the interface.
        """
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components
        # Initialize session state
        if "analysis_running" not in st.session_state:
            st.session_state.analysis_running = False

    def perform_ai_analysis(
        self, query: str, sample_data: pd.DataFrame, llm: Any
    ) -> Optional[str]:
        """Perform AI-powered analysis using PandasAI with fallback to basic analysis.

        Args:
            query: User query for analysis.
            sample_data: DataFrame containing the data to analyze.
            llm: Initialized LLM instance for PandasAI.

        Returns:
            Analysis result as a string or None if both AI and basic analysis fail.
        """
        if not isinstance(sample_data, pd.DataFrame) or sample_data.empty:
            st.error("无效的数据集，请检查数据源")
            return None

        try:
            if llm:
                result = self._perform_pandasai_analysis(query, sample_data, llm)
                if result:
                    return result
                st.info("AI分析无结果，使用基础分析")
                return self._perform_basic_analysis(query, sample_data)
            return self._perform_basic_analysis(query, sample_data)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            st.error(TEXTS["error_occurred"].format(error=str(e)))
            try:
                return self._perform_basic_analysis(query, sample_data)
            except Exception as fallback_error:
                logger.error(f"Basic analysis failed: {fallback_error}")
                st.error(f"基础分析也失败: {fallback_error}")
                return None

    def _perform_pandasai_analysis(
        self, query: str, sample_data: pd.DataFrame, llm: Any
    ) -> Optional[str]:
        """Perform intelligent analysis using PandasAI.

        Args:
            query: User query for analysis.
            sample_data: DataFrame containing the data to analyze.
            llm: Initialized LLM instance for PandasAI.

        Returns:
            Analysis result as a string or None if analysis fails.
        """
        try:
            agent = create_pandasai_agent(sample_data, llm)
            if not agent:
                st.warning("AI智能体创建失败，使用基础分析")
                return self._perform_basic_analysis(query, sample_data)

            prompt = f"""请用中文分析以下数据：{query}

要求：
1. 分析结果必须用中文展示
2. 提供简洁明了的洞察
3. 生成1个最相关的plotly图表
4. 图表标题和标签使用中文
5. 返回plotly图表对象，不使用.show()或write_html()
6. 示例：
   import plotly.express as px
   fig = px.bar(data, x='column', y='value', title='标题')
   return fig"""

            start_time = time.time()
            timeout = 60  # 60 seconds timeout
            response = agent.chat(prompt)

            if time.time() - start_time > timeout:
                st.warning("AI分析超时，使用基础分析")
                return self._perform_basic_analysis(query, sample_data)

            charts_displayed = self._handle_pandasai_response(
                response, sample_data, query
            )
            if not charts_displayed:
                st.info("AI未生成图表，创建基础可视化")
                self._create_fallback_charts(sample_data, query)

            return str(response) if response else None

        except Exception as e:
            logger.warning(f"PandasAI analysis failed: {e}")
            st.warning(f"AI分析失败，使用基础分析: {e}")
            return self._perform_basic_analysis(query, sample_data)

    def _perform_basic_analysis(
        self, query: str, sample_data: pd.DataFrame
    ) -> Optional[str]:
        """Perform basic analysis when PandasAI is unavailable.

        Args:
            query: User query for analysis.
            sample_data: DataFrame containing the data to analyze.

        Returns:
            Analysis result as a string or None if analysis fails.
        """
        try:
            query_lower = query.lower()
            if any(k in query_lower for k in ["统计", "概览", "统计信息"]):
                return self._generate_statistical_analysis(sample_data)
            elif any(k in query_lower for k in ["图表", "可视化", "图形"]):
                return self._generate_visualization_analysis(sample_data)
            elif any(k in query_lower for k in ["趋势", "变化"]):
                return self._generate_trend_analysis(sample_data)
            elif "分布" in query_lower:
                return self._generate_distribution_analysis(sample_data)
            elif any(k in query_lower for k in ["关联", "关系"]):
                return self._generate_correlation_analysis(sample_data)
            elif any(k in query_lower for k in ["效率", "性能"]):
                return self._generate_efficiency_analysis(sample_data)
            return self._generate_general_analysis(sample_data, query)
        except Exception as e:
            logger.error(f"Basic analysis failed: {e}")
            st.error(f"基础分析失败: {e}")
            return None

    def _generate_statistical_analysis(self, data: pd.DataFrame) -> str:
        """Generate statistical analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Statistical analysis as a markdown string.
        """
        analysis = "## 📊 数据统计分析\n\n"
        analysis += f"- **总记录数**: {len(data)}\n"
        analysis += f"- **字段数**: {len(data.columns)}\n\n"

        numeric_cols = data.select_dtypes(include=["number"]).columns
        if numeric_cols.any():
            analysis += "### 数值型字段统计\n"
            stats = data[numeric_cols].describe()
            analysis += f"- 数值字段: {', '.join(numeric_cols)}\n"
            analysis += f"- 平均值范围: {stats.loc['mean'].min():.2f} - {stats.loc['mean'].max():.2f}\n"
            analysis += f"- 标准差范围: {stats.loc['std'].min():.2f} - {stats.loc['std'].max():.2f}\n\n"

        categorical_cols = data.select_dtypes(include=["object"]).columns
        if categorical_cols.any():
            analysis += "### 分类型字段统计\n"
            for col in categorical_cols[:3]:
                unique_count = data[col].nunique()
                analysis += f"- **{col}**: {unique_count} 个唯一值\n"

        return analysis

    def _generate_visualization_analysis(self, data: pd.DataFrame) -> str:
        """Generate visualization analysis suggestions in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Visualization suggestions as a markdown string.
        """
        analysis = "## 📈 数据可视化分析\n\n"
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if numeric_cols.any():
            analysis += "### 数值型数据可视化建议\n"
            analysis += "- 直方图: 查看数值分布\n"
            analysis += "- 箱线图: 识别异常值\n"
            if len(numeric_cols) >= 2:
                analysis += "- 散点图: 分析变量关系\n"

        if categorical_cols.any():
            analysis += "\n### 分类型数据可视化建议\n"
            analysis += "- 柱状图: 显示类别频次\n"
            analysis += "- 饼图: 显示比例分布\n"

        return analysis

    def _generate_trend_analysis(self, data: pd.DataFrame) -> str:
        """Generate trend analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Trend analysis as a markdown string.
        """
        analysis = "## 📈 趋势分析\n\n"
        time_cols = self._find_time_columns(data)

        if time_cols:
            analysis += f"发现时间相关字段: {', '.join(time_cols)}\n"
            analysis += "建议进行时间序列分析:\n"
            analysis += "- 时间趋势图\n"
            analysis += "- 周期性分析\n"
            analysis += "- 季节性模式识别\n"
        else:
            analysis += "未发现明显的时间字段，建议:\n"
            analysis += "- 检查是否有日期/时间列\n"
            analysis += "- 考虑添加时间维度进行分析\n"

        return analysis

    def _generate_distribution_analysis(self, data: pd.DataFrame) -> str:
        """Generate distribution analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Distribution analysis as a markdown string.
        """
        analysis = "## 📊 分布分析\n\n"
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if numeric_cols.any():
            analysis += "### 数值型数据分布\n"
            for col in numeric_cols[:3]:
                stats = data[col].describe()
                analysis += f"- **{col}**: 均值={stats['mean']:.2f}, 标准差={stats['std']:.2f}\n"

        if categorical_cols.any():
            analysis += "\n### 分类型数据分布\n"
            for col in categorical_cols[:3]:
                value_counts = data[col].value_counts()
                analysis += f"- **{col}**: 最多值='{value_counts.index[0]}' ({value_counts.iloc[0]}次)\n"

        return analysis

    def _generate_correlation_analysis(self, data: pd.DataFrame) -> str:
        """Generate correlation analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Correlation analysis as a markdown string.
        """
        analysis = "## 🔗 关联关系分析\n\n"
        numeric_cols = data.select_dtypes(include=["number"]).columns

        if len(numeric_cols) >= 2:
            corr_matrix = data[numeric_cols].corr()
            fig = self._create_plotly_chart(
                px.imshow,
                corr_matrix,
                title="数值字段相关性热力图",
                color_continuous_scale="RdBu",
                aspect="auto",
                height=500,
            )
            st.plotly_chart(fig, use_container_width=True)

            analysis += "### 相关性分析结果\n"
            analysis += f"- 分析了 {len(numeric_cols)} 个数值字段之间的相关性\n"
            strong_corr = [
                (corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j])
                for i in range(len(corr_matrix.columns))
                for j in range(i + 1, len(corr_matrix.columns))
                if abs(corr_matrix.iloc[i, j]) > 0.7
            ]

            if strong_corr:
                analysis += "- **强相关性发现**:\n"
                for var1, var2, corr in strong_corr:
                    analysis += f"  - {var1} 与 {var2}: {corr:.3f}\n"
            else:
                analysis += "- 未发现强相关性关系\n"
        else:
            analysis += "数值字段不足，无法进行相关性分析\n"

        return analysis

    def _generate_efficiency_analysis(self, data: pd.DataFrame) -> str:
        """Generate efficiency analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Efficiency analysis as a markdown string.
        """
        analysis = "## ⚡ 效率性能分析\n\n"

        if "数据源" in data.columns:
            source_counts = data["数据源"].value_counts()
            fig = self._create_plotly_chart(
                px.bar,
                x=source_counts.index,
                y=source_counts.values,
                title="各数据源记录分布",
                labels={"x": "数据源", "y": "记录数"},
                color=source_counts.values,
                color_continuous_scale="viridis",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            analysis += "### 数据源效率分析\n"
            analysis += f"- 总记录数: {len(data)}\n"
            analysis += f"- 数据源分布: {', '.join([f'{k}({v})' for k, v in source_counts.items()])}\n"
            for source, count in source_counts.items():
                percentage = (count / len(data)) * 100
                analysis += f"- {source}: {count} 条记录 ({percentage:.1f}%)\n"

        elif "时长" in data.columns:
            duration_stats = data["时长"].describe()
            fig = self._create_plotly_chart(
                px.histogram,
                data,
                x="时长",
                title="会议时长分布",
                nbins=20,
                color_discrete_sequence=["#1f77b4"],
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            analysis += "### 会议时长效率分析\n"
            analysis += f"- 平均时长: {duration_stats['mean']:.1f} 分钟\n"
            analysis += f"- 最短时长: {duration_stats['min']:.1f} 分钟\n"
            analysis += f"- 最长时长: {duration_stats['max']:.1f} 分钟\n"
            analysis += f"- 时长标准差: {duration_stats['std']:.1f} 分钟\n"
            analysis += "- **效率建议**: " + (
                "平均会议时长较长，建议优化会议流程\n"
                if duration_stats["mean"] > 60
                else "会议时长合理，效率良好\n"
            )

        elif "状态" in data.columns:
            status_counts = data["状态"].value_counts()
            fig = self._create_plotly_chart(
                px.pie,
                values=status_counts.values,
                names=status_counts.index,
                title="任务状态分布",
                color_discrete_sequence=px.colors.qualitative.Set3,
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            total_tasks = len(data)
            completed_tasks = status_counts.get("完成", 0)
            completion_rate = (
                (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            )
            analysis += "### 任务完成效率分析\n"
            analysis += f"- 总任务数: {total_tasks}\n"
            analysis += f"- 已完成任务: {completed_tasks}\n"
            analysis += f"- 完成率: {completion_rate:.1f}%\n"
            analysis += "- **效率评估**: " + (
                "任务完成率优秀\n"
                if completion_rate >= 80
                else (
                    "任务完成率良好\n"
                    if completion_rate >= 60
                    else "任务完成率需要改进\n"
                )
            )

        return analysis

    def _generate_general_analysis(self, data: pd.DataFrame, query: str) -> str:
        """Generate general analysis based on query.

        Args:
            data: DataFrame to analyze.
            query: User query for analysis.

        Returns:
            General analysis as a markdown string.
        """
        analysis = f"### 🤖 AI 分析结果\n\n针对查询: **{query}**\n\n"
        analysis += "### 数据洞察\n"
        analysis += f"- 数据集包含 {len(data)} 条记录\n"
        analysis += f"- 涵盖 {len(data.columns)} 个字段\n"

        numeric_cols = data.select_dtypes(include=["number"]).columns
        if numeric_cols.any():
            analysis += f"- 包含 {len(numeric_cols)} 个数值型字段\n"
            st.markdown("#### 📊 数值字段分布")
            for col in numeric_cols[:2]:
                fig = self._create_plotly_chart(
                    px.histogram, data, x=col, title=f"{col} 分布", nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)

        categorical_cols = data.select_dtypes(include=["object"]).columns
        if categorical_cols.any():
            analysis += f"- 包含 {len(categorical_cols)} 个分类型字段\n"
            st.markdown("#### 📈 分类字段分布")
            for col in categorical_cols[:2]:
                value_counts = data[col].value_counts()
                fig = self._create_plotly_chart(
                    px.bar,
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"{col} 分布",
                    labels={"x": col, "y": "数量"},
                    color=value_counts.values,
                    color_continuous_scale="viridis",
                )
                st.plotly_chart(fig, use_container_width=True)

        analysis += "\n### 建议\n"
        analysis += "- 尝试更具体的查询，如'显示统计信息'或'生成图表'\n"
        analysis += "- 使用内置查询获取常用分析结果\n"

        return analysis

    def show(self) -> None:
        """Display the main analysis page."""
        self.ui.create_header(TEXTS["header"])

        # 侧边栏功能说明
        st.sidebar.markdown("### 🔍 功能说明")
        st.sidebar.markdown(
            """
        **📊 智能分析**:
        - 多数据源综合分析
        - AI驱动的数据洞察
        - 自动生成可视化图表
        - 业务效率深度分析
        
        **🎯 分析类型**:
        - 统计分析：基础数据统计
        - 趋势分析：时间序列分析
        - 关联分析：数据关联挖掘
        - 效率分析：业务效率评估
        """
        )

        llm = setup_pandasai_llm()

        if llm:
            st.success(TEXTS["ai_enabled"])
        else:
            st.error(TEXTS["ai_init_failed"])
            return

        data_sources = ["会议数据", "任务数据", "用户数据", "会议室数据", "全部数据"]
        selected_source = st.selectbox("选择数据源", data_sources, index=0)

        sample_data = self._get_selected_data(selected_source)
        if sample_data.empty:
            st.info(TEXTS["no_data"])
            return

        self._show_data_overview(sample_data)
        self._show_data_preview(sample_data)
        self._show_analysis_interface(sample_data, llm, selected_source)

    def _get_selected_data(self, selected_source: str) -> pd.DataFrame:
        """Get data based on selected source.

        Args:
            selected_source: Selected data source name.

        Returns:
            DataFrame containing the selected data.
        """
        data_mapping = {
            "全部数据": self._get_merged_data,
            "会议数据": lambda: self.data_manager.get_dataframe("meetings"),
            "任务数据": lambda: self.data_manager.get_dataframe("tasks"),
            "用户数据": lambda: self.data_manager.get_dataframe("users"),
            "会议室数据": lambda: self.data_manager.get_dataframe("rooms"),
        }
        return data_mapping.get(selected_source, lambda: pd.DataFrame())()

    def _get_merged_data(self) -> pd.DataFrame:
        """Get merged dataset from all sources.

        Returns:
            Merged DataFrame.
        """
        meetings_df = self.data_manager.get_dataframe("meetings")
        tasks_df = self.data_manager.get_dataframe("tasks")
        users_df = self.data_manager.get_dataframe("users")
        rooms_df = self.data_manager.get_dataframe("rooms")
        return self._create_merged_dataset(meetings_df, tasks_df, users_df, rooms_df)

    def _show_data_overview(self, sample_data: pd.DataFrame) -> None:
        """Display data overview.

        Args:
            sample_data: DataFrame to display overview for.
        """
        st.markdown(TEXTS["data_overview"])
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总记录数", len(sample_data))
        with col2:
            st.metric("字段数", len(sample_data.columns))
        with col3:
            st.metric(
                "数值字段", len(sample_data.select_dtypes(include=["number"]).columns)
            )
        with col4:
            st.metric(
                "分类字段", len(sample_data.select_dtypes(include=["object"]).columns)
            )

        st.markdown("---")

    def _show_data_preview(self, sample_data: pd.DataFrame) -> None:
        """Display data preview.

        Args:
            sample_data: DataFrame to display preview for.
        """
        st.markdown(TEXTS["data_preview"])
        with st.expander("查看数据详情", expanded=True):
            st.dataframe(sample_data.head(8), use_container_width=True)
        st.markdown("---")

    def _show_analysis_interface(
        self, sample_data: pd.DataFrame, llm: Any, selected_source: str
    ) -> None:
        """Display analysis query interface.

        Args:
            sample_data: DataFrame to analyze.
            llm: Initialized LLM instance.
            selected_source: Selected data source.
        """
        st.markdown(TEXTS["analysis_query"])
        query = self._get_user_query(selected_source)

        if st.button(TEXTS["start_analysis"], type="primary", use_container_width=True):
            self._execute_analysis(query, sample_data, llm)

    def _get_user_query(self, selected_source: str) -> str:
        """Get user query from built-in or custom input.

        Args:
            selected_source: Selected data source.

        Returns:
            User query string.
        """
        built_in_queries = self._get_built_in_queries(selected_source)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(TEXTS["built_in_query"])
            selected_built_in = st.selectbox(
                TEXTS["select_query"],
                [TEXTS["select_query"]] + list(built_in_queries.keys()),
                help=TEXTS["query_help"],
            )
            query = (
                built_in_queries.get(selected_built_in, "")
                if selected_built_in != TEXTS["select_query"]
                else ""
            )
            if query:
                st.markdown(f"**查询内容：** {query}")

        with col2:
            st.markdown(TEXTS["custom_query"])
            custom_query = st.text_area(
                TEXTS["custom_query"],
                placeholder=TEXTS["query_placeholder"],
                height=100,
                help=TEXTS["query_help"],
            )
            if custom_query:
                query = custom_query

        return query

    def _execute_analysis(
        self, query: str, sample_data: pd.DataFrame, llm: Any
    ) -> None:
        """Execute analysis with progress indicators.

        Args:
            query: User query for analysis.
            sample_data: DataFrame to analyze.
            llm: Initialized LLM instance.
        """
        if not query:
            st.warning(TEXTS["no_query"])
            return

        if st.session_state.analysis_running:
            st.warning(TEXTS["analysis_running"])
            return

        st.session_state.analysis_running = True
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text(TEXTS["ai_analyzing"])
            progress_bar.progress(25)

            if llm:
                status_text.text(TEXTS["ai_executing"])
                progress_bar.progress(50)
                analysis_result = self.perform_ai_analysis(query, sample_data, llm)
                progress_bar.progress(75)
                status_text.text(TEXTS["generating_visuals"])

                if analysis_result:
                    progress_bar.progress(100)
                    status_text.text(TEXTS["analysis_complete"])
                    progress_bar.empty()
                    status_text.empty()
                    st.success(TEXTS["analysis_complete"])
                    self._display_analysis_results(analysis_result, sample_data, query)
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(TEXTS["analysis_failed"])
            else:
                progress_bar.empty()
                status_text.empty()
                st.error(TEXTS["ai_not_initialized"])
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(TEXTS["error_occurred"].format(error=str(e)))
        finally:
            st.session_state.analysis_running = False

    def _display_analysis_results(
        self, analysis_result: str, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display analysis results and appropriate visualizations.

        Args:
            analysis_result: Analysis result as a string.
            sample_data: DataFrame analyzed.
            query: User query.
        """
        st.markdown(analysis_result)
        self._show_appropriate_visualizations(sample_data, query)

    def _show_appropriate_visualizations(
        self, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display visualizations based on query type.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        query_lower = query.lower()
        visualization_mapping: Dict[str, Callable] = {
            "统计": self._show_statistical_visualizations,
            "概览": self._show_statistical_visualizations,
            "分布": self._show_statistical_visualizations,
            "分析": self._show_statistical_visualizations,
            "效率": self._show_efficiency_visualizations,
            "性能": self._show_efficiency_visualizations,
            "完成率": self._show_efficiency_visualizations,
            "利用率": self._show_efficiency_visualizations,
            "关联": self._show_correlation_visualizations,
            "关系": self._show_correlation_visualizations,
            "相关性": self._show_correlation_visualizations,
            "影响": self._show_correlation_visualizations,
            "趋势": self._show_temporal_visualizations,
            "时间": self._show_temporal_visualizations,
            "模式": self._show_temporal_visualizations,
            "变化": self._show_temporal_visualizations,
            "对比": self._show_comparison_visualizations,
            "比较": self._show_comparison_visualizations,
            "差异": self._show_comparison_visualizations,
            "排名": self._show_comparison_visualizations,
        }

        executed_methods = set()
        chart_count = 0
        max_charts = 2

        for keyword, method in visualization_mapping.items():
            if (
                keyword in query_lower
                and method not in executed_methods
                and chart_count < max_charts
            ):
                method(sample_data, query)
                executed_methods.add(method)
                chart_count += 1

    def _show_statistical_visualizations(
        self, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display statistical visualizations.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        st.markdown("#### 📈 统计可视化")
        numeric_cols = sample_data.select_dtypes(include=["number"]).columns
        categorical_cols = sample_data.select_dtypes(include=["object"]).columns

        if numeric_cols.any():
            self._create_plotly_chart(
                px.histogram,
                sample_data,
                x=numeric_cols[0],
                title=f"{numeric_cols[0]} 分布",
                nbins=20,
                color_discrete_sequence=["#1f77b4"],
            )
            st.plotly_chart(st.session_state.last_chart, use_container_width=True)
        elif categorical_cols.any():
            value_counts = sample_data[categorical_cols[0]].value_counts()
            self._create_plotly_chart(
                px.bar,
                x=value_counts.index,
                y=value_counts.values,
                title=f"{categorical_cols[0]} 分布",
                labels={"x": categorical_cols[0], "y": "数量"},
                color=value_counts.values,
                color_continuous_scale="viridis",
            )
            st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _show_efficiency_visualizations(
        self, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display efficiency visualizations.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        st.markdown("#### ⚡ 效率分析可视化")
        if "数据源" in sample_data.columns:
            self._show_data_source_efficiency(sample_data)
        elif "时长" in sample_data.columns:
            self._show_duration_efficiency(sample_data)
        elif "状态" in sample_data.columns:
            self._show_status_efficiency(sample_data)
        else:
            numeric_cols = sample_data.select_dtypes(include=["number"]).columns
            if numeric_cols.any():
                self._create_plotly_chart(
                    px.histogram,
                    sample_data,
                    x=numeric_cols[0],
                    title=f"{numeric_cols[0]} 效率分布",
                    nbins=20,
                )
                st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _show_data_source_efficiency(self, sample_data: pd.DataFrame) -> None:
        """Display data source efficiency visualization.

        Args:
            sample_data: DataFrame containing data source information.
        """
        source_efficiency = sample_data["数据源"].value_counts()
        self._create_plotly_chart(
            px.pie,
            values=source_efficiency.values,
            names=source_efficiency.index,
            title="各数据源记录分布",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _show_duration_efficiency(self, sample_data: pd.DataFrame) -> None:
        """Display duration efficiency visualization and metrics.

        Args:
            sample_data: DataFrame containing duration information.
        """
        duration_stats = sample_data["时长"].describe()
        efficiency_score = min(100, max(0, 100 - (duration_stats["mean"] - 30) * 2))
        col1, col2 = st.columns(2)

        with col1:
            st.metric("平均时长", f"{duration_stats['mean']:.1f} 分钟")
            st.metric("效率评分", f"{efficiency_score:.1f}/100")
        with col2:
            st.metric("最短时长", f"{duration_stats['min']:.1f} 分钟")
            st.metric("最长时长", f"{duration_stats['max']:.1f} 分钟")

        self._create_plotly_chart(
            px.histogram,
            sample_data,
            x="时长",
            title="会议时长分布",
            nbins=20,
            color_discrete_sequence=["#1f77b4"],
        )
        st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _show_status_efficiency(self, sample_data: pd.DataFrame) -> None:
        """Display status efficiency visualization and metrics.

        Args:
            sample_data: DataFrame containing status information.
        """
        status_counts = sample_data["状态"].value_counts()
        completion_rate = (status_counts.get("完成", 0) / len(sample_data)) * 100
        col1, col2 = st.columns(2)

        with col1:
            st.metric("总任务数", len(sample_data))
            st.metric("完成率", f"{completion_rate:.1f}%")
        with col2:
            st.metric("已完成", status_counts.get("完成", 0))
            st.metric("进行中", status_counts.get("进行中", 0))

        self._create_plotly_chart(
            px.pie,
            values=status_counts.values,
            names=status_counts.index,
            title="任务状态分布",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _show_correlation_visualizations(
        self, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display correlation visualizations.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        st.markdown("#### 🔗 关联关系可视化")
        numeric_cols = sample_data.select_dtypes(include=["number"]).columns

        if len(numeric_cols) >= 2:
            self._create_plotly_chart(
                px.imshow,
                sample_data[numeric_cols].corr(),
                title="数值字段相关性热力图",
                color_continuous_scale="RdBu",
                aspect="auto",
                height=500,
            )
            st.plotly_chart(st.session_state.last_chart, use_container_width=True)
        else:
            categorical_cols = sample_data.select_dtypes(include=["object"]).columns
            if categorical_cols.any():
                value_counts = sample_data[categorical_cols[0]].value_counts()
                self._create_plotly_chart(
                    px.bar,
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"{categorical_cols[0]} 分布",
                    labels={"x": categorical_cols[0], "y": "数量"},
                )
                st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _show_temporal_visualizations(
        self, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display temporal visualizations.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        st.markdown("#### 📅 时间模式可视化")
        time_cols = self._find_time_columns(sample_data)

        if time_cols:
            self._create_time_series_chart(sample_data, time_cols[0])
        else:
            numeric_cols = sample_data.select_dtypes(include=["number"]).columns
            if numeric_cols.any():
                self._create_plotly_chart(
                    px.histogram,
                    sample_data,
                    x=numeric_cols[0],
                    title=f"{numeric_cols[0]} 分布",
                    nbins=20,
                )
                st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _find_time_columns(self, data: pd.DataFrame) -> list:
        """Find time-related columns in the DataFrame.

        Args:
            data: DataFrame to analyze.

        Returns:
            List of column names that are time-related.
        """
        time_cols = []
        for col in data.columns:
            try:
                if (
                    pd.api.types.is_datetime64_any_dtype(data[col])
                    or pd.to_datetime(data[col], errors="coerce").notna().sum()
                    > len(data) * 0.5
                ):
                    time_cols.append(col)
            except Exception:
                continue
        return time_cols

    def _create_time_series_chart(self, data: pd.DataFrame, column: str) -> None:
        """Create a time series chart.

        Args:
            data: DataFrame containing the time column.
            column: Name of the time column.
        """
        try:
            time_data = pd.to_datetime(data[column], errors="coerce")
            if not time_data.isna().all():
                time_counts = time_data.dt.date.value_counts().sort_index()
                self._create_plotly_chart(
                    px.line,
                    x=time_counts.index,
                    y=time_counts.values,
                    title=f"{column} 时间趋势",
                    labels={"x": "日期", "y": "数量"},
                )
                st.plotly_chart(st.session_state.last_chart, use_container_width=True)
        except Exception as e:
            st.warning(f"无法处理时间字段 {column}: {e}")

    def _show_comparison_visualizations(
        self, sample_data: pd.DataFrame, query: str
    ) -> None:
        """Display comparison visualizations.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        st.markdown("#### 📊 对比分析可视化")
        categorical_cols = sample_data.select_dtypes(include=["object"]).columns
        numeric_cols = sample_data.select_dtypes(include=["number"]).columns

        if categorical_cols.any() and numeric_cols.any():
            self._create_plotly_chart(
                px.box,
                sample_data,
                x=categorical_cols[0],
                y=numeric_cols[0],
                title=f"{categorical_cols[0]} vs {numeric_cols[0]} 对比",
            )
            st.plotly_chart(st.session_state.last_chart, use_container_width=True)
        else:
            if categorical_cols.any():
                value_counts = sample_data[categorical_cols[0]].value_counts()
                self._create_plotly_chart(
                    px.bar,
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"{categorical_cols[0]} 分布",
                    labels={"x": categorical_cols[0], "y": "数量"},
                )
                st.plotly_chart(st.session_state.last_chart, use_container_width=True)
            elif numeric_cols.any():
                self._create_plotly_chart(
                    px.histogram,
                    sample_data,
                    x=numeric_cols[0],
                    title=f"{numeric_cols[0]} 分布",
                    nbins=20,
                )
                st.plotly_chart(st.session_state.last_chart, use_container_width=True)

    def _create_plotly_chart(self, chart_func: Callable, *args, **kwargs) -> None:
        """Create a Plotly chart with consistent styling and store in session state.

        Args:
            chart_func: Plotly Express chart function (e.g., px.bar, px.histogram).
            *args: Positional arguments for the chart function.
            **kwargs: Keyword arguments for the chart function, including title and other configurations.
        """
        try:
            kwargs.setdefault("height", 400)
            fig = chart_func(*args, **kwargs)
            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=True,
                font=dict(size=12),
                title_x=0.5,
            )
            st.session_state.last_chart = fig
        except Exception as e:
            logger.error(f"Failed to create Plotly chart: {e}")
            st.warning(f"创建图表失败: {e}")

    def _handle_pandasai_response(
        self, response: Any, sample_data: pd.DataFrame, query: str
    ) -> bool:
        """Handle PandasAI response and attempt to display charts.

        Args:
            response: PandasAI response object.
            sample_data: DataFrame analyzed.
            query: User query.

        Returns:
            Boolean indicating if charts were displayed.
        """
        try:
            if isinstance(response, (go.Figure, dict)) and "data" in response:
                st.plotly_chart(response, use_container_width=True)
                return True
            elif (
                isinstance(response, (list, tuple))
                and len(response) > 0
                and isinstance(response[0], go.Figure)
            ):
                st.plotly_chart(response[0], use_container_width=True)
                return True
            else:
                st.info("未检测到图表信息，创建基础可视化")
                self._create_fallback_charts(sample_data, query)
                return True
        except Exception as e:
            logger.warning(f"Failed to handle PandasAI response: {e}")
            st.warning(f"处理PandasAI响应失败: {e}")
            self._create_fallback_charts(sample_data, query)
            return True

    def _create_fallback_charts(self, sample_data: pd.DataFrame, query: str) -> None:
        """Create fallback charts when AI analysis fails.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        try:
            st.info(TEXTS["fallback_info"])
            numeric_cols = sample_data.select_dtypes(include=["number"]).columns
            categorical_cols = sample_data.select_dtypes(include=["object"]).columns

            query_lower = query.lower()
            if "时长" in query_lower or "duration" in query_lower:
                if "时长" in sample_data.columns:
                    self._create_plotly_chart(
                        px.histogram,
                        sample_data,
                        x="时长",
                        title="会议时长分布",
                        labels={"时长": "时长（分钟）", "count": "会议数量"},
                        nbins=20,
                        color_discrete_sequence=["#1f77b4"],
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )
                elif "duration_minutes" in sample_data.columns:
                    self._create_plotly_chart(
                        px.histogram,
                        sample_data,
                        x="duration_minutes",
                        title="会议时长分布",
                        labels={
                            "duration_minutes": "时长（分钟）",
                            "count": "会议数量",
                        },
                        nbins=20,
                        color_discrete_sequence=["#1f77b4"],
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )
                elif numeric_cols.any():
                    self._create_plotly_chart(
                        px.histogram,
                        sample_data,
                        x=numeric_cols[0],
                        title=f"{numeric_cols[0]} 分布",
                        nbins=20,
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )

            elif "状态" in query_lower or "status" in query_lower:
                if "状态" in sample_data.columns:
                    status_counts = sample_data["状态"].value_counts()
                    self._create_plotly_chart(
                        px.pie,
                        values=status_counts.values,
                        names=status_counts.index,
                        title="状态分布",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )
                elif categorical_cols.any():
                    value_counts = sample_data[categorical_cols[0]].value_counts()
                    self._create_plotly_chart(
                        px.bar,
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"{categorical_cols[0]} 分布",
                        labels={"x": categorical_cols[0], "y": "数量"},
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )
            else:
                if numeric_cols.any():
                    self._create_plotly_chart(
                        px.histogram,
                        sample_data,
                        x=numeric_cols[0],
                        title=f"{numeric_cols[0]} 分布",
                        nbins=20,
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )
                elif categorical_cols.any():
                    value_counts = sample_data[categorical_cols[0]].value_counts()
                    self._create_plotly_chart(
                        px.bar,
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"{categorical_cols[0]} 分布",
                        labels={"x": categorical_cols[0], "y": "数量"},
                    )
                    st.plotly_chart(
                        st.session_state.last_chart, use_container_width=True
                    )
                else:
                    st.warning(TEXTS["no_visualizable_cols"])
        except Exception as e:
            logger.error(f"Failed to create fallback charts: {e}")
            st.warning(f"创建备用图表失败: {e}")

    def _create_merged_dataset(
        self,
        meetings_df: pd.DataFrame,
        tasks_df: pd.DataFrame,
        users_df: pd.DataFrame,
        rooms_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Create a merged dataset from all data sources with standardized data types.

        Args:
            meetings_df: Meetings DataFrame.
            tasks_df: Tasks DataFrame.
            users_df: Users DataFrame.
            rooms_df: Rooms DataFrame.

        Returns:
            Merged DataFrame with standardized columns.
        """
        merged_data = []
        default_values = {
            "数据源": str,
            "记录ID": str,
            "标题": str,
            "时长": float,
            "状态": str,
            "创建时间": str,
            "会议室": str,
            "组织者": str,
            "类型": str,
            "优先级": str,
            "截止日期": str,
            "负责人": str,
            "部门": str,
            "用户名": str,
            "姓名": str,
            "角色": str,
            "邮箱": str,
            "名称": str,
            "容量": float,
        }

        def safe_get(row, key, default=""):
            value = row.get(key, default)
            return str(value) if value is not None else default

        if not meetings_df.empty:
            for _, meeting in meetings_df.iterrows():
                merged_data.append(
                    {
                        "数据源": "会议",
                        "记录ID": safe_get(meeting, "id"),
                        "标题": safe_get(meeting, "title"),
                        "时长": float(meeting.get("duration", 0)),
                        "状态": safe_get(meeting, "status"),
                        "创建时间": safe_get(meeting, "created_datetime"),
                        "会议室": safe_get(meeting, "room_id"),
                        "组织者": safe_get(meeting, "organizer_id"),
                        "类型": "会议记录",
                    }
                )

        if not tasks_df.empty:
            for _, task in tasks_df.iterrows():
                merged_data.append(
                    {
                        "数据源": "任务",
                        "记录ID": safe_get(task, "id"),
                        "标题": safe_get(task, "title"),
                        "优先级": safe_get(task, "priority"),
                        "状态": safe_get(task, "status"),
                        "创建时间": safe_get(task, "created_datetime"),
                        "截止日期": safe_get(task, "deadline"),
                        "负责人": safe_get(task, "assignee_id"),
                        "部门": safe_get(task, "department"),
                        "类型": "任务记录",
                    }
                )

        if not users_df.empty:
            for _, user in users_df.iterrows():
                merged_data.append(
                    {
                        "数据源": "用户",
                        "记录ID": safe_get(user, "id"),
                        "用户名": safe_get(user, "username"),
                        "姓名": safe_get(user, "name"),
                        "部门": safe_get(user, "department"),
                        "角色": safe_get(user, "role"),
                        "邮箱": safe_get(user, "email"),
                        "类型": "用户记录",
                    }
                )

        if not rooms_df.empty:
            for _, room in rooms_df.iterrows():
                merged_data.append(
                    {
                        "数据源": "会议室",
                        "记录ID": safe_get(room, "id"),
                        "名称": safe_get(room, "name"),
                        "容量": float(room.get("capacity", 0)),
                        "状态": safe_get(room, "status"),
                        "类型": "会议室记录",
                    }
                )

        df = pd.DataFrame(merged_data)
        for col, dtype in default_values.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)
        return df

    def _get_built_in_queries(self, data_source: str) -> Dict[str, str]:
        """Return built-in query options based on data source.

        Args:
            data_source: Selected data source.

        Returns:
            Dictionary of built-in query options.
        """
        queries = {}
        if data_source == "全部数据":
            queries = {
                "跨数据源综合分析": "分析所有数据源的整体情况，包括各数据源的记录数量、分布特征，以及数据质量评估。生成可视化图表展示数据源分布和关键指标对比。",
                "业务效率深度分析": "深入分析会议时长分布、任务完成率、用户活跃度等关键业务指标。计算效率评分，识别效率瓶颈，并提供优化建议。生成相关图表支持分析结果。",
                "数据关联性挖掘": "分析会议、任务、用户、会议室之间的潜在关联关系。识别数据间的依赖性和影响因子，发现业务模式。使用热力图和网络图展示关联强度。",
            }
        elif data_source == "会议数据":
            queries = {
                "会议时长分布": "分析会议时长的分布情况，展示主要的时长区间。",
                "会议数量趋势": "统计每月的会议数量变化趋势。",
                "会议室使用统计": "统计各会议室的使用次数。",
            }
        elif data_source == "任务数据":
            queries = {
                "任务完成率统计": "统计任务的完成情况，计算完成率。",
                "任务优先级分布": "分析不同优先级任务的分布情况。",
                "部门任务统计": "统计各部门的任务分配情况。",
            }
        elif data_source == "用户数据":
            queries = {
                "用户角色分布": "分析用户在不同角色的分布情况。",
                "部门人员统计": "统计各部门的人员分布情况。",
                "用户活跃度": "分析用户的活跃程度。",
            }
        elif data_source == "会议室数据":
            queries = {
                "会议室容量分布": "分析会议室容量的分布情况。",
                "会议室状态统计": "统计不同状态会议室的数量。",
                "会议室使用率": "分析会议室的使用效率。",
            }
        return queries
