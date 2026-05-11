import '../../App.css';
import GameWrapper from './GameWrapper';
import type { PlayerAnswer, BoardData } from '../../types';

interface GameViewProps {
  totalPlayers: number;
  players: PlayerAnswer[];
  boardData: BoardData | null;
  handleCloseRoom: () => void;
  handleEndRound: () => void;
}

const GameView = ({
  totalPlayers,
  players,
  boardData,
  handleCloseRoom,
  handleEndRound,
}: GameViewProps) => {
  return (
    <div className="game-container">
      {/* <h1 className='title'>Game View</h1> */}
      <div className="right-section">
        <div className="wrapper">
          <h3>Answers:</h3>
          {players.length === 0 ? (
            <p>Waiting for answers...</p>
          ) : (
            <ul>
              {players.map((player, index) => (
                <li key={index} className="player-item">
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
      <div className="left-section">
        <GameWrapper boardData={boardData}></GameWrapper>
      </div>
    </div>
  );
};

export default GameView;
