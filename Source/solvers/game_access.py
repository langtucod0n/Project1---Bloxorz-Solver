"""Cho DUY NHAT code cua TV1 cham vao noi bo game cua TV2."""
from game.state import cells

def occupied(game, s):
    return cells(s)

def tile_kind(game, r, c):
    return game.tile(r, c)

def goal_pos(game):
    return game.goal

def is_split(s):
    return getattr(s, "split", None) is not None

def split_switches(game):
    """Trả về dict: ô công tắc split -> (vị trí cube 0, vị trí cube 1).
    Rỗng nếu màn không có split switch. Hoạt động cả với WeightedGame."""
    return getattr(game, '_split_at', {})

def bridge_cells(game):
    """Tập mọi ô thuộc một cầu (bất kể đang đóng hay mở). Hoạt động cả với WeightedGame."""
    return set(getattr(game, '_bridge_of', {}))