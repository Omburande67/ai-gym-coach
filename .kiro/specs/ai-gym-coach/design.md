# Design Document: AI Gym Coach System

## Overview

The AI Gym Coach is a privacy-first, real-time workout recognition platform that combines computer vision, biomechanical analysis, and conversational AI to provide personalized fitness coaching. The system architecture follows a client-server model where video processing occurs entirely in the browser to ensure privacy, while the backend handles exercise recognition, form analysis, workout planning, and data persistence.

### Key Design Principles

1. **Privacy-First Architecture**: Raw video frames never leave the user's device. Only skeletal keypoints are transmitted.
2. **Real-Time Performance**: Target <500ms latency for pose detection and <1s for form feedback.
3. **Modular Exercise System**: Extensible architecture allowing new exercises to be added through configuration rather than code changes.
4. **Rule-Based MVP**: Use deterministic biomechanical rules for exercise recognition and form analysis (faster, more reliable than ML for MVP).
5. **Progressive Enhancement**: Core functionality works offline; enhanced features require backend connectivity.

### Technology Stack

**Frontend:**
- React/Next.js for UI framework
- TensorFlow.js with MediaPipe BlazePose for browser-based pose detection
- WebRTC API for camera access
- Canvas API for skeleton overlay visualization
- WebSocket client for real-time communication

**Backend:**
- FastAPI (Python) for REST API and WebSocket server
- PostgreSQL for user data and workout history
- Redis for session management and caching
- OpenAI API (or similar LLM) for AI Coach and workout plan generation

**Infrastructure:**
- Docker for containerization
- Nginx for reverse proxy and load balancing
- AWS/GCP for cloud hosting (optional)

## Architecture

### System Components

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

### Data Flow

1. **Video Capture → Pose Detection (Browser)**
   - User grants camera permission
   - WebRTC captures video frames at 30 FPS
   - TensorFlow.js + BlazePose extracts 33 3D keypoints per frame
   - Raw frame immediately discarded from memory
   - Keypoints sent to backend via WebSocket

2. **Exercise Recognition (Backend)**
   - Receives keypoint stream
   - Calculates joint angles (elbow, knee, hip, shoulder)
   - Matches angle patterns against exercise definitions
   - Returns exercise type to frontend

3. **Rep Counting (Backend)**
   - Tracks biomechanical angles over time
   - Detects state transitions (up→down→up)
   - Validates full range of motion
   - Increments counter and notifies frontend

4. **Form Analysis (Backend)**
   - Evaluates posture against ideal form rules
   - Detects common mistakes (hip sag, knee cave, elbow flare)
   - Calculates form score
   - Sends corrective feedback to frontend

5. **Post-Workout Summary (Backend)**
   - Aggregates session data (reps, duration, form scores)
   - Identifies top mistakes
   - Generates recommendations
   - Stores in database

6. **AI Coaching (Backend)**
   - User sends chat message or requests workout plan
   - Backend queries LLM API with user context
   - LLM generates personalized response
   - Response sent to frontend

## Components and Interfaces

### 1. Pose Detector (Frontend)

**Responsibility:** Extract skeletal keypoints from video frames in real-time.

**Technology:** TensorFlow.js with MediaPipe BlazePose model

**Interface:**
```typescript
interface PoseKeypoint {
  x: number;        // Normalized 0-1
  y: number;        // Normalized 0-1
  z: number;        // Depth relative to hips
  visibility: number; // Confidence 0-1
  name: string;     // Joint name (e.g., "left_elbow")
}

interface PoseData {
  keypoints: PoseKeypoint[]; // 33 keypoints
  timestamp: number;          // Unix timestamp ms
}

class PoseDetector {
  async initialize(): Promise<void>;
  async detectPose(videoFrame: HTMLVideoElement): Promise<PoseData>;
  dispose(): void;
}
```

**Implementation Details:**
- Load BlazePose model on component mount
- Process frames at 15-30 FPS (configurable)
- Use requestAnimationFrame for smooth processing
- Implement frame skipping if processing falls behind
- Validate keypoint visibility before transmission

### 2. Exercise Recognizer (Backend)

**Responsibility:** Identify which exercise the user is performing based on pose keypoints.

**Approach:** Rule-based classification using joint angle patterns

**Interface:**
```python
from enum import Enum
from typing import List, Optional

class ExerciseType(Enum):
    PUSHUP = "pushup"
    SQUAT = "squat"
    PLANK = "plank"
    JUMPING_JACK = "jumping_jack"
    UNKNOWN = "unknown"

class ExerciseRecognizer:
    def recognize(self, pose_data: PoseData) -> ExerciseType:
        """Classify exercise based on pose keypoints."""
        pass
    
    def get_confidence(self) -> float:
        """Return confidence score 0-1 for current classification."""
        pass
```

**Recognition Rules:**

**Push-ups:**
- Body horizontal (torso angle 0-20° from ground)
- Hands on ground (wrist y-coordinate near ground)
- Elbow angle oscillating 90-180°
- Feet stationary

