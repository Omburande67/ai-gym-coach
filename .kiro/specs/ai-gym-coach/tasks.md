# Implementation Plan: AI Gym Coach System

## Overview

This implementation plan breaks down the AI Gym Coach system into incremental, testable steps. The approach follows a bottom-up strategy: build core components first (pose detection, exercise recognition, rep counting), then integrate them into the full system. Each task builds on previous work, with checkpoints to ensure stability before proceeding.

The implementation uses:
- **Frontend**: TypeScript with React/Next.js, TensorFlow.js with MediaPipe BlazePose
- **Backend**: Python with FastAPI, PostgreSQL, Redis
- **Testing**: fast-check (TypeScript) and Hypothesis (Python) for property-based testing

## Tasks

- [x] 1. Set up project structure and development environment
  - Create Next.js frontend project with TypeScript
  - Create FastAPI backend project with Python
  - Set up PostgreSQL and Redis with Docker Compose
  - Configure ESLint, Prettier, Black, isort
  - Set up testing frameworks (Jest, pytest, fast-check, Hypothesis)
  - Create .env files for configuration
  - _Requirements: All (foundational)_

- [ ] 2. Implement database schema and user management
  - [x] 2.1 Create PostgreSQL database schema
    - Write SQL migration for users, workout_sessions, exercise_records, workout_streaks, notification_preferences, workout_plans tables
    - Add indexes for performance optimization
    - _Requirements: 10.1, 10.5_
  
  - [x] 2.2 Implement user registration and authentication
    - Create UserService with register, authenticate, get_profile, update_profile methods
    - Implement password hashing with bcrypt
    - Implement JWT token generation and validation
    - _Requirements: 10.1, 10.3, 10.4_
  
  - [ ]* 2.3 Write property test for email and password validation
    - **Property 30: Email and Password Validation**
    - **Validates: Requirements 10.2**
  
  - [ ]* 2.4 Write property test for password encryption
    - **Property 31: Password Encryption**
    - **Validates: Requirements 10.3**
  
  - [x] 2.5 Create REST API endpoints for user management
    - POST /api/auth/register
    - POST /api/auth/login
    - GET /api/users/profile
    - PUT /api/users/profile
    - _Requirements: 10.1, 10.4, 10.6_
  
  - [ ]* 2.6 Write unit tests for user management endpoints
    - Test registration with valid/invalid data
    - Test authentication with correct/incorrect credentials
    - Test profile updates
    - _Requirements: 10.1, 10.4, 10.6_

- [ ] 3. Implement frontend camera access and pose detection
  - [x] 3.1 Create camera access component
    - Implement WebRTC camera permission request
    - Handle permission granted/denied states
    - Display video stream in canvas element
    - _Requirements: 1.1, 15.1_
  
  - [x] 3.2 Integrate TensorFlow.js with MediaPipe BlazePose
    - Load BlazePose model on component mount
    - Implement pose detection on video frames
    - Extract 33 3D keypoints with visibility scores
    - _Requirements: 1.2, 11.2_
  
  - [x] 3.3 Implement frame processing and privacy controls
    - Process frames at 15-30 FPS using requestAnimationFrame
    - Delete raw frame immediately after keypoint extraction
    - Verify no frame data in memory after extraction
    - _Requirements: 1.3, 11.3_
  
  - [ ]* 3.4 Write property test for frame deletion after extraction
    - **Property 1: Frame Deletion After Extraction**
    - **Validates: Requirements 1.3, 11.3**
  
  - [ ]* 3.5 Write property test for keypoint-only extraction
    - **Property 4: Keypoint-Only Extraction**
    - **Validates: Requirements 11.2**
  
  - [x] 3.6 Create skeleton overlay visualization
    - Draw keypoints and connections on canvas
    - Color-code joints by visibility confidence
    - Update visualization in real-time
    - _Requirements: 1.1_
  
  - [ ]* 3.7 Write unit tests for camera component
    - Test permission request flow
    - Test error handling for denied permissions
    - Test video stream initialization
    - _Requirements: 1.1, 15.1_

