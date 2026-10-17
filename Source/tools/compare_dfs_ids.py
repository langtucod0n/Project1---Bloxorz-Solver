"""So sánh DFS và IDS trên các màn có sẵn: python -m tools.compare_dfs_ids"""
import statistics
import sys
from pathlib import Path

from game.game import Game
from game.level_loader import load_level
from solvers.dfs import dfs
from solvers.ids import ids
from solvers.metrics import run_solver

SOLVERS = {"DFS": dfs, "IDS": ids}
REPEATS = 20  # số lần chạy để lấy trung vị (mỗi lần chỉ vài phần nghìn giây)
WARMUP = 5    # những lần chạy đầu bị nhiễu (bộ nhớ đệm của Python) nên bỏ đi
LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels"


def measure(solver, game):
    runs = [run_solver(solver, game) for _ in range(REPEATS)][WARMUP:]
    res = dict(runs[0])
    res["time"] = statistics.median(r["time"] for r in runs)
    res["peak_memory"] = int(statistics.median(r["peak_memory"] for r in runs))
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # console Windows không in được tiếng Việt
    for path in sorted(LEVELS_DIR.glob("*.json")):
        game = Game(load_level(path))
        print(f"\n## {path.stem}")
        print("| Thuật toán | Số nước | Trạng thái xem xét | Bộ nhớ đỉnh (byte) | Thời gian (ms) | Lời giải |")
        print("|---|---|---|---|---|---|")
        for name, solver in SOLVERS.items():
            r = measure(solver, game)
            print(f"| {name} | {r['length']} | {r['expanded']} | {r['peak_memory']} | "
                  f"{r['time'] * 1000:.3f} | {''.join(r['moves'])} |")


if __name__ == "__main__":
    main()
