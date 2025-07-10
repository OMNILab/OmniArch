# 部署指南

## 🐳 Docker 部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 快速部署

1. **克隆项目**
```bash
git clone <repository-url>
cd frontend
```

2. **配置环境变量**
```bash
cp env.example .env.production
# 编辑 .env.production 文件，填入实际的配置值
```

3. **构建并运行**
```bash
# 使用构建脚本
./build.sh

# 或使用 docker-compose
docker-compose up -d
```

4. **访问应用**
打开浏览器访问 `http://localhost`

### 生产环境部署

#### 1. 构建生产镜像

```bash
# 构建镜像
docker build -t smart-meeting-frontend:latest .

# 推送到镜像仓库（可选）
docker tag smart-meeting-frontend:latest your-registry/smart-meeting-frontend:latest
docker push your-registry/smart-meeting-frontend:latest
```

#### 2. 使用 Docker Compose 部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f frontend

# 停止服务
docker-compose down
```

#### 3. 使用 Docker 命令部署

```bash
# 运行容器
docker run -d \
  --name smart-meeting-frontend \
  -p 80:80 \
  -p 443:443 \
  --restart unless-stopped \
  smart-meeting-frontend:latest

# 查看容器状态
docker ps

# 查看日志
docker logs -f smart-meeting-frontend

# 停止容器
docker stop smart-meeting-frontend
```

### 环境变量配置

在 `.env.production` 文件中配置以下变量：

```env
# Supabase 配置
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-production-anon-key

# API 配置
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

### Nginx 配置

应用使用自定义的 Nginx 配置 (`nginx.conf`)，包含：

- React Router 支持（SPA 路由）
- Gzip 压缩
- 安全头设置
- 静态资源缓存
- API 代理配置
- 健康检查端点

### 健康检查

应用提供健康检查端点：`http://localhost/health`

### 日志管理

```bash
# 查看容器日志
docker logs smart-meeting-frontend

# 实时查看日志
docker logs -f smart-meeting-frontend

# 查看 Nginx 访问日志
docker exec smart-meeting-frontend tail -f /var/log/nginx/access.log
```

### 故障排除

#### 1. 容器无法启动

```bash
# 检查容器状态
docker ps -a

# 查看错误日志
docker logs smart-meeting-frontend
```

#### 2. 应用无法访问

```bash
# 检查端口是否开放
netstat -tulpn | grep :80

# 检查容器网络
docker network ls
docker network inspect bridge
```

#### 3. 构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker build --no-cache -t smart-meeting-frontend:latest .
```

### 性能优化

1. **启用 Docker BuildKit**
```bash
export DOCKER_BUILDKIT=1
docker build -t smart-meeting-frontend:latest .
```

2. **多阶段构建优化**
Dockerfile 已使用多阶段构建，生产镜像只包含必要文件。

3. **资源限制**
```bash
docker run -d \
  --name smart-meeting-frontend \
  --memory=512m \
  --cpus=1 \
  -p 80:80 \
  smart-meeting-frontend:latest
```

### 监控

#### 1. 容器监控
```bash
# 查看资源使用情况
docker stats smart-meeting-frontend

# 查看容器详细信息
docker inspect smart-meeting-frontend
```

#### 2. 应用监控
- 健康检查：`curl http://localhost/health`
- 应用状态：访问主页面检查功能

### 备份和恢复

#### 1. 备份镜像
```bash
# 导出镜像
docker save smart-meeting-frontend:latest > smart-meeting-frontend.tar

# 导入镜像
docker load < smart-meeting-frontend.tar
```

#### 2. 备份配置
```bash
# 备份环境配置
cp .env.production .env.production.backup

# 备份 Nginx 配置
cp nginx.conf nginx.conf.backup
```

### 更新部署

#### 1. 滚动更新
```bash
# 构建新镜像
docker build -t smart-meeting-frontend:new .

# 停止旧容器
docker stop smart-meeting-frontend

# 启动新容器
docker run -d --name smart-meeting-frontend-new -p 80:80 smart-meeting-frontend:new

# 验证新版本
curl http://localhost/health

# 删除旧容器
docker rm smart-meeting-frontend
docker tag smart-meeting-frontend:new smart-meeting-frontend:latest
```

#### 2. 使用 Docker Compose 更新
```bash
# 更新镜像
docker-compose pull

# 重新部署
docker-compose up -d
``` 