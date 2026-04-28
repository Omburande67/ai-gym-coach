/**
 * Workout and Exercise Types
 */

export enum ExerciseType {
  PUSHUP = 'pushup',
  SQUAT = 'squat',
  PLANK = 'plank',
  JUMPING_JACK = 'jumping_jack',
  UNKNOWN = 'unknown',
}

export interface ExerciseRecord {
  record_id: string;
  session_id: string;
  exercise_type: ExerciseType | string;
  reps_completed: number;
  duration_seconds?: number;
  form_score?: number;
  mistakes?: FormMistake[];
  created_at: string;
}

export interface FormMistake {
  type: string;
  severity: number;
  suggestion: string;
  count?: number;
}

export interface WorkoutSession {
  session_id: string;
  user_id: string;
  start_time: string;
  end_time?: string;
  total_duration_seconds?: number;
  total_reps: number;
  average_form_score?: number;
  created_at: string;
  exercise_records: ExerciseRecord[];
}

export interface WorkoutSummaryData {
  total_workouts: number;
  current_streak: number;
  longest_streak: number;
  exercise_breakdown: {};
  session_id: string;
  total_reps: number;
  total_duration_seconds: number;
  average_form_score: number;
  top_mistakes: FormMistake[];
  recommendations: string[];
  exercises: ExerciseRecord[];
  detailed_analysis?: string;
  strengths?: string;
  improvements?: string;
  consistency_rating?: string;
}
export interface PlanExercise {
  name: string;
  sets?: number;
  reps?: number | string;
  duration?: string;
  notes?: string;
}

export interface PlanDay {
  day: string;
  focus: string;
  exercises: PlanExercise[];
  total_duration?: string;
  intensity?: string;
}

export interface WorkoutPlanData {
  title: string;
  description?: string;
  days: PlanDay[];
}

export interface WorkoutPlanResponse {
  plan_id: string;
  user_id: string;
  title: string;
  plan_data: WorkoutPlanData;
  is_active: boolean;
  created_at: string;
}
