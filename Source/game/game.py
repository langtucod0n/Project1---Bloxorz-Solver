from .state import State

class Game:
    def __init__(self, level: dict):
        raise NotImplementedError

    # --- 5 hàm giao diện cho solver ---
    def initial_state(self) -> State:
        raise NotImplementedError

    def actions(self, s: State) -> list[str]:
        """Chỉ trả nước HỢP LỆ, theo THỨ TỰ CỐ ĐỊNH ['U', 'D', 'L', 'R']"""
        raise NotImplementedError

    def result(self, s: State, a: str) -> State:
        """Không sửa s; a không hợp lệ thì raise ValueError"""
        raise NotImplementedError

    def is_goal(self, s: State) -> bool:
        """Kiểm tra xem block có đang đứng trên goal không"""
        raise NotImplementedError

    def cost(self, s: State, a: str, s2: State) -> float:
        """Chi phí di chuyển, mặc định tạm bằng 1"""
        return 1.0  # Tạm trả về 1 theo yêu cầu

    # --- Hàm cho GUI chơi tay ---
    def step(self, s: State, a: str) -> tuple[State, str]:
        """Trả về (state_mới, status) với status là 'PLAYING', 'WON', hoặc 'LOST'"""
        raise NotImplementedError

    # --- Các thuộc tính thông tin bàn (TV1 và TV4 cần) ---
    @property
    def goal(self) -> tuple[int, int]:
        raise NotImplementedError

    @property
    def rows(self) -> int:
        raise NotImplementedError

    @property
    def cols(self) -> int:
        raise NotImplementedError

    def tile(self, r: int, c: int) -> str:
        """Trả về 'floor', 'void', 'goal', 'fragile' (Ngoài bàn trả 'void')"""
        raise NotImplementedError