import os
import json
from app.game_state.BoardState import Board, Position

def render_board(board: Board):
    print(f"\n=== PLANSZA: {board.width}x{board.height} ===")
    
    # 1. Górna krawędź zewnętrzna
    print(" " + "__" * board.width)

    for y in range(board.height):
        # Linia pionowa (ściany boczne i zawartość)
        # Zaczynamy od lewej krawędzi zewnętrznej
        line_content = "|"
        
        # Linia pozioma (podłogi / ściany dolne)
        line_bottom = "|"

        for x in range(board.width):
            cell = board.grid[y][x]
            
            # Określamy znak zawartości
            char = "o"
            if x == board.finish.pos.x and y == board.finish.pos.y:
                char = "*"
            elif any(p.x == x and p.y == y for p in board.mole_spawn_points):
                char = "+"

            # Sprawdzamy prawą ścianę komórki
            # Jeśli wall_right jest True, rysujemy |, w przeciwnym razie spację
            right_wall = "|" if cell.wall_right else " "
            line_content += f"{char}{right_wall}"

            # Sprawdzamy dolną ścianę komórki
            # Jeśli wall_bottom jest True, rysujemy __, w przeciwnym razie spacje
            bottom_wall = "__" if cell.wall_bottom else "  "
            line_bottom += bottom_wall

        print(line_content)
        # Wyświetlamy linię dolną tylko jeśli nie jest to ostatnia linia 
        # (którą i tak zamknie wall_bottom ustawiony przez validator)
        if any(board.grid[y][ix].wall_bottom for ix in range(board.width)):
            # Podmieniamy ostatni znak dolnej linii na krawędź, żeby domknąć ramkę
            print(line_bottom[:-1] + "|")


def print_cell_details(board: Board):
    print("\n--- SZCZEGÓŁY KOMÓREK ---")
    # Iteracja przez grid zdefiniowany w Board
    for y in range(board.height):
        for x in range(board.width):
            cell = board.grid[y][x]
            # Zbieramy aktywne ściany dla czytelności
            walls = []
            if cell.wall_top: walls.append("Góra")
            if cell.wall_bottom: walls.append("Dół")
            if cell.wall_left: walls.append("Lewo")
            if cell.wall_right: walls.append("Prawo")
            
            wall_str = ", ".join(walls) if walls else "Brak"
            
            special = []
            if cell.is_finish: special.append("META")
            if cell.can_spawn_mole: special.append("SPAWN-OK")
            
            special_str = f" [{', '.join(special)}]" if special else ""
            
            print(f"Komórka ({x}, {y}): Ściany: {wall_str}{special_str}")


def run_tests():
    folder_path = "../board_jason"
    
    if not os.path.exists(folder_path):
        print(f"Błąd: Folder '{folder_path}' nie istnieje.")
        return

    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    if not json_files:
        print("Nie znaleziono plików JSON w folderze.")
        return

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        print(f"\nWczytywanie: {file_name}")
        
        try:
            board = Board.from_json_file(file_path)
            render_board(board)
            print_cell_details(board)
        except Exception as e:
            print(f"Błąd podczas wczytywania {file_name}: {e}")

if __name__ == "__main__":
    run_tests()