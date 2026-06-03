import '../../App.css';
import '../../Room.css';
import type { PlayerAnswer } from '../../types';
import TupitruTitle from '../Title';

import Confetti from 'react-confetti';

import goldCrown from '../../assets/crown-gold.svg';
import silverCrown from '../../assets/crown-silver.svg';
import bronzeCrown from '../../assets/crown-bronze.svg';

interface GameEndViewProps {
  ranking: PlayerAnswer[];
  handleStartGame: () => void;
  handleCloseRoom: () => void;
}

const GameEndView = ({ ranking, handleStartGame, handleCloseRoom }: GameEndViewProps) => {
  const top3 = ranking.slice(0, 3);
  const others = ranking.slice(3);

  return (
    <div className="game-end-container">
      <Confetti
        width={window.innerWidth}
        height={window.innerHeight}
        recycle={false}
        numberOfPieces={670}
      />
      <TupitruTitle />

      <div className="game-end-content">
        <div className="podium-section">
          {top3[1] && (
            <div className="podium-place place-2">
              <div className="podium-winner">
                <div className="crown crown-silver">
                  <img src={silverCrown} alt="Silver Crown" className="crown-icon" />
                </div>
                <div className="player-item podium-avatar">{top3[1].nick}</div>
              </div>
              <div className="podium-block block-2"></div>
            </div>
          )}

          {top3[0] && (
            <div className="podium-place place-1">
              <div className="podium-winner">
                <div className="crown crown-gold">
                  <img src={goldCrown} alt="Gold Crown" className="crown-icon" />
                </div>
                <div className="player-item">{top3[0].nick}</div>
              </div>
              <div className="podium-block block-1"></div>
            </div>
          )}

          {top3[2] && (
            <div className="podium-place place-3">
              <div className="podium-winner">
                <div className="crown crown-bronze">
                  <img src={bronzeCrown} alt="Bronze Crown" className="crown-icon" />
                </div>
                <div className="player-item podium-avatar">{top3[2].nick}</div>
              </div>
              <div className="podium-block block-3"></div>
            </div>
          )}
        </div>

        <div className="action-buttons">
          <button className="button button-white button-ret" onClick={handleStartGame}>
            Start New Game
          </button>
          <button className="button button-orange button-ret" onClick={handleCloseRoom}>
            Close Room
          </button>
        </div>
      </div>

      <div className="others-list">
        {others.map((player, index) => (
          <div key={index + 3} className="player-item">
            {player.nick}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GameEndView;
