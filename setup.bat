@echo off
REM AI Gym Coach Setup Script for Windows
REM This script helps set up the development environment

echo ================================================
echo AI Gym Coach - Development Environment Setup
echo ================================================
echo.

REM Check for Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check for Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 20+ first.
    exit /b 1
)

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed. Please install Python 3.11+ first.
    exit /b 1
)

echo [OK] All required tools are installed
echo.

REM Create environment files
echo Setting up environment files...

if not exist "frontend\.env.local" (
    copy "frontend\.env.local.example" "frontend\.env.local"
    echo [OK] Created frontend\.env.local
) else (
    echo [WARNING] frontend\.env.local already exists, skipping
)

if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo [OK] Created backend\.env
    echo [WARNING] Please edit backend\.env and add your OPENAI_API_KEY
) else (
    echo [WARNING] backend\.env already exists, skipping
)

echo.

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..
echo [OK] Frontend dependencies installed
echo.

REM Install backend dependencies
echo Installing backend dependencies...
cd backend
if not exist "venv" (
    python -m venv venv
    echo [OK] Created Python virtual environment
)

call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..
echo [OK] Backend dependencies installed
echo.

REM Start Docker services
echo Starting Docker services (PostgreSQL and Redis)...
docker-compose up -d postgres redis
echo [OK] Docker services started
echo.

REM Wait for services
echo Waiting for services to be ready...
timeout /t 5 /nobreak >nul
echo [OK] Services are ready
echo.

echo ================================================
echo [OK] Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env and add your OPENAI_API_KEY
echo 2. Start the development servers:
echo    - Backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo    - Frontend: cd frontend ^&^& npm run dev
echo.
echo Or use Docker Compose to start everything:
echo    docker-compose up
echo.
echo Access the application:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Happy coding!
