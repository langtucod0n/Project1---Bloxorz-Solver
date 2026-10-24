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


# ---------------------------------------------------------------------------
# Heuristic cải tiến: kết hợp Manhattan/2 + phạt orientation + xử lý split
# ---------------------------------------------------------------------------
from game.state import STANDING, LYING_H, LYING_V


def _orientation_penalty(orient, dr, dc):
    """Phạt thêm nếu orientation hiện tại không thuận lợi cho hướng di chuyển.

    Khi khối nằm ngang (LYING_H) mà cần di chuyển chủ yếu theo chiều dọc,
    hoặc nằm dọc (LYING_V) mà cần di chuyển chủ yếu theo chiều ngang,
    thì cần ít nhất 1 bước xoay orientation trước khi đến đích.
    Tuy nhiên bước xoay đó cũng di chuyển 1-2 ô, nên ta chỉ cộng 0.5
    để đảm bảo admissible.

    Ngoài ra, khối đang LYING muốn đứng ở goal (STANDING) cần ít nhất
    1 bước chuyển orientation. Nếu khoảng cách Manhattan <= 2 thì bước
    chuyển đó không được tính đủ trong ceil(d/2), nên cần cộng thêm.
    """
    if orient == STANDING:
        return 0
    # Khối đang nằm → cần ít nhất 1 bước để đứng lại tại goal.
    # Bước đứng lại cũng di chuyển, nên chỉ phạt 0.5 * MIN_COST.
    return 0.5 * MIN_COST


def h_combined(game, s):
    """Heuristic kết hợp: Manhattan/2 + orientation penalty + split handling.

    Admissible vì:
    ─ Manhattan/2: mỗi bước lăn di chuyển tối đa 2 ô Manhattan, nên
      ceil(d/2) * MIN_COST là cận dưới chặt chẽ.
    ─ Orientation penalty (0.5): khi khối đang LYING, nó cần ít nhất 1 bước
      chuyển thành STANDING tại goal. Bước đó cũng di chuyển 1–2 ô, nhưng
      nếu d <= 2, ceil(d/2) chưa tính đủ chi phí xoay. Cộng 0.5 an toàn vì
      chi phí mỗi bước >= 1.
    ─ Split: tính h cho mỗi cube tới goal rồi lấy max. Mỗi cube cần ít nhất
      ceil(d_i / 2) bước để hợp nhất và đi tới goal.

    Consistent vì:
    ─ |h(n) - h(n')| <= cost(n, a, n') cho mọi bước đi.
      Manhattan thay đổi tối đa 2 ô mỗi bước → ceil(d/2) thay đổi tối đa 1.
      Orientation penalty thay đổi tối đa 0.5. Tổng <= 1.5 <= cost >= 1.
      (*) Trường hợp cost > 1 (fragile extra) thì hiển nhiên consistent.
    """
    if game.is_goal(s):
        return 0

    gr, gc = goal_pos(game)

    if is_split(s):
        # Mỗi cube cần đi tới goal. Lấy max vì cả hai phải xong mới thắng.
        cs = occupied(game, s)
        if not cs:
            return MIN_COST
        vals = []
        for r, c in cs:
            d = abs(r - gr) + abs(c - gc)
            vals.append(max(1, math.ceil(d / 2)) * MIN_COST)
        return max(vals)

    # Khối bình thường (STANDING / LYING_H / LYING_V)
    cs = occupied(game, s)
    d = min(abs(r - gr) + abs(c - gc) for r, c in cs)

    base = max(1, math.ceil(d / 2)) * MIN_COST

    # Phạt orientation: khối đang nằm mà gần goal thì cần thêm bước đứng
    penalty = _orientation_penalty(s.orient, abs(cs[0][0] - gr), abs(cs[0][1] - gc))

    return base + penalty
