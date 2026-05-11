import '../../App.css';
import TupitruTitle from '../Title';

interface RoundWinnerViewProps {
  nickname: string;
  handleStartGame: () => void;
}

function RoundWinnerView({ nickname, handleStartGame }: RoundWinnerViewProps) {
  return (
    <div className="app-container">
      <TupitruTitle />

      <div className="wrapper">
        <h1> Player {nickname} has won the round! </h1>
      </div>

      <button className="button button-white button-ret" onClick={handleStartGame}>
        Next round
      </button>
    </div>
  );
}

export default RoundWinnerView;
