"""WebSocket endpoint for real-time workout tracking.

This module implements the WebSocket server for bidirectional communication
between frontend and backend during workout sessions.

Implements Requirements 14.5, 14.6:
- Define and validate message protocol
- Handle malformed messages gracefully
"""

from typing import Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import ValidationError
import json
import logging
from datetime import datetime
from uuid import UUID

from app.models.pose import PoseData
from app.models.exercise import ExerciseType
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.websocket_messages import (
    parse_client_message,
    MessageType,
    PoseDataMessage,
    PingMessage,
    ExerciseDetectedMessage,
    RepCountedMessage,
    FormFeedbackMessage,
    FormMistakeData,
    PongMessage,
    ErrorMessage,
    ServerMessage,
    SessionEndMessage,
    SessionSavedMessage
)
from app.api.deps import get_db
from app.schemas.workout import WorkoutSessionCreate, ExerciseRecordCreate
from app.services.user_service import UserService
from app.services.exercise_recognizer import ExerciseRecognizer
from app.services.rep_counter import RepCounter
from app.services.form_analyzer import FormAnalyzer
from app.services.exercise_registry import exercise_registry

logger = logging.getLogger(__name__)

router = APIRouter()


class WorkoutSession:
    """
    Manages state for a single workout session.
    
    Implements Requirements 14.1, 14.7:
    - Manages WebSocket connection and session state
    - Processes pose data and sends feedback
    """
    
    def __init__(self, user_id: str, websocket: WebSocket, db: AsyncSession):
        """
        Initialize a workout session.
        
        Args:
            user_id: Unique identifier for the user
            websocket: WebSocket connection
            db: Database session for persistence
        """
        self.user_id = user_id
        self.websocket = websocket
        self.db = db
        
        # Initialize analysis components
        self.exercise_recognizer = ExerciseRecognizer()
        self.rep_counter: Optional[RepCounter] = None
        self.form_analyzer = FormAnalyzer(exercise_registry)
        
        # Session state
        self.current_exercise: Optional[ExerciseType] = None
        self.is_active = True
        self.start_time = datetime.utcnow()
        
        # Aggregated data for persistence
        self.exercise_history: Dict[ExerciseType, Dict] = {}
        self.total_reps_session = 0
        
        logger.info(f"WorkoutSession created for user {user_id}")
    
    async def handle_pose_data(self, pose_data: PoseData) -> None:
        """
        Process incoming pose data and send feedback.
        
        Args:
            pose_data: Pose keypoints from frontend
        """
        try:
            # Step 1: Exercise recognition
            exercise_type, confidence = self.exercise_recognizer.recognize(pose_data)
            
            # If exercise changed, notify frontend and reset rep counter
            if exercise_type != self.current_exercise and exercise_type != ExerciseType.UNKNOWN:
                self.current_exercise = exercise_type
                self.rep_counter = RepCounter(exercise_type)
                
                message = ExerciseDetectedMessage(
                    exercise=exercise_type.value,
                    confidence=confidence
                )
                await self.send_message(message)
                
                logger.info(f"Exercise detected for user {self.user_id}: {exercise_type.value}")
            
            # Step 2: Rep counting (if exercise is recognized)
            if self.current_exercise and self.current_exercise != ExerciseType.UNKNOWN and self.rep_counter:
                new_count = self.rep_counter.update(pose_data)
                
                if new_count is not None:
                    # Update aggregate total
                    self.total_reps_session += 1
                    
                    # Update exercise history
                    if self.current_exercise not in self.exercise_history:
                        self.exercise_history[self.current_exercise] = {
                            "reps": 0,
                            "form_scores": [],
                            "mistakes": []
                        }
                    self.exercise_history[self.current_exercise]["reps"] = new_count
                    
                    message = RepCountedMessage(
                        count=new_count,
                        total=self.total_reps_session
                    )
                    await self.send_message(message)
                    
                    logger.debug(f"Rep counted for user {self.user_id}: {new_count}")
            
            # Step 3: Form analysis (if exercise is recognized)
            if self.current_exercise and self.current_exercise != ExerciseType.UNKNOWN:
                mistakes = self.form_analyzer.analyze(pose_data, self.current_exercise)
                
                if self.current_exercise in self.exercise_history:
                    # Calculate form score (simplified for now)
                    form_score = max(0, 100 - len(mistakes) * 10)
                    
                    self.exercise_history[self.current_exercise]["form_scores"].append(form_score)
                    mistake_records = []
                    for mistake in mistakes:
                        mistake_records.append({
                            "type": mistake.mistake_type,
                            "severity": mistake.severity,
                            "suggestion": mistake.suggestion,
                            "timestamp": pose_data.timestamp
                        })
                    
                    if "mistakes" not in self.exercise_history[self.current_exercise]:
                         self.exercise_history[self.current_exercise]["mistakes"] = []
                    self.exercise_history[self.current_exercise]["mistakes"].extend(mistake_records)
                    
                    message = FormFeedbackMessage(
                        mistakes=[
                            FormMistakeData(
                                type=mistake.mistake_type,
                                severity=mistake.severity,
                                suggestion=mistake.suggestion
                            )
                            for mistake in mistakes
                        ],
                        form_score=form_score
                    )
                    await self.send_message(message)
                    
                    logger.debug(f"Form feedback sent for user {self.user_id}: {len(mistakes)} mistakes")
        
        except Exception as e:
            logger.error(f"Error processing pose data for user {self.user_id}: {e}", exc_info=True)
            error_message = ErrorMessage(
                message="Error processing pose data",
                code="POSE_PROCESSING_ERROR"
            )
            await self.send_message(error_message)

    async def handle_session_end(self, message: SessionEndMessage) -> None:
        """
        Handle session end message and persist workout data.
        
        Args:
            message: Session end message
        """
        try:
            logger.info(f"Saving workout session for user {self.user_id}")
            
            # Prepare exercise records
            exercise_records = []
            for ex_type, data in self.exercise_history.items():
                # Calculate average form score for this exercise
                avg_score = None
                if data["form_scores"]:
                    avg_score = sum(data["form_scores"]) / len(data["form_scores"])
                
                exercise_records.append(
                    ExerciseRecordCreate(
                        exercise_type=ex_type.value,
                        reps_completed=data["reps"],
                        duration_seconds=data.get("duration"),  # For plank
                        form_score=avg_score,
                        mistakes=data["mistakes"]  # This will be JSONB
                    )
                )
            
            if not exercise_records:
                logger.warning(f"No exercises recorded for user {self.user_id}, skipping save")
                self.is_active = False
                return

            # Create session persistence data
            workout_data = WorkoutSessionCreate(
                user_id=UUID(self.user_id),
                start_time=self.start_time,
                end_time=datetime.utcnow(),
                exercise_records=exercise_records
            )
            
            user_service = UserService(self.db)
            saved_session = await user_service.save_workout(workout_data)
            
            logger.info(f"Workout session saved with ID: {saved_session.session_id}")
            
            # Notify client that session has been saved
            await self.send_message(SessionSavedMessage(session_id=saved_session.session_id))
            
            self.is_active = False
            
        except Exception as e:
            logger.error(f"Error saving workout session for user {self.user_id}: {e}", exc_info=True)
            error_message = ErrorMessage(
                message="Error saving workout session",
                code="PERSISTENCE_ERROR"
            )
            await self.send_message(error_message)
    
    async def send_message(self, message: ServerMessage) -> None:
        """
        Send a typed message to frontend.
        
        Args:
            message: Server message to send
        """
        try:
            await self.websocket.send_json(message.dict())
        except Exception as e:
            logger.error(f"Error sending message to user {self.user_id}: {e}")
            self.is_active = False
    
    async def send_feedback(self, feedback: Dict) -> None:
        """
        Send feedback message to frontend (legacy method for compatibility).
        
        Args:
            feedback: Feedback data to send
            
        Deprecated: Use send_message() with typed messages instead.
        """
        try:
            await self.websocket.send_json(feedback)
        except Exception as e:
            logger.error(f"Error sending feedback to user {self.user_id}: {e}")
            self.is_active = False
    
    def cleanup(self) -> None:
        """Clean up session resources."""
        self.is_active = False
        logger.info(f"WorkoutSession cleaned up for user {self.user_id}")


