import '../RespondView.css';

interface PadArrowIconProps {
  dir: string;
  isActive: boolean;
  onClick: () => void;
  fillColor: string;
}

const DIRECTIONS = {
  U: { rotation: 0 },
  R: { rotation: 90 },
  D: { rotation: 180 },
  L: { rotation: 270 },
} as const;

export default function ArrowIcon({ dir, isActive, onClick, fillColor }: PadArrowIconProps) {
  const rotation = DIRECTIONS[dir as keyof typeof DIRECTIONS]?.rotation || 0;

  return (
    <svg
      viewBox="0 0 100 100"
      className={`arrow-icon ${isActive ? 'active' : ''}`}
      onClick={onClick}
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      <polygon
        points="50,10 90,50 70,50 70,90 30,90 30,50 10,50"
        fill={fillColor}
        stroke="black"
        strokeWidth={isActive ? '4' : '0'}
        strokeLinejoin="round"
      />
    </svg>
  );
}
