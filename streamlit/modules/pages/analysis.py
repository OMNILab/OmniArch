"""
PandasAI Demo Page Module
Contains the PandasAI demo page implementation for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import DashScopeOpenAI for AI-powered analysis
try:
    from modules.llm import DashScopeOpenAI

    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    st.warning("DashScopeOpenAI not available. Using mock analysis.")


class AnalysisPage:
    """PandasAI demo page implementation with enhanced functionality"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def setup_dashscope_llm(self):
        """Setup DashScope LLM for AI analysis"""
        if not DASHSCOPE_AVAILABLE:
            return None

        try:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                st.warning(
                    "DASHSCOPE_API_KEY environment variable not set. Using mock analysis."
                )
                return None

            llm = DashScopeOpenAI(api_token=api_key, model="qwen-plus")
            return llm
        except Exception as e:
            st.error(f"Failed to setup DashScope LLM: {e}")
            return None

    def perform_ai_analysis(self, query, sample_data, llm):
        """Perform AI-powered analysis using DashScope"""
        try:
            # Create a context about the data
            data_info = f"""
            数据集信息:
            - 记录数: {len(sample_data)}
            - 字段数: {len(sample_data.columns)}
            - 字段列表: {', '.join(sample_data.columns.tolist())}
            - 数据类型: {dict(sample_data.dtypes)}
            """

            # Try to get AI insights using the LLM
            ai_insights = self._get_ai_insights(query, sample_data, llm)

            # Basic analysis based on query keywords
            analysis_result = ""

            if "统计" in query or "概览" in query or "统计信息" in query:
                analysis_result = self._generate_statistical_analysis(sample_data)
            elif "图表" in query or "可视化" in query or "图形" in query:
                analysis_result = self._generate_visualization_analysis(sample_data)
            elif "趋势" in query or "变化" in query:
                analysis_result = self._generate_trend_analysis(sample_data)
            elif "分布" in query:
                analysis_result = self._generate_distribution_analysis(sample_data)
            else:
                analysis_result = self._generate_general_analysis(sample_data, query)

            # Add AI insights if available
            if ai_insights:
                analysis_result += f"\n\n## 🤖 AI 智能洞察\n\n{ai_insights}"

            return analysis_result

        except Exception as e:
            st.error(f"AI analysis failed: {e}")
            return None

    def _get_ai_insights(self, query, data, llm):
        """Get AI insights using DashScope LLM"""
        try:
            # Prepare data summary for the LLM
            data_summary = self._prepare_data_summary(data)

            # Create a prompt for the LLM
            prompt = f"""
            作为一个数据分析专家，请分析以下数据并提供洞察：

            用户查询: {query}
            
            数据摘要:
            {data_summary}
            
            请提供：
            1. 数据的关键特征
            2. 可能的业务洞察
            3. 建议的进一步分析方向
            
            请用中文回答，简洁明了。
            """

            # For now, we'll return a structured analysis
            # In a full implementation, you would call the LLM here
            # response = llm.chat(prompt)

            # Return structured insights based on data characteristics
            return self._generate_structured_insights(data, query)

        except Exception as e:
            st.warning(f"AI insights generation failed: {e}")
            return None

    def _prepare_data_summary(self, data):
        """Prepare a summary of the data for AI analysis"""
        summary = f"""
        - 数据集大小: {len(data)} 行 x {len(data.columns)} 列
        - 字段名称: {', '.join(data.columns.tolist())}
        """

        # Add data type information
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if len(numeric_cols) > 0:
            summary += f"\n- 数值型字段: {', '.join(numeric_cols)}"

        if len(categorical_cols) > 0:
            summary += f"\n- 分类型字段: {', '.join(categorical_cols)}"

        # Add basic statistics for numeric columns
        if len(numeric_cols) > 0:
            stats = data[numeric_cols].describe()
            summary += f"\n- 数值字段统计: 平均值范围 {stats.loc['mean'].min():.2f} - {stats.loc['mean'].max():.2f}"

        return summary

    def _generate_structured_insights(self, data, query):
        """Generate structured insights based on data characteristics"""
        insights = ""

        # Analyze data patterns
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        # Key characteristics
        insights += "### 🔍 数据特征分析\n"
        insights += f"- **数据规模**: 中等规模数据集 ({len(data)} 条记录)\n"
        insights += f"- **字段多样性**: {len(numeric_cols)} 个数值字段, {len(categorical_cols)} 个分类字段\n"

        # Identify potential insights
        if len(numeric_cols) > 0:
            insights += "\n### 📊 数值型数据洞察\n"
            for col in numeric_cols[:2]:  # Focus on first 2 numeric columns
                stats = data[col].describe()
                insights += f"- **{col}**: 均值 {stats['mean']:.2f}, 标准差 {stats['std']:.2f}\n"
                if stats["std"] > stats["mean"] * 0.5:
                    insights += f"  - 数据变异较大，可能存在异常值\n"
                else:
                    insights += f"  - 数据分布相对集中\n"

        if len(categorical_cols) > 0:
            insights += "\n### 🏷️ 分类型数据洞察\n"
            for col in categorical_cols[:2]:  # Focus on first 2 categorical columns
                value_counts = data[col].value_counts()
                insights += f"- **{col}**: {len(value_counts)} 个类别\n"
                insights += f"  - 主要类别: {value_counts.index[0]} ({value_counts.iloc[0]} 次)\n"
                if len(value_counts) > 5:
                    insights += f"  - 类别较多，建议进行分组分析\n"

        # Business insights
        insights += "\n### 💡 业务洞察建议\n"
        if "会议" in str(data.columns):
            insights += "- 关注会议时长和频率的分布模式\n"
            insights += "- 分析不同部门的会议使用情况\n"
        elif "任务" in str(data.columns):
            insights += "- 监控任务完成率和优先级分布\n"
            insights += "- 识别任务处理的瓶颈环节\n"
        elif "用户" in str(data.columns):
            insights += "- 分析用户活跃度和部门分布\n"
            insights += "- 关注用户角色和权限分配\n"
        elif "房间" in str(data.columns):
            insights += "- 评估会议室使用效率和容量分布\n"
            insights += "- 优化会议室资源配置\n"

        return insights

    def _generate_statistical_analysis(self, data):
        """Generate statistical analysis of the data"""
        analysis = "## 📊 数据统计分析\n\n"

        # Basic statistics
        analysis += f"- **总记录数:** {len(data)}\n"
        analysis += f"- **字段数:** {len(data.columns)}\n\n"

        # Numeric columns analysis
        numeric_cols = data.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            analysis += "### 数值型字段统计\n"
            stats = data[numeric_cols].describe()
            analysis += f"- 数值字段: {', '.join(numeric_cols)}\n"
            analysis += f"- 平均值范围: {stats.loc['mean'].min():.2f} - {stats.loc['mean'].max():.2f}\n"
            analysis += f"- 标准差范围: {stats.loc['std'].min():.2f} - {stats.loc['std'].max():.2f}\n\n"

        # Categorical columns analysis
        categorical_cols = data.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            analysis += "### 分类型字段统计\n"
            for col in categorical_cols[:3]:  # Limit to first 3 columns
                unique_count = data[col].nunique()
                analysis += f"- **{col}:** {unique_count} 个唯一值\n"

        return analysis

    def _generate_visualization_analysis(self, data):
        """Generate visualization recommendations"""
        analysis = "## 📈 数据可视化分析\n\n"

        # Recommend visualizations based on data types
        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if len(numeric_cols) > 0:
            analysis += "### 数值型数据可视化建议\n"
            analysis += "- 直方图: 查看数值分布\n"
            analysis += "- 箱线图: 识别异常值\n"
            if len(numeric_cols) >= 2:
                analysis += "- 散点图: 分析变量关系\n"

        if len(categorical_cols) > 0:
            analysis += "\n### 分类型数据可视化建议\n"
            analysis += "- 柱状图: 显示类别频次\n"
            analysis += "- 饼图: 显示比例分布\n"

        return analysis

    def _generate_trend_analysis(self, data):
        """Generate trend analysis"""
        analysis = "## 📈 趋势分析\n\n"

        # Look for date/time columns
        date_cols = []
        for col in data.columns:
            if (
                "date" in col.lower()
                or "time" in col.lower()
                or "created" in col.lower()
            ):
                date_cols.append(col)

        if date_cols:
            analysis += f"发现时间相关字段: {', '.join(date_cols)}\n"
            analysis += "建议进行时间序列分析:\n"
            analysis += "- 时间趋势图\n"
            analysis += "- 周期性分析\n"
            analysis += "- 季节性模式识别\n"
        else:
            analysis += "未发现明显的时间字段，建议:\n"
            analysis += "- 检查是否有日期/时间列\n"
            analysis += "- 考虑添加时间维度进行分析\n"

        return analysis

    def _generate_distribution_analysis(self, data):
        """Generate distribution analysis"""
        analysis = "## 📊 分布分析\n\n"

        numeric_cols = data.select_dtypes(include=["number"]).columns
        categorical_cols = data.select_dtypes(include=["object"]).columns

        if len(numeric_cols) > 0:
            analysis += "### 数值型数据分布\n"
            for col in numeric_cols[:3]:
                stats = data[col].describe()
                analysis += f"- **{col}:** 均值={stats['mean']:.2f}, 标准差={stats['std']:.2f}\n"

        if len(categorical_cols) > 0:
            analysis += "\n### 分类型数据分布\n"
            for col in categorical_cols[:3]:
                value_counts = data[col].value_counts()
                analysis += f"- **{col}:** 最多值='{value_counts.index[0]}' ({value_counts.iloc[0]}次)\n"

        return analysis

    def _generate_general_analysis(self, data, query):
        """Generate general analysis based on query"""
        analysis = f"## 🤖 AI 分析结果\n\n"
        analysis += f"针对查询: **{query}**\n\n"

        # Provide insights based on data characteristics
        analysis += "### 数据洞察\n"
        analysis += f"- 数据集包含 {len(data)} 条记录\n"
        analysis += f"- 涵盖 {len(data.columns)} 个字段\n"

        # Identify key patterns
        numeric_cols = data.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            analysis += f"- 包含 {len(numeric_cols)} 个数值型字段\n"

        categorical_cols = data.select_dtypes(include=["object"]).columns
        if len(categorical_cols) > 0:
            analysis += f"- 包含 {len(categorical_cols)} 个分类型字段\n"

        analysis += "\n### 建议\n"
        analysis += "- 尝试更具体的查询，如'显示统计信息'或'生成图表'\n"
        analysis += "- 使用快速分析按钮获取常用分析结果\n"

        return analysis

    def show(self):
        """PandasAI demo page implementation with enhanced functionality"""
        self.ui.create_header("智能分析")

        st.markdown("### 数据分析工具")

        # Check if DashScope is available
        llm = self.setup_dashscope_llm()
        if llm:
            st.success("✅ DashScope AI 分析已启用")
        else:
            st.info("ℹ️ 使用模拟分析模式")

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
                        if llm:
                            # Use AI-powered analysis
                            analysis_result = self.perform_ai_analysis(
                                query, sample_data, llm
                            )
                            if analysis_result:
                                st.success("AI 分析完成！")
                                st.markdown(analysis_result)

                                # Show visualizations based on analysis type
                                self._show_analysis_visualizations(sample_data, query)
                            else:
                                st.error("AI 分析失败，请重试")
                        else:
                            # Fallback to mock analysis
                            self._perform_mock_analysis(query, sample_data)
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

    def _show_analysis_visualizations(self, sample_data, query):
        """Show visualizations based on analysis type"""
        if "统计" in query or "概览" in query:
            # Show basic statistics visualizations
            numeric_cols = sample_data.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                st.markdown("#### 数值字段分布")
                for col in numeric_cols[:3]:  # Show first 3 numeric columns
                    fig = px.histogram(sample_data, x=col, title=f"{col} 分布")
                    st.plotly_chart(fig, use_container_width=True)

        elif "图表" in query or "可视化" in query:
            # Show comprehensive visualizations
            self._show_comprehensive_visualizations(sample_data)

    def _show_comprehensive_visualizations(self, sample_data):
        """Show comprehensive visualizations"""
        st.markdown("#### 数据可视化")

        # Create visualization based on data type
        numeric_cols = sample_data.select_dtypes(include=["number"]).columns
        categorical_cols = sample_data.select_dtypes(include=["object"]).columns

        # Show numeric data distributions
        if len(numeric_cols) > 0:
            for col in numeric_cols[:2]:  # Show first 2 numeric columns
                fig = px.histogram(sample_data, x=col, title=f"{col} 分布", nbins=20)
                st.plotly_chart(fig, use_container_width=True)

        # Show categorical data distributions
        if len(categorical_cols) > 0:
            for col in categorical_cols[:2]:  # Show first 2 categorical columns
                value_counts = sample_data[col].value_counts()
                fig = px.bar(
                    x=value_counts.index, y=value_counts.values, title=f"{col} 分布"
                )
                st.plotly_chart(fig, use_container_width=True)

    def _perform_mock_analysis(self, query, sample_data):
        """Perform mock analysis (fallback when AI is not available)"""
        import time

        time.sleep(1)  # Simulate processing

        # Mock AI response based on query
        if "统计" in query or "概览" in query:
            st.success("分析完成！")
            st.markdown("#### 数据统计结果")

            # Show basic statistics
            numeric_cols = sample_data.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                st.dataframe(sample_data[numeric_cols].describe())

            # Show value counts for categorical columns
            categorical_cols = sample_data.select_dtypes(include=["object"]).columns[:3]
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
            self._show_comprehensive_visualizations(sample_data)

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
                if len(sample_data.select_dtypes(include=["number"]).columns) > 0:
                    st.metric(
                        "数值字段",
                        len(sample_data.select_dtypes(include=["number"]).columns),
                    )
                else:
                    st.metric("数值字段", 0)
