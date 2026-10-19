from collections import deque

from game.game import Game


def bfs(game: Game) -> dict:
    """Tìm kiếm theo chiều rộng. Lời giải ngắn nhất theo số nước đi.

    Trả về {"moves": list[str] | None, "expanded": int}.
    moves là None nếu màn không có lời giải.
    """
    start = game.initial_state()
    parent = {start: None}  # đồng thời là tập visited
    queue = deque([start])
    expanded = 0

    while queue:
        s = queue.popleft()
        expanded += 1
        if game.is_goal(s):
            moves = []
            while parent[s] is not None:
                s, a = parent[s]
                moves.append(a)
            moves.reverse()
            return {"moves": moves, "expanded": expanded}
        for a in game.actions(s):
            s2 = game.result(s, a)
            if s2 not in parent:
                parent[s2] = (s, a)
                queue.append(s2)

    return {"moves": None, "expanded": expanded}