**Squats:**
- Body vertical (torso angle 70-90° from ground)
- Feet shoulder-width apart
- Knee angle oscillating 90-170°
- Hands free or at chest

**Plank:**
- Body horizontal (torso angle 0-20° from ground)
- Forearms or hands on ground
- Minimal movement (velocity < threshold)
- Sustained position

**Jumping Jacks:**
- Body vertical (torso angle 70-90° from ground)
- Arms oscillating (shoulder angle 30-180°)
- Legs oscillating (hip angle changes)
- Rhythmic pattern detected

**Implementation Strategy:**
- Calculate angles using 3-point joint positions
- Use sliding window (2-3 seconds) to detect patterns
- Require 80% confidence over window before classification
- Prioritize most distinctive features first

### 3. Rep Counter (Backend)

**Responsibility:** Count exercise repetitions using biomechanical state machines.

**Interface:**
```python
from enum import Enum

class RepPhase(Enum):
    UP = "up"
    DOWN = "down"
    TRANSITION = "transition"

class RepCounter:
    def __init__(self, exercise_type: ExerciseType):
        self.exercise_type = exercise_type
        self.count = 0
        self.current_phase = RepPhase.UP
        
    def update(self, pose_data: PoseData) -> Optional[int]:
        """
        Update state machine with new pose data.
        Returns new rep count if rep completed, else None.
        """
        pass
    
    def reset(self) -> None:
        """Reset counter to zero."""
        pass
    
    def get_count(self) -> int:
        """Return current rep count."""
        return self.count
```

**State Machine Logic:**

**Push-ups:**
- **UP State:** Elbow angle > 160°
- **DOWN State:** Elbow angle < 90°
- **Transition:** UP → DOWN → UP = 1 rep
- **Validation:** Torso remains straight (hip angle deviation < 15°)

**Squats:**
- **UP State:** Knee angle > 160°
- **DOWN State:** Knee angle < 90° (parallel or below)
- **Transition:** UP → DOWN → UP = 1 rep
- **Validation:** Knees track over toes (alignment check)

**Jumping Jacks:**
- **UP State:** Arms above 160° (overhead)
- **DOWN State:** Arms below 30° (at sides)
- **Transition:** DOWN → UP → DOWN = 1 rep
- **Validation:** Legs also oscillating

**Plank:**
- No rep counting (duration-based)
- Track hold time in seconds

**Implementation Details:**
- Use hysteresis to prevent double-counting (require 10° buffer)
- Implement debouncing (minimum 0.5s between reps)
- Validate full range of motion before counting
- Track partial reps separately for feedback

### 4. Form Analyzer (Backend)

**Responsibility:** Evaluate exercise form and detect common mistakes.

**Interface:**
```python
from typing import List, Dict

class FormMistake:
    def __init__(self, mistake_type: str, severity: float, suggestion: str):
        self.mistake_type = mistake_type
        self.severity = severity  # 0-1
        self.suggestion = suggestion

class FormAnalyzer:
    def analyze(self, pose_data: PoseData, exercise_type: ExerciseType) -> List[FormMistake]:
        """Detect form mistakes in current pose."""
        pass
    
    def calculate_form_score(self, mistakes: List[FormMistake]) -> float:
        """Calculate overall form score 0-100."""
        pass
```

**Form Rules by Exercise:**

**Push-ups:**
1. **Hip Sag:** Hip y-coordinate > shoulder y-coordinate by >10cm → "Engage your core, keep hips in line"
2. **Hip Pike:** Hip y-coordinate < shoulder y-coordinate by >10cm → "Lower your hips to maintain straight line"
3. **Elbow Flare:** Elbow angle from torso > 45° → "Tuck elbows closer to body"
4. **Partial Range:** Elbow never reaches <100° → "Go deeper, aim for 90° elbow bend"
5. **Head Drop:** Neck angle > 30° → "Keep neck neutral, look slightly forward"

**Squats:**
1. **Knee Cave:** Knee x-coordinate moves inward past toe → "Push knees outward, track over toes"
2. **Shallow Depth:** Knee angle never reaches <100° → "Go deeper, aim for parallel or below"
3. **Forward Lean:** Torso angle < 60° from vertical → "Keep chest up, don't lean too far forward"
4. **Heel Lift:** Ankle angle changes significantly → "Keep heels planted on ground"
5. **Knee Over Toe:** Knee x-coordinate > toe x-coordinate by >5cm → "Sit back more, don't let knees shoot forward"

**Plank:**
1. **Hip Sag:** Hip y-coordinate > shoulder y-coordinate by >5cm → "Engage core, lift hips"
2. **Hip Pike:** Hip y-coordinate < shoulder y-coordinate by >5cm → "Lower hips to straight line"
3. **Shoulder Collapse:** Shoulder y-coordinate drops → "Push through shoulders, stay strong"

