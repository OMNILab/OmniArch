# 智慧会议系统 - 前端

基于 React + TypeScript + Tailwind CSS 的智慧会议系统前端应用，集成 Supabase 作为后端服务。

## 🚀 功能特性

### 1. 智能会议室预定
- 自然语言输入会议需求
- AI 智能解析时间、地点、人数、设备要求
- 会议室推荐算法，显示匹配度和偏差提示
- 一键预定确认

### 2. 自动会议纪要生成
- 音频文件上传（支持 MP3、WAV 格式）
- AI 语音转写和智能分析
- 结构化纪要输出（摘要、要点、决策、发言记录）
- 支持导出 PDF 和 Markdown 格式

### 3. 任务看板管理
- 从会议纪要自动提取任务
- 按部门分类的看板视图
- 任务状态管理（草稿、已确认、已完成）
- 任务统计图表展示

### 4. 系统管理
- 用户管理（组织者、参与者、管理员）
- 组织架构管理
- 纪要模板配置
- 系统设置

## 🛠️ 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式框架**: Tailwind CSS
- **UI 组件**: Headless UI + Heroicons
- **状态管理**: React Context + Hooks
- **路由**: React Router DOM
- **图表**: Recharts
- **通知**: React Hot Toast
- **后端服务**: Supabase

## 📦 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 环境配置

复制环境变量文件并配置：

```bash
cp env.example .env.local
```

编辑 `.env.local` 文件，配置 Supabase 连接信息：

```env
VITE_SUPABASE_URL=your-supabase-project-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 4. 构建生产版本

```bash
npm run build
```

## 🏗️ 项目结构

```
src/
├── components/          # 可复用组件
│   └── Layout.tsx      # 主布局组件
├── contexts/           # React Context
│   └── AuthContext.tsx # 认证上下文
├── lib/               # 工具库
│   ├── supabase.ts    # Supabase 客户端
│   └── utils.ts       # 工具函数
├── pages/             # 页面组件
│   ├── LoginPage.tsx  # 登录页
│   ├── BookingPage.tsx # 智能预定页
│   ├── MinutesPage.tsx # 会议纪要页
│   ├── TasksPage.tsx  # 任务看板页
│   └── SettingsPage.tsx # 系统设置页
├── App.tsx            # 主应用组件
├── main.tsx           # 应用入口
└── index.css          # 全局样式
```

## 🎨 设计规范

### 颜色系统
- **主色**: Blue 600 (#2563eb)
- **成功色**: Green 500 (#10b981)
- **警告色**: Orange 500 (#f59e0b)
- **错误色**: Red 500 (#ef4444)

### 组件样式
- **按钮**: 圆角设计，支持主要、次要、危险等状态
- **卡片**: 阴影效果，圆角设计
- **输入框**: 聚焦时蓝色边框
- **模态框**: 居中显示，背景遮罩

## 🔐 认证系统

- 基于 JWT Token 的认证
- 三种用户角色：组织者、参与者、管理员
- 路由保护，未登录用户重定向到登录页
- 模拟登录系统（演示用）

## 📱 响应式设计

- 移动端优先的设计理念
- 支持桌面端、平板、手机等多种设备
- 自适应布局和组件

## 🚀 部署

### Docker 部署（推荐）

#### 1. 构建 Docker 镜像

```bash
# 使用构建脚本
./build.sh

# 或直接使用 Docker
docker build -t smart-meeting-frontend:latest .
```

#### 2. 运行容器

```bash
# 使用 Docker
docker run -d -p 80:80 --name smart-meeting-frontend smart-meeting-frontend:latest

# 或使用 docker-compose
docker-compose up -d
```

#### 3. 访问应用

应用将在 `http://localhost` 启动。

### Vercel 部署

1. 连接 GitHub 仓库
2. 配置环境变量
3. 自动部署

### 其他平台

构建后部署 `dist` 目录到任何静态文件服务器。

## 🔧 开发指南

### Docker 开发环境

```bash
# 构建开发镜像
docker build -t smart-meeting-frontend:dev .

# 运行开发容器（挂载源码）
docker run -d -p 3000:3000 -v $(pwd):/app -w /app smart-meeting-frontend:dev npm run dev
```

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 添加路由
3. 在 `src/components/Layout.tsx` 添加导航项

### 添加新组件

1. 在 `src/components/` 创建组件
2. 使用 TypeScript 定义 Props 接口
3. 遵循组件命名规范

### 样式开发

- 使用 Tailwind CSS 类名
- 自定义样式在 `src/index.css` 中定义
- 遵循设计系统规范

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## �� 支持

如有问题，请联系开发团队。
