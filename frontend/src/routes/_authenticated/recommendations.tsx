import { createRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { Route as authenticatedRoute } from '../_authenticated';
import { getRecommendations } from '../../lib/api/services';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorState } from '../../components/ui/ErrorState';

const priorityVariant: Record<string, 'info' | 'warning' | 'danger'> = {
  low: 'info',
  medium: 'warning',
  high: 'danger',
};

function RecommendationsPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations,
  });

  if (isLoading) return <LoadingSpinner size="lg" />;
  if (isError) return <ErrorState message="Failed to load recommendations" onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">AI Coach Recommendations</h1>
        <p className="text-sm text-gray-400 mt-1">Personalized advice from your AI trainer</p>
      </div>
      {!data || data.length === 0 ? (
        <Card><p className="text-center text-gray-500 py-8">No recommendations yet. Keep training!</p></Card>
      ) : (
        <div className="space-y-4">
          {data.map((rec) => (
            <Card key={rec.id}>
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-100">{rec.title}</h3>
                <div className="flex gap-2">
                  <Badge>{rec.category}</Badge>
                  <Badge variant={priorityVariant[rec.priority] ?? 'info'}>{rec.priority}</Badge>
                </div>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">{rec.description}</p>
              <p className="text-xs text-gray-600 mt-3">{new Date(rec.created_at).toLocaleString()}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export const Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/recommendations',
  component: RecommendationsPage,
});
