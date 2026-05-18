import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export const usePlayerGame = (nick: string) => {
  const navigate = useNavigate();

  const [status, setStatus] = useState(
    () => sessionStorage.getItem('playerStatus') || 'connecting'
  );
  const [countdown, setCountdown] = useState(5);
  const [answer, setAnswer] = useState(() => sessionStorage.getItem('playerAnswer') || '');
  const [currentAnswer, setCurrentAnswer] = useState(() =>
    parseInt(sessionStorage.getItem('playerCurrentAnswer') || '0', 10)
  );
  const [respondent, setRespondent] = useState(
    () => sessionStorage.getItem('playerRespondent') || ''
  );

  const [movesLeft, setMovesLeft] = useState(() =>
    parseInt(sessionStorage.getItem('playerMovesLeft') || '0', 10)
  );

  const [winner, setWinner] = useState('');

  const [mole, setMole] = useState(-1);
  const [direction, setDirection] = useState('');

  const [sessionId] = useState(() => {
    let sid = sessionStorage.getItem('playerSessionId');
    if (!sid) {
      sid =
        Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      sessionStorage.setItem('playerSessionId', sid);
    }
    return sid;
  });

  useEffect(() => {
    sessionStorage.setItem('playerStatus', status);
  }, [status]);
  useEffect(() => {
    sessionStorage.setItem('playerAnswer', answer);
  }, [answer]);
  useEffect(() => {
    sessionStorage.setItem('playerCurrentAnswer', currentAnswer.toString());
  }, [currentAnswer]);
  useEffect(() => {
    sessionStorage.setItem('playerRespondent', respondent);
  }, [respondent]);
  useEffect(() => {
    sessionStorage.setItem('playerMovesLeft', movesLeft.toString());
  }, [movesLeft]);

  useEffect(() => {
    if (status !== 'connecting') return;
    const interval = setInterval(() => setCountdown((prev) => (prev > 0 ? prev - 1 : 0)), 1000);
    return () => clearInterval(interval);
  }, [status]);

  const handleMessage = useCallback(
    (data: any) => {
      console.log(data);

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
          const { game_state, answer, respondent, respond } = data;

          if (game_state === 'no_game') {
            sessionStorage.clear();
            navigate('/');
          } else if (game_state === 'awaiting_start') {
            setStatus('waiting');
          } else if (game_state === 'awaiting_answers') {
            setStatus('playing');
            if (answer !== undefined) {
              setAnswer(answer.toString());
              setCurrentAnswer(answer);
            }
          } else if (game_state === 'settling_round') {
            setRespondent(respondent || '');
            if (answer !== undefined) setCurrentAnswer(answer);
            setStatus(respond ? 'awaiting_response' : 'showing_solution');
          }
        },
        'success:join': () => {
          setStatus((prev) => (prev === 'connecting' ? 'waiting' : prev));
        },
        'success:answer': () => {
          setAnswer('');
          setCurrentAnswer(data.answer);
        },
        'info:room_destroyed': () => {
          sessionStorage.clear();
          navigate('/', { state: { previousNick: nick } });
          alert('Room was destroyed.');
        },
        'info:game_start': () => {
          setAnswer('');
          setCurrentAnswer(0);
          setStatus('playing');
        },
        'info:awaiting_response': () => {
          setRespondent(data.respondent);
          setStatus('awaiting_response');
        },
        'info:respond': () => {
          console.log(currentAnswer);
          setMovesLeft(currentAnswer);
          setStatus('showing_solution');
        },
        'info:won': () => {
          setStatus('won');
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
        'info:kick': () => {
          sessionStorage.clear();
          navigate('/', { state: { previousNick: nick } });
          alert('You have been kicked out by host.');
        },
      };

      const key = `${data.type}:${data.message}`;
      const handler = actionHandlers[key];

      if (handler) handler();
    },
    [navigate, nick, currentAnswer]
  );

  return {
    state: {
      status,
      countdown,
      answer,
      currentAnswer,
      respondent,
      winner,
      mole,
      direction,
      sessionId,
      movesLeft,
    },
    setters: { setAnswer, setMole, setDirection, setStatus, setMovesLeft },
    handleMessage,
  };
};
