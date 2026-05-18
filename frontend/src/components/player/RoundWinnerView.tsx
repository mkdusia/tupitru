import '../../App.css';
import TupitruTitle from '../Title';

interface RoundWinnerViewProps {
  nickname: string;
}

function RoundWinnerView({ nickname }: RoundWinnerViewProps) {
  return (
    <div className="app-container">
      <TupitruTitle />

      <div className="wrapper">
        <h1> {nickname} won this round! </h1>
      </div>
    </div>
  );
}

export default RoundWinnerView;
