import '../App.css';

interface CircleIconProps {
  color: string;
  isActive: boolean;
  onClick: () => void;
}

export default function CircleIcon({ color, isActive, onClick }: CircleIconProps) {
  return (
    <button
      className={`button-circle ${isActive ? 'active' : ''}`}
      onClick={onClick}
      style={{
        backgroundColor: color,
        border: isActive ? '4px solid black' : 'none',
        width: 'clamp(70px, 15vw, 85px)',
        height: 'clamp(70px, 15vw, 85px)',
      }}
    />
  );
}
