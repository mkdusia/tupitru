import '../../App.css';
import TupitruTitle from '../Title';

interface GameEndViewProps {
  score: number;
  position: number;
  handleExit: () => void;
}

function GameEndView({ score, position, handleExit }: GameEndViewProps) {
  return (
    <div className="app-container">
      <TupitruTitle />

      <div className="wrapper">
        <div className="info-row">
          <label className="label">Your score:</label>
          <span className="value">{score}</span>
        </div>

        <div className="info-row">
          <label className="label">Your position:</label>
          <span className="value">{position}</span>
        </div>

        <h3 style={{ marginTop: '20px' }}>Congrats!</h3>

        <button className="button" onClick={handleExit}>
          Exit
        </button>
      </div>
    </div>
  );
}

export default GameEndView;
