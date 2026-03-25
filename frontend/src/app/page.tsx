'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const { user, logout, isLoading: authLoading } = useAuth();
  const isLoggedIn = !!user;

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleLogout = () => {
    logout();
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  return (
    <>
      {/* Neural Network Background Pattern */}
      <div className="neural-pattern" />
      
      {/* Interactive Cursor Glow */}
      <div 
        className="fixed w-96 h-96 rounded-full pointer-events-none transition-all duration-300 ease-out z-0"
        style={{
          left: mousePosition.x - 192,
          top: mousePosition.y - 192,
          background: 'radial-gradient(circle, rgba(102, 126, 234, 0.15) 0%, transparent 70%)',
        }}
      />

      <main className="relative min-h-screen flex flex-col items-center justify-center p-4 sm:p-8 overflow-hidden">
        <div className="max-w-7xl w-full space-y-16 relative z-10">
          
          {/* Hero Section */}
          <div className="text-center space-y-8 py-12">
            {/* Floating Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-4 float-animation">
              <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse" />
              <span className="text-sm font-medium text-gray-300">
                {isLoggedIn ? 'Welcome Back, Athlete' : 'Powered by Advanced AI'}
              </span>
            </div>

            {/* Main Heading with Gradient */}
            <h1 className="text-6xl sm:text-7xl lg:text-8xl font-black tracking-tight">
              <span className="gradient-text-neural">AI Gym Coach</span>
            </h1>

            {/* Subheading */}
            <p className="text-xl sm:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed font-light">
              {isLoggedIn ? (
                <>Ready for your next session? Your <span className="text-gradient-purple font-semibold">personalized coaching</span> is waiting.</>
              ) : (
                <>Experience the <span className="text-gradient-purple font-semibold">future of fitness</span> with privacy-first, 
                real-time workout recognition and intelligent form feedback.</>
              )}
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
              {isLoggedIn ? (
                <>
                  <Link href="/workout-demo">
                    <button className="glow-button text-lg px-8 py-4 w-full sm:w-auto min-w-[220px] flex items-center justify-center gap-2">
                       <i className="bi bi-play-fill text-2xl"></i> START WORKOUT
                    </button>
                  </Link>
                  <button 
                    onClick={handleLogout}
                    className="glass-card px-8 py-4 text-lg font-bold hover:bg-white/10 transition-all w-full sm:w-auto text-red-400 border-red-500/20 flex items-center justify-center gap-2"
                  >
                    <i className="bi bi-box-arrow-right"></i> SIGN OUT
                  </button>
                </>
              ) : (
                <>
                  <Link href="/login">
                    <button className="glow-button text-lg px-8 py-4 w-full sm:w-auto min-w-[200px] flex items-center justify-center gap-2">
                      <i className="bi bi-box-arrow-in-right"></i> LOGIN
                    </button>
                  </Link>
                  <Link href="/register">
                    <button className="glass-card px-8 py-4 text-lg font-bold hover:bg-white/10 transition-all w-full sm:w-auto min-w-[200px] border-white/20 flex items-center justify-center gap-2">
                      <i className="bi bi-person-plus"></i> REGISTER
                    </button>
                  </Link>
                  <Link href="/pose-demo">
                    <button className="px-8 py-4 text-lg font-bold text-gray-400 hover:text-white transition-all w-full sm:w-auto flex items-center gap-2 group">
                       LIVE DEMO
                       <i className="bi bi-play-circle text-xl group-hover:scale-125 transition-transform"></i>
                    </button>
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Conditional Features Grid */}
          {isLoggedIn ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
              
              {/* Workout Session Card */}
              <Link href="/workout-demo" className="group">
                <div className="glass-card p-8 h-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-blue-500" />
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <i className="bi bi-lightning-charge-fill text-3xl text-white"></i>
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-gradient-purple transition-colors">
                    Workout Session
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    Jump into a real-time workout session with AI-powered form correction and rep counting.
                  </p>
                  <div className="mt-6 flex items-center text-purple-400 font-semibold group-hover:translate-x-2 transition-transform">
                    Start Session <i className="bi bi-arrow-right ml-2"></i>
                  </div>
                </div>
              </Link>

              {/* Pose Detection Card */}
              <Link href="/pose-demo" className="group">
                <div className="glass-card p-8 h-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-pink-500 to-purple-500" />
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <i className="bi bi-person-bounding-box text-3xl text-white"></i>
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-gradient-pink transition-colors">
                    Pose Detection
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    Visualize how extensive skeletal tracking works with your camera in real-time.
                  </p>
                  <div className="mt-6 flex items-center text-pink-400 font-semibold group-hover:translate-x-2 transition-transform">
                    Try Demo <i className="bi bi-arrow-right ml-2"></i>
                  </div>
                </div>
              </Link>

              {/* AI Planner Card */}
              <Link href="/plan" className="group">
                <div className="glass-card p-8 h-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-500" />
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <i className="bi bi-calendar-week-fill text-3xl text-white"></i>
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-gradient-blue transition-colors">
                    AI Workout Planner
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    Generate a personalized 7-day workout routine tailored to your goals and fitness level.
                  </p>
                  <div className="mt-6 flex items-center text-cyan-400 font-semibold group-hover:translate-x-2 transition-transform">
                    Create Plan <i className="bi bi-arrow-right ml-2"></i>
                  </div>
                </div>
              </Link>

              {/* Chat Card */}
              <Link href="/chat" className="group">
                <div className="glass-card p-8 h-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 to-pink-500" />
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-500 to-pink-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <i className="bi bi-chat-dots-fill text-3xl text-white"></i>
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-gradient-pink transition-colors">
                    AI Coach Chat
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    Ask questions about your form, nutrition, or get motivation from your personal AI coach.
                  </p>
                  <div className="mt-6 flex items-center text-orange-400 font-semibold group-hover:translate-x-2 transition-transform">
                    Start Chat <i className="bi bi-arrow-right ml-2"></i>
                  </div>
                </div>
              </Link>

              {/* Profile Card */}
              <Link href="/profile" className="group">
                <div className="glass-card p-8 h-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500" />
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <i className="bi bi-person-circle text-3xl text-white"></i>
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-gradient-purple transition-colors">
                    Profile & Stats
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    Track your progress, view workout history, update goals, and manage notifications.
                  </p>
                  <div className="mt-6 flex items-center text-purple-400 font-semibold group-hover:translate-x-2 transition-transform">
                    View Profile <i className="bi bi-arrow-right ml-2"></i>
                  </div>
                </div>
              </Link>

              {/* Camera Tutorial Card */}
              <Link href="/camera-tutorial-demo" className="group">
                <div className="glass-card p-8 h-full relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-cyan-500" />
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <i className="bi bi-camera-video-fill text-3xl text-white"></i>
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-gradient-blue transition-colors">
                    Camera Setup
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    Learn optimal camera placement and setup for the best workout tracking experience.
                  </p>
                  <div className="mt-6 flex items-center text-blue-400 font-semibold group-hover:translate-x-2 transition-transform">
                    View Tutorial <i className="bi bi-arrow-right ml-2"></i>
                  </div>
                </div>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
              {/* Marketing Landing Card 1 */}
              <div className="glass-card p-10 flex flex-col justify-between group cursor-default">
                <div>
                  <div className="text-4xl font-bold text-white mb-6">Revolutionary <span className="text-gradient-purple">AI Tracking</span></div>
                  <p className="text-gray-400 text-lg leading-relaxed mb-8">
                    Our advanced neural networks detect and analyze your movement in real-time, providing instant form feedback without any hardware sensors.
                  </p>
                  <ul className="space-y-4 mb-10">
                    <li className="flex items-center gap-3 text-gray-300 italic">
                      <div className="w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-xs"><i className="bi bi-check-lg"></i></div>
                      33 Body Joint Tracking
                    </li>
                    <li className="flex items-center gap-3 text-gray-300 italic">
                      <div className="w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-xs"><i className="bi bi-check-lg"></i></div>
                      Real-time Form Correction
                    </li>
                    <li className="flex items-center gap-3 text-gray-300 italic">
                      <div className="w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-xs"><i className="bi bi-check-lg"></i></div>
                      Automatic Rep Counting
                    </li>
                  </ul>
                </div>
                <Link href="/workout-demo">
                  <button className="glass-card px-8 py-3 text-purple-400 hover:text-white transition-all w-full text-center font-bold">
                    Learn more about AI Tracking
                  </button>
                </Link>
              </div>

              {/* Marketing Landing Card 2 */}
              <div className="glass-card p-10 flex flex-col justify-between group cursor-default shadow-2xl shadow-purple-900/10">
                <div>
                  <div className="text-4xl font-bold text-white mb-6">Privacy <span className="text-gradient-pink">First</span></div>
                  <p className="text-gray-400 text-lg leading-relaxed mb-8">
                    Your data stays yours. All video processing happens entirely on your device. We never store or transmit your camera feed.
                  </p>
                  <div className="p-6 rounded-xl bg-white/5 border border-white/10 mb-8">
                    <div className="text-sm font-semibold uppercase tracking-widest text-pink-500 mb-2">Secure Architecture</div>
                    <div className="text-gray-400 text-sm">
                      Utilizing TensorFlow.js and MediaPipe for local execution. No cloud video analysis. Pure local intelligence.
                    </div>
                  </div>
                </div>
                <Link href="/chat">
                  <button className="glow-button px-8 py-4 w-full text-center text-lg shadow-lg">
                    Get Started Free <i className="bi bi-lightning-fill ml-2"></i>
                  </button>
                </Link>
              </div>
            </div>
          )}

          {/* Features Highlight */}
          <div className="glass-card p-8 sm:p-12 max-w-4xl mx-auto relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full -translate-y-16 translate-x-16" />
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 text-center relative z-10">
              <div className="space-y-4 group">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mx-auto group-hover:bg-purple-500/20 transition-all">
                  <i className="bi bi-shield-lock-fill text-2xl text-purple-400"></i>
                </div>
                <div className="text-4xl font-black text-gradient-purple">100%</div>
                <div className="text-gray-400 font-medium tracking-wide">Privacy-First</div>
                <div className="text-sm text-gray-500 leading-relaxed">All processing happens locally on your device</div>
              </div>
              <div className="space-y-4 group">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mx-auto group-hover:bg-blue-500/20 transition-all">
                  <i className="bi bi-stopwatch-fill text-2xl text-blue-400"></i>
                </div>
                <div className="text-4xl font-black text-gradient-blue">Real-Time</div>
                <div className="text-gray-400 font-medium tracking-wide">Instant Feedback</div>
                <div className="text-sm text-gray-500 leading-relaxed">Get immediate form corrections as you workout</div>
              </div>
              <div className="space-y-4 group">
                <div className="w-12 h-12 rounded-xl bg-pink-500/10 flex items-center justify-center mx-auto group-hover:bg-pink-500/20 transition-all">
                  <i className="bi bi-cpu-fill text-2xl text-pink-400"></i>
                </div>
                <div className="text-4xl font-black text-gradient-pink">AI-Powered</div>
                <div className="text-gray-400 font-medium tracking-wide">Smart Tracking</div>
                <div className="text-sm text-gray-500 leading-relaxed">Advanced ML models for accurate joint tracking</div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center pt-8 pb-4 space-y-4">
            <div className="flex items-center justify-center gap-3 text-sm text-gray-500">
              <span className="flex items-center gap-2">
                <i className="bi bi-check-circle-fill text-green-500/50"></i>
                Powered by MediaPipe & TensorFlow.js
              </span>
            </div>
            <p className="text-xs text-gray-600 flex items-center justify-center gap-2">
              <i className="bi bi-c-circle"></i> 2026 AI Gym Coach. Privacy-First Architecture.
            </p>
          </div>

        </div>
      </main>
    </>
  );
}

