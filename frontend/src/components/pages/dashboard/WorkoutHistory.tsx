import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ErrorState } from '../../ui/ErrorState';
import { useWorkouts } from '../../../hooks/useWorkouts';

export function WorkoutHistory() {
  const { data: workouts, isLoading, isError, refetch } = useWorkouts();

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorState message="Failed to load workouts" onRetry={() => void refetch()} />;
  if (!workouts || workouts.length === 0) {
    return <Card><p className="text-center text-gray-500">No workouts logged yet.</p></Card>;
  }

  return (
    <Card className="overflow-hidden p-0">
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-gray-100">Recent Workouts</h3>
      </div>
      <div className="divide-y divide-gray-800">
        {workouts.slice(0, 10).map((w) => (
          <div key={w.id} className="flex items-center justify-between p-4 hover:bg-gray-800/50 transition-colors">
            <div>
              <p className="font-medium text-gray-100">{w.type}</p>
              <p className="text-sm text-gray-500">{new Date(w.date).toLocaleDateString()}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-400">{w.duration_minutes} min</span>
              <span className="text-sm text-gray-400">{w.total_volume_kg} kg</span>
              <Badge variant={w.avg_rpe >= 8 ? 'danger' : w.avg_rpe >= 6 ? 'warning' : 'success'}>
                RPE {w.avg_rpe.toFixed(1)}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
