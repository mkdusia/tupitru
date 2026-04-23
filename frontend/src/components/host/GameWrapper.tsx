import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { config } from '../../phaser/config';

const GameWrapper = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);

  useEffect(() => {
    if (!gameRef.current && containerRef.current) {
      gameRef.current = new Phaser.Game({
        ...config,
        parent: containerRef.current,
      });
    }

    return () => {
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, []);

  return <div ref={containerRef} className="game-container" />;
};

export default GameWrapper;
