# 创建学习通自动学习助手桌面快捷方式
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$desktop = [Environment]::GetFolderPath("Desktop")
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$shortcutPath = Join-Path $desktop "学习通自动学习助手.lnk"
$targetPath = Join-Path $appDir "启动学习通助手.bat"

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $appDir
$shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"
$shortcut.Description = "学习通自动学习助手 - 开发者：丁辉"
$shortcut.Save()

Write-Host "✓ 桌面快捷方式已创建" -ForegroundColor Green
Write-Host "位置: $shortcutPath" -ForegroundColor Cyan
