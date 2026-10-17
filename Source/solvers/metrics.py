import time
import tracemalloc
from typing import Callable

from game.game import Game

# Mọi solver có dạng solver(game) -> {"moves": list[str] | None, "expanded": int}.
# run_solver bọc solver và trả về cấu trúc kết quả thống nhất:
#   {"moves", "expanded", "time", "peak_memory", "length"}
#   moves        : danh sách nước đi, None nếu không có lời giải
#   expanded     : số node được lấy ra mở rộng
#   time         : thời gian tìm kiếm (giây)
#   peak_memory  : bộ nhớ đỉnh (byte) theo tracemalloc
#   length       : số nước đi của lời giải, None nếu không có lời giải
Solver = Callable[[Game], dict]


def run_solver(solver: Solver, game: Game) -> dict:
    # tracemalloc làm chậm chương trình đáng kể nên đo thời gian và bộ nhớ ở hai lần chạy riêng.
    t0 = time.perf_counter()
    result = solver(game)
    elapsed = time.perf_counter() - t0

    tracemalloc.start()
    try:
        solver(game)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    moves = result["moves"]
    return {
        "moves": moves,
        "expanded": result["expanded"],
        "time": elapsed,
        "peak_memory": peak,
        "length": None if moves is None else len(moves),
    }
