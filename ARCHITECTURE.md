# AI Gym Coach - Architecture Documentation

## Overview

The AI Gym Coach is a privacy-first, real-time workout recognition platform built with a modern client-server architecture. This document provides a detailed overview of the system architecture, design decisions, and implementation details.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (Frontend)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Camera     │→ │ Pose Detector│→ │  Visualizer  │      │
│  │   Access     │  │ (TF.js +     │  │  (Canvas)    │      │
│  └──────────────┘  │  BlazePose)  │  └──────────────┘      │
│                     └──────┬───────┘                         │
│                            │ Keypoints Only                  │
│                            ↓                                 │
│                     ┌──────────────┐                         │
│                     │  WebSocket   │                         │
│                     │    Client    │                         │
│                     └──────┬───────┘                         │
└────────────────────────────┼─────────────────────────────────┘
                             │ WSS (Keypoints)
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  WebSocket   │→ │  Exercise    │→ │ Rep Counter  │      │
│  │   Handler    │  │  Recognizer  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Form      │  │   AI Coach   │  │  Workout     │      │
│  │   Analyzer   │  │   (LLM API)  │  │  Planner     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Notification │  │     User     │  │  PostgreSQL  │      │
│  │   Service    │  │  Management  │  │   Database   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend

- **Framework**: Next.js 14 with React 18
- **Language**: TypeScript
- **Pose Detection**: TensorFlow.js with MediaPipe BlazePose
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Testing**: Jest + React Testing Library + fast-check
- **Build Tool**: Next.js built-in (Webpack/Turbopack)

### Backend

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt
- **LLM Integration**: OpenAI API
- **Testing**: pytest + Hypothesis
- **Code Quality**: Black, isort, flake8, mypy

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Web Server**: Uvicorn (ASGI)
- **Reverse Proxy**: Nginx (production)
- **CI/CD**: GitHub Actions (planned)

## Design Principles

### 1. Privacy-First Architecture

**Problem**: Users are uncomfortable with video being recorded or transmitted.

**Solution**: 
- All video processing happens in the browser using TensorFlow.js
- Only skeletal keypoints (33 3D coordinates) are extracted
- Raw video frames are immediately deleted after processing
- No video data is stored or transmitted over the network

**Implementation**:
```typescript
// Frontend: Pose detection
const poses = await detector.estimatePoses(videoElement);
const keypoints = poses[0].keypoints; // Extract only keypoints
// Video frame is automatically garbage collected
```

### 2. Real-Time Performance

**Problem**: Workout feedback must be immediate to be useful.

**Solution**:
- Target <500ms latency for pose detection
- WebSocket for bidirectional real-time communication
- Efficient rule-based algorithms for exercise recognition
- Client-side rendering for instant UI updates

**Performance Targets**:
- Pose detection: 15-30 FPS
- WebSocket latency: <100ms
- Exercise recognition: <3 seconds
- Form feedback: <1 second

### 3. Modular Exercise System

**Problem**: Adding new exercises should not require code changes.

**Solution**:
- Exercise definitions stored in configuration files
- Rule-based system with configurable thresholds
- Pluggable architecture for exercise recognizers

**Example Exercise Definition**:
```json
{
  "name": "pushup",
  "angles": {
    "elbow": { "up": 160, "down": 90 },
    "hip": { "min": 165, "max": 185 }
  },
  "form_rules": [
    {
      "type": "hip_sag",
      "threshold": 15,
      "message": "Engage your core"
    }
  ]
}
```

### 4. Rule-Based MVP

**Problem**: ML models are complex, slow, and require training data.

**Solution**:
- Use deterministic biomechanical rules for MVP
- Faster, more reliable, and easier to debug
- Can be replaced with ML in future versions

**Benefits**:
- No training data required
- Predictable behavior
- Easy to understand and modify
- Lower computational requirements

## Data Flow

### 1. Video Capture → Pose Detection (Browser)

```
User grants camera permission
    ↓
WebRTC captures video frames at 30 FPS
    ↓
TensorFlow.js + BlazePose extracts 33 keypoints
    ↓
Raw frame immediately discarded
    ↓
Keypoints sent to backend via WebSocket
```