**Jumping Jacks:**
1. **Incomplete Arms:** Arms never reach >150° → "Raise arms fully overhead"
2. **Incomplete Legs:** Legs don't spread wide enough → "Jump wider, spread legs more"

**Form Score Calculation:**
```
Base Score = 100
For each mistake:
  - Minor (severity 0-0.3): -5 points
  - Moderate (severity 0.3-0.7): -10 points
  - Severe (severity 0.7-1.0): -20 points
Final Score = max(0, Base Score - deductions)
```

### 5. WebSocket Handler (Backend)

**Responsibility:** Manage real-time bidirectional communication between frontend and backend.

**Interface:**
```python
from fastapi import WebSocket
from typing import Callable

class WorkoutSession:
    def __init__(self, user_id: str, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket
        self.exercise_recognizer = ExerciseRecognizer()
        self.rep_counter: Optional[RepCounter] = None
        self.form_analyzer = FormAnalyzer()
        self.current_exercise: Optional[ExerciseType] = None
        
    async def handle_pose_data(self, pose_data: PoseData) -> None:
        """Process incoming pose data and send feedback."""
        pass
    
    async def send_feedback(self, feedback: Dict) -> None:
        """Send feedback to frontend."""
        pass

class WebSocketManager:
    def __init__(self):
        self.active_sessions: Dict[str, WorkoutSession] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept WebSocket connection and create session."""
        pass
    
    async def disconnect(self, user_id: str) -> None:
        """Close WebSocket and cleanup session."""
        pass
```

**Message Protocol:**

**Client → Server:**
```json
{
  "type": "pose_data",
  "timestamp": 1234567890,
  "keypoints": [
    {"name": "nose", "x": 0.5, "y": 0.3, "z": 0.0, "visibility": 0.99},
    ...
  ]
}
```

**Server → Client:**
```json
{
  "type": "exercise_detected",
  "exercise": "pushup",
  "confidence": 0.95
}

{
  "type": "rep_counted",
  "count": 5,
  "total": 5
}

{
  "type": "form_feedback",
  "mistakes": [
    {
      "type": "hip_sag",
      "severity": 0.6,
      "suggestion": "Engage your core, keep hips in line"
    }
  ],
  "form_score": 85
}
```

### 6. AI Coach (Backend)

**Responsibility:** Provide conversational AI coaching and generate personalized workout plans.

**Interface:**
```python
from typing import Dict, List

class AICoach:
    def __init__(self, llm_api_key: str):
        self.llm_client = OpenAI(api_key=llm_api_key)
        
    async def chat(self, user_id: str, message: str, context: Dict) -> str:
        """
        Generate conversational response to user message.
        Context includes user profile and recent workout history.
        """
        pass
    
    async def generate_workout_plan(
        self, 
        user_profile: UserProfile,
        duration_minutes: int,
        focus_areas: List[str]
    ) -> WorkoutPlan:
        """Generate personalized workout plan."""
        pass
```

**System Prompt for Chat:**
```
You are an enthusiastic and supportive AI fitness coach. Your personality is:
- Motivating and encouraging, never judgmental
- Knowledgeable about exercise science and proper form
- Empathetic to user struggles and challenges
- Celebratory of user achievements, no matter how small
- Clear and concise in explanations
- Safety-focused, always prioritizing injury prevention

User Context:
- Name: {name}
- Goals: {goals}
- Recent workouts: {workout_summary}
- Current streak: {streak} days

Respond to the user's message with helpful, personalized advice.
```

**Workout Plan Generation Prompt:**
```
Generate a personalized workout plan with the following parameters:

User Profile:
- Weight: {weight} kg
- Height: {height} cm
- Body Type: {body_type}
- Fitness Level: {fitness_level}
- Goals: {goals}
- Available Time: {duration} minutes
- Equipment: Bodyweight only
- Focus Areas: {focus_areas}

Create a structured workout plan with:
1. Warm-up (5 minutes)
2. Main workout (exercises with sets/reps)
3. Cool-down (5 minutes)

Supported exercises: push-ups, squats, plank, jumping jacks

Return as JSON:
{
  "warmup": [...],
  "exercises": [
    {"name": "pushup", "sets": 3, "reps": 10, "rest_seconds": 60},
    ...
  ],
  "cooldown": [...]
}
```

### 7. User Management (Backend)

**Responsibility:** Handle authentication, user profiles, and workout history.

