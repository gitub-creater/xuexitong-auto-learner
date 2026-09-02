@echo off
chcp 65001 >nul
title 学习通自动学习助手
cd /d "%~dp0"
python main.py
pause
