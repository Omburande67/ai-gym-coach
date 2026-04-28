/**
 * API utility functions
 */

import { WorkoutSummaryData } from '../types/workout';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Get auth token from localStorage (using correct key)
const getAuthHeader = (): Record<string, string> => {
  // Try both possible token keys that the backend might use
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  console.log('🔑 Token found:', token ? 'Yes' : 'No');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

/**
 * Fetch workout summary after session is saved
 */
export async function fetchWorkoutSummary(sessionId: string): Promise<WorkoutSummaryData> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
  };

  // Use the /summary endpoint which returns the full AI-powered coaching report
  const response = await fetch(`${API_BASE_URL}/api/workouts/${sessionId}/summary`, {
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to fetch workout summary: ' + response.status);
  }

  const data = await response.json();
  // Normalize response into WorkoutSummaryData shape
  return {
    session_id: data.session_id || sessionId,
    total_reps: data.total_reps || 0,
    total_duration_seconds: data.total_duration_seconds || 0,
    average_form_score: data.average_form_score || 0,
    top_mistakes: data.top_mistakes || [],
    recommendations: data.recommendations || [],
    exercises: data.exercises || [],
    detailed_analysis: data.detailed_analysis,
    strengths: data.strengths,
    improvements: data.improvements,
    consistency_rating: data.consistency_rating,
    total_workouts: data.total_workouts || 0,
    current_streak: data.current_streak || 0,
    longest_streak: data.longest_streak || 0,
    exercise_breakdown: data.exercise_breakdown || {},
  };
}

/**
 * Save workout session to backend
 */
export async function saveWorkoutSession(sessionData: any): Promise<any> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
  };

  console.log('📤 Saving workout with headers:', headers);
  console.log('📦 Session data:', sessionData);

  const response = await fetch(`${API_BASE_URL}/api/workouts`, {
    method: 'POST',
    headers,
    body: JSON.stringify(sessionData),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('❌ Save failed:', response.status, errorText);
    throw new Error('Failed to save workout: ' + response.status + ' - ' + errorText);
  }

  const result = await response.json();
  console.log('✅ Save successful:', result);
  return result;
}

/**
 * Get user's workout history
 */
export async function getWorkoutHistory(limit: number = 50, offset: number = 0): Promise<any[]> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
  };

  const response = await fetch(`${API_BASE_URL}/api/workouts?limit=${limit}&offset=${offset}`, {
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to fetch workout history: ' + response.status);
  }

  return response.json();
}

/**
 * Get user's workout statistics
 */
export async function getWorkoutStatistics(): Promise<any> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
  };

  const response = await fetch(`${API_BASE_URL}/api/workouts/statistics`, {
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to fetch statistics: ' + response.status);
  }

  return response.json();
}

/**
 * Delete a workout session
 */
export async function deleteWorkoutSession(sessionId: string): Promise<void> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
  };

  const response = await fetch(`${API_BASE_URL}/api/workouts/${sessionId}`, {
    method: 'DELETE',
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to delete workout: ' + response.status);
  }
}

/**
 * Analyze an uploaded video file for workout data
 */
export async function analyzeVideoFile(file: File, exerciseType?: string): Promise<WorkoutSummaryData> {
  const formData = new FormData();
  formData.append('file', file);
  if (exerciseType) {
    formData.append('exercise_type', exerciseType);
  }

  const headers = getAuthHeader();

  const response = await fetch(`${API_BASE_URL}/api/workouts/analyze-video`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to analyze video: ${response.status} - ${errorText}`);
  }

  const data = await response.json();
  // Normalize API WorkoutSummary into WorkoutSummaryData shape
  return {
    session_id: data.session_id || '',
    total_reps: data.total_reps || 0,
    total_duration_seconds: data.total_duration_seconds || 0,
    average_form_score: data.average_form_score || 0,
    top_mistakes: data.top_mistakes || [],
    recommendations: data.recommendations || [],
    exercises: data.exercises || [],
    detailed_analysis: data.detailed_analysis,
    strengths: data.strengths,
    improvements: data.improvements,
    consistency_rating: data.consistency_rating,
    total_workouts: 0,
    current_streak: 0,
    longest_streak: 0,
    exercise_breakdown: {},
  };
}