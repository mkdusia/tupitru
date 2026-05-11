import '../../App.css';
import GameWrapper from './GameWrapper';
import type { BoardData } from '../../types';

interface ShowingSolutionViewProps {
  nickname: string;
  boardData: BoardData | null;
}

const ShowingSolutionView = ({ nickname, boardData }: ShowingSolutionViewProps) => {
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
      <div className="right-section"></div>
    </div>
  );
};

export default ShowingSolutionView;
