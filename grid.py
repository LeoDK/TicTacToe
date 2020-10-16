class Grid:

    def __init__ (self, neutral):
        self.grid = [ [neutral]*3 for i in range(3) ]
        self.neutral = neutral

    def set (self, x, y, player):
        self.grid[x][y] = player

    def copy (self, other):
        self.grid = other.grid

    def __str__ (self):
        ret = "______\n"
        for line in self.grid:
            ret = ret + "|" + " ".join(line) + "|" + "\n"
        ret += "------\n"
        return ret
