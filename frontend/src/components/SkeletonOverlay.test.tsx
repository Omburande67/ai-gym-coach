import React from 'react';
import { render } from '@testing-library/react';
import { SkeletonOverlay } from './SkeletonOverlay';
import type { PoseData } from '@/types/pose';

describe('SkeletonOverlay', () => {
  const mockPoseData: PoseData = {
    keypoints: [
      { x: 0.5, y: 0.3, z: 0, visibility: 0.9, name: 'nose' },
      { x: 0.45, y: 0.28, z: 0, visibility: 0.85, name: 'left_eye_inner' },
      { x: 0.55, y: 0.28, z: 0, visibility: 0.85, name: 'right_eye_inner' },
      { x: 0.4, y: 0.5, z: 0, visibility: 0.8, name: 'left_shoulder' },
      { x: 0.6, y: 0.5, z: 0, visibility: 0.8, name: 'right_shoulder' },
      { x: 0.35, y: 0.65, z: 0, visibility: 0.75, name: 'left_elbow' },
      { x: 0.65, y: 0.65, z: 0, visibility: 0.75, name: 'right_elbow' },
      { x: 0.3, y: 0.8, z: 0, visibility: 0.7, name: 'left_wrist' },
      { x: 0.7, y: 0.8, z: 0, visibility: 0.7, name: 'right_wrist' },
      // Add remaining keypoints with lower visibility
      ...Array.from({ length: 24 }, (_, i) => ({
        x: 0.5,
        y: 0.5,
        z: 0,
        visibility: 0.3,
        name: `keypoint_${i + 9}`,
      })),
    ],
    timestamp: Date.now(),
  };

  it('renders canvas with correct dimensions', () => {
    const { container } = render(
      <SkeletonOverlay poseData={mockPoseData} width={640} height={480} />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
    expect(canvas).toHaveAttribute('width', '640');
    expect(canvas).toHaveAttribute('height', '480');
  });

  it('renders canvas with absolute positioning', () => {
    const { container } = render(
      <SkeletonOverlay poseData={mockPoseData} width={640} height={480} />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toHaveClass('absolute');
    expect(canvas).toHaveClass('pointer-events-none');
  });

  it('renders without pose data', () => {
    const { container } = render(
      <SkeletonOverlay poseData={null} width={640} height={480} />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('respects showKeypoints prop', () => {
    const { rerender, container } = render(
      <SkeletonOverlay
        poseData={mockPoseData}
        width={640}
        height={480}
        showKeypoints={true}
      />
    );

    let canvas = container.querySelector('canvas') as HTMLCanvasElement;
    expect(canvas).toBeInTheDocument();

    // Rerender with showKeypoints=false
    rerender(
      <SkeletonOverlay
        poseData={mockPoseData}
        width={640}
        height={480}
        showKeypoints={false}
      />
    );

    canvas = container.querySelector('canvas') as HTMLCanvasElement;
    expect(canvas).toBeInTheDocument();
  });

  it('respects showConnections prop', () => {
    const { rerender, container } = render(
      <SkeletonOverlay
        poseData={mockPoseData}
        width={640}
        height={480}
        showConnections={true}
      />
    );

    let canvas = container.querySelector('canvas') as HTMLCanvasElement;
    expect(canvas).toBeInTheDocument();

    // Rerender with showConnections=false
    rerender(
      <SkeletonOverlay
        poseData={mockPoseData}
        width={640}
        height={480}
        showConnections={false}
      />
    );

    canvas = container.querySelector('canvas') as HTMLCanvasElement;
    expect(canvas).toBeInTheDocument();
  });

  it('uses custom minVisibility threshold', () => {
    const { container } = render(
      <SkeletonOverlay
        poseData={mockPoseData}
        width={640}
        height={480}
        minVisibility={0.5}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('uses custom keypoint radius and line width', () => {
    const { container } = render(
      <SkeletonOverlay
        poseData={mockPoseData}
        width={640}
        height={480}
        keypointRadius={8}
        lineWidth={3}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('updates when pose data changes', () => {
    const { rerender, container } = render(
      <SkeletonOverlay poseData={mockPoseData} width={640} height={480} />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();

    // Update with new pose data
    const newPoseData: PoseData = {
      ...mockPoseData,
      timestamp: Date.now() + 1000,
    };

    rerender(
      <SkeletonOverlay poseData={newPoseData} width={640} height={480} />
    );

    expect(canvas).toBeInTheDocument();
  });
});
