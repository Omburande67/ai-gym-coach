/**
 * Camera Placement Tutorial Demo Page
 * 
 * Demonstrates the camera placement tutorial component
 * with different exercise types
 */

'use client';

import React, { useState } from 'react';
import { CameraPlacementTutorial, ExerciseType } from '../../components/CameraPlacementTutorial';

export default function CameraTutorialDemo() {
  const [showTutorial, setShowTutorial] = useState(false);
  const [selectedExercise, setSelectedExercise] = useState<ExerciseType | undefined>(undefined);

  const exercises: { type: ExerciseType; label: string }[] = [
    { type: 'pushup', label: 'Push-ups' },
    { type: 'squat', label: 'Squats' },
    { type: 'plank', label: 'Plank' },
    { type: 'jumping_jack', label: 'Jumping Jacks' },
  ];

  const handleShowTutorial = (exercise?: ExerciseType) => {
    setSelectedExercise(exercise);
    setShowTutorial(true);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Camera Placement Tutorial Demo</h1>
        <p className="text-gray-600 mb-8">
          Test the camera placement tutorial component with different exercise types
        </p>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">General Tutorial</h2>
          <p className="text-gray-600 mb-4">
            Shows general camera placement guidance without exercise-specific instructions
          </p>
          <button
            onClick={() => handleShowTutorial(undefined)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            Show General Tutorial
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Exercise-Specific Tutorials</h2>
          <p className="text-gray-600 mb-4">
            Shows general guidance first, then exercise-specific camera angles and tips
          </p>
          <div className="grid grid-cols-2 gap-4">
            {exercises.map((exercise) => (
              <button
                key={exercise.type}
                onClick={() => handleShowTutorial(exercise.type)}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
              >
                {exercise.label}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-semibold mb-2">Implementation Notes</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>✓ Displays tutorial modal on first workout session (Requirement 5.1)</li>
            <li>✓ Shows distance guidance of 2.5-3 meters (Requirement 5.2)</li>
            <li>✓ Shows height guidance at waist level (Requirement 5.3)</li>
            <li>✓ Shows exercise-specific camera angles (Requirement 5.4)</li>
            <li>✓ Integrated with WorkoutSession component</li>
            <li>✓ Uses localStorage to track if user has seen tutorial</li>
            <li>✓ Can be manually triggered via "Camera Setup Guide" button</li>
          </ul>
        </div>
      </div>

      <CameraPlacementTutorial
        isOpen={showTutorial}
        onClose={() => setShowTutorial(false)}
        onComplete={() => {
          setShowTutorial(false);
          alert('Tutorial completed! In a real workout session, the camera would now start.');
        }}
        exerciseType={selectedExercise}
      />
    </div>
  );
}
