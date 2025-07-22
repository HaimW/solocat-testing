@echo off
REM Audio Processing System - Windows Setup Script

echo 🪟 Setting up Audio Processing System for Windows...
echo ==================================================

REM Check Python version
echo 📋 Checking Python version...
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install minimal requirements first
echo 📥 Installing minimal requirements...
pip install -r pytest\requirements-minimal.txt

REM Try to install full requirements (with fallback)
echo 📥 Attempting to install full requirements...
pip install -r pytest\requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️ Some dependencies failed, using minimal setup
    echo This is normal on Windows without PostgreSQL libraries
)

REM Create directories
echo 📁 Creating necessary directories...
if not exist logs mkdir logs
if not exist test-reports mkdir test-reports
if not exist performance_results mkdir performance_results

echo.
echo ✅ Setup completed!
echo.
echo 🚀 Quick start:
echo    .venv\Scripts\activate
echo    python pytest\demo_test.py
echo.
echo 📖 For more options, see:
echo    scripts\run_tests.bat
echo    type pytest\RUN_TESTS.md

pause 