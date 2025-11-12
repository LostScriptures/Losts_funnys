from random import randint

class Dice:
    total: int = 0

    def __init__(self, num_rolls: int = 1, sides: int = 6, mod: int = 0, die_string: str | None = None):
        self.num_rolls = num_rolls
        self.sides = sides
        self.mod = mod

        if die_string is not None:
            self.parse_notation(die_string)
    
    def _roll(self):
        return randint(1, self.sides)
   
    def roll(self):
        """Does not count towards the dice total, but uses the dices settings"""
        return self._roll() + self.mod

    def roll_all(self):
        """Rolls all deice and saves in total. Re-rolling will overwrite the total. Same for avg_total"""
        for _ in range(self.num_rolls):
            self.total += self._roll()
        self.total += self.mod

        return self.total

    def parse_notation(self, notation: str):
        """Parses the DnD string notation for dice rolls into the class parameters"""
        notation = notation.replace(" ", "")
        temp = notation.split("d")
        
        self.num_rolls = int(temp[0])

        for i, s in enumerate(temp[1]):
            if not s.isdigit():
                self.sides = int(temp[1][0:i])
                self.mod = int(temp[1][i:])
                break
    
    @property
    def avg(self):
        """Returns the average total amount for the current dice settings"""
        sum_sides = sum([x for x in range(1, self.sides + 1)])
        return (sum_sides / self.sides) * self.num_rolls + self.mod

    @property
    def min_max(self):
        lowest = self.num_rolls + self.mod
        highest = self.sides * self.num_rolls + self.mod
        return lowest, highest

    def __repr__(self):
        return f"Dice(Num Rolls: {self.num_rolls}, Sides: {self.sides}, Mod: {self.mod})"


def do_dice(self, args):
    """Rolls dice in DnD notation. Example: '2d6+3' rolls two six-sided dice and adds 3 to the total."""
    pass

def help_dice(self):
    print(do_dice.__doc__)

if __name__ == "__main__":
    d = Dice()

    print(d)
    print(d.roll_all())
    print(d.avg)
    print(d.min_max)