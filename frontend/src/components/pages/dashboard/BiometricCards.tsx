import { Card } from '../../ui/Card';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ErrorState } from '../../ui/ErrorState';
import { useBiometrics } from '../../../hooks/useBiometrics';

export function BiometricCards() {
  const { data, isLoading, isError, refetch } = useBiometrics();

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorState message="Failed to load biometrics" onRetry={() => void refetch()} />;
  if (!data) return null;

  const fmt = (v: unknown, decimals = 1): string =>
    typeof v === 'number' && !Number.isNaN(v) ? v.toFixed(decimals) : '—';

  const metrics = [
    { label: 'Recovery', value: `${fmt(data.recovery_percentage, 0)}%`, color: 'text-green-400' },
    { label: 'HRV', value: `${fmt(data.hrv_ms, 0)} ms`, color: 'text-blue-400' },
    { label: 'Strain', value: fmt(data.strain_score), color: 'text-orange-400' },
    { label: 'VO2 Max', value: fmt(data.vo2_max), color: 'text-purple-400' },
    { label: 'Resting HR', value: `${fmt(data.resting_hr, 0)} bpm`, color: 'text-red-400' },
    { label: 'Sleep', value: `${fmt(data.sleep_hours)}h`, color: 'text-indigo-400' },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
      {metrics.map((m) => (
        <Card key={m.label} className="text-center">
          <p className="text-xs font-medium text-gray-400">{m.label}</p>
          <p className={`mt-2 text-xl font-bold ${m.color}`}>{m.value}</p>
        </Card>
      ))}
    </div>
  );
}
