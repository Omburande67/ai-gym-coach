const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface UserProfile {
  user_id: string;
  email: string;
  weight_kg: number | null;
  height_cm: number | null;
  body_type: string | null;
  fitness_goals: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface UserStatistics {
  total_workouts: number;
  total_reps: number;
  average_form_score: number;
  current_streak: number;
  longest_streak: number;
  last_workout_date: string | null;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  workout_residues: boolean;
  daily_reminder_time: string | null;
}

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Not authenticated');

  const res = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
     const error = await res.json().catch(() => ({}));
     throw new Error(error.detail || 'API request failed');
  }
  return res.json();
}

export async function getProfile(): Promise<UserProfile> {
  return fetchWithAuth('/api/users/profile');
}

export async function updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  return fetchWithAuth('/api/users/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getStatistics(): Promise<UserStatistics> {
  return fetchWithAuth('/api/users/statistics');
}

export async function getPreferences(): Promise<NotificationPreferences> {
  return fetchWithAuth('/api/users/preferences');
}

export async function updatePreferences(data: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
  return fetchWithAuth('/api/users/preferences', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
