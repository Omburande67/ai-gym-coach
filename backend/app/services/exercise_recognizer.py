"""Exercise recognition service using rule-based pattern matching.

This module implements exercise recognition by analyzing pose keypoints
and matching them against predefined exercise patterns.
"""

from collections import deque
from typing import Dict, List, Optional, Tuple
import time

from app.models.exercise import ExerciseType, ExerciseDefinition
from app.models.pose import PoseData
from app.services.exercise_registry import exercise_registry
from app.utils.biomechanics import calculate_joint_angles, get_average_angle


class ExerciseRecognizer:
    """
    Rule-based exercise recognizer using biomechanical pattern matching.
    
    Implements Requirements 2.1, 2.3, 2.6:
    - Identifies exercise type within 3 seconds
    - Supports pushup, squat, plank, jumping_jack
    - Uses rule-based joint angle analysis
    """
    
    def __init__(self, window_size_seconds: float = 2.5, confidence_threshold: float = 0.8):
        """
        Initialize the exercise recognizer.
        
        Args:
            window_size_seconds: Size of sliding window for pattern detection
            confidence_threshold: Minimum confidence required for classification
        """
        self.window_size_seconds = window_size_seconds
        self.confidence_threshold = confidence_threshold
        
        # Sliding window of recent pose data
        self.pose_history: deque = deque(maxlen=100)  # Store last 100 poses
        
        # Current recognition state
        self.current_exercise: ExerciseType = ExerciseType.UNKNOWN
        self.current_confidence: float = 0.0
        self.last_recognition_time: float = 0.0
    
    def recognize(self, pose_data: PoseData) -> Tuple[ExerciseType, float]:
        """
        Recognize exercise type from pose data.
        
        Args:
            pose_data: Current pose keypoints
            
        Returns:
            Tuple of (exercise_type, confidence_score)
        """
        # Add pose to history
        self.pose_history.append(pose_data)
        
        # Remove old poses outside the window
        current_time = pose_data.timestamp / 1000  # Convert ms to seconds
        cutoff_time = current_time - self.window_size_seconds
        
        while self.pose_history and self.pose_history[0].timestamp / 1000 < cutoff_time:
            self.pose_history.popleft()
        
        # Need at least 10 poses for reliable recognition
        if len(self.pose_history) < 10:
            return ExerciseType.UNKNOWN, 0.0
        
        # Calculate confidence scores for each exercise type
        scores: Dict[ExerciseType, float] = {}
        
        for exercise_type in [ExerciseType.PUSHUP, ExerciseType.SQUAT, 
                              ExerciseType.PLANK, ExerciseType.JUMPING_JACK,
                              ExerciseType.NECK_ROTATION, ExerciseType.HAND_ROTATION]:
            exercise_def = exercise_registry.get_exercise(exercise_type)
            if exercise_def:
                scores[exercise_type] = self._calculate_match_score(exercise_def)
        
        # Find exercise with highest score
        if scores:
            best_exercise = max(scores, key=scores.get)
            best_score = scores[best_exercise]
            
            # Update current exercise if confidence threshold is met
            if best_score >= self.confidence_threshold:
                self.current_exercise = best_exercise
                self.current_confidence = best_score
                self.last_recognition_time = current_time
            else:
                # Low confidence - return unknown
                self.current_exercise = ExerciseType.UNKNOWN
                self.current_confidence = best_score
            
            return self.current_exercise, self.current_confidence
        
        return ExerciseType.UNKNOWN, 0.0
    
    def _calculate_match_score(self, exercise_def: ExerciseDefinition) -> float:
        """
        Calculate how well the pose history matches an exercise definition.
        
        Args:
            exercise_def: Exercise definition to match against
            
        Returns:
            Confidence score (0-1)
        """
        pattern = exercise_def.recognition_pattern
        scores: List[float] = []
        
        for pose_data in self.pose_history:
            angles = calculate_joint_angles(pose_data)
            pose_score = 0.0
            checks = 0
            
            # Check body orientation (torso angle)
            if angles['torso'] is not None:
                checks += 1
                if pattern.torso_angle_min <= angles['torso'] <= pattern.torso_angle_max:
                    pose_score += 1.0
            
            # Check primary joint oscillation
            primary_angle = self._get_primary_joint_angle(angles, pattern.primary_joint)
            if primary_angle is not None:
                checks += 1
                # For now, just check if angle is valid (not None)
                # Oscillation check requires multiple frames
                pose_score += 0.5
            
            # Calculate average score for this pose
            if checks > 0:
                scores.append(pose_score / checks)
        
        # Check oscillation over the window if required
        if pattern.oscillation_required and len(self.pose_history) >= 10:
            oscillation_score = self._check_oscillation(pattern.primary_joint, 
                                                        pattern.min_oscillation_range)
            scores.append(oscillation_score)
        
        # Return average score across all poses
        return sum(scores) / len(scores) if scores else 0.0
    
    def _get_primary_joint_angle(self, angles: Dict[str, Optional[float]], 
                                  joint_name: str) -> Optional[float]:
        """
        Get the angle for the primary joint (averaging left/right if applicable).
        
        Args:
            angles: Dictionary of joint angles
            joint_name: Name of the joint (e.g., 'elbow', 'knee')
            
        Returns:
            Average angle or None
        """
        left_key = f'left_{joint_name}'
        right_key = f'right_{joint_name}'
        
        if left_key in angles and right_key in angles:
            return get_average_angle(angles[left_key], angles[right_key])
        elif joint_name in angles:
            return angles[joint_name]
        
        return None
    
    def _check_oscillation(self, joint_name: str, min_range: float) -> float:
        """
        Check if the primary joint is oscillating with sufficient range.
        
        Args:
            joint_name: Name of the joint to check
            min_range: Minimum oscillation range in degrees
            
        Returns:
            Score (0-1) indicating oscillation quality
        """
        angles: List[float] = []
        
        for pose_data in self.pose_history:
            joint_angles = calculate_joint_angles(pose_data)
            angle = self._get_primary_joint_angle(joint_angles, joint_name)
            if angle is not None:
                angles.append(angle)
        
        if len(angles) < 5:
            return 0.0
        
        # Calculate range of motion
        angle_range = max(angles) - min(angles)
        
        # Score based on whether range meets minimum
        if angle_range >= min_range:
            return 1.0
        else:
            return angle_range / min_range
    
    def get_confidence(self) -> float:
        """
        Get current confidence score.
        
        Returns:
            Confidence score (0-1)
        """
        return self.current_confidence
    
    def reset(self) -> None:
        """Reset the recognizer state."""
        self.pose_history.clear()
        self.current_exercise = ExerciseType.UNKNOWN
        self.current_confidence = 0.0
        self.last_recognition_time = 0.0
