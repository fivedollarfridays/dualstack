/**
 * Tests for useWebSocket hook — first-message auth pattern.
 */
import { renderHook, act, waitFor } from '@testing-library/react';

// Mock auth context
const mockGetToken = jest.fn();
jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({ getToken: mockGetToken }),
}));

// Mock WebSocket
class MockWebSocket {
  static OPEN = 1;
  static instances: MockWebSocket[] = [];

  url: string;
  readyState = 0;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onerror: (() => void) | null = null;
  close = jest.fn(() => {
    this.readyState = 3;
  });
  send = jest.fn();

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  simulateOpen() {
    this.readyState = 1;
    this.onopen?.();
  }

  simulateMessage(data: string) {
    this.onmessage?.({ data });
  }
}

(global as unknown as { WebSocket: typeof MockWebSocket }).WebSocket = MockWebSocket;

import { useWebSocket } from './use-websocket';

beforeEach(() => {
  MockWebSocket.instances = [];
  mockGetToken.mockReset();
});

describe('useWebSocket — first-message auth', () => {
  it('connects WITHOUT token in URL query string', async () => {
    mockGetToken.mockResolvedValue('test-token');

    renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    // URL must NOT contain token query param
    expect(MockWebSocket.instances[0].url).not.toContain('token=');
    expect(MockWebSocket.instances[0].url).not.toContain('?');
  });

  it('sends auth message as first message after open', async () => {
    mockGetToken.mockResolvedValue('my-jwt-token');

    renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    expect(MockWebSocket.instances[0].send).toHaveBeenCalledWith(
      JSON.stringify({ type: 'auth', token: 'my-jwt-token' })
    );
  });

  it('transitions to connected only after auth_ok', async () => {
    mockGetToken.mockResolvedValue('test-token');

    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    // After open, should still be connecting (waiting for auth_ok)
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });
    expect(result.current.status).toBe('connecting');

    // After auth_ok, should be connected
    act(() => {
      MockWebSocket.instances[0].simulateMessage('{"type":"auth_ok"}');
    });
    expect(result.current.status).toBe('connected');
  });

  it('closes connection if first message is not auth_ok', async () => {
    mockGetToken.mockResolvedValue('test-token');

    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    // Server sends an error instead of auth_ok
    act(() => {
      MockWebSocket.instances[0].simulateMessage('{"type":"auth_error"}');
    });

    expect(MockWebSocket.instances[0].close).toHaveBeenCalled();
  });

  it('forwards messages to onMessage after auth_ok', async () => {
    mockGetToken.mockResolvedValue('test-token');
    const onMessage = jest.fn();

    renderHook(() => useWebSocket({ onMessage }));

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.simulateOpen();
    });

    // auth_ok should NOT be forwarded to onMessage
    act(() => {
      ws.simulateMessage('{"type":"auth_ok"}');
    });
    expect(onMessage).not.toHaveBeenCalled();

    // Subsequent messages should be forwarded
    act(() => {
      ws.simulateMessage('{"type":"item.created"}');
    });
    expect(onMessage).toHaveBeenCalledWith({ data: '{"type":"item.created"}' });
  });

  it('does not connect when no token', async () => {
    mockGetToken.mockResolvedValue(null);

    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(result.current.status).toBe('disconnected');
    });

    expect(MockWebSocket.instances.length).toBe(0);
  });

  it('does not connect when disabled', () => {
    mockGetToken.mockResolvedValue('test-token');

    renderHook(() => useWebSocket({ enabled: false }));

    expect(MockWebSocket.instances.length).toBe(0);
  });

  it('sets status to disconnected on close and retries with backoff', async () => {
    jest.useFakeTimers();
    mockGetToken.mockResolvedValue('test-token');

    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    const ws1 = MockWebSocket.instances[0];
    act(() => {
      ws1.simulateOpen();
      ws1.simulateMessage('{"type":"auth_ok"}');
    });
    expect(result.current.status).toBe('connected');

    // Simulate close
    act(() => {
      ws1.onclose?.();
    });
    expect(result.current.status).toBe('disconnected');

    // Advance timer past the first retry delay (1000ms * 2^0 = 1000ms)
    await act(async () => {
      jest.advanceTimersByTime(1100);
    });

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(2);
    });

    jest.useRealTimers();
  });

  it('closes socket on error', async () => {
    mockGetToken.mockResolvedValue('test-token');

    renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    const ws = MockWebSocket.instances[0];
    act(() => {
      ws.onerror?.();
    });

    expect(ws.close).toHaveBeenCalled();
  });

  it('skips reconnect when socket is already open', async () => {
    mockGetToken.mockResolvedValue('test-token');

    const onMessage1 = jest.fn();
    const { result, rerender } = renderHook(
      ({ onMsg }: { onMsg: (e: MessageEvent) => void }) =>
        useWebSocket({ onMessage: onMsg }),
      { initialProps: { onMsg: onMessage1 } }
    );

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    const ws = MockWebSocket.instances[0];
    act(() => {
      ws.simulateOpen();
      ws.simulateMessage('{"type":"auth_ok"}');
    });
    expect(result.current.status).toBe('connected');

    const onMessage2 = jest.fn();
    rerender({ onMsg: onMessage2 });

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });
  });

  it('does not call onMessage when no handler provided', async () => {
    mockGetToken.mockResolvedValue('test-token');

    renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    // Should not throw when onMessage is called without handler
    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateMessage('{"type":"auth_ok"}');
      MockWebSocket.instances[0].simulateMessage('test');
    });
  });

  it('stops retrying after MAX_RETRIES', async () => {
    jest.useFakeTimers();
    mockGetToken.mockResolvedValue('test-token');

    renderHook(() => useWebSocket());

    for (let i = 0; i < 5; i++) {
      await waitFor(() => {
        expect(MockWebSocket.instances.length).toBe(i + 1);
      });
      act(() => {
        MockWebSocket.instances[i].onclose?.();
      });
      await act(async () => {
        jest.advanceTimersByTime(2000 * Math.pow(2, i));
      });
    }

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(6);
    });

    // Close the 6th - should NOT retry
    const countBefore = MockWebSocket.instances.length;
    act(() => {
      MockWebSocket.instances[5].onclose?.();
    });
    await act(async () => {
      jest.advanceTimersByTime(100000);
    });

    expect(MockWebSocket.instances.length).toBe(countBefore);
    jest.useRealTimers();
  });

  it('refuses to connect on ws:// in production', async () => {
    mockGetToken.mockResolvedValue('test-token');
    const originalEnv = process.env.NODE_ENV;

    process.env.NODE_ENV = 'production';

    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(result.current.status).toBe('disconnected');
    });

    expect(MockWebSocket.instances.length).toBe(0);

    process.env.NODE_ENV = originalEnv;
  });

  it('cleans up socket on unmount', async () => {
    mockGetToken.mockResolvedValue('test-token');

    const { unmount } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateMessage('{"type":"auth_ok"}');
    });

    unmount();
    expect(MockWebSocket.instances[0].close).toHaveBeenCalled();
  });
});
