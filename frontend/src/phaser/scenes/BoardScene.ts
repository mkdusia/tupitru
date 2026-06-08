import Phaser from 'phaser';
import type { BoardData } from '../../types';

const MOLE_COLOR_NAMES = ['blue', 'green', 'red', 'pink', 'yellow'];

export default class BoardScene extends Phaser.Scene {
  private moles: Phaser.GameObjects.Sprite[] = [];
  private boardGraphics!: Phaser.GameObjects.Graphics;
  private target!: Phaser.GameObjects.Image;

  constructor() {
    super('BoardScene');
  }

  preload() {
    this.load.image('background', '/graphics/grass.png');
    this.load.image('target-multi', '/graphics/hole1.png');

    MOLE_COLOR_NAMES.forEach((color) => {
      this.load.image(`mole-${color}`, `/graphics/mole-${color}.png`);
      this.load.image(`target-${color}`, `/graphics/target-${color}.png`);

      this.load.spritesheet(`sprite_${color}`, `/lalala/sprite_${color}.png`, {
        frameWidth: 256,
        frameHeight: 256,
      });
    });
  }

  create() {
    this.add.image(0, 0, 'background').setOrigin(0, 0).setDepth(0);
    this.boardGraphics = this.add.graphics().setDepth(1);
    this.game.events.on('UPDATE_BOARD', this.handleNewBoardData, this);

    MOLE_COLOR_NAMES.forEach((color) => {
      this.anims.create({
        key: `${color}-trans`,
        frames: this.anims.generateFrameNumbers(`sprite_${color}`, { start: 0, end: 5 }),
        frameRate: 15,
        repeat: 0,
      });

      this.anims.create({
        key: `${color}-walk`,
        frames: this.anims.generateFrameNumbers(`sprite_${color}`, { start: 6, end: 9 }),
        frameRate: 15,
        repeat: -1,
      });
    });

    this.game.events.emit('BOARD_SCENE_READY');
  }

  handleNewBoardData(data: BoardData) {
    this.renderBoard(data);
  }

  private getBoardMetrics(cols: number, rows: number) {
    const canvasWidth = this.scale.width;
    const canvasHeight = this.scale.height;
    const PADDING = 40;
    const usableWidth = canvasWidth - PADDING * 2;
    const usableHeight = canvasHeight - PADDING * 2;
    const cellWidth = usableWidth / cols;
    const cellHeight = usableHeight / rows;
    const CELL_SIZE = Math.min(cellWidth, cellHeight);

    const totalGridWidth = CELL_SIZE * cols;
    const totalGridHeight = CELL_SIZE * rows;
    const OFFSET_X = (canvasWidth - totalGridWidth) / 2;
    const OFFSET_Y = (canvasHeight - totalGridHeight) / 2;

    return { CELL_SIZE, OFFSET_X, OFFSET_Y };
  }

