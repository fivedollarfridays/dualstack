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
  const onMessageRef = useRef(onMessage);
  const enabledRef = useRef(enabled);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const authedRef = useRef(false);
  const tokenRef = useRef<string | null>(null);

  // Keep refs in sync without triggering reconnects
  onMessageRef.current = onMessage;
  enabledRef.current = enabled;

  const connect = useCallback(async () => {
    if (process.env.NODE_ENV === 'production' && WS_URL.startsWith('ws://')) {
      console.error('[Security] NEXT_PUBLIC_WS_URL must use wss:// in production');
      setStatus('disconnected');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    const token = await getToken();
    if (!token) {
      setStatus('disconnected');
      return;
    }

    tokenRef.current = token;
    authedRef.current = false;

    // Connect WITHOUT token in URL — use first-message auth pattern
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send auth message as first message
      ws.send(JSON.stringify({ type: 'auth', token: tokenRef.current }));
    };

    ws.onmessage = (event) => {
      if (!authedRef.current) {
        // First message must be auth_ok from server
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'auth_ok') {
            authedRef.current = true;
            setStatus('connected');
            retriesRef.current = 0;
            return;
          }
        } catch {
          // Not JSON — not auth_ok
        }
        // First message was not auth_ok — close
        ws.close();
        return;
      }
      // Authenticated — forward to handler
      onMessageRef.current?.(event);
    };

    ws.onclose = () => {
      setStatus('disconnected');
      wsRef.current = null;
      authedRef.current = false;
      if (enabledRef.current && retriesRef.current < MAX_RETRIES) {
        const delay = BASE_DELAY_MS * Math.pow(2, retriesRef.current);
        retriesRef.current += 1;
        setTimeout(() => { if (enabledRef.current) connect(); }, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [getToken]);

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
