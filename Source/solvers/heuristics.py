import math
from solvers.costs import MIN_COST
from solvers.game_access import occupied, goal_pos, is_split

def h_manhattan_half(game, s):
    """Cận dưới chi phí còn lại. Admissible và consistent (xem báo cáo)."""
    if game.is_goal(s):
        return 0

    if is_split(s):
        return MIN_COST     # tạm an toàn khi khối tách; chứng minh lại sau khi TV3 xong

    gr, gc = goal_pos(game)
    d = min(abs(r - gr) + abs(c - gc) for r, c in occupied(game, s))
    return max(1, math.ceil(d / 2)) * MIN_COST

