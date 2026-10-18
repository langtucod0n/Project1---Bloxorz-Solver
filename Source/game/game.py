from __future__ import annotations

from .level_loader import validate_level
from .state import State, STANDING, LYING_H, LYING_V, TRANSITIONS, cells

# bước lăn 1 ô của cube đơn khi split
CUBE_DELTA = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
SWITCH_ACTION = "S"  # đổi cube điều khiển, chỉ hợp lệ khi đang split


class Game:
    ACTIONS = ("U", "D", "L", "R")  # thứ tự CỐ ĐỊNH của khối thường

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
        self._switches = []
        self._split_at = {}                     # ô công tắc split -> (ô cube 0, ô cube 1)
        for sw in level.get("switches", []):
            if sw["type"] == "split":
                self._split_at[tuple(sw["cell"])] = tuple(tuple(p) for p in sw["split_to"])
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

    def _roll_cube(self, s: State, a: str) -> State:
        #Cube đang điều khiển lăn 1 ô. Lăn vào ô cube kia là nước KHÔNG hợp lệ (P1).
        try:
            dr, dc = CUBE_DELTA[a]
        except KeyError:
            raise ValueError(f"Nước đi không hợp lệ: {a!r}") from None
        p0, p1, act = s.split
        cur, other = (p0, p1) if act == 0 else (p1, p0)
        new = (cur[0] + dr, cur[1] + dc)
        if new == other:
            raise ValueError(f"Nước {a!r} từ {s}: cube lăn vào ô của cube kia")
        pair = (new, other) if act == 0 else (other, new)
        return s._replace(r=new[0], c=new[1], split=(*pair, act))

    def _apply_switches(self, s: State, arrived) -> State:
        #Áp công tắc soft/heavy tại các ô VỪA ĐẾN, lần lượt theo thứ tự khai báo.
        #Heavy chỉ nhận khối 1x2 đứng (không split).
        bits = s.bridges
        for kind, pos, mode, mask in self._switches:
            if pos not in arrived:
                continue
            if kind == "heavy" and (s.orient != STANDING or s.split is not None):
                continue
            if mode == "toggle":
                bits ^= mask
            elif mode == "open":
                bits |= mask
            else:
                bits &= ~mask
        return s if bits == s.bridges else s._replace(bridges=bits)

    @staticmethod
    def _merge(s: State) -> State:
        #Hai cube kề nhau (|dr|+|dc|==1) thì ghép lại thành khối 1x2 nằm.
        if s.split is None:
            return s
        (r0, c0), (r1, c1), _ = s.split
        if abs(r0 - r1) + abs(c0 - c1) != 1:
            return s
        if r0 == r1:
            return State(LYING_H, r0, min(c0, c1), s.bridges)
        return State(LYING_V, min(r0, r1), c0, s.bridges)

    def _land(self, s: State, a: str) -> tuple[State, str]:
        #B1 lăn, B2 kiểm tra rơi theo cầu hiện tại, B3 công tắc, rồi ghép khối.
        #Nước sai / S khi không split / cube lăn vào cube kia: ValueError.
        if a == SWITCH_ACTION:
            if s.split is None:
                raise ValueError("Hành động 'S' chỉ hợp lệ khi đang split")
            p0, p1, act = s.split
            new = 1 - act
            s2 = s._replace(r=s.split[new][0], c=s.split[new][1], split=(p0, p1, new))
            return s2, self.status(s2)          # không kích hoạt gì, không bao giờ rơi
        if s.split is None:
            s2 = self._roll(s, a)
            arrived = cells(s2)
        else:
            s2 = self._roll_cube(s, a)
            arrived = ((s2.r, s2.c),)
        st = self.status(s2)
        if st == "LOST":
            return s2, st                       # rơi: không kích hoạt công tắc
        s3 = self._apply_switches(s2, arrived)
        if s.split is None and s3.orient == STANDING and (s3.r, s3.c) in self._split_at:
            p0, p1 = self._split_at[(s3.r, s3.c)]   # tách: cube 0 điều khiển
            s3 = s3._replace(r=p0[0], c=p0[1], split=(p0, p1, 0))
        st = self.status(s3)
        if st == "LOST":
            return s3, st                       # P4: trả state sau B3 (bridges đã đổi)
        s4 = self._merge(s3)
        return s4, self.status(s4)

    def status(self, s: State) -> str:
        #PLAYING / WON / LOST của một trạng thái (theo mục 0.4).
        cs = cells(s)
        if any(self.tile(r, c, s) == "void" for r, c in cs):   # gồm cả ngoài bàn, cầu đóng
            return "LOST"
        if s.split is not None:                 # từng cube: fragile thì thua, goal không thắng
            if any(self.tile(r, c, s) == "fragile" for r, c in cs):
                return "LOST"
            return "PLAYING"
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
        #Chỉ trả nước HỢP LỆ, theo THỨ TỰ CỐ ĐỊNH ['U', 'D', 'L', 'R'] (+ 'S' khi split).
        acts = self.ACTIONS + ((SWITCH_ACTION,) if s.split is not None else ())
        out = []
        for a in acts:
            try:
                if self._land(s, a)[1] != "LOST":
                    out.append(a)
            except ValueError:                  # cube lăn vào cube kia
                pass
        return out

    def result(self, s: State, a: str) -> State:
        #Không sửa s. a không hợp lệ (hoặc dẫn tới rơi) thì raise ValueError.
        s2, st = self._land(s, a)
        if st == "LOST":
            raise ValueError(f"Nước {a!r} từ {s} dẫn tới rơi")
        return s2

    def is_goal(self, s: State) -> bool:
        return s.split is None and s.orient == STANDING and self.tile(s.r, s.c, s) == "goal"

    def cost(self, s: State, a: str, s2: State) -> float:
        return 1.0

    # --- cho GUI chơi tay ---
    def step(self, s: State, a: str) -> tuple[State, str]:
        return self._land(s, a)        # LOST: trả trạng thái thô để GUI vẽ hiệu ứng rơi