**Interface:**
```python
from pydantic import BaseModel
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    email: str
    password_hash: str
    weight_kg: float
    height_cm: float
    body_type: str  # ectomorph, mesomorph, endomorph
    fitness_goals: List[str]
    created_at: datetime
    
class WorkoutHistory(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    exercises: List[Dict]  # Exercise type, reps, form scores
    total_reps: int
    average_form_score: float
    mistakes: List[Dict]
    
class UserService:
    async def register(self, email: str, password: str, profile_data: Dict) -> UserProfile:
        """Create new user account."""
        pass
    
    async def authenticate(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and return session token."""
        pass
    
    async def get_profile(self, user_id: str) -> UserProfile:
        """Retrieve user profile."""
        pass
    
    async def update_profile(self, user_id: str, updates: Dict) -> UserProfile:
        """Update user profile data."""
        pass
    
    async def save_workout(self, workout: WorkoutHistory) -> None:
        """Save completed workout to history."""
        pass
    
    async def get_workout_history(self, user_id: str, limit: int = 10) -> List[WorkoutHistory]:
        """Retrieve recent workout history."""
        pass
```

### 8. Notification Service (Backend)

**Responsibility:** Manage workout reminders, streak tracking, and motivational notifications.

**Interface:**
```python
from datetime import time

class NotificationPreferences(BaseModel):
    user_id: str
    enabled: bool
    workout_times: List[time]  # Scheduled workout times
    reminder_minutes_before: int
    missed_workout_reminder: bool
    
class NotificationService:
    async def schedule_reminder(self, user_id: str, workout_time: time) -> None:
        """Schedule workout reminder notification."""
        pass
    
    async def send_reminder(self, user_id: str, message: str) -> None:
        """Send notification to user."""
        pass
    
    async def update_streak(self, user_id: str) -> int:
        """Update and return current workout streak."""
        pass
    
    async def check_missed_workouts(self) -> None:
        """Background job to check for missed workouts and send reminders."""
        pass
```

**Streak Logic:**
- Streak increments when user completes at least one workout in a day
- Streak resets to 0 if user misses a full day (no workouts)
- Grace period: 36 hours between workouts before streak breaks
- Milestone notifications at 7, 14, 30, 60, 90 days

## Data Models

### Database Schema (PostgreSQL)

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    body_type VARCHAR(50),
    fitness_goals TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Workout sessions table
CREATE TABLE workout_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_duration_seconds INT,
    total_reps INT DEFAULT 0,
    average_form_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exercise records table (one per exercise in a session)
