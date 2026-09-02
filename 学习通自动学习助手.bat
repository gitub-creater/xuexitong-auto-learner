@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动学习通自动学习助手...
python main.py
pause
