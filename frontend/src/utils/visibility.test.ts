/**
 * Unit tests for visibility detection utilities
 * 
 * Tests Requirement 5.5: Full body visibility detection
 */

import { checkFullBodyVisibility, getVisibilityWarningMessage } from './visibility';
import { PoseData, PoseKeypoint } from '@/types/pose';

describe('checkFullBodyVisibility', () => {
  // Helper to create pose data with specified visibility scores
  const createPoseData = (visibilityScores: number[]): PoseData => {
    const keypoints: PoseKeypoint[] = visibilityScores.map((visibility, index) => ({
      x: 0.5,
      y: 0.5,
      z: 0,
      visibility,
      name: `keypoint_${index}`,
    }));

    return {
      keypoints,
      timestamp: Date.now(),
    };
  };

  describe('with null or empty pose data', () => {
    it('should return not visible for null pose data', () => {
      const result = checkFullBodyVisibility(null);
      
      expect(result.isFullyVisible).toBe(false);
      expect(result.visibleKeypointsCount).toBe(0);
      expect(result.totalKeypointsCount).toBe(0);
      expect(result.visibilityPercentage).toBe(0);
      expect(result.lowVisibilityPercentage).toBe(1);
    });

    it('should return not visible for empty keypoints', () => {
      const poseData: PoseData = {
        keypoints: [],
        timestamp: Date.now(),
      };
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(false);
      expect(result.totalKeypointsCount).toBe(0);
    });
  });

  describe('with fully visible user (all keypoints > 0.5)', () => {
    it('should return fully visible when all keypoints have high visibility', () => {
      const poseData = createPoseData([0.9, 0.8, 0.95, 0.85, 0.92]);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(true);
      expect(result.visibleKeypointsCount).toBe(5);
      expect(result.totalKeypointsCount).toBe(5);
      expect(result.visibilityPercentage).toBe(1);
      expect(result.lowVisibilityPercentage).toBe(0);
    });

    it('should return fully visible when exactly 20% have low visibility', () => {
      // 10 keypoints, 2 with low visibility = exactly 20%
      const poseData = createPoseData([0.9, 0.8, 0.95, 0.85, 0.92, 0.88, 0.91, 0.87, 0.4, 0.3]);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(true);
      expect(result.visibleKeypointsCount).toBe(8);
      expect(result.totalKeypointsCount).toBe(10);
      expect(result.visibilityPercentage).toBe(0.8);
      expect(result.lowVisibilityPercentage).toBe(0.2);
    });
  });

  describe('with partially visible user (>20% keypoints < 0.5)', () => {
    it('should return not visible when more than 20% have low visibility', () => {
      // 10 keypoints, 3 with low visibility = 30%
      const poseData = createPoseData([0.9, 0.8, 0.95, 0.85, 0.92, 0.88, 0.91, 0.4, 0.3, 0.2]);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(false);
      expect(result.visibleKeypointsCount).toBe(7);
      expect(result.totalKeypointsCount).toBe(10);
      expect(result.visibilityPercentage).toBe(0.7);
      expect(result.lowVisibilityPercentage).toBe(0.3);
    });

    it('should return not visible when all keypoints have low visibility', () => {
      const poseData = createPoseData([0.1, 0.2, 0.15, 0.3, 0.25]);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(false);
      expect(result.visibleKeypointsCount).toBe(0);
      expect(result.totalKeypointsCount).toBe(5);
      expect(result.visibilityPercentage).toBe(0);
      expect(result.lowVisibilityPercentage).toBe(1);
    });

    it('should return not visible when exactly 21% have low visibility', () => {
      // 100 keypoints, 21 with low visibility = 21%
      const visibilityScores = Array(79).fill(0.9).concat(Array(21).fill(0.3));
      const poseData = createPoseData(visibilityScores);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(false);
      expect(result.visibleKeypointsCount).toBe(79);
      expect(result.totalKeypointsCount).toBe(100);
      expect(result.lowVisibilityPercentage).toBe(0.21);
    });
  });

  describe('with custom thresholds', () => {
    it('should use custom visibility threshold', () => {
      // With default threshold (0.5), 2 keypoints are low visibility
      // With threshold 0.7, 4 keypoints are low visibility
      const poseData = createPoseData([0.9, 0.8, 0.6, 0.55, 0.4]);
      
      const resultDefault = checkFullBodyVisibility(poseData, 0.5);
      expect(resultDefault.lowVisibilityPercentage).toBe(0.2); // 1/5
      
      const resultCustom = checkFullBodyVisibility(poseData, 0.7);
      expect(resultCustom.lowVisibilityPercentage).toBe(0.6); // 3/5
    });

    it('should use custom max low visibility percentage', () => {
      // 10 keypoints, 3 with low visibility = 30%
      const poseData = createPoseData([0.9, 0.8, 0.95, 0.85, 0.92, 0.88, 0.91, 0.4, 0.3, 0.2]);
      
      // With default max (0.2), should be not visible
      const resultDefault = checkFullBodyVisibility(poseData, 0.5, 0.2);
      expect(resultDefault.isFullyVisible).toBe(false);
      
      // With custom max (0.4), should be visible
      const resultCustom = checkFullBodyVisibility(poseData, 0.5, 0.4);
      expect(resultCustom.isFullyVisible).toBe(true);
    });
  });

  describe('with edge cases', () => {
    it('should handle keypoints with exactly 0.5 visibility (boundary)', () => {
      const poseData = createPoseData([0.5, 0.5, 0.5, 0.5, 0.5]);
      
      const result = checkFullBodyVisibility(poseData);
      
      // 0.5 is not less than 0.5, so all keypoints are visible
      expect(result.isFullyVisible).toBe(true);
      expect(result.lowVisibilityPercentage).toBe(0);
    });

    it('should handle keypoints with visibility just below threshold', () => {
      const poseData = createPoseData([0.49, 0.49, 0.49, 0.49, 0.49]);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(false);
      expect(result.lowVisibilityPercentage).toBe(1);
    });

    it('should handle single keypoint', () => {
      const poseData = createPoseData([0.9]);
      
      const result = checkFullBodyVisibility(poseData);
      
      expect(result.isFullyVisible).toBe(true);
      expect(result.totalKeypointsCount).toBe(1);
    });
  });
});

describe('getVisibilityWarningMessage', () => {
  it('should return empty string when fully visible', () => {
    const status = {
      isFullyVisible: true,
      visibleKeypointsCount: 30,
      totalKeypointsCount: 33,
      visibilityPercentage: 0.91,
      lowVisibilityPercentage: 0.09,
    };
    
    const message = getVisibilityWarningMessage(status);
    
    expect(message).toBe('');
  });

  it('should return warning message when not fully visible', () => {
    const status = {
      isFullyVisible: false,
      visibleKeypointsCount: 20,
      totalKeypointsCount: 33,
      visibilityPercentage: 0.61,
      lowVisibilityPercentage: 0.39,
    };
    
    const message = getVisibilityWarningMessage(status);
    
    expect(message).toContain('not fully visible');
    expect(message).toContain('39%');
    expect(message).toContain('out of view');
  });

  it('should round percentage correctly', () => {
    const status = {
      isFullyVisible: false,
      visibleKeypointsCount: 25,
      totalKeypointsCount: 33,
      visibilityPercentage: 0.76,
      lowVisibilityPercentage: 0.242, // Should round to 24%
    };
    
    const message = getVisibilityWarningMessage(status);
    
    expect(message).toContain('24%');
  });
});
