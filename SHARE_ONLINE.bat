@echo off
title Khedut AI - Public Online Launch
cd /d "%~dp0"

echo ========================================================================
echo        KHEDUT AI - WORLDWIDE PUBLIC URL LAUNCHER
echo ========================================================================
echo Starting PyTorch AI backend and creating secure public HTTPS link...
echo.

python run_app.py
pause
