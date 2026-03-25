/**
 * Unit tests for WebSocket client
 * 
 * Tests Requirements 14.1, 14.3, 14.4, 14.5, 14.6:
 * - WebSocket connection establishment
 * - Reconnection logic
 * - Message buffering when offline
 * - Message sending and receiving
 */

import { WebSocketClient } from './websocket-client';
import { MessageType, WebSocketStatus } from '../types/websocket';
import { PoseData, PoseKeypoint } from '../types/pose';

// Mock WebSocket
class MockWebSocket {
  public readyState: number = WebSocket.CONNECTING;
  public onopen: ((event: Event) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;
  
  private sentMessages: string[] = [];

  constructor(public url: string) {}

  send(data: string): void {
    this.sentMessages.push(data);
  }

  close(code?: number, reason?: string): void {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }));
    }
  }

  // Test helpers
  simulateOpen(): void {
    this.readyState = WebSocket.OPEN;
    if (this.onopen) {
      this.onopen(new Event('open'));
    }
  }

  simulateMessage(data: any): void {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }));
    }
  }

  simulateError(): void {
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }

  simulateClose(code: number = 1000, reason: string = ''): void {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }));
    }
  }

  getSentMessages(): any[] {
    return this.sentMessages.map(msg => JSON.parse(msg));
  }

  getLastSentMessage(): any {
    const messages = this.getSentMessages();
    return messages[messages.length - 1];
  }
}

// Mock global WebSocket
let mockWebSocketInstance: MockWebSocket | null = null;
(global as any).WebSocket = class {
  constructor(url: string) {
    mockWebSocketInstance = new MockWebSocket(url);
    return mockWebSocketInstance;
  }
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
};

