import '../App.css';
import { useState, useEffect, useRef } from 'react';

import WaitingView from '../components/player/WaitingView';
import AnswerView from '../components/player/AnswerView';
import RespondView from '../components/player/RespondView';
import AwaitingResponseView from '../components/player/AwaitingResponseView';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

export default function PlayerRoute() {
  const navigate = useNavigate();
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const { roomId: roomCode } = useParams();
  const [searchParams] = useSearchParams();
  const nick = searchParams.get('nick') || '';

  const ws = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState('connecting');
  const [countdown, setCountdown] = useState(5);
  const [answer, setAnswer] = useState(0);
  const [current_answer, setCurrentAnswer] = useState(0);
  const [respondent, setRespondent] = useState('');

  useEffect(() => {
    if (!nick || !roomCode) {
      navigate('/');
      return;
    }

    const socket = new WebSocket(baseUrl);
    ws.current = socket;

    const connectingTimeout = setTimeout(() => {
      alert('Room not found or session has expired.');
      navigate('/');
    }, 5000);

    const countdownInterval = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    socket.onopen = () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(
          JSON.stringify({
            type: 'join',
            room_id: roomCode,
            nickname: nick,
          })
        );
      }
    };

    socket.onmessage = (event: { data: string }) => {
      const data = JSON.parse(event.data);

      console.log(data.type + ' ' + data.message);

      if (data.type === 'success' || data.type === 'error') {
        clearTimeout(connectingTimeout);
        clearInterval(countdownInterval);
      }

      if (data.type === 'success' && data.message === 'join') {
        setStatus('waiting');
      }

      if (data.type === 'success' && data.message == 'answer') {
        setCurrentAnswer(data.answer);
      }

      if (data.type === 'info' && data.message === 'room_destroyed') {
        navigate('/', { state: { previousNick: nick } });
        alert('Room was destroyed.');
      }

      if (data.type === 'info' && data.message === 'game_start') {
        setStatus('playing');
      }

      if (data.type === 'info' && data.message === 'awaiting_response') {
        setRespondent(data.respondent);
        setStatus('awaiting_response');
      }

      if (data.type === 'info' && data.message === 'respond') {
        setStatus('showing_solution');
      }

      if (data.type === 'error') {
        alert('Error: ' + data.message);
        navigate('/');
      }
    };

    socket.onclose = (event) => {
      if (!event.wasClean) {
        clearTimeout(connectingTimeout);
        navigate('/');
      }
    };

    return () => {
      clearTimeout(connectingTimeout);
      clearInterval(countdownInterval);
      socket.close();
      if (socket === ws.current) {
        ws.current = null;
      }
    };
  }, [roomCode, nick, navigate]);

  const handleWaitingViewExit = () => {
    navigate('/', { state: { previousRoomCode: roomCode, previousNick: nick } });
  };

  const handleSendAnswer = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: 'answer',
          answer: answer,
        })
      );
    }
  };

  if (status === 'connecting')
    return (
      <div className="wrapper">
        <h1>Connecting...</h1>
        <p>
          Remaining seconds to connect: <strong>{countdown}s</strong>
        </p>
      </div>
    );

  if (status === 'playing') {
    return (
      <AnswerView
        current_answer={current_answer}
        setAnswer={setAnswer}
        handleSendAnswer={handleSendAnswer}
      />
    );
  }

  if (status === 'waiting') {
    return <WaitingView nick={nick} roomCode={roomCode} handleExit={handleWaitingViewExit} />;
  }

  if (status === 'awaiting_response') {
    return <AwaitingResponseView respondent={respondent} />;
  }

  if (status === 'showing_solution') {
    return <RespondView answer={current_answer} />;
  }
}
