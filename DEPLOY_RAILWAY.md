# Railway 部署指南

> 本文档指导如何将 English Video Learner 后端部署到 Railway 平台。

---

## 前置条件

- 已安装 Git
- 项目已推送到 GitHub（已完成）
- 有稳定的网络连接

---

## 第一步：注册 Railway 账号

1. 打开浏览器，访问：https://railway.app
2. 点击页面右上角的 **Get Started**
3. 选择 **Continue with GitHub**
4. 授权 Railway 访问你的 GitHub 账号
5. 完成注册流程

---

## 第二步：创建新项目

1. 登录后进入 Railway Dashboard
2. 点击 **New Project**
3. 选择 **Deploy from GitHub repo**
4. 如果这是你第一次使用 Railway，会弹出 GitHub 授权页面：
   - 点击 **Configure GitHub App**
   - 选择 **All repositories** 或只选择 `english-video-learner`
   - 点击 **Save**
5. 在仓库列表中找到并选择 `18758484667/english-video-learner`

---

## 第三步：配置服务

1. 选择仓库后，Railway 会自动检测项目结构
2. 如果自动检测到 Dockerfile，会显示 Docker 构建选项
3. 点击 **Create Service**
4. 服务名称默认是仓库名，可以保留或修改

---

## 第四步：设置环境变量

1. 进入刚创建的服务详情页
2. 点击顶部菜单的 **Variables**
3. 点击 **New Variable** 添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | `8000` | 应用监听端口 |
| `DATABASE_URL` | `sqlite:///app/data/app.db` | 数据库路径 |

> 注：如果后续需要 PostgreSQL，可以在 Railway 中添加 PostgreSQL 插件，然后使用其提供的 DATABASE_URL。

---

## 第五步：添加持久化存储（Volume）

由于 Railway 免费实例会重启，必须添加 Volume 保存 SQLite 数据和上传的视频文件。

1. 在服务详情页，点击顶部菜单的 **Settings**
2. 左侧菜单选择 **Volumes**
3. 点击 **Add Volume**
4. 配置如下：
   - **Mount Path**: `/app/data`
   - **Size**: 1GB（免费额度）
   - 其他保持默认

---

## 第六步：部署服务

1. 回到服务概览页
2. 点击 **Deploy** 按钮（如果之前已经自动部署，可以跳过）
3. 等待构建完成（首次构建约需 3-5 分钟）
4. 构建日志可以在 **Deployments** 标签页查看

---

## 第七步：获取域名

1. 部署成功后，点击顶部菜单的 **Settings**
2. 找到 **Networking** 部分
3. 点击 **Generate Domain**
4. Railway 会分配一个域名，格式如：
   ```
   https://english-video-learner-production-1234.up.railway.app
   ```

---

## 第八步：更新前端 API 地址

1. 复制上一步获取的域名
2. 修改项目文件：`frontend/src/config.ts`
   ```typescript
   export const API_BASE_URL = 'https://你的-railway-域名.up.railway.app'
   ```
3. 提交并推送更改：
   ```bash
   git add frontend/src/config.ts
   git commit -m "Update API URL to Railway"
   git push origin master
   ```
4. 等待 GitHub Actions 自动重新部署前端到 GitHub Pages

---

## 第九步：验证部署

### 测试后端健康检查
```bash
curl https://你的-railway-域名.up.railway.app/api/health
```
预期返回：`{"status": "ok"}`

### 测试前端访问
1. 打开你的 GitHub Pages 地址
2. 尝试上传一个视频文件
3. 检查浏览器的 Network 面板，确认 API 请求正常

---

## 常见问题排查

### 构建失败：Dockerfile 找不到
- 确保 `railway.json` 已提交到 GitHub
- 检查 `backend/Dockerfile` 是否存在

### 应用启动后数据库无法写入
- 检查 Volume 是否正确挂载到 `/app/data`
- 检查 `DATABASE_URL` 是否为 `sqlite:///app/data/app.db`

### 前端提示 CORS 错误
- 检查后端是否允许跨域请求
- 确认 `frontend/src/config.ts` 中的 URL 是否正确

### 服务休眠
- Railway 免费实例在不活跃一段时间后会休眠
- 首次访问时可能需要等待 10-30 秒冷启动
- 如果希望保持活跃，可以设置定时请求（如 UptimeRobot）

---

## 替代方案

如果 Railway 部署遇到问题，可以考虑：
- **Render**：同样支持 Docker 免费部署，但冷启动更慢
- **Fly.io**：需要安装 flyctl CLI，性能更好
- **LocalTunnel**：临时本地暴露，URL 会变化

---

*本文档由 Lingma 自动生成*
