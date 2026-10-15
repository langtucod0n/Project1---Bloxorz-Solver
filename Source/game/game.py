from .level_loader import validate_level
from .state import State, STANDING, TRANSITIONS, cells

class Game:
    ACTIONS = ("U", "D", "L", "R")  # thứ tự CỐ ĐỊNH

    def __init__(self, level: dict):
        validate_level(level)
        self.level = level
        legend = level["legend"]
        self._tiles = tuple(tuple(legend[ch] for ch in row) for row in level["grid"])
        self._rows = len(self._tiles)
        self._cols = len(self._tiles[0])
        self._start = tuple(level["start"])
        self._goal = next(
            (r, c)
            for r, row in enumerate(self._tiles)
            for c, t in enumerate(row)
            if t == "goal"
        )

    # --- thông tin bàn ---
    @property
    def goal(self) -> tuple[int, int]:
        return self._goal

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def tile(self, r: int, c: int) -> str:
        if 0 <= r < self._rows and 0 <= c < self._cols:
            return self._tiles[r][c]
        return "void"

    # --- nội bộ ---
    def _roll(self, s: State, a: str) -> State:
        #Lăn thô: chưa kiểm tra hợp lệ. _replace giữ nguyên bridges, split.
        try:
            orient, dr, dc = TRANSITIONS[(s.orient, a)]
        except KeyError:
            raise ValueError(f"Nước đi không hợp lệ: {a!r}") from None
        return s._replace(orient=orient, r=s.r + dr, c=s.c + dc)

    def status(self, s: State) -> str:
        #PLAYING / WON / LOST của một trạng thái (theo mục 0.4).
        cs = cells(s)
        if any(self.tile(r, c) == "void" for r, c in cs):   # gồm cả ngoài bàn
            return "LOST"
        if s.orient == STANDING:
            t = self.tile(*cs[0])
            if t == "fragile":
                return "LOST"
            if t == "goal":
                return "WON"
        return "PLAYING"

     # --- 5 hàm giao diện cho solver ---
    def initial_state(self) -> State:
        return State(STANDING, self._start[0], self._start[1])

    def actions(self, s: State) -> list[str]:
        #Chỉ trả nước HỢP LỆ, theo THỨ TỰ CỐ ĐỊNH ['U', 'D', 'L', 'R'].
        return [a for a in self.ACTIONS if self.status(self._roll(s, a)) != "LOST"]

    def result(self, s: State, a: str) -> State:
        #Không sửa s. a không hợp lệ (hoặc dẫn tới rơi) thì raise ValueError.
        s2 = self._roll(s, a)
        if self.status(s2) == "LOST":
            raise ValueError(f"Nước {a!r} từ {s} dẫn tới rơi")
        return s2

    def is_goal(self, s: State) -> bool:
        return s.orient == STANDING and self.tile(s.r, s.c) == "goal"

    def cost(self, s: State, a: str, s2: State) -> float:
        return 1.0

    # --- cho GUI chơi tay ---
    def step(self, s: State, a: str) -> tuple[State, str]:
        s2 = self._roll(s, a)          # LOST: trả trạng thái thô để GUI vẽ hiệu ứng rơi
        return s2, self.status(s2)