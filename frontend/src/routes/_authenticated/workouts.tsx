import { createRoute } from '@tanstack/react-router';
import { Route as authenticatedRoute } from '../_authenticated';
import { useWorkouts } from '../../hooks/useWorkouts';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorState } from '../../components/ui/ErrorState';

function WorkoutsPage() {
  const { data: workouts, isLoading, isError, refetch } = useWorkouts();

  if (isLoading) return <LoadingSpinner size="lg" />;
  if (isError) return <ErrorState message="Failed to load workouts" onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Workout History</h1>
        <p className="text-sm text-gray-400 mt-1">All your logged sessions</p>
      </div>
      {!workouts || workouts.length === 0 ? (
        <Card><p className="text-center text-gray-500 py-8">No workouts logged yet. Start training!</p></Card>
      ) : (
        <div className="space-y-3">
          {workouts.map((w) => (
            <Card key={w.id} className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-gray-100">{w.type}</p>
                <p className="text-sm text-gray-500">{new Date(w.date).toLocaleDateString()} &middot; {w.duration_minutes} min</p>
                <p className="text-xs text-gray-600 mt-1">{w.exercises.length} exercises &middot; {w.total_volume_kg} kg total</p>
              </div>
              <Badge variant={w.avg_rpe >= 8 ? 'danger' : w.avg_rpe >= 6 ? 'warning' : 'success'}>
                RPE {w.avg_rpe.toFixed(1)}
              </Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export const Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/workouts',
  component: WorkoutsPage,
});
