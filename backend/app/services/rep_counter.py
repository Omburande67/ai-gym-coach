"""Repetition counting service using state machine logic.

This module implements rep counting by tracking biomechanical state transitions
for different exercise types.
"""

from enum import Enum
from typing import Optional
from app.models.exercise import ExerciseType
from app.models.pose import PoseData
from app.utils.biomechanics import calculate_joint_angles, get_average_angle


class RepPhase(Enum):
    """Exercise phase states for rep counting."""
    UP = "up"
    DOWN = "down"
    TRANSITION = "transition"


class RepCounter:
    """
    State machine-based repetition counter.
    
    Implements Requirements 3.1, 3.2:
    - Counts reps using biomechanical state transitions
    - Tracks current phase (UP, DOWN, TRANSITION)
    """
    
    def __init__(self, exercise_type: ExerciseType):
        """
        Initialize the rep counter for a specific exercise.
        
        Args:
            exercise_type: Type of exercise to count reps for
        """
        self.exercise_type = exercise_type
        self.count = 0
        
        # Set initial phase based on exercise type
        # Jumping jacks start with arms down, others start in UP position
        if exercise_type == ExerciseType.JUMPING_JACK:
            self.current_phase = RepPhase.DOWN
        else:
            self.current_phase = RepPhase.UP
            
        self.last_transition_time = 0.0
        
        # Hysteresis buffer to prevent double-counting (degrees)
        self.hysteresis_buffer = 10
        
        # Minimum time between reps (seconds)
        self.min_rep_duration = 0.5
        
        # Track duration for plank
        self.start_time: Optional[float] = None
        self.duration_seconds = 0.0
    
    def update(self, pose_data: PoseData) -> Optional[int]:
        """
        Update state machine with new pose data.
        
        Args:
            pose_data: Current pose keypoints
            
        Returns:
            New rep count if rep completed, else None
        """
        current_time = pose_data.timestamp / 1000  # Convert ms to seconds
        
        # Calculate joint angles
        angles = calculate_joint_angles(pose_data)
        
        # Handle plank (duration-based, not rep-based)
        if self.exercise_type == ExerciseType.PLANK:
            return self._update_plank_duration(current_time)
        
        # Get primary joint angle for this exercise
        primary_angle = self._get_primary_angle(angles)
        
        if primary_angle is None:
            return None
        
        # Check for state transitions
        new_phase = self._check_transition(primary_angle, current_time)
        
        if new_phase != self.current_phase:
            self.current_phase = new_phase
            
            # Rep completed based on exercise type
            # For jumping jacks: count when returning to DOWN (arms at sides)
            # For others: count when returning to UP (extended position)
            rep_completed = False
            
            if self.exercise_type == ExerciseType.JUMPING_JACK:
                # Jumping jack: DOWN → UP → DOWN = 1 rep
                if new_phase == RepPhase.DOWN and current_time - self.last_transition_time >= self.min_rep_duration:
                    rep_completed = True
            else:
                # Push-up, squat: UP → DOWN → UP = 1 rep
                if new_phase == RepPhase.UP and current_time - self.last_transition_time >= self.min_rep_duration:
                    rep_completed = True
            
            if rep_completed:
                self.count += 1
                self.last_transition_time = current_time
                return self.count
        
        return None
    
    def _get_primary_angle(self, angles: dict) -> Optional[float]:
        """
        Get the primary joint angle for the current exercise.
        
        Args:
            angles: Dictionary of joint angles
            
        Returns:
            Primary angle or None
        """
        if self.exercise_type == ExerciseType.PUSHUP:
            # Use elbow angle (average of left and right)
            return get_average_angle(angles.get('left_elbow'), angles.get('right_elbow'))
        
        elif self.exercise_type == ExerciseType.SQUAT:
            # Use knee angle (average of left and right)
            return get_average_angle(angles.get('left_knee'), angles.get('right_knee'))
        
        elif self.exercise_type == ExerciseType.JUMPING_JACK:
            # Use shoulder angle (average of left and right)
            return get_average_angle(angles.get('left_shoulder'), angles.get('right_shoulder'))
        
        return None
    
    def _check_transition(self, angle: float, current_time: float) -> RepPhase:
        """
        Check if angle indicates a phase transition.
        
        Args:
            angle: Current joint angle
            current_time: Current timestamp in seconds
            
        Returns:
            New phase
        """
        if self.exercise_type == ExerciseType.PUSHUP:
            return self._check_pushup_transition(angle)
        
        elif self.exercise_type == ExerciseType.SQUAT:
            return self._check_squat_transition(angle)
        
        elif self.exercise_type == ExerciseType.JUMPING_JACK:
            return self._check_jumping_jack_transition(angle)
        
        return self.current_phase
    
    def _check_pushup_transition(self, elbow_angle: float) -> RepPhase:
        """
        Check push-up phase transition.
        
        UP: elbow > 160°
        DOWN: elbow < 90°
        
        Args:
            elbow_angle: Current elbow angle
            
        Returns:
            New phase
        """
        if self.current_phase == RepPhase.UP:
            # Transition to DOWN when elbow bends significantly
            if elbow_angle < 90 + self.hysteresis_buffer:
                return RepPhase.DOWN
        
        elif self.current_phase == RepPhase.DOWN:
            # Transition back to UP when elbow extends
            if elbow_angle > 160 - self.hysteresis_buffer:
                return RepPhase.UP
        
        return self.current_phase
    
    def _check_squat_transition(self, knee_angle: float) -> RepPhase:
        """
        Check squat phase transition.
        
        UP: knee > 160°
        DOWN: knee < 90°
        
        Args:
            knee_angle: Current knee angle
            
        Returns:
            New phase
        """
        if self.current_phase == RepPhase.UP:
            # Transition to DOWN when knee bends significantly
            if knee_angle < 90 + self.hysteresis_buffer:
                return RepPhase.DOWN
        
        elif self.current_phase == RepPhase.DOWN:
            # Transition back to UP when knee extends
            if knee_angle > 160 - self.hysteresis_buffer:
                return RepPhase.UP
        
        return self.current_phase
    
    def _check_jumping_jack_transition(self, shoulder_angle: float) -> RepPhase:
        """
        Check jumping jack phase transition.
        
        DOWN: arms at sides (shoulder angle < 30°)
        UP: arms overhead (shoulder angle > 160°)
        
        Args:
            shoulder_angle: Current shoulder angle
            
        Returns:
            New phase
        """
        if self.current_phase == RepPhase.DOWN:
            # Transition to UP when arms go overhead
            if shoulder_angle > 160 - self.hysteresis_buffer:
                return RepPhase.UP
        
        elif self.current_phase == RepPhase.UP:
            # Transition back to DOWN when arms come down
            if shoulder_angle < 30 + self.hysteresis_buffer:
                return RepPhase.DOWN
        
        return self.current_phase
    
    def _update_plank_duration(self, current_time: float) -> Optional[int]:
        """
        Update plank duration (not rep-based).
        
        Args:
            current_time: Current timestamp in seconds
            
        Returns:
            None (plank doesn't count reps)
        """
        if self.start_time is None:
            self.start_time = current_time
        
        self.duration_seconds = current_time - self.start_time
        return None
    
    def get_count(self) -> int:
        """
        Get current rep count.
        
        Returns:
            Current rep count
        """
        return self.count
    
    def get_duration(self) -> float:
        """
        Get duration for duration-based exercises (plank).
        
        Returns:
            Duration in seconds
        """
        return self.duration_seconds
    
    def reset(self) -> None:
        """Reset counter to initial state."""
        self.count = 0
        
        # Reset to appropriate starting phase
        if self.exercise_type == ExerciseType.JUMPING_JACK:
            self.current_phase = RepPhase.DOWN
        else:
            self.current_phase = RepPhase.UP
            
        self.last_transition_time = 0.0
        self.start_time = None
        self.duration_seconds = 0.0
