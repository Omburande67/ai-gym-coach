"""User schemas for request/response validation"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr
    weight_kg: Optional[float] = Field(None, gt=0, description="Weight in kilograms")
    height_cm: Optional[float] = Field(None, gt=0, description="Height in centimeters")
    body_type: Optional[str] = Field(
        None, description="Body type: ectomorph, mesomorph, or endomorph"
    )
    fitness_goals: Optional[List[str]] = Field(
        None, description="List of fitness goals"
    )

    @field_validator("body_type")
    @classmethod
    def validate_body_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate body type is one of the allowed values"""
        if v is not None and v not in ["ectomorph", "mesomorph", "endomorph"]:
            raise ValueError(
                "body_type must be one of: ectomorph, mesomorph, endomorph"
            )
        return v


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(..., min_length=8, description="User password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password meets security requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates"""

    weight_kg: Optional[float] = Field(None, gt=0, description="Weight in kilograms")
    height_cm: Optional[float] = Field(None, gt=0, description="Height in centimeters")
    body_type: Optional[str] = Field(
        None, description="Body type: ectomorph, mesomorph, or endomorph"
    )
    fitness_goals: Optional[List[str]] = Field(
        None, description="List of fitness goals"
    )

    @field_validator("body_type")
    @classmethod
    def validate_body_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate body type is one of the allowed values"""
        if v is not None and v not in ["ectomorph", "mesomorph", "endomorph"]:
            raise ValueError(
                "body_type must be one of: ectomorph, mesomorph, endomorph"
            )
        return v


class UserProfile(UserBase):
    """Schema for user profile response"""

    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload"""

    user_id: Optional[UUID] = None
    email: Optional[str] = None


class NotificationPreferencesBase(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    workout_residues: bool = True
    daily_reminder_time: Optional[str] = None # HH:MM

class NotificationPreferencesUpdate(NotificationPreferencesBase):
    pass

class NotificationPreferencesResponse(NotificationPreferencesBase):
    user_id: UUID
    updated_at: datetime
    model_config = {"from_attributes": True}


class WorkoutStreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_workout_date: Optional[datetime]
    updated_at: datetime
    model_config = {"from_attributes": True}

class UserStatistics(BaseModel):
    total_workouts: int
    total_reps: int
    average_form_score: float
    current_streak: int
    longest_streak: int
    last_workout_date: Optional[datetime]
