"""
Pages Module
Contains all page implementations for the smart meeting system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from modules.ui_components import UIComponents

class Pages:
    """Contains all page implementations"""
    
    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components
    
    def show_login_page(self):
        """Login page implementation"""
        st.markdown('<h1 class="main-header">智慧会议系统</h1>', unsafe_allow_html=True)
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            
            st.markdown("### 用户登录")
            
            with st.form("login_form"):
                username = st.text_input("用户名", placeholder="请输入用户名")
                password = st.text_input("密码", type="password", placeholder="请输入密码")
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("登录", type="primary")
                with col2:
                    if st.form_submit_button("重置"):
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Handle login outside form
            if submitted:
                if username and password:
                    if self.auth_manager.login(username, password):
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("登录失败，请检查用户名和密码")
                else:
                    st.warning("请输入用户名和密码")
    
    def show_booking_page(self):
        """Smart booking page implementation"""
        self.ui.create_header("智能预定")
        
        # Enhanced booking statistics
        col1, col2, col3, col4 = st.columns(4)
        
        meetings_df = self.data_manager.get_dataframe('meetings')
        rooms_df = self.data_manager.get_dataframe('rooms')
        
        with col1:
            self.ui.create_metric_card("今日会议", str(len(meetings_df[meetings_df['start_time'].dt.date == datetime.now().date()])))
        
        with col2:
            available_rooms = len(rooms_df[rooms_df['status'] == '可用'])
            self.ui.create_metric_card("可用会议室", str(available_rooms))
        
        with col3:
            total_meetings = len(meetings_df)
            self.ui.create_metric_card("总会议数", str(total_meetings))
        
        with col4:
            avg_duration = meetings_df['duration'].mean()
            self.ui.create_metric_card("平均时长", f"{avg_duration:.0f}分钟")
        
        # Room recommendations
        st.markdown("---")
        st.markdown("### 会议室推荐")
        
        self.ui.create_modern_container()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 会议日历")
            
            # Mock calendar data
            calendar_data = pd.DataFrame({
                '时间': ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
                'A301': ['可用', '已预订', '可用', '可用', '已预订', '可用'],
                'A302': ['已预订', '已预订', '可用', '可用', '可用', '可用'],
                'A303': ['可用', '可用', '可用', '已预订', '已预订', '可用']
            })
            
            st.dataframe(calendar_data, use_container_width=True)
        
        with col2:
            st.markdown("#### 推荐会议室")
            
            # Room recommendations
            recommended_rooms = rooms_df.head(3).to_dict('records')
            
            for room in recommended_rooms:
                self.ui.create_room_card(room)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"预定 {room['name']}", key=f"book_{room['id']}"):
                        st.success(f"已预定 {room['name']}")
                with col2:
                    if st.button(f"详情", key=f"details_{room['id']}"):
                        st.info(f"会议室详情: {room['name']} - 容量{room['capacity']}人")
        
        self.ui.close_modern_container()
        
        # Natural language input
        st.markdown("---")
        st.markdown("### 智能预定")
        
        self.ui.create_modern_container()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            meeting_request = st.text_area(
                "请输入会议需求",
                placeholder="例如：明天下午2点需要开一个10人的项目讨论会，需要视频会议设备",
                height=100
            )
        
        with col2:
            st.markdown("")
            st.markdown("")
            if st.button("开始识别", type="primary"):
                if meeting_request:
                    st.success("正在分析您的需求...")
                    
                    # Mock AI analysis
                    st.info("""
                    分析结果：
                    - 时间：明天下午2点
                    - 人数：10人
                    - 类型：项目讨论
                    - 设备需求：视频会议设备
                    - 推荐会议室：A301会议室
                    """)
                else:
                    st.warning("请输入会议需求")
        
        self.ui.close_modern_container()
        
        # Booking form
        st.markdown("---")
        st.markdown("### 预定确认")
        
        self.ui.create_modern_container()
        
        with st.form("booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                meeting_title = st.text_input("会议主题", placeholder="请输入会议主题")
                meeting_date = st.date_input("会议日期", value=datetime.now().date())
                meeting_time = st.time_input("会议时间", value=datetime.now().time())
            
            with col2:
                participants = st.number_input("参与人数", min_value=1, max_value=50, value=10)
                room_selection = st.selectbox("选择会议室", rooms_df['name'].tolist())
                meeting_type = st.selectbox("会议类型", ["项目讨论", "产品评审", "技术分享", "团队会议", "客户会议"])
            
            meeting_description = st.text_area("会议描述", placeholder="请输入会议描述")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                if st.form_submit_button("确认预定", type="primary"):
                    if meeting_title and room_selection:
                        st.success("预定成功！")
                    else:
                        st.error("请填写完整信息")
        
        self.ui.close_modern_container()
    
    def show_minutes_page(self):
        """Meeting minutes page implementation"""
        self.ui.create_header("会议纪要")
        
        # Minutes statistics
        col1, col2, col3, col4 = st.columns(4)
        
        minutes_df = self.data_manager.get_dataframe('minutes')
        
        with col1:
            self.ui.create_metric_card("总纪要数", str(len(minutes_df)))
        
        with col2:
            confirmed_minutes = len(minutes_df[minutes_df['status'] == '已确认'])
            self.ui.create_metric_card("已确认", str(confirmed_minutes))
        
        with col3:
            draft_minutes = len(minutes_df[minutes_df['status'] == '草稿'])
            self.ui.create_metric_card("草稿", str(draft_minutes))
        
        with col4:
            published_minutes = len(minutes_df[minutes_df['status'] == '已发布'])
            self.ui.create_metric_card("已发布", str(published_minutes))
        
        # Upload and transcription
        st.markdown("---")
        st.markdown("### 音频/文本上传")
        
        self.ui.create_modern_container()
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_audio = st.file_uploader("上传音频文件", type=['mp3', 'wav', 'm4a'])
            if uploaded_audio:
                st.success(f"已上传: {uploaded_audio.name}")
        
        with col2:
            uploaded_text = st.file_uploader("上传文本文件", type=['txt', 'docx', 'pdf'])
            if uploaded_text:
                st.success(f"已上传: {uploaded_text.name}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("开始转写", type="primary"):
                st.info("正在转写音频...")
                st.success("转写完成！")
        
        with col2:
            if st.button("生成纪要", type="primary"):
                st.info("正在生成会议纪要...")
                st.success("纪要生成完成！")
        
        self.ui.close_modern_container()
        
        # Minutes preview
        st.markdown("---")
        st.markdown("### 纪要预览")
        
        self.ui.create_modern_container()
        
        # Mock minutes data
        sample_minutes = {
            'title': '项目进度讨论会议纪要',
            'summary': '本次会议主要讨论了当前项目的进展情况，确定了下一步的工作计划和时间节点。',
            'decisions': [
                '确定项目交付时间为下月底',
                '增加测试人员配置',
                '调整技术方案以提升性能'
            ],
            'action_items': [
                '张三负责完成需求文档',
                '李四准备技术方案',
                '王五协调测试资源'
            ]
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 会议摘要")
            st.write(sample_minutes['summary'])
            
            st.markdown("#### 决策事项")
            for i, decision in enumerate(sample_minutes['decisions'], 1):
                st.markdown(f"{i}. {decision}")
        
        with col2:
            st.markdown("#### 行动项")
            for i, action in enumerate(sample_minutes['action_items'], 1):
                st.markdown(f"{i}. {action}")
            
            st.markdown("#### 导出选项")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("导出PDF"):
                    st.success("PDF导出成功")
            with col2:
                if st.button("导出Markdown"):
                    st.success("Markdown导出成功")
        
        self.ui.close_modern_container()
    
    def show_tasks_page(self):
        """Task board page implementation"""
        self.ui.create_header("任务看板")
        
        # Enhanced task statistics with modern metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        tasks_df = self.data_manager.get_dataframe('tasks')
        users_df = self.data_manager.get_dataframe('users')
        
        with col1:
            self.ui.create_metric_card("总任务数", str(len(tasks_df)))
        
        with col2:
            completed_tasks = len(tasks_df[tasks_df['status'] == '完成'])
            self.ui.create_metric_card("已完成", str(completed_tasks))
        
        with col3:
            in_progress = len(tasks_df[tasks_df['status'] == '进行中'])
            self.ui.create_metric_card("进行中", str(in_progress))
        
        with col4:
            pending = len(tasks_df[tasks_df['status'] == '草稿'])
            self.ui.create_metric_card("待处理", str(pending))
        
        # Task board view with modern layout
        st.markdown("---")
        st.markdown("### 任务看板")
        
        # Enhanced department filter
        departments = ['全部'] + list(tasks_df['department'].unique())
        selected_dept = st.selectbox("选择部门", departments)
        
        if selected_dept != '全部':
            filtered_tasks = tasks_df[tasks_df['department'] == selected_dept]
        else:
            filtered_tasks = tasks_df
        
        # Modern task board with cards
        self.ui.create_modern_container()
        
        # Display tasks by department with improved layout
        dept_cols = st.columns(len(filtered_tasks['department'].unique()))
        
        for i, dept in enumerate(filtered_tasks['department'].unique()):
            with dept_cols[i]:
                st.markdown(f"#### {dept}")
                
                dept_tasks = filtered_tasks[filtered_tasks['department'] == dept]
                
                for _, task in dept_tasks.iterrows():
                    assignee = users_df[users_df['id'] == task['assignee_id']]['name'].iloc[0] if len(users_df[users_df['id'] == task['assignee_id']]) > 0 else "未分配"
                    self.ui.create_task_card(task.to_dict(), assignee)
        
        self.ui.close_modern_container()
        
        # Enhanced task statistics chart
        st.markdown("---")
        st.markdown("### 任务统计")
        
        self.ui.create_modern_container()
        
        col1, col2 = st.columns(2)
        
        with col1:
            dept_task_counts = tasks_df['department'].value_counts()
            
            fig = px.bar(
                x=dept_task_counts.index,
                y=dept_task_counts.values,
                title="各部门任务数量",
                labels={'x': '部门', 'y': '任务数量'},
                color=dept_task_counts.values,
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Status distribution pie chart
            status_counts = tasks_df['status'].value_counts()
            
            fig2 = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="任务状态分布",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        self.ui.close_modern_container()
    
    def show_dashboard_page(self):
        """Data dashboard page implementation"""
        self.ui.create_header("数据面板")
        
        # Modern date range selector
        self.ui.create_modern_container()
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("开始日期", value=datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("结束日期", value=datetime.now())
        
        self.ui.close_modern_container()
        
        # Enhanced overall overview with modern metric cards
        st.markdown("### 整体概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        meetings_df = self.data_manager.get_dataframe('meetings')
        rooms_df = self.data_manager.get_dataframe('rooms')
        
        with col1:
            self.ui.create_metric_card("总会议数", str(len(meetings_df)))
        
        with col2:
            avg_duration = meetings_df['duration'].mean()
            self.ui.create_metric_card("平均时长", f"{avg_duration:.0f}分钟")
        
        with col3:
            total_participants = meetings_df['participants'].sum()
            self.ui.create_metric_card("总参与人数", str(total_participants))
        
        with col4:
            total_rooms = len(rooms_df)
            self.ui.create_metric_card("会议室数量", str(total_rooms))
        
        # Enhanced room usage charts
        st.markdown("---")
        st.markdown("### 会议室使用分析")
        
        self.ui.create_modern_container()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 会议室使用频率")
            
            # Room usage heatmap data
            room_usage = meetings_df.groupby('room_id').size().reset_index(name='usage_count')
            room_usage = room_usage.merge(rooms_df[['id', 'name']], left_on='room_id', right_on='id')
            
            fig = px.bar(
                room_usage,
                x='name',
                y='usage_count',
                title="会议室使用频率",
                labels={'name': '会议室', 'usage_count': '使用次数'},
                color='usage_count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                xaxis_tickangle=-45
            )
            
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
                title="会议时长分布",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        self.ui.close_modern_container()
        
        # Enhanced department usage analysis
        st.markdown("---")
        st.markdown("### 部门使用概览")
        
        self.ui.create_modern_container()
        
        # Mock department data with enhanced visualization
        dept_usage = pd.DataFrame({
            'department': ['研发部', '测试部', '市场部', '产品部', '运营部'],
            'meetings_count': [25, 15, 20, 18, 12],
            'total_duration': [1800, 900, 1200, 1080, 720],
            'avg_participants': [8, 6, 10, 7, 5]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                dept_usage,
                x='department',
                y='meetings_count',
                title="各部门会议数量",
                labels={'department': '部门', 'meetings_count': '会议数量'},
                color='meetings_count',
                color_continuous_scale='plasma'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                dept_usage,
                x='department',
                y='total_duration',
                title="各部门会议总时长",
                labels={'department': '部门', 'total_duration': '总时长(分钟)'},
                color='total_duration',
                color_continuous_scale='inferno'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        self.ui.close_modern_container()
        
        # Enhanced historical query with modern interface
        st.markdown("---")
        st.markdown("### 历史查询")
        
        self.ui.create_modern_container()
        
        col1, col2 = st.columns(2)
        
        with col1:
            room_query = st.text_input("会议室名称", placeholder="输入会议室名称")
        
        with col2:
            if st.button("查询", type="primary"):
                if room_query:
                    # Mock query results with enhanced display
                    st.success(f"查询到 {room_query} 的使用记录")
                    
                    # Display mock results with modern table
                    mock_results = pd.DataFrame({
                        '日期': [datetime.now() - timedelta(days=i) for i in range(5)],
                        '会议主题': [f'会议{i+1}' for i in range(5)],
                        '时长(分钟)': [60, 90, 45, 120, 75],
                        '参与人数': [8, 12, 6, 15, 10]
                    })
                    
                    # Use AgGrid for better table display
                    gb = GridOptionsBuilder.from_dataframe(mock_results)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_side_bar()
                    gb.configure_selection('multiple', use_checkbox=True)
                    grid_options = gb.build()
                    
                    grid_response = AgGrid(
                        mock_results,
                        gridOptions=grid_options,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        fit_columns_on_grid_load=True,
                        theme="streamlit",
                        height=300
                    )
                else:
                    st.warning("请输入会议室名称")
        
        self.ui.close_modern_container()
        
        # Enhanced export functionality
        st.markdown("---")
        st.markdown("### 数据导出")
        
        self.ui.create_modern_container()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("导出数据 (CSV)", type="primary"):
                st.success("数据已导出为CSV文件")
        
        with col2:
            if st.button("导出图表 (PNG)", type="primary"):
                st.success("图表已导出为PNG文件")
        
        with col3:
            if st.button("生成报告 (PDF)", type="primary"):
                st.success("报告已生成并导出为PDF文件")
        
        self.ui.close_modern_container()
    
    def show_settings_page(self):
        """System settings page implementation"""
        self.ui.create_header("系统设置")
        
        if not self.auth_manager.is_admin():
            st.error("您没有权限访问此页面")
            return
        
        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs(["用户管理", "组织架构管理", "声纹库", "纪要模板管理"])
        
        with tab1:
            st.markdown("### 用户管理")
            
            users_df = self.data_manager.get_dataframe('users')
            
            # User management interface
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(users_df[['username', 'name', 'department', 'role']], use_container_width=True)
            
            with col2:
                st.markdown("#### 添加用户")
                
                with st.form("add_user_form"):
                    new_username = st.text_input("用户名")
                    new_name = st.text_input("姓名")
                    new_department = st.selectbox("部门", ['研发部', '测试部', '市场部', '产品部', '运营部'])
                    new_role = st.selectbox("角色", ['会议组织者', '会议参与者', '系统管理员'])
                    
                    if st.form_submit_button("添加用户"):
                        if new_username and new_name:
                            st.success("用户添加成功")
                        else:
                            st.error("请填写完整信息")
        
        with tab2:
            st.markdown("### 组织架构管理")
            
            # Mock organization data
            org_data = pd.DataFrame({
                '部门': ['研发部', '测试部', '市场部', '产品部', '运营部'],
                '负责人': ['张三', '李四', '王五', '赵六', '钱七'],
                '人数': [25, 15, 20, 18, 12],
                '状态': ['正常', '正常', '正常', '正常', '正常']
            })
            
            st.dataframe(org_data, use_container_width=True)
        
        with tab3:
            st.markdown("### 声纹库管理")
            st.info("声纹库功能正在开发中...")
        
        with tab4:
            st.markdown("### 纪要模板管理")
            
            # Mock template data
            templates = [
                "标准会议纪要模板",
                "项目评审会议模板",
                "技术分享会议模板",
                "客户会议纪要模板"
            ]
            
            selected_template = st.selectbox("选择模板", templates)
            
            if st.button("预览模板"):
                st.info(f"预览 {selected_template}")
            
            if st.button("编辑模板"):
                st.info(f"编辑 {selected_template}")
            
            if st.button("删除模板"):
                st.warning(f"删除 {selected_template}")
    
    def show_pandasai_demo(self):
        """PandasAI demo page implementation"""
        self.ui.create_header("智能数据分析")
        
        st.markdown("### PandasAI 演示")
        
        # Sample data for demo
        sample_data = pd.DataFrame({
            '会议室': ['A301', 'A302', 'A303', 'B401', 'B402'],
            '使用次数': [25, 18, 22, 15, 12],
            '平均时长': [90, 75, 120, 60, 45],
            '满意度': [4.2, 4.5, 4.1, 4.3, 4.0]
        })
        
        st.markdown("#### 示例数据")
        st.dataframe(sample_data, use_container_width=True)
        
        # Natural language query
        st.markdown("#### 自然语言查询")
        
        query = st.text_input(
            "请输入您的问题",
            placeholder="例如：哪个会议室使用最频繁？",
            value="哪个会议室使用最频繁？"
        )
        
        if st.button("分析", type="primary"):
            if query:
                st.info("正在分析...")
                
                # Mock AI response
                if "使用最频繁" in query:
                    st.success("分析结果：A301会议室使用最频繁，共使用25次")
                elif "时长" in query:
                    st.success("分析结果：A303会议室平均时长最长，为120分钟")
                elif "满意度" in query:
                    st.success("分析结果：A302会议室满意度最高，为4.5分")
                else:
                    st.success("分析完成，请查看结果")
                
                # Show visualization
                fig = px.bar(sample_data, x='会议室', y='使用次数', title="会议室使用频率")
                st.plotly_chart(fig, use_container_width=True) 