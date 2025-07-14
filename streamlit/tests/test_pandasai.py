"""
pandasAI 集成演示
展示如何在智慧会议系统中使用 pandasAI 进行智能数据查询

Run with:

```bash
streamlit run tests/test_pandasai.py
```
"""

import sys
import pandas as pd
from pandasai import SmartDataframe
from pandasai.config import Config
from pandasai.llm.openai import OpenAI
import streamlit as st
from faker import Faker
import random
import os
from datetime import datetime, timedelta
import openai
from pandasai.connectors import PandasConnector  # <-- Add this import

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from modules.llm_dashscope import DashScopeOpenAI
from modules.utils import setup_matplotlib_fonts


# Setup fonts
setup_matplotlib_fonts()

# 初始化 Faker
fake = Faker("zh_CN")


def setup_pandasai():
    """设置 pandasAI"""
    try:
        llm = DashScopeOpenAI(
            api_token=os.getenv("DASHSCOPE_API_KEY"), model="qwen-plus"
        )
        return llm
    except Exception as e:
        st.warning(f"pandasAI 设置失败: {e}")
        return None


def create_smart_dataframe(df, llm):
    """创建 SmartDataframe"""
    try:
        config = Config(
            llm=llm,
            verbose=True,
            enable_plotting=True,
            save_charts=True,
            save_charts_path="./charts",
        )
        smart_df = SmartDataframe(df, config=config)
        return smart_df
    except Exception as e:
        st.error(f"创建 SmartDataframe 失败: {e}")
        return None


def generate_demo_data():
    """生成演示数据"""

    # 会议室数据
    rooms_data = []
    room_types = ["会议室", "培训室", "视频会议室", "小型会议室"]
    floors = ["A", "B", "C"]

    for i in range(10):
        floor = random.choice(floors)
        room_num = random.randint(101, 999)
        capacity = random.choice([4, 6, 8, 12, 20, 30])
        room_type = random.choice(room_types)

        rooms_data.append(
            {
                "room_id": i + 1,
                "room_name": f"{floor}{room_num}{room_type}",
                "floor": floor,
                "capacity": capacity,
                "room_type": room_type,
                "equipment": random.choice(
                    ["基础设备", "视频会议设备", "投影设备", "白板设备"]
                ),
                "hourly_rate": random.randint(50, 200),
            }
        )

    # 会议数据
    meetings_data = []
    topics = ["产品评审", "技术讨论", "项目规划", "客户会议", "团队建设", "培训会议"]
    departments = ["研发部", "测试部", "市场部", "产品部", "运营部"]

    for i in range(100):
        start_time = fake.date_time_between(start_date="-60d", end_date="+30d")
        duration = random.choice([30, 60, 90, 120, 180])
        end_time = start_time + timedelta(minutes=duration)

        meetings_data.append(
            {
                "meeting_id": i + 1,
                "title": random.choice(topics),
                "room_id": random.randint(1, 10),
                "department": random.choice(departments),
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration,
                "participants": random.randint(2, 20),
                "status": random.choice(["已预定", "进行中", "已完成", "已取消"]),
                "cost": random.randint(100, 1000),
            }
        )

    # 用户数据
    users_data = []
    roles = ["会议组织者", "会议参与者", "系统管理员"]

    for i in range(30):
        users_data.append(
            {
                "user_id": i + 1,
                "username": fake.user_name(),
                "name": fake.name(),
                "role": random.choice(roles),
                "department": random.choice(departments),
                "email": fake.email(),
                "join_date": fake.date_between(start_date="-365d", end_date="today"),
            }
        )

    return (
        pd.DataFrame(rooms_data),
        pd.DataFrame(meetings_data),
        pd.DataFrame(users_data),
    )


