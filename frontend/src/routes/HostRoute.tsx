import '../App.css';
import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { useWebSocket } from '../hooks/useWebSocket';
import { useHostGame } from '../hooks/useHostGame';

import HostRoomView from '../components/host/HostRoomView';
import GameView from '../components/host/GameView';
import ShowingSolutionView from '../components/host/ShowingSolutionView';
import RoundWinnerView from '../components/host/RoundWinnerView';
import GameEndView from '../components/host/GameEndView';

const DEFAULT_ROUNDS = 5;

export default function HostRoute() {
  const navigate = useNavigate();
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const frontURL = window.location.origin;

  const { roomId: roomCode } = useParams();

  const { state, setters, handleMessage } = useHostGame();
  const pools = state.pools;

  const [selectedPoolId, setSelectedPoolId] = useState<string>('');
  const [seedInput, setSeedInput] = useState<string>('');
  const [roundsInput, setRoundsInput] = useState<string>(`${DEFAULT_ROUNDS}`);

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
    const poolId = selectedPoolId || pools?.[0]?.id;
    if (!poolId) {
      alert('No board pools are available.');
      return;
    }
    const trimmedSeed = seedInput.trim();
    let seed: number;
    if (trimmedSeed === '') {
      seed = Math.floor(Math.random() * 2 ** 32);
    } else {
      seed = Number(trimmedSeed);
      if (!Number.isInteger(seed) || seed < 0 || seed >= 2 ** 32) {
        alert('Seed must be a non-negative integer below 2^32.');
        return;
      }
    }
    const trimmedRounds = roundsInput.trim();
    const rounds = trimmedRounds === '' ? DEFAULT_ROUNDS : Number(trimmedRounds);
    if (!Number.isInteger(rounds) || rounds < 1 || rounds > 50) {
      alert('Rounds must be an integer between 1 and 50.');
      return;
    }
    const rt = parseInt(state.roundTime, 10);
    const hasTimer = Number.isFinite(rt) && rt > 0;
    sendMessage({
      type: 'start_game',
      pool_id: poolId,
      seed,
      rounds,
      ...(hasTimer && { round_time: rt }),
    });
  };

  const handleCloseRoom = () => {
    sessionStorage.clear();
    sendMessage({ type: 'close' });
    navigate('/');
  };

  // Advance the room to its next stage (settle round, next responder, back to lobby).
  const handleChangeState = () => {
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
        handleEndRound={handleChangeState}
      />
    );
  }

  if (state.status === 'showing') {
    return <ShowingSolutionView nickname={state.respondent} boardData={state.boardData} />;
  }

  if (state.status === 'winner') {
    return <RoundWinnerView nickname={state.winner} handleStartGame={handleChangeState} />;
  }

  if (state.status === 'game_end') {
    return (
      <GameEndView
        ranking={state.ranking}
        handleStartGame={handleChangeState}
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
      pools={pools}
      selectedPoolId={selectedPoolId}
      setSelectedPoolId={setSelectedPoolId}
      seedInput={seedInput}
      setSeedInput={setSeedInput}
      roundsInput={roundsInput}
      setRoundsInput={setRoundsInput}
    />
  );
}
