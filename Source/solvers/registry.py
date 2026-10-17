"""Bảng tên thuật toán -> solver. None nghĩa là chưa được cài đặt."""
from importlib import import_module

from solvers.bfs import bfs
from solvers.dfs import dfs


def _optional(module: str, name: str):
    # UCS và A* do TV1 làm; chưa có file thì để None, API trả 501.
    try:
        return getattr(import_module(module), name)
    except (ImportError, AttributeError):
        return None


ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": _optional("solvers.ucs", "ucs"),
    "astar": _optional("solvers.astar", "astar"),
}
