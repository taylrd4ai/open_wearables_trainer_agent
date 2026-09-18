import { Card } from '../../ui/Card';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ErrorState } from '../../ui/ErrorState';
import { useBiometrics } from '../../../hooks/useBiometrics';

export function BiometricCards() {
  const { data, isLoading, isError, refetch } = useBiometrics();

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorState message="Failed to load biometrics" onRetry={() => void refetch()} />;
  if (!data) return null;

  const metrics = [
    { label: 'Recovery', value: `${data.recovery_percentage}%`, color: 'text-green-400' },
    { label: 'HRV', value: `${data.hrv_ms} ms`, color: 'text-blue-400' },
    { label: 'Strain', value: data.strain_score.toFixed(1), color: 'text-orange-400' },
    { label: 'VO2 Max', value: data.vo2_max.toFixed(1), color: 'text-purple-400' },
    { label: 'Resting HR', value: `${data.resting_hr} bpm`, color: 'text-red-400' },
    { label: 'Sleep', value: `${data.sleep_hours}h`, color: 'text-indigo-400' },
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
