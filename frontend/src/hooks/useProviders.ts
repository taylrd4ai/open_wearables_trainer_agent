import { useCallback, useEffect, useState } from 'react';

export interface ProviderStatus {
  name: string;
  connected: boolean | null;
  status: string;
}

interface ProvidersResponse {
  configured: boolean;
  providers: ProviderStatus[];
}

const API_BASE: string = import.meta.env.VITE_API_URL ?? '';

export function useProviders() {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [configured, setConfigured] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/providers`);
      if (!res.ok) throw new Error(`Provider list failed (${res.status})`);
      const data: ProvidersResponse = await res.json();
      setConfigured(Boolean(data.configured));
      setProviders(Array.isArray(data.providers) ? data.providers : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load providers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const connect = useCallback(
    async (name: string) => {
      setBusy(name);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/v1/providers/${name}/connect`, {
          method: 'POST',
        });
        if (!res.ok) throw new Error(`Connect failed (${res.status})`);
        const data = await res.json();
        if (typeof data.authorization_url === 'string' && data.authorization_url) {
          window.location.href = data.authorization_url;
          return; // browser leaves for the provider consent screen
        }
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Connect failed');
      } finally {
        setBusy(null);
      }
    },
    [refresh],
  );

  const disconnect = useCallback(
    async (name: string) => {
      setBusy(name);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/v1/providers/${name}/disconnect`, {
          method: 'POST',
        });
        if (!res.ok) throw new Error(`Disconnect failed (${res.status})`);
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Disconnect failed');
      } finally {
        setBusy(null);
      }
    },
    [refresh],
  );

  return { providers, configured, loading, error, busy, connect, disconnect, refresh };
}
