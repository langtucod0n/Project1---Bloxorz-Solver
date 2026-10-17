from pathlib import Path

import pytest

from game.game import Game
from game.level_loader import load_level
from solvers.bfs import bfs
from solvers.dfs import dfs
from solvers.metrics import run_solver

LEVELS = sorted((Path(__file__).resolve().parent.parent / "levels").glob("*.json"))
LEGEND = {".": "floor", "#": "void", "G": "goal", "F": "fragile"}


def make_game(grid, start=(0, 0)):
    return Game({"version": 1, "id": "T", "grid": grid, "start": list(start), "legend": LEGEND})


def replay(game, moves):
    s = game.initial_state()
    for a in moves:
        s = game.result(s, a)
    return s


@pytest.mark.parametrize("path", LEVELS, ids=lambda p: p.name)
def test_dfs_solves_bundled_levels(path):
    g = Game(load_level(path))
    res = dfs(g)
    assert res["moves"] is not None
    assert g.is_goal(replay(g, res["moves"]))
    # BFS tối ưu nên lời giải DFS không thể ngắn hơn
    assert len(res["moves"]) >= len(bfs(g)["moves"])


def test_dfs_unsolvable_terminates():
    res = dfs(make_game(["..#G"]))
    assert res["moves"] is None
    assert res["expanded"] > 0


def test_dfs_max_depth_cuts_off():
    g = make_game(["...G"])
    assert dfs(g, max_depth=1)["moves"] is None
    assert dfs(g, max_depth=2)["moves"] == ["R", "R"]


def test_dfs_with_metrics():
    res = run_solver(dfs, make_game(["...G"]))
    assert res["length"] == len(res["moves"])
    assert res["expanded"] > 0
