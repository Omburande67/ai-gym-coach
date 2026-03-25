'use client';

import React, { useRef, useEffect } from 'react';
import type { PoseData, PoseKeypoint } from '@/types/pose';
import { SKELETON_CONNECTIONS, getColorByVisibility } from '@/utils/skeleton';

interface SkeletonOverlayProps {
  poseData: PoseData | null;
  width: number;
  height: number;
  minVisibility?: number;
  showKeypoints?: boolean;
  showConnections?: boolean;
  keypointRadius?: number;
  lineWidth?: number;
}

/**
 * SkeletonOverlay Component
 * 
 * Draws pose keypoints and skeleton connections on a canvas overlay.
 * Implements task 3.6 requirements:
 * - Draw keypoints and connections on canvas
 * - Color-code joints by visibility confidence
 * - Update visualization in real-time
 * 
 * Color coding:
 * - Green (visibility >= 0.7): High confidence
 * - Yellow (visibility >= 0.4): Medium confidence
 * - Red (visibility < 0.4): Low confidence
 */
export const SkeletonOverlay: React.FC<SkeletonOverlayProps> = ({
  poseData,
  width,
  height,
  minVisibility = 0.3,
  showKeypoints = true,
  showConnections = true,
  keypointRadius = 5,
  lineWidth = 2,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  /**
   * Draw skeleton overlay on canvas
   */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !poseData) {
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.clearRect(0, 0, width, height);
      }
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    const keypoints = poseData.keypoints;

    // Set globally for futuristic feel
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Draw connections first (so keypoints appear on top)
    if (showConnections) {
      drawConnections(ctx, keypoints, width, height, minVisibility, lineWidth);
    }

    // Draw keypoints
    if (showKeypoints) {
      drawKeypoints(ctx, keypoints, width, height, minVisibility, keypointRadius);
    }
  }, [poseData, width, height, minVisibility, showKeypoints, showConnections, keypointRadius, lineWidth]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="absolute top-0 left-0 pointer-events-none z-20"
      style={{ filter: 'drop-shadow(0 0 8px rgba(102, 126, 234, 0.5))' }}
    />
  );
};

/**
 * Draw keypoints on canvas
 * Futuristic node-style joint markers
 */
function drawKeypoints(
  ctx: CanvasRenderingContext2D,
  keypoints: PoseKeypoint[],
  width: number,
  height: number,
  minVisibility: number,
  radius: number
): void {
  keypoints.forEach((keypoint, idx) => {
    // Skip keypoints with low visibility
    if (keypoint.visibility < minVisibility) return;

    // Convert normalized coordinates (0-1) to canvas coordinates
    const x = keypoint.x * width;
    const y = keypoint.y * height;

    // Get color based on visibility
    const color = getColorByVisibility(keypoint.visibility);

    // Draw glow effect
    ctx.shadowBlur = 10;
    ctx.shadowColor = color;
    
    // Draw outer node
    ctx.beginPath();
    ctx.arc(x, y, radius + 2, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.fill();
    
    // Draw inner node (the core)
    ctx.beginPath();
    ctx.arc(x, y, radius - 1, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Reset shadow for next element
    ctx.shadowBlur = 0;

    // Draw white center dot for "tech" look
    ctx.beginPath();
    ctx.arc(x, y, 1.5, 0, 2 * Math.PI);
    ctx.fillStyle = 'white';
    ctx.fill();
    
    // Add joint labels for specific main joints if high visibility
    const mainJoints = [0, 11, 12, 23, 24]; // Nose, Shoulders, Hips
    if (mainJoints.includes(idx) && keypoint.visibility > 0.8) {
        ctx.font = '8px monospace';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.fillText(keypoint.name.replace(/_/g, ' '), x + 8, y);
    }
  });
}

/**
 * Draw skeleton connections between keypoints
 * Glowing "cyber" connections
 */
function drawConnections(
  ctx: CanvasRenderingContext2D,
  keypoints: PoseKeypoint[],
  width: number,
  height: number,
  minVisibility: number,
  lineWidth: number
): void {
  SKELETON_CONNECTIONS.forEach(([startIdx, endIdx]) => {
    const startKeypoint = keypoints[startIdx];
    const endKeypoint = keypoints[endIdx];

    // Skip if either keypoint is missing or has low visibility
    if (
      !startKeypoint ||
      !endKeypoint ||
      startKeypoint.visibility < minVisibility ||
      endKeypoint.visibility < minVisibility
    ) {
      return;
    }

    // Convert normalized coordinates to canvas coordinates
    const startX = startKeypoint.x * width;
    const startY = startKeypoint.y * height;
    const endX = endKeypoint.x * width;
    const endY = endKeypoint.y * height;

    // Use average visibility for connection color
    const avgVisibility = (startKeypoint.visibility + endKeypoint.visibility) / 2;
    const color = getColorByVisibility(avgVisibility);

    // Draw connection line glow
    ctx.shadowBlur = 8;
    ctx.shadowColor = color;
    
    // Draw thick background line for depth
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.stroke();

    // Draw thin bright core line for "tech" look
    ctx.shadowBlur = 0;
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.lineWidth = 0.5;
    ctx.stroke();
  });
}

export default SkeletonOverlay;
