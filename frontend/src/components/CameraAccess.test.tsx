import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CameraAccess, useCameraAccess } from './CameraAccess';
import type { CameraError } from '@/types/pose';

// Mock MediaStream
class MockMediaStream {
  private tracks: MediaStreamTrack[] = [];

  getTracks() {
    return this.tracks;
  }

  addTrack(track: MediaStreamTrack) {
    this.tracks.push(track);
  }
}

// Mock MediaStreamTrack
class MockMediaStreamTrack {
  kind = 'video';
  enabled = true;
  stopped = false;

  stop() {
    this.stopped = true;
  }
}

// Mock getUserMedia
const mockGetUserMedia = jest.fn();

// Mock HTMLVideoElement methods
Object.defineProperty(HTMLVideoElement.prototype, 'play', {
  configurable: true,
  value: jest.fn().mockResolvedValue(undefined),
});

Object.defineProperty(HTMLVideoElement.prototype, 'pause', {
  configurable: true,
  value: jest.fn(),
});

// Mock HTMLCanvasElement.getContext
HTMLCanvasElement.prototype.getContext = jest.fn().mockReturnValue({
  drawImage: jest.fn(),
  clearRect: jest.fn(),
  fillRect: jest.fn(),
});

// Mock requestAnimationFrame
let rafCallback: ((time: number) => void) | null = null;
global.requestAnimationFrame = jest.fn((cb) => {
  rafCallback = cb;
  return 1;
});

global.cancelAnimationFrame = jest.fn(() => {
  rafCallback = null;
});

