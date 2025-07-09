# 📡 智慧会议 PoC RESTful API 规范（v1）

- 基础路径：`/api/v1`
- 请求格式：`application/json`（除上传接口使用 multipart/form-data）
- 返回格式：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
````

---

## 🔐 1. 用户与权限管理

### POST `/auth/login`

用户登录，返回 JWT Token

#### 请求体

```json
{
  "username": "alice",
  "password": "123456"
}
```

#### 返回体

```json
{
  "token": "eyJhbGciOi...xxx"
}
```

---

### GET `/auth/me`

获取当前用户信息

#### 返回体

```json
{
  "user_id": "u001",
  "username": "alice",
  "role": "organizer",
  "department": "研发部"
}
```

---

## 📅 2. 会议室推荐与预定模块

### POST `/meeting/intent`

解析自然语言输入 → 抽取会议预定参数

#### 请求体

```json
{
  "input_text": "明天下午三点，10人，A栋，需要视频会议"
}
```

#### 返回体

```json
{
  "datetime": "2025-07-10T15:00:00",
  "participants": 10,
  "location": "A栋",
  "requirements": ["视频会议"]
}
```

---

### POST `/meeting/recommend`

推荐匹配的会议室列表

#### 请求体

```json
{
  "datetime": "2025-07-10T15:00:00",
  "participants": 10,
  "location": "A栋",
  "requirements": ["视频会议"]
}
```

#### 返回体

```json
[
  {
    "room_id": "A301",
    "name": "A栋301会议室",
    "capacity": 12,
    "equipment": ["视频会议", "白板"],
    "status": "available",
    "match_score": 0.92,
    "deviation": []
  },
  {
    "room_id": "A305",
    "name": "A栋305会议室",
    "capacity": 10,
    "equipment": ["白板"],
    "status": "available",
    "match_score": 0.75,
    "deviation": ["缺少视频会议"]
  }
]
```

---

### POST `/meeting/book`

提交会议室预定

#### 请求体

```json
{
  "room_id": "A301",
  "datetime": "2025-07-10T15:00:00",
  "duration_minutes": 60,
  "title": "项目复盘会议"
}
```

#### 返回体

```json
{
  "booking_id": "bk_87342",
  "status": "confirmed"
}
```

---

## 📝 3. 会议纪要生成模块

### POST `/meeting/transcribe`

上传音频并进行转写

#### 请求参数（FormData）

* `file`: 音频文件（MP3/WAV）
* `meeting_id`: 可选参数

#### 返回体

```json
{
  "transcript": [
    {
      "speaker": "发言人1",
      "text": "我们下周发布版本",
      "timestamp": "00:02:15"
    },
    ...
  ]
}
```

---

### POST `/meeting/minutes/generate`

根据转写内容 + 标记数据 → 生成结构化纪要草稿

#### 请求体

```json
{
  "transcript": [...],
  "template_id": "default"
}
```

#### 返回体

```json
{
  "title": "项目复盘会议纪要",
  "summary": "...",
  "points": ["问题回顾", "讨论方案"],
  "decisions": ["延期到7月20日"],
  "tasks": [...]
}
```

---

### GET `/meeting/minutes/templates`

获取纪要模板列表

#### 返回体

```json
[
  {
    "template_id": "default",
    "name": "默认模板",
    "sections": ["主题", "摘要", "要点", "任务", "决议"]
  }
]
```

---

## ✅ 4. 任务提取与管理模块

### POST `/tasks/extract`

从纪要文本中提取任务列表

#### 请求体

```json
{
  "meeting_minutes": "张三需要准备测试报告，下周一前完成..."
}
```

#### 返回体

```json
[
  {
    "task": "准备测试报告",
    "owner": "张三",
    "due_date": "2025-07-14",
    "department": "测试部"
  }
]
```

---

### GET `/tasks/kanban`

获取任务看板（按部门）

#### 返回体

```json
{
  "研发部": [
    { "task": "接口优化", "owner": "李四", "due_date": "2025-07-15" }
  ],
  "测试部": [
    { "task": "测试报告", "owner": "张三", "due_date": "2025-07-12" }
  ]
}
```

---

### GET `/tasks/stats`

获取任务统计数据（PoC可视化用）

#### 返回体

```json
{
  "total_tasks": 12,
  "by_department": {
    "研发部": 5,
    "测试部": 3,
    "市场部": 4
  }
}
```

---

## 🧾 5. 管理接口（管理员）

### GET `/admin/users`

获取用户列表（管理员）

#### 返回体

```json
[
  {
    "user_id": "u001",
    "username": "alice",
    "role": "organizer",
    "department": "研发部"
  }
]
```

---

### GET `/admin/org-structure`

获取组织架构信息（用于任务分配）

#### 返回体

```json
{
  "研发部": ["李四", "王强"],
  "测试部": ["张三"],
  "市场部": ["赵六"]
}
```

---

## 🚧 待扩展接口建议（非 PoC 必须）

* `POST /meeting/live-transcribe`（实时转写）
* `POST /minutes/mark`（主持人语音或点击标注）
* `PUT /tasks/confirm`（任务负责人确认）
* `POST /tasks/sync`（同步至外部任务系统）

---

## 🔐 通用错误码（建议）

| Code | Message           | 说明            |
| ---- | ----------------- | ------------- |
| 0    | success           | 请求成功          |
| 1001 | unauthorized      | 未登录或 token 无效 |
| 1002 | forbidden         | 无权限访问接口       |
| 2001 | validation\_error | 参数校验失败        |
| 3001 | model\_error      | LLM处理失败       |
| 5000 | server\_error     | 内部服务错误        |

---

> 文档版本：v1.0
> 更新时间：2025-07-09
> 作者：产品/研发联合团队

```

---

你可以将此文档保存为 `api.md` 或集成进项目 API 文档系统（如 Swagger/OpenAPI 文档生成工具）。  
如需转换为 OpenAPI YAML/JSON 文件，我可继续帮你生成。是否继续？
```