describe('WebSocketClient', () => {
  let client: WebSocketClient;
  let statusChanges: WebSocketStatus[] = [];
  let exerciseDetections: Array<{ exercise: string; confidence: number }> = [];
  let repCounts: Array<{ count: number; total: number }> = [];
  let formFeedbacks: Array<{ mistakes: any[]; formScore: number }> = [];
  let errors: Array<{ message: string; code?: string }> = [];

  beforeEach(() => {
    jest.useFakeTimers();
    mockWebSocketInstance = null;
    statusChanges = [];
    exerciseDetections = [];
    repCounts = [];
    formFeedbacks = [];
    errors = [];

    client = new WebSocketClient(
      {
        url: 'ws://localhost:8000',
        userId: 'test-user',
        reconnectInterval: 5000,
        maxReconnectAttempts: 3,
        bufferSize: 10,
      },
      {
        onStatusChange: (status) => statusChanges.push(status),
        onExerciseDetected: (exercise, confidence) => 
          exerciseDetections.push({ exercise, confidence }),
        onRepCounted: (count, total) => 
          repCounts.push({ count, total }),
        onFormFeedback: (mistakes, formScore) => 
          formFeedbacks.push({ mistakes, formScore }),
        onError: (message, code) => 
          errors.push({ message, code }),
      }
    );
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
    if (client) {
      client.disconnect();
    }
  });

  describe('Connection Management', () => {
    test('should establish WebSocket connection', () => {
      client.connect();

      expect(mockWebSocketInstance).not.toBeNull();
      expect(mockWebSocketInstance!.url).toBe('ws://localhost:8000/ws/test-user');
      expect(statusChanges).toContain(WebSocketStatus.CONNECTING);
    });

    test('should update status to connected when connection opens', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();

      expect(statusChanges).toContain(WebSocketStatus.CONNECTED);
      expect(client.isConnected()).toBe(true);
    });

    test('should disconnect gracefully', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();
      
      client.disconnect();

      expect(statusChanges).toContain(WebSocketStatus.DISCONNECTED);
      expect(client.isConnected()).toBe(false);
    });

    test('should not reconnect after intentional disconnect', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();
      client.disconnect();

      // Advance timers to trigger reconnect attempt
      jest.advanceTimersByTime(6000);

      // Should not have created a new WebSocket
      expect(statusChanges.filter(s => s === WebSocketStatus.RECONNECTING)).toHaveLength(0);
    });
  });

  describe('Reconnection Logic', () => {
    test('should attempt reconnection when connection closes unexpectedly', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();
      mockWebSocketInstance!.simulateClose(1006, 'Abnormal closure');

      expect(statusChanges).toContain(WebSocketStatus.DISCONNECTED);

      // Advance timer to trigger reconnect
      jest.advanceTimersByTime(5000);

      expect(statusChanges).toContain(WebSocketStatus.RECONNECTING);
    });

    test('should stop reconnecting after max attempts', () => {
      client.connect();
      
      // Simulate 3 failed connection attempts
      for (let i = 0; i < 3; i++) {
        mockWebSocketInstance!.simulateClose(1006);
        jest.advanceTimersByTime(5000);
      }

      // After 3 attempts, should give up
      mockWebSocketInstance!.simulateClose(1006);
      jest.advanceTimersByTime(5000);

      expect(statusChanges).toContain(WebSocketStatus.ERROR);
    });
  });

  describe('Message Sending', () => {
    test('should send pose data when connected', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();

      const poseData: PoseData = {
        keypoints: [
          { x: 0.5, y: 0.5, z: 0, visibility: 0.9, name: 'nose' },
        ],
        timestamp: Date.now(),
      };

      client.sendPoseData(poseData);

      const sentMessage = mockWebSocketInstance!.getLastSentMessage();
      expect(sentMessage.type).toBe(MessageType.POSE_DATA);
      expect(sentMessage.keypoints).toEqual(poseData.keypoints);
      expect(sentMessage.timestamp).toBe(poseData.timestamp);
    });

    test('should send ping message', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();

      client.sendPing();

      const sentMessage = mockWebSocketInstance!.getLastSentMessage();
      expect(sentMessage.type).toBe(MessageType.PING);
    });
  });

  describe('Message Buffering', () => {
    test('should buffer pose data when disconnected', () => {
      const poseData: PoseData = {
        keypoints: [
          { x: 0.5, y: 0.5, z: 0, visibility: 0.9, name: 'nose' },
        ],
        timestamp: Date.now(),
      };

      // Send without connecting
      client.sendPoseData(poseData);

      expect(client.getBufferSize()).toBe(1);
    });

    test('should flush buffer when connection is established', () => {
      // Buffer some messages
      for (let i = 0; i < 3; i++) {
        client.sendPoseData({
          keypoints: [{ x: 0.5, y: 0.5, z: 0, visibility: 0.9, name: 'nose' }],
          timestamp: Date.now() + i,
        });
      }

      expect(client.getBufferSize()).toBe(3);

      // Connect
      client.connect();
      mockWebSocketInstance!.simulateOpen();

      // Buffer should be flushed
      expect(client.getBufferSize()).toBe(0);
      expect(mockWebSocketInstance!.getSentMessages().length).toBeGreaterThanOrEqual(3);
    });

    test('should limit buffer size', () => {
      // Send more messages than buffer size
      for (let i = 0; i < 15; i++) {
        client.sendPoseData({
          keypoints: [{ x: 0.5, y: 0.5, z: 0, visibility: 0.9, name: 'nose' }],
          timestamp: Date.now() + i,
        });
      }

      // Buffer should be limited to 10
      expect(client.getBufferSize()).toBe(10);
    });
  });

  describe('Message Receiving', () => {
    beforeEach(() => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();
    });

    test('should handle exercise detected message', () => {
      mockWebSocketInstance!.simulateMessage({
        type: MessageType.EXERCISE_DETECTED,
        exercise: 'pushup',
        confidence: 0.95,
      });

      expect(exerciseDetections).toHaveLength(1);
      expect(exerciseDetections[0]).toEqual({
        exercise: 'pushup',
        confidence: 0.95,
      });
    });

    test('should handle rep counted message', () => {
      mockWebSocketInstance!.simulateMessage({
        type: MessageType.REP_COUNTED,
        count: 5,
        total: 5,
      });

      expect(repCounts).toHaveLength(1);
      expect(repCounts[0]).toEqual({
        count: 5,
        total: 5,
      });
    });

    test('should handle form feedback message', () => {
      mockWebSocketInstance!.simulateMessage({
        type: MessageType.FORM_FEEDBACK,
        mistakes: [
          {
            type: 'hip_sag',
            severity: 0.6,
            suggestion: 'Engage your core',
          },
        ],
        form_score: 85,
      });

      expect(formFeedbacks).toHaveLength(1);
      expect(formFeedbacks[0].formScore).toBe(85);
      expect(formFeedbacks[0].mistakes).toHaveLength(1);
    });

    test('should handle error message', () => {
      mockWebSocketInstance!.simulateMessage({
        type: MessageType.ERROR,
        message: 'Invalid pose data',
        code: 'VALIDATION_ERROR',
      });

      expect(errors).toHaveLength(1);
      expect(errors[0]).toEqual({
        message: 'Invalid pose data',
        code: 'VALIDATION_ERROR',
      });
    });

    test('should handle pong message', () => {
      // Should not throw error
      mockWebSocketInstance!.simulateMessage({
        type: MessageType.PONG,
      });

      // No callback for pong, just verify it doesn't crash
      expect(errors).toHaveLength(0);
    });
  });

  describe('Connection Health', () => {
    test('should send periodic ping messages', () => {
      client.connect();
      mockWebSocketInstance!.simulateOpen();

      // Clear any initial messages
      const initialCount = mockWebSocketInstance!.getSentMessages().length;

      // Advance timer by ping interval (30 seconds)
      jest.advanceTimersByTime(30000);

      const messages = mockWebSocketInstance!.getSentMessages();
      const pingMessages = messages.filter(m => m.type === MessageType.PING);
      
      expect(pingMessages.length).toBeGreaterThan(0);
    });
  });
});
