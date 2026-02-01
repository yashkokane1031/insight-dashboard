import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

interface DataPoint {
    id: number;
    name: string;
    value: number;
    timestamp: string;
}

interface WebSocketMessage {
    type: 'new_data';
    payload: DataPoint;
}

interface UseWebSocketReturn {
    latestValue: DataPoint | null;
    history: DataPoint[];
    isConnected: boolean;
    connectionError: string | null;
}

/**
 * Custom React hook for WebSocket connection to the InSight backend.
 * 
 * Features:
 * - Auto-connects with JWT token from AuthContext
 * - Parses incoming data points and maintains history
 * - Auto-reconnects on disconnect
 * - Provides connection status
 * 
 * Usage:
 * const { latestValue, history, isConnected } = useWebSocket();
 */
export function useWebSocket(maxHistoryLength: number = 50): UseWebSocketReturn {
    const { token } = useAuth();
    const [latestValue, setLatestValue] = useState<DataPoint | null>(null);
    const [history, setHistory] = useState<DataPoint[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | null>(null);

    // Fetch initial history via HTTP (for data before WebSocket connected)
    const fetchInitialHistory = useCallback(async () => {
        if (!token) return;

        try {
            const response = await fetch('http://127.0.0.1:8000/data/history', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data: DataPoint[] = await response.json();
                setHistory(data);
                if (data.length > 0) {
                    setLatestValue(data[data.length - 1]);
                }
            }
        } catch (error) {
            console.error('Error fetching initial history:', error);
        }
    }, [token]);

    // Connect to WebSocket
    const connect = useCallback(() => {
        if (!token) return;

        // Clear any existing connection
        if (wsRef.current) {
            wsRef.current.close();
        }

        const wsUrl = `ws://127.0.0.1:8000/ws?token=${token}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
            setConnectionError(null);
        };

        ws.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);

                if (message.type === 'new_data') {
                    const newDataPoint = message.payload;

                    // Update latest value
                    setLatestValue(newDataPoint);

                    // Add to history, keeping only the last N items
                    setHistory(prev => {
                        const updated = [...prev, newDataPoint];
                        return updated.slice(-maxHistoryLength);
                    });
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setConnectionError('WebSocket connection error');
        };

        ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            setIsConnected(false);

            // Auto-reconnect after 3 seconds (unless intentionally closed)
            if (event.code !== 1000) {
                reconnectTimeoutRef.current = window.setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, 3000);
            }
        };
    }, [token, maxHistoryLength]);

    // Initial connection and cleanup
    useEffect(() => {
        if (token) {
            fetchInitialHistory();
            connect();
        }

        return () => {
            // Cleanup on unmount
            if (wsRef.current) {
                wsRef.current.close(1000, 'Component unmounted');
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [token, connect, fetchInitialHistory]);

    return { latestValue, history, isConnected, connectionError };
}

export default useWebSocket;
