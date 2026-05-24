import '../../App.css';
import GameWrapper from './GameWrapper';
import type { BoardData } from '../../types';
import { useBackgroundMusic } from '../../hooks/useBackgroundMusic';

interface ShowingSolutionViewProps {
  nickname: string;
  boardData: BoardData | null;
}

const ShowingSolutionView = ({ nickname, boardData }: ShowingSolutionViewProps) => {
  const { isPlaying, toggleMute } = useBackgroundMusic('/audio/ShowingMove.mp3');
  return (
    <div className="show-solution-container">
      {/* <h1 className='title'>Game View</h1> */}
      <div className="left-section"></div>
      <div className="middle-section">
        <div className="wrapper" style={{ marginTop: -50 }}>
          <h3>Player {nickname} showing their solution:</h3>
          <GameWrapper boardData={boardData}></GameWrapper>
        </div>
      </div>
      <div className="right-section">
        <div className="side-controls wrapper">
          <button className="button-circle" onClick={toggleMute}>
            <img 
              src={isPlaying ? "/icons/mute.svg" : "/icons/unmute.svg"} 
              alt={isPlaying ? "Mute" : "Music"} 
              className="button-icon"
            />
          </button>
          <button className="button-circle"></button>
        </div>
      </div>
    </div>
  );
};

export default ShowingSolutionView;
