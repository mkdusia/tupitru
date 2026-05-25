import '../App.css';
import { useNavigate, useParams } from 'react-router-dom';

import { useWebSocket } from '../hooks/useWebSocket';
import { useHostGame } from '../hooks/useHostGame';

import HostRoomView from '../components/host/HostRoomView';
import GameView from '../components/host/GameView';
import ShowingSolutionView from '../components/host/ShowingSolutionView';
import RoundWinnerView from '../components/host/RoundWinnerView';
import GameEndView from '../components/host/GameEndView';

export default function HostRoute() {
  const navigate = useNavigate();
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const frontURL = window.location.origin;

  const { roomId: roomCode } = useParams();

  const { state, setters, handleMessage } = useHostGame();

  const sendMessage = useWebSocket({
    url: baseUrl,
    onMessage: (data) => {
      if (data.type === 'success' && data.message === 'connect') {
        sessionStorage.setItem('user_id', data.user_id);
        if (!roomCode) {
          sendMessage({ type: 'host' });
        }
      } else {
        handleMessage(data);
      }
    },
  });

  const handleStartGame = () => {
    const rt = parseInt(state.roundTime, 10);
    const hasTimer = Number.isFinite(rt) && rt > 0;
    sendMessage({ type: 'change_state', ...(hasTimer && { round_time: rt }) });
    if (hasTimer) setters.setCountdownEnd(Date.now() + rt * 1000);
  };

  const handleCloseRoom = () => {
    sessionStorage.clear();
    sendMessage({ type: 'close' });
    navigate('/');
  };

  const handleEndRound = () => {
    sendMessage({ type: 'change_state' });
  };

  const handleKickPlayer = (nick: string) => {
    sendMessage({ type: 'kick', nickname: nick });
    setters.setPlayers((prev) => prev.filter((p) => p !== nick));
  };

  if (state.status === 'start_game') {
    return (
      <GameView
        totalPlayers={state.players.length}
        players={state.playersAnswered}
        boardData={state.boardData}
        countdownEnd={state.countdownEnd}
        handleCloseRoom={handleCloseRoom}
        handleEndRound={handleEndRound}
      />
    );
  }

  if (state.status === 'showing') {
    return <ShowingSolutionView nickname={state.respondent} boardData={state.boardData} />;
  }

  if (state.status === 'winner') {
    return <RoundWinnerView nickname={state.winner} handleStartGame={handleStartGame} />;
  }

  if (state.status === 'game_end') {
    return (
      <GameEndView
        ranking={state.ranking}
        handleStartGame={handleStartGame}
        handleCloseRoom={handleCloseRoom}
      />
    );
  }

  const QRUrl = `${frontURL}/?room=${roomCode}`;

  return (
    <HostRoomView
      roomCode={state.currentRoomCode}
      players={state.players}
      handleStartGame={handleStartGame}
      handleCloseRoom={handleCloseRoom}
      isDeleteMode={state.isDeleteMode}
      setIsDeleteMode={setters.setIsDeleteMode}
      handleKickPlayer={handleKickPlayer}
      currentURL={QRUrl}
    />
  );
}
