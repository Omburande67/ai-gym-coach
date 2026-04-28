"""WebSocket message models for real-time workout tracking.

This module defines the message protocol for bidirectional communication
between frontend and backend during workout sessions.

Implements Requirements 14.5, 14.6:
- Define message types and structure
- Provide message validation
"""

from typing import List, Literal, Union, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.pose import PoseKeypoint


class MessageType(str, Enum):
    """WebSocket message types."""
    # Client -> Server messages
    POSE_DATA = "pose_data"
    PING = "ping"
    SESSION_END = "session_end"
    SET_EXERCISE = "set_exercise"
    
    # Server -> Client messages
    EXERCISE_DETECTED = "exercise_detected"
    REP_COUNTED = "rep_counted"
    FORM_FEEDBACK = "form_feedback"
    PONG = "pong"
    ERROR = "error"
    SESSION_SAVED = "session_saved"


# Client -> Server Messages

class PoseDataMessage(BaseModel):
    """
    Pose data message from client to server.
    
    Sent by frontend when new pose keypoints are detected.
    """
    type: Literal[MessageType.POSE_DATA] = Field(
        default=MessageType.POSE_DATA,
        description="Message type identifier"
    )
    keypoints: List[PoseKeypoint] = Field(
        ...,
        description="33 keypoints from pose detection",
        min_items=1,
        max_items=33
    )
    timestamp: float = Field(
        ...,
        description="Unix timestamp in milliseconds",
        gt=0
    )
    
    @validator('keypoints')
    def validate_keypoints(cls, v):
        """Validate that keypoints have required fields."""
        if not v:
            raise ValueError("Keypoints list cannot be empty")
        
        # Check that all keypoints have valid coordinates
        for kp in v:
            if not (0 <= kp.x <= 1):
                raise ValueError(f"Keypoint {kp.name} x-coordinate must be between 0 and 1")
            if not (0 <= kp.y <= 1):
                raise ValueError(f"Keypoint {kp.name} y-coordinate must be between 0 and 1")
            if not (0 <= kp.visibility <= 1):
                raise ValueError(f"Keypoint {kp.name} visibility must be between 0 and 1")
        
        return v


class PingMessage(BaseModel):
    """
    Ping message for connection health check.
    
    Sent by frontend to verify WebSocket connection is alive.
    """
    type: Literal[MessageType.PING] = Field(
        default=MessageType.PING,
        description="Message type identifier"
    )


class SessionEndMessage(BaseModel):
    """
    Message from client to signal end of workout session.
    
    Triggers workout data persistence on the server.
    """
    type: Literal[MessageType.SESSION_END] = Field(
        default=MessageType.SESSION_END,
        description="Message type identifier"
    )
    timestamp: float = Field(
        ...,
        description="Unix timestamp in milliseconds",
        gt=0
    )


class SetExerciseMessage(BaseModel):
    """
    Message to explicitly set the exercise to track.
    
    Sent by frontend when a specific exercise is selected for the session.
    """
    type: Literal[MessageType.SET_EXERCISE] = Field(
        default=MessageType.SET_EXERCISE,
        description="Message type identifier"
    )
    exercise: str = Field(
        ...,
        description="Exercise type to track"
    )


# Server -> Client Messages

class ExerciseDetectedMessage(BaseModel):
    """
    Exercise detection message from server to client.
    
    Sent when the system identifies which exercise the user is performing.
    """
    type: Literal[MessageType.EXERCISE_DETECTED] = Field(
        default=MessageType.EXERCISE_DETECTED,
        description="Message type identifier"
    )
    exercise: str = Field(
        ...,
        description="Exercise type (pushup, squat, plank, jumping_jack)"
    )
    confidence: float = Field(
        ...,
        description="Confidence score (0-1)",
        ge=0.0,
        le=1.0
    )


class RepCountedMessage(BaseModel):
    """
    Rep counted message from server to client.
    
    Sent when a complete repetition is detected.
    """
    type: Literal[MessageType.REP_COUNTED] = Field(
        default=MessageType.REP_COUNTED,
        description="Message type identifier"
    )
    count: int = Field(
        ...,
        description="New rep count for current set",
        ge=0
    )
    total: int = Field(
        ...,
        description="Total reps in session",
        ge=0
    )


class FormMistakeData(BaseModel):
    """Form mistake data structure."""
    type: str = Field(
        ...,
        description="Mistake type (hip_sag, knee_cave, etc.)"
    )
    severity: float = Field(
        ...,
        description="Severity score (0-1)",
        ge=0.0,
        le=1.0
    )
    suggestion: str = Field(
        ...,
        description="Corrective suggestion for the user"
    )


class FormFeedbackMessage(BaseModel):
    """
    Form feedback message from server to client.
    
    Sent when form mistakes are detected during exercise.
    """
    type: Literal[MessageType.FORM_FEEDBACK] = Field(
        default=MessageType.FORM_FEEDBACK,
        description="Message type identifier"
    )
    mistakes: List[FormMistakeData] = Field(
        ...,
        description="List of detected form mistakes"
    )
    form_score: float = Field(
        ...,
        description="Overall form score (0-100)",
        ge=0.0,
        le=100.0
    )


class SessionSavedMessage(BaseModel):
    """
    Message from server when workout has been successfully saved.
    """
    type: Literal[MessageType.SESSION_SAVED] = Field(
        default=MessageType.SESSION_SAVED,
        description="Message type identifier"
    )
    session_id: UUID = Field(
        ...,
        description="UUID of the saved workout session"
    )
    
class PongMessage(BaseModel):
    """
    Pong message response to ping.
    
    Sent by server in response to ping for connection health check.
    """
    type: Literal[MessageType.PONG] = Field(
        default=MessageType.PONG,
        description="Message type identifier"
    )


class ErrorMessage(BaseModel):
    """
    Error message from server to client.
    
    Sent when an error occurs during message processing.
    """
    type: Literal[MessageType.ERROR] = Field(
        default=MessageType.ERROR,
        description="Message type identifier"
    )
    message: str = Field(
        ...,
        description="Error message description"
    )
    code: Optional[str] = Field(
        None,
        description="Optional error code for client handling"
    )


# Union type for all client messages
ClientMessage = Union[PoseDataMessage, PingMessage, SessionEndMessage, SetExerciseMessage]

# Union type for all server messages
ServerMessage = Union[
    ExerciseDetectedMessage,
    RepCountedMessage,
    FormFeedbackMessage,
    PongMessage,
    ErrorMessage,
    SessionSavedMessage
]


def parse_client_message(data: dict) -> ClientMessage:
    """
    Parse and validate incoming client message.
    
    Args:
        data: Raw message data from WebSocket
        
    Returns:
        Validated message object
        
    Raises:
        ValueError: If message type is unknown or validation fails
    """
    message_type = data.get("type")
    
    if message_type == MessageType.POSE_DATA:
        return PoseDataMessage(**data)
    elif message_type == MessageType.PING:
        return PingMessage(**data)
    elif message_type == MessageType.SESSION_END:
        return SessionEndMessage(**data)
    elif message_type == MessageType.SET_EXERCISE:
        return SetExerciseMessage(**data)
    else:
        raise ValueError(f"Unknown message type: {message_type}")
