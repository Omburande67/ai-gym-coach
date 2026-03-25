'use client';

import React from 'react';
import { CameraAccess, useCameraAccess } from '@/components/CameraAccess';

/**
 * Camera Demo Page
 * 
 * Demonstrates the CameraAccess component functionality
 */
export default function CameraDemoPage() {
  const { stream, error, permissionState, handleStreamReady, handleError } =
    useCameraAccess();

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI Gym Coach - Camera Access Demo
          </h1>
          <p className="text-lg text-gray-600">
            Test the camera access component for workout tracking
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Camera Feed</h2>
          
          <div className="flex justify-center">
            <CameraAccess
              onStreamReady={handleStreamReady}
              onError={handleError}
              width={640}
              height={480}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Status Information</h2>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="font-medium text-gray-700">Permission State:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  permissionState === 'granted'
                    ? 'bg-green-100 text-green-800'
                    : permissionState === 'denied'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {permissionState}
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="font-medium text-gray-700">Stream Active:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  stream ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}
              >
                {stream ? 'Yes' : 'No'}
              </span>
            </div>

            {stream && (
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="font-medium text-gray-700">Video Tracks:</span>
                <span className="text-gray-600">
                  {stream.getVideoTracks().length} track(s)
                </span>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <span className="font-medium text-red-700">Error Type:</span>
                <span className="ml-2 text-red-600">{error.type}</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            📋 Implementation Details
          </h3>
          <ul className="list-disc list-inside space-y-1 text-blue-800 text-sm">
            <li>WebRTC camera permission request implemented</li>
            <li>Permission granted/denied states handled</li>
            <li>Video stream displayed in canvas element</li>
            <li>Error handling for various camera access scenarios</li>
            <li>Implements Requirements 1.1 and 15.1</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
