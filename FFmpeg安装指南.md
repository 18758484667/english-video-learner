# FFmpeg 安装指南

由于网络原因,自动下载失败。请按照以下步骤手动安装FFmpeg。

## 🎯 方法1: 使用winget安装(推荐)

Windows 10/11自带winget包管理器,这是最简单的安装方式。

### 步骤:

1. **打开PowerShell或命令提示符**
   - 按 `Win + X`,选择 "Windows PowerShell" 或 "终端"

2. **运行安装命令**:
   ```powershell
   winget install --id Gyan.FFmpeg -e --accept-package-agreements
   ```

3. **等待安装完成**
   - winget会自动下载并安装FFmpeg
   - 安装完成后,FFmpeg会自动添加到系统PATH

4. **验证安装**:
   打开新的命令行窗口,输入:
   ```bash
   ffmpeg -version
   ```
   如果看到版本信息,说明安装成功!

---

## 🎯 方法2: 手动下载安装

如果winget无法使用,可以手动下载。

### 步骤:

1. **下载FFmpeg**:
   
   访问以下任一网址下载:
   
   - **官方GitHub releases**(推荐):
     ```
     https://github.com/GyanD/codexffmpeg/releases/latest
     ```
     下载 `ffmpeg-xxx-full_build.zip`
   
   - **备用下载地址**:
     ```
     https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
     ```

2. **解压文件**:
   - 将下载的zip文件解压到 `C:\ffmpeg` 目录
   - 确保解压后的结构是:
     ```
     C:\ffmpeg\
       └── bin\
           ├── ffmpeg.exe
           ├── ffprobe.exe
           └── ...
     ```

3. **添加到系统PATH**:
   
   **方法A: 通过图形界面**
   - 右键"此电脑" → "属性" → "高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到 `Path`,双击编辑
   - 点击"新建",输入: `C:\ffmpeg\bin`
   - 一路点击"确定"保存
   
   **方法B: 通过命令行**(需要管理员权限)
   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")
   ```

4. **重启命令行并验证**:
   - 关闭所有命令行窗口
   - 打开新的命令行窗口
   - 输入:
     ```bash
     ffmpeg -version
     ```
   - 应该看到类似输出:
     ```
     ffmpeg version x.x.x Copyright (c) 2000-2024 the FFmpeg developers
     ...
     ```

---

## ✅ 验证安装

安装完成后,运行以下命令验证:

```bash
ffmpeg -version
ffprobe -version
```

两个命令都应该显示版本信息。

---

## 🔧 安装后测试

安装FFmpeg后,回到英语学习视频工具项目:

1. **启动后端服务器**:
   ```bash
   cd backend
   start-backend.bat
   ```

2. **上传一个测试视频**:
   - 打开浏览器访问 http://localhost:5173
   - 登录后点击 "Upload Video"
   - 选择一个短视频文件(1-2分钟)
   - 等待处理完成

3. **检查后端日志**:
   - 应该能看到 "Audio extracted to: ..." 的消息
   - 如果没有FFmpeg,会看到 "FFmpeg not found" 错误

---

## ❓ 常见问题

### Q: winget命令找不到?
**解决**: 
- Windows 10 1709+ 和 Windows 11 自带winget
- 如果没有,可以从Microsoft Store安装 "App Installer"

### Q: 安装后ffmpeg命令还是找不到?
**解决**:
1. 确认 `C:\ffmpeg\bin\ffmpeg.exe` 文件存在
2. 确认已添加到PATH
3. **必须重启命令行窗口**才能生效

### Q: 下载速度很慢?
**解决**:
- 尝试使用国内镜像或VPN
- 或者找朋友帮忙下载后分享给你

---

## 📞 需要帮助?

如果遇到问题,请:
1. 截图错误信息
2. 告诉我你使用的是哪种安装方法
3. 我会帮你解决!
