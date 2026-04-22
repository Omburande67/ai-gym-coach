"""Workout session and exercise record database models"""

from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid

from sqlalchemy import DECIMAL, ForeignKey, Integer, String, JSON, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # ✅ FIXED (timezone=True)
    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    end_time: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    total_duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    total_reps: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    average_form_score: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2), nullable=True
    )

    # ✅ FIXED
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    exercise_records: Mapped[list["ExerciseRecord"]] = relationship(
        "ExerciseRecord",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class ExerciseRecord(Base):
    __tablename__ = "exercise_records"

    record_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )

    exercise_type: Mapped[str] = mapped_column(String(50), nullable=False)

    reps_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    form_score: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2), nullable=True
    )

    mistakes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # ✅ FIXED
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    session: Mapped["WorkoutSession"] = relationship(
        "WorkoutSession",
        back_populates="exercise_records"
    )


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    plan_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )