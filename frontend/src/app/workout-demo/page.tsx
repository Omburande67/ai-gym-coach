/**
 * Workout Demo Page
 * 
 * Demonstrates full WebSocket integration with real-time workout tracking
 */

'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { WorkoutSession } from '../../components/WorkoutSession';
import { useAuth } from '@/context/AuthContext';

export default function WorkoutDemoPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  const handleSessionEnd = () => {
    console.log('Workout session ended');
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  // Calculate dynamic WebSocket URL
  const getWsUrl = () => {
    if (process.env.NEXT_PUBLIC_WS_URL) {
      return process.env.NEXT_PUBLIC_WS_URL;
    }
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return apiUrl.replace(/^http/, 'ws');
  };

  return (
    <main className="min-h-screen bg-[#0a0e27] py-8 relative">
      <div className="neural-pattern" />
      <div className="container mx-auto relative z-10">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-black mb-2 gradient-text-neural">AI Gym Coach</h1>
          <p className="text-gray-400">
            Real-time workout tracking with WebSocket feedback
          </p>
        </div>

        <WorkoutSession
          userId={user.user_id || (user as any).id || 'unknown-user'}
          websocketUrl={getWsUrl()}
          onSessionEnd={handleSessionEnd}
        />

        <div className="mt-8 max-w-2xl mx-auto glass-card border border-white/10 rounded-2xl shadow-xl p-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-blue-500 to-purple-500" />
          <h2 className="text-xl font-black text-white mb-4 tracking-tight uppercase">Operational Guide</h2>
          <ol className="list-decimal list-inside space-y-3 text-gray-400 font-medium">
            <li>Click <span className="text-white font-bold">"Initialize Session"</span> to begin</li>
            <li>Grant camera permissions when prompted</li>
            <li>Position yourself <span className="text-blue-400 font-bold">2.5-3 meters</span> from the camera</li>
            <li>Start exercising (push-ups, squats, jumping jacks, or plank)</li>
            <li>Receive real-time feedback on form and rep counting</li>
            <li>Click <span className="text-red-400 font-bold">"Terminate Session"</span> when finished</li>
          </ol>

          <div className="mt-8 p-6 bg-blue-900/20 border border-blue-500/20 rounded-xl">
            <h3 className="font-black text-white mb-3 tracking-widest uppercase text-sm">Supported Biometrics</h3>
            <ul className="list-disc list-inside space-y-2 text-sm text-gray-300">
              <li><strong className="text-blue-400">Push-ups:</strong> Full range of motion with proper form</li>
              <li><strong className="text-blue-400">Squats:</strong> Depth tracking and knee alignment</li>
              <li><strong className="text-blue-400">Jumping Jacks:</strong> Full arm and leg extension</li>
              <li><strong className="text-blue-400">Plank:</strong> Hold time and body alignment</li>
            </ul>
          </div>

          <div className="mt-6 p-6 bg-green-900/20 border border-green-500/20 rounded-xl">
            <h3 className="font-black text-white mb-3 tracking-widest uppercase text-sm flex items-center gap-2">
              <i className="bi bi-shield-check text-green-400"></i> Privacy First
            </h3>
            <p className="text-sm text-gray-300 leading-relaxed">
              Your video is processed <span className="text-white font-bold">locally</span> in your browser. Only skeletal
              keypoints are sent to the server. No video frames are ever
              transmitted or stored.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}