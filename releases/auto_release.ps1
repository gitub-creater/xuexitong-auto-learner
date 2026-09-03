# GitHub 自动发布脚本
# 需要先安装 GitHub CLI: https://cli.github.com/
# 或使用: winget install --id GitHub.cli

# 配置
$version = "v2.0.0"
$title = "v2.0.0 - AI 智能答题 + 绿色免安装版"
$zipFile = "releases\学习通自动学习助手_v2.0.0_绿色版.zip"
$notesFile = "RELEASE_NOTES.md"

# 检查文件是否存在
if (-not (Test-Path $zipFile)) {
    Write-Host "✗ 错误: 找不到打包文件 $zipFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $notesFile)) {
    Write-Host "✗ 错误: 找不到发布说明 $notesFile" -ForegroundColor Red
    exit 1
}

# 检查 gh 是否已安装
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghInstalled) {
    Write-Host "✗ 错误: 未安装 GitHub CLI" -ForegroundColor Red
    Write-Host "请访问 https://cli.github.com/ 下载安装" -ForegroundColor Yellow
    exit 1
}

# 检查是否已登录
Write-Host "检查 GitHub 登录状态..." -ForegroundColor Cyan
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "请先登录 GitHub: gh auth login" -ForegroundColor Yellow
    exit 1
}

# 创建 Release
Write-Host "
创建 GitHub Release..." -ForegroundColor Cyan
gh release create $version `
    --title $title `
    --notes-file $notesFile `
    $zipFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "
✓ Release 创建成功！" -ForegroundColor Green
    Write-Host "查看: https://github.com/gitub-creater/xuexitong-auto-learner/releases/tag/$version" -ForegroundColor Green
} else {
    Write-Host "
✗ Release 创建失败" -ForegroundColor Red
    exit 1
}
