import { createRoute } from '@tanstack/react-router';
import { Route as authenticatedRoute } from '../_authenticated';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';

const providers = [
  { name: 'Whoop', status: 'connected' as const },
  { name: 'Garmin', status: 'disconnected' as const },
  { name: 'Oura', status: 'disconnected' as const },
  { name: 'Apple Health', status: 'connected' as const },
  { name: 'Polar', status: 'disconnected' as const },
];

function SettingsPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Settings</h1>
        <p className="text-sm text-gray-400 mt-1">Manage connections and preferences</p>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-gray-100 mb-4">Wearable Providers</h2>
        <div className="space-y-3">
          {providers.map((p) => (
            <div key={p.name} className="flex items-center justify-between rounded-lg border border-gray-800 p-4">
              <div className="flex items-center gap-3">
                <span className="font-medium text-gray-200">{p.name}</span>
                <Badge variant={p.status === 'connected' ? 'success' : 'default'}>
                  {p.status}
                </Badge>
              </div>
              <Button variant={p.status === 'connected' ? 'danger' : 'secondary'} size="sm">
                {p.status === 'connected' ? 'Disconnect' : 'Connect'}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-gray-100 mb-4">AI Coach Persona</h2>
        <p className="text-sm text-gray-400 mb-4">Choose how your AI trainer communicates with you.</p>
        <div className="grid grid-cols-2 gap-3">
          {(['standard', 'encouraging', 'balanced', 'hard_ass'] as const).map((mode) => (
            <button
              key={mode}
              className="rounded-lg border border-gray-700 p-3 text-left text-sm font-medium text-gray-300 hover:border-primary-500 hover:text-primary-400 transition-colors capitalize"
            >
              {mode.replace('_', ' ')}
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
}

export const Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/settings',
  component: SettingsPage,
});