CREATE TABLE exercise_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES workout_sessions(session_id) ON DELETE CASCADE,
    exercise_type VARCHAR(50) NOT NULL,
    reps_completed INT DEFAULT 0,
    duration_seconds INT,
    form_score DECIMAL(5,2),
    mistakes JSONB,  -- Array of mistake objects
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workout streaks table
CREATE TABLE workout_streaks (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    last_workout_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification preferences table
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    workout_times TIME[],
    reminder_minutes_before INT DEFAULT 30,
    missed_workout_reminder BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Workout plans table
CREATE TABLE workout_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    plan_name VARCHAR(255),
    plan_data JSONB NOT NULL,  -- Full workout plan structure
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_workout_sessions_user_id ON workout_sessions(user_id);
CREATE INDEX idx_workout_sessions_start_time ON workout_sessions(start_time);
CREATE INDEX idx_exercise_records_session_id ON exercise_records(session_id);
```

### Frontend State Management

```typescript
// Global app state (React Context or Redux)
interface AppState {
  user: UserProfile | null;
  currentSession: WorkoutSession | null;
  isWorkoutActive: boolean;
  cameraPermission: 'granted' | 'denied' | 'prompt';
  websocketStatus: 'connected' | 'disconnected' | 'connecting';
}

interface WorkoutSession {
  sessionId: string;
  startTime: number;
  currentExercise: ExerciseType | null;
  repCount: number;
  formScore: number;
  recentMistakes: FormMistake[];
  duration: number;
}

interface UserProfile {
  userId: string;
  email: string;
  weightKg: number;
  heightCm: number;
  bodyType: string;
  fitnessGoals: string[];
  currentStreak: number;
}
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several redundant properties were identified:
- Requirements 1.3 and 11.3 both test frame deletion after extraction (consolidated)
- Requirements 1.2 and 12.1 both test pose detection latency (consolidated)
- Requirements 5.5 and 15.3 both test out-of-frame detection (consolidated)
- Multiple form analysis properties (4.3-4.6) can be generalized into a single configurable form rule property
- Multiple rep counting properties (3.3-3.5) can be generalized into a single exercise-specific counting property

The following properties represent the unique, non-redundant correctness guarantees for the system:

### Privacy and Data Protection Properties

**Property 1: Frame Deletion After Extraction**
*For any* video frame processed by the Pose_Detector, after Pose_Keypoints are extracted, the raw frame data shall be immediately deleted from memory and shall not be accessible.
**Validates: Requirements 1.3, 11.3**

**Property 2: No Video Frame Transmission**
*For any* network request sent by the System, the payload shall not contain raw video frame data, only Pose_Keypoints or derived metrics.
**Validates: Requirements 1.6, 11.1, 11.5**

**Property 3: No Video Frame Persistence**
*For any* storage operation (browser storage, server storage, database), the System shall not write raw video frame data to any persistent medium.
**Validates: Requirements 11.4**

**Property 4: Keypoint-Only Extraction**
*For any* video frame, the Pose_Detector output shall contain only Pose_Keypoints (33 3D coordinates with visibility scores) and no other image data.
**Validates: Requirements 11.2**

### Performance Properties

**Property 5: Pose Detection Latency**
*For any* video frame, the Pose_Detector shall extract Pose_Keypoints within 500 milliseconds from frame capture.
**Validates: Requirements 1.2, 12.1**

### Exercise Recognition Properties

**Property 6: Low Confidence Prompts Confirmation**
*For any* Pose_Keypoints where the Exercise_Recognizer confidence score is below 0.8, the System shall prompt the user to confirm the exercise type.
**Validates: Requirements 2.5**

### Repetition Counting Properties

**Property 7: Full Range Rep Counting**
*For any* exercise type and valid full-range-of-motion angle sequence, the Rep_Counter shall increment the count by exactly one when the biomechanical angle transitions through the exercise-specific thresholds (up→down→up or down→up→down).
**Validates: Requirements 3.1, 3.3, 3.4, 3.5**

**Property 8: Partial Range Rejection**
*For any* angle sequence that does not meet the exercise-specific range-of-motion thresholds, the Rep_Counter shall not increment the count and shall generate feedback indicating partial range.
**Validates: Requirements 3.6**

### Form Analysis Properties

**Property 9: Form Mistake Detection**
*For any* Pose_Keypoints and exercise type, when a biomechanical angle deviates from the exercise-specific form rules by more than the configured threshold, the Form_Analyzer shall detect the mistake and generate a corrective suggestion.
**Validates: Requirements 4.3, 4.4, 4.5, 4.6**

**Property 10: Form Score Calculation**
*For any* list of detected form mistakes with severity scores, the Form_Score shall be calculated as: max(0, 100 - sum(mistake_penalty)) where mistake_penalty = 5 for severity <0.3, 10 for severity 0.3-0.7, and 20 for severity >0.7.
**Validates: Requirements 4.7**

### Camera Placement Properties

**Property 11: Out-of-Frame Detection**
*For any* Pose_Keypoints where more than 20% of keypoints have visibility scores below 0.5, the System shall pause exercise tracking and display a warning that the user is not fully visible.
**Validates: Requirements 5.5, 15.3**

### Post-Workout Summary Properties

**Property 12: Summary Rep Totals**
*For any* completed Workout_Session, the summary shall display total repetitions equal to the sum of all reps counted across all exercises in the session.
**Validates: Requirements 6.2**

**Property 13: Summary Duration Calculation**
*For any* completed Workout_Session, the summary duration shall equal (end_time - start_time) displayed in minutes and seconds.
**Validates: Requirements 6.3**

**Property 14: Summary Average Form Score**
*For any* completed Workout_Session with N exercise records, the average Form_Score shall equal the sum of all exercise Form_Scores divided by N.
**Validates: Requirements 6.4**

**Property 15: Top Mistakes Identification**
*For any* completed Workout_Session, the top 3 most frequent form mistakes shall be identified by counting mistake occurrences and selecting the 3 with highest counts.
**Validates: Requirements 6.5**

**Property 16: Recommendations Generation**
*For any* completed Workout_Session with identified weak areas, the System shall generate at least one specific recommendation for each weak area.
**Validates: Requirements 6.6**

**Property 17: Summary Persistence**
*For any* completed Workout_Session, the workout summary shall be stored in the database and retrievable via the user's workout history.
**Validates: Requirements 6.7**

### AI Workout Plan Properties

**Property 18: Workout Plan Context Inclusion**
*For any* workout plan generation request, the prompt sent to the LLM shall include the user's weight, height, body type, fitness goals, dietary preferences, available time, and any physical limitations.
**Validates: Requirements 7.2, 7.7**

**Property 19: Workout Plan Structure**
*For any* generated Workout_Plan, the plan shall include warmup exercises, main exercises with sets/reps/rest periods, and cooldown exercises.
**Validates: Requirements 7.3**

**Property 20: Workout Plan Time Constraint**
*For any* generated Workout_Plan with user-specified available time T minutes, the total calculated duration (warmup + exercises + rest + cooldown) shall not exceed T minutes.
**Validates: Requirements 7.6**

**Property 21: Adaptive Plan Generation**
*For any* workout plan generation request after the user has completed previous plans, the prompt sent to the LLM shall include performance data from the most recent 5 completed workouts.
**Validates: Requirements 7.5**

### AI Coach Chat Properties

**Property 22: Chat Context Inclusion**
*For any* chat message sent to the AI_Coach, the prompt shall include the user's workout history from the past 30 days and current streak count.
**Validates: Requirements 8.6**

### Notification Properties

**Property 23: Scheduled Reminder Delivery**
*For any* user with notification preferences enabled and scheduled workout times, the Notification_Service shall queue reminders at (scheduled_time - reminder_minutes_before).
**Validates: Requirements 9.1**

**Property 24: Streak Calculation**
*For any* sequence of workout dates, the streak count shall equal the number of consecutive days with at least one completed workout, where days are considered consecutive if they are within 36 hours of each other.
**Validates: Requirements 9.2**

**Property 25: Streak Update on Completion**
*For any* completed workout, if it is the first workout of the day, the Notification_Service shall increment the streak counter by 1 if the previous workout was within 36 hours, otherwise reset to 1.
**Validates: Requirements 9.3**

**Property 26: Missed Workout Reminders**
*For any* scheduled workout that is not completed within 2 hours of the scheduled time, the Notification_Service shall send a motivational reminder if missed_workout_reminder preference is enabled.
**Validates: Requirements 9.4**

**Property 27: Milestone Notifications**
*For any* streak count that reaches a milestone value (7, 14, 30, 60, 90 days), the Notification_Service shall display a congratulatory message.
**Validates: Requirements 9.5**

**Property 28: Notification Preferences Persistence**
*For any* user notification preference update, the new preferences shall be stored in the database and applied to all future notification operations.
**Validates: Requirements 9.6**

**Property 29: Reminder Rescheduling**
*For any* dismissed workout reminder, the Notification_Service shall calculate the next reminder time based on the user's workout_times schedule and queue a new reminder.
**Validates: Requirements 9.7**

### User Management Properties

**Property 30: Email and Password Validation**
*For any* registration attempt, the System shall validate that the email matches the pattern `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` and the password has at least 8 characters with at least one uppercase, one lowercase, and one number.
**Validates: Requirements 10.2**

**Property 31: Password Encryption**
*For any* stored User_Profile, the password_hash field shall not contain the plaintext password and shall be the output of a cryptographic hash function (bcrypt, argon2, or similar).
**Validates: Requirements 10.3**

**Property 32: Workout History Completeness**
*For any* user, all completed Workout_Sessions shall be stored in the database and retrievable via the get_workout_history API.
**Validates: Requirements 10.5**

**Property 33: Profile Update Persistence**
*For any* user profile update request, the updated fields shall be persisted to the database and reflected in subsequent profile retrievals.
**Validates: Requirements 10.6**

**Property 34: Workout Statistics Calculation**
*For any* user profile view, the displayed statistics shall include: total_sessions = count of all workout sessions, total_reps = sum of reps across all sessions, average_form_score = mean of all session form scores.
**Validates: Requirements 10.7**

### WebSocket Communication Properties

**Property 35: WebSocket Reconnection Attempts**
*For any* interrupted WebSocket connection, the System shall attempt to reconnect every 5 seconds for up to 10 attempts before displaying a connection error.
**Validates: Requirements 14.3**

**Property 36: Offline Keypoint Buffering**
*For any* Pose_Keypoints generated while the WebSocket connection is disconnected, the System shall buffer them in browser memory (up to 1000 keypoints) and transmit them in order when the connection is re-established.
**Validates: Requirements 14.4**

### Error Handling Properties

**Property 37: Low Confidence Alert**
*For any* Pose_Keypoints where more than 50% of keypoints have visibility scores below 0.3, the System shall alert the user about poor lighting conditions.
**Validates: Requirements 15.2**

**Property 38: Error Logging and User Messaging**
*For any* unexpected error (uncaught exception), the System shall log the error details (timestamp, error type, stack trace) to the console/logging service and display a user-friendly error message.
**Validates: Requirements 15.6**

**Property 39: Error Recovery Options**
*For any* error state, the System shall provide at least one recovery action (retry, refresh data, return to home, contact support) without requiring a full page refresh.
**Validates: Requirements 15.7**

## Error Handling

### Error Categories and Responses

**1. Camera Access Errors**
- **Permission Denied**: Display modal with instructions to enable camera in browser settings
- **Camera Not Found**: Alert user that no camera device was detected
- **Camera In Use**: Notify user that camera is being used by another application

**2. Pose Detection Errors**
- **Model Load Failure**: Retry loading BlazePose model up to 3 times, then display error
- **Low Confidence**: Alert user about poor lighting or positioning
- **Processing Timeout**: Skip frame and continue with next frame

**3. Network Errors**
- **WebSocket Connection Failed**: Attempt reconnection with exponential backoff
- **WebSocket Disconnected**: Buffer data locally and sync when reconnected
- **API Request Failed**: Retry up to 3 times with exponential backoff, then show error

**4. Backend Errors**
- **500 Internal Server Error**: Log error, display generic error message to user
- **Authentication Failed**: Redirect to login page
- **Rate Limit Exceeded**: Display message asking user to wait before retrying

**5. Data Validation Errors**
- **Invalid Input**: Display field-specific error messages
- **Missing Required Fields**: Highlight missing fields and prevent submission

**6. Exercise Recognition Errors**
- **Ambiguous Exercise**: Prompt user to select exercise manually
- **Unsupported Exercise**: Notify user that exercise is not yet supported

### Error Recovery Strategies

**Graceful Degradation:**
- If backend is unavailable, continue pose detection locally without rep counting
- If LLM API fails, provide pre-defined workout templates
- If database is unavailable, cache workout data locally and sync later

**User Feedback:**
- All errors display user-friendly messages (no technical jargon)
- Provide clear next steps for recovery
- Include "Report Issue" button for unexpected errors

**Logging:**
- Frontend errors logged to browser console and optionally sent to logging service
- Backend errors logged with full context (user_id, request_id, timestamp, stack trace)
- Privacy-sensitive data (passwords, video frames) never logged

## Testing Strategy

### Dual Testing Approach

The AI Gym Coach system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary values, null handling)
- Integration points between components
- Error conditions and exception handling
- UI component rendering and user interactions

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must be maintained
- Round-trip properties (serialization/deserialization)
- Metamorphic properties (relationships between operations)

