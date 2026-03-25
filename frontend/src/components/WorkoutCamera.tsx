'use client';

import React, { useRef, useState, useCallback } from 'react';
import { CameraAccess } from './CameraAccess';
import { PoseDetector } from './PoseDetector';
import type { PoseData, CameraError } from '@/types/pose';

interface WorkoutCameraProps {
  onPoseDetected?: (poseData: PoseData) => void;
  onError?: (error: Error | CameraError) => void;
  width?: number;
  height?: number;
  targetFps?: number;
  showStatus?: boolean;
}

/**
 * WorkoutCamera Component
 * 
 * Integrated component that combines CameraAccess and PoseDetector
 * for easy workout tracking setup.
 * 
 * This component handles:
 * - Camera permission and video stream
 * - Pose detection with BlazePose
 * - Error handling for both camera and pose detection
 */
export const WorkoutCamera: React.FC<WorkoutCameraProps> = ({
  onPoseDetected,
  onError,
  width = 640,
  height = 480,
  targetFps = 15,
  showStatus = true,
}) => {
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const [isCameraReady, setIsCameraReady] = useState(false);

  /**
   * Handle camera stream ready
   */
  const handleStreamReady = useCallback((_stream: MediaStream) => {
    // Get the video element from the DOM
    const videoElement = document.querySelector('video') as HTMLVideoElement;
    if (videoElement) {
      videoElementRef.current = videoElement;
      setIsCameraReady(true);
    }
  }, []);

  /**
   * Handle camera error
   */
  const handleCameraError = useCallback((error: CameraError) => {
    if (onError) {
      onError(error);
    }
  }, [onError]);

  /**
   * Handle pose detection error
   */
  const handlePoseError = useCallback((error: Error) => {
    if (onError) {
      onError(error);
    }
  }, [onError]);

  return (
    <div className="workout-camera">
      {/* Camera Access */}
      <CameraAccess
        onStreamReady={handleStreamReady}
        onError={handleCameraError}
        width={width}
        height={height}
      />

      {/* Pose Detector */}
      {isCameraReady && showStatus && (
        <div className="mt-4">
          <PoseDetector
            videoElement={videoElementRef.current}
            onPoseDetected={onPoseDetected}
            onError={handlePoseError}
            enabled={true}
            targetFps={targetFps}
          />
        </div>
      )}

      {/* Hidden pose detector (no status display) */}
      {isCameraReady && !showStatus && (
        <div className="hidden">
          <PoseDetector
            videoElement={videoElementRef.current}
            onPoseDetected={onPoseDetected}
            onError={handlePoseError}
            enabled={true}
            targetFps={targetFps}
          />
        </div>
      )}
    </div>
  );
};

export default WorkoutCamera;
