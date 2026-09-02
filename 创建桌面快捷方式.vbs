Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

Desktop = WshShell.SpecialFolders("Desktop")
ProjectPath = fso.GetParentFolderName(WScript.ScriptFullName)
ShortcutPath = Desktop & "\学习通自动学习助手.lnk"

Set Shortcut = WshShell.CreateShortcut(ShortcutPath)
Shortcut.TargetPath = ProjectPath & "\启动学习通助手.vbs"
Shortcut.WorkingDirectory = ProjectPath
Shortcut.Description = "学习通自动学习助手 - 开发者：丁辉"
Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"
Shortcut.Save

MsgBox "桌面快捷方式已创建成功！", 64, "完成"
