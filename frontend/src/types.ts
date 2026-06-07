export type PlayerAnswer = {
  nick: string;
  answer: number;
};

export interface PoolOption {
  id: string;
  display_name: string;
}

export interface Position {
  x: number;
  y: number;
}

export interface Cell {
  wall: [boolean, boolean, boolean, boolean];
}

export interface BoardData {
  width: number;
  height: number;
  grid: Cell[][];
  mole_position: Position[];
  moves: number;
  finish: Position;
  finish_mole: -1 | 0 | 1 | 2 | 3 | 4;
}