def demo_pandasai_queries():
    """演示 pandasAI 查询功能"""

    st.markdown("## 🤖 pandasAI 智能查询演示")

    # 生成演示数据
    rooms_df, meetings_df, users_df = generate_demo_data()

    # 显示数据概览
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("会议室数量", len(rooms_df))
        st.dataframe(rooms_df.head(), use_container_width=True)

    with col2:
        st.metric("会议记录数", len(meetings_df))
        st.dataframe(meetings_df.head(), use_container_width=True)

    with col3:
        st.metric("用户数量", len(users_df))
        st.dataframe(users_df.head(), use_container_width=True)

    # pandasAI 查询演示
    st.markdown("### 📊 智能数据查询示例")

    # 预设查询示例
    query_examples = [
        "哪个会议室使用频率最高？",
        "各部门的会议时长分布如何？",
        "平均每次会议的成本是多少？",
        "哪些用户最常组织会议？",
        "会议室使用率随时间的变化趋势",
        "按楼层统计会议室使用情况",
    ]

    selected_query = st.selectbox("选择查询示例", query_examples)

    if st.button("🚀 执行智能查询"):
        llm = setup_pandasai()

        # 合并数据以便查询
        merged_df = meetings_df.merge(rooms_df, on="room_id", how="left")

        with st.spinner(f"正在执行智能查询..."):
            # 执行查询
            smart_df = create_smart_dataframe(merged_df, llm)
            if smart_df is not None:
                response = smart_df.chat(selected_query)
                st.success("查询完成！")
                st.markdown("### 📈 查询结果")

                # Handle different response types
                if isinstance(response, pd.DataFrame):
                    st.dataframe(response, use_container_width=True)
                elif isinstance(response, PandasConnector) or "PandasConnector" in str(
                    type(response)
                ):
                    try:
                        df = response.to_dataframe()
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.write(f"Error converting PandasConnector: {e}")
                        st.write(str(response))
                elif hasattr(response, "shape") and hasattr(response, "columns"):
                    st.dataframe(response, use_container_width=True)
                elif isinstance(response, (str, int, float)):
                    st.write(response)
                else:
                    st.write(str(response))
            else:
                st.error("无法创建智能数据框")

    # 自定义查询
    st.markdown("### 🔍 自定义查询")

    custom_query = st.text_area(
        "输入您的查询需求",
        placeholder="例如：显示所有容量大于10人的会议室的使用情况",
        height=100,
    )

    if st.button("🔍 执行自定义查询") and custom_query:
        llm = setup_pandasai()

        try:
            merged_df = meetings_df.merge(rooms_df, on="room_id", how="left")

            with st.spinner("正在执行自定义查询..."):
                smart_df = create_smart_dataframe(merged_df, llm)
                if smart_df is not None:
                    response = smart_df.chat(custom_query)
                    st.success("查询完成！")
                    st.markdown("### 📈 查询结果")

                    # Handle different response types
                    if isinstance(response, pd.DataFrame):
                        st.dataframe(response, use_container_width=True)
                    elif isinstance(
                        response, PandasConnector
                    ) or "PandasConnector" in str(type(response)):
                        try:
                            df = response.to_dataframe()
                            st.dataframe(df, use_container_width=True)
                        except Exception as e:
                            st.write(f"Error converting PandasConnector: {e}")
                            st.write(str(response))
                    elif hasattr(response, "shape") and hasattr(response, "columns"):
                        st.dataframe(response, use_container_width=True)
                    elif isinstance(response, (str, int, float)):
                        st.write(response)
                    else:
                        st.write(str(response))
                else:
                    st.error("无法创建智能数据框")

        except Exception as e:
            st.error(f"查询执行失败: {e}")


