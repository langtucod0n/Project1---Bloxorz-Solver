"""Unit tests cho UCS, A* và heuristic (TV1).

Chạy: cd Source && pytest tests/test_solvers.py -v
"""
import pytest
from solvers.loader import load_game
from solvers.bfs import bfs
from solvers.ucs import ucs
from solvers.astar import astar
from solvers.costs import path_cost, weighted
from solvers.heuristics import h_manhattan_half, h_combined


# ─── helpers ───────────────────────────────────────────────────────────────────

def replay(game, moves):
    """Phát lại chuỗi nước đi, trả về trạng thái cuối."""
    s = game.initial_state()
    for m in moves:
        s = game.result(s, m)
    return s


ALL_LEVELS = [f"L{i:02d}" for i in range(1, 17)]
SIMPLE_LEVELS = [f"L{i:02d}" for i in range(1, 5)]
FRAGILE_LEVELS = [f"L{i:02d}" for i in range(5, 9)]
SWITCH_LEVELS = [f"L{i:02d}" for i in range(9, 13)]
COMBINED_LEVELS = [f"L{i:02d}" for i in range(13, 17)]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. UCS tìm được lời giải
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_ucs_finds_solution(lid):
    game = load_game(lid)
    result = ucs(game)
    assert result["moves"] is not None, f"UCS không tìm được lời giải cho {lid}"
    assert result["expanded"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 2. A* tìm được lời giải
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_astar_finds_solution(lid):
    game = load_game(lid)
    result = astar(game)
    assert result["moves"] is not None, f"A* không tìm được lời giải cho {lid}"
    assert result["expanded"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 3. A* với h_combined tìm được lời giải
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_astar_combined_finds_solution(lid):
    game = load_game(lid)
    result = astar(game, h=h_combined)
    assert result["moves"] is not None, f"A*(h_combined) không tìm được lời giải cho {lid}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Chi phí UCS == chi phí A* (cả hai đều tối ưu)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_ucs_astar_same_cost(lid):
    game = load_game(lid)
    r_ucs = ucs(game)
    r_astar = astar(game)
    assert r_ucs["moves"] is not None and r_astar["moves"] is not None

    c_ucs = path_cost(game, r_ucs["moves"])
    c_astar = path_cost(game, r_astar["moves"])
    assert c_ucs == c_astar, (
        f"{lid}: chi phí UCS ({c_ucs}) != chi phí A* ({c_astar})"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Chi phí A*(h_combined) == chi phí UCS (h_combined cũng tối ưu)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_astar_combined_same_cost_as_ucs(lid):
    game = load_game(lid)
    r_ucs = ucs(game)
    r_astar = astar(game, h=h_combined)
    assert r_ucs["moves"] is not None and r_astar["moves"] is not None

    c_ucs = path_cost(game, r_ucs["moves"])
    c_astar = path_cost(game, r_astar["moves"])
    assert c_ucs == c_astar, (
        f"{lid}: chi phí UCS ({c_ucs}) != chi phí A*(h_combined) ({c_astar})"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. A* mở ít hoặc bằng node so với UCS (trên các màn đơn giản)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", SIMPLE_LEVELS + FRAGILE_LEVELS)
def test_astar_expands_leq_ucs(lid):
    game = load_game(lid)
    r_ucs = ucs(game)
    r_astar = astar(game)
    assert r_astar["expanded"] <= r_ucs["expanded"], (
        f"{lid}: A* mở {r_astar['expanded']} > UCS mở {r_ucs['expanded']} node"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Trên màn không fragile, UCS cost == BFS length (chi phí đều = 1)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", SIMPLE_LEVELS)
def test_ucs_matches_bfs_on_uniform_cost(lid):
    game = load_game(lid)
    r_bfs = bfs(game)
    r_ucs = ucs(game)
    assert r_bfs["moves"] is not None and r_ucs["moves"] is not None

    bfs_len = len(r_bfs["moves"])
    ucs_cost = path_cost(game, r_ucs["moves"])
    # Trên màn đơn giản (không fragile), WeightedGame cost = 1 cho mọi bước,
    # nên tổng cost = số bước. UCS tối ưu cost ↔ BFS tối ưu số bước.
    assert ucs_cost == bfs_len, (
        f"{lid}: UCS cost ({ucs_cost}) != BFS length ({bfs_len})"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Lời giải thực sự dẫn đến goal
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_ucs_solution_reaches_goal(lid):
    game = load_game(lid)
    result = ucs(game)
    assert result["moves"] is not None
    final = replay(game, result["moves"])
    assert game.is_goal(final), f"{lid}: UCS moves không dẫn đến goal"


@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_astar_solution_reaches_goal(lid):
    game = load_game(lid)
    result = astar(game)
    assert result["moves"] is not None
    final = replay(game, result["moves"])
    assert game.is_goal(final), f"{lid}: A* moves không dẫn đến goal"


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Test riêng cho nhóm Fragile (L05-L08)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", FRAGILE_LEVELS)
def test_fragile_levels(lid):
    game = load_game(lid)
    r_ucs = ucs(game)
    r_astar = astar(game)
    assert r_ucs["moves"] is not None, f"UCS thất bại trên fragile level {lid}"
    assert r_astar["moves"] is not None, f"A* thất bại trên fragile level {lid}"
    # Chi phí phải bằng nhau
    assert path_cost(game, r_ucs["moves"]) == path_cost(game, r_astar["moves"])


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Test riêng cho nhóm Switch & Cầu (L09-L12)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", SWITCH_LEVELS)
def test_switch_levels(lid):
    game = load_game(lid)
    r_ucs = ucs(game)
    r_astar = astar(game)
    assert r_ucs["moves"] is not None, f"UCS thất bại trên switch level {lid}"
    assert r_astar["moves"] is not None, f"A* thất bại trên switch level {lid}"
    assert path_cost(game, r_ucs["moves"]) == path_cost(game, r_astar["moves"])


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Test riêng cho nhóm Kết hợp (L13-L16)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", COMBINED_LEVELS)
def test_combined_levels(lid):
    game = load_game(lid)
    r_ucs = ucs(game)
    r_astar = astar(game)
    assert r_ucs["moves"] is not None, f"UCS thất bại trên combined level {lid}"
    assert r_astar["moves"] is not None, f"A* thất bại trên combined level {lid}"
    assert path_cost(game, r_ucs["moves"]) == path_cost(game, r_astar["moves"])


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Heuristic admissible: h(start) <= chi phí tối ưu thực tế
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", SIMPLE_LEVELS + FRAGILE_LEVELS)
def test_heuristic_admissible_manhattan(lid):
    game = load_game(lid)
    g = weighted(game)
    s0 = g.initial_state()
    h_val = h_manhattan_half(g, s0)
    # Chi phí tối ưu thực tế (từ UCS)
    r = ucs(game)
    assert r["moves"] is not None
    opt_cost = path_cost(game, r["moves"])
    assert h_val <= opt_cost, (
        f"{lid}: h_manhattan_half(start)={h_val} > optimal cost={opt_cost} → NOT admissible!"
    )


@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_heuristic_admissible_combined(lid):
    game = load_game(lid)
    g = weighted(game)
    s0 = g.initial_state()
    h_val = h_combined(g, s0)
    r = ucs(game)
    assert r["moves"] is not None
    opt_cost = path_cost(game, r["moves"])
    assert h_val <= opt_cost, (
        f"{lid}: h_combined(start)={h_val} > optimal cost={opt_cost} → NOT admissible!"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 13. h_combined >= h_manhattan_half (heuristic mới chặt hơn hoặc bằng)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("lid", ALL_LEVELS)
def test_combined_geq_manhattan(lid):
    game = load_game(lid)
    g = weighted(game)
    s0 = g.initial_state()
    h1 = h_manhattan_half(g, s0)
    h2 = h_combined(g, s0)
    assert h2 >= h1, (
        f"{lid}: h_combined(start)={h2} < h_manhattan_half(start)={h1}"
    )
