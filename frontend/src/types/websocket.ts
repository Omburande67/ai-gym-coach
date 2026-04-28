/**
 * WebSocket message types for real-time workout tracking
 * 
 * Implements Requirements 14.1, 14.5, 14.6:
 * - Define message protocol for client-server communication
 * - Type-safe message handling
 */

import { PoseKeypoint } from "./pose";



export enum MessageType {
  // Client -> Server messages
  POSE_DATA = 'pose_data',
  PING = 'ping',
  SESSION_END = 'session_end',
  SET_EXERCISE = 'set_exercise',
  
  // Server -> Client messages
  EXERCISE_DETECTED = 'exercise_detected',
  REP_COUNTED = 'rep_counted',
  FORM_FEEDBACK = 'form_feedback',
  PONG = 'pong',
  ERROR = 'error',
  SESSION_SAVED = 'session_saved',
}

// Client -> Server Messages

export interface PoseDataMessage {
  type: MessageType.POSE_DATA;
  keypoints: PoseKeypoint[];
  timestamp: number;
}

export interface PingMessage {
  type: MessageType.PING;
}

export interface SessionEndMessage {
  type: MessageType.SESSION_END;
  timestamp: number;
}

export interface SetExerciseMessage {
  type: MessageType.SET_EXERCISE;
  exercise: string;
}

export type ClientMessage = PoseDataMessage | PingMessage | SessionEndMessage | SetExerciseMessage;

// Server -> Client Messages

export interface ExerciseDetectedMessage {
  type: MessageType.EXERCISE_DETECTED;
  exercise: string;
  confidence: number;
}

export interface RepCountedMessage {
  type: MessageType.REP_COUNTED;
  count: number;
  total: number;
}

export interface FormMistakeData {
  type: string;
  severity: number;
  suggestion: string;
}

export interface FormFeedbackMessage {
  type: MessageType.FORM_FEEDBACK;
  mistakes: FormMistakeData[];
  form_score: number;
}

export interface SessionSavedMessage {
  type: MessageType.SESSION_SAVED;
  session_id: string;
}

export interface PongMessage {
  type: MessageType.PONG;
}

export interface ErrorMessage {
  type: MessageType.ERROR;
  message: string;
  code?: string;
}

export type ServerMessage =
  | ExerciseDetectedMessage
  | RepCountedMessage
  | FormFeedbackMessage
  | PongMessage
  | ErrorMessage
  | SessionSavedMessage;

// WebSocket connection states
export enum WebSocketStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error',
}

// Feedback state for UI updates
export interface WorkoutFeedback {
  currentExercise: string | null;
  exerciseConfidence: number;
  repCount: number;
  totalReps: number;
  formScore: number;
  recentMistakes: FormMistakeData[];
}
