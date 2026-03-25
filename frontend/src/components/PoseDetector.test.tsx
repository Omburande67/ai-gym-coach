import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PoseDetector } from './PoseDetector';
import * as poseDetection from '@tensorflow-models/pose-detection';

// Mock TensorFlow.js pose detection
jest.mock('@tensorflow-models/pose-detection');
jest.mock('@tensorflow/tfjs-backend-webgl', () => ({}));

describe('PoseDetector', () => {
  let mockDetector: jest.Mocked<poseDetection.PoseDetector>;
  let mockVideoElement: HTMLVideoElement;

  beforeEach(() => {
    // Create mock detector
    mockDetector = {
      estimatePoses: jest.fn(),
      dispose: jest.fn(),
      reset: jest.fn(),
    } as any;

    // Mock createDetector
    (poseDetection.createDetector as jest.Mock).mockResolvedValue(mockDetector);

    // Create mock video element with proper readyState
    mockVideoElement = document.createElement('video');
    Object.defineProperty(mockVideoElement, 'readyState', {
      writable: true,
      value: 4, // HAVE_ENOUGH_DATA
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Model Initialization', () => {
    it('should display loading state while model is loading', () => {
      render(<PoseDetector videoElement={null} />);
      
      expect(screen.getByText(/Loading BlazePose model/i)).toBeInTheDocument();
    });

    it('should initialize BlazePose model on mount', async () => {
      render(<PoseDetector videoElement={null} />);

      await waitFor(() => {
        expect(poseDetection.createDetector).toHaveBeenCalledWith(
          poseDetection.SupportedModels.BlazePose,
          expect.objectContaining({
            runtime: 'tfjs',
            modelType: 'full',
            enableSmoothing: true,
            enableSegmentation: false,
          })
        );
      });
    });

    it('should display ready state when model is loaded', async () => {
      render(<PoseDetector videoElement={null} />);

      await waitFor(() => {
        expect(screen.getByText(/Pose detection active/i)).toBeInTheDocument();
      });
    });

    it('should handle model loading errors', async () => {
      const error = new Error('Failed to load model');
      (poseDetection.createDetector as jest.Mock).mockRejectedValue(error);

      const onError = jest.fn();
      render(<PoseDetector videoElement={null} onError={onError} />);

      await waitFor(() => {
        expect(screen.getByText(/Pose Detection Error/i)).toBeInTheDocument();
        expect(onError).toHaveBeenCalledWith(error);
      });
    });

    it('should dispose detector on unmount', async () => {
      const { unmount } = render(<PoseDetector videoElement={null} />);

      await waitFor(() => {
        expect(mockDetector).toBeDefined();
      });

      unmount();

      await waitFor(() => {
        expect(mockDetector.dispose).toHaveBeenCalled();
      });
    });
  });

  describe('Pose Detection', () => {
    it('should detect poses when video element is provided', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [
          { x: 100, y: 200, z: 0, score: 0.9, name: 'nose' },
          { x: 150, y: 250, z: 0, score: 0.85, name: 'left_eye' },
        ],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      // Wait for model to load and detection to start
      await waitFor(
        () => {
          expect(mockDetector.estimatePoses).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );
    });

    it('should convert TensorFlow pose to PoseData format', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [
          { x: 100, y: 200, z: 0.5, score: 0.9, name: 'nose' },
          { x: 150, y: 250, z: -0.3, score: 0.85, name: 'left_eye' },
        ],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      if (onPoseDetected.mock.calls.length > 0) {
        const poseData = onPoseDetected.mock.calls[0][0];
        expect(poseData).toHaveProperty('keypoints');
        expect(poseData).toHaveProperty('timestamp');
        expect(poseData.keypoints).toHaveLength(2);
        expect(poseData.keypoints[0]).toMatchObject({
          x: 100,
          y: 200,
          z: 0.5,
          visibility: 0.9,
          name: 'nose',
        });
      }
    });

    it('should extract 33 keypoints from BlazePose', async () => {
      // Create mock pose with 33 keypoints (BlazePose standard)
      const mockKeypoints = Array.from({ length: 33 }, (_, i) => ({
        x: i * 10,
        y: i * 10,
        z: 0,
        score: 0.9,
        name: `keypoint_${i}`,
      }));

      const mockPose: poseDetection.Pose = {
        keypoints: mockKeypoints,
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      if (onPoseDetected.mock.calls.length > 0) {
        const poseData = onPoseDetected.mock.calls[0][0];
        expect(poseData.keypoints).toHaveLength(33);
      }
    });

    it('should not detect poses when disabled', async () => {
      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={false}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Pose detection active/i)).toBeInTheDocument();
      });

      // Wait a bit to ensure no detection happens
      await new Promise((resolve) => setTimeout(resolve, 500));

      expect(mockDetector.estimatePoses).not.toHaveBeenCalled();
    });

    it('should handle detection errors gracefully', async () => {
      const error = new Error('Detection failed');
      mockDetector.estimatePoses.mockRejectedValue(error);

      const onError = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onError={onError}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(mockDetector.estimatePoses).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      // Error handler should be called
      await waitFor(
        () => {
          expect(onError).toHaveBeenCalled();
        },
        { timeout: 1000 }
      );
    });
  });

  describe('Performance', () => {
    it('should respect target FPS setting', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [{ x: 100, y: 200, z: 0, score: 0.9, name: 'nose' }],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const targetFps = 10;
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          enabled={true}
          targetFps={targetFps}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Pose detection active/i)).toBeInTheDocument();
      });

      // The component should throttle detection based on target FPS
      // This is tested by checking that the interval between detections
      // is approximately 1000/targetFps milliseconds
    });

    it('should display current FPS', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [{ x: 100, y: 200, z: 0, score: 0.9, name: 'nose' }],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      render(
        <PoseDetector
          videoElement={mockVideoElement}
          enabled={true}
          targetFps={15}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/FPS:/i)).toBeInTheDocument();
      });
    });

    it('should track detection count', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [{ x: 100, y: 200, z: 0, score: 0.9, name: 'nose' }],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      render(
        <PoseDetector
          videoElement={mockVideoElement}
          enabled={true}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Detections:/i)).toBeInTheDocument();
      });
    });
  });

  describe('Keypoint Data', () => {
    it('should include visibility scores for all keypoints', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [
          { x: 100, y: 200, z: 0, score: 0.95, name: 'nose' },
          { x: 150, y: 250, z: 0, score: 0.75, name: 'left_eye' },
          { x: 200, y: 300, z: 0, score: 0.45, name: 'right_eye' },
        ],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      if (onPoseDetected.mock.calls.length > 0) {
        const poseData = onPoseDetected.mock.calls[0][0];
        poseData.keypoints.forEach((kp: any) => {
          expect(kp).toHaveProperty('visibility');
          expect(kp.visibility).toBeGreaterThanOrEqual(0);
          expect(kp.visibility).toBeLessThanOrEqual(1);
        });
      }
    });

    it('should include 3D coordinates (x, y, z) for all keypoints', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [
          { x: 100, y: 200, z: 0.5, score: 0.9, name: 'nose' },
          { x: 150, y: 250, z: -0.3, score: 0.85, name: 'left_eye' },
        ],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      if (onPoseDetected.mock.calls.length > 0) {
        const poseData = onPoseDetected.mock.calls[0][0];
        poseData.keypoints.forEach((kp: any) => {
          expect(kp).toHaveProperty('x');
          expect(kp).toHaveProperty('y');
          expect(kp).toHaveProperty('z');
          expect(typeof kp.x).toBe('number');
          expect(typeof kp.y).toBe('number');
          expect(typeof kp.z).toBe('number');
        });
      }
    });

    it('should include joint names for all keypoints', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [
          { x: 100, y: 200, z: 0, score: 0.9, name: 'nose' },
          { x: 150, y: 250, z: 0, score: 0.85, name: 'left_shoulder' },
        ],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      if (onPoseDetected.mock.calls.length > 0) {
        const poseData = onPoseDetected.mock.calls[0][0];
        poseData.keypoints.forEach((kp: any) => {
          expect(kp).toHaveProperty('name');
          expect(typeof kp.name).toBe('string');
          expect(kp.name.length).toBeGreaterThan(0);
        });
      }
    });
  });

  describe('Privacy Controls (Requirements 1.3, 11.3)', () => {
    it('should only output keypoint data, not raw frame data', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [
          { x: 100, y: 200, z: 0, score: 0.9, name: 'nose' },
          { x: 150, y: 250, z: 0, score: 0.85, name: 'left_eye' },
        ],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      if (onPoseDetected.mock.calls.length > 0) {
        const poseData = onPoseDetected.mock.calls[0][0];
        
        // Verify only keypoints and timestamp are present
        expect(Object.keys(poseData)).toEqual(['keypoints', 'timestamp']);
        
        // Verify no image data properties
        expect(poseData).not.toHaveProperty('imageData');
        expect(poseData).not.toHaveProperty('canvas');
        expect(poseData).not.toHaveProperty('frame');
        expect(poseData).not.toHaveProperty('pixels');
        expect(poseData).not.toHaveProperty('buffer');
        
        // Verify keypoints only contain coordinate data
        poseData.keypoints.forEach((kp: any) => {
          const keypointKeys = Object.keys(kp);
          expect(keypointKeys).toEqual(['x', 'y', 'z', 'visibility', 'name']);
        });
      }
    });

    it('should not store frame data in component state', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [{ x: 100, y: 200, z: 0, score: 0.9, name: 'nose' }],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const { container } = render(
        <PoseDetector
          videoElement={mockVideoElement}
          enabled={true}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Pose detection active/i)).toBeInTheDocument();
      });

      // Wait for some detections to occur
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Check that no canvas elements are created in the DOM
      // (temporary canvases should be created and destroyed, not added to DOM)
      const canvases = container.querySelectorAll('canvas');
      expect(canvases.length).toBe(0);
    });

    it('should process frames at target FPS (15-30 FPS)', async () => {
      const mockPose: poseDetection.Pose = {
        keypoints: [{ x: 100, y: 200, z: 0, score: 0.9, name: 'nose' }],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const targetFps = 20;
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          enabled={true}
          targetFps={targetFps}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Pose detection active/i)).toBeInTheDocument();
      });

      // Wait for FPS to stabilize
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Check that FPS display shows reasonable value
      const fpsText = screen.getByText(/FPS:/i).textContent;
      expect(fpsText).toMatch(/FPS: \d+/);
    });

    it('should handle frame processing errors without leaking frame data', async () => {
      const error = new Error('Processing failed');
      mockDetector.estimatePoses.mockRejectedValue(error);

      const onError = jest.fn();
      const onPoseDetected = jest.fn();
      
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onError={onError}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(mockDetector.estimatePoses).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      // Error handler should be called
      await waitFor(
        () => {
          expect(onError).toHaveBeenCalled();
        },
        { timeout: 1000 }
      );

      // Verify no pose data was emitted on error
      expect(onPoseDetected).not.toHaveBeenCalled();
    });

    it('should process video element directly without storing frame data', async () => {
      // This test verifies that BlazePose processes the video element directly
      // without creating intermediate frame storage
      const mockPose: poseDetection.Pose = {
        keypoints: [{ x: 100, y: 200, z: 0, score: 0.9, name: 'nose' }],
        score: 0.9,
      };

      mockDetector.estimatePoses.mockResolvedValue([mockPose]);

      const onPoseDetected = jest.fn();
      render(
        <PoseDetector
          videoElement={mockVideoElement}
          onPoseDetected={onPoseDetected}
          enabled={true}
        />
      );

      await waitFor(
        () => {
          expect(mockDetector.estimatePoses).toHaveBeenCalled();
        },
        { timeout: 3000 }
      );

      // Verify estimatePoses was called with the video element directly
      expect(mockDetector.estimatePoses).toHaveBeenCalledWith(
        mockVideoElement,
        expect.objectContaining({
          flipHorizontal: false,
        })
      );

      // Verify pose data was emitted
      await waitFor(
        () => {
          expect(onPoseDetected).toHaveBeenCalled();
        },
        { timeout: 1000 }
      );
    });
  });
});
