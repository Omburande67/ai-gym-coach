/**
 * Camera Placement Tutorial Component
 * 
 * Implements Requirements 5.1, 5.2, 5.3, 5.4:
 * - Display tutorial modal on first workout session
 * - Show distance guidance (2.5-3 meters)
 * - Show height guidance (waist level)
 * - Show exercise-specific camera angles
 */

'use client';

import React, { useState } from 'react';

export type ExerciseType = 'pushup' | 'squat' | 'plank' | 'jumping_jack';

export interface CameraPlacementTutorialProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  exerciseType?: ExerciseType;
}

interface CameraGuidance {
  distance: string;
  height: string;
  angle: string;
  tips: string[];
}

const GENERAL_GUIDANCE: CameraGuidance = {
  distance: '2.5-3 meters (8-10 feet)',
  height: 'Waist level',
  angle: 'Straight ahead, perpendicular to your body',
  tips: [
    'Ensure your entire body is visible in the frame',
    'Use good lighting - avoid backlighting from windows',
    'Clear the area around you for safe movement',
    'Position camera on a stable surface or tripod',
  ],
};

const EXERCISE_SPECIFIC_GUIDANCE: Record<ExerciseType, CameraGuidance> = {
  pushup: {
    distance: '2.5-3 meters (8-10 feet)',
    height: 'Waist level when standing',
    angle: 'Side view - camera perpendicular to your body',
    tips: [
      'Position camera to your side, not in front',
      'Ensure both hands and feet are visible',
      'Camera should capture your full body from head to toe',
      'Side angle allows tracking of elbow and hip alignment',
    ],
  },
  squat: {
    distance: '2.5-3 meters (8-10 feet)',
    height: 'Waist level',
    angle: 'Front or side view - 45° angle works best',
    tips: [
      'Front view helps track knee alignment',
      'Side view helps track depth and back angle',
      'Ensure full body visible from head to feet',
      'Camera should capture hip, knee, and ankle joints clearly',
    ],
  },
  plank: {
    distance: '2.5-3 meters (8-10 feet)',
    height: 'Floor level to waist level',
    angle: 'Side view - camera perpendicular to your body',
    tips: [
      'Position camera to your side for best hip tracking',
      'Ensure shoulders, hips, and feet are all visible',
      'Lower camera angle helps track body alignment',
      'Side angle is critical for detecting hip sag or pike',
    ],
  },
  jumping_jack: {
    distance: '3-3.5 meters (10-12 feet)',
    height: 'Waist level',
    angle: 'Front view - camera facing you directly',
    tips: [
      'Need more distance due to arm and leg movements',
      'Front view captures full range of arm and leg motion',
      'Ensure arms can extend fully overhead without leaving frame',
      'Legs should be visible when spread wide',
    ],
  },
};

