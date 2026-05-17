import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { PlayerAnswer } from '../types';

export const useHostGame = () => {
  const navigate = useNavigate();

  const [status, setStatus] = useState(
    () => sessionStorage.getItem('hostStatus') || 'waiting_for_players'
  );
  const [currentRoomCode, setCurrentRoomCode] = useState(
    () => sessionStorage.getItem('hostRoomCode') || null
  );
  const [players, setPlayers] = useState<string[]>(() =>
    JSON.parse(sessionStorage.getItem('hostPlayers') || '[]')
  );

  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [playersAnswered, setPlayersAnswered] = useState<PlayerAnswer[]>([]);

  const [boardData, setBoardData] = useState(() =>
    JSON.parse(sessionStorage.getItem('hostBoardData') || 'null')
  );
  const [respondent, setRespondent] = useState(
    () => sessionStorage.getItem('hostRespondent') || ''
  );
  const [winner, setWinner] = useState(() => sessionStorage.getItem('hostWinner') || '');
  const [ranking, setRanking] = useState<PlayerAnswer[]>(() =>
    JSON.parse(sessionStorage.getItem('hostRanking') || '[]')
  );

  useEffect(() => {
    sessionStorage.setItem('hostStatus', status);
  }, [status]);
  useEffect(() => {
    if (currentRoomCode) sessionStorage.setItem('hostRoomCode', currentRoomCode);
  }, [currentRoomCode]);
  useEffect(() => {
    sessionStorage.setItem('hostPlayers', JSON.stringify(players));
  }, [players]);
  useEffect(() => {
    sessionStorage.setItem('hostBoardData', JSON.stringify(boardData));
  }, [boardData]);
  useEffect(() => {
    sessionStorage.setItem('hostRespondent', respondent);
  }, [respondent]);
  useEffect(() => {
    sessionStorage.setItem('hostWinner', winner);
  }, [winner]);
  useEffect(() => {
    sessionStorage.setItem('hostRanking', JSON.stringify(ranking));
  }, [ranking]);

  const handleMessage = useCallback(
    (data: any) => {
      console.log(data);

      if (data.board) setBoardData(data.board);

      if (data.type === 'error') {
        alert('Error: ' + data.message);
        if (data.message !== 'Invalid event format') {
          sessionStorage.clear();
          navigate('/');
        }
        return;
      }

      const actionHandlers: Record<string, () => void> = {
        'success:reconnect': () => {
          const { game_state, room_id, board, respondent, ranking } = data;

          if (room_id) setCurrentRoomCode(room_id);

          if (game_state === 'no_game') {
            sessionStorage.clear();
            navigate('/');
          } else if (game_state === 'awaiting_start') {
            setStatus('waiting_for_players');
          } else if (game_state === 'awaiting_answers') {
            setStatus('start_game');
            if (board) setBoardData(board);
          } else if (game_state === 'settling_round') {
            setRespondent(respondent || '');
            if (board) setBoardData(board);
            setStatus('showing');
          } else if (game_state === 'game_ended') {
            if (ranking) {
              setRanking(
                ranking.map(([points, nickname]: [number, string]) => ({
                  nick: nickname,
                  answer: points,
                }))
              );
            }
            setStatus('game_end');
          }
        },
        'success:host': () => {
          setCurrentRoomCode(data.room_id);
          navigate(`/host/${data.room_id}`, { replace: true });
        },
        'info:player_joined': () => {
          setPlayers((prevPlayers) =>
            prevPlayers.includes(data.nickname) ? prevPlayers : [...prevPlayers, data.nickname]
          );
        },
        'info:player_disconnected': () => {
          setPlayers((prevPlayers) => prevPlayers.filter((player) => player !== data.nickname));
        },
        'info:game_start': () => {
          setPlayersAnswered([]);
          setRanking([]);
          setStatus('start_game');
        },
        'info:player_answered': () => {
          setPlayersAnswered((prevPlayers) => {
            const tmpPlayersAnswered = [...prevPlayers];
            const playerIdx = tmpPlayersAnswered.findIndex(
              (player) => player.nick === data.nickname
            );
            if (playerIdx !== -1) {
              if (data.answer === -1) {
                tmpPlayersAnswered.splice(playerIdx, 1);
              } else {
                tmpPlayersAnswered[playerIdx] = { nick: data.nickname, answer: data.answer };
              }
            } else if (data.answer !== -1) {
              tmpPlayersAnswered.push({ nick: data.nickname, answer: data.answer });
            }
            tmpPlayersAnswered.sort((a, b) => a.answer - b.answer);

            return tmpPlayersAnswered;
          });
        },
        'info:awaiting_response': () => {
          setRespondent(data.respondent);
          setStatus('showing');
        },
        'info:winner': () => {
          setWinner(data.nickname);
          setTimeout(() => setStatus('winner'), 1000);
        },
        'info:game_end': () => {
          setRanking(() => {
            return data.ranking.map(([points, nickname]: [number, string]) => ({
              nick: nickname,
              answer: points,
            }));
          });
          console.log(ranking);
          setStatus('game_end');
        },
        kick: () => {
          setPlayers((prevPlayers) => prevPlayers.filter((player) => player !== data.nickname));
        },
      };

      const key = data.message ? `${data.type}:${data.message}` : data.type;
      const handler = actionHandlers[key];

      if (handler) handler();
    },
    [navigate, ranking]
  );

  return {
    state: {
      status,
      currentRoomCode,
      players,
      boardData,
      respondent,
      winner,
      isDeleteMode,
      playersAnswered,
      ranking,
    },
    setters: { setIsDeleteMode, setStatus, setPlayers },
    handleMessage,
  };
};
