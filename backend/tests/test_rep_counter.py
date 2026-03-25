"""Unit tests for rep counter."""

import pytest
from app.models.exercise import ExerciseType
from app.models.pose import PoseKeypoint, PoseData
from app.services.rep_counter import RepCounter, RepPhase


class TestRepCounter:
    """Test suite for RepCounter."""
    
    def create_pushup_pose(self, elbow_angle: float, timestamp: float = 0) -> PoseData:
        """Create a pose with specific elbow angle for push-up."""
        # For push-up, elbow angle is: shoulder -> elbow -> wrist
        # We'll create a simple 2D configuration
        
        # When elbow_angle is 180 (straight arm): shoulder, elbow, wrist in line
        # When elbow_angle is 90 (bent arm): wrist is perpendicular to shoulder-elbow line
        
        if elbow_angle >= 160:
            # Straight arm position (UP)
            keypoints = [
                # Shoulders (above elbows)
                PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
                PoseKeypoint(x=0.6, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
                # Elbows (middle)
                PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
                PoseKeypoint(x=0.6, y=0.5, z=0.0, visibility=0.9, name="right_elbow"),
                # Wrists (below elbows, in line)
                PoseKeypoint(x=0.4, y=0.7, z=0.0, visibility=0.9, name="left_wrist"),
                PoseKeypoint(x=0.6, y=0.7, z=0.0, visibility=0.9, name="right_wrist"),
                # Hips
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
                # Knees
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
                # Ankles
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
            ]
        elif elbow_angle <= 100:
            # Bent arm position (DOWN)
            keypoints = [
                # Shoulders (above elbows)
                PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
                PoseKeypoint(x=0.6, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
                # Elbows (middle)
                PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
                PoseKeypoint(x=0.6, y=0.5, z=0.0, visibility=0.9, name="right_elbow"),
                # Wrists (to the side, creating ~90 degree angle)
                PoseKeypoint(x=0.2, y=0.5, z=0.0, visibility=0.9, name="left_wrist"),
                PoseKeypoint(x=0.8, y=0.5, z=0.0, visibility=0.9, name="right_wrist"),
                # Hips
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
                # Knees
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
                # Ankles
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
            ]
        else:
            # Intermediate position (partial range)
            keypoints = [
                # Shoulders (above elbows)
                PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
                PoseKeypoint(x=0.6, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
                # Elbows (middle)
                PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
                PoseKeypoint(x=0.6, y=0.5, z=0.0, visibility=0.9, name="right_elbow"),
                # Wrists (slightly to the side, creating ~120 degree angle)
                PoseKeypoint(x=0.3, y=0.6, z=0.0, visibility=0.9, name="left_wrist"),
                PoseKeypoint(x=0.7, y=0.6, z=0.0, visibility=0.9, name="right_wrist"),
                # Hips
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
                # Knees
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
                # Ankles
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
            ]
        
        return PoseData(keypoints=keypoints, timestamp=int(timestamp * 1000))
    
    def create_squat_pose(self, knee_angle: float, timestamp: float = 0) -> PoseData:
        """Create a pose with specific knee angle for squat."""
        # For squat, knee angle is: hip -> knee -> ankle
        
        if knee_angle >= 160:
            # Straight leg position (UP)
            keypoints = [
                # Shoulders
                PoseKeypoint(x=0.5, y=0.2, z=0.0, visibility=0.9, name="left_shoulder"),
                PoseKeypoint(x=0.5, y=0.2, z=0.0, visibility=0.9, name="right_shoulder"),
                # Elbows
                PoseKeypoint(x=0.4, y=0.4, z=0.0, visibility=0.9, name="left_elbow"),
                PoseKeypoint(x=0.6, y=0.4, z=0.0, visibility=0.9, name="right_elbow"),
                # Wrists
                PoseKeypoint(x=0.4, y=0.6, z=0.0, visibility=0.9, name="left_wrist"),
                PoseKeypoint(x=0.6, y=0.6, z=0.0, visibility=0.9, name="right_wrist"),
                # Hips
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
                PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
                # Knees (in line with hips and ankles)
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
                PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
                # Ankles
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
                PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
            ]
        else:
            # Bent leg position (DOWN)
            keypoints = [
                # Shoulders
                PoseKeypoint(x=0.5, y=0.2, z=0.0, visibility=0.9, name="left_shoulder"),
                PoseKeypoint(x=0.5, y=0.2, z=0.0, visibility=0.9, name="right_shoulder"),
                # Elbows
                PoseKeypoint(x=0.4, y=0.4, z=0.0, visibility=0.9, name="left_elbow"),
                PoseKeypoint(x=0.6, y=0.4, z=0.0, visibility=0.9, name="right_elbow"),
                # Wrists
                PoseKeypoint(x=0.4, y=0.6, z=0.0, visibility=0.9, name="left_wrist"),
                PoseKeypoint(x=0.6, y=0.6, z=0.0, visibility=0.9, name="right_wrist"),
                # Hips (lower for squat)
                PoseKeypoint(x=0.5, y=0.6, z=0.0, visibility=0.9, name="left_hip"),
                PoseKeypoint(x=0.5, y=0.6, z=0.0, visibility=0.9, name="right_hip"),
                # Knees (bent, creating ~90 degree angle)
                PoseKeypoint(x=0.5, y=0.8, z=0.0, visibility=0.9, name="left_knee"),
                PoseKeypoint(x=0.5, y=0.8, z=0.0, visibility=0.9, name="right_knee"),
                # Ankles (forward of knees)
                PoseKeypoint(x=0.3, y=0.8, z=0.0, visibility=0.9, name="left_ankle"),
                PoseKeypoint(x=0.7, y=0.8, z=0.0, visibility=0.9, name="right_ankle"),
            ]
        
        return PoseData(keypoints=keypoints, timestamp=int(timestamp * 1000))
    
    def test_initialization(self):
        """Test rep counter initialization."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        assert counter.exercise_type == ExerciseType.PUSHUP
        assert counter.count == 0
        assert counter.current_phase == RepPhase.UP
    
    def test_pushup_full_rep(self):
        """Test counting a full push-up rep."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Start in UP position
        pose_up = self.create_pushup_pose(elbow_angle=170, timestamp=0.0)
        result = counter.update(pose_up)
        assert result is None
        assert counter.current_phase == RepPhase.UP
        
        # Move to DOWN position
        pose_down = self.create_pushup_pose(elbow_angle=80, timestamp=0.3)
        result = counter.update(pose_down)
        assert result is None
        assert counter.current_phase == RepPhase.DOWN
        
        # Return to UP position (completes rep)
        pose_up2 = self.create_pushup_pose(elbow_angle=170, timestamp=0.6)
        result = counter.update(pose_up2)
        assert result == 1
        assert counter.get_count() == 1
    
    def test_squat_full_rep(self):
        """Test counting a full squat rep."""
        counter = RepCounter(ExerciseType.SQUAT)
        
        # Start in UP position
        pose_up = self.create_squat_pose(knee_angle=170, timestamp=0.0)
        result = counter.update(pose_up)
        assert result is None
        
        # Move to DOWN position
        pose_down = self.create_squat_pose(knee_angle=80, timestamp=0.3)
        result = counter.update(pose_down)
        assert result is None
        assert counter.current_phase == RepPhase.DOWN
        
        # Return to UP position (completes rep)
        pose_up2 = self.create_squat_pose(knee_angle=170, timestamp=0.6)
        result = counter.update(pose_up2)
        assert result == 1
        assert counter.get_count() == 1
    
    def test_multiple_reps(self):
        """Test counting multiple reps."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Perform 3 reps
        for i in range(3):
            base_time = i * 1.0
            
            # UP position
            pose_up = self.create_pushup_pose(elbow_angle=170, timestamp=base_time)
            counter.update(pose_up)
            
            # DOWN position
            pose_down = self.create_pushup_pose(elbow_angle=80, timestamp=base_time + 0.3)
            counter.update(pose_down)
            
            # UP position (completes rep)
            pose_up2 = self.create_pushup_pose(elbow_angle=170, timestamp=base_time + 0.6)
            result = counter.update(pose_up2)
            
            assert result == i + 1
        
        assert counter.get_count() == 3
    
    def test_partial_range_not_counted(self):
        """Test that partial range of motion doesn't count as rep."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Start in UP position
        pose_up = self.create_pushup_pose(elbow_angle=170, timestamp=0.0)
        counter.update(pose_up)
        
        # Only go to 120° (not deep enough - needs to be < 100° to count)
        pose_partial = self.create_pushup_pose(elbow_angle=120, timestamp=0.3)
        counter.update(pose_partial)
        
        # Return to UP
        pose_up2 = self.create_pushup_pose(elbow_angle=170, timestamp=0.6)
        result = counter.update(pose_up2)
        
        # Should not count as rep because we never reached DOWN phase
        assert result is None
        assert counter.get_count() == 0
    
    def test_hysteresis_prevents_double_counting(self):
        """Test that hysteresis buffer prevents double-counting."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Complete one rep
        counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.0))
        counter.update(self.create_pushup_pose(elbow_angle=80, timestamp=0.3))
        result = counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.6))
        assert result == 1
        
        # Small oscillation around threshold (should not trigger new rep)
        counter.update(self.create_pushup_pose(elbow_angle=165, timestamp=0.7))
        counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.8))
        
        assert counter.get_count() == 1
    
    def test_minimum_rep_duration(self):
        """Test that minimum rep duration is enforced."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Try to complete rep too quickly (< 0.5s)
        counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.0))
        counter.update(self.create_pushup_pose(elbow_angle=80, timestamp=0.1))
        result = counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.2))
        
        # Should not count due to minimum duration
        assert result is None
        assert counter.get_count() == 0
    
    def test_plank_duration_tracking(self):
        """Test plank duration tracking (not rep-based)."""
        counter = RepCounter(ExerciseType.PLANK)
        
        # Create plank pose
        keypoints = [
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_shoulder"),
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_shoulder"),
            PoseKeypoint(x=0.5, y=0.6, z=0.0, visibility=0.9, name="left_elbow"),
            PoseKeypoint(x=0.5, y=0.6, z=0.0, visibility=0.9, name="right_elbow"),
            PoseKeypoint(x=0.5, y=0.65, z=0.0, visibility=0.9, name="left_wrist"),
            PoseKeypoint(x=0.5, y=0.65, z=0.0, visibility=0.9, name="right_wrist"),
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
            PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
            PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
            PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
            PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
        ]
        
        # Update at different times
        pose1 = PoseData(keypoints=keypoints, timestamp=0)
        counter.update(pose1)
        
        pose2 = PoseData(keypoints=keypoints, timestamp=5000)  # 5 seconds later
        counter.update(pose2)
        
        # Should track duration, not reps
        assert counter.get_count() == 0
        assert counter.get_duration() >= 4.9  # Allow small floating point error
    
    def test_reset(self):
        """Test resetting the counter."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Count some reps
        counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.0))
        counter.update(self.create_pushup_pose(elbow_angle=80, timestamp=0.3))
        counter.update(self.create_pushup_pose(elbow_angle=170, timestamp=0.6))
        
        assert counter.get_count() > 0
        
        # Reset
        counter.reset()
        
        assert counter.get_count() == 0
        assert counter.current_phase == RepPhase.UP
        assert counter.duration_seconds == 0.0
    
    def test_missing_keypoints(self):
        """Test handling of missing keypoints."""
        counter = RepCounter(ExerciseType.PUSHUP)
        
        # Create pose with missing elbow keypoints
        keypoints = [
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.1, name="left_shoulder"),
            PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.1, name="right_shoulder"),
        ]
        pose = PoseData(keypoints=keypoints, timestamp=0)
        
        # Should handle gracefully
        result = counter.update(pose)
        assert result is None
    
    def test_get_count(self):
        """Test getting current count."""
        counter = RepCounter(ExerciseType.SQUAT)
        
        assert counter.get_count() == 0
        
        # Complete a rep
        counter.update(self.create_squat_pose(knee_angle=170, timestamp=0.0))
        counter.update(self.create_squat_pose(knee_angle=80, timestamp=0.3))
        counter.update(self.create_squat_pose(knee_angle=170, timestamp=0.6))
        
        assert counter.get_count() == 1
    
    def test_different_exercise_types(self):
        """Test that different exercise types use correct angles."""
        # Push-up uses elbow angle
        pushup_counter = RepCounter(ExerciseType.PUSHUP)
        assert pushup_counter.exercise_type == ExerciseType.PUSHUP
        assert pushup_counter.current_phase == RepPhase.UP
        
        # Squat uses knee angle
        squat_counter = RepCounter(ExerciseType.SQUAT)
        assert squat_counter.exercise_type == ExerciseType.SQUAT
        assert squat_counter.current_phase == RepPhase.UP
        
        # Jumping jack uses shoulder angle and starts in DOWN phase
        jj_counter = RepCounter(ExerciseType.JUMPING_JACK)
        assert jj_counter.exercise_type == ExerciseType.JUMPING_JACK
        assert jj_counter.current_phase == RepPhase.DOWN
        
        # Plank tracks duration
        plank_counter = RepCounter(ExerciseType.PLANK)
        assert plank_counter.exercise_type == ExerciseType.PLANK
    
    def test_jumping_jack_rep_counting(self):
        """Test jumping jack rep counting (DOWN → UP → DOWN = 1 rep)."""
        counter = RepCounter(ExerciseType.JUMPING_JACK)
        
        # Should start in DOWN phase (arms at sides)
        assert counter.current_phase == RepPhase.DOWN
        
        # Create jumping jack poses with shoulder angles
        # DOWN: arms at sides (shoulder angle < 30°)
        # UP: arms overhead (shoulder angle > 160°)
        
        def create_jj_pose(arms_up: bool, timestamp: float) -> PoseData:
            """Create jumping jack pose."""
            if arms_up:
                # Arms overhead (hip -> shoulder -> elbow in straight line upward)
                keypoints = [
                    PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
                    PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
                    PoseKeypoint(x=0.5, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
                    PoseKeypoint(x=0.5, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
                    PoseKeypoint(x=0.5, y=0.1, z=0.0, visibility=0.9, name="left_elbow"),
                    PoseKeypoint(x=0.5, y=0.1, z=0.0, visibility=0.9, name="right_elbow"),
                    PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
                    PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
                    PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
                    PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
                    PoseKeypoint(x=0.5, y=0.05, z=0.0, visibility=0.9, name="left_wrist"),
                    PoseKeypoint(x=0.5, y=0.05, z=0.0, visibility=0.9, name="right_wrist"),
                ]
            else:
                # Arms at sides (elbow below shoulder, creating small angle)
                keypoints = [
                    PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="left_hip"),
                    PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=0.9, name="right_hip"),
                    PoseKeypoint(x=0.5, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
                    PoseKeypoint(x=0.5, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
                    PoseKeypoint(x=0.5, y=0.35, z=0.0, visibility=0.9, name="left_elbow"),
                    PoseKeypoint(x=0.5, y=0.35, z=0.0, visibility=0.9, name="right_elbow"),
                    PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="left_knee"),
                    PoseKeypoint(x=0.5, y=0.7, z=0.0, visibility=0.9, name="right_knee"),
                    PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="left_ankle"),
                    PoseKeypoint(x=0.5, y=0.9, z=0.0, visibility=0.9, name="right_ankle"),
                    PoseKeypoint(x=0.5, y=0.4, z=0.0, visibility=0.9, name="left_wrist"),
                    PoseKeypoint(x=0.5, y=0.4, z=0.0, visibility=0.9, name="right_wrist"),
                ]
            return PoseData(keypoints=keypoints, timestamp=int(timestamp * 1000))
        
        # Start with arms down
        pose_down1 = create_jj_pose(arms_up=False, timestamp=0.0)
        result = counter.update(pose_down1)
        assert result is None
        assert counter.current_phase == RepPhase.DOWN
        
        # Raise arms overhead
        pose_up = create_jj_pose(arms_up=True, timestamp=0.3)
        result = counter.update(pose_up)
        assert result is None
        assert counter.current_phase == RepPhase.UP
        
        # Lower arms back down (completes rep)
        pose_down2 = create_jj_pose(arms_up=False, timestamp=0.6)
        result = counter.update(pose_down2)
        assert result == 1
        assert counter.get_count() == 1
