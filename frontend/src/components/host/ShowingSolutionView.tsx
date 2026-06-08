import '../../App.css';
import '../../ShowingSolution.css';
import GameWrapper from './GameWrapper';
import type { BoardData } from '../../types';
import { useBackgroundMusic } from '../../hooks/useBackgroundMusic';

interface ShowingSolutionViewProps {
  nickname: string;
  answer: number | null;
  boardData: BoardData | null;
}

const ShowingSolutionView = ({ nickname, answer, boardData }: ShowingSolutionViewProps) => {
  const { isPlaying, toggleMute } = useBackgroundMusic('/audio/ShowingMove.mp3');
  return (
    <div className="show-solution-container">
      <div className="left-section"></div>
      <div className="middle-section">
        <div className="wrapper header-text">
          <h2 className="title"> Player {nickname} showing their solution</h2>
          <h2> {answer !== null ? answer - (boardData?.moves || 0) : 0} moves left </h2>
          <GameWrapper boardData={boardData} className='showing-solution'></GameWrapper>
        </div>
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
          {/* <button className="button-circle"></button> */}
        </div>
      </div>
    </div>
  );
};

export default ShowingSolutionView;
