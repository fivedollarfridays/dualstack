/**
 * Tests for useRealtimeItems hook.
 */
import { renderHook, act } from '@testing-library/react';
// Track the onMessage callback passed to useWebSocket
let capturedOnMessage: ((event: { data: string }) => void) | undefined;

jest.mock('./use-websocket', () => ({
  useWebSocket: (opts: { onMessage?: (event: { data: string }) => void }) => {
    capturedOnMessage = opts?.onMessage;
    return { status: 'connected' as const };
  },
}));

const mockInvalidateQueries = jest.fn();
jest.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({
    invalidateQueries: mockInvalidateQueries,
  }),
}));

import { useRealtimeItems } from './use-realtime-items';

beforeEach(() => {
  mockInvalidateQueries.mockReset();
  capturedOnMessage = undefined;
});

describe('useRealtimeItems', () => {
  it('invalidates items query on item.created event', () => {
    renderHook(() => useRealtimeItems());

    act(() => {
      capturedOnMessage?.({ data: JSON.stringify({ type: 'item.created', data: { id: '1', user_id: 'u1' } }) });
    });

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['items'] });
  });

  it('invalidates items query on item.deleted event', () => {
    renderHook(() => useRealtimeItems());

    act(() => {
      capturedOnMessage?.({ data: JSON.stringify({ type: 'item.deleted', data: { id: '2', user_id: 'u1' } }) });
    });

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['items'] });
  });

  it('does not invalidate on non-item events', () => {
    renderHook(() => useRealtimeItems());

    act(() => {
      capturedOnMessage?.({ data: JSON.stringify({ type: 'user.updated', data: {} }) });
    });

    expect(mockInvalidateQueries).not.toHaveBeenCalled();
  });

  it('ignores non-JSON messages', () => {
    renderHook(() => useRealtimeItems());

    act(() => {
      capturedOnMessage?.({ data: 'not json' });
    });

    expect(mockInvalidateQueries).not.toHaveBeenCalled();
  });

  it('ignores events with no type field', () => {
    renderHook(() => useRealtimeItems());

    act(() => {
      capturedOnMessage?.({ data: JSON.stringify({ data: { id: '1' } }) });
    });

    expect(mockInvalidateQueries).not.toHaveBeenCalled();
  });
});
