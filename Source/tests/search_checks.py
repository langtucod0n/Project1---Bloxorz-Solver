"""Các phép kiểm tra dùng chung cho game giả và game thật."""
from collections import deque
from solvers.ucs import ucs
from solvers.astar import astar
from solvers.costs import weighted, path_cost
from solvers.heuristics import h_manhattan_half as h

def reachable(game):
    s0 = game.initial_state()
    seen, q = {s0}, deque([s0])
    while q:
        s = q.popleft()
        for a in game.actions(s):
            s2 = game.result(s, a)
            if s2 not in seen:
                seen.add(s2)
                q.append(s2)

    return seen

def check_same_cost_and_valid_path(game):
    u = ucs(game)
    a = astar(game)
    assert u["moves"] is not None and a["moves"] is not None
    
    cu = path_cost(game, u["moves"])
    ca = path_cost(game, a["moves"])
    assert cu == ca, (cu, ca)

    s = game.initial_state()
    for m in a["moves"]:
        s = game.result(s, m)
    assert game.is_goal(s)

    return cu, u["expanded"], a["expanded"]

def check_heuristic(game):
    g = weighted(game)
    for s in reachable(game):
        r = ucs(game, start=s)
        if r["moves"] is not None:
            assert h(g, s) <= path_cost(game, r["moves"], start=s), s

        for m in g.actions(s):
            s2 = g.result(s, m)
            assert h(g, s) <= g.cost(s, m, s2) + h(g, s2), (s, m)
    