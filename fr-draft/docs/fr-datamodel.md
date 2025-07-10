# 🗄️ 智慧会议 PoC 后端数据模型设计（PostgreSQL）

## 📌 数据库命名约定

- 所有表名使用 **snake_case**
- 主键字段统一为 `id UUID PRIMARY KEY`
- 时间字段统一使用 `created_at` / `updated_at`（自动更新）
- 所有模型使用 `soft delete` 可选字段（如 `is_deleted`）

---

## 👤 表：users（用户表）

| 字段名         | 类型            | 描述              |
|----------------|------------------|-------------------|
| id             | UUID PRIMARY KEY | 用户唯一标识      |
| username       | TEXT UNIQUE      | 用户名            |
| password_hash  | TEXT             | 密码哈希（可选）  |
| role           | TEXT             | 角色：`organizer` / `participant` / `admin` |
| department     | TEXT             | 所属部门          |
| created_at     | TIMESTAMP        | 创建时间          |
| updated_at     | TIMESTAMP        | 更新时间          |

---

## 🏢 表：meeting_rooms（会议室信息）

| 字段名         | 类型            | 描述               |
|----------------|------------------|--------------------|
| id             | UUID PRIMARY KEY | 会议室唯一标识     |
| name           | TEXT             | 名称（如“A301”）   |
| location       | TEXT             | 楼层或楼栋（如“A栋”）|
| capacity       | INTEGER          | 容纳人数           |
| equipment      | TEXT[]           | 设备列表（数组）   |
| status         | TEXT             | 当前状态：`available` / `booked` |
| created_at     | TIMESTAMP        |                    |
| updated_at     | TIMESTAMP        |                    |

---

## 📅 表：meetings（会议预定记录）

| 字段名         | 类型            | 描述                |
|----------------|------------------|---------------------|
| id             | UUID PRIMARY KEY | 会议唯一标识        |
| room_id        | UUID             | 外键 → meeting_rooms(id) |
| organizer_id   | UUID             | 外键 → users(id)    |
| title          | TEXT             | 会议标题            |
| start_time     | TIMESTAMP        | 开始时间            |
| duration_min   | INTEGER          | 会议时长（分钟）    |
| status         | TEXT             | `booked` / `cancelled` |
| created_at     | TIMESTAMP        |                     |
| updated_at     | TIMESTAMP        |                     |

---

## 🎙️ 表：meeting_transcripts（语音转写内容）

| 字段名         | 类型            | 描述                    |
|----------------|------------------|-------------------------|
| id             | UUID PRIMARY KEY | 唯一标识                |
| meeting_id     | UUID             | 外键 → meetings(id)     |
| speaker_label  | TEXT             | 发言人标签（如“发言人1”）|
| content        | TEXT             | 转写文本                |
| timestamp      | TEXT             | 时间戳字符串（00:02:15）|
| created_at     | TIMESTAMP        |                         |

---

## 📝 表：meeting_minutes（会议纪要草稿）

| 字段名         | 类型            | 描述                 |
|----------------|------------------|----------------------|
| id             | UUID PRIMARY KEY |                      |
| meeting_id     | UUID             | 外键 → meetings(id) |
| template_id    | TEXT             | 使用的模板 ID        |
| summary        | TEXT             | 会议摘要             |
| points         | TEXT[]           | 要点列表（JSON可选） |
| decisions      | TEXT[]           | 决策列表             |
| raw_transcript | TEXT             | 原始纪要全文（JSON or TEXT）|
| editable_html  | TEXT             | 富文本内容（可编辑） |
| created_at     | TIMESTAMP        |                      |

---

## ✅ 表：tasks（从纪要中提取的任务）

| 字段名         | 类型            | 描述                      |
|----------------|------------------|---------------------------|
| id             | UUID PRIMARY KEY |                           |
| meeting_id     | UUID             | 外键 → meetings(id)       |
| description    | TEXT             | 任务内容描述              |
| owner_id       | UUID             | 外键 → users(id)，可为空   |
| department     | TEXT             | 推断的责任部门            |
| due_date       | DATE             | 截止日期                  |
| status         | TEXT             | `draft` / `confirmed` / `done` |
| created_at     | TIMESTAMP        |                           |

---

## 📋 表：minutes_templates（纪要模板）

| 字段名         | 类型            | 描述               |
|----------------|------------------|--------------------|
| id             | TEXT PRIMARY KEY | 模板标识（如“default”）|
| name           | TEXT             | 模板名称           |
| structure_json | JSONB            | 模板结构字段定义   |
| created_by     | UUID             | 创建者 ID（可选）  |
| created_at     | TIMESTAMP        |                    |

---

## 📊 表：metrics_cache（任务统计缓存，可选）

| 字段名         | 类型            | 描述              |
|----------------|------------------|-------------------|
| id             | UUID PRIMARY KEY |                   |
| date_key       | DATE             | 缓存日期（如每日）|
| total_tasks    | INTEGER          | 总任务数          |
| dept_stats     | JSONB            | 部门 → 数量 map   |
| generated_at   | TIMESTAMP        | 缓存时间          |

---

## 🔐 表关系图（简要）

```plaintext
users ─────────┐
               │
               ├───┐
meeting_rooms──┤   ├──→ meetings ─→ meeting_minutes ─→ tasks
                   │                    │
                   └────→ meeting_transcripts
