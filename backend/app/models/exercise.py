"""Exercise models and enums for the AI Gym Coach system."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ExerciseType(str, Enum):
    """Supported exercise types."""
    PUSHUP = "pushup"
    SQUAT = "squat"
    PLANK = "plank"
    JUMPING_JACK = "jumping_jack"
    UNKNOWN = "unknown"


class RepPhase(str, Enum):
    """Phases of a repetition for state machine tracking."""
    UP = "up"
    DOWN = "down"
    TRANSITION = "transition"


class AngleThreshold(BaseModel):
    """Angle thresholds for exercise recognition and rep counting."""
    up_min: float = Field(..., description="Minimum angle for UP phase (degrees)")
    up_max: float = Field(..., description="Maximum angle for UP phase (degrees)")
    down_min: float = Field(..., description="Minimum angle for DOWN phase (degrees)")
    down_max: float = Field(..., description="Maximum angle for DOWN phase (degrees)")
    hysteresis: float = Field(default=10.0, description="Buffer to prevent double-counting (degrees)")


class FormRule(BaseModel):
    """Form rule for detecting exercise mistakes."""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    description: str = Field(..., description="Human-readable description of the rule")
    joint_angles: List[str] = Field(..., description="Joint angles to monitor (e.g., 'hip', 'elbow')")
    threshold: float = Field(..., description="Deviation threshold to trigger mistake detection")
    severity_multiplier: float = Field(default=1.0, description="Multiplier for severity calculation")
    suggestion: str = Field(..., description="Corrective suggestion to display to user")


class RecognitionPattern(BaseModel):
    """Pattern for exercise recognition."""
    body_orientation: str = Field(..., description="Expected body orientation: 'horizontal' or 'vertical'")
    torso_angle_min: float = Field(..., description="Minimum torso angle from ground (degrees)")
    torso_angle_max: float = Field(..., description="Maximum torso angle from ground (degrees)")
    primary_joint: str = Field(..., description="Primary joint to monitor (e.g., 'elbow', 'knee')")
    oscillation_required: bool = Field(..., description="Whether joint angle must oscillate")
    min_oscillation_range: float = Field(default=0.0, description="Minimum oscillation range (degrees)")
    stationary_feet: bool = Field(default=False, description="Whether feet should remain stationary")


class ExerciseDefinition(BaseModel):
    """Complete definition for an exercise type."""
    exercise_type: ExerciseType = Field(..., description="Type of exercise")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Brief description of the exercise")
    
    # Recognition configuration
    recognition_pattern: RecognitionPattern = Field(..., description="Pattern for exercise recognition")
    
    # Rep counting configuration
    angle_thresholds: Optional[AngleThreshold] = Field(None, description="Angle thresholds for rep counting")
    is_duration_based: bool = Field(default=False, description="Whether exercise is duration-based (e.g., plank)")
    min_rep_duration_seconds: float = Field(default=0.5, description="Minimum time between reps to prevent double-counting")
    
    # Form analysis configuration
    form_rules: List[FormRule] = Field(default_factory=list, description="Form rules for mistake detection")
    
    # Camera placement guidance
    camera_distance_meters: float = Field(default=2.5, description="Recommended camera distance")
    camera_height: str = Field(default="waist", description="Recommended camera height")
    camera_angle: str = Field(default="side", description="Recommended camera angle")


class FormMistake(BaseModel):
    """Detected form mistake during exercise execution."""
    mistake_type: str = Field(..., description="Type of mistake (e.g., 'hip_sag', 'elbow_flare')")
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity score from 0 (minor) to 1 (severe)")
    suggestion: str = Field(..., description="Corrective suggestion for the user")


class ExerciseRegistry(BaseModel):
    """Registry of all supported exercises."""
    exercises: Dict[ExerciseType, ExerciseDefinition] = Field(..., description="Map of exercise type to definition")
    version: str = Field(default="1.0.0", description="Version of exercise definitions")
