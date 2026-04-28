import React from 'react';
import { WorkoutSummaryData } from '../types/workout';

interface WorkoutSummaryProps {
  summary: WorkoutSummaryData | null;
  onClose: () => void;
}

export function WorkoutSummary({ summary, onClose }: WorkoutSummaryProps) {
  if (!summary) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md">
        <div className="glass-card border border-red-500/20 p-8 max-w-md w-full mx-4 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
          <div className="text-center">
            <i className="bi bi-exclamation-triangle text-5xl text-red-500/50 mb-4 inline-block"></i>
            <h2 className="text-2xl font-black text-white mb-2 uppercase tracking-widest">No Data Secured</h2>
            <p className="text-gray-400 mb-8 font-mono text-sm">Biometric processing failed or session was empty.</p>
            <button
              onClick={onClose}
              className="glow-button w-full py-3 text-sm font-black tracking-widest uppercase"
            >
              Acknowledge
            </button>
          </div>
        </div>
      </div>
    );
  }

  const totalReps = summary.total_reps || 0;
  const averageFormScore = summary.average_form_score || 0;
  const durationMinutes = Math.floor((summary.total_duration_seconds || 0) / 60);
  const durationSeconds = (summary.total_duration_seconds || 0) % 60;
  
  // Format top mistakes for display
  const topMistakes = summary.top_mistakes || [];

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]';
    if (score >= 70) return 'text-yellow-400 drop-shadow-[0_0_8px_rgba(250,204,21,0.5)]';
    return 'text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]';
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="glass-card border border-blue-500/20 rounded-3xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto custom-scrollbar relative overflow-hidden shadow-2xl shadow-blue-900/20">
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500" />
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        
        {/* Header */}
        <div className="flex justify-between items-start mb-10 relative z-10">
          <div>
            <h2 className="text-sm font-bold text-blue-400 tracking-widest uppercase mb-1 flex items-center gap-2">
              <i className="bi bi-check2-circle"></i> Session Terminated
            </h2>
            <h1 className="text-4xl font-black text-white tracking-tight">Post-Workout Analysis</h1>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-all"
          >
            <i className="bi bi-x-lg"></i>
          </button>
        </div>

        {/* Primary Stats */}
        <div className="grid grid-cols-3 gap-6 mb-10 relative z-10">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden group hover:border-blue-500/30 transition-all">
            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
              <i className="bi bi-repeat"></i> Total Reps
            </div>
            <div className="text-5xl font-black text-white">{totalReps}</div>
          </div>
          
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden group hover:border-purple-500/30 transition-all">
            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
              <i className="bi bi-stopwatch"></i> Duration
            </div>
            <div className="text-4xl font-black text-white">
              {durationMinutes}<span className="text-2xl text-gray-500">m</span> {durationSeconds}<span className="text-2xl text-gray-500">s</span>
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden group hover:border-green-500/30 transition-all">
            <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
              <i className="bi bi-bullseye"></i> Form Accuracy
            </div>
            <div className={`text-5xl font-black ${getScoreColor(averageFormScore)}`}>
              {Math.round(averageFormScore)}<span className="text-2xl text-gray-500">%</span>
            </div>
          </div>
        </div>

        {/* Detailed Breakdown & AI Analysis */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 relative z-10">
          <div>
            <h3 className="text-sm font-black text-white tracking-widest uppercase mb-4 flex items-center gap-2 border-b border-white/10 pb-2">
              <i className="bi bi-activity text-blue-400"></i> Exercise Log
            </h3>
            {summary.exercises && summary.exercises.length > 0 ? (
              <div className="space-y-3">
                {summary.exercises.map((ex, idx) => {
                  const mistakesRaw = (ex as any).mistakes;
                  const mistakesList = mistakesRaw?.list || (Array.isArray(mistakesRaw) ? mistakesRaw : []);
                  const hasMismatch = mistakesList.some((m: any) => m.type === 'EXERCISE_MISMATCH');
                  const hasNoPose = mistakesList.some((m: any) => m.type === 'NO_POSE_DETECTED');
                  return (
                    <div key={idx} className={`flex flex-col bg-white/5 rounded-xl p-4 border transition-all ${hasMismatch ? 'border-orange-500/30' : 'border-white/5 hover:border-blue-500/20'}`}>
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-bold capitalize text-lg flex items-center gap-2">
                            {ex.exercise_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            {hasMismatch && (
                              <span className="text-[9px] font-black bg-orange-500/20 text-orange-400 border border-orange-500/30 px-2 py-0.5 rounded-full uppercase tracking-wider">
                                ⚠ Mismatch Detected
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-400 font-mono mt-1 flex gap-3">
                            <span>Form: <span className={getScoreColor(ex.form_score || 0)}>{Math.round(ex.form_score || 0)}%</span></span>
                            {ex.duration_seconds && <span>Duration: {Math.floor(ex.duration_seconds/60)}m {ex.duration_seconds%60}s</span>}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-black text-blue-400">{ex.reps_completed}</div>
                          <div className="text-[10px] text-gray-500 uppercase font-bold">reps</div>
                        </div>
                      </div>
                      {hasNoPose && (
                        <div className="mt-2 text-[10px] text-red-400 bg-red-500/10 rounded px-2 py-1 font-mono">
                          ⚠ No body pose detected — ensure full body is visible and well-lit
                        </div>
                      )}
                      {hasMismatch && (
                        <div className="mt-2 text-[10px] text-orange-300 bg-orange-500/10 rounded px-2 py-1">
                          {mistakesList.find((m: any) => m.type === 'EXERCISE_MISMATCH')?.suggestion}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-6 text-center border border-dashed border-white/10 rounded-xl">
                <i className="bi bi-camera-video text-2xl text-gray-600 block mb-2"></i>
                <p className="text-gray-500 text-sm font-mono">No exercises detected in video.<br/>Ensure your full body is visible.</p>
              </div>
            )}
            
            {summary.detailed_analysis && (
              <div className="mt-8 bg-blue-500/5 border border-blue-500/20 rounded-2xl p-6">
                <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <i className="bi bi-robot"></i> AI Performance Analysis
                </h4>
                <p className="text-sm text-gray-300 leading-relaxed italic">
                  "{summary.detailed_analysis}"
                </p>
                {summary.consistency_rating && (
                  <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                    <span className="text-[10px] text-gray-500 font-bold uppercase">Consistency Rating</span>
                    <span className="text-xs font-black text-blue-400 uppercase tracking-widest">{summary.consistency_rating}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Actionable Feedback & Insights */}
          <div className="space-y-6">
            <h3 className="text-sm font-black text-white tracking-widest uppercase mb-4 flex items-center gap-2 border-b border-white/10 pb-2">
              <i className="bi bi-lightning-charge text-yellow-400"></i> AI Coach Insights
            </h3>
            
            {(summary.strengths || summary.improvements) ? (
              <div className="space-y-4">
                {summary.strengths && (
                  <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 flex gap-4">
                    <i className="bi bi-star-fill text-green-400 mt-1"></i>
                    <div>
                      <div className="text-xs font-black text-green-400 uppercase tracking-widest mb-1">Strengths</div>
                      <p className="text-sm text-gray-300 leading-tight">{summary.strengths}</p>
                    </div>
                  </div>
                )}
                {summary.improvements && (
                  <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 flex gap-4">
                    <i className="bi bi-arrow-up-circle-fill text-blue-400 mt-1"></i>
                    <div>
                      <div className="text-xs font-black text-blue-400 uppercase tracking-widest mb-1">To Improve</div>
                      <p className="text-sm text-gray-300 leading-tight">{summary.improvements}</p>
                    </div>
                  </div>
                )}
              </div>
            ) : topMistakes.length > 0 ? (
              <div className="space-y-3">
                {topMistakes.map((mistake: any, idx: number) => (
                  <div key={idx} className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4 flex gap-4">
                    <div className="mt-1">
                      <i className="bi bi-exclamation-circle text-orange-400"></i>
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white capitalize mb-1">
                        {mistake.type.replace(/_/g, ' ')}
                      </div>
                      <div className="text-xs text-gray-300 leading-relaxed">
                        {mistake.suggestion}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6 flex items-center gap-4">
                <i className="bi bi-shield-check text-green-400 text-3xl"></i>
                <div>
                  <div className="text-sm font-bold text-white mb-1">Perfect Biometrics</div>
                  <div className="text-xs text-gray-300">No major form deviations detected during this session.</div>
                </div>
              </div>
            )}

            {summary.recommendations && summary.recommendations.length > 0 && (
              <div className="mt-6 bg-purple-500/5 border border-purple-500/10 rounded-xl p-4">
                 <div className="text-[10px] font-black text-purple-400 uppercase tracking-widest mb-2">Coach's Pro Tip</div>
                 <p className="text-xs text-purple-200/70 italic">"{summary.recommendations[0]}"</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer / Action */}
        <div className="pt-6 border-t border-white/10 text-center relative z-10">
          <button
            onClick={onClose}
            className="glow-button px-12 py-4 text-sm font-black tracking-widest uppercase inline-flex items-center gap-3"
          >
            <i className="bi bi-arrow-right-circle-fill"></i> Return to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

export default WorkoutSummary;