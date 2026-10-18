"""Vẽ biểu đồ từ results.csv. Từ thư mục Source:  python -m benchmark.plot"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS = {"time_s": "Thời gian (giây)", "peak_memory_bytes": "Bộ nhớ đỉnh (byte)",
           "expanded": "Số node mở rộng", "length": "Độ dài lời giải (số nước)", "cost": "Tổng chi phí"}

def main(src="benchmark/results.csv", outdir="docs/figures"):
    os.makedirs(outdir, exist_ok=True)
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    levels = list(dict.fromkeys(r["level"] for r in rows))
    algos = list(dict.fromkeys(r["algo"] for r in rows))
    for key, title in METRICS.items():
        fig, ax = plt.subplots(figsize=(8,4))
        width = 0.8 / len(algos)
        for i, a in enumerate(algos):
            ys = []
            for lv in levels:
                v = next((r[key] for r in rows if r["level"] == lv and r["algo"] == a), "")
                ys.append(float(v) if v not in ("", None) else 0)
            ax.bar([x + i * width for x in range(len(levels))], ys, width, label=a)
        ax.set_xticks([x + 0.4 - width / 2 for x in range(len(levels))])
        ax.set_xticklabels(levels)
        ax.set_ylabel(title); ax.set_title(title); ax.legend()
        fig.tight_layout(); fig.savefig(f"{outdir}/{key}.png", dpi=200); plt.close(fig)
    print("Đã vẽ vào", outdir)

if __name__ == "__main__":
    main()