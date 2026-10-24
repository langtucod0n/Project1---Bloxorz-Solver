import heapq
import itertools

from solvers.costs import weighted
from solvers.heuristics import h_manhattan_half
from solvers.ucs import _build_path

def astar(game, h=h_manhattan_half, start=None):
    """Trả về {"moves": [...] hoặc None, "expanded": số}."""
    game = weighted(game)
    start = game.initial_state() if start is None else start
    tie = itertools.count()
    h0 = h(game, start)
    frontier = [(h0, h0, next(tie), 0, start)]      # (f, h, tie, g, state)
    best_g = {start: 0}
    parent = {start: None}
    expanded = 0

    while frontier:
        _, _, _, g, s = heapq.heappop(frontier)
        if g > best_g[s]:
            continue
        
        expanded += 1
        if game.is_goal(s):
            return {"moves": _build_path(parent, s), "expanded": expanded}
        
        for a in game.actions(s):
            s2 = game.result(s, a)
            g2 = g + game.cost(s, a, s2)
            if g2 < best_g.get(s2, float("inf")):
                best_g[s2] = g2
                parent[s2] = (s, a)
                h2 = h(game, s2)
                heapq.heappush(frontier, (g2 + h2, h2, next(tie), g2, s2))

    return {"moves": None, "expanded": expanded}