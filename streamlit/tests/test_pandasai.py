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

from pandasai import Agent
import pandasai as pai
import streamlit as st
from faker import Faker
import random
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from modules.llm import DashScopeOpenAI
from modules.plots import setup_matplotlib_fonts


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


def create_pandasai_agent(df, llm):
    try:
        pai.config.set(
            {
                "llm": llm,
                "verbose": False,
                "max_retries": 3,
                "enforce_privacy": True,
                "enable_logging": True,
                "enable_plotting": True,
                "save_charts": True,
                "save_charts_path": "./charts",
            }
        )
        agent = Agent([pai.DataFrame(df)])
        return agent
    except Exception as e:
        st.error(f"创建 pandasAI Agent 失败: {e}")
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
            # 执行查询 - 使用 Agent 替代 SmartDataframe
            agent = create_pandasai_agent(merged_df, llm)
            if agent is not None:
                response = agent.chat(selected_query)
                st.success("查询完成！")
                st.markdown("### 📈 查询结果")

                # Handle different response types for pandasai 3.0
                if isinstance(response, pd.DataFrame):
                    st.dataframe(response, use_container_width=True)
                elif hasattr(response, "shape") and hasattr(response, "columns"):
                    st.dataframe(response, use_container_width=True)
                elif isinstance(response, (str, int, float)):
                    st.write(response)
                else:
                    st.write(str(response))
            else:
                st.error("无法创建 pandasAI Agent")

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
                agent = create_pandasai_agent(merged_df, llm)
                if agent is not None:
                    response = agent.chat(custom_query)
                    st.success("查询完成！")
                    st.markdown("### 📈 查询结果")

                    # Handle different response types for pandasai 3.0
                    if isinstance(response, pd.DataFrame):
                        st.dataframe(response, use_container_width=True)
                    elif hasattr(response, "shape") and hasattr(response, "columns"):
                        st.dataframe(response, use_container_width=True)
                    elif isinstance(response, (str, int, float)):
                        st.write(response)
                    else:
                        st.write(str(response))
                else:
                    st.error("无法创建 pandasAI Agent")

        except Exception as e:
            st.error(f"查询执行失败: {e}")


def main():
    """主函数"""
    st.set_page_config(
        page_title="pandasAI 智能查询演示",
        page_icon="🤖",
        layout="wide",
    )

    st.title("🤖 pandasAI 智能查询演示")
    st.markdown("展示如何在智慧会议系统中使用 pandasAI 进行智能数据查询")

    demo_pandasai_queries()

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
