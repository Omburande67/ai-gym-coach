/**
 * WebSocket client for real-time workout tracking
 * 
 * Implements Requirements 14.1, 14.5, 14.6:
 * - Establish WebSocket connection on workout session start
 * - Send pose_data messages with keypoints
 * - Handle incoming feedback messages
 * - Automatic reconnection with exponential backoff
 * - Offline keypoint buffering
 */

import { PoseData } from '../types/pose';
import {
  MessageType,
  ClientMessage,
  ServerMessage,
  PoseDataMessage,
  PingMessage,
  ExerciseDetectedMessage,
  RepCountedMessage,
  FormFeedbackMessage,
  ErrorMessage,
  WebSocketStatus,
  WorkoutFeedback,
  SessionEndMessage,
  SessionSavedMessage
} from '../types/websocket';

export interface WebSocketClientConfig {
  url: string;
  userId: string;
  reconnectInterval?: number; // milliseconds
  maxReconnectAttempts?: number;
  bufferSize?: number; // max keypoints to buffer when offline
  pingInterval?: number; // milliseconds
}

export interface WebSocketClientCallbacks {
  onStatusChange?: (status: WebSocketStatus) => void;
  onExerciseDetected?: (exercise: string, confidence: number) => void;
  onRepCounted?: (count: number, total: number) => void;
  onFormFeedback?: (mistakes: any[], formScore: number) => void;
  onSessionSaved?: (sessionId: string) => void;
  onError?: (message: string, code?: string) => void;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketClientConfig>;
  private callbacks: WebSocketClientCallbacks;
  private status: WebSocketStatus = WebSocketStatus.DISCONNECTED;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingTimer: NodeJS.Timeout | null = null;
  private messageBuffer: PoseDataMessage[] = [];
  private isIntentionallyClosed = false;

  constructor(config: WebSocketClientConfig, callbacks: WebSocketClientCallbacks = {}) {
    this.config = {
      url: config.url,
      userId: config.userId,
      reconnectInterval: config.reconnectInterval ?? 5000,
      maxReconnectAttempts: config.maxReconnectAttempts ?? 10,
      bufferSize: config.bufferSize ?? 1000,
      pingInterval: config.pingInterval ?? 30000,
    };
    this.callbacks = callbacks;
  }

