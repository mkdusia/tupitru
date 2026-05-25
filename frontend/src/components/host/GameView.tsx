import '../../App.css';
import { useState, useEffect } from 'react';
import GameWrapper from './GameWrapper';
import type { PlayerAnswer, BoardData } from '../../types';
import { useBackgroundMusic } from '../../hooks/useBackgroundMusic';

interface GameViewProps {
  totalPlayers: number;
  players: PlayerAnswer[];
  boardData: BoardData | null;
  countdownEnd: number | null;
  handleCloseRoom: () => void;
  handleEndRound: () => void;
}

const GameView = ({
  totalPlayers,
  players,
  countdownEnd,
  handleCloseRoom,
  handleEndRound,
}: GameViewProps) => {
  const { isPlaying, toggleMute } = useBackgroundMusic('/audio/GameTime.mp3');
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (countdownEnd === null) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [countdownEnd]);

  const remaining =
    countdownEnd !== null ? Math.max(0, Math.ceil((countdownEnd - now) / 1000)) : null;

  return (
    <div className="game-container">
      {/* <h1 className='title'>Game View</h1> */}
      <div
        className="left-section"
        style={{ paddingTop: 0, paddingBottom: 0, paddingLeft: 40, paddingRight: 10 }}
      >
        <GameWrapper boardData={boardData}></GameWrapper>
      </div>
      <div className="right-section">
        <div className="side-controls wrapper">
          <button className="button-circle" onClick={toggleMute}>
            <img
              src={isPlaying ? '/icons/mute.svg' : '/icons/unmute.svg'}
              alt={isPlaying ? 'Mute' : 'Music'}
              className="button-icon"
            />
          </button>
          <button className="button-circle"></button>
        </div>
        <div className="wrapper answer-list">
          {remaining !== null && <h2 className="counter">{remaining}s</h2>}
          <h3>Answers:</h3>
          {players.length === 0 ? (
            <p>Waiting for answers...</p>
          ) : (
            <ul>
              {players.map((player, index) => (
                <li key={index} className="answer-item">
                  {player.nick}: {player.answer}
                </li>
              ))}
            </ul>
          )}
        </div>

        <h2 className="counter">
          {players.length} / {totalPlayers}
          {/*some type of placeholder */}
        </h2>
        <button className="button" onClick={handleEndRound}>
          End Round
        </button>
        <button className="button" onClick={handleCloseRoom}>
          Close Room
        </button>
      </div>
    </div>
  );
};

export default GameView;
