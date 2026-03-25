# Requirements Document: AI Gym Coach System

## Introduction

The AI Gym Coach is a privacy-first, real-time workout recognition and smart fitness assistant platform. The system analyzes user workouts through webcam video input, providing immediate feedback on exercise form, counting repetitions, and offering personalized coaching through an AI-powered conversational interface. The platform processes video frames locally to extract pose keypoints without storing or transmitting raw video data, ensuring user privacy while delivering professional-grade fitness guidance.

## Glossary

- **System**: The complete AI Gym Coach platform including frontend, backend, and AI components
- **Pose_Detector**: The component responsible for extracting skeletal keypoints from video frames using pose estimation models
- **Exercise_Recognizer**: The component that identifies which exercise the user is performing based on pose data
- **Rep_Counter**: The component that tracks and counts exercise repetitions using biomechanical angle analysis
- **Form_Analyzer**: The component that evaluates exercise form and detects posture mistakes
- **Workout_Session**: A single continuous period of exercise activity with start and end times
- **Pose_Keypoints**: The 33 3D coordinates representing body joint positions extracted from video frames
- **Biomechanical_Angle**: The angle between three joint points used to determine exercise phases
- **Form_Score**: A numerical rating (0-100) representing the quality of exercise execution
- **AI_Coach**: The LLM-powered conversational assistant that provides workout plans and motivation
- **User_Profile**: Stored user data including body stats, fitness goals, and workout history
- **Camera_Placement_Tutorial**: Interactive guide showing proper camera positioning for exercises
- **Workout_Plan**: A structured sequence of exercises with sets, reps, and rest periods
- **Notification_Service**: The component managing workout reminders and streak tracking

## Requirements

### Requirement 1: Real-Time Video Processing

**User Story:** As a user, I want the system to analyze my workout in real-time through my webcam, so that I receive immediate feedback during exercise.

#### Acceptance Criteria

1. WHEN the user grants camera permissions, THE Pose_Detector SHALL access the webcam stream and begin processing frames
2. WHEN a video frame is captured, THE Pose_Detector SHALL extract Pose_Keypoints within 500 milliseconds
3. WHEN Pose_Keypoints are extracted, THE System SHALL immediately delete the raw video frame from memory
4. THE Pose_Detector SHALL maintain a processing rate of at least 15 frames per second
5. WHEN network connectivity is lost, THE Pose_Detector SHALL continue processing frames locally without interruption
6. THE System SHALL NOT store raw video frames to disk or transmit them over the network

### Requirement 2: Exercise Recognition

**User Story:** As a user, I want the system to automatically detect which exercise I am performing, so that I don't need to manually select it.

#### Acceptance Criteria

1. WHEN the user begins moving, THE Exercise_Recognizer SHALL identify the exercise type within 3 seconds
2. THE Exercise_Recognizer SHALL support detection of push-ups, squats, plank holds, and jumping jacks
3. WHEN Pose_Keypoints match an exercise pattern, THE Exercise_Recognizer SHALL classify the exercise with at least 90% accuracy
4. WHEN the user transitions between exercises, THE Exercise_Recognizer SHALL detect the new exercise within 2 seconds
5. WHEN Pose_Keypoints are ambiguous, THE Exercise_Recognizer SHALL prompt the user to confirm the exercise type
6. THE Exercise_Recognizer SHALL use rule-based joint angle analysis for exercise classification

### Requirement 3: Repetition Counting

**User Story:** As a user, I want accurate counting of my exercise repetitions, so that I can track my workout progress.

#### Acceptance Criteria

1. WHEN the user completes a full range of motion, THE Rep_Counter SHALL increment the repetition count by one
2. THE Rep_Counter SHALL use Biomechanical_Angle thresholds specific to each exercise type
3. WHEN a push-up is performed, THE Rep_Counter SHALL count a repetition when elbow angle transitions from greater than 160 degrees to less than 90 degrees and back
4. WHEN a squat is performed, THE Rep_Counter SHALL count a repetition when knee angle transitions from greater than 160 degrees to less than 90 degrees and back
5. WHEN a jumping jack is performed, THE Rep_Counter SHALL count a repetition when arm angle transitions from less than 30 degrees to greater than 160 degrees and back
6. WHEN a partial range of motion is detected, THE Rep_Counter SHALL NOT increment the count and SHALL provide feedback
7. THE Rep_Counter SHALL maintain counting accuracy of at least 95% compared to manual counting

### Requirement 4: Form Analysis and Correction

**User Story:** As a user, I want real-time feedback on my exercise form, so that I can correct mistakes and prevent injury.

#### Acceptance Criteria

