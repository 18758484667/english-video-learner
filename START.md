# 快速启动指南

## 当前状态

前端已成功启动并运行在: http://localhost:5173

## 测试应用(无需后端)

你现在可以直接在浏览器中打开 http://localhost:5173 来体验以下功能:

### 1. 登录界面
- 输入任意用户名即可登录
- 系统会创建本地用户会话

### 2. 三层字幕演示
点击"Video Player"标签页,然后点击 **"Load Sample"** 按钮,你将看到:

**示例句子**: "The quick brown fox jumps over the lazy dog"

**三层显示效果**:
```
        狐狸     跳跃          ← 顶层: 生词中文释义(大字,彩色)
The quick brown fox jumps over the lazy dog  ← 中层: 英文字幕(白色大字)
那只敏捷的棕色狐狸跳过了懒惰的狗              ← 底层: 整句翻译(灰色小字)
```

### 3. 交互功能
- **点击单词**: 查看单词详情
- **Show/Hide Annotations**: 切换生词释义显示
- **Show/Hide Translation**: 切换整句翻译显示
- **播放速度控制**: 0.5x - 1.5x

### 4. 词汇测试
点击"Level Test"标签页可以体验词汇量测试界面(需要后端支持才能提交)

### 5. 生词本
点击"Vocabulary List"查看生词本功能(需要后端支持才能保存)

## 完整功能(需要后端)

要启用所有功能(视频处理、真实测试、生词本持久化),需要启动后端服务器:

### 安装Python依赖

```bash
cd backend
pip install fastapi uvicorn sqlalchemy python-multipart requests pydantic
```

### 启动后端

```bash
cd backend
uvicorn app.main:app --reload
```

后端将运行在: http://localhost:8000

API文档: http://localhost:8000/docs

## 下一步

1. 先在浏览器中体验前端UI和三层字幕显示效果
2. 如需完整功能,安装Python并启动后端
3. 后续可以集成真实的Whisper语音识别和翻译API

## 已知限制(当前版本)

- 视频上传和处理功能尚未完全实现
- 词汇测试需要后端才能提交答案
- 生词本数据存储在内存中,刷新页面会丢失(无后端时)
- 需要安装faster-whisper才能实现真实的视频转录

这些将在后续迭代中完善。
