from game.game import Game


def ids(game: Game, max_limit: int = 200) -> dict:
    """Iterative deepening: chạy DFS giới hạn độ sâu 0, 1, 2, ... đến khi thấy đích.

    Lời giải ngắn nhất như BFS nhưng tốn ít bộ nhớ hơn. Mỗi vòng chỉ giữ độ sâu nhỏ nhất đã
    tới được của từng trạng thái, nên không đi lại một trạng thái bằng đường dài hơn.

    Trả về {"moves": list[str] | None, "expanded": int}. expanded cộng dồn qua mọi vòng.
    """
    start = game.initial_state()
    expanded = 0

    for limit in range(max_limit + 1):
        best = {start: 0}  # độ sâu nhỏ nhất đã tới trạng thái này trong vòng hiện tại
        path = {start: None}
        stack = [start]
        cut = False  # có nhánh bị cắt vì chạm giới hạn không
        while stack:
            s = stack.pop()
            expanded += 1
            if game.is_goal(s):
                moves = []
                while path[s] is not None:
                    s, a = path[s]
                    moves.append(a)
                moves.reverse()
                return {"moves": moves, "expanded": expanded}
            d = best[s]
            if d >= limit:
                cut = True
                continue
            for a in reversed(game.actions(s)):
                s2 = game.result(s, a)
                if best.get(s2, limit + 1) > d + 1:
                    best[s2] = d + 1
                    path[s2] = (s, a)
                    stack.append(s2)
        if not cut:  # đã duyệt hết mà không bị cắt: không có lời giải
            break

    return {"moves": None, "expanded": expanded}