  /**
   * Connect to WebSocket server
   * Implements Requirement 14.1: Establish WebSocket connection
   */
  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.warn('WebSocket already connected or connecting');
      return;
    }

    this.isIntentionallyClosed = false;
    this.updateStatus(WebSocketStatus.CONNECTING);

    const wsUrl = `${this.config.url}/ws/${this.config.userId}`;
    console.log(`Connecting to WebSocket: ${wsUrl}`);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.updateStatus(WebSocketStatus.ERROR);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   * Implements Requirement 14.7: Gracefully close connection
   */
  public disconnect(): void {
    this.isIntentionallyClosed = true;
    this.clearTimers();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.updateStatus(WebSocketStatus.DISCONNECTED);
    this.reconnectAttempts = 0;
    this.messageBuffer = [];
  }

  /**
   * Send pose data to server
   * Implements Requirement 14.2: Transmit pose keypoints via WebSocket
   */
  public sendPoseData(poseData: PoseData): void {
    const message: PoseDataMessage = {
      type: MessageType.POSE_DATA,
      keypoints: poseData.keypoints,
      timestamp: poseData.timestamp,
    };

    if (this.isConnected()) {
      this.sendMessage(message);
      // If we have buffered messages, send them now
      this.flushBuffer();
    } else {
      // Buffer message for later transmission
      // Implements Requirement 14.4: Buffer keypoints when disconnected
      this.bufferMessage(message);
    }
  }

  /**
   * Send ping message for connection health check
   */
  public sendPing(): void {
    const message: PingMessage = {
      type: MessageType.PING,
    };
    this.sendMessage(message);
  }

  /**
   * End workout session
   */
  public endSession(): void {
    const message: SessionEndMessage = {
      type: MessageType.SESSION_END,
      timestamp: Date.now(),
    };
    this.sendMessage(message);
    // Connection will be closed by server or we can close it after some delay
  }

  /**
   * Check if WebSocket is connected
   */
  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get current connection status
   */
  public getStatus(): WebSocketStatus {
    return this.status;
  }

  /**
   * Get current buffer size
   */
  public getBufferSize(): number {
    return this.messageBuffer.length;
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.updateStatus(WebSocketStatus.CONNECTED);
      this.reconnectAttempts = 0;
      
      // Start ping timer
      this.startPingTimer();
      
      // Flush any buffered messages
      this.flushBuffer();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: ServerMessage = JSON.parse(event.data);
        this.handleServerMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.updateStatus(WebSocketStatus.ERROR);
    };

    this.ws.onclose = (event) => {
      console.log(`WebSocket closed: ${event.code} ${event.reason}`);
      this.clearTimers();
      
      if (!this.isIntentionallyClosed) {
        this.updateStatus(WebSocketStatus.DISCONNECTED);
        // Implements Requirement 14.3: Attempt reconnection every 5 seconds
        this.scheduleReconnect();
      }
    };
  }

  private handleServerMessage(message: ServerMessage): void {
    switch (message.type) {
      case MessageType.EXERCISE_DETECTED:
        this.handleExerciseDetected(message as ExerciseDetectedMessage);
        break;
      
      case MessageType.REP_COUNTED:
        this.handleRepCounted(message as RepCountedMessage);
        break;
      
      case MessageType.FORM_FEEDBACK:
        this.handleFormFeedback(message as FormFeedbackMessage);
        break;
      
      case MessageType.PONG:
        // Connection health check response
        console.debug('Received pong');
        break;
      
      case MessageType.ERROR:
        this.handleError(message as ErrorMessage);
        break;
      
      case MessageType.SESSION_SAVED:
        this.handleSessionSaved(message as SessionSavedMessage);
        break;
      
      default:
        console.warn('Unknown message type:', message);
    }
  }

  private handleExerciseDetected(message: ExerciseDetectedMessage): void {
    console.log(`Exercise detected: ${message.exercise} (${message.confidence})`);
    if (this.callbacks.onExerciseDetected) {
      this.callbacks.onExerciseDetected(message.exercise, message.confidence);
    }
  }

  private handleRepCounted(message: RepCountedMessage): void {
    console.log(`Rep counted: ${message.count} (total: ${message.total})`);
    if (this.callbacks.onRepCounted) {
      this.callbacks.onRepCounted(message.count, message.total);
    }
  }

  private handleFormFeedback(message: FormFeedbackMessage): void {
    console.log(`Form feedback: ${message.mistakes.length} mistakes, score: ${message.form_score}`);
    if (this.callbacks.onFormFeedback) {
      this.callbacks.onFormFeedback(message.mistakes, message.form_score);
    }
  }

  private handleSessionSaved(message: SessionSavedMessage): void {
    console.log(`Workout session saved: ${message.session_id}`);
    if (this.callbacks.onSessionSaved) {
      this.callbacks.onSessionSaved(message.session_id);
    }
  }

  private handleError(message: ErrorMessage): void {
    console.error(`Server error: ${message.message} (${message.code})`);
    if (this.callbacks.onError) {
      this.callbacks.onError(message.message, message.code);
    }
  }

  private sendMessage(message: ClientMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send message: WebSocket not connected');
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }

  private bufferMessage(message: PoseDataMessage): void {
    if (this.messageBuffer.length >= this.config.bufferSize) {
      // Remove oldest message to make room
      this.messageBuffer.shift();
    }
    this.messageBuffer.push(message);
    console.debug(`Buffered message (${this.messageBuffer.length}/${this.config.bufferSize})`);
  }

  private flushBuffer(): void {
    if (this.messageBuffer.length === 0) return;

    console.log(`Flushing ${this.messageBuffer.length} buffered messages`);
    
    while (this.messageBuffer.length > 0 && this.isConnected()) {
      const message = this.messageBuffer.shift();
      if (message) {
        this.sendMessage(message);
      }
    }
  }

  private scheduleReconnect(): void {
    if (this.isIntentionallyClosed) return;
    
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.updateStatus(WebSocketStatus.ERROR);
      return;
    }

    this.reconnectAttempts++;
    this.updateStatus(WebSocketStatus.RECONNECTING);
    
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts} in ${this.config.reconnectInterval}ms`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.config.reconnectInterval);
  }

  private startPingTimer(): void {
    this.pingTimer = setInterval(() => {
      if (this.isConnected()) {
        this.sendPing();
      }
    }, this.config.pingInterval);
  }

  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private updateStatus(status: WebSocketStatus): void {
    this.status = status;
    if (this.callbacks.onStatusChange) {
      this.callbacks.onStatusChange(status);
    }
  }
}
