"""Unit tests for biomechanics calculations."""

import math
import pytest
from app.models.pose import PoseKeypoint, PoseData
from app.utils.biomechanics import (
    calculate_angle,
    get_keypoint_by_name,
    calculate_joint_angles,
    get_average_angle
)


class TestCalculateAngle:
    """Tests for the calculate_angle function."""
    
    def test_right_angle(self):
        """Test calculation of a 90-degree angle."""
        # Create three points forming a right angle
        point1 = PoseKeypoint(x=0.0, y=0.0, z=0.0, visibility=1.0, name="p1")
        point2 = PoseKeypoint(x=0.0, y=1.0, z=0.0, visibility=1.0, name="p2")
        point3 = PoseKeypoint(x=1.0, y=1.0, z=0.0, visibility=1.0, name="p3")
        
        angle = calculate_angle(point1, point2, point3)
        
        assert angle is not None
        assert abs(angle - 90.0) < 0.1
    
    def test_straight_angle(self):
        """Test calculation of a 180-degree angle (straight line)."""
        # Three points in a straight line
        point1 = PoseKeypoint(x=0.0, y=0.0, z=0.0, visibility=1.0, name="p1")
        point2 = PoseKeypoint(x=0.5, y=0.0, z=0.0, visibility=1.0, name="p2")
        point3 = PoseKeypoint(x=1.0, y=0.0, z=0.0, visibility=1.0, name="p3")
        
        angle = calculate_angle(point1, point2, point3)
        
        assert angle is not None
        assert abs(angle - 180.0) < 0.1
    
    def test_acute_angle(self):
        """Test calculation of a 60-degree angle."""
        # Create three points forming a 60-degree angle
        # Using equilateral triangle geometry
        point1 = PoseKeypoint(x=0.0, y=0.0, z=0.0, visibility=1.0, name="p1")
        point2 = PoseKeypoint(x=1.0, y=0.0, z=0.0, visibility=1.0, name="p2")
        point3 = PoseKeypoint(x=0.5, y=0.866, z=0.0, visibility=1.0, name="p3")
        
        angle = calculate_angle(point1, point2, point3)
        
        assert angle is not None
        assert 55.0 < angle < 65.0  # Approximately 60 degrees
    
    def test_low_visibility_returns_none(self):
        """Test that low visibility keypoints return None."""
        point1 = PoseKeypoint(x=0.0, y=0.0, z=0.0, visibility=0.3, name="p1")
        point2 = PoseKeypoint(x=0.0, y=1.0, z=0.0, visibility=1.0, name="p2")
        point3 = PoseKeypoint(x=1.0, y=1.0, z=0.0, visibility=1.0, name="p3")
        
        angle = calculate_angle(point1, point2, point3, min_visibility=0.5)
        
        assert angle is None
    
    def test_coincident_points_returns_none(self):
        """Test that coincident points (zero-length vector) return None."""
        # point1 and point2 are the same
        point1 = PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=1.0, name="p1")
        point2 = PoseKeypoint(x=0.5, y=0.5, z=0.0, visibility=1.0, name="p2")
        point3 = PoseKeypoint(x=1.0, y=1.0, z=0.0, visibility=1.0, name="p3")
        
        angle = calculate_angle(point1, point2, point3)
        
        assert angle is None
    
    def test_custom_visibility_threshold(self):
        """Test custom visibility threshold."""
        point1 = PoseKeypoint(x=0.0, y=0.0, z=0.0, visibility=0.6, name="p1")
        point2 = PoseKeypoint(x=0.0, y=1.0, z=0.0, visibility=0.6, name="p2")
        point3 = PoseKeypoint(x=1.0, y=1.0, z=0.0, visibility=0.6, name="p3")
        
        # Should return None with default threshold (0.5)
        angle_default = calculate_angle(point1, point2, point3)
        assert angle_default is not None
        
        # Should return None with higher threshold
        angle_high = calculate_angle(point1, point2, point3, min_visibility=0.7)
        assert angle_high is None


