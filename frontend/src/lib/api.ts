/**
 * API utility functions
 */

import { WorkoutSummaryData } from '../types/workout';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function fetchWorkoutSummary(sessionId: string): Promise<WorkoutSummaryData> {
  const response = await fetch(`${API_BASE_URL}/api/workouts/${sessionId}/summary`, {
    headers: {
      // Add auth headers if needed
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch workout summary');
  }

  return response.json();
}
