import { useEffect, useRef, useCallback } from 'react';

interface UseWebSocketProps {
  url: string;
  onOpen?: () => void;
  onMessage: (data: any) => void;
  onClose?: (event: CloseEvent) => void;
}

export const useWebSocket = ({ url, onOpen, onMessage, onClose }: UseWebSocketProps) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<number | null>(null);
  const isMounted = useRef(true);

  const onOpenRef = useRef(onOpen);
  const onMessageRef = useRef(onMessage);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onOpenRef.current = onOpen;
    onMessageRef.current = onMessage;
    onCloseRef.current = onClose;
  });

  const connect = useCallback(() => {
    if (
      ws.current?.readyState === WebSocket.OPEN ||
      ws.current?.readyState === WebSocket.CONNECTING
    ) {
      return;
    }

    let wsUrl = url;
    const userId = sessionStorage.getItem('user_id');
    if (userId) {
      wsUrl += `?user_id=${userId}`;
    }
    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onopen = () => {
      if (onOpenRef.current) onOpenRef.current();
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessageRef.current(data);
      } catch (error) {
        console.error('Error during message parsing: ', error);
      }
    };

    socket.onclose = (event) => {
      if (onCloseRef.current) onCloseRef.current(event);

      if (event.code === 1008) {
        console.warn('WebSocket closed (1008): Unauthenticated. Removing user_id.');
        sessionStorage.removeItem('user_id');
        return;
      }

      if (isMounted.current && !event.wasClean) {
        reconnectTimeout.current = window.setTimeout(() => {
          connect();
        }, 200);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [url]);

  useEffect(() => {
    isMounted.current = true;
    connect();

    return () => {
      isMounted.current = false;
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
    };
  }, [connect]);

  const sendMessage = useCallback((payload: any) => {
    console.log('Sending message: ', payload);
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(payload));
    }
  }, []);

  return sendMessage;
};
