"""Chạy benchmark. Từ thư mục Source:  python -m benchmark.run_all"""
import csv, importlib, os, statistics, sys
from pathlib import Path

# Đảm bảo import được module solvers dù chạy từ bất kỳ thư mục nào
SOURCE_DIR = Path(__file__).resolve().parents[1]
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from solvers.metrics import run_solver
from solvers.costs import path_cost
from solvers.loader import load_game

# Fix encoding cho Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPEATS = 5                                      # lặp để lấy trung vị thời gian
GROUPS = {
    "1-Đơn giản":      ["L01", "L02", "L03", "L04"],
    "2-Fragile":        ["L05", "L06", "L07", "L08"],
    "3-Switch & Cầu":   ["L09", "L10", "L11", "L12"],
    "4-Kết hợp":        ["L13", "L14", "L15", "L16"],
}
SOLVERS = {"BFS": ("solvers.bfs", "bfs"), "IDS": ("solvers.ids", "ids"), "DFS": ("solvers.dfs", "dfs"),
           "UCS": ("solvers.ucs", "ucs"), "A*": ("solvers.astar", "astar")}

def get_solvers():
    found = {}
    for name, (mod, fn) in SOLVERS.items():
        try:
            found[name] = getattr(importlib.import_module(mod), fn)
        except (ImportError, AttributeError):
            print(f"[bỏ qua] không tìm thấy {mod}.{fn}")
    return found

DEFAULT_OUT = Path(__file__).resolve().parent / "results.csv"

def main(out=DEFAULT_OUT):
    solvers = get_solvers()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["group", "level", "algo", "time_s", "peak_memory_bytes", "expanded", "length", "cost"])
        for group, levels in GROUPS.items():
            for lid in levels:
                game = load_game(lid)
                for name, fn in solvers.items():
                    times, r = [], None
                    for _ in range(REPEATS):
                        r = run_solver(fn, game)
                        times.append(r["time"])
                    moves = r["moves"]
                    cost = path_cost(game, moves) if moves is not None else ""
                    w.writerow([group, lid, name, statistics.median(times), r["peak_memory"],
                                r["expanded"], r["length"] if moves is not None else "", cost])
                    print(group, lid, name, "xong")
    print("Đã ghi", out)
 
 
if __name__ == "__main__":
    main()
