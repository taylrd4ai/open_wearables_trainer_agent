export interface ExerciseEntry {
  name: string;
  sets: number;
  reps: number;
  weight_kg: number;
  rpe?: number;
  notes?: string;
}

export interface WorkoutSession {
  id: string;
  date: string;
  type: string;
  duration_minutes: number;
  exercises: ExerciseEntry[];
  total_volume_kg: number;
  avg_rpe: number;
  notes?: string;
}

export interface BiometricSummary {
  recovery_percentage: number;
  hrv_ms: number;
  strain_score: number;
  vo2_max: number;
  resting_hr: number;
  sleep_hours: number;
  sleep_quality: string;
  last_updated: string;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  category: 'workout' | 'recovery' | 'nutrition' | 'general';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
}

export interface DashboardStats {
  total_workouts: number;
  total_volume_kg: number;
  avg_rpe: number;
  recent_workouts: WorkoutSession[];
  biometrics: BiometricSummary;
  trainer_message: TrainerMessage;
  recommendations: Recommendation[];
}

export interface TrainerMessage {
  message: string;
  persona_mode: 'hard_ass' | 'encouraging' | 'balanced' | 'standard';
  timestamp: string;
}

export interface WorkoutLogRequest {
  date: string;
  type: string;
  duration_minutes: number;
  exercises: ExerciseEntry[];
  notes?: string;
}
