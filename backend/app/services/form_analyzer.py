"""Form analysis service for detecting exercise mistakes."""

from typing import List
from app.models.exercise import ExerciseType, FormMistake, FormRule
from app.models.pose import PoseData
from app.services.exercise_registry import ExerciseRegistry
from app.utils.biomechanics import (
    calculate_angle,
    calculate_hip_shoulder_alignment,
    calculate_knee_alignment,
    calculate_neck_angle,
    calculate_torso_angle,
    calculate_elbow_angle_from_torso,
    calculate_ankle_angle,
    calculate_shoulder_angle,
    calculate_hip_angle,
)


class FormAnalyzer:
    """Analyzes exercise form and detects common mistakes."""

    def __init__(self, exercise_registry: ExerciseRegistry):
        """
        Initialize the form analyzer.

        Args:
            exercise_registry: Registry containing exercise definitions and form rules
        """
        self.exercise_registry = exercise_registry

    def analyze(
        self, pose_data: PoseData, exercise_type: ExerciseType
    ) -> List[FormMistake]:
        """
        Detect form mistakes in current pose.

        Args:
            pose_data: Current pose keypoints
            exercise_type: Type of exercise being performed

        Returns:
            List of detected form mistakes with severity and suggestions
        """
        if exercise_type == ExerciseType.UNKNOWN:
            return []

        # Get exercise definition
        exercise_def = self.exercise_registry.get_exercise(exercise_type)
        if not exercise_def:
            return []

        mistakes = []

        # Check each form rule for the exercise
        for rule in exercise_def.form_rules:
            mistake = self._check_form_rule(pose_data, rule, exercise_type)
            if mistake:
                mistakes.append(mistake)

        return mistakes

    def _check_form_rule(
        self, pose_data: PoseData, rule: FormRule, exercise_type: ExerciseType
    ) -> FormMistake | None:
        """
        Check a specific form rule against pose data.

        Args:
            pose_data: Current pose keypoints
            rule: Form rule to check
            exercise_type: Type of exercise being performed

        Returns:
            FormMistake if rule is violated, None otherwise
        """
        # Convert keypoints to dict for easier access
        keypoints_dict = {kp.name: kp for kp in pose_data.keypoints}

        # Check visibility of required keypoints
        required_keypoints = self._get_required_keypoints(rule, exercise_type)
        if not all(
            keypoints_dict.get(kp) and keypoints_dict[kp].visibility > 0.5
            for kp in required_keypoints
        ):
            return None

        # Apply rule-specific logic based on rule_id
        if rule.rule_id == "pushup_hip_sag":
            return self._check_hip_sag(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "pushup_hip_pike":
            return self._check_hip_pike(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "pushup_elbow_flare":
            return self._check_elbow_flare(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "pushup_partial_range":
            return self._check_partial_range_pushup(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "pushup_head_drop":
            return self._check_head_drop(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "squat_knee_cave":
            return self._check_knee_cave(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "squat_shallow_depth":
            return self._check_shallow_depth(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "squat_forward_lean":
            return self._check_forward_lean(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "squat_heel_lift":
            return self._check_heel_lift(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "squat_knee_over_toe":
            return self._check_knee_over_toe(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "plank_hip_sag":
            return self._check_hip_sag(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "plank_hip_pike":
            return self._check_hip_pike(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "plank_shoulder_collapse":
            return self._check_shoulder_collapse(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "jumping_jack_incomplete_arms":
            return self._check_incomplete_arms(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "jumping_jack_incomplete_legs":
            return self._check_incomplete_legs(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "neck_speed":
            return self._check_neck_speed(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "neck_torso_movement":
            return self._check_torso_sway(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "hand_rotation_small_range":
            return self._check_rotation_range(pose_data, rule, keypoints_dict)
        elif rule.rule_id == "hand_rotation_stiff_elbow":
            return self._check_stiff_elbow(pose_data, rule, keypoints_dict)

        return None

    def _get_required_keypoints(
        self, rule: FormRule, exercise_type: ExerciseType
    ) -> List[str]:
        """Get list of required keypoints for a form rule."""
        # Map of rule types to required keypoints
        keypoint_map = {
            "hip": ["left_hip", "right_hip", "left_shoulder", "right_shoulder"],
            "elbow": ["left_elbow", "right_elbow", "left_shoulder", "right_shoulder", "left_wrist", "right_wrist"],
            "knee": ["left_knee", "right_knee", "left_hip", "right_hip", "left_ankle", "right_ankle"],
            "neck": ["nose", "left_shoulder", "right_shoulder"],
            "torso": ["left_shoulder", "right_shoulder", "left_hip", "right_hip"],
            "ankle": ["left_ankle", "right_ankle", "left_knee", "right_knee"],
            "shoulder": ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow"],
        }

        required = set()
        for joint in rule.joint_angles:
            required.update(keypoint_map.get(joint, []))

        return list(required)

    # Push-up form checks
    def _check_hip_sag(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for hip sagging below shoulder line."""
        deviation = calculate_hip_shoulder_alignment(pose_data)
        if deviation > rule.threshold:
            severity = min(1.0, (deviation / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_hip_pike(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for hip raised above shoulder line."""
        deviation = calculate_hip_shoulder_alignment(pose_data)
        if deviation < -rule.threshold:
            severity = min(1.0, (abs(deviation) / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_elbow_flare(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for elbows flaring beyond threshold."""
        elbow_angle = calculate_elbow_angle_from_torso(pose_data)
        if elbow_angle and elbow_angle > rule.threshold:
            severity = min(1.0, (elbow_angle / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_partial_range_pushup(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for partial range of motion in push-ups."""
        # This check is typically done in the rep counter, but we can detect it here too
        # by checking if elbow angle is in the middle range (not fully extended or flexed)
        left_elbow_angle = calculate_angle(
            keypoints_dict["left_shoulder"],
            keypoints_dict["left_elbow"],
            keypoints_dict["left_wrist"],
        )
        right_elbow_angle = calculate_angle(
            keypoints_dict["right_shoulder"],
            keypoints_dict["right_elbow"],
            keypoints_dict["right_wrist"],
        )
        
        if left_elbow_angle and right_elbow_angle:
            avg_angle = (left_elbow_angle + right_elbow_angle) / 2
            # If angle is in middle range (100-160), might be partial range
            if rule.threshold < avg_angle < 160:
                severity = min(1.0, ((160 - avg_angle) / 60) * rule.severity_multiplier)
                return FormMistake(
                    mistake_type=rule.rule_id,
                    severity=severity,
                    suggestion=rule.suggestion,
                )
        return None

    def _check_head_drop(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for head dropping (neck angle deviation)."""
        neck_angle = calculate_neck_angle(pose_data)
        if neck_angle and abs(neck_angle) > rule.threshold:
            severity = min(1.0, (abs(neck_angle) / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    # Squat form checks
    def _check_knee_cave(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for knees caving inward."""
        knee_alignment = calculate_knee_alignment(pose_data)
        if knee_alignment and knee_alignment < -rule.threshold:
            severity = min(1.0, (abs(knee_alignment) / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_shallow_depth(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for shallow squat depth."""
        # Calculate knee angle
        left_knee_angle = calculate_angle(
            keypoints_dict["left_hip"],
            keypoints_dict["left_knee"],
            keypoints_dict["left_ankle"],
        )
        right_knee_angle = calculate_angle(
            keypoints_dict["right_hip"],
            keypoints_dict["right_knee"],
            keypoints_dict["right_ankle"],
        )
        
        if left_knee_angle and right_knee_angle:
            avg_angle = (left_knee_angle + right_knee_angle) / 2
            # If angle is above threshold, squat is too shallow
            if avg_angle > rule.threshold:
                severity = min(1.0, ((avg_angle - rule.threshold) / 80) * rule.severity_multiplier)
                return FormMistake(
                    mistake_type=rule.rule_id,
                    severity=severity,
                    suggestion=rule.suggestion,
                )
        return None

    def _check_forward_lean(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for excessive forward torso lean."""
        torso_angle = calculate_torso_angle(pose_data)
        if torso_angle and torso_angle < rule.threshold:
            severity = min(1.0, ((rule.threshold - torso_angle) / rule.threshold) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_heel_lift(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for heels lifting off ground."""
        ankle_angle = calculate_ankle_angle(pose_data)
        if ankle_angle and abs(ankle_angle) > rule.threshold:
            severity = min(1.0, (abs(ankle_angle) / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_knee_over_toe(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for knees shooting too far forward."""
        # Calculate horizontal distance between knee and ankle
        left_knee = keypoints_dict.get("left_knee")
        left_ankle = keypoints_dict.get("left_ankle")
        right_knee = keypoints_dict.get("right_knee")
        right_ankle = keypoints_dict.get("right_ankle")
        
        if left_knee and left_ankle and right_knee and right_ankle:
            left_distance = abs(left_knee.x - left_ankle.x)
            right_distance = abs(right_knee.x - right_ankle.x)
            avg_distance = (left_distance + right_distance) / 2
            
            # Normalize threshold (assuming normalized coordinates 0-1)
            normalized_threshold = rule.threshold / 100  # Convert cm to normalized units
            
            if avg_distance > normalized_threshold:
                severity = min(1.0, (avg_distance / normalized_threshold - 1.0) * rule.severity_multiplier)
                return FormMistake(
                    mistake_type=rule.rule_id,
                    severity=severity,
                    suggestion=rule.suggestion,
                )
        return None

    # Plank form checks
    def _check_shoulder_collapse(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for shoulder collapse in plank."""
        # Calculate shoulder height relative to elbow
        left_shoulder = keypoints_dict.get("left_shoulder")
        right_shoulder = keypoints_dict.get("right_shoulder")
        left_elbow = keypoints_dict.get("left_elbow")
        right_elbow = keypoints_dict.get("right_elbow")
        
        if left_shoulder and right_shoulder and left_elbow and right_elbow:
            shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
            elbow_y = (left_elbow.y + right_elbow.y) / 2
            
            # If shoulders drop significantly below elbows (in normalized coords)
            drop = (shoulder_y - elbow_y) * 100  # Convert to approximate cm
            
            if drop > rule.threshold:
                severity = min(1.0, (drop / rule.threshold - 1.0) * rule.severity_multiplier)
                return FormMistake(
                    mistake_type=rule.rule_id,
                    severity=severity,
                    suggestion=rule.suggestion,
                )
        return None

    # Jumping jack form checks
    def _check_incomplete_arms(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for incomplete arm raise in jumping jacks."""
        shoulder_angle = calculate_shoulder_angle(pose_data)
        if shoulder_angle and shoulder_angle < rule.threshold:
            severity = min(1.0, ((rule.threshold - shoulder_angle) / rule.threshold) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_incomplete_legs(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for incomplete leg spread in jumping jacks."""
        hip_angle = calculate_hip_angle(pose_data)
        if hip_angle and hip_angle < rule.threshold:
            severity = min(1.0, ((rule.threshold - hip_angle) / rule.threshold) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_neck_speed(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check if neck is rotating too fast (simulated for now)."""
        # In a real implementation, we'd compare consecutive frames
        # For now, we'll use a placeholder logic that checks for extreme visibility variance
        return None

    def _check_torso_sway(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for excessive torso swaying."""
        torso_angle = calculate_torso_angle(pose_data)
        if torso_angle and abs(90 - torso_angle) > rule.threshold:
            severity = min(1.0, (abs(90 - torso_angle) / rule.threshold - 1.0) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_rotation_range(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for small arm rotation range."""
        shoulder_angle = calculate_shoulder_angle(pose_data)
        if shoulder_angle and shoulder_angle < rule.threshold:
            severity = min(1.0, ((rule.threshold - shoulder_angle) / rule.threshold) * rule.severity_multiplier)
            return FormMistake(
                mistake_type=rule.rule_id,
                severity=severity,
                suggestion=rule.suggestion,
            )
        return None

    def _check_stiff_elbow(self, pose_data: PoseData, rule: FormRule, keypoints_dict: dict) -> FormMistake | None:
        """Check for stiff elbows during rotations."""
        left_elbow = calculate_angle(keypoints_dict["left_shoulder"], keypoints_dict["left_elbow"], keypoints_dict["left_wrist"])
        right_elbow = calculate_angle(keypoints_dict["right_shoulder"], keypoints_dict["right_elbow"], keypoints_dict["right_wrist"])
        
        if left_elbow and right_elbow:
            avg_elbow = (left_elbow + right_elbow) / 2
            if avg_elbow > rule.threshold:
                severity = min(1.0, ((avg_elbow - rule.threshold) / 20) * rule.severity_multiplier)
                return FormMistake(
                    mistake_type=rule.rule_id,
                    severity=severity,
                    suggestion=rule.suggestion,
                )
        return None

    def calculate_form_score(self, mistakes: List[FormMistake]) -> float:
        """
        Calculate overall form score based on detected mistakes.

        Scoring:
        - Base score: 100
        - Minor mistakes (severity 0-0.3): -5 points
        - Moderate mistakes (severity 0.3-0.7): -10 points
        - Severe mistakes (severity 0.7-1.0): -20 points

        Args:
            mistakes: List of detected form mistakes

        Returns:
            Form score from 0-100
        """
        base_score = 100.0
        deductions = 0.0

        for mistake in mistakes:
            if mistake.severity < 0.3:
                deductions += 5.0
            elif mistake.severity < 0.7:
                deductions += 10.0
            else:
                deductions += 20.0

        final_score = max(0.0, base_score - deductions)
        return final_score
