"""Biomechanical calculations for exercise analysis.

This module provides functions for calculating joint angles and other
biomechanical metrics from pose keypoints.
"""

import math
from typing import Dict, Optional, Tuple
from app.models.pose import PoseKeypoint, PoseData


def calculate_angle(
    point1: PoseKeypoint,
    point2: PoseKeypoint,
    point3: PoseKeypoint,
    min_visibility: float = 0.5
) -> Optional[float]:
    """
    Calculate the angle between three keypoints.
    
    The angle is calculated at point2 (the vertex), formed by the lines
    point1->point2 and point2->point3.
    
    Args:
        point1: First keypoint (e.g., shoulder)
        point2: Vertex keypoint (e.g., elbow)
        point3: Third keypoint (e.g., wrist)
        min_visibility: Minimum visibility threshold for valid calculation
        
    Returns:
        Angle in degrees (0-180), or None if keypoints have low visibility
        
    Example:
        >>> shoulder = PoseKeypoint(x=0.5, y=0.3, z=0, visibility=0.9, name="shoulder")
        >>> elbow = PoseKeypoint(x=0.6, y=0.5, z=0, visibility=0.9, name="elbow")
        >>> wrist = PoseKeypoint(x=0.7, y=0.7, z=0, visibility=0.9, name="wrist")
        >>> angle = calculate_angle(shoulder, elbow, wrist)
        >>> print(f"Elbow angle: {angle:.1f}°")
    """
    # Check visibility of all three keypoints
    if (point1.visibility < min_visibility or 
        point2.visibility < min_visibility or 
        point3.visibility < min_visibility):
        return None
    
    # Calculate vectors from point2 to point1 and point2 to point3
    # Using 2D coordinates (x, y) for angle calculation
    vector1_x = point1.x - point2.x
    vector1_y = point1.y - point2.y
    
    vector2_x = point3.x - point2.x
    vector2_y = point3.y - point2.y
    
    # Calculate magnitudes of vectors
    magnitude1 = math.sqrt(vector1_x**2 + vector1_y**2)
    magnitude2 = math.sqrt(vector2_x**2 + vector2_y**2)
    
    # Handle edge case where points are too close (avoid division by zero)
    if magnitude1 < 1e-6 or magnitude2 < 1e-6:
        return None
    
    # Calculate dot product
    dot_product = vector1_x * vector2_x + vector1_y * vector2_y
    
    # Calculate angle using dot product formula: cos(θ) = (a·b) / (|a||b|)
    cos_angle = dot_product / (magnitude1 * magnitude2)
    
    # Clamp to [-1, 1] to handle floating point errors
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    # Calculate angle in radians and convert to degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = math.degrees(angle_radians)
    
    return angle_degrees


def get_keypoint_by_name(pose_data: PoseData, name: str) -> Optional[PoseKeypoint]:
    """
    Get a keypoint from pose data by its name.
    
    Args:
        pose_data: Complete pose data
        name: Name of the keypoint to retrieve
        
    Returns:
        PoseKeypoint if found, None otherwise
    """
    for keypoint in pose_data.keypoints:
        if keypoint.name == name:
            return keypoint
    return None


