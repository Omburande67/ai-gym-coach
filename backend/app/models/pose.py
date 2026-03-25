"""Pose detection models for the AI Gym Coach system."""

from typing import List
from pydantic import BaseModel, Field


class PoseKeypoint(BaseModel):
    """A single keypoint from pose detection."""
    x: float = Field(..., description="Normalized x-coordinate (0-1)")
    y: float = Field(..., description="Normalized y-coordinate (0-1)")
    z: float = Field(..., description="Depth relative to hips")
    visibility: float = Field(..., description="Confidence score (0-1)")
    name: str = Field(..., description="Joint name (e.g., 'left_elbow')")


class PoseData(BaseModel):
    """Complete pose data from a single frame."""
    keypoints: List[PoseKeypoint] = Field(..., description="33 keypoints from pose detection")
    timestamp: float = Field(..., description="Unix timestamp in milliseconds")
