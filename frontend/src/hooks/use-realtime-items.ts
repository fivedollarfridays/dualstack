import { useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from './use-websocket';

interface ItemEvent {
  type: string;
  data: { id: string; user_id: string };
}

export function useRealtimeItems() {
  const queryClient = useQueryClient();

  const onMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const parsed: ItemEvent = JSON.parse(event.data);
        if (parsed.type?.startsWith('item.')) {
          queryClient.invalidateQueries({ queryKey: ['items'] });
        }
      } catch {
        // Ignore non-JSON messages (e.g., pings)
      }
    },
    [queryClient]
  );

  return useWebSocket({ onMessage });
}
