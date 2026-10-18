"""Game giả theo giao diện TV2 (chỉ để thử logic solver). Game thật nằm trong game/."""
from typing import NamedTuple, Optional

TABLE = {(0, "U"): (2, -2, 0), (0, "D"): (2, 1, 0), (0, "L"): (1, 0, -2), (0, "R"): (1, 0, 1),
         (1, "U"): (1, -1, 0), (1, "D"): (1, 1, 0), (1, "L"): (0, 0, -1), (1, "R"): (0, 0, 2),
         (2, "U"): (0, -1, 0), (2, "D"): (0, 2, 0), (2, "L"): (2, 0, -1), (2, "R"): (2, 0, 1)}
NAMES = {".": "floor", "#": "void", "G": "goal", "F": "fragile"}

class State(NamedTuple):
    orient: int
    r: int
    c: int
    bridges: int = 0
    split: Optional[tuple] = None

class Game:
    def __init__(self, grid, start):
        self.grid, self.start = grid, start
        self.rows, self.cols = len(grid), len(grid[0])
        self.goal = next((r, c) for r in range(self.rows) for c in range(self.cols) if grid[r][c] == "G")

    def tile(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return NAMES[self.grid[r][c]]
        return "void"

    def cells(self, s):
        if s.orient == 0:
            return ((s.r, s.c),)
        return ((s.r, s.c), (s.r, s.c + 1) if s.orient == 1 else (s.r + 1, s.c))

    def initial_state(self):
        return State(0, *self.start)

    def _roll(self, s, a):
        o, dr, dc = TABLE[(s.orient, a)]
        return s._replace(orient=o, r=s.r + dr, c=s.c + dc) 

    def _valid(self, s):
        return all(self.tile(r, c) != "void" and not (self.tile(r, c) == "fragile" and s.orient == 0)
                   for r, c in self.cells(s))

    def actions(self, s):
        return [a for a in "UDLR" if self._valid(self._roll(s, a))]

    def result(self, s, a):
        s2 = self._roll(s, a)
        if not self._valid(s2): raise ValueError("nước đi không hợp lệ")
        return s2

    def is_goal(self, s):
        return s.orient == 0 and self.tile(s.r, s.c) == "goal"

    def cost(self, s, a, s2):
        return 1
           