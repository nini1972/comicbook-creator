@echo off
cd /d "%~dp0backend"
uv run python tests\test_full_run.py
pause
