/**
 * Workout Summary Component
 * 
 * Displays post-workout analytics, totals, form feedback, and recommendations.
 * Implements Requirements 6.2, 6.3, 6.4, 6.5, 6.6
 */

'use client';

import React from 'react';
import { WorkoutSummaryData, ExerciseType } from '../types/workout';

interface WorkoutSummaryProps {
  summary: WorkoutSummaryData;
  onClose: () => void;
}

export function WorkoutSummary({ summary, onClose }: WorkoutSummaryProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-500/10 border-green-500/20';
    if (score >= 70) return 'bg-yellow-500/10 border-yellow-500/20';
    return 'bg-red-500/10 border-red-500/20';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
      <div className="glass-card shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-300 border-white/10 relative">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600/20 to-blue-700/20 p-8 border-b border-white/10 relative">
          <button 
            onClick={onClose}
            className="absolute top-6 right-6 text-gray-400 hover:text-white transition-colors bg-white/5 p-2 rounded-full border border-white/10"
          >
            <i className="bi bi-x-lg"></i>
          </button>
          
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
             <i className="bi bi-trophy-fill text-blue-400 text-xs"></i>
             <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Workout Complete</span>
          </div>
          
          <h1 className="text-4xl font-black gradient-text-neural mb-2">Sessional Analytics</h1>
          <p className="text-gray-400">Biometric data sequence successfully processed and archived.</p>
        </div>

        <div className="p-8">
          {/* Main Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center group hover:bg-white/10 transition-all">
              <div className="text-blue-400 mb-3">
                <i className="bi bi-clock-history text-3xl"></i>
              </div>
              <div className="text-3xl font-black text-white">{formatDuration(summary.total_duration_seconds)}</div>
              <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest mt-1">Total Duration</div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center group hover:bg-white/10 transition-all">
              <div className="text-purple-400 mb-3">
                <i className="bi bi-activity text-3xl"></i>
              </div>
              <div className="text-3xl font-black text-white">{summary.total_reps}</div>
              <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest mt-1">Total Repetitions</div>
            </div>

            <div className={`${getScoreBg(summary.average_form_score)} border rounded-2xl p-6 text-center group transition-all`}>
              <div className={getScoreColor(summary.average_form_score)}>
                <i className="bi bi-shield-check text-3xl mb-3"></i>
              </div>
              <div className={`text-3xl font-black ${getScoreColor(summary.average_form_score)}`}>
                {summary.average_form_score.toFixed(0)}%
              </div>
              <div className="text-[10px] text-gray-500 font-black uppercase tracking-widest mt-1">Average Precision</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            {/* Left Column: Exercises & Recommendations */}
            <div className="space-y-8">
              <section>
                <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-3">
                  <i className="bi bi-list-columns-reverse text-blue-400"></i>
                  Exercise Sequence
                  <div className="flex-1 h-[1px] bg-white/10" />
                </h2>
                <div className="space-y-3">
                  {summary.exercises.map((record, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10 hover:border-blue-500/30 transition-all group">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                           <i className="bi bi-person-walking text-blue-400"></i>
                        </div>
                        <div>
                          <span className="font-bold text-white capitalize text-sm">
                            {record.exercise_type.replace('_', ' ')}
                          </span>
                          <div className="text-[10px] text-gray-500 font-mono">
                            {record.reps_completed} REPS • {record.form_score}% SCORE
                          </div>
                        </div>
                      </div>
                      <div className={`text-sm font-black ${getScoreColor(record.form_score || 0)}`}>
                        {record.form_score}%
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section>
                <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-3">
                  <i className="bi bi-lightbulb-fill text-yellow-400"></i>
                  AI Insights
                  <div className="flex-1 h-[1px] bg-white/10" />
                </h2>
                <div className="bg-white/5 border border-yellow-500/20 p-6 rounded-2xl relative overflow-hidden">
                   <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500/50" />
                  {summary.recommendations.map((rec, index) => (
                    <div key={index} className="flex gap-3 mb-3 last:mb-0">
                       <i className="bi bi-quote text-yellow-500/30 text-2xl"></i>
                       <p className="text-xs text-gray-300 italic leading-relaxed">{rec}</p>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* Right Column: Mistakes & Comparison */}
            <div className="space-y-8">
              <section>
                <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-3">
                  <i className="bi bi-exclamation-triangle-fill text-red-500"></i>
                  Biometric Anomalies
                  <div className="flex-1 h-[1px] bg-white/10" />
                </h2>
                {summary.top_mistakes.length > 0 ? (
                  <div className="space-y-4">
                    {summary.top_mistakes.map((mistake, index) => (
                      <div key={index} className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 transition-colors group">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-bold text-white capitalize text-sm flex items-center gap-2">
                            <i className="bi bi-bug-fill text-red-500/50"></i>
                            {mistake.type.replace('_', ' ')}
                          </h3>
                          <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-[10px] font-black rounded-full border border-red-500/30">
                            {mistake.count} DETECTED
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 leading-tight">
                          {mistake.suggestion}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center bg-green-500/5 rounded-2xl border-2 border-dashed border-green-500/20">
                    <div className="text-green-400 mb-2 font-black text-lg flex items-center justify-center gap-2">
                       <i className="bi bi-patch-check-fill"></i> PERFECT EXECUTION
                    </div>
                    <p className="text-gray-500 text-xs">No bio-mechanical error patterns were detected during this session.</p>
                  </div>
                )}
              </section>

              <div className="pt-4">
                 <button
                  onClick={onClose}
                  className="glow-button w-full py-5 font-black tracking-widest uppercase flex items-center justify-center gap-3 text-lg"
                >
                  <i className="bi bi-check2-circle"></i> ARCHIVE & RETURN
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
