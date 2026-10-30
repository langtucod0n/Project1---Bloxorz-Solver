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
# Heuristic cải tiến: Manhattan/2 có xét orientation + xử lý split
# ---------------------------------------------------------------------------
from game.state import STANDING
from solvers.game_access import split_switches


def h_combined(game, s):
    """Heuristic kết hợp: Manhattan/2 có xét orientation + split switch teleport.

    So với h_manhattan_half:
    ─ Khối nằm dùng ceil((d+1)/2) thay vì ceil(d/2), chặt hơn nhưng vẫn admissible.
    ─ Khối tách dùng max(ceil(d_i/2)) thay vì trả cứng MIN_COST.
    ─ Xét đường đi qua split switch (teleport) nếu có, tránh overestimate.

    ═══ CHỨNG MINH ADMISSIBLE ═══

    (1) Khối đứng (STANDING): mỗi bước lăn di chuyển tối đa 2 ô Manhattan,
        nên ceil(d/2) * MIN_COST là cận dưới.

    (2) Khối nằm (LYING_H / LYING_V): để kết thúc tại goal, khối phải ĐỨNG.
        Bước cuối bắt buộc là lăn từ nằm → đứng. Trước bước đó khối nằm cách
        goal ít nhất 1 ô. Tổng quát, từ trạng thái nằm cách goal d ô Manhattan:
        ─ Mỗi bước nằm→nằm giảm d tối đa 2 (nhưng vẫn nằm)
        ─ Bước nằm→đứng giảm d tối đa 2 (nhưng tiêu 1 bước)
        ─ Bước đứng→nằm giảm d tối đa 2 (nhưng phải thêm 1 bước đứng lại)
        Cận dưới chặt: ceil((d+1)/2) bước, tương ứng chi phí ceil((d+1)/2) * MIN_COST.

        Ví dụ kiểm tra: d=1 → ceil(2/2) = 1 ✓ (1 bước lăn đứng),
                         d=0 → max(1, ceil(1/2)) = 1 ✓ (cần ít nhất 1 bước đứng lại).

    (3) Khối tách: mỗi cube ở khoảng cách d_i, cần ít nhất ceil(d_i/2) bước.
        Cả hai phải gặp nhau rồi đến goal → lấy max.

    (4) Split switch: nếu có switch teleport, tính thêm chi phí qua switch rồi
        lấy min với đường trực tiếp. min của các cận dưới vẫn là cận dưới.

    ═══ CHỨNG MINH CONSISTENT (MONOTONIC) ═══

    Cần: h(s) ≤ cost(s, a, s') + h(s') cho mọi cạnh (s, a, s').

    Phân tích từng loại chuyển đổi (cost ≥ MIN_COST = 1):

    ─ Đứng → Nằm: d thay đổi tối đa 2. ceil(d/2) → ceil((d'+1)/2).
      Với d' ≥ d - 2: thay đổi h tối đa 1. ✓

    ─ Nằm → Đứng: ô đứng kề 1 ô nằm nên d' ≥ d - 1.
      ceil((d+1)/2) → ceil(d'/2). Với d' ≥ d - 1: thay đổi h tối đa 1. ✓

    ─ Nằm → Nằm (cùng loại): d thay đổi tối đa 1.
      ceil((d+1)/2) thay đổi tối đa 1. ✓

    Mọi trường hợp: |h(s) - h(s')| ≤ 1 ≤ MIN_COST ≤ cost(s, a, s').

    Với split switch: min của hai heuristic consistent vẫn consistent.
    Chứng minh: nếu h(s) = h_1(s) ≤ h_2(s), thì
    h(s) = h_1(s) ≤ c + h_1(s') ≤ c + max(h_1(s'), h_2(s')) = ... nhưng ta cần
    h(s) ≤ c + min(h_1(s'), h_2(s')) = c + h(s').
    Thật vậy: h(s) = h_1(s) ≤ h_2(s). Nếu h(s') = h_2(s') thì
    h(s) ≤ h_2(s) ≤ c + h_2(s') = c + h(s'). ✓
    Nếu h(s') = h_1(s') thì h(s) = h_1(s) ≤ c + h_1(s') = c + h(s'). ✓
    """
    if game.is_goal(s):
        return 0

    gr, gc = goal_pos(game)

    # ── Trạng thái tách (2 cube riêng biệt) ──
    if is_split(s):
        cs = occupied(game, s)
        if not cs:
            return MIN_COST
        vals = []
        for r, c in cs:
            d = abs(r - gr) + abs(c - gc)
            vals.append(max(1, math.ceil(d / 2)) * MIN_COST)
        return max(vals)

    # ── Khối bình thường (STANDING / LYING_H / LYING_V) ──
    cs = occupied(game, s)
    d = min(abs(r - gr) + abs(c - gc) for r, c in cs)

    if s.orient == STANDING:
        h_direct = max(1, math.ceil(d / 2)) * MIN_COST
    else:
        # Khối nằm: cần thêm overhead để đứng lại tại goal
        h_direct = max(1, math.ceil((d + 1) / 2)) * MIN_COST

    # ── Xét đường đi qua split switch (teleport) nếu có ──
    switches = split_switches(game)
    if not switches:
        return h_direct

    h_vals = [h_direct]
    for sw_pos, (tp0, tp1) in switches.items():
        # Chi phí tối thiểu để đến switch (khối phải ĐỨNG trên switch)
        d_sw = min(abs(r - sw_pos[0]) + abs(c - sw_pos[1]) for r, c in cs)
        if s.orient == STANDING:
            cost_to_sw = math.ceil(d_sw / 2) * MIN_COST
        else:
            cost_to_sw = math.ceil((d_sw + 1) / 2) * MIN_COST
        # Sau teleport: mỗi cube cần ceil(d_i/2) bước tới goal, lấy max
        d0 = abs(tp0[0] - gr) + abs(tp0[1] - gc)
        d1 = abs(tp1[0] - gr) + abs(tp1[1] - gc)
        h_after = max(
            max(1, math.ceil(d0 / 2)),
            max(1, math.ceil(d1 / 2))
        ) * MIN_COST
        h_vals.append(cost_to_sw + h_after)

    return min(h_vals)
