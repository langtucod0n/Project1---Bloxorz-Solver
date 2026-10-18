import heapq
import itertools
from solvers.costs import weighted

def _build_path(parent, s):
    moves = []
    while parent[s] is not None:
        s, a = parent[s]
        moves.append(a)
    
    moves.reverse()
    return moves

def ucs(game, start=None):
    """Trả về {"moves": [...] hoặc None, "expanded": số},
    đúng hợp đồng của solvers/registry.py."""
    game = weighted(game)
    start = game.initial_state() if start is None else start
    tie = itertools.count()     # phá hòa, để heap không so sánh State

    frontier = [(0, next(tie), start)]  # (g, tie, state)
    best_g = {start: 0}
    parent = {start: None}
    expanded = 0

    while frontier:
        g, _, s = heapq.heappop(frontier)
        if g > best_g[s]:
            continue    # bản cũ, đã có đường rẻ hơn
        
        expanded += 1
        if game.is_goal(s):
            return {"moves": _build_path(parent, s), "expanded": expanded}

        for a in game.actions(s):
            s2 = game.result(s, a)
            g2 = g + game.cost(s, a, s2)
            if g2 < best_g.get(s2, float("inf")):
                best_g[s2] = g2
                parent[s2] = (s, a)
                heapq.heappush(frontier, (g2, next(tie), s2))

    return {"moves": None, "expanded": expanded}



