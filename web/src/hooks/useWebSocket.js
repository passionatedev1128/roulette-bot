import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url, onEvent) => {
  const handlerRef = useRef(onEvent);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // 'connected', 'disconnected', 'connecting'
  const wsRef = useRef(null);

  useEffect(() => {
    handlerRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!url) {
      setConnectionStatus('disconnected');
      return () => undefined;
    }

    let ws;
    let reconnectTimeout;

    const connect = () => {
      try {
        setConnectionStatus('connecting');
        ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected:', url);
          setConnectionStatus('connected');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handlerRef.current?.(data);
          } catch (error) {
            console.warn('WebSocket message parse error', error);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          console.error('Failed to connect to:', url);
          setConnectionStatus('disconnected');
        };

        ws.onclose = (event) => {
          setConnectionStatus('disconnected');
          if (event.code !== 1000) {
            console.warn('WebSocket closed unexpectedly. Code:', event.code, 'Reason:', event.reason);
          }
          reconnectTimeout = window.setTimeout(connect, 3000);
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        setConnectionStatus('disconnected');
        reconnectTimeout = window.setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (reconnectTimeout) {
        window.clearTimeout(reconnectTimeout);
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      wsRef.current = null;
      setConnectionStatus('disconnected');
    };
  }, [url]);

  return { connectionStatus, ws: wsRef.current };
};

export default useWebSocket;


