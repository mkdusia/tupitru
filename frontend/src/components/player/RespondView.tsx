import '../../App.css';
import TupitruTitle from '../Title';

interface RespondViewProps {
  answer: number;
}

function RespondView({ answer }: RespondViewProps) {
  return (
    <div className="app-container">
      <TupitruTitle />

      <div className="wrapper">
        <h2> You have given the best answer of: {answer}! </h2>
        <h2> Show the solution: </h2>
      </div>
    </div>
  );
}

export default RespondView;
