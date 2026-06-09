# English Video Learner

一个基于Web的英语学习工具,通过视频字幕智能标注生词,帮助你更高效地学习英语。

## 功能特性

- **三层字幕显示**:
  - 顶层: 生词中文释义(大字,特殊颜色标注)
  - 中层: 英文字幕(大字,主显示)
  - 底层: 整句中文翻译(小字,辅助理解)

- **智能生词标注**: 根据你的英语水平自动标注超出水平的单词

- **词汇量测试**: 自适应测试评估你的CEFR等级

- **生词本**: 收集和管理学习中遇到的生词

## 技术栈

### 前端
- React 18 + TypeScript
- Vite
- TailwindCSS
- Zustand (状态管理)
- ReactPlayer (视频播放)
- Axios (HTTP客户端)

### 后端
- FastAPI (Python)
- SQLite (数据库)
- faster-whisper (语音识别,可选)
- yt-dlp (视频下载,可选)

## 快速开始

### 前置要求

- **Node.js 18+** (前端运行必需)
- **Python 3.9+** (后端运行必需)
- **FFmpeg** (视频处理必需,用于提取音频)
  - Windows: 下载 https://github.com/BtbN/FFmpeg-Builds/releases
  - 解压后将 `ffmpeg.exe` 放到系统PATH中(如 `C:\Windows`)
  - 验证: 命令行输入 `ffmpeg -version`

### 🚀 一键启动(推荐)

**方式1: 完整启动(前后端)**
1. 双击项目根目录的 `start.bat`
2. 等待两个窗口都启动完成
3. 浏览器自动打开 http://localhost:5173

**方式2: 分别启动**

#### 步骤1: 启动后端

```bash
# 方法A: 双击脚本(推荐)
cd backend
双击 start-backend.bat

# 方法B: 命令行启动
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd app && python init_db.py && cd ..
uvicorn app.main:app --reload
```

后端将运行在 `http://localhost:8000`  
API文档: `http://localhost:8000/docs`

#### 步骤2: 启动前端

```bash
cd frontend
npm install  # 首次运行需要
npm run dev
```

前端将运行在 `http://localhost:5173`

## 使用指南

### 1. 登录/注册

首次使用时,输入用户名即可开始学习。系统会自动创建用户账户。

### 2. 英语水平测试

点击"Level Test"标签页,完成词汇量测试,系统会评估你的CEFR等级(A1-C2)。

### 3. 加载视频

**方式A: 上传本地视频(推荐)**
1. 点击"Upload Video"标签页
2. 选择本地视频文件(MP4、AVI、MOV等格式)
3. 等待后台处理(音频提取→语音识别→翻译→生词标注)
4. 处理完成后自动跳转到播放器

**方式B: 使用示例字幕**
- 点击"Load Sample"加载示例字幕,体验三层字幕显示功能

**注意**: 首次使用本地视频上传需要:
- 安装FFmpeg(见前置要求)
- (可选)配置百度翻译API密钥以获得更好的翻译效果

### 4. 字幕交互

- **点击单词**: 查看详细信息
- **生词标注**: 超出你水平的单词会用特殊颜色显示中文释义
  - 红色: 超出2级以上
  - 黄色: 超出1级
- **控制按钮**:
  - "Show/Hide Annotations": 切换生词释义显示
  - "Show/Hide Translation": 切换整句翻译显示
  - 播放速度: 0.5x - 1.5x

### 5. 生词本

点击"Vocabulary List"查看你收藏的所有生词,可以导出为CSV格式。

## 项目结构

```
english-video-learner/
├── backend/                 # 后端FastAPI应用
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑服务
│   │   ├── database.py     # 数据库配置
│   │   ├── init_db.py      # 数据库初始化
│   │   └── main.py         # FastAPI入口
│   ├── data/               # SQLite数据库文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端React应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── store/          # Zustand状态管理
│   │   ├── App.tsx         # 主应用组件
│   │   └── index.css       # 全局样式
│   └── package.json        # Node.js依赖
└── README.md
```

## API端点

### 用户
- `POST /api/users/` - 创建用户
- `GET /api/users/{user_id}` - 获取用户信息
- `PUT /api/users/{user_id}` - 更新用户信息

### 视频
- `POST /api/videos/upload/` - 上传视频
- `POST /api/videos/online/` - 处理在线视频
- `GET /api/videos/{process_id}` - 获取处理状态

### 词汇
- `POST /api/vocabulary/items/` - 添加生词
- `GET /api/vocabulary/items/{user_id}` - 获取生词本
- `DELETE /api/vocabulary/items/{item_id}` - 删除生词
- `GET /api/vocabulary/word-info/{word}` - 获取单词信息

### 测试
- `POST /api/tests/start/` - 开始测试
- `POST /api/tests/submit/` - 提交测试答案
- `GET /api/tests/history/{user_id}` - 获取测试历史

## 下一步开发计划

1. ✅ **完整视频处理**: 已集成faster-whisper实现真实的视频转录
2. ✅ **翻译API集成**: 已接入百度翻译API(可选配置)
3. ⏳ **间隔重复算法**: 实现SM-2算法优化复习计划
4. ⏳ **移动端优化**: 响应式设计适配手机
5. ⏳ **用户认证**: 添加密码和JWT认证
6. ⏳ **云存储**: 支持视频文件云端存储

## ❓ 常见问题

### Q1: 点击登录按钮没反应?
**解决**: 确保后端服务器已启动。如果不想使用后端功能,前端支持本地模式,直接输入用户名即可登录。

### Q2: 上传视频后一直显示"处理中"?
**可能原因**:
1. FFmpeg未安装或路径配置错误
2. 视频文件过大,处理时间较长
3. 后端服务器未启动

**检查方法**:
- 查看后端控制台日志输出
- 确认FFmpeg安装: 命令行输入 `ffmpeg -version`

### Q3: 翻译结果都是"[翻译] xxx"?
**原因**: 未配置百度翻译API密钥,系统使用模拟翻译。

**解决**: 
1. 在 `backend` 目录创建 `.env` 文件
2. 添加以下内容:
   ```env
   BAIDU_TRANSLATE_APPID=你的APP_ID
   BAIDU_TRANSLATE_SECRET_KEY=你的密钥
   ```
3. 重启后端服务器

### Q4: Whisper转录很慢?
**原因**: CPU运行Whisper模型速度较慢。

**优化方案**:
- 使用较小的模型(tiny或base),修改 `.env` 文件:
  ```env
  WHISPER_MODEL_SIZE=tiny
  ```
- 如果有NVIDIA显卡,启用GPU加速(需要CUDA支持)

### Q5: 样式加载不正常?
**解决**: 
1. 确保已安装TailwindCSS依赖
2. 重新运行 `npm install`
3. 重启前端开发服务器

## 许可证

MIT License