- [ ] 4. Implement exercise recognition system
  - [x] 4.1 Create exercise definition data structure
    - Define ExerciseType enum (pushup, squat, plank, jumping_jack)
    - Create exercise configuration with angle thresholds and form rules
    - Store exercise definitions in separate JSON/config file
    - _Requirements: 2.2, 13.1, 13.3_
  
  - [x] 4.2 Implement biomechanical angle calculation
    - Create function to calculate angle between three keypoints
    - Handle edge cases (missing keypoints, low visibility)
    - Return angles for elbow, knee, hip, shoulder, torso
    - _Requirements: 2.6, 3.2_
  
  - [x] 4.3 Implement rule-based exercise recognizer
    - Create ExerciseRecognizer class with recognize() method
    - Implement pattern matching for each exercise type
    - Use sliding window (2-3 seconds) for pattern detection
    - Return exercise type and confidence score
    - _Requirements: 2.1, 2.3, 2.6_
  
  - [ ]* 4.4 Write property test for low confidence prompts
    - **Property 6: Low Confidence Prompts Confirmation**
    - **Validates: Requirements 2.5**
  
  - [ ]* 4.5 Write unit tests for exercise recognition
    - Test push-up pattern recognition with known poses
    - Test squat pattern recognition with known poses
    - Test plank pattern recognition with known poses
    - Test jumping jack pattern recognition with known poses
    - _Requirements: 2.2, 2.3_

- [ ] 5. Implement repetition counting system
  - [x] 5.1 Create rep counter state machine
    - Create RepCounter class with state (UP, DOWN, TRANSITION)
    - Implement update() method to process new pose data
    - Track current phase and rep count
    - _Requirements: 3.1, 3.2_
  
  - [x] 5.2 Implement exercise-specific rep counting logic
    - Push-up: Track elbow angle transitions (>160° → <90° → >160°)
    - Squat: Track knee angle transitions (>160° → <90° → >160°)
    - Jumping jack: Track arm angle transitions (<30° → >160° → <30°)
    - Plank: Track duration instead of reps
    - Add hysteresis and debouncing to prevent double-counting
    - _Requirements: 3.3, 3.4, 3.5_
  
  - [ ]* 5.3 Write property test for full range rep counting
    - **Property 7: Full Range Rep Counting**
    - **Validates: Requirements 3.1, 3.3, 3.4, 3.5**
  
  - [ ]* 5.4 Write property test for partial range rejection
    - **Property 8: Partial Range Rejection**
    - **Validates: Requirements 3.6**
  
  - [ ]* 5.5 Write unit tests for rep counter
    - Test state transitions for each exercise
    - Test edge cases (rapid movements, pauses)
    - Test reset functionality
    - _Requirements: 3.1, 3.6_

- [x] 6. Checkpoint - Ensure core components work
  - Verify pose detection runs at 15+ FPS
  - Verify exercise recognition correctly identifies exercises
  - Verify rep counting accurately counts reps
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement form analysis system
  - [x] 7.1 Create form mistake detection rules
    - Define FormMistake class with type, severity, suggestion
    - Create form rules for push-ups (hip sag, elbow flare, partial range, head drop)
    - Create form rules for squats (knee cave, shallow depth, forward lean, heel lift)
    - Create form rules for plank (hip sag, hip pike, shoulder collapse)
    - Create form rules for jumping jacks (incomplete arms, incomplete legs)
    - _Requirements: 4.3, 4.4, 4.5, 4.6_
  
  - [x] 7.2 Implement FormAnalyzer class
    - Create analyze() method to detect mistakes in pose data
    - Implement calculate_form_score() method using mistake severity
    - Return list of detected mistakes with suggestions
    - _Requirements: 4.1, 4.7_
  
  - [ ]* 7.3 Write property test for form mistake detection
    - **Property 9: Form Mistake Detection**
    - **Validates: Requirements 4.3, 4.4, 4.5, 4.6**
  
  - [ ]* 7.4 Write property test for form score calculation
    - **Property 10: Form Score Calculation**
    - **Validates: Requirements 4.7**
  
  - [ ]* 7.5 Write unit tests for form analyzer
    - Test each form rule with known mistake patterns
    - Test form score calculation with various mistake combinations
    - Test edge cases (no mistakes, all mistakes)
    - _Requirements: 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ] 8. Implement WebSocket communication
  - [x] 8.1 Create WebSocket server in FastAPI
    - Set up WebSocket endpoint /ws/{user_id}
    - Implement connection/disconnection handling
    - Create WorkoutSession class to manage session state
    - _Requirements: 14.1, 14.7_
  
  - [x] 8.2 Implement WebSocket message protocol
    - Define message types (pose_data, exercise_detected, rep_counted, form_feedback)
    - Implement message parsing and validation
    - Handle malformed messages gracefully
    - _Requirements: 14.5, 14.6_
  
  - [x] 8.3 Integrate exercise recognition and rep counting in WebSocket handler
    - Process incoming pose_data messages
    - Run exercise recognition on pose keypoints
    - Update rep counter with new pose data
    - Run form analysis on pose data
    - Send feedback messages to frontend
    - _Requirements: 2.1, 3.1, 4.1_
  
  - [x] 8.4 Create WebSocket client in frontend
    - Implement WebSocket connection on workout session start
    - Send pose_data messages with keypoints
    - Handle incoming feedback messages (exercise_detected, rep_counted, form_feedback)
    - Update UI with real-time feedback
    - _Requirements: 14.1, 14.5, 14.6_
  
  - [x] 8.5 Implement WebSocket reconnection logic
    - Detect connection interruptions
    - Attempt reconnection every 5 seconds
    - Buffer pose keypoints during disconnection
    - Sync buffered data when reconnected
    - _Requirements: 14.3, 14.4_
  
  - [ ]* 8.6 Write property test for WebSocket reconnection
    - **Property 35: WebSocket Reconnection Attempts**
    - **Validates: Requirements 14.3**
  
  - [ ]* 8.7 Write property test for offline keypoint buffering
    - **Property 36: Offline Keypoint Buffering**
    - **Validates: Requirements 14.4**
  
  - [ ]* 8.8 Write unit tests for WebSocket communication
    - Test message parsing and validation
    - Test session management
    - Test error handling
    - _Requirements: 14.1, 14.5, 14.6_

