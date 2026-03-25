# WebSocket API Documentation

## Overview

The AI Gym Coach WebSocket API provides real-time bidirectional communication for workout tracking. The frontend sends pose keypoints, and the backend responds with exercise recognition, rep counting, and form feedback.

## Endpoint

```
ws://localhost:8000/ws/{user_id}
```

### Parameters

- `user_id` (path parameter): Unique identifier for the user

## Message Protocol

### Client → Server Messages

#### 1. Pose Data Message

Sent continuously during workout to provide pose keypoints for analysis.

```json
{
  "type": "pose_data",
  "keypoints": [
    {
      "x": 0.5,
      "y": 0.5,
      "z": 0.0,
      "visibility": 0.9,
      "name": "nose"
    },
    // ... 32 more keypoints
  ],
  "timestamp": 1234567890.0
}
```

**Fields:**
- `type`: Must be "pose_data"
- `keypoints`: Array of 33 pose keypoints from MediaPipe BlazePose
  - `x`: Normalized x-coordinate (0-1)
  - `y`: Normalized y-coordinate (0-1)
  - `z`: Depth relative to hips
  - `visibility`: Confidence score (0-1)
  - `name`: Joint name (e.g., "left_elbow", "right_knee")
- `timestamp`: Unix timestamp in milliseconds

#### 2. Ping Message

Used for connection health checks.

```json
{
  "type": "ping"
}
```

### Server → Client Messages

#### 1. Exercise Detected

Sent when the system recognizes which exercise the user is performing.

```json
{
  "type": "exercise_detected",
  "exercise": "pushup",
  "confidence": 0.95
}
```

**Fields:**
- `type`: "exercise_detected"
- `exercise`: Exercise type ("pushup", "squat", "plank", "jumping_jack")
- `confidence`: Recognition confidence (0-1)

#### 2. Rep Counted

Sent when a complete repetition is detected.

```json
{
  "type": "rep_counted",
  "count": 5,
  "total": 5
}
```

**Fields:**
- `type`: "rep_counted"
- `count`: Current rep count
- `total`: Total reps in session

#### 3. Form Feedback

Sent when form mistakes are detected.

```json
{
  "type": "form_feedback",
  "mistakes": [
    {
      "type": "hip_sag",
      "severity": 0.6,
      "suggestion": "Engage your core, keep hips in line"
    }
  ],
  "form_score": 85.0
}
```

**Fields:**
- `type`: "form_feedback"
- `mistakes`: Array of detected form mistakes
  - `type`: Mistake identifier (e.g., "hip_sag", "knee_cave")
  - `severity`: Severity score (0-1)
  - `suggestion`: Corrective suggestion text
- `form_score`: Overall form score (0-100)

#### 4. Pong Message

Response to ping for health check.

```json
{
  "type": "pong"
}
```

#### 5. Error Message

Sent when an error occurs during processing.

```json
{
  "type": "error",
  "message": "Error processing pose data"
}
```

**Fields:**
- `type`: "error"
- `message`: Error description

## Connection Flow

1. **Connect**: Client establishes WebSocket connection to `/ws/{user_id}`
2. **Session Created**: Server creates a `WorkoutSession` with exercise recognizer, rep counter, and form analyzer
3. **Pose Streaming**: Client continuously sends pose_data messages (15-30 FPS)
4. **Real-time Feedback**: Server processes each pose and sends back:
   - Exercise detection (when exercise changes)
   - Rep counting (when rep completes)
   - Form feedback (when mistakes detected)
5. **Disconnect**: Client closes connection, server cleans up session

## Example Usage (JavaScript)

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onopen = () => {
  console.log('Connected to workout session');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'exercise_detected':
      console.log(`Exercise: ${message.exercise} (${message.confidence})`);
      break;
    
    case 'rep_counted':
      console.log(`Reps: ${message.count}`);
      break;
    
    case 'form_feedback':
      console.log(`Form score: ${message.form_score}`);
      message.mistakes.forEach(mistake => {
        console.log(`- ${mistake.suggestion}`);
      });
      break;
    
    case 'error':
      console.error(`Error: ${message.message}`);
      break;
  }
};

// Send pose data
function sendPoseData(keypoints) {
  const message = {
    type: 'pose_data',
    keypoints: keypoints,
    timestamp: Date.now()
  };
  ws.send(JSON.stringify(message));
}

// Health check
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);

ws.onclose = () => {
  console.log('Disconnected from workout session');
};
```

## Implementation Details

### WorkoutSession Class

Manages state for a single workout session:
- Maintains exercise recognizer, rep counter, and form analyzer
- Processes incoming pose data
- Sends real-time feedback to client
- Handles errors gracefully

### WebSocketManager Class

Manages multiple active WebSocket connections:
- Tracks active sessions by user_id
- Handles connection/disconnection
- Ensures only one session per user

### Processing Pipeline

For each pose_data message:
1. **Exercise Recognition**: Identify exercise type using biomechanical patterns
2. **Rep Counting**: Track state transitions and count completed reps
3. **Form Analysis**: Detect form mistakes and calculate form score
4. **Feedback**: Send relevant feedback messages to client

## Error Handling

- Invalid JSON: Returns error message, continues connection
- Processing errors: Returns error message, continues connection
- Connection errors: Logs error, closes connection, cleans up session
- Malformed messages: Logs warning, ignores message

## Performance Considerations

- **Latency**: Target <100ms for pose data processing
- **Throughput**: Handles 15-30 pose messages per second
- **Memory**: Each session maintains sliding window of recent poses
- **Concurrency**: Supports multiple concurrent user sessions

## Requirements Implemented

- **Requirement 14.1**: WebSocket connection established at session start
- **Requirement 14.7**: Graceful connection closure at session end
- **Requirement 2.1**: Exercise recognition within 3 seconds
- **Requirement 3.1**: Rep counting with state machine
- **Requirement 4.1**: Form analysis every 500ms

## Testing

Run WebSocket tests:
```bash
pytest tests/test_websocket.py -v
```

Test coverage includes:
- Session initialization and cleanup
- Message handling (pose_data, ping)
- Exercise detection
- Rep counting
- Form analysis
- Error handling
- Connection management
