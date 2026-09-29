@echo off
title Khedut AI - Smart Farming Assistant
cd /d "%~dp0"

echo ========================================================
echo        KHEDUT AI - FULL-STACK AI APPLICATION LAUNCH
echo ========================================================
echo Starting AI backend and opening application in browser...
echo.

python run_app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start Khedut AI.
    echo Please make sure Python is installed and run: python run_app.py
    pause
)
