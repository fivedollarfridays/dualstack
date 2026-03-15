import { useEffect, useRef, useCallback, useState } from 'react';
import { useAppAuth } from '@/contexts/auth-context';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
const MAX_RETRIES = 5;
const BASE_DELAY_MS = 1000;

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

export interface UseWebSocketOptions {
  onMessage?: (event: MessageEvent) => void;
  enabled?: boolean;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { onMessage, enabled = true } = options;
  const { getToken } = useAppAuth();
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');

  const connect = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    const token = await getToken();
    if (!token) {
      setStatus('disconnected');
      return;
    }

    const ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      retriesRef.current = 0;
    };

    ws.onmessage = (event) => {
      onMessage?.(event);
    };

    ws.onclose = () => {
      setStatus('disconnected');
      wsRef.current = null;
      if (enabled && retriesRef.current < MAX_RETRIES) {
        const delay = BASE_DELAY_MS * Math.pow(2, retriesRef.current);
        retriesRef.current += 1;
        setTimeout(() => { if (enabled) connect(); }, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [getToken, onMessage, enabled]);

  useEffect(() => {
    if (!enabled) return;
    connect();
    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect, enabled]);

  return { status };
}
