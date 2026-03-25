"""Tests for form analyzer service."""

import pytest
from app.models.exercise import ExerciseType, FormMistake, ExerciseRegistry
from app.models.pose import PoseData, PoseKeypoint
from app.services.form_analyzer import FormAnalyzer
from app.services.exercise_registry import ExerciseRegistryService


@pytest.fixture
def exercise_registry():
    """Load exercise registry from config."""
    service = ExerciseRegistryService()
    return ExerciseRegistry(
        exercises=service.get_all_exercises(),
        version=service.get_version()
    )


@pytest.fixture
def form_analyzer(exercise_registry):
    """Create form analyzer instance."""
    return FormAnalyzer(exercise_registry)


def create_pose_data(keypoints_dict: dict, timestamp: float = 1234567890.0) -> PoseData:
    """Helper to create pose data from keypoint dictionary."""
    keypoints = []
    for name, (x, y, z, visibility) in keypoints_dict.items():
        keypoints.append(
            PoseKeypoint(x=x, y=y, z=z, visibility=visibility, name=name)
        )
    return PoseData(keypoints=keypoints, timestamp=timestamp)


class TestFormAnalyzer:
    """Test form analyzer functionality."""

    def test_analyze_returns_empty_for_unknown_exercise(self, form_analyzer):
        """Test that analyze returns empty list for unknown exercise."""
        pose_data = create_pose_data({
            "nose": (0.5, 0.3, 0.0, 0.9),
            "left_shoulder": (0.4, 0.4, 0.0, 0.9),
            "right_shoulder": (0.6, 0.4, 0.0, 0.9),
        })
        
        mistakes = form_analyzer.analyze(pose_data, ExerciseType.UNKNOWN)
        assert mistakes == []

    def test_analyze_pushup_hip_sag(self, form_analyzer):
        """Test detection of hip sag in push-ups."""
        # Create pose with hips sagging (hip y > shoulder y)
        pose_data = create_pose_data({
            "left_shoulder": (0.3, 0.4, 0.0, 0.9),
            "right_shoulder": (0.7, 0.4, 0.0, 0.9),
            "left_hip": (0.3, 0.6, 0.0, 0.9),  # Hips lower than shoulders
            "right_hip": (0.7, 0.6, 0.0, 0.9),
            "left_elbow": (0.25, 0.5, 0.0, 0.9),
            "right_elbow": (0.75, 0.5, 0.0, 0.9),
            "left_wrist": (0.2, 0.6, 0.0, 0.9),
            "right_wrist": (0.8, 0.6, 0.0, 0.9),
        })
        
        mistakes = form_analyzer.analyze(pose_data, ExerciseType.PUSHUP)
        
        # Should detect hip sag
        hip_sag_mistakes = [m for m in mistakes if "hip_sag" in m.mistake_type]
        assert len(hip_sag_mistakes) > 0
        assert hip_sag_mistakes[0].severity > 0
        assert "core" in hip_sag_mistakes[0].suggestion.lower()

    def test_analyze_squat_shallow_depth(self, form_analyzer):
        """Test detection of shallow squat depth."""
        # Create pose with shallow squat (knee angle > 100 degrees)
        pose_data = create_pose_data({
            "left_hip": (0.3, 0.3, 0.0, 0.9),
            "right_hip": (0.7, 0.3, 0.0, 0.9),
            "left_knee": (0.3, 0.5, 0.0, 0.9),
            "right_knee": (0.7, 0.5, 0.0, 0.9),
            "left_ankle": (0.3, 0.8, 0.0, 0.9),
            "right_ankle": (0.7, 0.8, 0.0, 0.9),
            "left_shoulder": (0.3, 0.2, 0.0, 0.9),
            "right_shoulder": (0.7, 0.2, 0.0, 0.9),
        })
        
        mistakes = form_analyzer.analyze(pose_data, ExerciseType.SQUAT)
        
        # Should detect shallow depth
        shallow_mistakes = [m for m in mistakes if "shallow" in m.mistake_type]
        assert len(shallow_mistakes) > 0
        assert "deeper" in shallow_mistakes[0].suggestion.lower()

    def test_analyze_plank_hip_pike(self, form_analyzer):
        """Test detection of hip pike in plank."""
        # Create pose with hips raised (hip y < shoulder y)
        pose_data = create_pose_data({
            "left_shoulder": (0.3, 0.5, 0.0, 0.9),
            "right_shoulder": (0.7, 0.5, 0.0, 0.9),
            "left_hip": (0.3, 0.3, 0.0, 0.9),  # Hips higher than shoulders
            "right_hip": (0.7, 0.3, 0.0, 0.9),
            "left_elbow": (0.25, 0.6, 0.0, 0.9),
            "right_elbow": (0.75, 0.6, 0.0, 0.9),
        })
        
        mistakes = form_analyzer.analyze(pose_data, ExerciseType.PLANK)
        
        # Should detect hip pike
        pike_mistakes = [m for m in mistakes if "pike" in m.mistake_type]
        assert len(pike_mistakes) > 0
        assert "lower" in pike_mistakes[0].suggestion.lower()

    def test_calculate_form_score_no_mistakes(self, form_analyzer):
        """Test form score calculation with no mistakes."""
        mistakes = []
        score = form_analyzer.calculate_form_score(mistakes)
        assert score == 100.0

    def test_calculate_form_score_minor_mistakes(self, form_analyzer):
        """Test form score calculation with minor mistakes."""
        mistakes = [
            FormMistake(mistake_type="test1", severity=0.2, suggestion="Fix it"),
            FormMistake(mistake_type="test2", severity=0.1, suggestion="Fix it"),
        ]
        score = form_analyzer.calculate_form_score(mistakes)
        assert score == 90.0  # 100 - 5 - 5

    def test_calculate_form_score_moderate_mistakes(self, form_analyzer):
        """Test form score calculation with moderate mistakes."""
        mistakes = [
            FormMistake(mistake_type="test1", severity=0.5, suggestion="Fix it"),
            FormMistake(mistake_type="test2", severity=0.6, suggestion="Fix it"),
        ]
        score = form_analyzer.calculate_form_score(mistakes)
        assert score == 80.0  # 100 - 10 - 10

    def test_calculate_form_score_severe_mistakes(self, form_analyzer):
        """Test form score calculation with severe mistakes."""
        mistakes = [
            FormMistake(mistake_type="test1", severity=0.8, suggestion="Fix it"),
            FormMistake(mistake_type="test2", severity=0.9, suggestion="Fix it"),
        ]
        score = form_analyzer.calculate_form_score(mistakes)
        assert score == 60.0  # 100 - 20 - 20

    def test_calculate_form_score_mixed_mistakes(self, form_analyzer):
        """Test form score calculation with mixed severity mistakes."""
        mistakes = [
            FormMistake(mistake_type="test1", severity=0.2, suggestion="Fix it"),  # -5
            FormMistake(mistake_type="test2", severity=0.5, suggestion="Fix it"),  # -10
            FormMistake(mistake_type="test3", severity=0.8, suggestion="Fix it"),  # -20
        ]
        score = form_analyzer.calculate_form_score(mistakes)
        assert score == 65.0  # 100 - 5 - 10 - 20

    def test_calculate_form_score_minimum_zero(self, form_analyzer):
        """Test that form score never goes below zero."""
        mistakes = [
            FormMistake(mistake_type=f"test{i}", severity=0.9, suggestion="Fix it")
            for i in range(10)  # 10 severe mistakes = -200 points
        ]
        score = form_analyzer.calculate_form_score(mistakes)
        assert score == 0.0  # Should be clamped to 0

    def test_analyze_with_low_visibility_keypoints(self, form_analyzer):
        """Test that low visibility keypoints are ignored."""
        # Create pose with low visibility keypoints
        pose_data = create_pose_data({
            "left_shoulder": (0.3, 0.4, 0.0, 0.2),  # Low visibility
            "right_shoulder": (0.7, 0.4, 0.0, 0.2),
            "left_hip": (0.3, 0.6, 0.0, 0.2),
            "right_hip": (0.7, 0.6, 0.0, 0.2),
        })
        
        mistakes = form_analyzer.analyze(pose_data, ExerciseType.PUSHUP)
        
        # Should not detect mistakes due to low visibility
        assert len(mistakes) == 0
