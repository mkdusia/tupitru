import '../App.css';
import { useState, useEffect, useRef } from 'react';
import type { PlayerAnswer } from '../types';

import HostRoomView from '../components/host/HostRoomView';
import GameView from '../components/host/GameView';
import ShowingSolutionView from '../components/host/ShowingSolutionView';
import RoundWinnerView from '../components/host/RoundWinnerView';
import GameEndView from '../components/host/GameEndView';
import { useNavigate, useParams } from 'react-router-dom';

export default function HostRoute() {
  const navigate = useNavigate();
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const frontURL = window.location.origin;

  const { roomId: roomCode } = useParams();

  const ws = useRef<WebSocket | null>(null);

  const [status, setStatus] = useState('waiting_for_players');
  const [currentRoomCode, setCurrentRoomCode] = useState(null);
  const [players, setPlayers] = useState<string[]>([]);
  const [isDeleteMode, setIsDeleteMode] = useState(false);

  const [playersAnswered, setPlayersAnswered] = useState<PlayerAnswer[]>([]);

  const [boardData, setBoardData] = useState(null);

  const [respondent, setRespondent] = useState('');

  const [winner, setWinner] = useState('');

  const [ranking, setRanking] = useState<PlayerAnswer[]>([]);

  useEffect(() => {
    if (ws.current) return;

    const socket = new WebSocket(baseUrl);
    ws.current = socket;

    socket.onopen = () => {
      if (!roomCode) {
        socket?.send(JSON.stringify({ type: 'host' }));
      }
    };

    socket.onmessage = (event: { data: string }) => {
      const data = JSON.parse(event.data);

      console.log(data);

      if (data.type === 'success' && data.message === 'host') {
        setCurrentRoomCode(data.room_id);
        navigate(`/host/${data.room_id}`, { replace: true });
      }

      if (data.type === 'info' && data.message === 'player_joined') {
        setPlayers((prevPlayers) => [...prevPlayers, data.nickname]);
      }

      if (data.type === 'info' && data.message === 'player_disconnected') {
        setPlayers((prevPlayers) => prevPlayers.filter((player) => player !== data.nickname));
      }

      if (data.type === 'info' && data.message === 'game_start') {
        setPlayersAnswered([]);
        setRanking([]);
        setStatus('start_game');
      }

      if (data.board) {
        setBoardData(data.board);
      }

      if (data.type === 'info' && data.message === 'player_answered') {
        setPlayersAnswered((prevPlayers) => {
          const tmpPlayersAnswered = [...prevPlayers];
          // console.log(tmpPlayersAnswered);
          const playerIdx = tmpPlayersAnswered.findIndex((p) => p.nick === data.nickname);
          // console.log('idx:', {playerIdx}, 'nick:', data.nickname, data.answer);

          if (playerIdx !== -1) {
            if (data.answer === -1) {
              tmpPlayersAnswered.splice(playerIdx, 1);
            } else {
              tmpPlayersAnswered[playerIdx] = { nick: data.nickname, answer: data.answer };
            }
          } else if (data.answer !== -1) {
            tmpPlayersAnswered.push({ nick: data.nickname, answer: data.answer });
          }
          // console.log(tmpPlayersAnswered);

          tmpPlayersAnswered.sort((a, b) => a.answer - b.answer);

          return tmpPlayersAnswered;
        });
      }

      if (data.type === 'info' && data.message === 'awaiting_response') {
        setRespondent(data.respondent);
        setStatus('showing');
      }

      if (data.type === 'info' && data.message === 'winner') {
        setWinner(data.nickname);
        setTimeout(() => {
          setStatus('winner');
        }, 1000);
      }

      if (data.type === 'info' && data.message === 'game_end') {
        setRanking(() => {
          return data.ranking.map(([points, nickname]: [number, string]) => ({
            nick: nickname,
            answer: points,
          }));
        });
        console.log(ranking);
        setStatus('game_end');
      }

      if (data.type === 'error') {
        alert('Error: ' + data.message);
        navigate('/');
      }
    };

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'room_destroyed' }));
        navigate('/');
      }

      socket.close();
      if (socket === ws.current) {
        ws.current = null;
      }
    };
  }, []);

  const handleStartGame = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: 'change_state',
        })
      );
    }
  };

  const handleCloseRoom = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'room_destroyed' }));
      navigate('/');
    }
  };

  const handleEndRound = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: 'change_state',
        })
      );
    }
  };

  const handleKickPlayer = (nick: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(
        JSON.stringify({
          type: 'kick',
          player: nick,
        })
      );
    }
  };

  if (status === 'start_game') {
    return (
      <GameView
        totalPlayers={players.length}
        players={playersAnswered}
        boardData={boardData}
        handleCloseRoom={handleCloseRoom}
        handleEndRound={handleEndRound}
      />
    );
  }

  if (status === 'showing') {
    return <ShowingSolutionView nickname={respondent} boardData={boardData} />;
  }

  if (status === 'winner') {
    return <RoundWinnerView nickname={winner} handleStartGame={handleStartGame} />;
  }

  if (status === 'game_end') {
    return (
      <GameEndView
        ranking={ranking}
        handleStartGame={handleStartGame}
        handleCloseRoom={handleCloseRoom}
      />
    );
  }

  const QRUrl = `${frontURL}/?room=${roomCode}`;

  return (
    <HostRoomView
      roomCode={currentRoomCode}
      players={players}
      handleStartGame={handleStartGame}
      handleCloseRoom={handleCloseRoom}
      isDeleteMode={isDeleteMode}
      setIsDeleteMode={setIsDeleteMode}
      handleKickPlayer={handleKickPlayer}
      currentURL={QRUrl}
    />
  );
}
