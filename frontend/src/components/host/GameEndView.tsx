import '../../App.css';
import type { PlayerAnswer } from '../../types';
import TupitruTitle from '../Title';

interface GameEndViewProps {
  ranking: PlayerAnswer[];
  handleStartGame: () => void;
  handleCloseRoom: () => void;
  seed: number | null;
  poolDisplayName: string | null;
}

const GameEndView = ({
  ranking,
  handleStartGame,
  handleCloseRoom,
  seed,
  poolDisplayName,
}: GameEndViewProps) => {
  return (
    <div className="app-container">
      <TupitruTitle />
      <div className="wrapper">
        <h3>Ranking:</h3>
        <ul>
          {ranking.map((player, index) => (
            <li key={index} className="player-item">
              {player.nick}: {player.answer}
            </li>
          ))}
        </ul>
        {seed !== null && poolDisplayName !== null && (
          <p>
            Pool: <strong>{poolDisplayName}</strong> — Seed: <strong>{seed}</strong>
          </p>
        )}
        <button className="button" onClick={handleStartGame}>
          Start another game
        </button>
        <button className="button" onClick={handleCloseRoom}>
          Close Room
        </button>
      </div>
    </div>
  );
};

export default GameEndView;
