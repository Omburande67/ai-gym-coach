"""User database model"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DECIMAL, String, TIMESTAMP, Text, text, ForeignKey, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


class User(Base):
    """User model representing the users table"""

    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_kg: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    body_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fitness_goals: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"


class NotificationPreferences(Base):
    """Model for user notification preferences"""
    __tablename__ = "notification_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True
    )
    email_notifications: Mapped[bool] = mapped_column(default=True)
    push_notifications: Mapped[bool] = mapped_column(default=True)
    workout_residues: Mapped[bool] = mapped_column(default=True) # Reminder if missed workout
    daily_reminder_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True) # HH:MM format
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class WorkoutStreak(Base):
    """Model for tracking user workout streaks"""
    __tablename__ = "workout_streaks"

    streak_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True
    )
    current_streak: Mapped[int] = mapped_column(default=0)
    longest_streak: Mapped[int] = mapped_column(default=0)
    last_workout_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