def calculate_joint_angles(
    pose_data: PoseData,
    min_visibility: float = 0.5
) -> Dict[str, Optional[float]]:
    """
    Calculate all relevant joint angles from pose data.
    
    Returns angles for: elbow (left/right), knee (left/right), 
    hip (left/right), shoulder (left/right), and torso.
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold for valid calculation
        
    Returns:
        Dictionary mapping joint names to angles in degrees.
        Missing or low-visibility joints will have None values.
        
    Example:
        >>> angles = calculate_joint_angles(pose_data)
        >>> if angles['left_elbow'] is not None:
        ...     print(f"Left elbow: {angles['left_elbow']:.1f}°")
    """
    angles: Dict[str, Optional[float]] = {}
    
    # Left elbow angle: shoulder -> elbow -> wrist
    left_shoulder = get_keypoint_by_name(pose_data, "left_shoulder")
    left_elbow = get_keypoint_by_name(pose_data, "left_elbow")
    left_wrist = get_keypoint_by_name(pose_data, "left_wrist")
    
    if left_shoulder and left_elbow and left_wrist:
        angles['left_elbow'] = calculate_angle(
            left_shoulder, left_elbow, left_wrist, min_visibility
        )
    else:
        angles['left_elbow'] = None
    
    # Right elbow angle: shoulder -> elbow -> wrist
    right_shoulder = get_keypoint_by_name(pose_data, "right_shoulder")
    right_elbow = get_keypoint_by_name(pose_data, "right_elbow")
    right_wrist = get_keypoint_by_name(pose_data, "right_wrist")
    
    if right_shoulder and right_elbow and right_wrist:
        angles['right_elbow'] = calculate_angle(
            right_shoulder, right_elbow, right_wrist, min_visibility
        )
    else:
        angles['right_elbow'] = None
    
    # Left knee angle: hip -> knee -> ankle
    left_hip = get_keypoint_by_name(pose_data, "left_hip")
    left_knee = get_keypoint_by_name(pose_data, "left_knee")
    left_ankle = get_keypoint_by_name(pose_data, "left_ankle")
    
    if left_hip and left_knee and left_ankle:
        angles['left_knee'] = calculate_angle(
            left_hip, left_knee, left_ankle, min_visibility
        )
    else:
        angles['left_knee'] = None
    
    # Right knee angle: hip -> knee -> ankle
    right_hip = get_keypoint_by_name(pose_data, "right_hip")
    right_knee = get_keypoint_by_name(pose_data, "right_knee")
    right_ankle = get_keypoint_by_name(pose_data, "right_ankle")
    
    if right_hip and right_knee and right_ankle:
        angles['right_knee'] = calculate_angle(
            right_hip, right_knee, right_ankle, min_visibility
        )
    else:
        angles['right_knee'] = None
    
    # Left hip angle: shoulder -> hip -> knee
    if left_shoulder and left_hip and left_knee:
        angles['left_hip'] = calculate_angle(
            left_shoulder, left_hip, left_knee, min_visibility
        )
    else:
        angles['left_hip'] = None
    
    # Right hip angle: shoulder -> hip -> knee
    if right_shoulder and right_hip and right_knee:
        angles['right_hip'] = calculate_angle(
            right_shoulder, right_hip, right_knee, min_visibility
        )
    else:
        angles['right_hip'] = None
    
    # Left shoulder angle: hip -> shoulder -> elbow
    if left_hip and left_shoulder and left_elbow:
        angles['left_shoulder'] = calculate_angle(
            left_hip, left_shoulder, left_elbow, min_visibility
        )
    else:
        angles['left_shoulder'] = None
    
    # Right shoulder angle: hip -> shoulder -> elbow
    if right_hip and right_shoulder and right_elbow:
        angles['right_shoulder'] = calculate_angle(
            right_hip, right_shoulder, right_elbow, min_visibility
        )
    else:
        angles['right_shoulder'] = None
    
    # Torso angle: Calculate angle of torso relative to vertical
    # Using midpoint of shoulders and midpoint of hips
    if left_shoulder and right_shoulder and left_hip and right_hip:
        # Calculate midpoints
        shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_mid_x = (left_hip.x + right_hip.x) / 2
        hip_mid_y = (left_hip.y + right_hip.y) / 2
        
        # Check visibility
        avg_visibility = (
            left_shoulder.visibility + right_shoulder.visibility +
            left_hip.visibility + right_hip.visibility
        ) / 4
        
        if avg_visibility >= min_visibility:
            # Calculate angle from vertical (y-axis)
            # Vertical vector is (0, 1), torso vector is (hip->shoulder)
            torso_x = shoulder_mid_x - hip_mid_x
            torso_y = shoulder_mid_y - hip_mid_y
            
            # Calculate magnitude
            magnitude = math.sqrt(torso_x**2 + torso_y**2)
            
            if magnitude > 1e-6:
                # Angle from vertical: arccos(dot product with (0, -1))
                # Note: y increases downward in image coordinates
                cos_angle = abs(torso_y) / magnitude
                cos_angle = max(-1.0, min(1.0, cos_angle))
                angle_radians = math.acos(cos_angle)
                angles['torso'] = math.degrees(angle_radians)
            else:
                angles['torso'] = None
        else:
            angles['torso'] = None
    else:
        angles['torso'] = None
    
    return angles


def get_average_angle(angle1: Optional[float], angle2: Optional[float]) -> Optional[float]:
    """
    Calculate the average of two angles, handling None values.
    
    Useful for averaging left and right side angles (e.g., both elbows).
    
    Args:
        angle1: First angle in degrees
        angle2: Second angle in degrees
        
    Returns:
        Average angle if at least one is not None, otherwise None
    """
    if angle1 is not None and angle2 is not None:
        return (angle1 + angle2) / 2
    elif angle1 is not None:
        return angle1
    elif angle2 is not None:
        return angle2
    else:
        return None


