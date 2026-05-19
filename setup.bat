@echo off
REM Funda Malitinne LMS - Local Development Setup Script (Windows)

echo.
echo ==================================================
echo Funda Malitinne LMS - Development Setup
echo ==================================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed

REM Create .env file if not exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env with your settings
) else (
    echo .env file already exists
)

REM Create directories
if not exist "media" mkdir media
if not exist "staticfiles" mkdir staticfiles
if not exist "logs" mkdir logs
echo Directories created

REM Run migrations
echo Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo Error: Migrations failed
    pause
    exit /b 1
)
echo Migrations completed

REM Create demo data
echo Creating demo data...
python manage.py create_demo_data
if errorlevel 1 (
    echo Error: Failed to create demo data
    pause
    exit /b 1
)
echo Demo data created

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo Error: Failed to collect static files
    pause
    exit /b 1
)
echo Static files collected

echo.
echo ==================================================
echo Setup Complete!
echo ==================================================
echo.
echo To start the development server, run:
echo   venv\Scripts\activate.bat (if not already activated)
echo   python manage.py runserver
echo.
echo Admin credentials:
echo   Username: admin
echo   Password: admin123456
echo.
echo Access the application at: http://localhost:8000
echo.
pause
