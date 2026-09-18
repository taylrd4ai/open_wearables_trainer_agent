import { useQuery } from '@tanstack/react-query';
import { getWorkouts } from '../lib/api/services';

export function useWorkouts() {
  return useQuery({
    queryKey: ['workouts'],
    queryFn: getWorkouts,
    staleTime: 60_000,
  });
}