class TestGetKeypointByName:
    """Tests for the get_keypoint_by_name function."""
    
    def test_find_existing_keypoint(self):
        """Test finding a keypoint that exists."""
        keypoints = [
            PoseKeypoint(x=0.1, y=0.2, z=0.0, visibility=0.9, name="nose"),
            PoseKeypoint(x=0.3, y=0.4, z=0.0, visibility=0.8, name="left_elbow"),
            PoseKeypoint(x=0.5, y=0.6, z=0.0, visibility=0.7, name="right_knee"),
        ]
        pose_data = PoseData(keypoints=keypoints, timestamp=1234567890)
        
        keypoint = get_keypoint_by_name(pose_data, "left_elbow")
        
        assert keypoint is not None
        assert keypoint.name == "left_elbow"
        assert keypoint.x == 0.3
        assert keypoint.y == 0.4
    
    def test_keypoint_not_found(self):
        """Test that non-existent keypoint returns None."""
        keypoints = [
            PoseKeypoint(x=0.1, y=0.2, z=0.0, visibility=0.9, name="nose"),
        ]
        pose_data = PoseData(keypoints=keypoints, timestamp=1234567890)
        
        keypoint = get_keypoint_by_name(pose_data, "left_elbow")
        
        assert keypoint is None
    
    def test_empty_keypoints(self):
        """Test with empty keypoints list."""
        pose_data = PoseData(keypoints=[], timestamp=1234567890)
        
        keypoint = get_keypoint_by_name(pose_data, "nose")
        
        assert keypoint is None


