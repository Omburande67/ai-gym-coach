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

  const response = await fetch(`${API_BASE_URL}/api/workouts/${sessionId}`, {
    headers,
  });

  if (!response.ok) {
    throw new Error('Failed to fetch workout summary: ' + response.status);
  }

  return response.json();
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