describe('CameraAccess Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    rafCallback = null;

    // Setup navigator.mediaDevices.getUserMedia mock
    Object.defineProperty(global.navigator, 'mediaDevices', {
      writable: true,
      configurable: true,
      value: {
        getUserMedia: mockGetUserMedia,
      },
    });

    // Mock video element readyState
    Object.defineProperty(HTMLVideoElement.prototype, 'readyState', {
      writable: true,
      value: 4, // HAVE_ENOUGH_DATA
    });

    Object.defineProperty(HTMLVideoElement.prototype, 'HAVE_ENOUGH_DATA', {
      writable: false,
      value: 4,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Permission Request Flow', () => {
    it('should display enable camera button in prompt state', () => {
      render(<CameraAccess />);

      expect(screen.getByText('Enable Camera')).toBeInTheDocument();
      expect(screen.getByText(/Camera access is required/i)).toBeInTheDocument();
    });

    it('should show loading state when requesting camera access', async () => {
      // Mock getUserMedia to delay
      mockGetUserMedia.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => {
              const stream = new MockMediaStream();
              stream.addTrack(new MockMediaStreamTrack() as any);
              resolve(stream);
            }, 100);
          })
      );

      render(<CameraAccess />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/Requesting camera access/i)).toBeInTheDocument();
      });
    });

    it('should call onStreamReady when camera access is granted', async () => {
      const mockStream = new MockMediaStream();
      mockStream.addTrack(new MockMediaStreamTrack() as any);
      mockGetUserMedia.mockResolvedValue(mockStream);

      const onStreamReady = jest.fn();
      render(<CameraAccess onStreamReady={onStreamReady} />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(onStreamReady).toHaveBeenCalledWith(mockStream);
      });
    });

    it('should display success message when camera is active', async () => {
      const mockStream = new MockMediaStream();
      mockStream.addTrack(new MockMediaStreamTrack() as any);
      mockGetUserMedia.mockResolvedValue(mockStream);

      render(<CameraAccess />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/Camera active/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle permission denied error', async () => {
      const permissionError = new Error('Permission denied');
      permissionError.name = 'NotAllowedError';
      mockGetUserMedia.mockRejectedValue(permissionError);

      const onError = jest.fn();
      render(<CameraAccess onError={onError} />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/Camera Access Error/i)).toBeInTheDocument();
        expect(screen.getByText(/Camera access was denied/i)).toBeInTheDocument();
      });

      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'permission_denied',
          message: expect.stringContaining('denied'),
        })
      );
    });

    it('should handle camera not found error', async () => {
      const notFoundError = new Error('No camera found');
      notFoundError.name = 'NotFoundError';
      mockGetUserMedia.mockRejectedValue(notFoundError);

      const onError = jest.fn();
      render(<CameraAccess onError={onError} />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/No camera device was found/i)).toBeInTheDocument();
      });

      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'not_found',
        })
      );
    });

    it('should handle camera in use error', async () => {
      const inUseError = new Error('Camera in use');
      inUseError.name = 'NotReadableError';
      mockGetUserMedia.mockRejectedValue(inUseError);

      const onError = jest.fn();
      render(<CameraAccess onError={onError} />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/Camera is already in use/i)).toBeInTheDocument();
      });

      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'in_use',
        })
      );
    });

    it('should handle unknown errors', async () => {
      const unknownError = new Error('Unknown error');
      unknownError.name = 'UnknownError';
      mockGetUserMedia.mockRejectedValue(unknownError);

      const onError = jest.fn();
      render(<CameraAccess onError={onError} />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to access camera/i)).toBeInTheDocument();
      });

      expect(onError).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'unknown',
        })
      );
    });

    it('should show try again button on error', async () => {
      const permissionError = new Error('Permission denied');
      permissionError.name = 'NotAllowedError';
      mockGetUserMedia.mockRejectedValue(permissionError);

      render(<CameraAccess />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });
    });

    it('should show instructions for permission denied error', async () => {
      const permissionError = new Error('Permission denied');
      permissionError.name = 'NotAllowedError';
      mockGetUserMedia.mockRejectedValue(permissionError);

      render(<CameraAccess />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/To enable camera access:/i)).toBeInTheDocument();
        expect(screen.getByText(/Click the camera icon/i)).toBeInTheDocument();
      });
    });
  });

  describe('Video Stream Initialization', () => {
    it('should request camera with correct constraints', async () => {
      const mockStream = new MockMediaStream();
      mockStream.addTrack(new MockMediaStreamTrack() as any);
      mockGetUserMedia.mockResolvedValue(mockStream);

      render(<CameraAccess width={1280} height={720} />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(mockGetUserMedia).toHaveBeenCalledWith({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user',
          },
          audio: false,
        });
      });
    });

    it('should attach stream to video element', async () => {
      const mockStream = new MockMediaStream();
      mockStream.addTrack(new MockMediaStreamTrack() as any);
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { container } = render(<CameraAccess />);

      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        const videoElement = container.querySelector('video');
        expect(videoElement?.srcObject).toBe(mockStream);
      });
    });

    it('should render canvas element with correct dimensions', () => {
      const { container } = render(<CameraAccess width={800} height={600} />);

      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      expect(canvas?.width).toBe(800);
      expect(canvas?.height).toBe(600);
    });
  });

  describe('Camera Stop Functionality', () => {
    it('should stop camera when stop button is clicked', async () => {
      const mockTrack = new MockMediaStreamTrack();
      const mockStream = new MockMediaStream();
      mockStream.addTrack(mockTrack as any);
      mockGetUserMedia.mockResolvedValue(mockStream);

      render(<CameraAccess />);

      // Start camera
      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/Camera active/i)).toBeInTheDocument();
      });

      // Stop camera
      const stopButton = screen.getByText('Stop Camera');
      fireEvent.click(stopButton);

      await waitFor(() => {
        expect(mockTrack.stopped).toBe(true);
        expect(screen.getByText('Enable Camera')).toBeInTheDocument();
      });
    });

    it('should cleanup on unmount', async () => {
      const mockTrack = new MockMediaStreamTrack();
      const mockStream = new MockMediaStream();
      mockStream.addTrack(mockTrack as any);
      mockGetUserMedia.mockResolvedValue(mockStream);

      const { unmount } = render(<CameraAccess />);

      // Start camera
      const enableButton = screen.getByText('Enable Camera');
      fireEvent.click(enableButton);

      await waitFor(() => {
        expect(screen.getByText(/Camera active/i)).toBeInTheDocument();
      });

      // Unmount component
      unmount();

      // Verify cleanup
      expect(mockTrack.stopped).toBe(true);
    });
  });

  describe('useCameraAccess Hook', () => {
    it('should provide stream and error state', () => {
      const TestComponent = () => {
        const { stream, error, permissionState, handleStreamReady, handleError } =
          useCameraAccess();

        return (
          <div>
            <div data-testid="permission-state">{permissionState}</div>
            <div data-testid="has-stream">{stream ? 'yes' : 'no'}</div>
            <div data-testid="has-error">{error ? 'yes' : 'no'}</div>
            <button onClick={() => handleStreamReady(new MockMediaStream() as any)}>
              Set Stream
            </button>
            <button
              onClick={() =>
                handleError({ type: 'permission_denied', message: 'Test error' })
              }
            >
              Set Error
            </button>
          </div>
        );
      };

      render(<TestComponent />);

      expect(screen.getByTestId('permission-state')).toHaveTextContent('prompt');
      expect(screen.getByTestId('has-stream')).toHaveTextContent('no');
      expect(screen.getByTestId('has-error')).toHaveTextContent('no');

      // Set stream
      fireEvent.click(screen.getByText('Set Stream'));
      expect(screen.getByTestId('has-stream')).toHaveTextContent('yes');
      expect(screen.getByTestId('permission-state')).toHaveTextContent('granted');

      // Set error
      fireEvent.click(screen.getByText('Set Error'));
      expect(screen.getByTestId('has-error')).toHaveTextContent('yes');
      expect(screen.getByTestId('permission-state')).toHaveTextContent('denied');
    });
  });
});
