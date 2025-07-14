"""
PandasAI Demo Page Module
Contains the PandasAI demo page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import time
import logging
import re
from smartmeeting.llm import setup_pandasai_llm, create_pandasai_agent

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
    "plotly_chart_created": "📊 已生成交互式图表",
    "analysis_insights": "#### 🔍 分析洞察",
    "chart_generation_failed": "⚠️ 图表生成失败，显示基础统计信息",
    "no_charts_generated": "⚠️ 未生成图表，使用备用可视化方案",
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
        if "last_charts" not in st.session_state:
            st.session_state.last_charts = []

    def perform_ai_analysis(
        self, query: str, sample_data: pd.DataFrame, llm: Any
    ) -> Optional[str]:
        """Perform AI-powered analysis using PandasAI with enhanced error handling and Plotly integration.

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
                result = self._perform_enhanced_pandasai_analysis(query, sample_data, llm)
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

    def _perform_enhanced_pandasai_analysis(
        self, query: str, sample_data: pd.DataFrame, llm: Any
    ) -> Optional[str]:
        """Perform intelligent analysis using PandasAI with enhanced Plotly integration and error handling.

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

            # Enhanced prompt with strict Plotly requirements
            enhanced_prompt = f"""请用中文分析以下数据：{query}

严格要求：
1. 分析结果必须用中文展示
2. 提供简洁明了的洞察和结论
3. 必须生成1-2个最相关的plotly图表
4. 图表标题、轴标签、图例必须使用中文
5. 严格使用plotly.express或plotly.graph_objects创建图表
6. 绝对不要使用matplotlib、seaborn或其他库
7. 不要使用.show()、write_html()或save()方法
8. 直接返回plotly图表对象
9. 确保图表具有交互性和美观性

数据列信息：
{list(sample_data.columns)}

示例代码格式：
import plotly.express as px
import plotly.graph_objects as go

# 创建图表
fig = px.bar(data, x='列名', y='列名', title='中文标题')
fig.update_layout(
    title_x=0.5,
    font=dict(size=12),
    showlegend=True
)
return fig

