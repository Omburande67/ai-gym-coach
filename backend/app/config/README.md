# Exercise Definitions Configuration

This directory contains the exercise definitions for the AI Gym Coach system.

## Files

- `exercise_definitions.json` - Complete exercise configuration including recognition patterns, angle thresholds, and form rules

## Structure

The exercise definitions file contains:

### Exercise Type
Each exercise has a unique type identifier:
- `pushup` - Push-up exercise
- `squat` - Squat exercise
- `plank` - Plank hold exercise
- `jumping_jack` - Jumping jack exercise

### Recognition Pattern
Defines how to identify the exercise from pose keypoints:
- `body_orientation` - Expected body position (horizontal/vertical)
- `torso_angle_min/max` - Torso angle range from ground (degrees)
- `primary_joint` - Main joint to monitor for the exercise
- `oscillation_required` - Whether the joint should oscillate
- `min_oscillation_range` - Minimum oscillation range (degrees)
- `stationary_feet` - Whether feet should remain stationary

### Angle Thresholds
Defines the angle ranges for rep counting:
- `up_min/up_max` - Angle range for UP phase (degrees)
- `down_min/down_max` - Angle range for DOWN phase (degrees)
- `hysteresis` - Buffer to prevent double-counting (degrees)

### Form Rules
Defines rules for detecting form mistakes:
- `rule_id` - Unique identifier for the rule
- `description` - Human-readable description
- `joint_angles` - Joints to monitor
- `threshold` - Deviation threshold to trigger detection
- `severity_multiplier` - Multiplier for severity calculation
- `suggestion` - Corrective feedback for the user

### Camera Placement
Guidance for optimal camera positioning:
- `camera_distance_meters` - Recommended distance from user
- `camera_height` - Recommended height (e.g., "waist")
- `camera_angle` - Recommended angle (e.g., "side", "front")

## Usage

### Python Backend

```python
from app.services.exercise_registry import exercise_registry
from app.models.exercise import ExerciseType

# Get a specific exercise definition
pushup = exercise_registry.get_exercise(ExerciseType.PUSHUP)

# Access angle thresholds
if pushup.angle_thresholds:
    print(f"UP phase: {pushup.angle_thresholds.up_min}° - {pushup.angle_thresholds.up_max}°")
    print(f"DOWN phase: {pushup.angle_thresholds.down_min}° - {pushup.angle_thresholds.down_max}°")

# Access form rules
for rule in pushup.form_rules:
    print(f"{rule.rule_id}: {rule.suggestion}")

# Get all supported exercises
all_exercises = exercise_registry.get_all_exercises()
for exercise_type, definition in all_exercises.items():
    print(f"{definition.display_name}: {definition.description}")
```

## Adding New Exercises

To add a new exercise:

1. Add the exercise type to `ExerciseType` enum in `app/models/exercise.py`
2. Add the exercise definition to `exercise_definitions.json`
3. Include all required fields:
   - Basic info (exercise_type, display_name, description)
   - Recognition pattern
   - Angle thresholds (if rep-based) or set `is_duration_based: true`
   - Form rules
   - Camera placement guidance
4. Update tests in `tests/test_exercise_definitions.py`

## Validation

The exercise definitions are validated using Pydantic models:
- `ExerciseDefinition` - Main exercise configuration
- `RecognitionPattern` - Exercise recognition rules
- `AngleThreshold` - Rep counting thresholds
- `FormRule` - Form analysis rules

All fields are type-checked and validated when loaded.

## Version

Current version: 1.0.0

The version number follows semantic versioning:
- Major: Breaking changes to the structure
- Minor: New exercises or non-breaking additions
- Patch: Bug fixes or clarifications