- [ ]* 9. Write property tests for privacy guarantees
  - [ ]* 9.1 Write property test for no video frame transmission
    - **Property 2: No Video Frame Transmission**
    - **Validates: Requirements 1.6, 11.1, 11.5**
  
  - [ ]* 9.2 Write property test for no video frame persistence
    - **Property 3: No Video Frame Persistence**
    - **Validates: Requirements 11.4**

- [x] 10. Implement camera placement guidance and validation
  - [x] 10.1 Create camera placement tutorial component
    - Display tutorial modal on first workout session
    - Show distance guidance (2.5-3 meters)
    - Show height guidance (waist level)
    - Show exercise-specific camera angles
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 10.2 Implement full body visibility detection
    - Check keypoint visibility scores
    - Detect when user is out of frame (>20% keypoints with visibility <0.5)
    - Pause tracking and display warning
    - _Requirements: 5.5, 5.6_
  
  - [x] 10.3 Write property test for out-of-frame detection
    - **Property 11: Out-of-Frame Detection**
    - **Validates: Requirements 5.5, 15.3**
  
  - [x] 10.4 Write unit tests for camera placement guidance
    - Test tutorial display logic
    - Test visibility detection
    - Test warning display
    - _Requirements: 5.1, 5.5, 5.6_

- [~] 11. Checkpoint - Ensure real-time workout tracking works end-to-end
  - Test complete workout flow: camera → pose detection → exercise recognition → rep counting → form feedback
  - Verify WebSocket communication is stable
  - Verify privacy guarantees (no frame storage/transmission)
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement post-workout summary and persistence
  - [x] 12.1 Implement workout persistence
    - Implement save_workout() method in UserService
    - Store workout_sessions and exercise_records in database
    - _Requirements: 6.7, 10.5_
  
  - [x] 12.2 Implement post-workout summary generation
    - Calculate total reps across all exercises
    - Calculate total duration (end_time - start_time)
    - Calculate average form score
    - Identify top 3 most frequent mistakes
    - Generate recommendations for weak areas
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [x] 12.3 Create workout summary UI component
    - Display total reps, duration, form score
    - Display top mistakes with suggestions
    - Display recommendations
    - Add button to view detailed history
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 12.4 Write property tests for summary calculations
    - **Property 12: Summary Rep Totals**
    - **Property 13: Summary Duration Calculation**
    - **Property 14: Summary Average Form Score**
    - **Property 15: Top Mistakes Identification**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5**
  
  - [ ]* 12.5 Write property test for summary persistence
    - **Property 17: Summary Persistence**
    - **Validates: Requirements 6.7**
  
  - [ ]* 12.6 Write property test for workout history completeness
    - **Property 18: Workout History Integrity**
    - **Validates: Requirements 10.5**

