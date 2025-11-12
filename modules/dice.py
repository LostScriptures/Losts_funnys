from random import randint

class Dice:
    total: int = 0
    __avg_total: float = 0.0
    __highest: int = 0
    __lowest: int = 0

    def __init__(self, num_rolls: int = 1, sides: int = 6, mod: int = 0, die_string: str | None = None):
        self.num_rolls = num_rolls
        self.sides = sides
        self.mod = mod

        if die_string is not None:
            self.parse_notation(die_string)
        
        else:
            self._calc_avg_total()
            self._calc_min_max()
    
    def _roll(self):
        return randint(1, self.sides)

    def _calc_avg_total(self):
        sum_sides = sum([x for x in range(1, self.sides + 1)])
        self.__avg_total = (sum_sides / self.sides) * self.num_rolls + self.mod

    def _calc_min_max(self):
        self.__lowest = self.num_rolls + self.mod
        self.__highest = self.sides * self.num_rolls + self.mod

    def roll(self):
        """Does not count towards the dice total, but uses the dices settings"""
        return self._roll() + self.mod

    def roll_all(self):
        """Rolls all deice and saves in total. Re-rolling will overwrite the total. Same for avg_total"""
        for _ in range(self.num_rolls):
            self.total += self._roll()
        self.total += self.mod

        self._calc_avg_total()

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

        self._calc_avg_total()
        self._calc_min_max()
    
    def avg(self):
        """Returns the average total amount for the current dice settings"""
        return self.__avg_total

    def min_max(self):
        return self.__lowest, self.__highest

    def __repr__(self):
        return f"Dice(Num Rolls: {self.num_rolls}, Sides: {self.sides}, Mod: {self.mod})"


def do_dice(self, args):
    pass

if __name__ == "__main__":
    d = Dice()

    print(d)
    print(d.roll_all())
    print(d.avg())
    print(d.min_max())