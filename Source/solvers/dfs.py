from game.game import Game


def dfs(game: Game, max_depth: int | None = None) -> dict:
    """Tìm kiếm theo chiều sâu, dùng stack tự tạo (không đệ quy) và tập visited.

    Lời giải tìm được thường dài và không tối ưu. max_depth=None nghĩa là không giới hạn
    độ sâu (visited đã đảm bảo không lặp vô hạn).

    Trả về {"moves": list[str] | None, "expanded": int}.
    """
    start = game.initial_state()
    parent = {start: None}  # đồng thời là tập visited
    depth = {start: 0}
    stack = [start]
    expanded = 0

    while stack:
        s = stack.pop()
        expanded += 1
        if game.is_goal(s):
            moves = []
            while parent[s] is not None:
                s, a = parent[s]
                moves.append(a)
            moves.reverse()
            return {"moves": moves, "expanded": expanded}
        if max_depth is not None and depth[s] >= max_depth:
            continue
        # Đẩy ngược để nước đầu tiên theo thứ tự U, D, L, R được thử trước.
        for a in reversed(game.actions(s)):
            s2 = game.result(s, a)
            if s2 not in parent:
                parent[s2] = (s, a)
                depth[s2] = depth[s] + 1
                stack.append(s2)

    return {"moves": None, "expanded": expanded}
