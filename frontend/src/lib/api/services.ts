import apiClient from './client';
import type {
  DashboardStats,
  WorkoutSession,
  Recommendation,
  BiometricSummary,
  WorkoutLogRequest,
} from './types';

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>('/api/v1/dashboard/stats');
  return response.data;
}

export async function getWorkouts(): Promise<WorkoutSession[]> {
  const response = await apiClient.get<WorkoutSession[]>('/api/v1/workouts');
  return response.data;
}

export async function logWorkout(data: WorkoutLogRequest): Promise<WorkoutSession> {
  const response = await apiClient.post<WorkoutSession>('/api/v1/workouts', data);
  return response.data;
}

export async function getRecommendations(): Promise<Recommendation> {
  const response = await apiClient.get<Recommendation>('/api/v1/recommendations/workout');
  return response.data;
}

export async function getBiometricSummary(): Promise<BiometricSummary> {
  const response = await apiClient.get<BiometricSummary>('/api/v1/biometrics/summary');
  return response.data;
}
