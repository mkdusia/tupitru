import '../../App.css'
import GameWrapper from './GameWrapper';
import type { PlayerAnswer } from '../../types';

interface GameViewProps {
    totalPlayers: number;
    players : PlayerAnswer[]
    handleCloseRoom : () => void;
    handleEndRound : () => void;
}

const GameView = ({totalPlayers, players, handleCloseRoom, handleEndRound } : GameViewProps) => {
return (
    <div className="app-container">
      {/* <h1 className='title'>Game View</h1> */}

      <div className='wrapper'>
        <h3>Already answered:</h3>
          {players.length === 0 ? (
          <p>Waiting for answers...</p>
          ) : (
          <ul>
              {players.map((player, index) => (
              <li key={index} className="player-item">{player.nick}: {player.answer}</li>
              ))}
          </ul>
          )}
      <GameWrapper></GameWrapper>
      <h2 className="counter">
          {players.length} / {totalPlayers} 
          {/*some type of placeholder */}
        </h2>
      <button className='button' onClick={handleEndRound}> 
        End Round
      </button>
      <button className='button' onClick={handleCloseRoom}>
          Close Room
      </button>
      </div>
    </div>
  );
}

export default GameView;