1. WHEN the user performs an exercise, THE Form_Analyzer SHALL evaluate posture every 500 milliseconds
2. WHEN a form mistake is detected, THE Form_Analyzer SHALL display a corrective suggestion within 1 second
3. WHEN performing push-ups with hips sagging, THE Form_Analyzer SHALL detect hip angle deviation greater than 15 degrees and suggest core engagement
4. WHEN performing squats with knees caving inward, THE Form_Analyzer SHALL detect knee alignment deviation and suggest proper knee tracking
5. WHEN performing push-ups with elbows flaring beyond 45 degrees, THE Form_Analyzer SHALL suggest tucking elbows closer to body
6. WHEN a plank is held, THE Form_Analyzer SHALL continuously monitor hip height and alert when deviation exceeds 10 degrees
7. THE Form_Analyzer SHALL calculate a Form_Score for each Workout_Session based on detected mistakes
8. THE Form_Analyzer SHALL use rule-based biomechanical analysis for mistake detection

### Requirement 5: Camera Placement Guidance

**User Story:** As a user, I want clear instructions on camera placement, so that the system can accurately track my movements.

#### Acceptance Criteria

1. WHEN the user starts a new Workout_Session, THE System SHALL display the Camera_Placement_Tutorial
2. THE Camera_Placement_Tutorial SHALL specify a distance of 2.5 to 3 meters from the user
3. THE Camera_Placement_Tutorial SHALL specify camera height at waist level
4. THE Camera_Placement_Tutorial SHALL show exercise-specific camera angles for each supported exercise
5. WHEN the user is not fully visible in frame, THE System SHALL display a warning and pause exercise tracking
6. THE System SHALL verify full body visibility before allowing Workout_Session to begin
7. WHEN camera placement is incorrect, THE System SHALL provide visual guides showing proper positioning

### Requirement 6: Post-Workout Analysis

**User Story:** As a user, I want a detailed summary after my workout, so that I can understand my performance and areas for improvement.

#### Acceptance Criteria

1. WHEN a Workout_Session ends, THE System SHALL generate a summary within 2 seconds
2. THE System SHALL display total repetitions completed for each exercise type
3. THE System SHALL display total workout duration in minutes and seconds
4. THE System SHALL display the average Form_Score for the Workout_Session
5. THE System SHALL identify and display the top 3 most frequent form mistakes
6. THE System SHALL provide specific recommendations for improving weak areas
7. THE System SHALL store the workout summary in the User_Profile for historical tracking

### Requirement 7: AI Workout Plan Generation

**User Story:** As a user, I want personalized workout plans based on my body stats and goals, so that I can follow an effective fitness routine.

#### Acceptance Criteria

1. WHEN the user requests a Workout_Plan, THE AI_Coach SHALL generate a plan within 10 seconds
2. THE AI_Coach SHALL incorporate user weight, height, body type, fitness goals, dietary preferences, and available time
3. THE Workout_Plan SHALL include specific exercises with sets, repetitions, and rest periods
4. THE AI_Coach SHALL use an LLM API to generate contextually appropriate workout recommendations
5. WHEN the user completes a Workout_Plan, THE AI_Coach SHALL adjust future plans based on performance data
6. THE Workout_Plan SHALL be achievable within the user's specified available time
7. WHEN the user has physical limitations, THE AI_Coach SHALL modify exercises to accommodate restrictions

### Requirement 8: Conversational AI Coach

**User Story:** As a user, I want to chat with an AI coach for fitness advice and motivation, so that I feel supported in my fitness journey.

#### Acceptance Criteria

1. WHEN the user sends a message, THE AI_Coach SHALL respond within 5 seconds
2. THE AI_Coach SHALL provide motivating and encouraging responses using a supportive personality
3. THE AI_Coach SHALL answer fitness-related questions using accurate exercise science principles
4. WHEN the user asks about exercise form, THE AI_Coach SHALL provide detailed technique explanations
5. WHEN the user expresses frustration, THE AI_Coach SHALL provide empathetic and constructive encouragement
6. THE AI_Coach SHALL reference the user's workout history when providing personalized advice
7. THE AI_Coach SHALL use an LLM API for natural language understanding and generation

### Requirement 9: Notifications and Reminders

**User Story:** As a user, I want workout reminders and streak tracking, so that I stay consistent with my fitness routine.

#### Acceptance Criteria

1. WHEN the user sets a workout schedule, THE Notification_Service SHALL send reminders at specified times
2. THE Notification_Service SHALL track consecutive days of completed workouts as a streak
3. WHEN the user completes a workout, THE Notification_Service SHALL update the streak counter
4. WHEN the user misses a scheduled workout, THE Notification_Service SHALL send a motivational reminder within 2 hours
5. WHEN the user achieves a streak milestone, THE Notification_Service SHALL display a congratulatory message
6. THE System SHALL allow users to configure notification preferences including frequency and timing
7. WHEN a workout reminder is dismissed, THE Notification_Service SHALL reschedule according to user preferences

