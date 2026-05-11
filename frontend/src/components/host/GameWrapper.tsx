import { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import { config } from '../../phaser/config';
import type { BoardData } from '../../types';

interface GameWrapperProps {
  boardData: BoardData | null;
}

const GameWrapper = ({ boardData }: GameWrapperProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);

  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!gameRef.current && containerRef.current) {
      gameRef.current = new Phaser.Game({
        ...config,
        parent: containerRef.current,
        scale: {
          ...config.scale,
          mode: Phaser.Scale.FIT,
          autoCenter: Phaser.Scale.CENTER_BOTH,
        },
      });

      gameRef.current.events.once('ready', () => {
        setIsReady(true);
      });
    }

    return () => {
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (isReady && gameRef.current && boardData) {
      gameRef.current.events.emit('UPDATE_BOARD', boardData);
    }
  }, [boardData, isReady]);

  return <div ref={containerRef} className="phaser-wrapper" />;
};

export default GameWrapper;
