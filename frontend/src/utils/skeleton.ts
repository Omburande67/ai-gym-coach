/**
 * Skeleton visualization utilities for pose detection
 * 
 * Defines the connections between keypoints to draw a skeleton overlay
 * Based on MediaPipe BlazePose 33-keypoint model
 */

/**
 * BlazePose keypoint indices
 * Reference: https://google.github.io/mediapipe/solutions/pose.html
 */
export const POSE_KEYPOINT_INDICES = {
  NOSE: 0,
  LEFT_EYE_INNER: 1,
  LEFT_EYE: 2,
  LEFT_EYE_OUTER: 3,
  RIGHT_EYE_INNER: 4,
  RIGHT_EYE: 5,
  RIGHT_EYE_OUTER: 6,
  LEFT_EAR: 7,
  RIGHT_EAR: 8,
  MOUTH_LEFT: 9,
  MOUTH_RIGHT: 10,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_PINKY: 17,
  RIGHT_PINKY: 18,
  LEFT_INDEX: 19,
  RIGHT_INDEX: 20,
  LEFT_THUMB: 21,
  RIGHT_THUMB: 22,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
  LEFT_HEEL: 29,
  RIGHT_HEEL: 30,
  LEFT_FOOT_INDEX: 31,
  RIGHT_FOOT_INDEX: 32,
} as const;

/**
 * Skeleton connections (pairs of keypoint indices)
 * Organized by body part for easier visualization
 */
export const SKELETON_CONNECTIONS: [number, number][] = [
  // Face
  [0, 1], // nose to left eye inner
  [1, 2], // left eye inner to left eye
  [2, 3], // left eye to left eye outer
  [3, 7], // left eye outer to left ear
  [0, 4], // nose to right eye inner
  [4, 5], // right eye inner to right eye
  [5, 6], // right eye to right eye outer
  [6, 8], // right eye outer to right ear
  [9, 10], // mouth left to mouth right

  // Torso
  [11, 12], // left shoulder to right shoulder
  [11, 23], // left shoulder to left hip
  [12, 24], // right shoulder to right hip
  [23, 24], // left hip to right hip

  // Left arm
  [11, 13], // left shoulder to left elbow
  [13, 15], // left elbow to left wrist
  [15, 17], // left wrist to left pinky
  [15, 19], // left wrist to left index
  [15, 21], // left wrist to left thumb
  [17, 19], // left pinky to left index

  // Right arm
  [12, 14], // right shoulder to right elbow
  [14, 16], // right elbow to right wrist
  [16, 18], // right wrist to right pinky
  [16, 20], // right wrist to right index
  [16, 22], // right wrist to right thumb
  [18, 20], // right pinky to right index

  // Left leg
  [23, 25], // left hip to left knee
  [25, 27], // left knee to left ankle
  [27, 29], // left ankle to left heel
  [27, 31], // left ankle to left foot index
  [29, 31], // left heel to left foot index

  // Right leg
  [24, 26], // right hip to right knee
  [26, 28], // right knee to right ankle
  [28, 30], // right ankle to right heel
  [28, 32], // right ankle to right foot index
  [30, 32], // right heel to right foot index
];

/**
 * Get color based on visibility confidence
 * High confidence: green, medium: yellow, low: red
 */
export function getColorByVisibility(visibility: number): string {
  if (visibility >= 0.7) {
    return '#22c55e'; // green-500
  } else if (visibility >= 0.4) {
    return '#eab308'; // yellow-500
  } else {
    return '#ef4444'; // red-500
  }
}

/**
 * Get color with alpha based on visibility
 */
export function getColorWithAlpha(visibility: number): string {
  const color = getColorByVisibility(visibility);
  return `${color}${Math.round(visibility * 255).toString(16).padStart(2, '0')}`;
}