- [ ] 13. Implement AI Workout Planning
  - [x] 13.1 Create workout plan data model
    - Create WorkoutPlan model and schemas
    - Add migration for workout_plans (included in 2.1)
    - _Requirements: 7.1_
  
  - [x] 13.2 Implement LLM service integration
    - Create LLMService class with OpenAI integration
    - Implement generate_workout_plan() method
    - Handle API failures with mock fallback
    - _Requirements: 7.1, 7.2_
  
  - [x] 13.3 Create workout plan generation logic in UserService
    - Implement generate_and_save_plan()
    - Implement get_active_plan()
    - Integrate user profile data into prompts
    - _Requirements: 7.3, 7.4, 7.5_
  
  - [x] 13.4 Create API endpoints for workout plans
    - POST /api/workouts/plan
    - GET /api/workouts/plan/active
    - _Requirements: 7.1, 7.4_
  
  - [x] 13.5 Create Frontend UI for plan generation
    - Create WorkoutPlan component
    - Add "Generate Plan" button in dashboard
    - Display active plan details
    - _Requirements: 7.1, 7.4_
    - **Property 32: Workout History Completeness**
    - **Validates: Requirements 10.5**
  
  - [ ]* 12.7 Write unit tests for summary generation
    - Test calculation logic with various workout data
    - Test edge cases (no reps, no mistakes, single exercise)
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_


- [ ] 14. Implement AI coach chatbot
  - [x] 14.1 Create chat interface
    - Build chat UI component with message history
    - Implement message input and send functionality
    - Display user and AI messages with timestamps
    - _Requirements: 8.1_
  
  - [x] 14.2 Implement chat backend
    - Create chat() method in AICoach class
    - Build system prompt with coach personality
    - Include user context (profile, workout history, streak)
    - Send message to LLM API and return response
    - _Requirements: 8.2, 8.6_
  
  - [ ]* 14.3 Write property test for chat context inclusion
    - **Property 22: Chat Context Inclusion**
    - **Validates: Requirements 8.6**
  
  - [x] 14.4 Create chat API endpoints
    - POST /api/chat/message
    - GET /api/chat/history (optional)
    - _Requirements: 8.1_
  
  - [ ]* 14.5 Write unit tests for chat functionality
    - Test prompt construction with user context
    - Test error handling (API failures)
    - _Requirements: 8.2, 8.6_

- [ ] 15. Implement notification and streak tracking system
  - [x] 15.1 Create notification preferences management
    - Implement CRUD operations for notification_preferences table
    - Create API endpoints for preferences
    - _Requirements: 9.6_
  
  - [x] 15.2 Implement streak calculation logic
    - Create update_streak() method in NotificationService
    - Calculate consecutive days with workouts (36-hour grace period)
    - Update workout_streaks table
    - _Requirements: 9.2, 9.3_
  
  - [x] 15.3 Implement scheduled workout reminders
    - Create background job to check scheduled workout times
    - Send reminders at (scheduled_time - reminder_minutes_before)
    - _Requirements: 9.1_
  
  - [x] 15.4 Implement missed workout reminders
    - Create background job to check for missed workouts
    - Send motivational reminder 2 hours after missed workout
    - _Requirements: 9.4_
  
  - [x] 15.5 Implement milestone notifications
    - Detect streak milestones (7, 14, 30, 60, 90 days)
    - Display congratulatory message
    - _Requirements: 9.5_
  
  - [ ]* 15.6 Write property tests for notification system
    - **Property 23: Scheduled Reminder Delivery**
    - **Property 24: Streak Calculation**
    - **Property 25: Streak Update on Completion**
    - **Property 26: Missed Workout Reminders**
    - **Property 27: Milestone Notifications**
    - **Property 28: Notification Preferences Persistence**
    - **Property 29: Reminder Rescheduling**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7**
  
  - [ ]* 15.7 Write unit tests for notification system
    - Test streak calculation with various workout patterns
    - Test reminder scheduling logic
    - Test milestone detection
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 16. Implement user profile and statistics
  - [x] 16.1 Create profile update functionality
    - Implement update_profile() API endpoint
    - Allow updates to weight, height, body type, goals
    - _Requirements: 10.6_
  
  - [ ]* 16.2 Write property test for profile update persistence
    - **Property 33: Profile Update Persistence**
    - **Validates: Requirements 10.6**
  
  - [x] 16.3 Implement workout statistics calculation
    - Calculate total sessions, total reps, average form score
    - Create API endpoint to retrieve statistics
    - _Requirements: 10.7_
  
  - [ ]* 16.4 Write property test for workout statistics
    - **Property 34: Workout Statistics Calculation**
    - **Validates: Requirements 10.7**
  
  - [x] 16.5 Create profile UI component
    - Display user info (email, weight, height, goals)
    - Display workout statistics
    - Display current streak
    - Add edit profile functionality
    - _Requirements: 10.6, 10.7_
  
  - [ ]* 16.6 Write unit tests for profile functionality
    - Test profile updates
    - Test statistics calculation
    - _Requirements: 10.6, 10.7_

