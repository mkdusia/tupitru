import '../../App.css';
import TupitruTitle from '../Title';

interface RespondViewProps {
  answer: number;
  setMole: (num: number) => void;
  setDirection: (num: number) => void;
  handleSendStep: () => void;
  handleGiveUp: () => void;
  handleRevert: () => void;
}

function RespondView({
  answer,
  setMole,
  setDirection,
  handleSendStep,
  handleGiveUp,
  handleRevert,
}: RespondViewProps) {
  return (
    <div className="app-container">
      <TupitruTitle />

      <div className="wrapper">
        <h2> You have given the best answer of: {answer} </h2>
        <h2> Show the solution: </h2>

        <div className="button-container">
          <label> Choose mole: </label>
          <button className="button-circle" onClick={() => setMole(0)}>
            0
          </button>
          <button className="button-circle" onClick={() => setMole(1)}>
            1
          </button>
          <button className="button-circle" onClick={() => setMole(2)}>
            2
          </button>
          <button className="button-circle" onClick={() => setMole(3)}>
            3
          </button>
          <button className="button-circle" onClick={() => setMole(4)}>
            4
          </button>
        </div>

        <div className="button-container">
          <label> Choose direction: </label>
          <button className="button-circle" onClick={() => setDirection(0)}>
            L
          </button>
          <button className="button-circle" onClick={() => setDirection(1)}>
            U
          </button>
          <button className="button-circle" onClick={() => setDirection(2)}>
            R
          </button>
          <button className="button-circle" onClick={() => setDirection(3)}>
            D
          </button>
        </div>

        <button className="button" onClick={handleSendStep}>
          Send
        </button>

        <div className="button-container">
          <button className="button" onClick={handleGiveUp}>
            Give up
          </button>
          <button className="button" onClick={handleRevert}>
            Revert
          </button>
        </div>
      </div>
    </div>
  );
}

export default RespondView;
