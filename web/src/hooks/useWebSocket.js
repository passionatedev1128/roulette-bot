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
      ws = new WebSocket(url);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handlerRef.current?.(data);
        } catch (error) {
          console.warn('WebSocket message parse error', error);
        }
      };

      ws.onclose = () => {
        reconnectTimeout = window.setTimeout(connect, 3000);
      };
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


