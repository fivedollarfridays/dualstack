/**
 * Tests for useWebSocket hook.
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

describe('useWebSocket', () => {
  it('connects with auth token in query param', async () => {
    mockGetToken.mockResolvedValue('test-token');

    renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    expect(MockWebSocket.instances[0].url).toContain('token=test-token');
  });

  it('reports connected status after open', async () => {
    mockGetToken.mockResolvedValue('test-token');

    const { result } = renderHook(() => useWebSocket());

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
    });

    expect(result.current.status).toBe('connected');
  });

  it('calls onMessage when message received', async () => {
    mockGetToken.mockResolvedValue('test-token');
    const onMessage = jest.fn();

    renderHook(() => useWebSocket({ onMessage }));

    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBe(1);
    });

    act(() => {
      MockWebSocket.instances[0].simulateOpen();
      MockWebSocket.instances[0].simulateMessage('{"type":"item.created"}');
    });

    expect(onMessage).toHaveBeenCalledWith({ data: '{"type":"item.created"}' });
  });

  it('does not connect when no token', async () => {
    mockGetToken.mockResolvedValue(null);

    const { result } = renderHook(() => useWebSocket());

    // Wait for the async getToken to resolve
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
});