class TestCalculateJointAngles:
    """Tests for the calculate_joint_angles function."""
    
    def create_standing_pose(self) -> PoseData:
        """Create a simple standing pose with all keypoints visible."""
        keypoints = [
            # Shoulders
            PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
            PoseKeypoint(x=0.6, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
            # Elbows (arms down, ~180 degree angle)
            PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
            PoseKeypoint(x=0.6, y=0.5, z=0.0, visibility=0.9, name="right_elbow"),
            # Wrists
            PoseKeypoint(x=0.4, y=0.7, z=0.0, visibility=0.9, name="left_wrist"),
            PoseKeypoint(x=0.6, y=0.7, z=0.0, visibility=0.9, name="right_wrist"),
            # Hips
            PoseKeypoint(x=0.4, y=0.6, z=0.0, visibility=0.9, name="left_hip"),
            PoseKeypoint(x=0.6, y=0.6, z=0.0, visibility=0.9, name="right_hip"),
            # Knees (standing straight, ~180 degree angle)
            PoseKeypoint(x=0.4, y=0.8, z=0.0, visibility=0.9, name="left_knee"),
            PoseKeypoint(x=0.6, y=0.8, z=0.0, visibility=0.9, name="right_knee"),
            # Ankles
            PoseKeypoint(x=0.4, y=1.0, z=0.0, visibility=0.9, name="left_ankle"),
            PoseKeypoint(x=0.6, y=1.0, z=0.0, visibility=0.9, name="right_ankle"),
        ]
        return PoseData(keypoints=keypoints, timestamp=1234567890)
    
    def test_calculate_all_angles_standing(self):
        """Test calculating all angles for a standing pose."""
        pose_data = self.create_standing_pose()
        
        angles = calculate_joint_angles(pose_data)
        
        # Check that all expected angles are present
        expected_angles = [
            'left_elbow', 'right_elbow',
            'left_knee', 'right_knee',
            'left_hip', 'right_hip',
            'left_shoulder', 'right_shoulder',
            'torso'
        ]
        
        for angle_name in expected_angles:
            assert angle_name in angles
            assert angles[angle_name] is not None
        
        # Standing pose should have extended limbs (~180 degrees)
        assert angles['left_elbow'] > 160
        assert angles['right_elbow'] > 160
        assert angles['left_knee'] > 160
        assert angles['right_knee'] > 160
    
    def test_missing_keypoints_return_none(self):
        """Test that missing keypoints result in None angles."""
        # Create pose with only a few keypoints
        keypoints = [
            PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
            PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
            # Missing left_wrist
        ]
        pose_data = PoseData(keypoints=keypoints, timestamp=1234567890)
        
        angles = calculate_joint_angles(pose_data)
        
        # Left elbow should be None (missing wrist)
        assert angles['left_elbow'] is None
        # Right elbow should be None (missing all right arm keypoints)
        assert angles['right_elbow'] is None
    
    def test_low_visibility_keypoints(self):
        """Test that low visibility keypoints result in None angles."""
        keypoints = [
            PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
            PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.2, name="left_elbow"),  # Low visibility
            PoseKeypoint(x=0.4, y=0.7, z=0.0, visibility=0.9, name="left_wrist"),
        ]
        pose_data = PoseData(keypoints=keypoints, timestamp=1234567890)
        
        angles = calculate_joint_angles(pose_data, min_visibility=0.5)
        
        # Left elbow should be None due to low visibility
        assert angles['left_elbow'] is None
    
    def test_pushup_position(self):
        """Test angles for a pushup position (arms bent)."""
        keypoints = [
            # Shoulders
            PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_shoulder"),
            PoseKeypoint(x=0.6, y=0.5, z=0.0, visibility=0.9, name="right_shoulder"),
            # Elbows (bent at ~90 degrees)
            PoseKeypoint(x=0.3, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
            PoseKeypoint(x=0.7, y=0.5, z=0.0, visibility=0.9, name="right_elbow"),
            # Wrists (on ground)
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
        pose_data = PoseData(keypoints=keypoints, timestamp=1234567890)
        
        angles = calculate_joint_angles(pose_data)
        
        # Elbows should be bent (less than 180 degrees)
        assert angles['left_elbow'] is not None
        assert angles['right_elbow'] is not None
        assert angles['left_elbow'] < 120
        assert angles['right_elbow'] < 120
    
    def test_squat_position(self):
        """Test angles for a squat position (knees bent)."""
        keypoints = [
            # Shoulders
            PoseKeypoint(x=0.4, y=0.3, z=0.0, visibility=0.9, name="left_shoulder"),
            PoseKeypoint(x=0.6, y=0.3, z=0.0, visibility=0.9, name="right_shoulder"),
            # Elbows
            PoseKeypoint(x=0.4, y=0.5, z=0.0, visibility=0.9, name="left_elbow"),
            PoseKeypoint(x=0.6, y=0.5, z=0.0, visibility=0.9, name="right_elbow"),
            # Wrists
            PoseKeypoint(x=0.4, y=0.7, z=0.0, visibility=0.9, name="left_wrist"),
            PoseKeypoint(x=0.6, y=0.7, z=0.0, visibility=0.9, name="right_wrist"),
            # Hips (lower than standing)
            PoseKeypoint(x=0.4, y=0.7, z=0.0, visibility=0.9, name="left_hip"),
            PoseKeypoint(x=0.6, y=0.7, z=0.0, visibility=0.9, name="right_hip"),
            # Knees (bent - knees forward and down from hips)
            PoseKeypoint(x=0.35, y=0.85, z=0.0, visibility=0.9, name="left_knee"),
            PoseKeypoint(x=0.65, y=0.85, z=0.0, visibility=0.9, name="right_knee"),
            # Ankles (back from knees to create acute angle)
            PoseKeypoint(x=0.4, y=1.0, z=0.0, visibility=0.9, name="left_ankle"),
            PoseKeypoint(x=0.6, y=1.0, z=0.0, visibility=0.9, name="right_ankle"),
        ]
        pose_data = PoseData(keypoints=keypoints, timestamp=1234567890)
        
        angles = calculate_joint_angles(pose_data)
        
        # Knees should be bent (less than 180 degrees)
        assert angles['left_knee'] is not None
        assert angles['right_knee'] is not None
        assert angles['left_knee'] < 150
        assert angles['right_knee'] < 150


class TestGetAverageAngle:
    """Tests for the get_average_angle function."""
    
    def test_average_two_angles(self):
        """Test averaging two valid angles."""
        avg = get_average_angle(90.0, 110.0)
        assert avg == 100.0
    
    def test_one_none_angle(self):
        """Test with one None angle."""
        avg1 = get_average_angle(90.0, None)
        assert avg1 == 90.0
        
        avg2 = get_average_angle(None, 110.0)
        assert avg2 == 110.0
    
    def test_both_none_angles(self):
        """Test with both angles None."""
        avg = get_average_angle(None, None)
        assert avg is None
    
    def test_zero_angles(self):
        """Test with zero angles."""
        avg = get_average_angle(0.0, 0.0)
        assert avg == 0.0
    
    def test_large_angles(self):
        """Test with angles near 180 degrees."""
        avg = get_average_angle(170.0, 180.0)
        assert avg == 175.0
