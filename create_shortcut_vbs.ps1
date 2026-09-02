$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "学习通自动学习助手.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Users\丁辉\.zcode\workspace\default\xuexitong-auto-learner\启动学习通助手.vbs"
$Shortcut.WorkingDirectory = "C:\Users\丁辉\.zcode\workspace\default\xuexitong-auto-learner"
$Shortcut.Description = "学习通自动学习助手 - 开发者：丁辉"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"
$Shortcut.Save()

Write-Host "桌面快捷方式已更新（VBS版本，无安全警告）"