### Property-Based Testing Configuration

**Framework Selection:**
- **Frontend (TypeScript)**: fast-check library
- **Backend (Python)**: Hypothesis library

**Test Configuration:**
- Minimum 100 iterations per property test (due to randomization)
- Configurable seed for reproducibility
- Shrinking enabled to find minimal failing examples
- Timeout: 30 seconds per property test

**Property Test Tagging:**
Each property test must include a comment referencing its design property:
```python
# Feature: ai-gym-coach, Property 7: Full Range Rep Counting
@given(exercise_type=st.sampled_from(ExerciseType), 
       angle_sequence=valid_rep_sequence())
def test_full_range_rep_counting(exercise_type, angle_sequence):
    # Test implementation
    pass
```

### Test Coverage by Component

**1. Pose Detector (Frontend)**
- Unit: Test model initialization, frame processing, keypoint extraction
- Property: Frame deletion after extraction (Property 1), keypoint-only output (Property 4)
- Integration: Test with real video frames, verify performance

**2. Exercise Recognizer (Backend)**
- Unit: Test each exercise pattern recognition with known poses
- Property: Low confidence confirmation prompts (Property 6)
- Integration: Test with recorded pose sequences

**3. Rep Counter (Backend)**
- Unit: Test state machine transitions for each exercise
- Property: Full range counting (Property 7), partial range rejection (Property 8)
- Integration: Test with realistic angle sequences

