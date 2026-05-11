import '../../App.css';
import GameWrapper from './GameWrapper';
import type { BoardData } from '../../types';

interface ShowingSolutionViewProps {
  nickname: string;
  boardData: BoardData | null;
}

const ShowingSolutionView = ({ nickname, boardData }: ShowingSolutionViewProps) => {
  return (
    <div className="app-container">
      {/* <h1 className='title'>Game View</h1> */}

      <div className="wrapper">
        <h3>Player {nickname} showing their solution:</h3>
        <GameWrapper boardData={boardData}></GameWrapper>
      </div>
    </div>
  );
};

export default ShowingSolutionView;