export function CameraPlacementTutorial({
  isOpen,
  onClose,
  onComplete,
  exerciseType,
}: CameraPlacementTutorialProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [showExerciseSpecific, setShowExerciseSpecific] = useState(false);

  if (!isOpen) return null;

  const guidance = exerciseType && showExerciseSpecific
    ? EXERCISE_SPECIFIC_GUIDANCE[exerciseType]
    : GENERAL_GUIDANCE;

  const handleNext = () => {
    if (exerciseType && !showExerciseSpecific) {
      setShowExerciseSpecific(true);
    } else {
      onComplete();
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-xl flex items-center justify-center z-[100] p-4 animate-in fade-in duration-500">
      <div className="glass-card shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col relative border border-white/20">
        <div className="neural-pattern opacity-20" />
        
        {/* Header */}
        <div className="p-8 relative z-10 border-b border-white/10 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
              <i className="bi bi-camera-video text-blue-400"></i>
              {showExerciseSpecific && exerciseType
                ? `${exerciseType.replace('_', ' ').toUpperCase()} SETUP`
                : 'HARDWARE LINK GUIDE'}
            </h2>
            <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
              <i className="bi bi-x-lg text-xl"></i>
            </button>
          </div>
          <p className="text-gray-400 text-sm font-medium tracking-wide">
            ESTABLISHING OPTIMAL BIOMETRIC LINE-OF-SIGHT
          </p>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8 overflow-y-auto relative z-10 custom-scrollbar">
          {/* Guidance Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Distance Guidance */}
            <div className="bg-white/5 p-6 rounded-2xl border border-white/10 hover:border-blue-500/30 transition-all group">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i className="bi bi-rulers text-blue-400 text-xl"></i>
                </div>
                <h3 className="font-black text-white tracking-widest text-xs uppercase opacity-60">Optimal Distance</h3>
              </div>
              <p className="text-xl font-bold text-white mb-1">{guidance.distance}</p>
              <p className="text-xs text-gray-500 leading-relaxed">
                Clear space between sensors and biomechanical markers.
              </p>
            </div>

            {/* Height Guidance */}
            <div className="bg-white/5 p-6 rounded-2xl border border-white/10 hover:border-green-500/30 transition-all group">
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i className="bi bi-layout-sidebar-inset text-green-400 text-xl"></i>
                </div>
                <h3 className="font-black text-white tracking-widest text-xs uppercase opacity-60">Sensor Height</h3>
              </div>
              <p className="text-xl font-bold text-white mb-1">{guidance.height}</p>
              <p className="text-xs text-gray-500 leading-relaxed">
                Position hardware lens at central pelvic point when upright.
              </p>
            </div>
          </div>

          {/* Angle Guidance */}
          <div className="bg-white/5 p-6 rounded-2xl border border-white/10 hover:border-purple-500/30 transition-all group">
            <div className="flex items-center gap-4 mb-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <i className="bi bi-aspect-ratio text-purple-400 text-xl"></i>
              </div>
              <h3 className="font-black text-white tracking-widest text-xs uppercase opacity-60">Field of View</h3>
            </div>
            <p className="text-xl font-bold text-white mb-1">{guidance.angle}</p>
            <p className="text-xs text-gray-500 leading-relaxed">
              {showExerciseSpecific && exerciseType
                ? 'Dynamic vector tracking engaged for this movement pattern.'
                : 'Ensure clear FOV with no geometric obstructions.'}
            </p>
          </div>

          {/* Tips List */}
          <div className="space-y-4">
             <h3 className="font-black text-white text-xs tracking-widest uppercase opacity-40 flex items-center gap-3">
               PRE-INIT CHECKLIST <div className="flex-1 h-[1px] bg-white/5" />
             </h3>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
               {guidance.tips.map((tip, index) => (
                 <div key={index} className="flex items-start gap-3 bg-white/5 p-4 rounded-xl border border-white/5">
                   <i className="bi bi-check2-circle text-blue-400 mt-0.5"></i>
                   <span className="text-sm text-gray-300 font-medium leading-snug">{tip}</span>
                 </div>
               ))}
             </div>
          </div>

          {/* Visual Setup */}
          <div className="bg-white/5 p-8 rounded-3xl border border-white/10 flex flex-col items-center">
             <div className="flex justify-between items-center w-full max-w-sm relative">
                <div className="flex flex-col items-center gap-2 group">
                   <div className="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center group-hover:bg-blue-500/20 transition-all">
                    <i className="bi bi-phone-vibrate text-3xl text-blue-400"></i>
                   </div>
                   <span className="text-[10px] font-black text-gray-500 tracking-widest">SENSOR</span>
                </div>

                <div className="flex-1 border-t-2 border-dashed border-white/10 mx-4 relative">
                   <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#0a0e27] px-3 py-1 rounded-full border border-white/10 whitespace-nowrap">
                      <span className="text-[10px] font-mono text-blue-400">{guidance.distance}</span>
                   </div>
                </div>

                <div className="flex flex-col items-center gap-2 group">
                   <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-all overflow-hidden border border-white/5">
                      <i className="bi bi-person text-4xl text-purple-400"></i>
                   </div>
                   <span className="text-[10px] font-black text-gray-500 tracking-widest">ATHLETE</span>
                </div>
             </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-8 border-t border-white/10 bg-white/5 flex gap-4 relative z-10">
          <button
            onClick={handleSkip}
            className="px-6 py-4 text-gray-500 hover:text-white transition-all text-sm font-black tracking-widest uppercase"
          >
            DISMISS
          </button>
          <div className="flex-1 flex gap-3">
            {exerciseType && !showExerciseSpecific && (
              <button
                onClick={handleNext}
                className="flex-1 py-4 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-xl font-black tracking-widest uppercase transition-all"
              >
                DETAILED {exerciseType.replace('_', ' ')} SETUP
              </button>
            )}
            <button
              onClick={handleNext}
              className="glow-button flex-1 py-4 text-sm font-black tracking-widest uppercase"
            >
              {showExerciseSpecific || !exerciseType ? 'LINK ESTABLISHED' : 'NEXT STEP'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
