import { useQuery } from '@tanstack/react-query';
import { getBiometricSummary } from '../lib/api/services';

export function useBiometrics() {
  return useQuery({
    queryKey: ['biometrics'],
    queryFn: getBiometricSummary,
    staleTime: 60_000,
  });
}
