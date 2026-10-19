from pathlib import Path

import pytest

from game.game import Game
from game.level_loader import load_level
from game.state import STANDING
from solvers.bfs import bfs

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
def test_bfs_solves_bundled_levels(path):
    g = Game(load_level(path))
    res = bfs(g)
    assert res["moves"] is not None
    assert g.is_goal(replay(g, res["moves"]))
    assert res["expanded"] > 0


def test_bfs_unsolvable():
    g = make_game(["..#G"])  # ô void chặn đường tới đích
    res = bfs(g)
    assert res["moves"] is None


def test_bfs_start_is_not_goal_and_shortest():
    # Đích cách 3 ô: lăn R hai lần (đứng -> nằm -> đứng)
    g = make_game(["...G"])
    res = bfs(g)
    assert res["moves"] == ["R", "R"]
    assert replay(g, res["moves"]).orient == STANDING


def test_bfs_with_metrics():
    from solvers.metrics import run_solver

    res = run_solver(bfs, make_game(["...G"]))
    assert res["moves"] == ["R", "R"]
    assert res["length"] == 2
    assert res["expanded"] > 0
