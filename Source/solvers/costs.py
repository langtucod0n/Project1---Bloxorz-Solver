"""Hàm chi phí của nhóm. Chi phí cơ sở lấy từ Game.cost của TV2 (hiện = 1),
bọc thêm phụ thu cho ô fragile. Không sửa file nào của TV2."""
from solvers.game_access import occupied, tile_kind

FRAGILE_EXTRA = 1    # phụ thu khi khối nằm lên ô fragile
MIN_COST = 1         # chi phí nhỏ nhất của 1 nước đi. Heuristic PHẢI dùng số này.
                     # = chi phí cơ sở của TV2 (1) vì phụ thu luôn >= 0.

class WeightedGame:
    """Bọc Game: chuyển mọi thứ cho Game thật, chỉ đổi cost()."""

    def __init__(self, game):
        self._g = game

    def __getattr__(self, name):
        if name == "_g":
            raise AttributeError(name)
        return getattr(self._g, name)

    def cost(self, s, a, s2):
        extra = FRAGILE_EXTRA if any(tile_kind(self._g, r, c) == "fragile" 
                                     for r, c in occupied(self._g, s2)) else 0

        return self._g.cost(s, a, s2) + extra

def weighted(game):
    return game if isinstance(game, WeightedGame) else WeightedGame(game)

def path_cost(game, moves, start=None):
    """Tổng chi phí khi đi theo moves (dùng cho test và benchmark)."""
    g = weighted(game)
    s = g.initial_state() if start is None else start
    total = 0
    
    for m in moves:
        s2 = g.result(s, m)
        total += g.cost(s, m ,s2)
        s = s2

    return total