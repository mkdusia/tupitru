import Phaser from 'phaser';
import type { BoardData } from '../../types';

export default class BoardScene extends Phaser.Scene {

  private moles: Phaser.GameObjects.Arc[] = [];
  private moleTexts: Phaser.GameObjects.Text[] = []; 
  
  private boardGraphics!: Phaser.GameObjects.Graphics;
  private targetRectangle!: Phaser.GameObjects.Rectangle;

  constructor() {
    super('BoardScene');
  }

  create() {
    this.boardGraphics = this.add.graphics();
    this.game.events.on('UPDATE_BOARD', this.handleNewBoardData, this);
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

    const MOLE_COLORS = [0xff9933, 0x99cc66, 0x66ccff, 0xffcc33, 0xff66cc];
    const MULTICOLOR_TARGET = 0xffffff;

    const targetColor = data.finish_mole === -1 ? MULTICOLOR_TARGET : MOLE_COLORS[data.finish_mole];
    const fx = OFFSET_X + data.finish.x * CELL_SIZE;
    const fy = OFFSET_Y + data.finish.y * CELL_SIZE;

    if(!this.targetRectangle){
      this.targetRectangle = this.add
        .rectangle(
          fx + CELL_SIZE / 2,
          fy + CELL_SIZE / 2,
          CELL_SIZE * 0.6,
          CELL_SIZE * 0.6,
          targetColor,
          0.5
        )
    }
    else {
      this.targetRectangle.setPosition(fx + CELL_SIZE / 2, fy + CELL_SIZE / 2);
      this.targetRectangle.setFillStyle(targetColor, 0.5);
    }
    this.targetRectangle.setStrokeStyle(4, targetColor);

    this.boardGraphics.clear()

    for (let y = 0; y < data.height; y++) {
      for (let x = 0; x < data.width; x++) {
        const cell = data.grid[y][x];
        const px = OFFSET_X + x * CELL_SIZE;
        const py = OFFSET_Y + y * CELL_SIZE;

        this.boardGraphics.lineStyle(1, 0x444444, 0.5);
        this.boardGraphics.strokeRect(px, py, CELL_SIZE, CELL_SIZE);

        this.boardGraphics.lineStyle(4, 0xffffff, 1);

        if (cell.wall[0]) this.boardGraphics.lineBetween(px, py, px + CELL_SIZE, py);
        if (cell.wall[1]) this.boardGraphics.lineBetween(px + CELL_SIZE, py, px + CELL_SIZE, py + CELL_SIZE);
        if (cell.wall[2]) this.boardGraphics.lineBetween(px, py + CELL_SIZE, px + CELL_SIZE, py + CELL_SIZE);
        if (cell.wall[3]) this.boardGraphics.lineBetween(px, py, px, py + CELL_SIZE);
      }
    }

    data.mole_position.forEach((pos, index) => {
      const mx = OFFSET_X + pos.x * CELL_SIZE + CELL_SIZE / 2;
      const my = OFFSET_Y + pos.y * CELL_SIZE + CELL_SIZE / 2;

      if(!this.moles[index]){
        const mole = this.add.circle(mx, my, CELL_SIZE * 0.35, MOLE_COLORS[index]);
        mole.setStrokeStyle(2, 0x000000);
        this.moles[index] = mole;
        this.moleTexts[index] = this.add
        .text(mx, my, index.toString(), {
          fontSize: '20px',
          color: '#ffffff',
          fontStyle: 'bold',
        })
        .setOrigin(0.5);
      }
      else {
        this.tweens.add({
          targets: this.moles[index],
          x: mx,
          y: my,
          duration: 250,
          ease: 'Power2.easeInOut'
        })

        this.tweens.add({
          targets: this.moleTexts[index],
          x: mx,
          y: my,
          duration: 250,
          ease: 'Power2.easeInOut'
        })
      }
    });
  }

  shutdown() {
    this.game.events.off('UPDATE_BOARD', this.handleNewBoardData, this);
    this.moles = [];
    this.moleTexts = [];
  }
}