class WebSocketManager:
    """
    Manages active WebSocket connections and workout sessions.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_sessions: Dict[str, WorkoutSession] = {}
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket, user_id: str, db: AsyncSession) -> WorkoutSession:
        """
        Accept WebSocket connection and create session.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
            db: Database session
            
        Returns:
            Created WorkoutSession
        """
        await websocket.accept()
        
        # Close existing session if any
        if user_id in self.active_sessions:
            await self.disconnect(user_id)
        
        # Create new session
        session = WorkoutSession(user_id, websocket, db)
        self.active_sessions[user_id] = session
        
        logger.info(f"WebSocket connected for user {user_id}")
        return session
    
    async def disconnect(self, user_id: str) -> None:
        """
        Close WebSocket and cleanup session.
        
        Args:
            user_id: User identifier
        """
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            session.cleanup()
            del self.active_sessions[user_id]
            
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    def get_session(self, user_id: str) -> Optional[WorkoutSession]:
        """
        Get active session for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            WorkoutSession if exists, None otherwise
        """
        return self.active_sessions.get(user_id)


# Global WebSocket manager instance
ws_manager = WebSocketManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: AsyncSession = Depends(get_db)):
    """
    WebSocket endpoint for real-time workout tracking.
    
    Implements Requirements 14.1, 14.5, 14.6, 14.7:
    - Establishes WebSocket connection
    - Validates and parses incoming messages
    - Handles malformed messages gracefully
    - Sends real-time feedback
    
    Args:
        websocket: WebSocket connection
        user_id: User identifier
        db: Database session for persistence
    """
    session = await ws_manager.connect(websocket, user_id, db)
    
    try:
        while session.is_active:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse JSON
                message_data = json.loads(data)
                
                # Validate and parse message using Pydantic models
                try:
                    message = parse_client_message(message_data)
                    
                    # Handle different message types
                    if isinstance(message, PoseDataMessage):
                        # Convert to PoseData for processing
                        pose_data = PoseData(
                            keypoints=message.keypoints,
                            timestamp=message.timestamp
                        )
                        await session.handle_pose_data(pose_data)
                    
                    elif isinstance(message, SessionEndMessage):
                        # Signal end of workout and persist data
                        await session.handle_session_end(message)
                        # We don't break yet, let the while loop check session.is_active
                    
                    elif isinstance(message, PingMessage):
                        # Respond to ping for connection health check
                        pong = PongMessage()
                        await session.send_message(pong)
                
                except ValueError as e:
                    # Unknown message type or validation error
                    logger.warning(f"Invalid message from user {user_id}: {e}")
                    error_message = ErrorMessage(
                        message=f"Invalid message: {str(e)}",
                        code="INVALID_MESSAGE_TYPE"
                    )
                    await session.send_message(error_message)
                
                except ValidationError as e:
                    # Pydantic validation error
                    logger.warning(f"Message validation failed for user {user_id}: {e}")
                    error_message = ErrorMessage(
                        message=f"Message validation failed: {str(e)}",
                        code="VALIDATION_ERROR"
                    )
                    await session.send_message(error_message)
            
            except json.JSONDecodeError as e:
                # Malformed JSON
                logger.error(f"Invalid JSON from user {user_id}: {e}")
                error_message = ErrorMessage(
                    message="Invalid message format: JSON parsing failed",
                    code="JSON_DECODE_ERROR"
                )
                await session.send_message(error_message)
            
            except Exception as e:
                # Unexpected error
                logger.error(f"Error processing message from user {user_id}: {e}", exc_info=True)
                error_message = ErrorMessage(
                    message="Error processing message",
                    code="PROCESSING_ERROR"
                )
                await session.send_message(error_message)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected by client: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
    
    finally:
        await ws_manager.disconnect(user_id)
