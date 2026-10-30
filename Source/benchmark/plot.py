"""Vẽ biểu đồ từ results.csv. Từ thư mục Source:  python -m benchmark.plot"""
import csv, os, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Fix encoding cho Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

SOURCE_DIR = Path(__file__).resolve().parents[1]
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

DEFAULT_SRC = Path(__file__).resolve().parent / "results.csv"
DEFAULT_OUTDIR = SOURCE_DIR / "docs" / "figures"

METRICS = {"time_s": "Thời gian (giây)", "peak_memory_bytes": "Bộ nhớ đỉnh (byte)",
           "expanded": "Số node mở rộng", "length": "Độ dài lời giải (số nước)", "cost": "Tổng chi phí"}

def main(src=DEFAULT_SRC, outdir=DEFAULT_OUTDIR):
    os.makedirs(outdir, exist_ok=True)
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    levels = list(dict.fromkeys(r["level"] for r in rows))
    algos = list(dict.fromkeys(r["algo"] for r in rows))
    for key, title in METRICS.items():
        fig, ax = plt.subplots(figsize=(10, 5))
        width = 0.8 / len(algos)
        for i, a in enumerate(algos):
            ys = []
            for lv in levels:
                v = next((r[key] for r in rows if r["level"] == lv and r["algo"] == a), "")
                ys.append(float(v) if v not in ("", None) else 0)
            ax.bar([x + i * width for x in range(len(levels))], ys, width, label=a)
        ax.set_xticks([x + 0.4 - width / 2 for x in range(len(levels))])
        ax.set_xticklabels(levels, rotation=45, ha="right")
        ax.set_ylabel(title); ax.set_title(title); ax.legend()
        fig.tight_layout(); fig.savefig(f"{outdir}/{key}.png", dpi=200); plt.close(fig)
    print("Đã vẽ vào", outdir)

if __name__ == "__main__":
    main()
