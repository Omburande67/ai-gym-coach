/**
 * Pose detection types for AI Gym Coach
 */

export interface PoseKeypoint {
  x: number; // Normalized 0-1
  y: number; // Normalized 0-1
  z: number; // Depth relative to hips
  visibility: number; // Confidence 0-1
  name: string; // Joint name (e.g., "left_elbow")
}

export interface PoseData {
  keypoints: PoseKeypoint[]; // 33 keypoints
  timestamp: number; // Unix timestamp ms
}

export type CameraPermissionState = 'granted' | 'denied' | 'prompt';

export interface CameraError {
  type: 'permission_denied' | 'not_found' | 'in_use' | 'unknown';
  message: string;
}
