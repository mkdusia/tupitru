import '../../App.css'
import GameWrapper from './GameWrapper';

interface GameViewProps {
    totalPlayers: number;
    players : string[]
}


const GameView = ({totalPlayers, players } : GameViewProps) => {
return (
    <div className="app-container">
      <h1 className='title'>Game View</h1>

      <div className='wrapper'>
        <h2 className="counter">
          {players.length} / {totalPlayers} 
          {/*some type of placeholder */}
        </h2>
      <GameWrapper></GameWrapper>
      </div>
    </div>
  );
}

export default GameView;