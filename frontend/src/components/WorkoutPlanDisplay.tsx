import React from 'react';
import { WorkoutPlanResponse, PlanDay, PlanExercise } from '@/types/workout';

interface WorkoutPlanDisplayProps {
  plan: WorkoutPlanResponse;
}

const ExerciseItem = ({ exercise }: { exercise: PlanExercise }) => (
  <li className="flex justify-between items-center py-3 border-b last:border-0 border-white/5 hover:bg-white/5 transition-colors px-2 rounded-lg group">
    <div className="flex items-center gap-3">
       <i className="bi bi-circle text-[8px] text-blue-500/50 group-hover:text-blue-500 transition-colors"></i>
       <span className="font-medium text-gray-300 text-sm">{exercise.name}</span>
    </div>
    <span className="text-xs text-gray-500 font-mono">
      {exercise.sets && `${exercise.sets}S x `}
      {exercise.reps && `${exercise.reps}R`}
      {exercise.duration && `${exercise.duration}`}
    </span>
  </li>
);

const DayCard = ({ day }: { day: PlanDay }) => (
  <div className="glass-card p-6 h-full border border-white/10 hover:border-blue-500/30 transition-all group">
    <div className="flex justify-between items-start mb-6">
      <div>
        <h3 className="text-xl font-black text-white group-hover:text-blue-400 transition-colors uppercase tracking-tight">{day.day}</h3>
        <p className="text-xs text-blue-400 font-black uppercase tracking-widest mt-1 flex items-center gap-2">
           <i className="bi bi-bullseye"></i> {day.focus}
        </p>
      </div>
      <div className="flex flex-col items-end gap-2">
        <span className="text-[10px] font-mono bg-white/5 text-gray-400 px-2 py-1 rounded border border-white/10">
          <i className="bi bi-alarm mr-1"></i> {day.total_duration}
        </span>
        <span className={`text-[9px] font-black px-2 py-1 rounded uppercase tracking-tighter border ${
          day.intensity === 'High' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
          day.intensity === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
          'bg-green-500/10 text-green-400 border-green-500/20'
        }`}>
          {day.intensity} Intensity
        </span>
      </div>
    </div>
    
    <div className="space-y-1">
      <div className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 flex items-center gap-2">
         <i className="bi bi-list-task"></i> Routine
      </div>
      <ul className="space-y-0">
        {day.exercises.map((exercise, idx) => (
          <ExerciseItem key={idx} exercise={exercise} />
        ))}
      </ul>
    </div>
  </div>
);

export const WorkoutPlanDisplay: React.FC<WorkoutPlanDisplayProps> = ({ plan }) => {
  if (!plan.plan_data || !plan.plan_data.days) {
    return (
      <div className="glass-card p-12 text-center border-red-500/20">
        <i className="bi bi-exclamation-octagon text-4xl text-red-500 mb-4"></i>
        <h3 className="text-xl font-bold text-white">Invalid Plan Data</h3>
        <p className="text-gray-500">The architecture of this plan is corrupted.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-end gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
             <i className="bi bi-calendar-check text-blue-500 text-2xl"></i>
             <h2 className="text-3xl font-black text-white uppercase tracking-tight">{plan.title}</h2>
          </div>
          <p className="text-gray-500 text-xs font-mono">
            ARCHIVE_ID: {plan.plan_id.slice(0, 8)}... • DEPLOYED: {new Date(plan.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20">
           <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
           <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Active Protocol</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plan.plan_data.days.map((day, idx) => (
          <DayCard key={idx} day={day} />
        ))}
      </div>
    </div>
  );
};
