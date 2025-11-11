from random import randint

class Dice:
    last_roll: int = 0
    total: int = 0

    def __init__(self, sides: int = 6, mod: int = 0, num_rolls: int = 1):
        self.sides = sides
        self.mod = mod
        self.num_rolls = num_rolls
    
    def roll(self):
        pass

    def parse_notation(self, notation: str):
        notation = notation.replace(" ", "")
        temp = notation.split("d")
        
        self.num_rolls = int(temp[0])

        for i, s in enumerate(temp[1]):
            if not s.isdigit():
                self.sides = int(temp[1][0:i])
                self.mod = int(temp[1][i:])
                break

    def __repr__(self):
        return f"Dice(Num Rolls: {self.num_rolls}, Sides: {self.sides}, Mod: {self.mod})"


def do_dice(self, args):
    pass

if __name__ == "__main__":
    d = Dice()
    d.parse_notation("3d20 + 5")
    print(d)