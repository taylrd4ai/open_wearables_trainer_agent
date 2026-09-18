import { useDashboard } from '../../../hooks/useDashboard';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ErrorState } from '../../ui/ErrorState';
import { StatsCard } from './StatsCard';
import { BiometricCards } from './BiometricCards';
import { WorkoutHistory } from './WorkoutHistory';
import { TrainerMessage } from './TrainerMessage';

export function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboard();

  if (isLoading) return <LoadingSpinner size="lg" />;
  if (isError) return <ErrorState message="Failed to load dashboard" onRetry={() => void refetch()} />;
  if (!data) return <ErrorState message="No data available" />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Dashboard</h1>
        <p className="text-sm text-gray-400 mt-1">Your training overview</p>
      </div>

      <TrainerMessage data={data.trainer_message} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <StatsCard
          title="Total Workouts"
          value={data.total_workouts}
          icon={<svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
        />
        <StatsCard
          title="Total Volume"
          value={`${data.total_volume_kg.toLocaleString()} kg`}
          icon={<svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>}
        />
        <StatsCard
          title="Avg RPE"
          value={data.avg_rpe.toFixed(1)}
          subtitle="Rate of Perceived Exertion"
          icon={<svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
        />
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-100 mb-3">Biometrics</h2>
        <BiometricCards />
      </div>

      <WorkoutHistory />
    </div>
  );
}
