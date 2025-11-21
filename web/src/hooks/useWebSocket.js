import { useEffect, useRef } from 'react';

export const useWebSocket = (url, onEvent) => {
  const handlerRef = useRef(onEvent);

  useEffect(() => {
    handlerRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!url) {
      return () => undefined;
    }

    let ws;
    let reconnectTimeout;

    const connect = () => {
      try {
        ws = new WebSocket(url);

        ws.onopen = () => {
          console.log('WebSocket connected:', url);
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
        };

        ws.onclose = (event) => {
          if (event.code !== 1000) {
            console.warn('WebSocket closed unexpectedly. Code:', event.code, 'Reason:', event.reason);
          }
          reconnectTimeout = window.setTimeout(connect, 3000);
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
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
    };
  }, [url]);
};

export default useWebSocket;


