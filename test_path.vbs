Set WshShell = CreateObject("WScript.Shell")
Desktop = WshShell.SpecialFolders("Desktop")
WScript.Echo "Desktop path: " & Desktop
