# Quick Start Guide

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose (recommended)

## Option 1: Docker Compose (Recommended)

### 1. Clone and Setup
```bash
cd "d:\6th SEM\SDM_Project\project"
```

### 2. Configure Environment Variables

**Backend** - Create `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_gym_coach
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key-optional
ENVIRONMENT=development
```

**Frontend** - Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENV=development
```

### 3. Start All Services
```bash
docker-compose up
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## Option 2: Manual Setup

### Backend Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Start PostgreSQL and Redis**
```bash
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ai_gym_coach postgres:16-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

3. **Run Database Migrations**
```bash
# The schema is created automatically on first run
# Or manually run:
psql -U postgres -d ai_gym_coach -f scripts/001_create_schema.sql
```

4. **Start Backend Server**
```bash
python -m uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

---

## First Time Usage

### 1. Register an Account
- Navigate to http://localhost:3000
- Click "AI Workout Planner" or "Chat with AI Coach"
- Use the registration form
- Password requirements: 8+ chars, uppercase, lowercase, number
- Example: `Test@123`

### 2. Complete Your Profile
- Go to "Your Profile & Stats"
- Add weight, height, body type
- Set fitness goals

### 3. Generate a Workout Plan
- Click "AI Workout Planner"
- Click "Generate New Plan"
- View your personalized 7-day plan

### 4. Start a Workout
- Click "Start Workout Session"
- Allow camera access
- Select an exercise (Push-ups, Squats, Planks, Jumping Jacks)
- Follow the on-screen instructions
- View your summary after completion

### 5. Chat with AI Coach
- Click "Chat with AI Coach"
- Ask questions about form, nutrition, or motivation
- The coach has access to your profile and workout history

---

## Testing the Application

### Test User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "weight_kg": 70,
    "height_cm": 175,
    "body_type": "mesomorph",
    "fitness_goals": ["strength", "endurance"]
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### View API Documentation
Open http://localhost:8000/docs for interactive API documentation

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Error
```bash
# Verify PostgreSQL is running
docker ps | findstr postgres

# Check connection
psql -U postgres -h localhost -p 5432
```

### Camera Not Working
- Ensure you're using HTTPS or localhost
- Check browser permissions
- Try a different browser (Chrome/Edge recommended)
- Ensure good lighting

### OpenAI API Errors
- The app works without an API key (uses mock responses)
- To use real AI features, add your OpenAI API key to backend/.env
- Get a key from https://platform.openai.com/api-keys

---

## Development Commands

### Backend
```bash
# Run tests
pytest

# Run linter
flake8 app/

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### Frontend
```bash
# Run tests
npm run test

# Run linter
npm run lint

# Format code
npm run format

# Build for production
npm run build
```

---

## Project Structure

```
project/
├── frontend/              # Next.js application
│   ├── src/
│   │   ├── app/          # Pages (Next.js 14 app router)
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and API clients
│   │   └── types/        # TypeScript type definitions
│   └── public/           # Static assets
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API route handlers
│   │   ├── core/        # Config, security, database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── scripts/         # Database migrations
│   └── tests/           # Test suite
│
├── docker-compose.yml   # Container orchestration
├── README.md           # This file
└── FINAL_COMPLETION_REPORT.md  # Detailed status
```

---

## Key Features

✅ **Real-time Pose Detection** - MediaPipe BlazePose running in browser
✅ **Exercise Recognition** - Push-ups, Squats, Planks, Jumping Jacks
✅ **Form Analysis** - Real-time feedback on exercise form
✅ **AI Workout Plans** - Personalized 7-day plans
✅ **AI Coach Chat** - Context-aware coaching
✅ **Streak Tracking** - Maintain workout consistency
✅ **Progress Statistics** - Track your improvement
✅ **Privacy-First** - All pose detection runs locally

---

## Support

For issues or questions:
1. Check `FINAL_COMPLETION_REPORT.md` for detailed documentation
2. Review `ARCHITECTURE.md` for system design
3. Check `backend/API_ENDPOINTS.md` for API reference
4. Review `TESTING_SUMMARY.md` for test information

---

## License

See LICENSE file for details.

---

**Last Updated**: 2026-02-13
**Version**: 1.0.0
