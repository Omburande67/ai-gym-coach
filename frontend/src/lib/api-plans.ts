import { WorkoutPlanResponse } from '@/types/workout';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

/**
 * Fetch the currently active workout plan for the user.
 */
export async function fetchActivePlan(): Promise<WorkoutPlanResponse | null> {
  const token = localStorage.getItem('token');
  if (!token) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/api/workouts/plan/active`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error('Failed to fetch active plan');
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching active plan:', error);
    return null;
  }
}

/**
 * Generate a new workout plan based on the user's profile.
 */
export async function generateWorkoutPlan(): Promise<WorkoutPlanResponse> {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Not authenticated');

  const response = await fetch(`${API_BASE_URL}/api/workouts/plan`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to generate workout plan');
  }

  return response.json();
}