请根据查询内容生成相应的分析结果和图表。"""

            start_time = time.time()
            timeout = 90  # 增加超时时间到90秒
            
            with st.spinner(TEXTS["ai_analyzing"]):
                response = agent.chat(enhanced_prompt)

            if time.time() - start_time > timeout:
                st.warning("AI分析超时，使用基础分析")
                return self._perform_basic_analysis(query, sample_data)

            # Enhanced response handling
            charts_displayed = self._handle_enhanced_pandasai_response(
                response, sample_data, query
            )
            
            if not charts_displayed:
                st.info(TEXTS["no_charts_generated"])
                self._create_enhanced_fallback_charts(sample_data, query)

            return self._extract_text_analysis(response) if response else None

        except Exception as e:
            logger.warning(f"Enhanced PandasAI analysis failed: {e}")
            st.warning(f"AI分析失败，使用基础分析: {e}")
            return self._perform_basic_analysis(query, sample_data)

    def _perform_basic_analysis(
        self, query: str, sample_data: pd.DataFrame
    ) -> Optional[str]:
        """Perform basic analysis when PandasAI is unavailable with enhanced Plotly integration.

        Args:
            query: User query for analysis.
            sample_data: DataFrame containing the data to analyze.

        Returns:
            Analysis result as a string or None if analysis fails.
        """
        try:
            # Create appropriate charts based on query
            self._create_smart_fallback_chart(sample_data, query)
            
            query_lower = query.lower()
            if any(k in query_lower for k in ["统计", "概览", "统计信息"]):
                return self._generate_enhanced_statistical_analysis(sample_data)
            elif any(k in query_lower for k in ["图表", "可视化", "图形"]):
                return self._generate_enhanced_visualization_analysis(sample_data)
            elif any(k in query_lower for k in ["趋势", "变化"]):
                return self._generate_enhanced_trend_analysis(sample_data)
            elif "分布" in query_lower:
                return self._generate_enhanced_distribution_analysis(sample_data)
            elif any(k in query_lower for k in ["关联", "关系"]):
                return self._generate_enhanced_correlation_analysis(sample_data)
            elif any(k in query_lower for k in ["效率", "性能"]):
                return self._generate_enhanced_efficiency_analysis(sample_data)
            return self._generate_enhanced_general_analysis(sample_data, query)
        except Exception as e:
            logger.error(f"Basic analysis failed: {e}")
            st.error(f"基础分析失败: {e}")
            return None

    def _generate_enhanced_statistical_analysis(self, data: pd.DataFrame) -> str:
        """Generate enhanced statistical analysis in Chinese with better insights.

        Args:
            data: DataFrame to analyze.

        Returns:
            Enhanced statistical analysis as a markdown string.
        """
        analysis = "## 📊 数据统计分析\n\n"
        analysis += f"- **总记录数**: {len(data):,}\n"
        analysis += f"- **字段数**: {len(data.columns)}\n"
        analysis += f"- **数据完整性**: {((data.count().sum() / (len(data) * len(data.columns))) * 100):.1f}%\n\n"

        numeric_cols = data.select_dtypes(include=["number"]).columns
        if numeric_cols.any():
            analysis += "### 📈 数值型字段统计\n"
            stats = data[numeric_cols].describe()
            analysis += f"- **数值字段**: {', '.join(numeric_cols)}\n"
            analysis += f"- **平均值范围**: {stats.loc['mean'].min():.2f} - {stats.loc['mean'].max():.2f}\n"
            analysis += f"- **标准差范围**: {stats.loc['std'].min():.2f} - {stats.loc['std'].max():.2f}\n"
            analysis += f"- **数据范围**: {stats.loc['min'].min():.2f} - {stats.loc['max'].max():.2f}\n\n"

        categorical_cols = data.select_dtypes(include=["object"]).columns
        if categorical_cols.any():
            analysis += "### 📋 分类型字段统计\n"
            for col in categorical_cols[:5]:  # Show more columns
                unique_count = data[col].nunique()
                null_count = data[col].isnull().sum()
                analysis += f"- **{col}**: {unique_count} 个唯一值"
                if null_count > 0:
                    analysis += f" (缺失值: {null_count})"
                analysis += "\n"

        # Add data quality insights
        analysis += "\n### 🔍 数据质量洞察\n"
        total_cells = len(data) * len(data.columns)
        missing_cells = data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        analysis += f"- **数据完整性**: {completeness:.1f}%\n"
        analysis += f"- **缺失值总数**: {missing_cells:,}\n"
        
        if missing_cells > 0:
            missing_cols = data.columns[data.isnull().any()].tolist()
            analysis += f"- **包含缺失值的字段**: {', '.join(missing_cols[:3])}\n"

        return analysis

    def _generate_statistical_analysis(self, data: pd.DataFrame) -> str:
        """Generate statistical analysis in Chinese (legacy method for backward compatibility).

        Args:
            data: DataFrame to analyze.

        Returns:
            Statistical analysis as a markdown string.
        """
        return self._generate_enhanced_statistical_analysis(data)

    def _generate_enhanced_visualization_analysis(self, data: pd.DataFrame) -> str:
        """Generate enhanced visualization analysis suggestions in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Enhanced visualization suggestions as a markdown string.
        """
        analysis = "## 📈 数据可视化分析\n\n"
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if numeric_cols.any():
            analysis += "### 📊 数值型数据可视化建议\n"
            analysis += "- **直方图**: 查看数值分布和集中趋势\n"
            analysis += "- **箱线图**: 识别异常值和数据分布特征\n"
            analysis += "- **密度图**: 了解数据分布形状\n"
            if len(numeric_cols) >= 2:
                analysis += "- **散点图**: 分析变量间的相关性\n"
                analysis += "- **热力图**: 展示多变量相关性矩阵\n"

        if categorical_cols.any():
            analysis += "\n### 📋 分类型数据可视化建议\n"
            analysis += "- **柱状图**: 显示类别频次和排序\n"
            analysis += "- **饼图**: 显示比例分布和占比\n"
            analysis += "- **条形图**: 适合类别较多的数据\n"

        # Add specific recommendations based on data content
        analysis += "\n### 🎯 针对性建议\n"
        if "时长" in data.columns or "duration" in data.columns:
            analysis += "- **时长分析**: 建议使用直方图查看时长分布\n"
        if "状态" in data.columns or "status" in data.columns:
            analysis += "- **状态分析**: 建议使用饼图或柱状图查看状态分布\n"
        if "时间" in data.columns or "date" in data.columns:
            analysis += "- **时间分析**: 建议使用折线图查看趋势变化\n"

        return analysis

    def _generate_visualization_analysis(self, data: pd.DataFrame) -> str:
        """Generate visualization analysis suggestions in Chinese (legacy method for backward compatibility).

        Args:
            data: DataFrame to analyze.

        Returns:
            Visualization suggestions as a markdown string.
        """
        return self._generate_enhanced_visualization_analysis(data)

    def _generate_enhanced_trend_analysis(self, data: pd.DataFrame) -> str:
        """Generate enhanced trend analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Enhanced trend analysis as a markdown string.
        """
        analysis = "## 📈 趋势分析\n\n"
        time_columns = self._find_time_columns(data)
        
        if time_columns:
            analysis += f"### 🕒 发现时间相关字段\n"
            analysis += f"- **时间字段**: {', '.join(time_columns)}\n\n"
            
            # Analyze the first time column
            time_col = time_columns[0]
            try:
                data[time_col] = pd.to_datetime(data[time_col], errors='coerce')
                data_filtered = data.dropna(subset=[time_col])
                
                if not data_filtered.empty:
                    # Calculate time range
                    min_date = data_filtered[time_col].min()
                    max_date = data_filtered[time_col].max()
                    date_range = (max_date - min_date).days
                    
                    analysis += f"### 📅 时间范围分析\n"
                    analysis += f"- **开始时间**: {min_date.strftime('%Y-%m-%d')}\n"
                    analysis += f"- **结束时间**: {max_date.strftime('%Y-%m-%d')}\n"
                    analysis += f"- **时间跨度**: {date_range} 天\n"
                    
                    # Monthly trend
                    monthly_counts = data_filtered.groupby(data_filtered[time_col].dt.to_period('M')).size()
                    analysis += f"- **月度记录数**: {monthly_counts.mean():.1f} 条/月\n"
                    
                    # Trend direction
                    if len(monthly_counts) > 1:
                        trend = "上升" if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else "下降"
                        analysis += f"- **整体趋势**: {trend}\n"
                    
                    analysis += "\n### 💡 趋势分析建议\n"
                    analysis += "- 使用折线图查看时间序列变化\n"
                    analysis += "- 分析季节性模式和周期性变化\n"
                    analysis += "- 识别异常时间点和趋势转折点\n"
                else:
                    analysis += "⚠️ 时间数据格式异常，无法进行详细分析。\n"
            except Exception as e:
                analysis += f"⚠️ 时间数据处理失败: {str(e)}\n"
        else:
            analysis += "### ⚠️ 未发现时间字段\n"
            analysis += "当前数据中没有明显的时间相关字段，无法进行趋势分析。\n"
            analysis += "建议检查数据中是否包含日期、时间戳等时间信息。\n"
            
        return analysis

    def _generate_trend_analysis(self, data: pd.DataFrame) -> str:
        """Generate trend analysis in Chinese (legacy method for backward compatibility).

        Args:
            data: DataFrame to analyze.

        Returns:
            Trend analysis as a markdown string.
        """
        return self._generate_enhanced_trend_analysis(data)

    def _generate_enhanced_distribution_analysis(self, data: pd.DataFrame) -> str:
        """Generate enhanced distribution analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Enhanced distribution analysis as a markdown string.
        """
        analysis = "## 📊 分布分析\n\n"
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if numeric_cols.any():
            analysis += "### 📈 数值型数据分布\n"
            for col in numeric_cols[:5]:  # Show more columns
                stats = data[col].describe()
                null_count = data[col].isnull().sum()
                analysis += f"- **{col}**:\n"
                analysis += f"  - 均值: {stats['mean']:.2f}\n"
                analysis += f"  - 标准差: {stats['std']:.2f}\n"
                analysis += f"  - 最小值: {stats['min']:.2f}\n"
                analysis += f"  - 最大值: {stats['max']:.2f}\n"
                if null_count > 0:
                    analysis += f"  - 缺失值: {null_count}\n"
                analysis += "\n"

        if categorical_cols.any():
            analysis += "### 📋 分类型数据分布\n"
            for col in categorical_cols[:5]:  # Show more columns
                value_counts = data[col].value_counts()
                null_count = data[col].isnull().sum()
                analysis += f"- **{col}**:\n"
                analysis += f"  - 最多值: '{value_counts.index[0]}' ({value_counts.iloc[0]}次, {value_counts.iloc[0]/len(data)*100:.1f}%)\n"
                analysis += f"  - 唯一值数量: {len(value_counts)}\n"
                if null_count > 0:
                    analysis += f"  - 缺失值: {null_count}\n"
                analysis += "\n"

        # Add distribution insights
        analysis += "### 🔍 分布特征洞察\n"
        if numeric_cols.any():
            # Check for skewness
            for col in numeric_cols[:3]:
                skewness = data[col].skew()
                if abs(skewness) > 1:
                    skew_type = "右偏" if skewness > 0 else "左偏"
                    analysis += f"- **{col}**: 分布{skew_type} (偏度: {skewness:.2f})\n"
                else:
                    analysis += f"- **{col}**: 分布相对对称 (偏度: {skewness:.2f})\n"

        if categorical_cols.any():
            # Check for balanced distribution
            for col in categorical_cols[:3]:
                value_counts = data[col].value_counts()
                if len(value_counts) <= 5:  # Only for small number of categories
                    max_ratio = value_counts.iloc[0] / value_counts.iloc[-1]
                    if max_ratio > 5:
                        analysis += f"- **{col}**: 分布不均衡，主要类别占比过高\n"
                    else:
                        analysis += f"- **{col}**: 分布相对均衡\n"

        return analysis

    def _generate_distribution_analysis(self, data: pd.DataFrame) -> str:
        """Generate distribution analysis in Chinese (legacy method for backward compatibility).

        Args:
            data: DataFrame to analyze.

        Returns:
            Distribution analysis as a markdown string.
        """
        return self._generate_enhanced_distribution_analysis(data)

    def _generate_enhanced_correlation_analysis(self, data: pd.DataFrame) -> str:
        """Generate enhanced correlation analysis in Chinese.

        Args:
            data: DataFrame to analyze.

        Returns:
            Enhanced correlation analysis as a markdown string.
        """
        analysis = "## 🔗 关联关系分析\n\n"
        numeric_cols = data.select_dtypes(include=["number"]).columns

        if len(numeric_cols) >= 2:
            # Create correlation matrix
            corr_matrix = data[numeric_cols].corr()
            
            # Create heatmap using the new display method
            fig = px.imshow(
                corr_matrix,
                title="数值字段相关性热力图",
                color_continuous_scale="RdBu",
                aspect="auto",
                height=500,
            )
            fig.update_layout(
                title_x=0.5,
                font=dict(size=12),
                showlegend=True
            )
            self._display_plotly_chart(fig, "相关性热力图")

            analysis += "### 📊 相关性分析结果\n"
            analysis += f"- **分析字段**: {len(numeric_cols)} 个数值字段\n"
            analysis += f"- **相关性矩阵**: {len(numeric_cols)}×{len(numeric_cols)} 矩阵\n\n"
            
            # Find strong correlations
            strong_corr = []
            moderate_corr = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    var1, var2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    
                    if abs(corr_value) > 0.7:
                        strong_corr.append((var1, var2, corr_value))
                    elif abs(corr_value) > 0.3:
                        moderate_corr.append((var1, var2, corr_value))

            if strong_corr:
                analysis += "### 🔥 强相关性发现\n"
                for var1, var2, corr in strong_corr:
                    direction = "正相关" if corr > 0 else "负相关"
                    analysis += f"- **{var1}** 与 **{var2}**: {corr:.3f} ({direction})\n"
                analysis += "\n"

            if moderate_corr:
                analysis += "### 🔶 中等相关性发现\n"
                for var1, var2, corr in moderate_corr[:5]:  # Limit to top 5
                    direction = "正相关" if corr > 0 else "负相关"
                    analysis += f"- **{var1}** 与 **{var2}**: {corr:.3f} ({direction})\n"
                analysis += "\n"

            if not strong_corr and not moderate_corr:
                analysis += "### ℹ️ 相关性分析结果\n"
                analysis += "- 未发现明显的相关性关系\n"
                analysis += "- 各数值字段相对独立\n"

            # Add insights
            analysis += "### 💡 相关性分析洞察\n"
            if strong_corr:
                analysis += "- 存在强相关性，建议进一步分析因果关系\n"
                analysis += "- 可考虑特征选择或降维处理\n"
            elif moderate_corr:
                analysis += "- 存在中等相关性，可进行分组分析\n"
            else:
                analysis += "- 字段间独立性较好，适合进行多变量分析\n"
                
        else:
            analysis += "### ⚠️ 数值字段不足\n"
            analysis += "当前数据中数值字段少于2个，无法进行相关性分析。\n"
            analysis += "建议检查数据中是否包含足够的数值型字段。\n"

        return analysis

    def _generate_correlation_analysis(self, data: pd.DataFrame) -> str:
        """Generate correlation analysis in Chinese (legacy method for backward compatibility).

        Args:
            data: DataFrame to analyze.

        Returns:
            Correlation analysis as a markdown string.
        """
        return self._generate_enhanced_correlation_analysis(data)

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

    def _handle_enhanced_pandasai_response(
        self, response: Any, sample_data: pd.DataFrame, query: str
    ) -> bool:
        """Enhanced handler for PandasAI response with better Plotly chart detection and display.

        Args:
            response: PandasAI response object.
            sample_data: DataFrame analyzed.
            query: User query.

        Returns:
            Boolean indicating if charts were displayed.
        """
        try:
            charts_found = False
            
            # Clear previous charts
            st.session_state.last_charts = []
            
            # Handle different response types
            if isinstance(response, (go.Figure, dict)):
                if isinstance(response, dict) and "data" in response:
                    fig = go.Figure(response)
                    self._display_plotly_chart(fig, "AI生成图表")
                    charts_found = True
                elif isinstance(response, go.Figure):
                    self._display_plotly_chart(response, "AI生成图表")
                    charts_found = True
                    
            elif isinstance(response, (list, tuple)):
                for item in response:
                    if isinstance(item, go.Figure):
                        self._display_plotly_chart(item, "AI生成图表")
                        charts_found = True
                    elif isinstance(item, dict) and "data" in item:
                        fig = go.Figure(item)
                        self._display_plotly_chart(fig, "AI生成图表")
                        charts_found = True
                        
            # Try to extract charts from string response
            if not charts_found and isinstance(response, str):
                charts_found = self._extract_charts_from_string(response, sample_data, query)
                
            if charts_found:
                st.success(TEXTS["plotly_chart_created"])
                
            return charts_found
            
        except Exception as e:
            logger.warning(f"Failed to handle enhanced PandasAI response: {e}")
            st.warning(f"处理AI响应失败: {e}")
            return False

    def _extract_charts_from_string(self, response_str: str, sample_data: pd.DataFrame, query: str) -> bool:
        """Extract and create charts from string response containing chart code.

        Args:
            response_str: String response that may contain chart code.
            sample_data: DataFrame to use for chart creation.
            query: User query.

        Returns:
            Boolean indicating if charts were created.
        """
        try:
            # Look for plotly code patterns in the response
            plotly_patterns = [
                r'px\.(bar|line|scatter|histogram|box|violin|pie|area|heatmap)\([^)]+\)',
                r'go\.(Figure|Scatter|Bar|Histogram|Box|Violin|Pie|Heatmap)\([^)]+\)',
                r'fig\s*=\s*(px|go)\.[^)]+\)'
            ]
            
            for pattern in plotly_patterns:
                if re.search(pattern, response_str):
                    # Create fallback chart based on query content
                    return self._create_smart_fallback_chart(sample_data, query)
                    
            return False
            
        except Exception as e:
            logger.warning(f"Failed to extract charts from string: {e}")
            return False

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
                self._create_enhanced_fallback_charts(sample_data, query)
                return True
        except Exception as e:
            logger.warning(f"Failed to handle PandasAI response: {e}")
            st.warning(f"处理PandasAI响应失败: {e}")
            self._create_enhanced_fallback_charts(sample_data, query)
            return True

    def _create_enhanced_fallback_charts(self, sample_data: pd.DataFrame, query: str) -> None:
        """Create enhanced fallback charts with better error handling.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        try:
            st.info(TEXTS["fallback_info"])
            
            if self._create_smart_fallback_chart(sample_data, query):
                st.success("已生成备用可视化图表")
            else:
                st.warning(TEXTS["no_visualizable_cols"])
                
        except Exception as e:
            logger.error(f"Failed to create enhanced fallback charts: {e}")
            st.warning(f"创建备用图表失败: {e}")

    def _create_fallback_charts(self, sample_data: pd.DataFrame, query: str) -> None:
        """Create fallback charts when AI analysis fails (legacy method for backward compatibility).

        Args:
            sample_data: DataFrame to visualize.
            query: User query.
        """
        self._create_enhanced_fallback_charts(sample_data, query)

    def _create_smart_fallback_chart(self, sample_data: pd.DataFrame, query: str) -> bool:
        """Create intelligent fallback charts based on query content and data structure.

        Args:
            sample_data: DataFrame to visualize.
            query: User query.

        Returns:
            Boolean indicating if charts were created.
        """
        try:
            query_lower = query.lower()
            numeric_cols = sample_data.select_dtypes(include=["number"]).columns.tolist()
            categorical_cols = sample_data.select_dtypes(include=["object"]).columns.tolist()
            
            charts_created = False
            
            # Duration analysis
            if any(keyword in query_lower for keyword in ["时长", "duration", "时间", "time"]):
                duration_cols = [col for col in sample_data.columns if any(word in col.lower() for word in ["时长", "duration", "时间", "time"])]
                if duration_cols:
                    self._create_duration_chart(sample_data, duration_cols[0])
                    charts_created = True
                elif numeric_cols:
                    self._create_duration_chart(sample_data, numeric_cols[0])
                    charts_created = True
                    
            # Status analysis
            elif any(keyword in query_lower for keyword in ["状态", "status", "完成", "complete"]):
                status_cols = [col for col in sample_data.columns if any(word in col.lower() for word in ["状态", "status", "完成", "complete"])]
                if status_cols:
                    self._create_status_chart(sample_data, status_cols[0])
                    charts_created = True
                elif categorical_cols:
                    self._create_status_chart(sample_data, categorical_cols[0])
                    charts_created = True
                    
            # Distribution analysis
            elif any(keyword in query_lower for keyword in ["分布", "distribution", "统计", "statistics"]):
                if numeric_cols:
                    self._create_distribution_chart(sample_data, numeric_cols[0])
                    charts_created = True
                elif categorical_cols:
                    self._create_distribution_chart(sample_data, categorical_cols[0])
                    charts_created = True
                    
            # Trend analysis
            elif any(keyword in query_lower for keyword in ["趋势", "trend", "变化", "change"]):
                time_cols = self._find_time_columns(sample_data)
                if time_cols:
                    self._create_trend_chart(sample_data, time_cols[0])
                    charts_created = True
                    
            # Default chart
            if not charts_created:
                if numeric_cols:
                    self._create_distribution_chart(sample_data, numeric_cols[0])
                    charts_created = True
                elif categorical_cols:
                    self._create_distribution_chart(sample_data, categorical_cols[0])
                    charts_created = True
                    
            return charts_created
            
        except Exception as e:
            logger.error(f"Failed to create smart fallback chart: {e}")
            return False

    def _create_duration_chart(self, data: pd.DataFrame, column: str) -> None:
        """Create duration analysis chart.

        Args:
            data: DataFrame containing the data.
            column: Column name for duration data.
        """
        try:
            fig = px.histogram(
                data, 
                x=column, 
                title=f"{column}分布分析",
                labels={column: f"{column}（分钟）", "count": "频次"},
                nbins=20,
                color_discrete_sequence=["#1f77b4"]
            )
            fig.update_layout(
                title_x=0.5,
                font=dict(size=12),
                showlegend=True,
                height=400
            )
            self._display_plotly_chart(fig, f"{column}分布")
        except Exception as e:
            logger.error(f"Failed to create duration chart: {e}")

    def _create_status_chart(self, data: pd.DataFrame, column: str) -> None:
        """Create status analysis chart.

        Args:
            data: DataFrame containing the data.
            column: Column name for status data.
        """
        try:
            status_counts = data[column].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title=f"{column}分布分析",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                title_x=0.5,
                font=dict(size=12),
                height=400
            )
            self._display_plotly_chart(fig, f"{column}分布")
        except Exception as e:
            logger.error(f"Failed to create status chart: {e}")

    def _create_distribution_chart(self, data: pd.DataFrame, column: str) -> None:
        """Create distribution analysis chart.

        Args:
            data: DataFrame containing the data.
            column: Column name for the data to analyze.
        """
        try:
            if data[column].dtype in ['int64', 'float64']:
                fig = px.histogram(
                    data, 
                    x=column, 
                    title=f"{column}分布分析",
                    nbins=20,
                    color_discrete_sequence=["#1f77b4"]
                )
            else:
                value_counts = data[column].value_counts()
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"{column}分布分析",
                    labels={"x": column, "y": "数量"},
                    color_discrete_sequence=["#1f77b4"]
                )
            
            fig.update_layout(
                title_x=0.5,
                font=dict(size=12),
                showlegend=True,
                height=400
            )
            self._display_plotly_chart(fig, f"{column}分布")
        except Exception as e:
            logger.error(f"Failed to create distribution chart: {e}")

    def _create_trend_chart(self, data: pd.DataFrame, column: str) -> None:
        """Create trend analysis chart.

        Args:
            data: DataFrame containing the data.
            column: Column name for time data.
        """
        try:
            # Try to convert to datetime if possible
            try:
                data[column] = pd.to_datetime(data[column], errors='coerce')
                data_filtered = data.dropna(subset=[column])
                
                if not data_filtered.empty:
                    # Group by date and count
                    daily_counts = data_filtered.groupby(data_filtered[column].dt.date).size().reset_index()
                    daily_counts.columns = ['date', 'count']
                    
                    fig = px.line(
                        daily_counts,
                        x='date',
                        y='count',
                        title=f"{column}趋势分析",
                        labels={"date": "日期", "count": "数量"},
                        color_discrete_sequence=["#1f77b4"]
                    )
                    fig.update_layout(
                        title_x=0.5,
                        font=dict(size=12),
                        showlegend=True,
                        height=400
                    )
                    self._display_plotly_chart(fig, f"{column}趋势")
                    return
            except:
                pass
                
            # Fallback to simple count
            value_counts = data[column].value_counts().head(10)
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"{column}分布分析",
                labels={"x": column, "y": "数量"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig.update_layout(
                title_x=0.5,
                font=dict(size=12),
                showlegend=True,
                height=400
            )
            self._display_plotly_chart(fig, f"{column}分布")
            
        except Exception as e:
            logger.error(f"Failed to create trend chart: {e}")

    def _display_plotly_chart(self, fig: go.Figure, title: str) -> None:
        """Display a Plotly chart with consistent styling.

        Args:
            fig: Plotly figure object.
            title: Chart title.
        """
        try:
            # Ensure consistent styling
            fig.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=True,
                font=dict(size=12),
                title_x=0.5,
                height=400
            )
            
            # Store in session state
            st.session_state.last_charts.append(fig)
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Failed to display Plotly chart: {e}")
            st.warning(f"显示图表失败: {e}")

    def _extract_text_analysis(self, response: Any) -> str:
        """Extract text analysis from PandasAI response.

        Args:
            response: PandasAI response object.

        Returns:
            Extracted text analysis.
        """
        try:
            if isinstance(response, str):
                return response
            elif hasattr(response, '__str__'):
                return str(response)
            else:
                return "AI分析完成，请查看上方生成的图表。"
        except Exception as e:
            logger.error(f"Failed to extract text analysis: {e}")
            return "AI分析完成，请查看上方生成的图表。"

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
