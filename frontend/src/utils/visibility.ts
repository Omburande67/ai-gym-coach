/**
 * Visibility Detection Utilities
 * 
 * Implements Requirement 5.5: Full body visibility detection
 * - Check keypoint visibility scores
 * - Detect when user is out of frame (>20% keypoints with visibility <0.5)
 */

import { PoseData } from '@/types/pose';

export interface VisibilityStatus {
  isFullyVisible: boolean;
  visibleKeypointsCount: number;
  totalKeypointsCount: number;
  visibilityPercentage: number;
  lowVisibilityPercentage: number;
}

/**
 * Check if user is fully visible in frame
 * 
 * @param poseData - Pose data with keypoints
 * @param visibilityThreshold - Minimum visibility score (default: 0.5)
 * @param maxLowVisibilityPercentage - Maximum percentage of low visibility keypoints allowed (default: 0.2 = 20%)
 * @returns Visibility status
 */
export function checkFullBodyVisibility(
  poseData: PoseData | null,
  visibilityThreshold: number = 0.5,
  maxLowVisibilityPercentage: number = 0.8
): VisibilityStatus {
  if (!poseData || !poseData.keypoints || poseData.keypoints.length === 0) {
    return {
      isFullyVisible: false,
      visibleKeypointsCount: 0,
      totalKeypointsCount: 0,
      visibilityPercentage: 0,
      lowVisibilityPercentage: 1,
    };
  }

  const totalKeypoints = poseData.keypoints.length;
  const lowVisibilityKeypoints = poseData.keypoints.filter(
    (kp) => kp.visibility < visibilityThreshold
  ).length;

  const visibleKeypoints = totalKeypoints - lowVisibilityKeypoints;
  const lowVisibilityPercentage = lowVisibilityKeypoints / totalKeypoints;
  const visibilityPercentage = visibleKeypoints / totalKeypoints;

  // User is fully visible if less than maxLowVisibilityPercentage of keypoints have low visibility
  const isFullyVisible = lowVisibilityPercentage <= maxLowVisibilityPercentage;

  return {
    isFullyVisible,
    visibleKeypointsCount: visibleKeypoints,
    totalKeypointsCount: totalKeypoints,
    visibilityPercentage,
    lowVisibilityPercentage,
  };
}

/**
 * Get visibility warning message based on status
 */
export function getVisibilityWarningMessage(status: VisibilityStatus): string {
  if (status.isFullyVisible) {
    return '';
  }

  const lowVisibilityPercent = Math.round(status.lowVisibilityPercentage * 100);
  
  return `You are not fully visible in the frame. ${lowVisibilityPercent}% of your body is out of view. Please step back or adjust your camera position.`;
}
