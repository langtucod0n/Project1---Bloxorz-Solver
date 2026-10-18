import json
from pathlib import Path


class LevelError(ValueError):
    """Màn chơi không hợp lệ."""


def validate_level(level: dict) -> dict:
    for key in ("grid", "start", "legend"):
        if key not in level:
            raise LevelError(f"Thiếu khóa bắt buộc: '{key}'")

    grid, legend = level["grid"], level["legend"]
    if not isinstance(grid, list) or not grid or not all(isinstance(row, str) for row in grid):
        raise LevelError("'grid' phải là danh sách chuỗi, không rỗng")

    width = len(grid[0])
    if width == 0 or any(len(row) != width for row in grid):
        raise LevelError("'grid' phải là hình chữ nhật (mọi hàng cùng độ dài)")

    goals = 0
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch not in legend:
                raise LevelError(f"Ký tự lạ {ch!r} tại hàng {r}, cột {c}")
            if legend[ch] == "goal":
                goals += 1
    if goals != 1:
        raise LevelError(f"Cần đúng 1 ô goal, tìm thấy {goals}")

    start = level["start"]
    if (not isinstance(start, (list, tuple)) or len(start) != 2
            or not all(isinstance(x, int) for x in start)):
        raise LevelError("'start' phải có dạng [hàng, cột]")
    sr, sc = start
    if not (0 <= sr < len(grid) and 0 <= sc < width):
        raise LevelError(f"'start' {start} nằm ngoài bàn")
    if legend[grid[sr][sc]] in ("void", "fragile"):
        raise LevelError(f"'start' {start} không được là void hoặc fragile")

    _validate_bridges_switches(level)
    return level  # khóa lạ khác được giữ nguyên, không báo lỗi


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _check_cell(cell, where: str, rows: int, cols: int) -> tuple[int, int]:
    if (not isinstance(cell, (list, tuple)) or len(cell) != 2
            or not all(_is_int(x) for x in cell)):
        raise LevelError(f"{where}: ô phải có dạng [hàng, cột]")
    r, c = cell
    if not (0 <= r < rows and 0 <= c < cols):
        raise LevelError(f"{where}: ô {list(cell)} nằm ngoài bàn")
    return r, c


def _validate_bridges_switches(level: dict) -> None:
    #Kiểm tra chặt 'bridges' và 'switches' (cả hai tùy chọn; thiếu hoặc [] đều hợp lệ).
    grid, legend = level["grid"], level["legend"]
    rows, cols = len(grid), len(grid[0])
    kind = lambda r, c: legend[grid[r][c]]

    bridges = level.get("bridges", [])
    if not isinstance(bridges, list):
        raise LevelError("'bridges' phải là danh sách")
    bridge_cells: dict[tuple[int, int], int] = {}
    for i, b in enumerate(bridges):
        where = f"bridges[{i}]"
        if not isinstance(b, dict):
            raise LevelError(f"{where}: phải là đối tượng")
        if b.get("id") != i or not _is_int(b.get("id")):
            raise LevelError(f"{where}: 'id' phải là số nguyên, duy nhất và liên tục 0..n-1 (mong đợi {i}, nhận {b.get('id')!r})")
        if not isinstance(b.get("open"), bool):
            raise LevelError(f"{where}: 'open' bắt buộc là bool")
        cs = b.get("cells")
        if not isinstance(cs, list) or not cs:
            raise LevelError(f"{where}: 'cells' phải là danh sách không rỗng")
        for j, cell in enumerate(cs):
            r, c = _check_cell(cell, f"{where}.cells[{j}]", rows, cols)
            if kind(r, c) not in ("floor", "void"):
                raise LevelError(f"{where}.cells[{j}]: ô {[r, c]} trên grid phải là floor hoặc void, không phải {kind(r, c)}")
            if (r, c) in bridge_cells:
                raise LevelError(f"{where}.cells[{j}]: ô {[r, c]} đã thuộc cầu {bridge_cells[(r, c)]}")
            bridge_cells[(r, c)] = i

    sr, sc = level["start"]
    if (sr, sc) in bridge_cells and not bridges[bridge_cells[(sr, sc)]]["open"]:
        raise LevelError(f"'start' {[sr, sc]} nằm trên ô của cầu {bridge_cells[(sr, sc)]} đang đóng")

    switches = level.get("switches", [])
    if not isinstance(switches, list):
        raise LevelError("'switches' phải là danh sách")
    seen: set[tuple[int, int]] = set()
    for i, sw in enumerate(switches):
        where = f"switches[{i}]"
        if not isinstance(sw, dict):
            raise LevelError(f"{where}: phải là đối tượng")
        r, c = _check_cell(sw.get("cell"), f"{where}.cell", rows, cols)
        if kind(r, c) != "floor":
            raise LevelError(f"{where}: ô công tắc {[r, c]} trên grid phải là floor, không phải {kind(r, c)}")
        if (r, c) in bridge_cells:
            raise LevelError(f"{where}: ô công tắc {[r, c]} trùng ô của cầu {bridge_cells[(r, c)]}")
        if (r, c) in seen:
            raise LevelError(f"{where}: ô công tắc {[r, c]} trùng công tắc khác")
        seen.add((r, c))

        t = sw.get("type")
        if t in ("soft", "heavy"):
            if sw.get("mode") not in ("toggle", "open", "close", "permanent"):
                raise LevelError(f"{where}: 'mode' lạ {sw.get('mode')!r}")
            if "state" in sw and not isinstance(sw["state"], bool):
                raise LevelError(f"{where}: 'state' phải là bool")
            tg = sw.get("targets")
            if not isinstance(tg, list) or not tg:
                raise LevelError(f"{where}: 'targets' phải là danh sách không rỗng")
            for t_id in tg:
                if not _is_int(t_id) or not 0 <= t_id < len(bridges):
                    raise LevelError(f"{where}: 'targets' trỏ tới cầu không tồn tại: {t_id!r}")
        elif t == "split":
            st = sw.get("split_to")
            if not isinstance(st, list) or len(st) != 2:
                raise LevelError(f"{where}: 'split_to' phải gồm đúng 2 ô")
            pts = [_check_cell(p, f"{where}.split_to[{j}]", rows, cols) for j, p in enumerate(st)]
            if pts[0] == pts[1]:
                raise LevelError(f"{where}: 'split_to' phải gồm hai ô khác nhau")
            for p in pts:
                if kind(*p) != "floor":
                    raise LevelError(f"{where}: ô split_to {list(p)} trên grid phải là floor, không phải {kind(*p)}")
                if p in bridge_cells:
                    raise LevelError(f"{where}: ô split_to {list(p)} trùng ô của cầu {bridge_cells[p]}")
            if abs(pts[0][0] - pts[1][0]) + abs(pts[0][1] - pts[1][1]) <= 1:
                raise LevelError(f"{where}: 'split_to' không được trùng hoặc kề nhau")
        else:
            raise LevelError(f"{where}: 'type' lạ {t!r}")


def load_level(path) -> dict:
    with open(Path(path), encoding="utf-8") as f:
        return validate_level(json.load(f))