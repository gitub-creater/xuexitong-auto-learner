# GitHub Release 发布指南

## 📦 准备工作

已完成：
- ✅ 代码已推送到 GitHub
- ✅ 打包文件已准备：releases/学习通自动学习助手_v2.0.0_绿色版.zip (48.7 MB)
- ✅ 文档已完善（README、RELEASE_NOTES、LICENSE）

---

## 🚀 发布步骤

### 方式一：通过 GitHub 网页发布（推荐）

1. **访问项目页面**
   - 打开 https://github.com/gitub-creater/xuexitong-auto-learner
   - 点击右侧的 "Releases"

2. **创建新 Release**
   - 点击 "Draft a new release" 或 "Create a new release"

3. **填写 Release 信息**
   - **Tag version**: \2.0.0\
   - **Release title**: \2.0.0 - AI 智能答题 + 绿色免安装版\
   - **描述**: 复制下面的发布说明

4. **上传文件**
   - 点击 "Attach binaries by dropping them here or selecting them"
   - 上传 \eleases/学习通自动学习助手_v2.0.0_绿色版.zip\

5. **发布**
   - 确认信息无误
   - 点击 "Publish release"

---

## 📝 Release 描述模板

复制以下内容到 Release 描述框：

\\\markdown
## 🎉 学习通自动学习助手 v2.0.0

这是一个重大更新版本，添加了 AI 智能答题和绿色免安装打包。

---

## ✨ 新增功能

### 🤖 AI 智能答题
- ✅ 支持选择题、填空题、简答题
- ✅ 视频内弹题和课后作业全覆盖
- ✅ 兼容 OpenAI API 和各种兼容接口
- ✅ 支持本地大模型（Ollama、LM Studio）

### 🔄 无限重试机制
- ✅ 答错自动重新生成答案
- ✅ 最多尝试 3 次，每次不同策略
- ✅ 直到答对或达到最大次数

### 📦 绿色免安装版
- ✅ 无需 Python 环境，解压即用
- ✅ 双击启动，简单快捷
- ✅ 压缩包仅 48.7 MB，便于分享

---

## 📥 下载安装

### 绿色版（推荐）
1. 下载下方的 \学习通自动学习助手_v2.0.0_绿色版.zip\
2. 解压到任意目录（建议纯英文路径）
3. 双击运行 \学习通自动学习助手.exe\
4. 首次启动需要 10-30 秒，请耐心等待

### 源码运行
\\\ash
git clone https://github.com/gitub-creater/xuexitong-auto-learner.git
cd xuexitong-auto-learner
pip install -r requirements.txt
python main.py
\\\

---

## ⚙️ 快速配置

### 1. 登录学习通
- 填写账号密码
- 点击"登录"

### 2. 配置 AI 答题（可选）
- 点击"设置" → "AI 答题设置"
- 填写 API 地址和 Key
- 测试连接并保存

### 3. 开始学习
- 点击"开始学习"
- 选择课程
- 自动播放并答题

详细配置请查看 [AI答题功能说明](https://github.com/gitub-creater/xuexitong-auto-learner/blob/main/AI答题功能说明.md)

---

## ⚠️ 注意事项

### 首次使用
- 首次启动需要 10-30 秒加载
- Windows 可能提示"未识别的应用"，点击"仍要运行"
- 杀毒软件可能误报，请添加白名单

### 系统要求
- Windows 10/11 (64位)
- Chrome 或 Edge 浏览器
- 网络连接
- 至少 200 MB 磁盘空间

### 数据安全
- 账号密码仅存本地
- 不会上传服务器
- 分享前请删除 config.json

---

## 🔧 常见问题

**Q: 程序无法启动？**  
A: 检查路径是否包含中文，尝试管理员运行，查看杀毒软件是否拦截

**Q: AI 答题不工作？**  
A: 检查 API 配置，点击测试连接，确认 API 有余额

**Q: 可以分享给朋友吗？**  
A: 可以，但请删除 config.json，提醒对方自行配置 API

更多问题请查看 [Issues](https://github.com/gitub-creater/xuexitong-auto-learner/issues)

---

## 📊 版本信息

- **版本号**: v2.0.0
- **发布日期**: 2026-09-03
- **压缩包大小**: 48.7 MB
- **解压后大小**: 130.38 MB
- **文件数**: 1190 个

---

## 📝 完整更新日志

- [新增] AI 智能答题功能（选择题、填空题、简答题）
- [新增] 视频内外题目全场景覆盖
- [新增] 无限重试机制（答错自动重试，直到答对为止）
- [新增] 绿色免安装打包（PyInstaller）
- [优化] 视频播放检测逻辑
- [优化] 错误处理和日志记录
- [完善] README 和使用文档
- [完善] AI 配置说明和常见问题

---

## 🙏 致谢

感谢所有使用和支持本项目的用户！

如果觉得有帮助，请给个 ⭐ Star！

---

**祝你学习顺利！** 🎓
\\\

---

## 📋 检查清单

发布前请确认：

- [ ] 版本号正确：v2.0.0
- [ ] 标题正确：v2.0.0 - AI 智能答题 + 绿色免安装版
- [ ] 描述完整，包含所有新功能
- [ ] 文件已上传：学习通自动学习助手_v2.0.0_绿色版.zip
- [ ] 文件大小正确：48.7 MB
- [ ] 链接可访问
- [ ] 设置为 Latest release

---

## 🎯 发布后

1. **验证下载**
   - 访问 Release 页面
   - 下载文件并测试
   - 确认文件完整

2. **更新 README**
   - 已完成，无需修改

3. **通知用户**
   - 可以在相关群组或论坛发布通知
   - 分享 Release 链接

---

## 💡 提示

- 如果发现问题，可以编辑 Release 重新上传文件
- 可以添加多个文件到同一个 Release
- Release 描述支持 Markdown 格式
- 可以将 Release 标记为 Pre-release（预发布版）

---

**准备就绪，可以发布了！** 🚀
