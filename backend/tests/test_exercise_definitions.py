"""Unit tests for exercise definitions and registry."""

import pytest
from app.models.exercise import ExerciseType
from app.services.exercise_registry import ExerciseRegistryService


class TestExerciseRegistry:
    """Test suite for ExerciseRegistryService."""
    
    def test_singleton_pattern(self):
        """Test that ExerciseRegistryService follows singleton pattern."""
        registry1 = ExerciseRegistryService()
        registry2 = ExerciseRegistryService()
        assert registry1 is registry2
    
    def test_load_definitions(self):
        """Test that exercise definitions load successfully."""
        registry = ExerciseRegistryService()
        exercises = registry.get_all_exercises()
        
        assert exercises is not None
        assert len(exercises) > 0
    
    def test_get_pushup_definition(self):
        """Test retrieving push-up exercise definition."""
        registry = ExerciseRegistryService()
        pushup = registry.get_exercise(ExerciseType.PUSHUP)
        
        assert pushup is not None
        assert pushup.exercise_type == ExerciseType.PUSHUP
        assert pushup.display_name == "Push-up"
        assert pushup.is_duration_based is False
        assert pushup.angle_thresholds is not None
        assert pushup.angle_thresholds.up_min == 160
        assert pushup.angle_thresholds.down_max == 90
        assert len(pushup.form_rules) == 5
    
    def test_get_squat_definition(self):
        """Test retrieving squat exercise definition."""
        registry = ExerciseRegistryService()
        squat = registry.get_exercise(ExerciseType.SQUAT)
        
        assert squat is not None
        assert squat.exercise_type == ExerciseType.SQUAT
        assert squat.display_name == "Squat"
        assert squat.is_duration_based is False
        assert squat.angle_thresholds is not None
        assert len(squat.form_rules) == 5
    
    def test_get_plank_definition(self):
        """Test retrieving plank exercise definition."""
        registry = ExerciseRegistryService()
        plank = registry.get_exercise(ExerciseType.PLANK)
        
        assert plank is not None
        assert plank.exercise_type == ExerciseType.PLANK
        assert plank.display_name == "Plank"
        assert plank.is_duration_based is True
        assert plank.angle_thresholds is None  # Duration-based, no rep counting
        assert len(plank.form_rules) == 3
    
    def test_get_jumping_jack_definition(self):
        """Test retrieving jumping jack exercise definition."""
        registry = ExerciseRegistryService()
        jumping_jack = registry.get_exercise(ExerciseType.JUMPING_JACK)
        
        assert jumping_jack is not None
        assert jumping_jack.exercise_type == ExerciseType.JUMPING_JACK
        assert jumping_jack.display_name == "Jumping Jack"
        assert jumping_jack.is_duration_based is False
        assert jumping_jack.angle_thresholds is not None
        assert len(jumping_jack.form_rules) == 2
    
    def test_get_supported_exercise_types(self):
        """Test retrieving list of supported exercise types."""
        registry = ExerciseRegistryService()
        supported_types = registry.get_supported_exercise_types()
        
        assert ExerciseType.PUSHUP in supported_types
        assert ExerciseType.SQUAT in supported_types
        assert ExerciseType.PLANK in supported_types
        assert ExerciseType.JUMPING_JACK in supported_types
        assert len(supported_types) == 4
    
    def test_get_version(self):
        """Test retrieving exercise definitions version."""
        registry = ExerciseRegistryService()
        version = registry.get_version()
        
        assert version is not None
        assert isinstance(version, str)
        assert version == "1.0.0"
    
    def test_pushup_recognition_pattern(self):
        """Test push-up recognition pattern configuration."""
        registry = ExerciseRegistryService()
        pushup = registry.get_exercise(ExerciseType.PUSHUP)
        
        assert pushup.recognition_pattern.body_orientation == "horizontal"
        assert pushup.recognition_pattern.torso_angle_min == 0
        assert pushup.recognition_pattern.torso_angle_max == 20
        assert pushup.recognition_pattern.primary_joint == "elbow"
        assert pushup.recognition_pattern.oscillation_required is True
        assert pushup.recognition_pattern.stationary_feet is True
    
    def test_squat_recognition_pattern(self):
        """Test squat recognition pattern configuration."""
        registry = ExerciseRegistryService()
        squat = registry.get_exercise(ExerciseType.SQUAT)
        
        assert squat.recognition_pattern.body_orientation == "vertical"
        assert squat.recognition_pattern.torso_angle_min == 70
        assert squat.recognition_pattern.torso_angle_max == 90
        assert squat.recognition_pattern.primary_joint == "knee"
        assert squat.recognition_pattern.oscillation_required is True
    
    def test_form_rules_structure(self):
        """Test that form rules have correct structure."""
        registry = ExerciseRegistryService()
        pushup = registry.get_exercise(ExerciseType.PUSHUP)
        
        for rule in pushup.form_rules:
            assert rule.rule_id is not None
            assert rule.description is not None
            assert len(rule.joint_angles) > 0
            assert rule.threshold > 0
            assert rule.severity_multiplier > 0
            assert rule.suggestion is not None
    
    def test_camera_placement_guidance(self):
        """Test that camera placement guidance is provided."""
        registry = ExerciseRegistryService()
        
        for exercise_type in [ExerciseType.PUSHUP, ExerciseType.SQUAT, 
                              ExerciseType.PLANK, ExerciseType.JUMPING_JACK]:
            exercise = registry.get_exercise(exercise_type)
            assert exercise.camera_distance_meters > 0
            assert exercise.camera_height is not None
            assert exercise.camera_angle is not None
    
    def test_angle_thresholds_hysteresis(self):
        """Test that angle thresholds include hysteresis for debouncing."""
        registry = ExerciseRegistryService()
        
        # Test exercises with rep counting (not plank)
        for exercise_type in [ExerciseType.PUSHUP, ExerciseType.SQUAT, ExerciseType.JUMPING_JACK]:
            exercise = registry.get_exercise(exercise_type)
            assert exercise.angle_thresholds is not None
            assert exercise.angle_thresholds.hysteresis > 0
    
    def test_min_rep_duration(self):
        """Test that exercises have minimum rep duration to prevent double-counting."""
        registry = ExerciseRegistryService()
        
        for exercise_type in [ExerciseType.PUSHUP, ExerciseType.SQUAT, ExerciseType.JUMPING_JACK]:
            exercise = registry.get_exercise(exercise_type)
            assert exercise.min_rep_duration_seconds > 0
    
    def test_unknown_exercise_type(self):
        """Test handling of unknown exercise type."""
        registry = ExerciseRegistryService()
        unknown = registry.get_exercise(ExerciseType.UNKNOWN)
        
        assert unknown is None
