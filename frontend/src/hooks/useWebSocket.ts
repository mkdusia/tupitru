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

    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => {
      if (onOpenRef.current) onOpenRef.current();
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error during messege parsing: ', error);
      }
    };

    socket.onclose = (event) => {
      if (onClose) onClose(event);

      if (isMounted.current && !event.wasClean) {
        reconnectTimeout.current = window.setTimeout(() => {
          connect();
        }, 2000);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      socket.close();
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
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(payload));
    }
  }, []);

  return sendMessage;
};