### Requirement 10: User Management and Profile

**User Story:** As a user, I want to create an account and store my fitness data, so that I can track progress over time.

#### Acceptance Criteria

1. WHEN a new user registers, THE System SHALL collect email, password, weight, height, body type, and fitness goals
2. THE System SHALL validate email format and password strength before account creation
3. THE System SHALL store User_Profile data securely with encrypted passwords
4. WHEN the user logs in, THE System SHALL authenticate credentials and establish a session
5. THE System SHALL maintain a complete history of all Workout_Sessions for each user
6. THE System SHALL allow users to update their body stats and fitness goals at any time
7. WHEN the user views their profile, THE System SHALL display workout statistics including total sessions, total reps, and average Form_Score

### Requirement 11: Privacy and Data Protection

**User Story:** As a user, I want my workout video to remain private, so that I feel comfortable exercising at home.

#### Acceptance Criteria

1. THE System SHALL process all video frames locally in the browser before any network transmission
2. THE System SHALL extract only Pose_Keypoints from video frames
3. THE System SHALL delete raw video frames immediately after Pose_Keypoints extraction
4. THE System SHALL NOT store raw video frames in browser storage, server storage, or any persistent medium
5. THE System SHALL transmit only Pose_Keypoints and derived metrics to the backend server
6. WHEN the user closes the browser, THE System SHALL clear all pose data from browser memory
7. THE System SHALL comply with privacy-first design principles throughout all components

### Requirement 12: Performance and Responsiveness

**User Story:** As a user, I want the system to respond quickly without lag, so that I receive timely feedback during my workout.

#### Acceptance Criteria

1. THE Pose_Detector SHALL process video frames with latency less than 500 milliseconds
2. THE System SHALL maintain frame processing rate of at least 15 frames per second on standard hardware
3. WHEN the Rep_Counter detects a completed repetition, THE System SHALL update the display within 200 milliseconds
4. WHEN the Form_Analyzer detects a mistake, THE System SHALL display feedback within 1 second
5. THE System SHALL optimize browser performance to use less than 70% CPU during active workout tracking
6. THE System SHALL function on devices with at least 4GB RAM and dual-core processors
7. WHEN multiple users access the system simultaneously, THE System SHALL maintain response times within specified limits

### Requirement 13: Scalable Exercise Library

**User Story:** As a developer, I want the system architecture to support adding new exercises, so that the platform can grow beyond the MVP.

#### Acceptance Criteria

1. THE Exercise_Recognizer SHALL use a modular architecture allowing new exercise definitions to be added
2. WHEN a new exercise is added, THE System SHALL require only exercise-specific angle thresholds and form rules
3. THE System SHALL store exercise definitions in a structured format separate from core logic
4. THE Rep_Counter SHALL support configurable Biomechanical_Angle thresholds for each exercise type
5. THE Form_Analyzer SHALL support configurable form rules for each exercise type
6. WHEN a new exercise is added, THE System SHALL NOT require changes to the Pose_Detector component
7. THE System SHALL maintain a registry of supported exercises accessible to all components

### Requirement 14: WebSocket Real-Time Communication

**User Story:** As a user, I want seamless real-time communication between my browser and the server, so that feedback is immediate.

#### Acceptance Criteria

1. WHEN a Workout_Session begins, THE System SHALL establish a WebSocket connection between frontend and backend
2. THE System SHALL transmit Pose_Keypoints from frontend to backend via WebSocket with latency less than 100 milliseconds
3. WHEN the WebSocket connection is interrupted, THE System SHALL attempt reconnection every 5 seconds
4. WHEN the WebSocket connection is lost, THE System SHALL buffer Pose_Keypoints locally and sync when reconnected
5. THE System SHALL send exercise recognition results from backend to frontend via WebSocket
6. THE System SHALL send form correction feedback from backend to frontend via WebSocket
7. WHEN a Workout_Session ends, THE System SHALL gracefully close the WebSocket connection

### Requirement 15: Error Handling and Edge Cases

**User Story:** As a user, I want the system to handle errors gracefully, so that my workout experience is not disrupted.

#### Acceptance Criteria

1. WHEN camera access is denied, THE System SHALL display a clear error message with instructions to enable permissions
2. WHEN lighting conditions are poor, THE System SHALL detect low confidence in Pose_Keypoints and alert the user
3. WHEN the user moves out of frame, THE System SHALL pause tracking and display a warning
4. WHEN the Pose_Detector fails to extract keypoints, THE System SHALL retry for 3 seconds before alerting the user
5. WHEN the backend server is unreachable, THE System SHALL display an offline message and cache data locally
6. WHEN an unexpected error occurs, THE System SHALL log the error details and display a user-friendly message
7. THE System SHALL provide recovery options for all error conditions without requiring page refresh
