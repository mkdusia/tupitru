import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { PlayerAnswer, PoolOption } from '../types';

const ROUND_TIME = 60;

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
  const [playersAnswered, setPlayersAnswered] = useState<PlayerAnswer[]>(() =>
    JSON.parse(sessionStorage.getItem('hostPlayersAnswered') || '[]')
  );

  const [boardData, setBoardData] = useState(() =>
    JSON.parse(sessionStorage.getItem('hostBoardData') || 'null')
  );
  const [respondent, setRespondent] = useState(
    () => sessionStorage.getItem('hostRespondent') || ''
  );
  const [respondentAnswer, setRespondentAnswer] = useState<number | null>(() => {
    const saved = sessionStorage.getItem('hostRespondentAnswer');
    return saved ? parseInt(saved, 10) : null;
  });

  const [winner, setWinner] = useState(() => sessionStorage.getItem('hostWinner') || '');
  const [ranking, setRanking] = useState<PlayerAnswer[]>(() =>
    JSON.parse(sessionStorage.getItem('hostRanking') || '[]')
  );
  const [countdownEnd, setCountdownEnd] = useState<number | null>(() => {
    const saved = sessionStorage.getItem('hostCountdownEnd');
    return saved ? parseInt(saved, 10) : null;
  });

  const roundTime = String(ROUND_TIME);

  const [endSeed, setEndSeed] = useState<number | null>(() => {
    const v = sessionStorage.getItem('hostEndSeed');
    return v ? Number(v) : null;
  });
  const [endPoolId, setEndPoolId] = useState<string | null>(
    () => sessionStorage.getItem('hostEndPoolId') || null
  );
  const [pools, setPools] = useState<PoolOption[] | null>(() =>
    JSON.parse(sessionStorage.getItem('hostPools') || 'null')
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
    sessionStorage.setItem('hostPlayersAnswered', JSON.stringify(playersAnswered));
  }, [playersAnswered]);
  useEffect(() => {
    sessionStorage.setItem('hostBoardData', JSON.stringify(boardData));
  }, [boardData]);
  useEffect(() => {
    sessionStorage.setItem('hostRespondent', respondent);
  }, [respondent]);
  useEffect(() => {
    sessionStorage.setItem('hostRespondentAnswer', String(respondentAnswer));
  }, [respondentAnswer]);
  useEffect(() => {
    sessionStorage.setItem('hostWinner', winner);
  }, [winner]);
  useEffect(() => {
    sessionStorage.setItem('hostRanking', JSON.stringify(ranking));
  }, [ranking]);
  useEffect(() => {
    if (countdownEnd !== null) {
      sessionStorage.setItem('hostCountdownEnd', String(countdownEnd));
    } else {
      sessionStorage.removeItem('hostCountdownEnd');
    }
  }, [countdownEnd]);
  useEffect(() => {
    if (endSeed !== null) sessionStorage.setItem('hostEndSeed', String(endSeed));
  }, [endSeed]);
  useEffect(() => {
    if (endPoolId !== null) sessionStorage.setItem('hostEndPoolId', endPoolId);
  }, [endPoolId]);
  useEffect(() => {
    if (pools !== null) sessionStorage.setItem('hostPools', JSON.stringify(pools));
  }, [pools]);

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
          const { game_state, room_id, nicknames, board, answers, respondent, answer, ranking } =
            data;

          if (room_id) setCurrentRoomCode(room_id);

          if (game_state === 'no_game') {
            sessionStorage.clear();
            navigate('/');
          } else if (game_state === 'awaiting_start') {
            setPlayers(nicknames || []);
            setStatus('waiting_for_players');
          } else if (game_state === 'awaiting_answers') {
            if (answers) {
              setRanking(
                answers.map(([answer, nickname]: [number, string]) => ({
                  nick: nickname,
                  answer: answer,
                }))
              );
            }
            setStatus('start_game');
            if (board) setBoardData(board);
          } else if (game_state === 'settling_round') {
            setRespondent(respondent || '');
            setRespondentAnswer(answer);
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
          if (data.pools) setPools(data.pools);
          navigate(`/host/${data.room_id}`, { replace: true });
        },
        'info:return_to_lobby': () => {
          setPlayersAnswered([]);
          setRanking([]);
          setBoardData(null);
          setCountdownEnd(null);
          setStatus('waiting_for_players');
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
          setCountdownEnd(Date.now() + ROUND_TIME * 1000);
          setStatus('start_game');
        },
        'info:player_answered': () => {
          setPlayersAnswered((prevPlayers) => {
            const tmpPlayersAnswered = [...prevPlayers];

            const playerIdx = tmpPlayersAnswered.findIndex(
              (player) => player.nick === data.nickname
            );
            if (playerIdx !== -1) {
              tmpPlayersAnswered.splice(playerIdx, 1);
            }

            if (data.answer > 0) {
              const answerIdx = tmpPlayersAnswered.findIndex(
                (player) => player.answer > data.answer
              );
              if (answerIdx === -1) {
                tmpPlayersAnswered.push({ nick: data.nickname, answer: data.answer });
              } else {
                tmpPlayersAnswered.splice(answerIdx, 0, {
                  nick: data.nickname,
                  answer: data.answer,
                });
              }
            }

            return tmpPlayersAnswered;
          });
        },
        'info:awaiting_response': () => {
          setRespondent(data.respondent);
          setRespondentAnswer(data.answer);
          setCountdownEnd(Date.now() + ROUND_TIME * 1000);
          setStatus('showing');
        },
        'info:winner': () => {
          if (data.nickname) {
            setWinner(data.nickname);
            setTimeout(() => setStatus('winner'), 1000);
          } else {
            setWinner('Nobody');
            setStatus('winner');
          }
        },
        'info:game_end': () => {
          if (typeof data.seed === 'number') setEndSeed(data.seed);
          if (typeof data.pool_id === 'string') setEndPoolId(data.pool_id);
          setRanking(() => {
            return data.ranking.map(([points, nickname]: [number, string]) => ({
              nick: nickname,
              answer: points,
            }));
          });
          console.log(ranking);
          setCountdownEnd(null);
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
      respondentAnswer,
      winner,
      isDeleteMode,
      playersAnswered,
      ranking,
      roundTime,
      countdownEnd,
      endSeed,
      endPoolId,
      pools,
    },
    setters: { setIsDeleteMode, setStatus, setPlayers, setCountdownEnd },
    handleMessage,
  };
};
