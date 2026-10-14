from typing import NamedTuple

# Khai báo các hằng số orientation
STANDING = 0
LYING_H = 1
LYING_V = 2

class State(NamedTuple):
    orient: int
    r: int
    c: int
    bridges: int = 0
    split: tuple | None = None

def cells(s: State) -> tuple[tuple[int, int], ...]:
    """Trả về danh sách các tọa độ ô mà khối block đang chiếm"""
    raise NotImplementedError

def state_to_dict(s: State, game: 'Game') -> dict:
    """Chuyển State thành dictionary để xuất ra JSON cho GUI/API"""
    raise NotImplementedError

def state_from_dict(d: dict) -> State:
    """Khôi phục State từ dictionary JSON"""
    raise NotImplementedError