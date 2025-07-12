# 智慧会议系统数据模型说明

## 概述

本文档描述了智慧会议系统的数据模型设计，包含了模拟数据的结构和使用方法。系统基于三栋智能大厦的场景，提供会议室智能推荐、预订、纪要生成和任务管理等功能。

## 系统架构

### 建筑布局
- **智慧大厦A座**: 主要承载研发和技术团队，15层，8个会议室
- **智慧大厦B座**: 主要承载产品和运营团队，12层，7个会议室  
- **智慧大厦C座**: 主要承载市场和销售团队，10层，6个会议室

### 部门分布
- **A座**: 研发部、测试部、架构部
- **B座**: 产品部、运营部、设计部、人事部
- **C座**: 市场部、销售部、财务部

## 数据模型

### 1. 建筑信息 (buildings.csv)
```csv
- building_id: 建筑ID
- building_name: 建筑中文名称
- building_name_en: 建筑英文名称
- floor_count: 楼层数量
- total_rooms: 会议室总数
- address: 建筑地址
- description: 建筑描述
```

### 2. 会议室信息 (meeting_rooms.csv)
```csv
- room_id: 会议室ID
- room_name: 会议室中文名称
- room_name_en: 会议室英文名称  
- building_id: 所属建筑ID
- floor: 楼层
- capacity: 容纳人数 (3-12人)
- room_type: 会议室类型
- status: 状态 (可用/维护中/已预订)
- has_screen: 是否有显示屏 (1/0)
- has_phone: 是否有电话 (1/0)
- has_whiteboard: 是否有白板 (1/0)
- has_projector: 是否有投影仪 (1/0)
- equipment_notes: 设备说明
```

### 3. 部门信息 (departments.csv)
```csv
- department_id: 部门ID
- department_name: 部门中文名称
- department_name_en: 部门英文名称
- building_id: 所在建筑ID
- floor_location: 所在楼层
- head_name: 部门负责人
- employee_count: 员工数量
- description: 部门描述
```

### 4. 用户信息 (users.csv)
```csv
- user_id: 用户ID
- username: 用户名
- password: 密码
- name: 真实姓名
- email: 邮箱
- phone: 电话
- department_id: 部门ID
- role: 角色 (会议组织者/会议参与者/系统管理员)
- permission_level: 权限级别
- is_active: 是否活跃
- created_date: 创建日期
- last_login: 最后登录时间
```

### 5. 会议预订 (bookings.csv)
```csv
- booking_id: 预订ID
- room_id: 会议室ID
- organizer_id: 组织者ID
- meeting_title: 会议标题
- meeting_type: 会议类型
- start_datetime: 开始时间
- end_datetime: 结束时间
- duration_minutes: 持续时间(分钟)
- participant_count: 参与人数
- status: 状态 (已完成/已确认/待确认)
- created_datetime: 创建时间
- natural_language_request: 自然语言需求
- ai_match_score: AI匹配分数
- notes: 备注
```

### 6. 会议纪要 (meeting_minutes.csv)
```csv
- minute_id: 纪要ID
- booking_id: 对应预订ID
- meeting_title: 会议标题
- summary: 会议摘要
- key_decisions: 关键决策
- action_items: 行动项
- attendees: 参会人员
- created_datetime: 创建时间
- updated_datetime: 更新时间
- status: 状态 (已发布/草稿/已确认)
- duration_minutes: 会议时长
- transcript_available: 是否有录音转写
```

### 7. 任务管理 (tasks.csv)
```csv
- task_id: 任务ID
- title: 任务标题
- description: 任务描述
- assignee_id: 负责人ID
- department_id: 部门ID
- priority: 优先级 (高/中/低)
- status: 状态 (完成/进行中/待处理)
- deadline: 截止日期
- created_datetime: 创建时间
- updated_datetime: 更新时间
- booking_id: 关联预订ID
- minute_id: 关联纪要ID
- estimated_hours: 预估工时
- actual_hours: 实际工时
- notes: 备注
```

### 8. 预订统计 (booking_statistics.csv)
```csv
- stat_id: 统计ID
- stat_type: 统计类型 (room_monthly/department_monthly/user_monthly)
- stat_period: 统计周期
- room_id: 会议室ID (可选)
- department_id: 部门ID (可选)
- user_id: 用户ID (可选)
- booking_count: 预订次数
- total_duration_minutes: 总时长
- avg_duration_minutes: 平均时长
- utilization_rate: 利用率
- peak_usage_hour: 高峰时段
- most_used_day: 最常用日期
- created_date: 创建日期
```

