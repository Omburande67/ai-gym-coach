'use client';

import React, { useState, useRef, useCallback } from 'react';
import { CameraAccess, useCameraAccess } from '@/components/CameraAccess';
import { PoseDetector, usePoseDetection } from '@/components/PoseDetector';
import { SkeletonOverlay } from '@/components/SkeletonOverlay';
import type { PoseData } from '@/types/pose';

/**
 * Pose Detection Demo Page
 * 
 * Demonstrates the integration of CameraAccess and PoseDetector components.
 * Shows real-time pose detection with keypoint visualization.
 */
export default function PoseDemoPage() {
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  
  const [detectionEnabled, setDetectionEnabled] = useState(true);
  const [latestPose, setLatestPose] = useState<PoseData | null>(null);
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [showKeypoints, setShowKeypoints] = useState(true);
  const [showConnections, setShowConnections] = useState(true);

  const { stream, error: cameraError, handleStreamReady, handleError: handleCameraError } = useCameraAccess();
  const { error: poseError, handlePoseDetected, handleError: handlePoseError } = usePoseDetection(
    videoElementRef.current,
    { enabled: detectionEnabled, targetFps: 15 }
  );

  /**
   * Handle camera stream ready
   */
  const onStreamReady = useCallback((mediaStream: MediaStream) => {
    handleStreamReady(mediaStream);
    
    // Get video element from CameraAccess component
    const videoElement = document.querySelector('video') as HTMLVideoElement;
    if (videoElement) {
      videoElementRef.current = videoElement;
    }
  }, [handleStreamReady]);

  /**
   * Handle pose detected
   */
  const onPoseDetected = useCallback((data: PoseData) => {
    handlePoseDetected(data);
    setLatestPose(data);
  }, [handlePoseDetected]);

  /**
   * Get keypoint statistics
   */
  const getKeypointStats = () => {
    if (!latestPose) return null;

    const visibleKeypoints = latestPose.keypoints.filter((kp) => kp.visibility > 0.5);
    const avgVisibility = latestPose.keypoints.reduce((sum, kp) => sum + kp.visibility, 0) / latestPose.keypoints.length;

    return {
      total: latestPose.keypoints.length,
      visible: visibleKeypoints.length,
      avgVisibility: avgVisibility.toFixed(2),
    };
  };

  const stats = getKeypointStats();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Pose Detection Demo
          </h1>
          <p className="text-gray-600">
            Real-time pose detection using TensorFlow.js and MediaPipe BlazePose
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Camera and Pose Visualization */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Camera Feed</h2>
              
              <div className="relative">
                <CameraAccess
                  onStreamReady={onStreamReady}
                  onError={handleCameraError}
                  width={640}
                  height={480}
                />
                
                {/* Skeleton overlay */}
                {showSkeleton && stream && (
                  <SkeletonOverlay
                    poseData={latestPose}
                    width={640}
                    height={480}
                    showKeypoints={showKeypoints}
                    showConnections={showConnections}
                    minVisibility={0.3}
                    keypointRadius={5}
                    lineWidth={2}
                  />
                )}
              </div>

              {/* Controls */}
              <div className="mt-4 space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={detectionEnabled}
                    onChange={(e) => setDetectionEnabled(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Enable Detection</span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showSkeleton}
                    onChange={(e) => setShowSkeleton(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Show Skeleton Overlay</span>
                </label>

                {showSkeleton && (
                  <div className="ml-6 space-y-2">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={showKeypoints}
                        onChange={(e) => setShowKeypoints(e.target.checked)}
                        className="rounded"
                      />
                      <span className="text-sm">Show Keypoints</span>
                    </label>

                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={showConnections}
                        onChange={(e) => setShowConnections(e.target.checked)}
                        className="rounded"
                      />
                      <span className="text-sm">Show Connections</span>
                    </label>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Status and Information */}
          <div className="space-y-4">
            {/* Pose Detector Status */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Detection Status</h2>
              
              <PoseDetector
                videoElement={videoElementRef.current}
                onPoseDetected={onPoseDetected}
                onError={handlePoseError}
                enabled={detectionEnabled}
                targetFps={15}
              />

              {/* Errors */}
              {(cameraError || poseError) && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-red-800 text-sm font-semibold">Error</p>
                  <p className="text-red-700 text-xs">
                    {cameraError?.message || poseError?.message}
                  </p>
                </div>
              )}
            </div>

            {/* Keypoint Statistics */}
            {stats && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Keypoint Stats</h2>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Keypoints:</span>
                    <span className="font-semibold">{stats.total}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Visible:</span>
                    <span className="font-semibold">{stats.visible}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Visibility:</span>
                    <span className="font-semibold">{stats.avgVisibility}</span>
                  </div>
                </div>

                {/* Visibility bar */}
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all"
                      style={{ width: `${parseFloat(stats.avgVisibility) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Latest Pose Data */}
            {latestPose && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Latest Pose</h2>
                
                <div className="text-xs text-gray-600 mb-2">
                  Timestamp: {new Date(latestPose.timestamp).toLocaleTimeString()}
                </div>

                <div className="max-h-64 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="text-left p-2">Joint</th>
                        <th className="text-right p-2">Vis</th>
                      </tr>
                    </thead>
                    <tbody>
                      {latestPose.keypoints
                        .filter((kp) => kp.visibility > 0.3)
                        .map((kp, idx) => (
                          <tr key={idx} className="border-t">
                            <td className="p-2">{kp.name}</td>
                            <td className="text-right p-2">
                              {(kp.visibility * 100).toFixed(0)}%
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            How to Use
          </h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Click &quot;Enable Camera&quot; to start the camera feed</li>
            <li>Position yourself 2-3 meters from the camera</li>
            <li>Ensure your full body is visible in the frame</li>
            <li>The system will detect 33 keypoints on your body</li>
            <li>Keypoints are color-coded: Green (high confidence), Yellow (medium), Red (low)</li>
            <li>Toggle skeleton overlay, keypoints, and connections independently</li>
            <li>Toggle detection on/off to see performance impact</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