**4. Form Analyzer (Backend)**
- Unit: Test each form rule with known mistake patterns
- Property: Form mistake detection (Property 9), form score calculation (Property 10)
- Integration: Test with recorded workout sessions

**5. WebSocket Handler (Backend)**
- Unit: Test message parsing, session management
- Property: Reconnection attempts (Property 35), offline buffering (Property 36)
- Integration: Test with simulated network interruptions

**6. AI Coach (Backend)**
- Unit: Test prompt construction, response parsing
- Property: Context inclusion (Properties 18, 21, 22), plan structure (Property 19)
- Integration: Test with real LLM API (mocked for CI/CD)

**7. User Management (Backend)**
- Unit: Test CRUD operations, authentication flow
- Property: Email/password validation (Property 30), password encryption (Property 31)
- Integration: Test with real database (test database for CI/CD)

**8. Notification Service (Backend)**
- Unit: Test notification scheduling, streak calculation
- Property: Streak calculation (Property 24), milestone detection (Property 27)
- Integration: Test with time-mocked scenarios

### Test Data Generation

**For Property-Based Tests:**

**Pose Keypoints Generator:**
```python
@st.composite
def pose_keypoints(draw):
    """Generate random but anatomically plausible pose keypoints."""
    keypoints = []
    for joint_name in JOINT_NAMES:
        x = draw(st.floats(min_value=0.0, max_value=1.0))
        y = draw(st.floats(min_value=0.0, max_value=1.0))
        z = draw(st.floats(min_value=-0.5, max_value=0.5))
        visibility = draw(st.floats(min_value=0.0, max_value=1.0))
        keypoints.append(PoseKeypoint(x, y, z, visibility, joint_name))
    return PoseData(keypoints=keypoints, timestamp=time.time())
```

**Angle Sequence Generator:**
```python
@st.composite
def valid_rep_sequence(draw, exercise_type):
    """Generate angle sequence representing valid rep."""
    if exercise_type == ExerciseType.PUSHUP:
        # Generate: high angle → low angle → high angle
        up_angle = draw(st.floats(min_value=160, max_value=180))
        down_angle = draw(st.floats(min_value=70, max_value=90))
        return [up_angle, down_angle, up_angle]
    # Similar for other exercises
```

**Form Mistake Generator:**
```python
@st.composite
def form_mistakes(draw):
    """Generate random list of form mistakes."""
    num_mistakes = draw(st.integers(min_value=0, max_value=10))
    mistakes = []
    for _ in range(num_mistakes):
        mistake_type = draw(st.sampled_from(MISTAKE_TYPES))
        severity = draw(st.floats(min_value=0.0, max_value=1.0))
        mistakes.append(FormMistake(mistake_type, severity, "suggestion"))
    return mistakes
```

