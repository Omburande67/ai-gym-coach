/**
 * React hook for WebSocket workout session management
 * 
 * Implements Requirements 14.1, 14.5, 14.6:
 * - Manage WebSocket connection lifecycle
 * - Update UI with real-time feedback
 * - Handle connection status changes
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { PoseData } from '../types/pose';
import {
  WebSocketStatus,
  WorkoutFeedback,
  FormMistakeData,
} from '../types/websocket';
import { WebSocketClient, WebSocketClientConfig } from './websocket-client';

export interface UseWorkoutWebSocketOptions {
  url: string;
  userId: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onSessionSaved?: (sessionId: string) => void;
}

export interface UseWorkoutWebSocketReturn {
  // Connection state
  status: WebSocketStatus;
  isConnected: boolean;
  bufferSize: number;
  
  // Workout feedback
  feedback: WorkoutFeedback;
  
  // Actions
  connect: () => void;
  disconnect: () => void;
  endSession: () => void;
  sendPoseData: (poseData: PoseData) => void;
  
  // Error state
  error: { message: string; code?: string } | null;
}

const initialFeedback: WorkoutFeedback = {
  currentExercise: null,
  exerciseConfidence: 0,
  repCount: 0,
  totalReps: 0,
  formScore: 100,
  recentMistakes: [],
};

/**
 * Hook for managing WebSocket connection during workout sessions
 * 
 * @param options - Configuration options
 * @returns WebSocket state and control functions
 */
export function useWorkoutWebSocket(
  options: UseWorkoutWebSocketOptions
): UseWorkoutWebSocketReturn {
  const [status, setStatus] = useState<WebSocketStatus>(WebSocketStatus.DISCONNECTED);
  const [feedback, setFeedback] = useState<WorkoutFeedback>(initialFeedback);
  const [error, setError] = useState<{ message: string; code?: string } | null>(null);
  const [bufferSize, setBufferSize] = useState(0);
  
  const clientRef = useRef<WebSocketClient | null>(null);
  const bufferCheckInterval = useRef<NodeJS.Timeout | null>(null);

  // Initialize WebSocket client
  useEffect(() => {
    const config: WebSocketClientConfig = {
      url: options.url,
      userId: options.userId,
      reconnectInterval: options.reconnectInterval,
      maxReconnectAttempts: options.maxReconnectAttempts,
    };

    const client = new WebSocketClient(config, {
      onStatusChange: (newStatus) => {
        setStatus(newStatus);
        
        // Clear error when connected
        if (newStatus === WebSocketStatus.CONNECTED) {
          setError(null);
        }
      },
      
      onExerciseDetected: (exercise, confidence) => {
        setFeedback((prev) => ({
          ...prev,
          currentExercise: exercise,
          exerciseConfidence: confidence,
          // Reset rep count when exercise changes
          repCount: 0,
        }));
      },
      
      onRepCounted: (count, total) => {
        setFeedback((prev) => ({
          ...prev,
          repCount: count,
          totalReps: total,
        }));
      },
      
      onFormFeedback: (mistakes, formScore) => {
        setFeedback((prev) => ({
          ...prev,
          formScore,
          recentMistakes: mistakes,
        }));
      },
      
      onSessionSaved: (sessionId) => {
        if (options.onSessionSaved) {
          options.onSessionSaved(sessionId);
        }
      },
      
      onError: (message, code) => {
        setError({ message, code });
      },
    });

    clientRef.current = client;

    // Auto-connect if enabled
    if (options.autoConnect) {
      client.connect();
    }

    // Start buffer size monitoring
    bufferCheckInterval.current = setInterval(() => {
      if (clientRef.current) {
        setBufferSize(clientRef.current.getBufferSize());
      }
    }, 1000);

    // Cleanup on unmount
    return () => {
      if (bufferCheckInterval.current) {
        clearInterval(bufferCheckInterval.current);
      }
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, [options.url, options.userId, options.autoConnect, options.reconnectInterval, options.maxReconnectAttempts]);

  const connect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.connect();
    }
  }, []);

  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
      // Reset feedback state
      setFeedback(initialFeedback);
      setError(null);
    }
  }, []);

  const endSession = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.endSession();
    }
  }, []);

  const sendPoseData = useCallback((poseData: PoseData) => {
    if (clientRef.current) {
      clientRef.current.sendPoseData(poseData);
    }
  }, []);

  const isConnected = status === WebSocketStatus.CONNECTED;

  return {
    status,
    isConnected,
    bufferSize,
    feedback,
    connect,
    disconnect,
    endSession,
    sendPoseData,
    error,
  };
}
