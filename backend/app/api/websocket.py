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
from uuid import UUID, uuid4

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
    SessionSavedMessage,
    SetExerciseMessage
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


def convert_uuids(obj):
    """Convert UUID objects to strings for JSON serialization"""
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_uuids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuids(item) for item in obj]
    return obj


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
        self.target_exercise: Optional[ExerciseType] = None
        self.current_exercise: Optional[ExerciseType] = None
        self.is_active = True
        self.start_time = datetime.utcnow()
        self.session_id: Optional[UUID] = None
        
        # Aggregated data for persistence
        self.exercise_history: Dict[ExerciseType, Dict] = {}
        self.total_reps_session = 0
        self.pose_buffer = []  # Buffer for pose data if needed
        
        logger.info(f"WorkoutSession created for user {user_id}")
    
    async def handle_pose_data(self, pose_data: PoseData) -> None:
        """
        Process incoming pose data and send continuous real-time feedback.
        """
        import time
        try:
            # ── Step 1: Exercise recognition ──
            if not self.target_exercise:
                exercise, confidence = self.exercise_recognizer.recognize(pose_data)
                if (exercise != ExerciseType.UNKNOWN and
                        exercise != self.current_exercise and
                        confidence > 0.7):
                    self.current_exercise = exercise
                    self.rep_counter = RepCounter(exercise)
                    await self.send_message(ExerciseDetectedMessage(
                        exercise=exercise.value, confidence=confidence
                    ))
                    logger.info(f"Exercise detected: {exercise.value} for user {self.user_id}")
            else:
                self.current_exercise = self.target_exercise
                if self.rep_counter is None:
                    self.rep_counter = RepCounter(self.target_exercise)

            # ── Step 2: Rep counting ──
            if self.current_exercise and self.current_exercise != ExerciseType.UNKNOWN and self.rep_counter:
                new_count = self.rep_counter.update(pose_data)
                if new_count is not None:
                    self.total_reps_session = new_count
                    if self.current_exercise not in self.exercise_history:
                        self.exercise_history[self.current_exercise] = {
                            "reps": 0, "form_scores": [], "mistakes": {}
                        }
                    self.exercise_history[self.current_exercise]["reps"] = new_count
                    await self.send_message(RepCountedMessage(
                        count=new_count, total=self.total_reps_session
                    ))
                    logger.info(f"REP! User {self.user_id} count={new_count}")

            # ── Step 3: Form analysis + continuous coach feedback ──
            now = time.time()
            run_feedback = (
                self.current_exercise and self.current_exercise != ExerciseType.UNKNOWN
            )
            if run_feedback:
                try:
                    mistakes = self.form_analyzer.analyze(pose_data, self.current_exercise)

                    if self.current_exercise not in self.exercise_history:
                        self.exercise_history[self.current_exercise] = {
                            "reps": 0, "form_scores": [], "mistakes": {}
                        }

                    form_score = self.form_analyzer.calculate_form_score(mistakes)

                    # Mismatch detection
                    if self.target_exercise:
                        detected_ex2, conf2 = self.exercise_recognizer.recognize(pose_data)
                        if (detected_ex2 != self.target_exercise and
                                detected_ex2 != ExerciseType.UNKNOWN and conf2 > 0.85):
                            await self.send_message(ErrorMessage(
                                message=f"⚠️ Mismatch! You selected {self.target_exercise.value} but we detect {detected_ex2.value}.",
                                code="EXERCISE_MISMATCH"
                            ))
                            form_score = min(form_score, 40)

                    # Visibility penalty
                    if pose_data.visibility_score and pose_data.visibility_score < 0.5:
                        form_score = min(form_score, 50)

                    self.exercise_history[self.current_exercise]["form_scores"].append(form_score)

                    for mistake in mistakes:
                        m_type = mistake.mistake_type
                        if m_type not in self.exercise_history[self.current_exercise]["mistakes"]:
                            self.exercise_history[self.current_exercise]["mistakes"][m_type] = {
                                "count": 0, "suggestion": mistake.suggestion, "severity": mistake.severity
                            }
                        self.exercise_history[self.current_exercise]["mistakes"][m_type]["count"] += 1

                    # Build feedback messages
                    form_mistakes = [
                        FormMistake(type=m.mistake_type, severity=m.severity, suggestion=m.suggestion)
                        for m in mistakes
                    ]

                    # Always send at least one feedback message (continuous coach)
                    if not form_mistakes:
                        rep_count = self.rep_counter.get_count() if self.rep_counter else 0
                        ex_name = self.current_exercise.value.replace('_', ' ').title()
                        if rep_count == 0:
                            tip = f"✅ Ready! Start your first {ex_name} rep. Keep your core tight."
                        elif rep_count < 5:
                            tip = f"💪 {rep_count} reps done! Great {ex_name} form — keep the rhythm going."
                        elif rep_count < 10:
                            tip = f"🔥 {rep_count} reps! You're building momentum. Control each movement."
                        else:
                            tip = f"⚡ {rep_count} reps! Outstanding! Push for {rep_count + 5} total."
                        form_mistakes.append(FormMistake(type="coach_tip", severity=0.0, suggestion=tip))

                    await self.send_message(FormFeedbackMessage(
                        mistakes=form_mistakes, form_score=form_score
                    ))
                except Exception as e:
                    logger.warning(f"Form analysis error: {e}")

            else:
                # No exercise detected — still send motivational coach feedback
                last_tip_time = getattr(self, '_last_idle_tip_time', 0)
                if now - last_tip_time > 3.0:  # Every 3 seconds when idle
                    self._last_idle_tip_time = now
                    ex_name = self.target_exercise.value.replace('_', ' ').title() if self.target_exercise else "an exercise"
                    tips = [
                        f"🎯 Stand in front of the camera and start {ex_name}. I'm watching!",
                        f"💡 Make sure your full body is visible in the frame for best tracking.",
                        f"🧘 Take a deep breath, set your stance, and begin when ready.",
                        f"⚡ Waiting for you to start {ex_name}. Let's go!",
                        f"📐 Position yourself 2-3 meters from the camera for full body detection.",
                    ]
                    import random
                    tip = random.choice(tips)
                    await self.send_message(FormFeedbackMessage(
                        mistakes=[FormMistake(type="coach_tip", severity=0.0, suggestion=tip)],
                        form_score=0.0
                    ))

        except Exception as e:
            logger.error(f"Error processing pose data for user {self.user_id}: {e}", exc_info=True)
            await self.send_message(ErrorMessage(
                message="Error processing pose data", code="POSE_PROCESSING_ERROR"
            ))

    async def handle_set_exercise(self, message: SetExerciseMessage) -> None:
        """
        Handle explicit exercise selection from frontend.
        """
        try:
            exercise_type = ExerciseType(message.exercise)
            self.target_exercise = exercise_type
            self.current_exercise = exercise_type
            self.rep_counter = RepCounter(exercise_type)
            
            # Initialize history for this exercise immediately
            if exercise_type not in self.exercise_history:
                self.exercise_history[exercise_type] = {
                    "reps": 0,
                    "form_scores": [],
                    "mistakes": {}
                }
            
            # Send immediate confirmation back
            await self.send_message(ExerciseDetectedMessage(
                exercise=exercise_type.value,
                confidence=1.0
            ))
            logger.info(f"Target exercise set to {exercise_type.value} for user {self.user_id}")
        except ValueError:
            logger.warning(f"Invalid exercise type requested: {message.exercise}")

    async def handle_session_end(self, message: SessionEndMessage) -> None:
        """
        Handle session end message and persist workout data.
        
        Args:
            message: Session end message
        """
        try:
            logger.info(f"Saving workout session for user {self.user_id}")
            logger.info(f"Exercise history: {self.exercise_history}")
            logger.info(f"Total reps: {self.total_reps_session}")
            logger.info(f"Current exercise: {self.current_exercise}")
            
            # If no exercises recorded, log it but do not create fake entries
            if not self.exercise_history:
                logger.info(f"No exercises recorded for user {self.user_id}, saving empty session.")
            
            # Prepare exercise records
            exercise_records = []
            for ex_type, data in self.exercise_history.items():
                ex_type_value = ex_type.value if hasattr(ex_type, 'value') else str(ex_type)
                
                # Calculate average form score
                avg_score = 85
                if data.get("form_scores") and len(data["form_scores"]) > 0:
                    avg_score = sum(data["form_scores"]) / len(data["form_scores"])
                
                reps = data.get("reps", 10)
                
                # Ensure mistakes is a dictionary
                mistakes_value = data.get("mistakes", {})
                if not isinstance(mistakes_value, dict):
                    if isinstance(mistakes_value, list):
                        mistakes_value = {"count": len(mistakes_value), "details": mistakes_value[:5] if mistakes_value else []}
                    else:
                        mistakes_value = {}
                
                logger.info(f"Creating record for {ex_type_value}: reps={reps}, form_score={avg_score}")
                
                exercise_records.append(
                    ExerciseRecordCreate(
                        exercise_type=ex_type_value,
                        reps_completed=reps,
                        duration_seconds=data.get("duration", 30),
                        form_score=avg_score,
                        mistakes=mistakes_value
                    )
                )
            
            # Calculate total reps
            total_reps = self.total_reps_session if self.total_reps_session > 0 else sum(r.reps_completed for r in exercise_records)
            
            # Handle user_id properly - if not a valid UUID, find user from database
            try:
                user_uuid = UUID(self.user_id)
                # Verify user exists in database
                from app.models.user import User
                from sqlalchemy import select
                result = await self.db.execute(select(User).where(User.user_id == user_uuid))
                user = result.scalar_one_or_none()
                if not user:
                    raise ValueError(f"User {user_uuid} not found")
            except ValueError as e:
                logger.error(f"Invalid or missing user: {e}. Falling back to omburande764@gmail.com")
                # Fallback specifically to omburande764@gmail.com as requested
                from app.models.user import User
                from sqlalchemy import select
                fallback_email = "omburande764@gmail.com"
                result = await self.db.execute(select(User).where(User.email == fallback_email))
                user = result.scalar_one_or_none()
                if user:
                    user_uuid = user.user_id
                    logger.info(f"Fallback successful. Using UID: {user_uuid}")
                else:
                    # If even the fallback doesn't exist, we must raise an error
                    raise ValueError(f"Valid user ID is required and fallback {fallback_email} not found in DB")
            
            # Create session persistence data
            workout_data = WorkoutSessionCreate(
                user_id=user_uuid,
                start_time=self.start_time,
                end_time=datetime.utcnow(),
                total_reps=total_reps,
                session_type="live",
                average_form_score=85,
                exercise_records=exercise_records
            )
            
            user_service = UserService(self.db)
            saved_session = await user_service.save_workout(workout_data)
            
            self.session_id = saved_session.session_id
            
            logger.info(f"Workout session saved with ID: {self.session_id}")
            
            # Notify client that session has been saved - convert UUID to string
            await self.send_message(SessionSavedMessage(session_id=str(self.session_id)))
            
            self.is_active = False
            
        except Exception as e:
            logger.error(f"Error saving workout session for user {self.user_id}: {e}", exc_info=True)
            error_message = ErrorMessage(
                message=f"Error saving workout session: {str(e)}",
                code="PERSISTENCE_ERROR"
            )
            await self.send_message(error_message)
            self.is_active = False
    
    async def send_message(self, message: ServerMessage) -> None:
        """
        Send a typed message to frontend.
        
        Args:
            message: Server message to send
        """
        try:
            # Convert to dict and handle UUID serialization
            message_dict = message.dict() if hasattr(message, 'dict') else message
            
            # Convert any UUID objects to strings
            serializable_dict = convert_uuids(message_dict)
            await self.websocket.send_json(serializable_dict)
        except Exception as e:
            logger.error(f"Error sending message to user {self.user_id}: {e}")
            self.is_active = False
    
    async def send_feedback(self, feedback: Dict) -> None:
        """Send feedback message to frontend (legacy method)."""
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
    """Manages active WebSocket connections and workout sessions."""
    
    def __init__(self):
        self.active_sessions: Dict[str, WorkoutSession] = {}
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket, user_id: str, db: AsyncSession) -> WorkoutSession:
        await websocket.accept()
        
        if user_id in self.active_sessions:
            await self.disconnect(user_id)
        
        session = WorkoutSession(user_id, websocket, db)
        self.active_sessions[user_id] = session
        
        logger.info(f"WebSocket connected for user {user_id}")
        return session
    
    async def disconnect(self, user_id: str) -> None:
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            session.cleanup()
            del self.active_sessions[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    def get_session(self, user_id: str) -> Optional[WorkoutSession]:
        return self.active_sessions.get(user_id)


ws_manager = WebSocketManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: AsyncSession = Depends(get_db)):
    session = await ws_manager.connect(websocket, user_id, db)
    
    try:
        await session.send_message(PongMessage())
        
        while session.is_active:
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected by client: {user_id}")
                break
            
            try:
                message_data = json.loads(data)
                
                try:
                    message = parse_client_message(message_data)
                    
                    if isinstance(message, PoseDataMessage):
                        pose_data = PoseData(
                            keypoints=message.keypoints,
                            timestamp=message.timestamp
                        )
                        await session.handle_pose_data(pose_data)
                    
                    elif isinstance(message, SessionEndMessage):
                        await session.handle_session_end(message)
                    
                    elif isinstance(message, PingMessage):
                        await session.send_message(PongMessage())
                        
                    elif isinstance(message, SetExerciseMessage):
                        await session.handle_set_exercise(message)
                
                except ValueError as e:
                    logger.warning(f"Invalid message from user {user_id}: {e}")
                    await session.send_message(ErrorMessage(
                        message=f"Invalid message: {str(e)}",
                        code="INVALID_MESSAGE_TYPE"
                    ))
                
                except ValidationError as e:
                    logger.warning(f"Message validation failed: {e}")
                    await session.send_message(ErrorMessage(
                        message=f"Message validation failed: {str(e)}",
                        code="VALIDATION_ERROR"
                    ))
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from user {user_id}: {e}")
                await session.send_message(ErrorMessage(
                    message="Invalid message format: JSON parsing failed",
                    code="JSON_DECODE_ERROR"
                ))
            
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await session.send_message(ErrorMessage(
                    message="Error processing message",
                    code="PROCESSING_ERROR"
                ))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected by client: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
    
    finally:
        await ws_manager.disconnect(user_id)