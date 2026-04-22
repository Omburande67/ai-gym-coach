/**
 * Workout Demo Page
 * 
 * Demonstrates full WebSocket integration with real-time workout tracking
 */

'use client';

import React from 'react';
import { WorkoutSession } from '../../components/WorkoutSession';

export default function WorkoutDemoPage() {
  const handleSessionEnd = () => {
    console.log('Workout session ended');
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-2">AI Gym Coach</h1>
          <p className="text-gray-600">
            Real-time workout tracking with WebSocket feedback
          </p>
        </div>

        <WorkoutSession
          userId="demo-user"
          websocketUrl={process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8000'}
          onSessionEnd={handleSessionEnd}
        />

        <div className="mt-8 max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">How It Works</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Click "Start Workout" to begin your session</li>
            <li>Grant camera permissions when prompted</li>
            <li>Position yourself 2.5-3 meters from the camera</li>
            <li>Start exercising (push-ups, squats, jumping jacks, or plank)</li>
            <li>Receive real-time feedback on form and rep counting</li>
            <li>Click "End Workout" when finished</li>
          </ol>

          <div className="mt-6 p-4 bg-blue-50 rounded">
            <h3 className="font-semibold mb-2">Supported Exercises:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              <li><strong>Push-ups:</strong> Full range of motion with proper form</li>
              <li><strong>Squats:</strong> Depth tracking and knee alignment</li>
              <li><strong>Jumping Jacks:</strong> Full arm and leg extension</li>
              <li><strong>Plank:</strong> Hold time and body alignment</li>
            </ul>
          </div>

          <div className="mt-4 p-4 bg-green-50 rounded">
            <h3 className="font-semibold mb-2">Privacy First:</h3>
            <p className="text-sm text-gray-700">
              Your video is processed locally in your browser. Only skeletal
              keypoints are sent to the server - no video frames are ever
              transmitted or stored.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}