def calculate_hip_shoulder_alignment(pose_data: PoseData, min_visibility: float = 0.5) -> float:
    """
    Calculate vertical alignment between hips and shoulders.
    
    Returns positive value if hips are below shoulders (sagging),
    negative value if hips are above shoulders (piking).
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Vertical deviation in normalized coordinates (approximate cm when multiplied by 100)
    """
    left_shoulder = get_keypoint_by_name(pose_data, "left_shoulder")
    right_shoulder = get_keypoint_by_name(pose_data, "right_shoulder")
    left_hip = get_keypoint_by_name(pose_data, "left_hip")
    right_hip = get_keypoint_by_name(pose_data, "right_hip")
    
    if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
        return 0.0
    
    avg_visibility = (
        left_shoulder.visibility + right_shoulder.visibility +
        left_hip.visibility + right_hip.visibility
    ) / 4
    
    if avg_visibility < min_visibility:
        return 0.0
    
    shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_y = (left_hip.y + right_hip.y) / 2
    
    # Return deviation (positive = hip sag, negative = hip pike)
    # Multiply by 100 to approximate cm
    return (hip_y - shoulder_y) * 100


def calculate_knee_alignment(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate knee alignment (knee cave detection).
    
    Returns negative value if knees cave inward, positive if knees bow outward.
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Knee alignment deviation in normalized coordinates, or None if insufficient data
    """
    left_knee = get_keypoint_by_name(pose_data, "left_knee")
    right_knee = get_keypoint_by_name(pose_data, "right_knee")
    left_ankle = get_keypoint_by_name(pose_data, "left_ankle")
    right_ankle = get_keypoint_by_name(pose_data, "right_ankle")
    
    if not all([left_knee, right_knee, left_ankle, right_ankle]):
        return None
    
    avg_visibility = (
        left_knee.visibility + right_knee.visibility +
        left_ankle.visibility + right_ankle.visibility
    ) / 4
    
    if avg_visibility < min_visibility:
        return None
    
    # Calculate horizontal distance between knees and ankles
    knee_width = abs(left_knee.x - right_knee.x)
    ankle_width = abs(left_ankle.x - right_ankle.x)
    
    # If knees are closer together than ankles, they're caving in
    # Return negative for cave, positive for bow
    return (knee_width - ankle_width) * 100


def calculate_neck_angle(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate neck angle deviation from neutral.
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Neck angle in degrees, or None if insufficient data
    """
    nose = get_keypoint_by_name(pose_data, "nose")
    left_shoulder = get_keypoint_by_name(pose_data, "left_shoulder")
    right_shoulder = get_keypoint_by_name(pose_data, "right_shoulder")
    
    if not all([nose, left_shoulder, right_shoulder]):
        return None
    
    avg_visibility = (nose.visibility + left_shoulder.visibility + right_shoulder.visibility) / 3
    
    if avg_visibility < min_visibility:
        return None
    
    # Calculate midpoint of shoulders
    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
    
    # Calculate angle from vertical
    dx = nose.x - shoulder_mid_x
    dy = nose.y - shoulder_mid_y
    
    magnitude = math.sqrt(dx**2 + dy**2)
    if magnitude < 1e-6:
        return None
    
    # Calculate angle from vertical (0 degrees = straight up)
    angle_radians = math.atan2(abs(dx), abs(dy))
    return math.degrees(angle_radians)


def calculate_torso_angle(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate torso angle from vertical.
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Torso angle from vertical in degrees (90 = horizontal, 0 = vertical), or None
    """
    angles = calculate_joint_angles(pose_data, min_visibility)
    return angles.get('torso')


def calculate_elbow_angle_from_torso(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate elbow flare angle from torso.
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Elbow angle from torso in degrees, or None if insufficient data
    """
    left_shoulder = get_keypoint_by_name(pose_data, "left_shoulder")
    right_shoulder = get_keypoint_by_name(pose_data, "right_shoulder")
    left_elbow = get_keypoint_by_name(pose_data, "left_elbow")
    right_elbow = get_keypoint_by_name(pose_data, "right_elbow")
    left_hip = get_keypoint_by_name(pose_data, "left_hip")
    right_hip = get_keypoint_by_name(pose_data, "right_hip")
    
    if not all([left_shoulder, right_shoulder, left_elbow, right_elbow, left_hip, right_hip]):
        return None
    
    avg_visibility = (
        left_shoulder.visibility + right_shoulder.visibility +
        left_elbow.visibility + right_elbow.visibility +
        left_hip.visibility + right_hip.visibility
    ) / 6
    
    if avg_visibility < min_visibility:
        return None
    
    # Calculate torso vector (shoulder midpoint to hip midpoint)
    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_mid_x = (left_hip.x + right_hip.x) / 2
    hip_mid_y = (left_hip.y + right_hip.y) / 2
    
    torso_dx = hip_mid_x - shoulder_mid_x
    torso_dy = hip_mid_y - shoulder_mid_y
    
    # Calculate elbow vector (shoulder to elbow)
    left_elbow_dx = left_elbow.x - left_shoulder.x
    left_elbow_dy = left_elbow.y - left_shoulder.y
    right_elbow_dx = right_elbow.x - right_shoulder.x
    right_elbow_dy = right_elbow.y - right_shoulder.y
    
    # Calculate angles
    torso_mag = math.sqrt(torso_dx**2 + torso_dy**2)
    left_elbow_mag = math.sqrt(left_elbow_dx**2 + left_elbow_dy**2)
    right_elbow_mag = math.sqrt(right_elbow_dx**2 + right_elbow_dy**2)
    
    if torso_mag < 1e-6 or left_elbow_mag < 1e-6 or right_elbow_mag < 1e-6:
        return None
    
    # Calculate angle between torso and elbow vectors
    left_dot = torso_dx * left_elbow_dx + torso_dy * left_elbow_dy
    left_cos = left_dot / (torso_mag * left_elbow_mag)
    left_cos = max(-1.0, min(1.0, left_cos))
    left_angle = math.degrees(math.acos(left_cos))
    
    right_dot = torso_dx * right_elbow_dx + torso_dy * right_elbow_dy
    right_cos = right_dot / (torso_mag * right_elbow_mag)
    right_cos = max(-1.0, min(1.0, right_cos))
    right_angle = math.degrees(math.acos(right_cos))
    
    # Return average angle
    return (left_angle + right_angle) / 2


def calculate_ankle_angle(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate ankle angle change (for heel lift detection).
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Ankle angle deviation in degrees, or None if insufficient data
    """
    left_knee = get_keypoint_by_name(pose_data, "left_knee")
    right_knee = get_keypoint_by_name(pose_data, "right_knee")
    left_ankle = get_keypoint_by_name(pose_data, "left_ankle")
    right_ankle = get_keypoint_by_name(pose_data, "right_ankle")
    left_heel = get_keypoint_by_name(pose_data, "left_heel")
    right_heel = get_keypoint_by_name(pose_data, "right_heel")
    
    # If heel keypoints are available, use them
    if left_heel and right_heel and left_ankle and right_ankle:
        avg_visibility = (
            left_heel.visibility + right_heel.visibility +
            left_ankle.visibility + right_ankle.visibility
        ) / 4
        
        if avg_visibility >= min_visibility:
            # Calculate vertical distance between ankle and heel
            left_diff = abs(left_ankle.y - left_heel.y)
            right_diff = abs(right_ankle.y - right_heel.y)
            avg_diff = (left_diff + right_diff) / 2
            
            # Convert to approximate angle (simplified)
            return avg_diff * 100
    
    # Fallback: use knee-ankle angle
    if left_knee and right_knee and left_ankle and right_ankle:
        avg_visibility = (
            left_knee.visibility + right_knee.visibility +
            left_ankle.visibility + right_ankle.visibility
        ) / 4
        
        if avg_visibility >= min_visibility:
            # Calculate angle change from vertical
            left_dx = left_ankle.x - left_knee.x
            left_dy = left_ankle.y - left_knee.y
            right_dx = right_ankle.x - right_knee.x
            right_dy = right_ankle.y - right_knee.y
            
            left_angle = math.degrees(math.atan2(abs(left_dx), abs(left_dy)))
            right_angle = math.degrees(math.atan2(abs(right_dx), abs(right_dy)))
            
            return (left_angle + right_angle) / 2
    
    return None


def calculate_shoulder_angle(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate shoulder angle (arm raise angle).
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Shoulder angle in degrees (0 = arms at sides, 180 = arms overhead), or None
    """
    angles = calculate_joint_angles(pose_data, min_visibility)
    left_shoulder = angles.get('left_shoulder')
    right_shoulder = angles.get('right_shoulder')
    
    return get_average_angle(left_shoulder, right_shoulder)


def calculate_hip_angle(pose_data: PoseData, min_visibility: float = 0.5) -> Optional[float]:
    """
    Calculate hip angle (leg spread angle).
    
    Args:
        pose_data: Complete pose data with keypoints
        min_visibility: Minimum visibility threshold
        
    Returns:
        Hip angle in degrees, or None if insufficient data
    """
    left_hip = get_keypoint_by_name(pose_data, "left_hip")
    right_hip = get_keypoint_by_name(pose_data, "right_hip")
    left_knee = get_keypoint_by_name(pose_data, "left_knee")
    right_knee = get_keypoint_by_name(pose_data, "right_knee")
    
    if not all([left_hip, right_hip, left_knee, right_knee]):
        return None
    
    avg_visibility = (
        left_hip.visibility + right_hip.visibility +
        left_knee.visibility + right_knee.visibility
    ) / 4
    
    if avg_visibility < min_visibility:
        return None
    
    # Calculate horizontal distance between knees (leg spread)
    knee_distance = abs(left_knee.x - right_knee.x)
    
    # Convert to approximate angle (simplified)
    # Wider spread = larger angle
    return knee_distance * 100