def show_advanced_analytics():
    """显示高级分析功能"""

    st.markdown("## 📊 高级数据分析")

    # 生成数据
    rooms_df, meetings_df, users_df = generate_demo_data()
    merged_df = meetings_df.merge(rooms_df, on="room_id", how="left")

    # 分析选项
    analysis_type = st.selectbox(
        "选择分析类型",
        ["会议室使用效率分析", "部门会议模式分析", "成本效益分析", "时间趋势分析"],
    )

    if analysis_type == "会议室使用效率分析":
        st.markdown("### 🏢 会议室使用效率分析")

        # 计算使用效率指标
        room_usage = (
            merged_df.groupby("room_name")
            .agg(
                {
                    "meeting_id": "count",
                    "duration_minutes": "sum",
                    "participants": "sum",
                    "cost": "sum",
                }
            )
            .reset_index()
        )

        room_usage.columns = [
            "会议室",
            "会议次数",
            "总时长(分钟)",
            "总参与人数",
            "总成本",
        ]
        room_usage["平均时长"] = room_usage["总时长(分钟)"] / room_usage["会议次数"]
        room_usage["平均参与人数"] = room_usage["总参与人数"] / room_usage["会议次数"]

        st.dataframe(room_usage, use_container_width=True)

        # 可视化
        import plotly.express as px

        fig = px.bar(room_usage, x="会议室", y="会议次数", title="会议室使用频率")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.scatter(
            room_usage,
            x="平均时长",
            y="平均参与人数",
            size="会议次数",
            hover_data=["会议室"],
            title="会议室效率散点图",
        )
        st.plotly_chart(fig2, use_container_width=True)

    elif analysis_type == "部门会议模式分析":
        st.markdown("### 🏢 部门会议模式分析")

        dept_analysis = (
            merged_df.groupby("department")
            .agg(
                {
                    "meeting_id": "count",
                    "duration_minutes": ["mean", "sum"],
                    "participants": "mean",
                    "cost": "sum",
                }
            )
            .reset_index()
        )

        dept_analysis.columns = [
            "部门",
            "会议次数",
            "平均时长",
            "总时长",
            "平均参与人数",
            "总成本",
        ]

        st.dataframe(dept_analysis, use_container_width=True)

        # 可视化
        import plotly.express as px

        fig = px.pie(
            dept_analysis, values="会议次数", names="部门", title="各部门会议数量分布"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "成本效益分析":
        st.markdown("### 💰 成本效益分析")

        # 计算成本效益指标
        cost_analysis = (
            merged_df.groupby("room_name")
            .agg({"cost": "sum", "duration_minutes": "sum", "participants": "sum"})
            .reset_index()
        )

        cost_analysis["每分钟成本"] = (
            cost_analysis["cost"] / cost_analysis["duration_minutes"]
        )
        cost_analysis["每人成本"] = (
            cost_analysis["cost"] / cost_analysis["participants"]
        )

        st.dataframe(cost_analysis, use_container_width=True)

        # 可视化
        import plotly.express as px

        fig = px.scatter(
            cost_analysis,
            x="每分钟成本",
            y="每人成本",
            size="cost",
            hover_data=["room_name"],
            title="会议室成本效益分析",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "时间趋势分析":
        st.markdown("### 📈 时间趋势分析")

        # 按时间统计
        time_analysis = (
            merged_df.groupby(merged_df["start_time"].dt.date)
            .agg({"meeting_id": "count", "duration_minutes": "sum", "cost": "sum"})
            .reset_index()
        )

        time_analysis.columns = ["日期", "会议次数", "总时长", "总成本"]

        st.dataframe(time_analysis, use_container_width=True)

        # 可视化
        import plotly.express as px

        fig = px.line(time_analysis, x="日期", y="会议次数", title="每日会议数量趋势")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.line(time_analysis, x="日期", y="总成本", title="每日会议成本趋势")
        st.plotly_chart(fig2, use_container_width=True)


def main():
    """主函数"""
    st.set_page_config(
        page_title="pandasAI 智能查询演示",
        page_icon="🤖",
        layout="wide",
    )

    st.title("🤖 pandasAI 智能查询演示")
    st.markdown("展示如何在智慧会议系统中使用 pandasAI 进行智能数据查询")

    # 侧边栏
    st.sidebar.title("功能选择")
    demo_type = st.sidebar.selectbox("选择演示类型", ["智能查询演示", "高级数据分析"])

    if demo_type == "智能查询演示":
        demo_pandasai_queries()
    else:
        show_advanced_analytics()

    # 底部信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 使用说明")
    st.sidebar.markdown(
        """
        1. 确保设置了 `DASHSCOPE_API_KEY` 环境变量
        2. 选择查询示例或输入自定义查询
        3. 点击执行按钮开始查询
        4. 查看智能分析结果
        """
    )


if __name__ == "__main__":
    main()
