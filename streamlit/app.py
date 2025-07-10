import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from faker import Faker
import json
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth

# Initialize Faker for mock data
fake = Faker('zh_CN')

# Page configuration
st.set_page_config(
    page_title="智慧会议系统",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .room-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .task-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Mock data generation functions
def generate_mock_users():
    """Generate mock user data"""
    users = []
    roles = ['会议组织者', '会议参与者', '系统管理员']
    departments = ['研发部', '测试部', '市场部', '产品部', '运营部']
    
    for i in range(20):
        users.append({
            'id': i + 1,
            'username': fake.user_name(),
            'name': fake.name(),
            'role': random.choice(roles),
            'department': random.choice(departments),
            'email': fake.email()
        })
    return users

def generate_mock_rooms():
    """Generate mock room data"""
    rooms = []
    room_types = ['会议室', '培训室', '视频会议室', '小型会议室']
    floors = ['A', 'B', 'C']
    
    for i in range(15):
        floor = random.choice(floors)
        room_num = random.randint(101, 999)
        capacity = random.choice([4, 6, 8, 12, 20, 30])
        room_type = random.choice(room_types)
        
        rooms.append({
            'id': i + 1,
            'name': f'{floor}{room_num}{room_type}',
            'floor': floor,
            'capacity': capacity,
            'type': room_type,
            'equipment': random.choice(['基础设备', '视频会议设备', '投影设备', '白板设备']),
            'status': random.choice(['可用', '维护中', '已预定'])
        })
    return rooms

def generate_mock_meetings():
    """Generate mock meeting data"""
    meetings = []
    topics = ['产品评审', '技术讨论', '项目规划', '客户会议', '团队建设', '培训会议']
    
    for i in range(50):
        start_time = fake.date_time_between(start_date='-30d', end_date='+30d')
        duration = random.choice([30, 60, 90, 120])
        end_time = start_time + timedelta(minutes=duration)
        
        meetings.append({
            'id': i + 1,
            'title': random.choice(topics),
            'room_id': random.randint(1, 15),
            'organizer_id': random.randint(1, 20),
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'participants': random.randint(2, 15),
            'status': random.choice(['已预定', '进行中', '已完成', '已取消'])
        })
    return meetings

def generate_mock_tasks():
    """Generate mock task data"""
    tasks = []
    task_types = ['准备报告', '代码审查', '测试用例', '文档编写', '会议纪要', '项目跟进']
    statuses = ['草稿', '确认', '进行中', '完成']
    
    for i in range(30):
        tasks.append({
            'id': i + 1,
            'title': f'{random.choice(task_types)} - {fake.sentence(nb_words=3)}',
            'assignee_id': random.randint(1, 20),
            'department': random.choice(['研发部', '测试部', '市场部', '产品部']),
            'deadline': fake.date_between(start_date='today', end_date='+30d'),
            'status': random.choice(statuses),
            'priority': random.choice(['高', '中', '低']),
            'description': fake.text(max_nb_chars=100)
        })
    return tasks

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'mock_data' not in st.session_state:
    st.session_state.mock_data = {
        'users': generate_mock_users(),
        'rooms': generate_mock_rooms(),
        'meetings': generate_mock_meetings(),
        'tasks': generate_mock_tasks()
    }

# Authentication function
def login_page():
    """Login page implementation"""
    st.markdown('<h1 class="main-header">智慧会议系统</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 用户登录")
        
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            submit_button = st.form_submit_button("登录")
            
            if submit_button:
                # Mock authentication - accept any non-empty credentials
                if username and password:
                    # Find user in mock data
                    user = next((u for u in st.session_state.mock_data['users'] if u['username'] == username), None)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.current_user = user
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        # For demo purposes, create a demo user if username doesn't exist
                        demo_user = {
                            'id': 999,
                            'username': username,
                            'name': f'演示用户 ({username})',
                            'role': '会议组织者',
                            'department': '演示部门',
                            'email': f'{username}@demo.com'
                        }
                        st.session_state.authenticated = True
                        st.session_state.current_user = demo_user
                        st.success("登录成功！")
                        st.rerun()
                else:
                    st.error("请输入用户名和密码")
        
        # Demo credentials
        st.info("演示模式：输入任意用户名和密码即可登录，系统会自动创建演示用户")

# Main application
def main_app():
    """Main application after authentication"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 导航菜单")
        
        selected = option_menu(
            menu_title=None,
            options=["智能预定", "会议纪要", "任务看板", "数据面板", "系统设置"],
            icons=["calendar", "file-text", "check-square", "bar-chart", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        
        # User info
        if st.session_state.current_user:
            st.markdown("---")
            st.markdown(f"**当前用户：** {st.session_state.current_user['name']}")
            st.markdown(f"**部门：** {st.session_state.current_user['department']}")
            st.markdown(f"**角色：** {st.session_state.current_user['role']}")
            
            if st.button("退出登录"):
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.rerun()
    
    # Main content area
    if selected == "智能预定":
        show_booking_page()
    elif selected == "会议纪要":
        show_minutes_page()
    elif selected == "任务看板":
        show_tasks_page()
    elif selected == "数据面板":
        show_dashboard_page()
    elif selected == "系统设置":
        show_settings_page()

def show_booking_page():
    """Smart booking page implementation"""
    st.markdown('<h1 class="main-header">智能预定</h1>', unsafe_allow_html=True)
    
    # Calendar and recommendation layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 会议日历")
        
        # Date selector
        selected_date = st.date_input("选择日期", value=datetime.now())
        
        # Room availability calendar
        st.markdown("#### 会议室可用状态")
        
        # Create a simple calendar view
        rooms_df = pd.DataFrame(st.session_state.mock_data['rooms'])
        meetings_df = pd.DataFrame(st.session_state.mock_data['meetings'])
        
        # Filter meetings for selected date
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        day_meetings = meetings_df[
            meetings_df['start_time'].dt.date == selected_date
        ]
        
        # Display room status
        for room in st.session_state.mock_data['rooms']:
            room_meetings = day_meetings[day_meetings['room_id'] == room['id']]
            
            if len(room_meetings) > 0:
                status = "已占用"
                meeting_info = f" - {room_meetings.iloc[0]['title']}"
            else:
                status = "可用"
                meeting_info = ""
            
            st.markdown(f"**{room['name']}** ({room['capacity']}人) - {status}{meeting_info}")
    
    with col2:
        st.markdown("### 智能推荐")
        
        # Mock recommendations
        recommendations = []
        for room in random.sample(st.session_state.mock_data['rooms'], 3):
            match_score = random.randint(70, 95)
            recommendations.append({
                'room': room,
                'match_score': match_score,
                'description': f"容纳{room['capacity']}人，{room['equipment']}",
                'deviation': random.choice(['', '人数略超', '时间冲突'])
            })
        
        for rec in recommendations:
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>{rec['room']['name']}</h4>
                <p>匹配度: {rec['match_score']}%</p>
                <div style="background: rgba(255,255,255,0.3); height: 10px; border-radius: 5px;">
                    <div style="background: white; height: 100%; width: {rec['match_score']}%; border-radius: 5px;"></div>
                </div>
                <p>{rec['description']}</p>
                {f'<p style="color: #ffd700;">⚠️ {rec["deviation"]}</p>' if rec['deviation'] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"确认预定 {rec['room']['name']}", key=f"book_{rec['room']['id']}"):
                st.success(f"已预定 {rec['room']['name']}")
    
    # Natural language input
    st.markdown("---")
    st.markdown("### 自然语言输入")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Voice input button outside form
        voice_button = st.button("语音输入")
        
        with st.form("nlp_form"):
            user_input = st.text_area(
                "请输入会议需求",
                placeholder="例如：明天下午2点需要开一个10人的产品评审会议，需要视频会议设备",
                height=100
            )
            
            submit_button = st.form_submit_button("提交需求")
            
            if submit_button and user_input:
                st.success("需求已提交，正在为您推荐会议室...")
                # Simulate processing
                with st.spinner("正在分析需求..."):
                    st.info("基于您的需求，推荐以下会议室：")
                    # Show recommendations based on input
        
        # Handle voice button click outside form
        if voice_button:
            st.info("语音输入功能开发中...")

def show_minutes_page():
    """Meeting minutes page implementation"""
    st.markdown('<h1 class="main-header">会议纪要</h1>', unsafe_allow_html=True)
    
    # File upload section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 音频/文本上传")
        uploaded_file = st.file_uploader(
            "选择音频或文本文件",
            type=['mp3', 'wav', 'txt', 'docx'],
            help="支持音频文件转写或直接上传文本文件"
        )
        
        if uploaded_file:
            st.success(f"文件 {uploaded_file.name} 上传成功")
    
    with col2:
        st.markdown("### 实时转写")
        if st.button("开始实时转写", type="primary"):
            st.info("正在连接音频设备...")
            # Mock real-time transcription
    
    # Minutes preview
    st.markdown("---")
    st.markdown("### 会议纪要预览")
    
    # Mock meeting minutes
    minutes_data = {
        'summary': '本次会议主要讨论了Q4产品规划，确定了新功能开发优先级，并分配了相关任务。',
        'decisions': [
            '确定新功能A的开发优先级为高',
            '分配张三负责功能B的开发',
            '下周三进行技术评审'
        ],
        'speakers': [
            {'time': '14:00', 'speaker': '张三', 'content': '大家好，今天我们讨论Q4的产品规划'},
            {'time': '14:05', 'speaker': '李四', 'content': '我建议优先开发功能A'},
            {'time': '14:15', 'speaker': '王五', 'content': '同意，功能A确实更重要'}
        ]
    }
    
    # Summary section
    st.markdown("#### 会议摘要")
    st.info(minutes_data['summary'])
    
    # Decisions section
    st.markdown("#### 决策要点")
    for decision in minutes_data['decisions']:
        st.markdown(f"- {decision}")
    
    # Speakers section
    st.markdown("#### 发言记录")
    for speaker in minutes_data['speakers']:
        st.markdown(f"**{speaker['time']} - {speaker['speaker']}:** {speaker['content']}")
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("导出PDF"):
            st.success("PDF导出成功")
    
    with col2:
        if st.button("导出Markdown"):
            st.success("Markdown导出成功")

def show_tasks_page():
    """Task board page implementation"""
    st.markdown('<h1 class="main-header">任务看板</h1>', unsafe_allow_html=True)
    
    # Task statistics
    col1, col2, col3, col4 = st.columns(4)
    
    tasks_df = pd.DataFrame(st.session_state.mock_data['tasks'])
    users_df = pd.DataFrame(st.session_state.mock_data['users'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>总任务数</h3>
            <h2>{len(tasks_df)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        completed_tasks = len(tasks_df[tasks_df['status'] == '完成'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>已完成</h3>
            <h2>{completed_tasks}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        in_progress = len(tasks_df[tasks_df['status'] == '进行中'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>进行中</h3>
            <h2>{in_progress}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pending = len(tasks_df[tasks_df['status'] == '草稿'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>待处理</h3>
            <h2>{pending}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Task board view
    st.markdown("---")
    st.markdown("### 任务看板")
    
    # Department filter
    departments = ['全部'] + list(tasks_df['department'].unique())
    selected_dept = st.selectbox("选择部门", departments)
    
    if selected_dept != '全部':
        filtered_tasks = tasks_df[tasks_df['department'] == selected_dept]
    else:
        filtered_tasks = tasks_df
    
    # Display tasks by department
    dept_cols = st.columns(len(filtered_tasks['department'].unique()))
    
    for i, dept in enumerate(filtered_tasks['department'].unique()):
        with dept_cols[i]:
            st.markdown(f"#### {dept}")
            
            dept_tasks = filtered_tasks[filtered_tasks['department'] == dept]
            
            for _, task in dept_tasks.iterrows():
                assignee = users_df[users_df['id'] == task['assignee_id']]['name'].iloc[0] if len(users_df[users_df['id'] == task['assignee_id']]) > 0 else "未分配"
                
                st.markdown(f"""
                <div class="task-card">
                    <h5>{task['title']}</h5>
                    <p><strong>负责人:</strong> {assignee}</p>
                    <p><strong>截止时间:</strong> {task['deadline'].strftime('%Y-%m-%d')}</p>
                    <p><strong>状态:</strong> {task['status']}</p>
                    <p><strong>优先级:</strong> {task['priority']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Task statistics chart
    st.markdown("---")
    st.markdown("### 任务统计")
    
    dept_task_counts = tasks_df['department'].value_counts()
    
    fig = px.bar(
        x=dept_task_counts.index,
        y=dept_task_counts.values,
        title="各部门任务数量",
        labels={'x': '部门', 'y': '任务数量'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_dashboard_page():
    """Data dashboard page implementation"""
    st.markdown('<h1 class="main-header">数据面板</h1>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("开始日期", value=datetime.now() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("结束日期", value=datetime.now())
    
    # Overall overview
    st.markdown("### 整体概览")
    
    col1, col2, col3 = st.columns(3)
    
    meetings_df = pd.DataFrame(st.session_state.mock_data['meetings'])
    rooms_df = pd.DataFrame(st.session_state.mock_data['rooms'])
    
    with col1:
        total_meetings = len(meetings_df)
        st.metric("总会议数", total_meetings)
    
    with col2:
        avg_duration = meetings_df['duration'].mean()
        st.metric("平均会议时长", f"{avg_duration:.0f}分钟")
    
    with col3:
        total_participants = meetings_df['participants'].sum()
        st.metric("总参与人数", total_participants)
    
    # Room usage charts
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 会议室使用情况")
        
        # Room usage heatmap data
        room_usage = meetings_df.groupby('room_id').size().reset_index(name='usage_count')
        room_usage = room_usage.merge(rooms_df[['id', 'name']], left_on='room_id', right_on='id')
        
        fig = px.bar(
            room_usage,
            x='name',
            y='usage_count',
            title="会议室使用频率",
            labels={'name': '会议室', 'usage_count': '使用次数'}
        )
        fig.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 会议时长分布")
        
        duration_bins = [0, 30, 60, 90, 120, 150, 180]
        duration_labels = ['0-30min', '30-60min', '60-90min', '90-120min', '120-150min', '150-180min']
        
        meetings_df['duration_bin'] = pd.cut(meetings_df['duration'], bins=duration_bins, labels=duration_labels)
        duration_dist = meetings_df['duration_bin'].value_counts().sort_index()
        
        fig = px.pie(
            values=duration_dist.values,
            names=duration_dist.index,
            title="会议时长分布"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Department usage
    st.markdown("---")
    st.markdown("### 部门使用概览")
    
    # Mock department data
    dept_usage = pd.DataFrame({
        'department': ['研发部', '测试部', '市场部', '产品部', '运营部'],
        'meetings_count': [25, 15, 20, 18, 12],
        'total_duration': [1800, 900, 1200, 1080, 720]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            dept_usage,
            x='department',
            y='meetings_count',
            title="各部门会议数量",
            labels={'department': '部门', 'meetings_count': '会议数量'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            dept_usage,
            x='department',
            y='total_duration',
            title="各部门会议总时长",
            labels={'department': '部门', 'total_duration': '总时长(分钟)'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Historical query
    st.markdown("---")
    st.markdown("### 历史查询")
    
    col1, col2 = st.columns(2)
    
    with col1:
        room_query = st.text_input("会议室名称", placeholder="输入会议室名称")
    
    with col2:
        if st.button("查询"):
            if room_query:
                # Mock query results
                st.success(f"查询到 {room_query} 的使用记录")
                
                # Display mock results
                mock_results = pd.DataFrame({
                    '日期': [datetime.now() - timedelta(days=i) for i in range(5)],
                    '会议主题': [f'会议{i+1}' for i in range(5)],
                    '时长(分钟)': [60, 90, 45, 120, 75],
                    '参与人数': [8, 12, 6, 15, 10]
                })
                
                st.dataframe(mock_results, use_container_width=True)
            else:
                st.warning("请输入会议室名称")
    
    # Export functionality
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("导出数据 (CSV)"):
            st.success("数据已导出为CSV文件")
    
    with col2:
        if st.button("导出图表 (PNG)"):
            st.success("图表已导出为PNG文件")

def show_settings_page():
    """System settings page implementation"""
    st.markdown('<h1 class="main-header">系统设置</h1>', unsafe_allow_html=True)
    
    # Check if user is admin
    if st.session_state.current_user and st.session_state.current_user['role'] == '系统管理员':
        
        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs(["用户管理", "组织架构", "声纹库", "纪要模板"])
        
        with tab1:
            st.markdown("### 用户管理")
            
            # User table
            users_df = pd.DataFrame(st.session_state.mock_data['users'])
            st.dataframe(
                users_df[['username', 'name', 'role', 'department', 'email']],
                use_container_width=True
            )
            
            # Add new user form
            with st.expander("添加新用户"):
                with st.form("add_user"):
                    new_username = st.text_input("用户名")
                    new_name = st.text_input("姓名")
                    new_role = st.selectbox("角色", ['会议组织者', '会议参与者', '系统管理员'])
                    new_dept = st.selectbox("部门", ['研发部', '测试部', '市场部', '产品部', '运营部'])
                    new_email = st.text_input("邮箱")
                    
                    if st.form_submit_button("添加用户"):
                        st.success("用户添加成功")
        
        with tab2:
            st.markdown("### 组织架构管理")
            
            # Department structure
            departments = ['研发部', '测试部', '市场部', '产品部', '运营部']
            
            for dept in departments:
                with st.expander(dept):
                    st.markdown(f"**部门负责人:** {fake.name()}")
                    st.markdown(f"**部门人数:** {random.randint(5, 20)}人")
                    st.markdown(f"**下属团队:** 团队A, 团队B, 团队C")
        
        with tab3:
            st.markdown("### 声纹库管理")
            st.info("声纹库功能在PoC版本中暂未实现")
            
            # Mock voice print data
            voice_prints = [
                {'user': '张三', 'status': '已录入', 'quality': '优秀'},
                {'user': '李四', 'status': '已录入', 'quality': '良好'},
                {'user': '王五', 'status': '待录入', 'quality': '-'}
            ]
            
            st.dataframe(pd.DataFrame(voice_prints), use_container_width=True)
        
        with tab4:
            st.markdown("### 纪要模板管理")
            
            # Template list
            templates = [
                '标准会议纪要模板',
                '产品评审会议模板',
                '技术讨论会议模板',
                '项目规划会议模板'
            ]
            
            selected_template = st.selectbox("选择模板", templates)
            
            if selected_template:
                st.markdown("#### 模板预览")
                st.markdown("""
                # 会议纪要
                
                **会议主题:** [主题]
                **会议时间:** [时间]
                **参会人员:** [人员列表]
                
                ## 会议内容
                [会议内容记录]
                
                ## 决策要点
                - [决策1]
                - [决策2]
                
                ## 任务分配
                - [ ] [任务1] - 负责人：[姓名] - 截止时间：[日期]
                - [ ] [任务2] - 负责人：[姓名] - 截止时间：[日期]
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("编辑模板"):
                        st.info("模板编辑功能开发中...")
                
                with col2:
                    if st.button("导出模板"):
                        st.success("模板导出成功")
    
    else:
        st.error("您没有访问系统设置的权限，需要管理员权限。")

# Main application flow
if not st.session_state.authenticated:
    login_page()
else:
    main_app() 