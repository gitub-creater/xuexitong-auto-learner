# GitHub Release 发布指南

## 📦 准备工作

已完成：
- ✅ 代码已推送到 GitHub
- ✅ 打包文件已准备：releases/学习通自动学习助手_v2.0_绿色版.zip (49 MB)
- ✅ 文档已完善（README、使用说明、AI答题功能说明）
- ✅ Bug修复完成（3个关键bug）

---

## 🚀 发布步骤

### 通过 GitHub 网页发布

1. **访问项目页面**
   - 打开 https://github.com/gitub-creater/xuexitong-auto-learner
   - 点击右侧的 "Releases"

2. **创建新 Release**
   - 点击 "Draft a new release" 或 "Create a new release"

3. **填写 Release 信息**
   - **Tag version**: `v2.0`
   - **Release title**: `v2.0 - Bug修复与优化版`
   - **描述**: 复制下面的发布说明

4. **上传文件**
   - 点击 "Attach binaries by dropping them here or selecting them"
   - 上传文件路径：`C:\Users\丁辉\.zcode\workspace\default\xuexitong-auto-learner\releases\学习通自动学习助手_v2.0_绿色版.zip`

5. **发布**
   - 勾选 "Set as the latest release"
   - 点击 "Publish release"

---

## 📝 Release 描述模板

复制以下内容到 Release 描述框：

```markdown
## 🎉 v2.0 更新内容

### 🐛 Bug修复
1. **未启用AI时不会误调用AI接口** - 严格的前置检查，确保只在配置正确时才使用AI
2. **题目识别失败时自动跳过** - 避免不完整的题目导致程序卡住
3. **优化视频播放流畅度** - 降低题目检查频率（每5秒一次），避免频繁扫描影响播放

### ✨ 核心功能
- ✅ 自动播放视频课程
- ✅ 智能答题（选择题/填空题/简答题）
- ✅ AI答题支持（豆包/DeepSeek/千问等）
- ✅ 答错无限重试机制（答错不限次数，只有技术故障才跳过）
- ✅ Cloudflare防护绕过
- ✅ 翡翠绿深色主题界面

---

## 📥 下载安装

### 绿色版（推荐）
1. 下载下方的 `学习通自动学习助手_v2.0_绿色版.zip` (49MB)
2. 解压到任意目录
3. 双击运行 `学习通自动学习助手.exe`
4. 首次启动需要加载，请耐心等待

### 系统要求
- Windows 10/11 (64位)
- 网络连接
- 至少 200 MB 磁盘空间

---

## 📝 快速开始

### 基础使用
1. 双击 `学习通自动学习助手.exe`
2. 点击"启动浏览器并登录"
3. 在浏览器中完成学习通登录
4. 点击"获取课程列表"
5. 选择课程，点击"开始学习"

### AI答题配置（可选）
默认使用本地策略答题。如需启用AI智能答题：
1. 点击"AI答题设置"
2. 选择服务商或填写自定义接口
3. 填写API Key和模型名称
4. 点击"测试连接"验证配置
5. 勾选"启用AI答题"并保存

详细说明请查看压缩包内的 `使用说明.txt` 和 `AI答题功能说明.md`

---

## ⚠️ 注意事项

### 首次使用
- 首次启动需要加载时间
- Windows 可能提示"未识别的应用"，点击"仍要运行"
- 杀毒软件可能误报，请添加白名单

### 数据安全
- 账号密码仅存本地
- 不会上传服务器
- 分享前请删除 config.json

---

## 🔧 常见问题

**Q: 程序无法启动？**  
A: 检查路径是否包含中文，尝试管理员运行，查看杀毒软件是否拦截

**Q: 登录后获取不到课程？**  
A: 请在浏览器中手动点击"我的课程"，然后重试"获取课程列表"

**Q: 视频播放卡住？**  
A: 可能遇到必须答对的题目，请查看浏览器手动答题或检查AI配置

**Q: AI答题不工作？**  
A: 请检查：1.是否启用AI 2.API Key是否正确 3.网络是否正常

更多问题请在 [Issues](https://github.com/gitub-creater/xuexitong-auto-learner/issues) 中反馈

---

## 📊 版本信息

- **版本号**: v2.0
- **发布日期**: 2026-09-03
- **压缩包大小**: 49 MB
- **解压后大小**: 约 130 MB

---

## 💬 问题反馈

如遇到问题，请在GitHub Issues中反馈，附上详细的错误日志（程序目录下的 `learning.log`）

---

**开发者**：大学在读生 丁辉  
**版权所有** © 2026 丁辉。保留所有权利。

---

**祝你学习顺利！** 🎓
```

---

## 📋 检查清单

发布前请确认：

- [ ] 版本号正确：v2.0
- [ ] 标题正确：v2.0 - Bug修复与优化版
- [ ] 描述完整，包含所有Bug修复说明
- [ ] 文件已上传：学习通自动学习助手_v2.0_绿色版.zip
- [ ] 文件大小正确：49 MB
- [ ] 设置为 Latest release

---

## 🎯 发布后

1. **验证下载**
   - 访问 Release 页面：https://github.com/gitub-creater/xuexitong-auto-learner/releases/tag/v2.0
   - 下载文件并测试
   - 确认文件完整

2. **分享链接**
   - Release页面：https://github.com/gitub-creater/xuexitong-auto-learner/releases/tag/v2.0
   - 直接下载：https://github.com/gitub-creater/xuexitong-auto-learner/releases/download/v2.0/学习通自动学习助手_v2.0_绿色版.zip

---

**准备就绪，可以发布了！** 🚀
