from random import randint, choice
from enum import IntEnum
from typing import List, Union, overload
from time import sleep

class Dir(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Board(list):
    invalid_move = False

    @overload
    def __init__(self, initial_board: List[List[int]]) -> None: ...
    @overload
    def __init__(self, rows: int, cols: int, default_value: Union[int, None] = None) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        if len(args) == 1 and isinstance(args[0], list):
            # Case: Board(initial_board)
            self.extend(args[0])
        else:
            # Case: Board(rows, cols, default_value)
            if len(args) == 2 or len(args) == 3:
                rows, cols = args[0], args[1]
                default_value = args[2] if len(args) == 3 else None
                self.extend([[default_value for _ in range(cols)] for _ in range(rows)])
    
    def rotate(self, direction: str = "right"):
        """Rotates the board in the specified direction"""
        N = len(self)

        if direction == "right":
            rotated = [list(row) for row in zip(*self[::-1])]

        elif direction == "left":
            rotated = [list(row) for row in zip(*[row[::-1] for row in self])]

        else:
            raise ValueError("Invalid direction. Use 'right' or 'left'.")

        self.clear()
        self.extend(rotated)
        return self

    def reverse(self):
        super().reverse()
        return self
    
    def merge_tiles(self):
        for x in range(len(self[0])):
            column = [self[y][x] for y in range(len(self))]
            cleaned = [num for num in column if num != 0]
            cleaned.extend([0] * (len(column) - len(cleaned)))
            new_column = []
            i = 0
            while i < len(cleaned):
                if i + 1 < len(cleaned) and cleaned[i] == cleaned[i + 1] and cleaned[i] != 0:
                    new_column.append(cleaned[i] * 2)
                    i += 2
                else:
                    if cleaned[i] != 0:
                        new_column.append(cleaned[i])
                    i += 1
            while len(new_column) < len(cleaned):
                new_column.append(0)
            for y in range(len(self)):
                self[y][x] = new_column[y]
        return self
    
class Game:
    choices = [2, 4]

    def __init__(self) -> None:
        self.reset()
        self.random_tile()
        self.random_tile()
    
    def move(self, dir: Dir):
        """Make a permanent move to the board"""
        save = self.board.copy()

        if dir == Dir.DOWN:
            self.board.reverse().merge_tiles().reverse()
            return

        elif dir == Dir.LEFT:
            self.board.rotate().merge_tiles().rotate("left")
            return
        
        elif dir == Dir.RIGHT:
            self.board.rotate().reverse().merge_tiles().reverse().rotate("left")
            return
            
        self.board.merge_tiles()
        
        if self.board == save: # The move did nothing
            self.board.invalid_move = True
    
    def simulate_move(self, dir: str):
        # Copys the current board and makes the move allowing to check for invalid moves
        ...

    def check_loss(self):
        # Check if there are any more valid moves by simulation every next move after a user move
        for y in range(4):
            for x in range(4):
                if self.board[y][x] == 0:
                    return False

        moves = []
        temp = Game()
        for dir in [Dir.UP, Dir.DOWN, Dir.LEFT, Dir.RIGHT]:
            temp.board = Board(self.board)
            temp.move(dir)

            if not temp.board.invalid_move:
                moves.append(True)

        if any(moves):
            return False
        
        return True                        

    def to_string(self):
        s = ""
        for row in self.board:
            s += f" --- --- --- ---\n| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n"
        s += " --- --- --- ---\n"
        return s

    def reset(self):
        self.board = Board(4, 4, 0)
    
    def random_tile(self):
        empty = []
        for y in range(4):
            for x in range(4):
                if self.board[y][x] == 0:
                    empty.append((y, x))
        
        if empty:
            pos = choice(empty)
            self.board[pos[0]][pos[1]] = choice(self.choices)

    def tick(self, dir: str):
        match dir:
            case "up":
                self.move(Dir.UP)
            case "down":
                self.move(Dir.DOWN)
            case "left":
                self.move(Dir.LEFT)
            case "right":
                self.move(Dir.RIGHT)

def do_2048(self):
    return

def help_2048(self):
    print("Not implemented yet")

if __name__ == "__main__":
    g = Game()

    while True:
        print(g.to_string())
        direction = input("Direction> ")

        match direction:
            case "u":
                g.tick("up")
            case "d":
                g.tick("down")
            case "l":
                g.tick("left")
            case "r":
                g.tick("right")
        
        if g.board.invalid_move:
            print("Invalid Move")
            sleep(0.75)
            continue

        g.random_tile()

        if g.check_loss():
            print("You lost")
            break
