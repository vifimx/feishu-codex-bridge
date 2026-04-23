@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Open-FeishuCodexBridgeDashboard.ps1" %*
