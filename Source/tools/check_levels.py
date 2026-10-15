from collections import deque
from pathlib import Path

from game.game import Game
from game.level_loader import load_level


def bfs(game: Game):
    start = game.initial_state()
    parent = {start: None}
    queue = deque([start])
    while queue:
        s = queue.popleft()
        if game.is_goal(s):
            path = []
            while parent[s] is not None:
                s, a = parent[s]
                path.append(a)
            return "".join(reversed(path))
        for a in game.actions(s):
            s2 = game.result(s, a)
            if s2 not in parent:
                parent[s2] = (s, a)
                queue.append(s2)
    return None


if __name__ == "__main__":
    ok = True
    for p in sorted(Path("levels").glob("*.json")):
        g = Game(load_level(p))
        sol = bfs(g)
        print(f"{p.name}: {'GIẢI ĐƯỢC, ' + str(len(sol)) + ' nước: ' + sol if sol is not None else 'KHÔNG CÓ LỜI GIẢI'}")
        ok &= sol is not None
    raise SystemExit(0 if ok else 1)