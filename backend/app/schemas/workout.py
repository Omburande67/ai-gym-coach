"""Workout session and exercise record schemas"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ExerciseRecordCreate(BaseModel):
    """Schema for creating an exercise record"""

    exercise_type: str = Field(..., description="Type of exercise performed")
    reps_completed: int = Field(default=0, description="Number of reps completed")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds for time-based exercises")
    form_score: Optional[float] = Field(None, ge=0, le=100, description="Form score 0-100")
    mistakes: Optional[dict] = Field(None, description="Form mistakes detected")


class ExerciseRecordResponse(BaseModel):
    """Schema for exercise record response"""

    record_id: UUID
    session_id: UUID
    exercise_type: str
    reps_completed: int
    duration_seconds: Optional[int]
    form_score: Optional[float]
    mistakes: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutSessionCreate(BaseModel):
    """Schema for creating a workout session"""

    user_id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    exercise_records: List[ExerciseRecordCreate] = Field(default_factory=list)


class WorkoutSessionUpdate(BaseModel):
    """Schema for updating a workout session"""

    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None
    total_reps: Optional[int] = None
    average_form_score: Optional[float] = None


class WorkoutSessionResponse(BaseModel):
    """Schema for workout session response"""

    session_id: UUID
    user_id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    total_duration_seconds: Optional[int]
    total_reps: int
    average_form_score: Optional[float]
    created_at: datetime
    exercise_records: List[ExerciseRecordResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class WorkoutSummary(BaseModel):
    """Schema for post-workout summary"""

    session_id: UUID
    total_reps: int = Field(..., description="Total repetitions across all exercises")
    total_duration_seconds: int = Field(..., description="Total workout duration")
    average_form_score: float = Field(..., ge=0, le=100, description="Average form score")
    top_mistakes: List[dict] = Field(..., description="Top 3 most frequent form mistakes")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    exercises: List[ExerciseRecordResponse] = Field(..., description="Exercise breakdown")


class WorkoutPlanCreate(BaseModel):
    """Schema for creating a workout plan"""
    title: str = Field(..., description="Plan title")
    plan_data: dict = Field(..., description="JSON data of the plan")


class WorkoutPlanResponse(BaseModel):
    """Schema for workout plan response"""
    plan_id: UUID
    user_id: UUID
    title: str
    plan_data: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
