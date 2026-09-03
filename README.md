# 学习通自动学习助手

[![GitHub release](https://img.shields.io/github/v/release/gitub-creater/xuexitong-auto-learner)](https://github.com/gitub-creater/xuexitong-auto-learner/releases)
[![License](https://img.shields.io/badge/license-Educational-blue)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](README.md)

自动播放学习通课程视频、AI 智能答题、连续学习整门课程的桌面工具。

**开发者：** 大学在读生 丁辉  
**版权所有 © 2026 丁辉。保留所有权利。**

---

## ✨ 功能特性

### 🎯 核心功能
- ✅ **自动播放视频** - 在官方播放器中真实播放，进度正常上报
- ✅ **AI 智能答题** - 支持选择题、填空题、简答题，视频内外全覆盖
- ✅ **无限重试机制** - 答错自动重试（最多 3 次），直到答对为止
- ✅ **连续学习** - 自动播放下一节，直到整门课程完成
- ✅ **手动控制** - 支持暂停、继续、停止操作

### 🤖 AI 答题
- ✅ **多种题型** - 选择题、填空题、简答题全支持
- ✅ **视频内外** - 弹题和课后作业都能处理
- ✅ **智能重试** - 答错自动生成新答案，最多 3 次
- ✅ **多 API 支持** - OpenAI、兼容接口、本地模型

### ⚙️ 配置与管理
- ✅ **AI 接口配置** - 兼容 OpenAI / 中转站 / 智谱 / 方舟 / DeepSeek
- ✅ **Cloudflare 穿透** - 自动处理被拦截的接口
- ✅ **日志记录** - 实时显示并写入 learning.log
- ✅ **安全授权** - 用户手动登录，不保存密码
- ✅ **深色界面** - 深色主题 + 翡翠绿配色

### 📦 打包版本
- ✅ **绿色免安装** - 无需 Python 环境
- ✅ **解压即用** - 双击启动，简单快捷
- ✅ **便于分享** - 压缩包仅 48.7 MB

---

## 📥 下载安装

### 方式一：绿色版（推荐，无需 Python）

1. 从 [Releases](https://github.com/gitub-creater/xuexitong-auto-learner/releases) 下载最新版本
2. 下载 \学习通自动学习助手_绿色版.zip\
3. 解压到任意目录（建议纯英文路径）
4. 双击运行 \学习通自动学习助手.exe\
5. 首次启动需要 10-30 秒，请耐心等待

### 方式二：源码运行（需要 Python 环境）

\\\ash
# 克隆项目
git clone https://github.com/gitub-creater/xuexitong-auto-learner.git
cd xuexitong-auto-learner

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
\\\

---

## 🚀 快速开始

### 第一步：登录学习通
1. 启动程序后，在登录区域填写账号密码
2. 点击"登录"按钮
3. 等待登录成功提示

### 第二步：配置 AI 答题（可选）
1. 点击"设置"标签
2. 切换到"AI 答题设置"
3. 填写 API 地址和 Key
4. 选择模型
5. 点击"测试连接"
6. 勾选"启用 AI 答题"
7. 保存设置

### 第三步：开始学习
1. 点击"开始学习"按钮
2. 程序自动打开浏览器
3. 选择课程
4. 自动播放视频并答题
5. 完成后自动进入下一节

---

## ⚙️ AI 答题配置

### 支持的 API 类型

#### 1. OpenAI 官方 API（推荐）
- **API 地址**: \https://api.openai.com/v1\
- **模型**: \gpt-4\, \gpt-3.5-turbo\
- **优点**: 准确率高，响应快
- **缺点**: 需要国际支付

#### 2. OpenAI 兼容接口
- **API 地址**: 自定义（如 \https://api.xxx.com/v1\）
- **模型**: 根据服务商提供
- **优点**: 国内可用，价格便宜
- **缺点**: 需要找到可靠的服务商

#### 3. 本地大模型
- **API 地址**: \http://localhost:11434/v1\（Ollama）
- **模型**: \qwen2.5:latest\, \llama3:latest\
- **优点**: 完全免费，数据私密
- **缺点**: 需要本地运行，占用资源

### 配置示例

\\\json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-xxxxxxxxxxxxxxxx",
  "model": "gpt-3.5-turbo",
  "enable_ai": true
}
\\\

详见 [AI答题功能说明.md](AI答题功能说明.md)

---

## 📖 详细文档

- [AI 答题功能说明](AI答题功能说明.md) - AI 配置和使用指南
- [无限重试功能说明](无限重试功能说明.md) - 重试机制详解
- [发布说明](RELEASE_NOTES.md) - 版本更新历史
- [打包完成报告](升级完成报告.md) - 技术细节

---

## ⚠️ 注意事项

### 首次使用
- 首次启动需要 10-30 秒加载依赖
- Windows 可能提示"未识别的应用"，点击"仍要运行"
- 杀毒软件可能误报，请添加到白名单

### 系统要求
- **操作系统**: Windows 10/11 (64位)
- **浏览器**: Chrome 或 Edge（程序需要）
- **网络**: 需要联网访问学习通和 AI API
- **磁盘空间**: 至少 200 MB

### 路径建议
- ✅ 推荐: \D:\Tools\xuexitong\
- ✅ 推荐: \C:\Program Files\xuexitong\
- ❌ 避免: 包含中文的路径
- ❌ 避免: 路径过长（超过 200 字符）

### 数据安全
- 账号密码仅存储在本地 \config.json\
- 不会上传到任何服务器
- API Key 请妥善保管，不要泄露
- 分享前请删除 \config.json\

---

## 🔧 常见问题

### Q1: 程序无法启动？
**A**: 
1. 检查是否解压完整
2. 确认路径不包含中文
3. 尝试以管理员身份运行
4. 查看是否被杀毒软件拦截

### Q2: 提示缺少 DLL 文件？
**A**: 
下载并安装 Visual C++ 运行库  
下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Q3: 提示找不到 Chrome？
**A**: 
安装 Chrome 或 Edge 浏览器，确保已更新到最新版本

### Q4: AI 答题不工作？
**A**: 
1. 检查 API 配置是否正确
2. 点击"测试连接"验证
3. 确认 API Key 有余额
4. 查看日志窗口的错误信息

### Q5: 视频播放但不答题？
**A**: 
1. 确认已勾选"启用 AI 答题"
2. 检查网络连接是否正常
3. 查看是否有弹题出现
4. 阅读日志了解具体错误

### Q6: 可以分享给朋友吗？
**A**: 
- ✅ 可以分享压缩包
- ❌ 删除你的 \config.json\（包含账号密码）
- ⚠️ 提醒朋友自行配置 AI API

更多问题请查看 [Issues](https://github.com/gitub-creater/xuexitong-auto-learner/issues)

---

## 📊 技术栈

- **语言**: Python 3.11
- **GUI**: Tkinter
- **浏览器自动化**: Selenium
- **HTTP 请求**: Requests
- **AI 集成**: OpenAI SDK
- **打包工具**: PyInstaller 6.22.2

---

## 📝 更新日志

### v2.0.0 (2026-09-03)
- ✅ [新增] AI 智能答题功能
- ✅ [新增] 填空题和简答题支持
- ✅ [新增] 无限重试机制（直到答对为止）
- ✅ [新增] 绿色免安装打包
- ✅ [优化] 视频播放检测逻辑
- ✅ [完善] 错误处理和日志记录
- ✅ [文档] 完善使用说明和配置指南

### v1.0.0
- ✅ 基础视频自动播放
- ✅ 选择题自动答题
- ✅ 连续学习功能

详见 [RELEASE_NOTES.md](RELEASE_NOTES.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 如何贡献
1. Fork 本项目
2. 创建特性分支 (\git checkout -b feature/AmazingFeature\)
3. 提交更改 (\git commit -m 'Add some AmazingFeature'\)
4. 推送到分支 (\git push origin feature/AmazingFeature\)
5. 提交 Pull Request

---

## 📄 开源协议

本项目仅供学习交流使用。

**使用限制**:
- ✅ 个人学习使用
- ✅ 分享给朋友使用
- ❌ 禁止商业用途
- ❌ 禁止违反学习通服务条款

**免责声明**:
- 本工具仅用于学习自动化技术
- 使用本工具产生的任何后果由使用者自行承担
- 请遵守学习通的使用规定
- 建议合理使用，避免滥用

---

## 🙏 致谢

感谢所有使用和支持本项目的用户！

如果觉得有帮助，请给个 ⭐ Star！

---

## 📞 联系方式

- **GitHub**: [@gitub-creater](https://github.com/gitub-creater)
- **项目主页**: https://github.com/gitub-creater/xuexitong-auto-learner
- **Issues**: https://github.com/gitub-creater/xuexitong-auto-learner/issues

---

**祝你学习顺利！** 🎓
