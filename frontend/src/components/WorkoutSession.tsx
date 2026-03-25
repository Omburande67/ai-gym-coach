/**
 * Workout Session Component
 * 
 * Demonstrates WebSocket integration with pose detection
 * Implements Requirements 14.1, 14.5, 14.6:
 * - Connect WebSocket on workout start
 * - Send pose data to backend
 * - Display real-time feedback
 */

'use client';

import React, { useRef, useEffect, useState } from 'react';
import { PoseDetector } from './PoseDetector';
import { SkeletonOverlay } from './SkeletonOverlay';
import { CameraPlacementTutorial, ExerciseType } from './CameraPlacementTutorial';
import { PoseData } from '../types/pose';
import { useWorkoutWebSocket } from '../lib/useWorkoutWebSocket';
import { WebSocketStatus } from '../types/websocket';
import { checkFullBodyVisibility, getVisibilityWarningMessage, VisibilityStatus } from '../utils/visibility';
import { WorkoutSummary } from './WorkoutSummary';
import { WorkoutSummaryData } from '../types/workout';
import { fetchWorkoutSummary } from '../lib/api';

export interface WorkoutSessionProps {
  userId: string;
  websocketUrl?: string;
  onSessionEnd?: () => void;
}

export function WorkoutSession({
  userId,
  websocketUrl = 'ws://127.0.0.1:8000',
  onSessionEnd,
}: WorkoutSessionProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [currentPose, setCurrentPose] = useState<PoseData | null>(null);
  const [videoDimensions, setVideoDimensions] = useState({ width: 640, height: 480 });
  const [showTutorial, setShowTutorial] = useState(false);
  const [hasSeenTutorial, setHasSeenTutorial] = useState(false);
  const [visibilityStatus, setVisibilityStatus] = useState<VisibilityStatus | null>(null);
  const [isTrackingPaused, setIsTrackingPaused] = useState(false);
  const [workoutSummary, setWorkoutSummary] = useState<WorkoutSummaryData | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // WebSocket connection
  const {
    status,
    isConnected,
    bufferSize,
    feedback,
    connect,
    disconnect,
    endSession: callEndSession,
    sendPoseData,
    error,
  } = useWorkoutWebSocket({
    url: websocketUrl,
    userId,
    autoConnect: false,
    onSessionSaved: async (sessionId) => {
      try {
        const summary = await fetchWorkoutSummary(sessionId);
        setWorkoutSummary(summary);
        setIsSaving(false);
      } catch (err) {
        console.error('Failed to fetch summary:', err);
        setIsSaving(false);
        // Fallback or error state
      }
    }
  });

  // Handle pose detection
  const handlePoseDetected = (poseData: PoseData) => {
    setCurrentPose(poseData);
    
    // Check visibility status (Requirement 5.5)
    const visibility = checkFullBodyVisibility(poseData);
    setVisibilityStatus(visibility);
    
    // Pause tracking if user is not fully visible (Requirement 5.5)
    if (!visibility.isFullyVisible) {
      setIsTrackingPaused(true);
      return; // Don't send pose data when user is out of frame
    } else {
      setIsTrackingPaused(false);
    }
    
    // Only send pose data if tracking is not paused and connected
    if (isActive && isConnected && !isTrackingPaused) {
      sendPoseData(poseData);
    }
  };

  // Check if user has seen tutorial before (using localStorage)
  useEffect(() => {
    const tutorialSeen = localStorage.getItem(`workout-tutorial-seen-${userId}`);
    setHasSeenTutorial(tutorialSeen === 'true');
  }, [userId]);

  // Show tutorial on first workout session
  useEffect(() => {
    if (!hasSeenTutorial && !isActive && !showTutorial) {
      // Don't show immediately, wait for user to click start
    }
  }, [hasSeenTutorial, isActive, showTutorial]);

  // Update video dimensions when video loads
  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      const updateDimensions = () => {
        setVideoDimensions({
          width: video.videoWidth || 640,
          height: video.videoHeight || 480,
        });
      };
      
      video.addEventListener('loadedmetadata', updateDimensions);
      return () => video.removeEventListener('loadedmetadata', updateDimensions);
    }
  }, [stream]);

  // Start workout session
  const startSession = async () => {
    // Show tutorial if first time
    if (!hasSeenTutorial) {
      setShowTutorial(true);
      return;
    }

    await startWorkout();
  };

  // Actually start the workout (after tutorial or if already seen)
  const startWorkout = async () => {
    try {
      // Request camera access
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
      });

      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }

      // Connect WebSocket
      connect();
      setIsActive(true);
    } catch (error: any) {
      console.error('Failed to start workout session:', error);
      
      let errorMessage = 'Failed to access camera. Please check your system settings.';
      let errorTitle = 'Camera Access Failed';

      if (error.name === 'NotAllowedError') {
        errorMessage = 'Camera permission denied. Please allow camera access in your browser settings to start the workout.';
        errorTitle = 'Permission Denied';
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorMessage = 'No camera found on your device. Please connect a webcam and try again.';
        errorTitle = 'Camera Not Found';
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        errorMessage = 'Camera is already in use by another application. Please close other apps using the camera and try again.';
        errorTitle = 'Camera In Use';
      } else if (error.name === 'OverconstrainedError') {
        errorMessage = 'Camera constraints could not be satisfied. Using default settings.';
        // Attempt to restart with default settings
        try {
          const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
          setStream(mediaStream);
          if (videoRef.current) videoRef.current.srcObject = mediaStream;
          connect();
          setIsActive(true);
          return;
        } catch (retryError) {
          console.error('Retry failed:', retryError);
        }
      }

      // Instead of alert, we'll let the error be displayed in the UI via the error property from useWorkoutWebSocket or a local state
      // Actually, let's use a local state for camera errors since useWorkoutWebSocket is for WS errors
      alert(`${errorTitle}: ${errorMessage}`);
    }
  };

  // Handle tutorial completion
  const handleTutorialComplete = () => {
    setShowTutorial(false);
    setHasSeenTutorial(true);
    localStorage.setItem(`workout-tutorial-seen-${userId}`, 'true');
    startWorkout();
  };

  // End workout session
  const endSession = async () => {
    setIsSaving(true);
    
    // Signal end to WebSocket for persistence
    callEndSession();
    
    // Stop camera
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }

    setIsActive(false);

    // Note: onSessionEnd will be called when user closes the summary modal
  };

  const handleCloseSummary = () => {
    setWorkoutSummary(null);
    if (onSessionEnd) {
      onSessionEnd();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  // Get status color
  const getStatusColor = () => {
    switch (status) {
      case WebSocketStatus.CONNECTED:
        return 'bg-green-500';
      case WebSocketStatus.CONNECTING:
      case WebSocketStatus.RECONNECTING:
        return 'bg-yellow-500';
      case WebSocketStatus.DISCONNECTED:
        return 'bg-gray-500';
      case WebSocketStatus.ERROR:
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="flex flex-col items-center gap-6 p-4 w-full max-w-7xl mx-auto">
      <div className="w-full flex justify-between items-center bg-white/5 p-6 rounded-2xl border border-white/10 glass-card">
        <div>
           <h1 className="text-3xl font-black gradient-text-neural">Live Tracking</h1>
           <p className="text-gray-400 text-sm">AI-Powered Biometric Session</p>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center gap-4 bg-white/5 px-4 py-2 rounded-full border border-white/10">
          <div className={`w-3 h-3 rounded-full animate-pulse ${getStatusColor()}`} />
          <span className="text-sm font-bold text-gray-300">
            {status === WebSocketStatus.CONNECTED && (
              <span className="flex items-center gap-2">
                <i className="bi bi-broadcast"></i> ONLINE
              </span>
            )}
            {status === WebSocketStatus.CONNECTING && (
              <span className="flex items-center gap-2 text-yellow-500">
                <i className="bi bi-hourglass-split animate-spin"></i> CONNECTING...
              </span>
            )}
            {status === WebSocketStatus.RECONNECTING && (
              <span className="flex items-center gap-2 text-yellow-500">
                <i className="bi bi-arrow-clockwise animate-spin"></i> RECONNECTING...
              </span>
            )}
            {status === WebSocketStatus.DISCONNECTED && (
              <span className="flex items-center gap-2">
                <i className="bi bi-plug"></i> OFFLINE
              </span>
            )}
            {status === WebSocketStatus.ERROR && (
              <span className="flex items-center gap-2 text-red-500">
                <i className="bi bi-exclamation-triangle-fill"></i> ERROR
              </span>
            )}
          </span>
          {bufferSize > 0 && (
            <span className="text-[10px] text-gray-500 border border-white/10 px-1 rounded uppercase font-mono">
              BUF: {bufferSize}
            </span>
          )}
        </div>
      </div>

      {/* Workout Summary Overlay */}
      {workoutSummary && (
        <WorkoutSummary 
          summary={workoutSummary} 
          onClose={handleCloseSummary} 
        />
      )}

      {/* Saving State */}
      {isSaving && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-md">
          <div className="glass-card p-12 flex flex-col items-center">
            <div className="spinner w-16 h-16 mb-6"></div>
            <p className="text-white font-black text-xl tracking-widest uppercase flex items-center gap-3">
              <i className="bi bi-cloud-arrow-up text-blue-400"></i> Analyzing & Saving
            </p>
            <p className="text-gray-400 text-sm mt-2 font-mono">Uploading biometric data sequence...</p>
          </div>
        </div>
      )}

      {/* Camera Placement Tutorial */}
      <CameraPlacementTutorial
        isOpen={showTutorial}
        onClose={() => setShowTutorial(false)}
        onComplete={handleTutorialComplete}
        exerciseType={feedback.currentExercise as ExerciseType | undefined}
      />

      {/* Error Display */}
      {error && (
        <div className="w-full bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-4 rounded-2xl flex items-center gap-4 animate-in slide-in-from-top duration-500">
          <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
             <i className="bi bi-exclamation-octagon text-xl"></i>
          </div>
          <div>
            <strong className="block">Hardware Link Failure</strong> 
            <span className="text-sm">{error.message}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full h-full">
        {/* Left: Video Area */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="relative glass-card overflow-hidden border border-white/20 shadow-2xl shadow-blue-500/5 group">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full aspect-video object-cover"
              style={{ transform: 'scaleX(-1)' }}
            />
            
            {/* Overlay Gradient for tech feel */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20 pointer-events-none" />
            
            {/* Tracking Status Badge */}
            <div className="absolute top-6 left-6 z-30">
               <div className="glass-card px-4 py-2 flex items-center gap-3 border-blue-500/30">
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
                  <span className="text-xs font-black text-blue-400 tracking-wider flex items-center gap-2">
                    <i className="bi bi-activity"></i> REAL-TIME BIOMETRICS
                  </span>
               </div>
            </div>

            {/* Visibility Warning Overlay */}
            {visibilityStatus && !visibilityStatus.isFullyVisible && (
              <div className="absolute inset-0 z-40 bg-yellow-900/40 backdrop-blur-[2px] flex items-center justify-center p-8 animate-in fade-in transition-all">
                <div className="glass-card border-yellow-500/50 p-8 max-w-lg text-center shadow-2xl">
                  <div className="w-20 h-20 rounded-full bg-yellow-500/20 flex items-center justify-center mx-auto mb-6 border border-yellow-500/30">
                    <i className="bi bi-person-bounding-box text-5xl text-yellow-500"></i>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-2 uppercase tracking-tight">Biometric Link Lost</h3>
                  <p className="text-yellow-200 text-sm leading-relaxed mb-6">
                    {getVisibilityWarningMessage(visibilityStatus)}
                  </p>
                  <div className="text-[10px] text-yellow-500/80 font-mono">
                    ACTIVE SENSORS: {visibilityStatus.visibleKeypointsCount} / {visibilityStatus.totalKeypointsCount}
                  </div>
                </div>
              </div>
            )}

            {isActive && videoRef.current && (
              <>
                <PoseDetector
                  videoElement={videoRef.current}
                  onPoseDetected={handlePoseDetected}
                  enabled={isActive}
                />
                <SkeletonOverlay
                  poseData={currentPose}
                  width={videoDimensions.width}
                  height={videoDimensions.height}
                />
              </>
            )}
            
            {/* Local Stats Bar */}
            <div className="absolute bottom-6 left-6 right-6 z-30 flex justify-between items-end">
               <div className="space-y-1">
                  <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest flex items-center gap-1">
                    <i className="bi bi-person-badge"></i> User ID
                  </div>
                  <div className="text-sm text-white font-mono">{userId}</div>
               </div>
               <div className="flex gap-4">
                  <div className="glass-card px-4 py-2 border-white/5">
                     <span className="text-[10px] text-gray-500 block uppercase font-bold">Latency</span>
                     <span className="text-xs text-white font-mono flex items-center gap-1">
                       <i className="bi bi-reception-4 text-blue-400"></i> 14ms
                     </span>
                  </div>
                  <div className="glass-card px-4 py-2 border-white/5">
                     <span className="text-[10px] text-gray-500 block uppercase font-bold">FPS</span>
                     <span className="text-xs text-white font-mono flex items-center gap-1">
                        <i className="bi bi-speedometer2 text-cyan-400"></i> 30
                     </span>
                  </div>
               </div>
            </div>
          </div>

          {/* Controls Bar */}
          <div className="glass-card p-4 flex gap-4" role="group" aria-label="Session Controls">
            {!isActive ? (
              <>
                <button
                  onClick={startSession}
                  className="glow-button flex-1 py-4 text-lg font-black tracking-widest uppercase flex items-center justify-center gap-3"
                  aria-label="Initialize workout session"
                >
                  <i className="bi bi-play-circle-fill" aria-hidden="true"></i> INITIALIZE SESSION
                </button>
                <button
                  onClick={() => setShowTutorial(true)}
                  className="glass-card px-8 py-4 text-sm font-bold text-gray-300 hover:text-white border-white/10 hover:border-white/30 transition-all uppercase flex items-center gap-2"
                  aria-label="View hardware setup guide"
                >
                  <i className="bi bi-gear-wide-connected" aria-hidden="true"></i> Setup
                </button>
              </>
            ) : (
              <button
                onClick={endSession}
                className="w-full py-4 bg-red-500/20 text-red-500 hover:bg-red-500/30 border border-red-500/30 rounded-xl font-black tracking-widest uppercase transition-all flex items-center justify-center gap-3"
                aria-label="Terminate current workout session"
              >
                <i className="bi bi-stop-circle-fill" aria-hidden="true"></i> TERMINATE SESSION
              </button>
            )}
          </div>
        </div>

        {/* Right: Feedback Area */}
        <div className="lg:col-span-4 flex flex-col gap-6" aria-live="polite">
          {/* Main Feedback Card */}
          <div className="glass-card p-6 flex-1 flex flex-col gap-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 group-hover:scale-125 transition-all duration-700">
               <i className="bi bi-cpu text-8xl text-white" aria-hidden="true"></i>
            </div>

            <div className="space-y-6">
              <h2 className="text-xl font-black text-white tracking-tight flex items-center gap-3">
                 <div className="w-2 h-6 bg-blue-500 rounded-full" aria-hidden="true" />
                 <i className="bi bi-graph-up-arrow" aria-hidden="true"></i> SESSION DATA
              </h2>
              
              <div className="grid grid-cols-2 gap-4">
                {/* Exercise Detection */}
                <div className="bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-all flex flex-col">
                  <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1">
                    <i className="bi bi-person-walking"></i> Exercise
                  </div>
                  <div className="text-lg font-black text-white truncate">
                    {(feedback.currentExercise || '---').replace(/_/g, ' ')}
                  </div>
                  {feedback.currentExercise && (
                    <div className="text-[10px] text-blue-400 font-mono mt-auto pt-1">
                      CONF: {(feedback.exerciseConfidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>

                {/* Rep Count */}
                <div className="bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-all flex flex-col">
                  <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1">
                    <i className="bi bi-repeat"></i> Reps
                  </div>
                  <div className="text-2xl font-black text-white">
                    {feedback.repCount}
                  </div>
                  <div className="text-[10px] text-gray-500 font-bold uppercase mt-auto pt-1">
                    TOTAL: {feedback.totalReps}
                  </div>
                </div>

                {/* Form Score */}
                <div className="bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-all flex flex-col">
                  <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1">
                    <i className="bi bi-shield-check"></i> Form
                  </div>
                  <div className={`text-2xl font-black ${getScoreColor(feedback.formScore)}`}>
                    {feedback.formScore.toFixed(0)}
                  </div>
                  <div className="text-[10px] text-gray-500 font-bold uppercase mt-auto pt-1">
                    {feedback.formScore >= 90 ? 'PERFECT' : feedback.formScore >= 70 ? 'STABLE' : 'UNSTABLE'}
                  </div>
                </div>

                {/* Mistakes */}
                <div className="bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-all flex flex-col">
                  <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1">
                    <i className="bi bi-megaphone"></i> Alerts
                  </div>
                  <div className="text-2xl font-black text-orange-400">
                    {feedback.recentMistakes.length}
                  </div>
                  <div className="text-[10px] text-gray-500 font-bold uppercase mt-auto pt-1">
                    DETECTED
                  </div>
                </div>
              </div>
            </div>

            {/* Form Suggestions */}
            <div className="flex-1 space-y-4">
              <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                 <i className="bi bi-chat-quote"></i> COACH FEEDBACK
                 <div className="flex-1 h-[1px] bg-white/10" />
              </h3>
              
              <div className="space-y-3 h-[200px] overflow-y-auto pr-2 custom-scrollbar">
                {feedback.recentMistakes.length > 0 ? (
                  feedback.recentMistakes.map((mistake, index) => (
                    <div
                      key={index}
                      className="bg-orange-500/10 p-4 rounded-2xl border border-orange-500/20 animate-in slide-in-from-right duration-500"
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-[10px] font-black text-orange-400 uppercase tracking-widest flex items-center gap-1">
                          <i className="bi bi-exclamation-circle"></i> {mistake.type.replace(/_/g, ' ')}
                        </span>
                        <span className="text-[8px] text-orange-500/60 font-mono">SEV: {(mistake.severity * 100).toFixed(0)}</span>
                      </div>
                      <p className="text-sm text-gray-300 font-bold leading-tight">
                        {mistake.suggestion}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center opacity-30 grayscale hover:opacity-50 transition-all cursor-default">
                    <i className="bi bi-shield-check text-4xl mb-2"></i>
                    <p className="text-xs font-bold uppercase tracking-widest">Awaiting Form Data</p>
                    <p className="text-[10px]">No bio-mechanical errors detected</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
