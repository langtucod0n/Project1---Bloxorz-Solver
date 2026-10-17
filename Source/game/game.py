from __future__ import annotations

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
        # cầu: bit i của State.bridges = 1 <=> cầu id=i đang mở
        self._bridge_of = {}                    # ô -> id cầu
        self._initial_bridges = 0
        for b in level.get("bridges", []):
            for r, c in b["cells"]:
                self._bridge_of[(r, c)] = b["id"]
            if b["open"]:
                self._initial_bridges |= 1 << b["id"]
        # công tắc soft/heavy theo thứ tự khai báo; chuẩn hóa mode về toggle|open|close
        # (công tắc split được bỏ qua ở đợt này)
        self._switches = []
        for sw in level.get("switches", []):
            if sw["type"] not in ("soft", "heavy"):
                continue
            mode = sw["mode"]
            if mode == "permanent":
                mode = "open" if sw.get("state", True) else "close"
            mask = sum(1 << t for t in sw["targets"])
            self._switches.append((sw["type"], tuple(sw["cell"]), mode, mask))

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

    def tile(self, r: int, c: int, s: State | None = None) -> str:
        #Loại ô; ô thuộc cầu: mở -> floor, đóng -> void. s=None dùng trạng thái cầu ban đầu.
        if not (0 <= r < self._rows and 0 <= c < self._cols):
            return "void"
        b = self._bridge_of.get((r, c))
        if b is not None:
            bits = self._initial_bridges if s is None else s.bridges
            return "floor" if bits >> b & 1 else "void"
        return self._tiles[r][c]

    # --- nội bộ ---
    def _roll(self, s: State, a: str) -> State:
        #Lăn thô: chưa kiểm tra hợp lệ. _replace giữ nguyên bridges, split.
        try:
            orient, dr, dc = TRANSITIONS[(s.orient, a)]
        except KeyError:
            raise ValueError(f"Nước đi không hợp lệ: {a!r}") from None
        return s._replace(orient=orient, r=s.r + dr, c=s.c + dc)

    def _apply_switches(self, s: State) -> State:
        #Áp hiệu ứng công tắc soft/heavy lên bridges, lần lượt theo thứ tự khai báo.
        cs = cells(s)
        bits = s.bridges
        for kind, pos, mode, mask in self._switches:
            if kind == "heavy":
                if s.orient != STANDING or s.split is not None or cs[0] != pos:
                    continue
            elif pos not in cs:
                continue
            if mode == "toggle":
                bits ^= mask
            elif mode == "open":
                bits |= mask
            else:
                bits &= ~mask
        return s if bits == s.bridges else s._replace(bridges=bits)

    def _land(self, s: State, a: str) -> tuple[State, str]:
        #Lăn (B1), kiểm tra rơi theo cầu hiện tại (B2), rồi mới áp công tắc (B3).
        s2 = self._roll(s, a)
        st = self.status(s2)
        if st == "LOST":
            return s2, st                       # rơi: không kích hoạt công tắc
        s3 = self._apply_switches(s2)
        return s3, self.status(s3)

    def status(self, s: State) -> str:
        #PLAYING / WON / LOST của một trạng thái (theo mục 0.4).
        cs = cells(s)
        if any(self.tile(r, c, s) == "void" for r, c in cs):   # gồm cả ngoài bàn, cầu đóng
            return "LOST"
        if s.orient == STANDING:
            t = self.tile(*cs[0], s)
            if t == "fragile":
                return "LOST"
            if t == "goal":
                return "WON"
        return "PLAYING"

     # --- 5 hàm giao diện cho solver ---
    def initial_state(self) -> State:
        return State(STANDING, self._start[0], self._start[1], self._initial_bridges)

    def actions(self, s: State) -> list[str]:
        #Chỉ trả nước HỢP LỆ, theo THỨ TỰ CỐ ĐỊNH ['U', 'D', 'L', 'R'].
        return [a for a in self.ACTIONS if self._land(s, a)[1] != "LOST"]

    def result(self, s: State, a: str) -> State:
        #Không sửa s. a không hợp lệ (hoặc dẫn tới rơi) thì raise ValueError.
        s2, st = self._land(s, a)
        if st == "LOST":
            raise ValueError(f"Nước {a!r} từ {s} dẫn tới rơi")
        return s2

    def is_goal(self, s: State) -> bool:
        return s.orient == STANDING and self.tile(s.r, s.c, s) == "goal"

    def cost(self, s: State, a: str, s2: State) -> float:
        return 1.0

    # --- cho GUI chơi tay ---
    def step(self, s: State, a: str) -> tuple[State, str]:
        return self._land(s, a)        # LOST: trả trạng thái thô để GUI vẽ hiệu ứng rơi