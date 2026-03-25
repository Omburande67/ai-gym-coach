#!/bin/bash

# AI Gym Coach Setup Script
# This script helps set up the development environment

set -e

echo "🏋️ AI Gym Coach - Development Environment Setup"
echo "================================================"
echo ""

# Check for required tools
echo "Checking for required tools..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ All required tools are installed"
echo ""

# Create environment files
echo "Setting up environment files..."

if [ ! -f "frontend/.env.local" ]; then
    cp frontend/.env.local.example frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "⚠️  frontend/.env.local already exists, skipping"
fi

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env"
    echo "⚠️  Please edit backend/.env and add your OPENAI_API_KEY"
else
    echo "⚠️  backend/.env already exists, skipping"
fi

echo ""

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✅ Frontend dependencies installed"
echo ""

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt
cd ..
echo "✅ Backend dependencies installed"
echo ""

# Start Docker services
echo "Starting Docker services (PostgreSQL and Redis)..."
docker-compose up -d postgres redis
echo "✅ Docker services started"
echo ""

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5
echo "✅ Services are ready"
echo ""

echo "================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your OPENAI_API_KEY"
echo "2. Start the development servers:"
echo "   - Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   - Frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose to start everything:"
echo "   docker-compose up"
echo ""
echo "Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🚀"
