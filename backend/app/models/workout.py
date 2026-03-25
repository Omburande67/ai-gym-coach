"""Workout session and exercise record database models"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DECIMAL, ForeignKey, Integer, TIMESTAMP, String, text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.user import Base


class WorkoutSession(Base):
    """WorkoutSession model representing the workout_sessions table"""

    __tablename__ = "workout_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    total_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_form_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationship to exercise records
    exercise_records: Mapped[list["ExerciseRecord"]] = relationship(
        "ExerciseRecord", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkoutSession(session_id={self.session_id}, user_id={self.user_id})>"


class ExerciseRecord(Base):
    """ExerciseRecord model representing the exercise_records table"""

    __tablename__ = "exercise_records"

    record_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reps_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    form_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    mistakes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationship to workout session
    session: Mapped["WorkoutSession"] = relationship("WorkoutSession", back_populates="exercise_records")

    def __repr__(self) -> str:
        return f"<ExerciseRecord(record_id={self.record_id}, exercise_type={self.exercise_type})>"


class WorkoutPlan(Base):
    """WorkoutPlan model representing the workout_plans table"""

    __tablename__ = "workout_plans"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    plan_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<WorkoutPlan(plan_id={self.plan_id}, user_id={self.user_id}, title={self.title})>"
