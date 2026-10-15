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

    return level  # khóa lạ (switches, bridges, ...) được giữ nguyên, không báo lỗi


def load_level(path) -> dict:
    with open(Path(path), encoding="utf-8") as f:
        return validate_level(json.load(f))