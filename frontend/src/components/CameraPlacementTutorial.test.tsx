/**
 * Unit tests for CameraPlacementTutorial component
 * 
 * Tests Requirements 5.1, 5.2, 5.3, 5.4:
 * - Tutorial modal display
 * - Distance guidance display
 * - Height guidance display
 * - Exercise-specific camera angles
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CameraPlacementTutorial, ExerciseType } from './CameraPlacementTutorial';

describe('CameraPlacementTutorial', () => {
  const mockOnClose = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Modal Display', () => {
    it('should not render when isOpen is false', () => {
      render(
        <CameraPlacementTutorial
          isOpen={false}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.queryByText('Camera Placement Guide')).not.toBeInTheDocument();
    });

    it('should render when isOpen is true', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByText('Camera Placement Guide')).toBeInTheDocument();
    });

    it('should display general guidance by default', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByText('Camera Placement Guide')).toBeInTheDocument();
      expect(screen.getByText(/Proper camera placement ensures accurate exercise tracking/i)).toBeInTheDocument();
    });
  });

  describe('Distance Guidance (Requirement 5.2)', () => {
    it('should display distance guidance of 2.5-3 meters', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByText('Distance')).toBeInTheDocument();
      expect(screen.getAllByText(/2\.5-3 meters/i).length).toBeGreaterThan(0);
    });

    it('should display distance guidance for push-ups', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="pushup"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show pushup Setup/i);
      fireEvent.click(showButton);

      expect(screen.getAllByText(/2\.5-3 meters/i).length).toBeGreaterThan(0);
    });

    it('should display distance guidance for squats', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="squat"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show squat Setup/i);
      fireEvent.click(showButton);

      expect(screen.getAllByText(/2\.5-3 meters/i).length).toBeGreaterThan(0);
    });

    it('should display distance guidance for jumping jacks (3-3.5 meters)', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="jumping_jack"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show jumping jack Setup/i);
      fireEvent.click(showButton);

      expect(screen.getAllByText(/3-3\.5 meters/i).length).toBeGreaterThan(0);
    });
  });

  describe('Height Guidance (Requirement 5.3)', () => {
    it('should display height guidance at waist level', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByText('Height')).toBeInTheDocument();
      expect(screen.getAllByText(/Waist level/i).length).toBeGreaterThan(0);
    });

    it('should display waist level height for all exercises', () => {
      const exercises: ExerciseType[] = ['pushup', 'squat', 'plank', 'jumping_jack'];

      exercises.forEach((exercise) => {
        const { unmount } = render(
          <CameraPlacementTutorial
            isOpen={true}
            onClose={mockOnClose}
            onComplete={mockOnComplete}
            exerciseType={exercise}
          />
        );

        // Click to show exercise-specific guidance
        const showButton = screen.getByText(new RegExp(`Show ${exercise.replace('_', ' ')} Setup`, 'i'));
        fireEvent.click(showButton);

        expect(screen.getAllByText(/Waist level/i).length).toBeGreaterThan(0);
        unmount();
      });
    });
  });

  describe('Exercise-Specific Camera Angles (Requirement 5.4)', () => {
    it('should show side view angle for push-ups', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="pushup"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show pushup Setup/i);
      fireEvent.click(showButton);

      expect(screen.getByText(/Side view - camera perpendicular to your body/i)).toBeInTheDocument();
      expect(screen.getByText(/Position camera to your side, not in front/i)).toBeInTheDocument();
    });

    it('should show front or side view angle for squats', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="squat"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show squat Setup/i);
      fireEvent.click(showButton);

      expect(screen.getByText(/Front or side view - 45° angle works best/i)).toBeInTheDocument();
      expect(screen.getByText(/Front view helps track knee alignment/i)).toBeInTheDocument();
    });

    it('should show side view angle for plank', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="plank"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show plank Setup/i);
      fireEvent.click(showButton);

      expect(screen.getByText(/Side view - camera perpendicular to your body/i)).toBeInTheDocument();
      expect(screen.getByText(/Position camera to your side for best hip tracking/i)).toBeInTheDocument();
    });

    it('should show front view angle for jumping jacks', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="jumping_jack"
        />
      );

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show jumping jack Setup/i);
      fireEvent.click(showButton);

      expect(screen.getByText(/Front view - camera facing you directly/i)).toBeInTheDocument();
      expect(screen.getByText(/Front view captures full range of arm and leg motion/i)).toBeInTheDocument();
    });
  });

  describe('Tutorial Navigation', () => {
    it('should call onComplete when "Got It!" is clicked without exercise type', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      const gotItButton = screen.getByText('Got It!');
      fireEvent.click(gotItButton);

      expect(mockOnComplete).toHaveBeenCalledTimes(1);
    });

    it('should show exercise-specific guidance when "Show Exercise Setup" is clicked', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="pushup"
        />
      );

      // Initially shows general guidance
      expect(screen.getByText('Camera Placement Guide')).toBeInTheDocument();

      // Click to show exercise-specific guidance
      const showButton = screen.getByText(/Show pushup Setup/i);
      fireEvent.click(showButton);

      // Now shows exercise-specific title
      expect(screen.getByText(/Camera Setup for PUSHUP/i)).toBeInTheDocument();
    });

    it('should call onComplete when "Got It!" is clicked after viewing exercise-specific guidance', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="squat"
        />
      );

      // Show exercise-specific guidance
      const showButton = screen.getByText(/Show squat Setup/i);
      fireEvent.click(showButton);

      // Click Got It
      const gotItButton = screen.getByText('Got It!');
      fireEvent.click(gotItButton);

      expect(mockOnComplete).toHaveBeenCalledTimes(1);
    });

    it('should call onComplete when "Skip Tutorial" is clicked', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      const skipButton = screen.getByText('Skip Tutorial');
      fireEvent.click(skipButton);

      expect(mockOnComplete).toHaveBeenCalledTimes(1);
    });
  });

  describe('Content Display', () => {
    it('should display all guidance sections', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByText('Distance')).toBeInTheDocument();
      expect(screen.getByText('Height')).toBeInTheDocument();
      expect(screen.getByText('Camera Angle')).toBeInTheDocument();
      expect(screen.getByText('Important Tips')).toBeInTheDocument();
      expect(screen.getByText('Setup Diagram')).toBeInTheDocument();
      expect(screen.getByText('Full Body Visibility Required')).toBeInTheDocument();
    });

    it('should display exercise-specific tips for push-ups', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType="pushup"
        />
      );

      // Show exercise-specific guidance
      const showButton = screen.getByText(/Show pushup Setup/i);
      fireEvent.click(showButton);

      expect(screen.getByText(/Side angle allows tracking of elbow and hip alignment/i)).toBeInTheDocument();
    });

    it('should display warning about full body visibility', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.getByText(/The system will pause tracking if you move out of frame/i)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined exerciseType gracefully', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
          exerciseType={undefined}
        />
      );

      expect(screen.getByText('Camera Placement Guide')).toBeInTheDocument();
      expect(screen.queryByText(/Show.*Setup/i)).not.toBeInTheDocument();
    });

    it('should not show exercise-specific button when exerciseType is not provided', () => {
      render(
        <CameraPlacementTutorial
          isOpen={true}
          onClose={mockOnClose}
          onComplete={mockOnComplete}
        />
      );

      expect(screen.queryByText(/Show.*Setup/i)).not.toBeInTheDocument();
      expect(screen.getByText('Got It!')).toBeInTheDocument();
    });
  });
});
