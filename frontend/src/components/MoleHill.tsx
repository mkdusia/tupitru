import { useState, useEffect, useRef } from 'react';
import '../App.css';
import '../Mole.css';
import Hole from '../graphics/hole1.png';
import MoleRed from '../graphics/mole-red.png';
import MoleBlue from '../graphics/mole-blue.png';
import MoleGreen from '../graphics/mole-green.png';
import MolePink from '../graphics/mole-pink.png';
import MoleYellow from '../graphics/mole-yellow.png';

function Molehill() {
  const [activeMole, setActiveMole] = useState<number | null>(null);
  const lastMoleRef = useRef<number | null>(null);

  const moles = [
    { color: 'red', src: MoleRed },
    { color: 'pink', src: MolePink },
    { color: 'blue', src: MoleBlue },
    { color: 'green', src: MoleGreen },
    { color: 'yellow', src: MoleYellow },
  ];

  useEffect(() => {
    let hideTimeout: ReturnType<typeof setTimeout>;

    const popRandomMole = () => {
      let randomIndex;
      do {
        randomIndex = Math.floor(Math.random() * moles.length);
      } while (randomIndex === lastMoleRef.current);

      lastMoleRef.current = randomIndex;
      setActiveMole(randomIndex);

      hideTimeout = setTimeout(() => {
        setActiveMole(null);
      }, 3000);
    };

    const initialTimer = setTimeout(popRandomMole, 1000);
    const intervalTimer = setInterval(popRandomMole, 4000);

    return () => {
      clearTimeout(initialTimer);
      clearTimeout(hideTimeout);
      clearInterval(intervalTimer);
    };
  }, [moles.length]);

  return (
    <div className="molehill-container">
      <img src={Hole} className="hole-graphic" alt="Hole" />
      <div className="mole-mask">
        {moles.map((mole, index) => (
          <img
            key={mole.color}
            src={mole.src}
            alt={`${mole.color} mole`}
            className={`mole ${activeMole === index ? 'is-active' : ''}`}
          />
        ))}
      </div>
    </div>
  );
}

export default Molehill;
