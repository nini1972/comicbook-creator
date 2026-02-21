@echo off
echo Clearing Python cache...
cd /d "%~dp0backend"

:: Remove __pycache__ directories
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: Remove .pyc files
del /s /q *.pyc 2>nul

echo Python cache cleared.
echo.
echo Starting test with UV...
uv run python tests\test_full_run.py
pause
