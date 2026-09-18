import { useQuery } from '@tanstack/react-query';
import { getDashboardStats } from '../lib/api/services';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    staleTime: 30_000,
  });
}
