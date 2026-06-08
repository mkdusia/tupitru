import { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import { config } from '../../phaser/config';
import type { BoardData } from '../../types';

interface GameWrapperProps {
  boardData: BoardData | null;
  className?: string;
}

const GameWrapper = ({ boardData, className = 'phaser-wrapper' }: GameWrapperProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);

  const [isSceneReady, setIsSceneReady] = useState(false);

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

      gameRef.current.events.once('BOARD_SCENE_READY', () => {
        setIsSceneReady(true);
      });
    }

    return () => {
      if (gameRef.current) {
        gameRef.current.events.off('BOARD_SCENE_READY');
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (isSceneReady && gameRef.current && boardData) {
      gameRef.current.events.emit('UPDATE_BOARD', boardData);
    }
  }, [boardData, isSceneReady]);

  return <div ref={containerRef} className={`${className}`} />;
};

export default GameWrapper;
