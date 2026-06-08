import '../../App.css';
import { useState, useEffect } from 'react';
import '../../RespondView.css';
import CircleIcon from '../../assets/CircleIcon';
import PadArrowIcon from '../../assets/PadArrowIcon';

interface RespondViewProps {
  answer: number;
  movesLeft: number;
  setMole: (num: number) => void;
  setDirection: (dir: string) => void;
  setMovesLeft: (moves: number) => void;
  handleSendStep: () => void;
  handleGiveUp: () => void;
  handleRevert: () => void;
}

const MOLES = [
  { id: 0, color: '#1975ff' },
  { id: 1, color: '#376637' },
  { id: 2, color: '#c00000' },
  { id: 3, color: '#ff6ed8' },
  { id: 4, color: '#ffc60b' },
];

function RespondView({
  answer,
  movesLeft,
  setMole,
  setDirection,
  setMovesLeft,
  handleSendStep,
  handleGiveUp,
  handleRevert,
}: RespondViewProps) {
  const [activeMole, setActiveMole] = useState<number | null>(null);
  const [activeDir, setActiveDir] = useState<string | null>(null);

  const handleMoleClick = (id: number) => {
    if (activeMole === id) {
      setActiveMole(null);
    } else {
      setActiveMole(id);
      setMole(id);
    }
  };

  const handleDirClick = (dir: string) => {
    if (activeDir === dir) {
      setActiveDir(null);
    } else {
      setActiveDir(dir);
      setDirection(dir);
    }
  };

  useEffect(() => {
    if (activeMole !== null && activeDir !== null && movesLeft > 0) {
      handleSendStep();

      setMovesLeft(movesLeft - 1);
      setActiveDir(null);
    }
  }, [activeMole, activeDir, movesLeft]);

  const onRevertClick = () => {
    if (movesLeft < answer) {
      handleRevert();
      setMovesLeft(movesLeft + 1);
    }
  };

  const defaultArrowColor = '#ffffff';
  const currentArrowColor = activeMole !== null ? MOLES[activeMole].color : defaultArrowColor;
  return (
    <div className="mobile-container">
      <div className="wrapper header-text">
        <h1 className="title"> Show solution </h1>
        <h2> {movesLeft} moves left </h2>

        <div className="moles-container">
          <div className="moles-row top-row">
            {MOLES.slice(0, 3).map((m) => (
              <CircleIcon
                key={m.id}
                color={m.color}
                isActive={activeMole === m.id}
                onClick={() => handleMoleClick(m.id)}
              />
            ))}
          </div>
          <div className="moles-row bottom-row">
            {MOLES.slice(3, 5).map((m) => (
              <CircleIcon
                key={m.id}
                color={m.color}
                isActive={activeMole === m.id}
                onClick={() => handleMoleClick(m.id)}
              />
            ))}
          </div>
        </div>

        <div className="dpad-container">
          <div className="dpad-up">
            <PadArrowIcon
              dir="U"
              isActive={activeDir === 'U'}
              onClick={() => handleDirClick('U')}
              fillColor={currentArrowColor}
            />
          </div>
          <div className="dpad-left">
            <PadArrowIcon
              dir="L"
              isActive={activeDir === 'L'}
              onClick={() => handleDirClick('L')}
              fillColor={currentArrowColor}
            />
          </div>
          <div className="dpad-right">
            <PadArrowIcon
              dir="R"
              isActive={activeDir === 'R'}
              onClick={() => handleDirClick('R')}
              fillColor={currentArrowColor}
            />
          </div>
          <div className="dpad-down">
            <PadArrowIcon
              dir="D"
              isActive={activeDir === 'D'}
              onClick={() => handleDirClick('D')}
              fillColor={currentArrowColor}
            />
          </div>
        </div>

        <div className="actions-container">
          <div className="bottom-actions">
            <button className="button-revert" onClick={onRevertClick}>
              <svg
                viewBox="0 0 24 24"
                width="24"
                height="24"
                fill="none"
                stroke="black"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M9 14L4 9l5-5" />
                <path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11" />
              </svg>
            </button>
            <button className="button-giveup" onClick={handleGiveUp}>
              Give Up
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RespondView;