### Continuous Integration

**CI/CD Pipeline:**
1. Run linters and formatters (ESLint, Prettier, Black, isort)
2. Run unit tests with coverage reporting (target: >80% coverage)
3. Run property-based tests (100 iterations in CI, 1000 in nightly builds)
4. Run integration tests with mocked external services
5. Build Docker images
6. Deploy to staging environment
7. Run end-to-end tests in staging
8. Deploy to production (manual approval)

**Test Environments:**
- **Local**: Full test suite with real services
- **CI**: Unit and property tests with mocked services
- **Staging**: Integration and E2E tests with test data
- **Production**: Smoke tests and monitoring

### Performance Testing

**Load Testing:**
- Simulate 100 concurrent users performing workouts
- Measure WebSocket message latency (target: <100ms)
- Measure API response times (target: <500ms)
- Monitor CPU and memory usage

**Stress Testing:**
- Gradually increase load until system degrades
- Identify bottlenecks and resource limits
- Test recovery after overload

**Benchmarking:**
- Pose detection: Target 15+ FPS on standard hardware
- Rep counting: Target <50ms processing per pose update
- Form analysis: Target <100ms processing per pose update

## Deployment Architecture

### Production Infrastructure

```
                    ┌─────────────┐
                    │   Cloudflare│
                    │     CDN     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Nginx    │
                    │ Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ FastAPI │       │ FastAPI │       │ FastAPI │
   │ Server 1│       │ Server 2│       │ Server 3│
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │PostgreSQL│       │  Redis  │       │   LLM   │
   │ Primary  │       │  Cache  │       │   API   │
   └────┬────┘       └─────────┘       └─────────┘
        │
   ┌────▼────┐
   │PostgreSQL│
   │ Replica  │
   └─────────┘
```

### Scaling Considerations

**Horizontal Scaling:**
- FastAPI servers: Scale based on CPU/memory usage
- WebSocket connections: Use Redis pub/sub for cross-server communication
- Database: Read replicas for workout history queries

**Caching Strategy:**
- User profiles: Cache in Redis (TTL: 1 hour)
- Exercise definitions: Cache in Redis (TTL: 24 hours)
- Workout plans: Cache in Redis (TTL: 7 days)

**Database Optimization:**
- Index on user_id, start_time for fast workout history queries
- Partition workout_sessions table by month
- Archive old workout data (>1 year) to cold storage

### Monitoring and Observability

**Metrics to Track:**
- WebSocket connection count and latency
- Pose detection FPS (client-side)
- API response times (p50, p95, p99)
- Error rates by component
- User engagement (workouts per day, streak distribution)

**Logging:**
- Structured JSON logs with correlation IDs
- Log levels: DEBUG (dev), INFO (staging), WARN/ERROR (production)
- Centralized logging with ELK stack or similar

**Alerting:**
- High error rate (>5% of requests)
- Slow API responses (p95 >1s)
- Database connection pool exhaustion
- High CPU/memory usage (>80%)

## Security Considerations

**Authentication:**
- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Secure HTTP-only cookies for token storage

**Authorization:**
- Users can only access their own workout data
- Admin role for system management
- Rate limiting: 100 requests per minute per user

**Data Protection:**
- HTTPS/WSS for all communication
- Password hashing with bcrypt (cost factor: 12)
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization and CSP headers

**Privacy:**
- No video frame storage or transmission
- User data encrypted at rest
- GDPR compliance: Data export and deletion APIs
- Privacy policy and terms of service

## Future Enhancements

**Phase 2 Features:**
1. **ML-Based Exercise Recognition**: Train LSTM/Transformer model for more accurate classification
2. **Additional Exercises**: Add 10+ new exercises (lunges, burpees, mountain climbers, etc.)
3. **Social Features**: Friend challenges, leaderboards, workout sharing
4. **Wearable Integration**: Sync with Fitbit, Apple Watch for heart rate data
5. **Nutrition Tracking**: Meal logging and calorie tracking
6. **Video Tutorials**: In-app exercise demonstration videos
7. **Voice Commands**: Hands-free workout control
8. **Offline Mode**: Full functionality without internet connection

**Technical Debt to Address:**
- Migrate from rule-based to ML-based form analysis for better accuracy
- Implement comprehensive E2E test suite with Playwright
- Add GraphQL API for more flexible data fetching
- Optimize pose detection model for mobile devices
- Implement progressive web app (PWA) for mobile installation

## Conclusion

The AI Gym Coach system provides a comprehensive, privacy-first fitness platform that combines real-time computer vision, biomechanical analysis, and conversational AI. The modular architecture ensures scalability and maintainability, while the rule-based MVP approach prioritizes reliability and performance. The dual testing strategy with property-based testing ensures correctness across all input scenarios, and the privacy-first design protects user data throughout the system.