  renderBoard(data: BoardData) {
    const { CELL_SIZE, OFFSET_X, OFFSET_Y } = this.getBoardMetrics(data.width, data.height);

    const targetTextureKey =
      data.finish_mole === -1 ? 'target-multi' : `target-${MOLE_COLOR_NAMES[data.finish_mole]}`;

    const fx = OFFSET_X + data.finish.x * CELL_SIZE + CELL_SIZE / 2;
    const fy = OFFSET_Y + data.finish.y * CELL_SIZE + CELL_SIZE / 2;

    if (!this.target) {
      this.target = this.add.image(fx, fy, targetTextureKey).setDepth(1);
      this.target.setDisplaySize(CELL_SIZE * 0.8, CELL_SIZE * 0.8);
    } else {
      this.target.setPosition(fx, fy);
      this.target.setTexture(targetTextureKey);
      this.target.setDisplaySize(CELL_SIZE * 0.8, CELL_SIZE * 0.8);
    }

    this.boardGraphics.clear();

    for (let y = 0; y < data.height; y++) {
      for (let x = 0; x < data.width; x++) {
        const cell = data.grid[y][x];
        const px = OFFSET_X + x * CELL_SIZE;
        const py = OFFSET_Y + y * CELL_SIZE;

        this.boardGraphics.lineStyle(2, 0x3c1022, 0.5);
        this.boardGraphics.strokeRect(px, py, CELL_SIZE, CELL_SIZE);

        this.boardGraphics.lineStyle(10, 0xffffff, 1);

        const totalGridWidth = data.width * CELL_SIZE;
        const totalGridHeight = data.height * CELL_SIZE;
        this.boardGraphics.lineStyle(10, 0xffffff, 1);
        this.boardGraphics.strokeRect(OFFSET_X, OFFSET_Y, totalGridWidth, totalGridHeight);

        if (cell.wall[0]) this.boardGraphics.lineBetween(px, py, px + CELL_SIZE, py);
        if (cell.wall[1])
          this.boardGraphics.lineBetween(px + CELL_SIZE, py, px + CELL_SIZE, py + CELL_SIZE);
        if (cell.wall[2])
          this.boardGraphics.lineBetween(px, py + CELL_SIZE, px + CELL_SIZE, py + CELL_SIZE);
        if (cell.wall[3]) this.boardGraphics.lineBetween(px, py, px, py + CELL_SIZE);
      }
    }

    data.mole_position.forEach((pos, index) => {
      console.log(`Rendering mole ${index} at (${pos.x}, ${pos.y})`);
      const mx = OFFSET_X + pos.x * CELL_SIZE + CELL_SIZE / 2;
      const my = OFFSET_Y + pos.y * CELL_SIZE + CELL_SIZE / 2;
      const colorName = MOLE_COLOR_NAMES[index];

      if (!this.moles[index]) {
        const mole = this.add.sprite(mx, my, `sprite_${colorName}`, 0).setDepth(2);
        mole.setDisplaySize(CELL_SIZE * 0.8, CELL_SIZE * 0.8);
        this.moles[index] = mole;
      } else {
        console.log(`Updating mole ${index} position to (${mx}, ${my})`);
        const mole = this.moles[index];
        const currX = mole.x;
        const currY = mole.y;

        const dx = mx - currX;
        const dy = my - currY;

        if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
          // FIX: Check if this specific mole is already playing its walk cycle
          const isContinuing = mole.anims.currentAnim?.key === `${colorName}-walk`;

          this.tweens.killTweensOf(mole);
          mole.anims.stop();
          mole.off(Phaser.Animations.Events.ANIMATION_COMPLETE);
          mole.off(Phaser.Animations.Events.ANIMATION_COMPLETE_KEY + `${colorName}-trans`);

          mole.setRotation(0);
          mole.setFlipX(false);

          const isMovingRight = dx > 0.5;
          const isMovingLeft = dx < -0.5;
          const isMovingDown = dy > 0.5;
          const isMovingUp = dy < -0.5;

          if (isMovingLeft) {
            mole.setFlipX(true);
          } else if (isMovingRight) {
            mole.setFlipX(false);
          } else if (isMovingDown) {
            mole.setFlipX(false);
            mole.setRotation(Math.PI / 2);
          } else if (isMovingUp) {
            mole.setFlipX(false);
            mole.setRotation(-Math.PI / 2);
          }

          mole.off(Phaser.Animations.Events.ANIMATION_COMPLETE_KEY + `${colorName}-trans`);
          this.tweens.killTweensOf(mole);

          if (isContinuing) {
            mole.play(`${colorName}-walk`);

            this.tweens.add({
              targets: mole,
              x: mx,
              y: my,
              duration: 500,
              ease: 'Power2.easeInOut',
              onComplete: () => {
                mole.stop();
                mole.setFrame(6);
              },
            });
          } else {
            mole.play(`${colorName}-trans`);
            mole.chain(`${colorName}-walk`);

            mole.once(
              Phaser.Animations.Events.ANIMATION_COMPLETE_KEY + `${colorName}-trans`,
              () => {
                this.tweens.add({
                  targets: mole,
                  x: mx,
                  y: my,
                  duration: 500,
                  ease: 'Power2.easeInOut',
                  onComplete: () => {
                    mole.stop();
                    mole.setFrame(6);
                  },
                });
              }
            );
          }
        }
      }
    });
  }

  shutdown() {
    this.game.events.off('UPDATE_BOARD', this.handleNewBoardData, this);
    this.moles = [];
  }
}