### 2. Exercise Recognition (Backend)

```
Receive keypoint stream
    ↓
Calculate joint angles (elbow, knee, hip, shoulder)
    ↓
Match angle patterns against exercise definitions
    ↓
Return exercise type to frontend
```

### 3. Rep Counting (Backend)

```
Track biomechanical angles over time
    ↓
Detect state transitions (up→down→up)
    ↓
Validate full range of motion
    ↓
Increment counter and notify frontend
```

### 4. Form Analysis (Backend)

```
Evaluate posture against ideal form rules
    ↓
Detect common mistakes (hip sag, knee cave, etc.)
    ↓
Calculate form score
    ↓
Send corrective feedback to frontend
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    body_type VARCHAR(50),
    fitness_goals TEXT[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Workout Sessions Table
```sql
CREATE TABLE workout_sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_duration_seconds INT,
    total_reps INT,
    average_form_score DECIMAL(5,2),
    created_at TIMESTAMP
);
```

### Exercise Records Table
```sql
CREATE TABLE exercise_records (
    record_id UUID PRIMARY KEY,
    session_id UUID REFERENCES workout_sessions(session_id),
    exercise_type VARCHAR(50) NOT NULL,
    reps_completed INT,
    duration_seconds INT,
    form_score DECIMAL(5,2),
    mistakes JSONB,
    created_at TIMESTAMP
);
```

## API Design

### REST Endpoints

```
POST   /api/auth/register          # User registration
POST   /api/auth/login             # User login
GET    /api/users/profile          # Get user profile
PUT    /api/users/profile          # Update user profile
GET    /api/workouts               # Get workout history
GET    /api/workouts/{id}          # Get specific workout
POST   /api/workout-plans/generate # Generate workout plan
GET    /api/workout-plans          # List workout plans
POST   /api/chat/message           # Send chat message
```

### WebSocket Protocol

**Client → Server**:
```json
{
  "type": "pose_data",
  "timestamp": 1234567890,
  "keypoints": [...]
}
```

**Server → Client**:
```json
{
  "type": "exercise_detected",
  "exercise": "pushup",
  "confidence": 0.95
}

{
  "type": "rep_counted",
  "count": 5
}

{
  "type": "form_feedback",
  "mistakes": [...],
  "form_score": 85
}
```

## Security

### Authentication
- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- HTTP-only cookies for token storage

### Authorization
- Users can only access their own data
- Admin role for system management
- Rate limiting: 100 requests/minute per user

### Data Protection
- HTTPS/WSS for all communication
- Password hashing with bcrypt (cost: 12)
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization

## Testing Strategy

### Unit Tests
- Test individual functions and components
- Mock external dependencies
- Focus on edge cases and error conditions

### Property-Based Tests
- Test universal properties across all inputs
- Use Hypothesis (Python) and fast-check (TypeScript)
- Validate invariants and correctness properties

### Integration Tests
- Test API endpoints end-to-end
- Test WebSocket communication
- Test database operations

### Performance Tests
- Load testing with 100+ concurrent users
- Measure WebSocket latency
- Monitor CPU and memory usage

## Deployment

### Development
```bash
docker-compose up
```

### Production
- Docker containers on cloud provider (AWS/GCP)
- Nginx reverse proxy
- PostgreSQL with read replicas
- Redis for caching
- CDN for static assets

## Future Enhancements

### Phase 2
- ML-based exercise recognition (LSTM/Transformer)
- Additional exercises (lunges, burpees, etc.)
- Social features (challenges, leaderboards)
- Wearable integration (heart rate data)
- Nutrition tracking
- Mobile app (React Native)

### Technical Improvements
- GraphQL API for flexible data fetching
- Progressive Web App (PWA)
- Offline mode with service workers
- E2E tests with Playwright
- Performance monitoring with Datadog

## Conclusion

The AI Gym Coach architecture prioritizes privacy, performance, and modularity. The privacy-first design ensures user trust, while the real-time architecture provides immediate feedback. The modular exercise system allows for easy expansion, and the rule-based MVP approach ensures reliability and maintainability.
