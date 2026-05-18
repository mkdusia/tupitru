import '../App.css';
import { useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { useWebSocket } from '../hooks/useWebSocket';
import { usePlayerGame } from '../hooks/usePlayerGame';

import WaitingView from '../components/player/WaitingView';
import AnswerView from '../components/player/AnswerView';
import RespondView from '../components/player/RespondView';
import AwaitingResponseView from '../components/player/AwaitingResponseView';
import RoundWinnerView from '../components/player/RoundWinnerView';
import WonRoundView from '../components/player/WonRoundView';

export default function PlayerRoute() {
  const navigate = useNavigate();
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const { roomId: roomCode } = useParams();
  const [searchParams] = useSearchParams();
  const nick = searchParams.get('nick') || '';

  const { state, setters, handleMessage } = usePlayerGame(nick);

  const sendMessage = useWebSocket({
    url: baseUrl,
    onMessage: (data) => {
      if (data.type === 'success' && data.message === 'connect') {
        sessionStorage.setItem('user_id', data.user_id);
        sendMessage({ type: 'join', room_id: roomCode, nickname: nick });
      } else {
        handleMessage(data);
      }
    },
  });

  useEffect(() => {
    if (!nick || !roomCode) navigate('/');
  }, [nick, roomCode, navigate]);

  const handleWaitingViewExit = () => {
    navigate('/', { state: { previousRoomCode: roomCode, previousNick: nick } });
  };

  const handleSendAnswer = () => {
    sendMessage({ type: 'answer', answer: parseInt(state.answer) });
  };

  const handleResetAnswer = () => {
    setters.setAnswer('');
    sendMessage({ type: 'answer', answer: -1 });
  };

  const handleSendStep = () => {
    sendMessage({ type: 'respond', mole: state.mole, direction: state.direction });
  };

  const handleGiveUp = () => {
    sendMessage({ type: 'give_up' });
  };

  const handleRevert = () => {
    sendMessage({ type: 'revert' });
  };

  if (state.status === 'connecting') {
    return (
      <div className="wrapper">
        <h1>Connecting...</h1>
        <p>
          Remaining seconds to connect: <strong>{state.countdown}s</strong>
        </p>
      </div>
    );
  }

  if (state.status === 'playing') {
    return (
      <AnswerView
        answer={state.answer}
        current_answer={state.currentAnswer}
        setAnswer={setters.setAnswer}
        handleSendAnswer={handleSendAnswer}
        handleResetAnswer={handleResetAnswer}
      />
    );
  }

  if (state.status === 'waiting') {
    return <WaitingView nick={nick} roomCode={roomCode} handleExit={handleWaitingViewExit} />;
  }

  if (state.status === 'awaiting_response') {
    return <AwaitingResponseView respondent={state.respondent} />;
  }

  if (state.status === 'showing_solution') {
    return (
      <RespondView
        answer={state.currentAnswer}
        movesLeft={state.movesLeft}
        setMovesLeft={setters.setMovesLeft}
        setMole={setters.setMole}
        setDirection={setters.setDirection}
        handleSendStep={handleSendStep}
        handleGiveUp={handleGiveUp}
        handleRevert={handleRevert}
      />
    );
  }

  if (state.status === 'winner') {
    return <RoundWinnerView nickname={state.winner} />;
  }

  if (state.status === 'won') {
    return <WonRoundView />;
  }
}
