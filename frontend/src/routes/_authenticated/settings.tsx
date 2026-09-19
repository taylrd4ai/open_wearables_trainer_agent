import { useMemo } from 'react';
import { createRoute } from '@tanstack/react-router';
import { Route as authenticatedRoute } from '../_authenticated';
import { useProviders, type ProviderStatus } from '../../hooks/useProviders';

function displayName(name: string): string {
  return name.charAt(0).toUpperCase() + name.slice(1);
}

function badgeClasses(p: ProviderStatus): string {
  if (p.connected === true) return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
  if (p.connected === false) return 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30';
  return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
}

function badgeLabel(p: ProviderStatus): string {
  if (p.connected === true) return 'Connected';
  if (p.connected === false) return 'Disconnected';
  return 'Unknown';
}

function SettingsPage() {
  const { providers, configured, loading, error, busy, connect, disconnect, refresh } =
    useProviders();

  const justConnected = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    const value = params.get('connected');
    // Clean the query string so a refresh doesn't re-show the banner
    if (value) window.history.replaceState(null, '', window.location.pathname);
    return value;
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-zinc-400">Manage wearable connections and preferences</p>
      </header>

      {justConnected ? (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-300">
          {displayName(justConnected)} authorization finished — waiting for Open Wearables to
          complete the first sync.
        </div>
      ) : null}

      {!configured && !loading ? (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-300">
          Open Wearables is not configured on the backend. Set OPEN_WEARABLES_API_KEY and
          OPEN_WEARABLES_USER_ID in the backend .env, then restart the backend container.
        </div>
      ) : null}

      {error ? (
        <div className="flex items-center justify-between rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
          <span>{error}</span>
          <button
            type="button"
            onClick={() => void refresh()}
            className="rounded border border-red-500/40 px-2 py-1 text-xs hover:bg-red-500/20"
          >
            Retry
          </button>
        </div>
      ) : null}

      <section className="rounded-lg border border-zinc-700/60">
        {loading ? (
          <div className="p-6 text-sm text-zinc-400">Loading provider status…</div>
        ) : providers.length === 0 ? (
          <div className="p-6 text-sm text-zinc-400">No providers available.</div>
        ) : (
          providers.map((p) => (
            <div
              key={p.name}
              className="flex items-center justify-between gap-4 border-b border-zinc-700/60 p-4 last:border-b-0"
            >
              <div className="flex items-center gap-3">
                <span className="font-medium">{displayName(p.name)}</span>
                <span
                  className={`rounded-full border px-2 py-0.5 text-xs ${badgeClasses(p)}`}
                >
                  {badgeLabel(p)}
                </span>
              </div>
              {p.connected === true ? (
                <button
                  type="button"
                  disabled={busy !== null}
                  onClick={() => void disconnect(p.name)}
                  className="rounded-md border border-zinc-600 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700/50 disabled:opacity-50"
                >
                  {busy === p.name ? 'Disconnecting…' : 'Disconnect'}
                </button>
              ) : (
                <button
                  type="button"
                  disabled={busy !== null || !configured}
                  onClick={() => void connect(p.name)}
                  className="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy === p.name ? 'Connecting…' : 'Connect'}
                </button>
              )}
            </div>
          ))
        )}
      </section>

      <p className="text-xs text-zinc-500">
        Connecting redirects you to the provider&apos;s own consent screen (via Open Wearables).
        Apple Health is intentionally not listed — HealthKit is only reachable from an iOS
        application, not a web backend.
      </p>
    </div>
  );
}

export const Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/settings',
  component: SettingsPage,
});
