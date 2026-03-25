"""User service for managing user accounts and authentication"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, NotificationPreferences, WorkoutStreak
from app.models.workout import WorkoutSession, ExerciseRecord, WorkoutPlan
from app.schemas.user import (
    UserCreate,
    UserProfile,
    UserUpdate,
    UserStatistics,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    WorkoutStreakResponse
)
from app.schemas.workout import (
    WorkoutSessionCreate,
    WorkoutSessionResponse,
    ExerciseRecordCreate,
    ExerciseRecordResponse,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
)
from app.services.llm_service import LLMService


class UserService:
    """Service class for user management operations"""

    def __init__(self, db: AsyncSession):
        """
        Initialize UserService with database session.
        
        Args:
            db: AsyncSession database session
        """
        self.db = db

    async def register(
        self, email: str, password: str, profile_data: Dict
    ) -> UserProfile:
        """
        Create a new user account.
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            profile_data: Dictionary containing weight_kg, height_cm, body_type, fitness_goals
            
        Returns:
            UserProfile: Created user profile
            
        Raises:
            ValueError: If email already exists
        """
        # Normalize email
        email = email.lower()

        # Check if user already exists
        existing_user = await self._get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash the password
        password_hash = hash_password(password)

        # Create new user
        new_user = User(
            email=email,
            password_hash=password_hash,
            weight_kg=profile_data.get("weight_kg"),
            height_cm=profile_data.get("height_cm"),
            body_type=profile_data.get("body_type"),
            fitness_goals=profile_data.get("fitness_goals"),
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return UserProfile.model_validate(new_user)

    async def authenticate(self, email: str, password: str) -> Optional[str]:
        """
        Authenticate user and return JWT token.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            Optional[str]: JWT access token if authentication successful, None otherwise
        """
        # Normalize email
        email = email.lower()

        # Get user by email
        user = await self._get_user_by_email(email)
        if not user:
            return None

        # Verify password
        if not verify_password(password, user.password_hash):
            return None

        # Create access token
        token_data = {"user_id": user.user_id, "email": user.email}
        access_token = create_access_token(data=token_data)

        return access_token

    async def get_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """
        Retrieve user profile by user ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            Optional[UserProfile]: User profile if found, None otherwise
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            return None

        return UserProfile.model_validate(user)

    async def update_profile(
        self, user_id: UUID, updates: Dict
    ) -> Optional[UserProfile]:
        """
        Update user profile data.
        
        Args:
            user_id: User UUID
            updates: Dictionary containing fields to update
            
        Returns:
            Optional[UserProfile]: Updated user profile if found, None otherwise
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            return None

        # Update allowed fields
        allowed_fields = ["weight_kg", "height_cm", "body_type", "fitness_goals"]
        for field in allowed_fields:
            if field in updates:
                setattr(user, field, updates[field])

        await self.db.commit()
        await self.db.refresh(user)

        return UserProfile.model_validate(user)

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        Internal method to get user by email.
        
        Args:
            email: User email address
            
        Returns:
            Optional[User]: User model if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Internal method to get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            Optional[User]: User model if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def save_workout(
        self, workout_data: WorkoutSessionCreate
    ) -> WorkoutSessionResponse:
        """
        Save completed workout session to database.
        
        Implements Requirements 6.7, 10.5:
        - Store workout_sessions and exercise_records in database
        - Maintain complete workout history
        
        Args:
            workout_data: Workout session data including exercise records
            
        Returns:
            WorkoutSessionResponse: Saved workout session with generated IDs
            
        Raises:
            ValueError: If user does not exist
        """
        # Verify user exists
        user = await self._get_user_by_id(workout_data.user_id)
        if not user:
            raise ValueError(f"User {workout_data.user_id} not found")

        # Calculate summary statistics
        total_reps = sum(record.reps_completed for record in workout_data.exercise_records)
        
        form_scores = [
            record.form_score
            for record in workout_data.exercise_records
            if record.form_score is not None
        ]
        average_form_score = (
            sum(form_scores) / len(form_scores) if form_scores else None
        )
        
        total_duration_seconds = None
        if workout_data.end_time and workout_data.start_time:
            total_duration_seconds = int(
                (workout_data.end_time - workout_data.start_time).total_seconds()
            )

        # Create workout session
        workout_session = WorkoutSession(
            user_id=workout_data.user_id,
            start_time=workout_data.start_time,
            end_time=workout_data.end_time,
            total_duration_seconds=total_duration_seconds,
            total_reps=total_reps,
            average_form_score=average_form_score,
        )

        self.db.add(workout_session)
        await self.db.flush()  # Flush to get session_id

        # Create exercise records
        for record_data in workout_data.exercise_records:
            exercise_record = ExerciseRecord(
                session_id=workout_session.session_id,
                exercise_type=record_data.exercise_type,
                reps_completed=record_data.reps_completed,
                duration_seconds=record_data.duration_seconds,
                form_score=record_data.form_score,
                mistakes=record_data.mistakes,
            )
            self.db.add(exercise_record)

        await self.db.commit()
        await self.db.refresh(workout_session)

        # Update user streak
        await self._update_streak(workout_session.user_id, workout_session.start_time)

        # Load exercise records for response
        result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.session_id == workout_session.session_id)
            .options(selectinload(WorkoutSession.exercise_records))
        )
        workout_with_records = result.scalar_one()

        return WorkoutSessionResponse.model_validate(workout_with_records)

    async def get_workout_history(
        self, user_id: UUID, limit: int = 10
    ) -> List[WorkoutSessionResponse]:
        """
        Retrieve recent workout history for a user.
        
        Implements Requirements 10.5:
        - Maintain complete history of all workout sessions
        
        Args:
            user_id: User UUID
            limit: Maximum number of sessions to return (default 10)
            
        Returns:
            List[WorkoutSessionResponse]: List of workout sessions with exercise records
        """
        # Query workout sessions with exercise records
        result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .options(selectinload(WorkoutSession.exercise_records))
            .order_by(WorkoutSession.start_time.desc())
            .limit(limit)
        )
        
        sessions = result.scalars().all()
        
        return [WorkoutSessionResponse.model_validate(session) for session in sessions]
    async def get_workout_summary(self, session_id: UUID) -> Optional[Dict]:
        """
        Generate a detailed summary for a workout session.
        
        Implements Requirements 6.2, 6.3, 6.4, 6.5, 6.6:
        - Calculate totals, duration, average form score
        - Identify top 3 most frequent mistakes
        - Generate recommendations
        
        Args:
            session_id: Workout session UUID
            
        Returns:
            Optional[Dict]: Workout summary data if found, None otherwise
        """
        # Get session with exercise records
        result = await self.db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.session_id == session_id)
            .options(selectinload(WorkoutSession.exercise_records))
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return None
            
        # Collect all mistakes
        all_mistakes = []
        for record in session.exercise_records:
            if record.mistakes:
                # Assuming mistakes is a list of dicts based on DATABASE.md
                if isinstance(record.mistakes, list):
                    all_mistakes.extend(record.mistakes)
                elif isinstance(record.mistakes, dict):
                    # Handle single mistake dict if stored that way
                    all_mistakes.append(record.mistakes)
        
        # Count frequency of each mistake type
        mistake_counts = {}
        mistake_details = {}
        for m in all_mistakes:
            m_type = m.get('type', 'unknown')
            mistake_counts[m_type] = mistake_counts.get(m_type, 0) + 1
            if m_type not in mistake_details:
                mistake_details[m_type] = {
                    'type': m_type,
                    'suggestion': m.get('suggestion', 'No suggestion available')
                }
        
        # Sort and get top 3
        sorted_mistakes = sorted(
            mistake_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        top_mistakes = [
            {
                **mistake_details[m_type],
                'count': count
            }
            for m_type, count in sorted_mistakes
        ]
        
        # Generate recommendations based on mistakes
        recommendations = []
        if not top_mistakes:
            recommendations.append("Excellent work! Your form was perfect. Try increasing intensity next time.")
        else:
            for m in top_mistakes:
                recommendations.append(f"Focus on your {m['type'].replace('_', ' ')}: {m['suggestion']}")
            
            if len(top_mistakes) > 1:
                recommendations.append("Consider doing a mobility session to improve your range of motion.")

        return {
            "session_id": session.session_id,
            "total_reps": session.total_reps,
            "total_duration_seconds": session.total_duration_seconds or 0,
            "average_form_score": float(session.average_form_score) if session.average_form_score is not None else 100.0,
            "top_mistakes": top_mistakes,
            "recommendations": recommendations,
            "exercises": [ExerciseRecordResponse.model_validate(r) for r in session.exercise_records]
        }

    async def generate_and_save_plan(self, user_id: UUID) -> WorkoutPlanResponse:
        """
        Generate a new personalized workout plan and save it.
        
        Implements Requirements 7.1, 7.2, 7.3, 7.4, 7.5:
        - Generate plan via LLM
        - Save to database
        - Set as active, deactivate previous plans
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        llm_service = LLMService()
        user_profile_dict = {
            "weight_kg": user.weight_kg,
            "height_cm": user.height_cm,
            "body_type": user.body_type,
            "fitness_goals": user.fitness_goals
        }
        
        # Get recent workout history for adaptive planning (Requirement 7.5)
        recent_workouts = await self.get_workout_history(user_id, limit=5)
        workout_history_summary = []
        for w in recent_workouts:
             if w.start_time: # Ensure start_time exists
                score = w.average_form_score if w.average_form_score is not None else 0
                workout_history_summary.append(
                    f"{w.start_time.date()}: {w.total_reps} reps, form score {score:.1f}"
                )

        plan_data = await llm_service.generate_workout_plan(user_profile_dict, workout_history_summary)
        
        # Deactivate previous plans
        await self.db.execute(
            text("UPDATE workout_plans SET is_active = FALSE WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        
        new_plan = WorkoutPlan(
            user_id=user_id,
            title=plan_data.get("title", "My Workout Plan"),
            plan_data=plan_data,
            is_active=True
        )
        
        self.db.add(new_plan)
        await self.db.commit()
        await self.db.refresh(new_plan)
        
        return WorkoutPlanResponse.model_validate(new_plan)

    async def get_active_plan(self, user_id: UUID) -> Optional[WorkoutPlanResponse]:
        """Retrieve the currently active workout plan for a user."""
        result = await self.db.execute(
            select(WorkoutPlan)
            .where(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active == True)
            .order_by(WorkoutPlan.created_at.desc())
        )
        plan = result.scalar_one_or_none()
        
        if not plan:
            return None
            
        return WorkoutPlanResponse.model_validate(plan)

    async def _update_streak(self, user_id: UUID, session_date: datetime):
        """Update user streak based on new workout session."""
        result = await self.db.execute(select(WorkoutStreak).where(WorkoutStreak.user_id == user_id))
        streak = result.scalar_one_or_none()

        if not streak:
            streak = WorkoutStreak(user_id=user_id, current_streak=1, longest_streak=1, last_workout_date=session_date)
            self.db.add(streak)
        else:
            if streak.last_workout_date:
                last_date = streak.last_workout_date.date()
                current_date = session_date.date()
                
                if current_date > last_date:
                    delta = (current_date - last_date).days
                    if delta == 1:
                        streak.current_streak += 1
                        if streak.current_streak > streak.longest_streak:
                            streak.longest_streak = streak.current_streak
                    elif delta > 1:
                        streak.current_streak = 1
                    
                    streak.last_workout_date = session_date
            else:
                streak.current_streak = 1
                streak.longest_streak = 1
                streak.last_workout_date = session_date
        
        await self.db.commit()

    async def get_user_statistics(self, user_id: UUID) -> UserStatistics:
        """Get aggregated user statistics."""
        # Get workout counts and totals
        result = await self.db.execute(
            select(
                text("COUNT(*)"), 
                text("COALESCE(SUM(total_reps), 0)"), 
                text("AVG(average_form_score)")
            ).select_from(WorkoutSession).where(WorkoutSession.user_id == user_id)
        )
        total_workouts, total_reps, avg_form_score = result.one()
        
        # Get streak info
        streak_result = await self.db.execute(select(WorkoutStreak).where(WorkoutStreak.user_id == user_id))
        streak = streak_result.scalar_one_or_none()
        
        return UserStatistics(
            total_workouts=total_workouts,
            total_reps=int(total_reps),
            average_form_score=float(avg_form_score) if avg_form_score is not None else 0.0,
            current_streak=streak.current_streak if streak else 0,
            longest_streak=streak.longest_streak if streak else 0,
            last_workout_date=streak.last_workout_date if streak else None
        )

    async def get_notification_preferences(self, user_id: UUID) -> NotificationPreferencesResponse:
        """Get user notification preferences."""
        result = await self.db.execute(select(NotificationPreferences).where(NotificationPreferences.user_id == user_id))
        prefs = result.scalar_one_or_none()
        
        if not prefs:
            prefs = NotificationPreferences(user_id=user_id)
            self.db.add(prefs)
            await self.db.commit()
            await self.db.refresh(prefs)
            
        return NotificationPreferencesResponse.model_validate(prefs)

    async def update_notification_preferences(self, user_id: UUID, updates: NotificationPreferencesUpdate) -> NotificationPreferencesResponse:
        """Update user notification preferences."""
        result = await self.db.execute(select(NotificationPreferences).where(NotificationPreferences.user_id == user_id))
        prefs = result.scalar_one_or_none()
        
        if not prefs:
            prefs = NotificationPreferences(user_id=user_id)
            self.db.add(prefs)
        
        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(prefs, field, value)
            
        await self.db.commit()
        await self.db.refresh(prefs)
        
        return NotificationPreferencesResponse.model_validate(prefs)
            
        return WorkoutPlanResponse.model_validate(plan)