- [x] 17. Checkpoint - Ensure all features are integrated
  - Test complete user journey: registration → workout → summary → plan generation → chat
  - Verify all API endpoints work correctly
  - Verify all UI components render properly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 18. Implement error handling and edge cases
  - [~] 18.1 Implement camera error handling
    - Handle permission denied with clear instructions
    - Handle camera not found error
    - Handle camera in use error
    - _Requirements: 15.1_
  
  - [x] 18.2 Implement pose detection error handling
    - Handle model load failure with retry logic
    - Detect low confidence keypoints and alert user
    - Handle processing timeouts
    - _Requirements: 15.2, 15.4_
  
  - [ ]* 18.3 Write property test for low confidence alert
    - **Property 37: Low Confidence Alert**
    - **Validates: Requirements 15.2**
  
  - [x] 18.4 Implement network error handling
    - Handle API request failures with retry logic
    - Handle authentication failures with redirect
    - Handle rate limiting with user message
    - _Requirements: 15.5_
  
  - [x] 18.5 Implement general error handling
    - Add global error boundary in React
    - Log all errors to console/logging service
    - Display user-friendly error messages
    - Provide recovery options (retry, refresh, home)
    - _Requirements: 15.6, 15.7_
  
  - [ ]* 18.6 Write property tests for error handling
    - **Property 38: Error Logging and User Messaging**
    - **Property 39: Error Recovery Options**
    - **Validates: Requirements 15.6, 15.7**
  
  - [ ]* 18.7 Write unit tests for error handling
    - Test each error scenario
    - Test recovery actions
    - _Requirements: 15.1, 15.2, 15.4, 15.5, 15.6, 15.7_

- [ ] 19. Implement UI/UX polish and responsive design
  - [~] 19.1 Create responsive layouts
    - Ensure all components work on desktop and tablet
    - Optimize camera view for different screen sizes
    - Add mobile-friendly navigation
    - _Requirements: All (user experience)_
  
  - [~] 19.2 Add loading states and animations
    - Show loading spinners during API calls
    - Add smooth transitions between screens
    - Animate rep counter updates
    - _Requirements: All (user experience)_
  
  - [~] 19.3 Implement accessibility features
    - Add ARIA labels to all interactive elements
    - Ensure keyboard navigation works
    - Add screen reader support
    - Test with accessibility tools
    - _Requirements: All (accessibility)_
  
  - [~] 19.4 Add user onboarding flow
    - Create welcome screen for new users
    - Add tutorial for first workout
    - Highlight key features
    - _Requirements: 5.1_

- [ ] 20. Set up deployment and monitoring
  - [~] 20.1 Create Docker containers
    - Write Dockerfile for frontend (Next.js)
    - Write Dockerfile for backend (FastAPI)
    - Create docker-compose.yml for local development
    - _Requirements: All (deployment)_
  
  - [~] 20.2 Set up CI/CD pipeline
    - Configure GitHub Actions or similar
    - Run linters and tests on every commit
    - Build and push Docker images
    - Deploy to staging environment
    - _Requirements: All (deployment)_
  
  - [~] 20.3 Implement logging and monitoring
    - Add structured logging to backend
    - Set up error tracking (Sentry or similar)
    - Add performance monitoring
    - Create health check endpoints
    - _Requirements: 15.6_
  
  - [~] 20.4 Deploy to production
    - Set up production infrastructure (cloud provider)
    - Configure environment variables
    - Set up database backups
    - Configure SSL certificates
    - _Requirements: All (deployment)_

- [~] 21. Final checkpoint - End-to-end testing and launch preparation
  - Run full test suite (unit, property, integration)
  - Perform manual testing of all features
  - Test on different browsers and devices
  - Verify performance metrics (FPS, latency, API response times)
  - Review security checklist
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks that can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities to address issues early
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a bottom-up approach: core components first, then integration
- Privacy is enforced at every layer: no video frames leave the browser
- The modular architecture allows easy addition of new exercises in the future
