import BoardScene from './scenes/BoardScene';

export const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 1024,
  height: 1024,
  scene: [BoardScene],
};
