'use client';

import React, { useState, useEffect } from 'react';
import { WorkoutPlanDisplay } from '@/components/WorkoutPlanDisplay';
import { fetchActivePlan, generateWorkoutPlan } from '@/lib/api-plans';
import { WorkoutPlanResponse } from '@/types/workout';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function WorkoutPlanPage() {
  const { user, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [plan, setPlan] = useState<WorkoutPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadPlan();
    }
  }, [user, authLoading, router]);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const activePlan = await fetchActivePlan();
      setPlan(activePlan);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!user) return;
    setGenerating(true);
    setError(null);
    try {
      const newPlan = await generateWorkoutPlan();
      setPlan(newPlan);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleLogout = () => {
    logout();
    setPlan(null);
  }

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  return (
    <>
      <div className="neural-pattern" />
      <div className="min-h-screen p-4 sm:p-8 relative">
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl sm:text-4xl font-black gradient-text-neural flex items-center gap-4">
              <i className="bi bi-calendar-event"></i>
              Workout Plan
            </h1>
            <button 
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-black uppercase tracking-widest text-gray-300 hover:text-white transition-all flex items-center gap-2"
            >
              <i className="bi bi-box-arrow-right"></i>
              Logout
            </button>
          </div>

          <div className="glass-card p-6 sm:p-8 mb-8 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-500 to-blue-500" />
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 relative z-10">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center border border-white/5">
                  <i className="bi bi-robot text-3xl text-purple-400"></i>
                </div>
                <div>
                  <h2 className="text-2xl font-black text-white tracking-tight">AI BIOMETRIC PLANNER</h2>
                  <p className="text-gray-400 font-medium">Synthetic generation of movement sequences based on goals.</p>
                </div>
              </div>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="glow-button px-8 py-4 disabled:opacity-50 flex items-center gap-3 w-full sm:w-auto justify-center text-sm font-black tracking-widest uppercase"
              >
                {generating ? (
                  <i className="bi bi-cpu animate-spin text-xl"></i>
                ) : (
                  <i className="bi bi-stars text-xl"></i>
                )}
                {plan ? 'REGENERATE MATRIX' : 'GENERATE NEW PLAN'}
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-8 glass-card p-4 bg-red-500/10 border-red-500/20 text-red-400 flex items-center gap-3">
              <i className="bi bi-exclamation-octagon-fill"></i>
              <span className="font-bold">{error}</span>
            </div>
          )}

          {loading ? (
            <div className="flex flex-col items-center justify-center p-20 gap-4">
              <div className="spinner w-12 h-12" />
              <p className="text-gray-500 font-black tracking-widest text-xs uppercase animate-pulse">Syncing Plan Data...</p>
            </div>
          ) : plan ? (
            <WorkoutPlanDisplay plan={plan} />
          ) : (
            <div className="py-24 glass-card text-center relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />
              <div className="relative z-10">
                <div className="mx-auto w-24 h-24 rounded-3xl bg-white/5 flex items-center justify-center mb-8 border border-white/10 group-hover:scale-110 transition-transform duration-500">
                  <i className="bi bi-journal-x text-5xl text-gray-600 group-hover:text-purple-400 transition-colors"></i>
                </div>
                <h3 className="text-2xl font-black text-white mb-3 tracking-tight uppercase">No Active Core Strategy</h3>
                <p className="text-gray-400 max-w-sm mx-auto mb-10 leading-relaxed font-medium">
                  The AI Coach has not yet formulated a movement progression for your current cycle.
                </p>
                <button
                  onClick={handleGenerate}
                  className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-4 rounded-xl font-black tracking-widest uppercase transition-all inline-flex items-center gap-2"
                >
                  <i className="bi bi-plus-lg"></i>
                  Initialize Planning Sequence
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