### 9. 用户需求 (user_requirements.csv)
```csv
- requirement_id: 需求ID
- user_id: 用户ID
- original_request: 原始自然语言请求
- parsed_datetime: 解析出的时间
- parsed_capacity: 解析出的人数
- parsed_duration: 解析出的时长
- parsed_equipment: 解析出的设备需求
- parsed_location: 解析出的位置需求
- parsed_meeting_type: 解析出的会议类型
- ai_analysis: AI分析结果
- recommended_rooms: 推荐会议室ID列表
- match_score: 匹配分数
- booking_id: 关联预订ID
- created_datetime: 创建时间
- status: 状态 (已预订/已确认/待确认/待匹配)
```

## 数据特点

### 1. 真实性
- 所有数据都基于实际企业场景设计
- 人员分布、会议类型、时间安排都符合真实办公环境
- 设备配置和会议室容量设计合理

### 2. 完整性
- 涵盖了智慧会议系统的所有核心功能
- 数据之间有完整的关联关系
- 支持完整的业务流程演示

### 3. 多样性
- 包含各种类型的会议室和设备配置
- 涵盖不同规模和类型的会议
- 包含多种用户角色和权限

### 4. 时效性
- 包含历史数据、当前数据和未来数据
- 支持统计分析和趋势预测
- 数据状态变化反映真实业务流程

## 使用说明

### 1. 数据加载
```python
# 在data_manager.py中加载CSV数据
import pandas as pd

buildings_df = pd.read_csv('streamlit/mock/buildings.csv')
rooms_df = pd.read_csv('streamlit/mock/meeting_rooms.csv')
departments_df = pd.read_csv('streamlit/mock/departments.csv')
users_df = pd.read_csv('streamlit/mock/users.csv')
bookings_df = pd.read_csv('streamlit/mock/bookings.csv')
minutes_df = pd.read_csv('streamlit/mock/meeting_minutes.csv')
tasks_df = pd.read_csv('streamlit/mock/tasks.csv')
statistics_df = pd.read_csv('streamlit/mock/booking_statistics.csv')
requirements_df = pd.read_csv('streamlit/mock/user_requirements.csv')
```

### 2. 数据查询示例
```python
# 查询可用会议室
available_rooms = rooms_df[rooms_df['status'] == '可用']

# 查询某部门的预订统计
dept_stats = statistics_df[
    (statistics_df['stat_type'] == 'department_monthly') & 
    (statistics_df['department_id'] == 1)
]

# 查询用户的自然语言需求
user_requests = requirements_df[requirements_df['user_id'] == 1]
```

### 3. 业务逻辑示例
```python
# AI会议室推荐逻辑
def recommend_rooms(capacity, equipment_needed, location_preference=None):
    # 根据容量筛选
    suitable_rooms = rooms_df[
        (rooms_df['capacity'] >= capacity) & 
        (rooms_df['status'] == '可用')
    ]
    
    # 根据设备需求筛选
    if '投影仪' in equipment_needed:
        suitable_rooms = suitable_rooms[suitable_rooms['has_projector'] == 1]
    
    # 根据位置偏好筛选
    if location_preference:
        suitable_rooms = suitable_rooms[
            suitable_rooms['building_id'] == location_preference
        ]
    
    return suitable_rooms
```

## 扩展说明

### 1. 自定义数据
- 可以根据实际需求调整CSV文件内容
- 可以添加新的数据字段
- 可以增加更多的模拟数据

### 2. 数据验证
- 建议在加载数据后进行完整性检查
- 验证外键关系的完整性
- 检查数据格式的正确性

### 3. 性能优化
- 对于大量数据，建议使用数据库
- 可以考虑添加索引优化查询性能
- 使用缓存机制提高响应速度

## 注意事项

1. **数据一致性**: 确保关联数据的ID对应关系正确
2. **时间格式**: 统一使用ISO 8601格式 (YYYY-MM-DD HH:MM:SS)
3. **中文支持**: 所有显示数据都使用中文，内部字段使用英文
4. **权限控制**: 注意用户权限和角色的正确设置
5. **数据更新**: 定期更新统计数据和状态信息

## 联系方式

如有问题或建议，请联系开发团队。