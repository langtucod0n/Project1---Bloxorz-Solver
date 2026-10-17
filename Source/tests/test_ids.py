from pathlib import Path

import pytest

from game.game import Game
from game.level_loader import load_level
from solvers.bfs import bfs
from solvers.ids import ids

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
def test_ids_is_shortest_like_bfs(path):
    g = Game(load_level(path))
    res = ids(g)
    assert g.is_goal(replay(g, res["moves"]))
    assert len(res["moves"]) == len(bfs(g)["moves"])


def test_ids_unsolvable_terminates():
    assert ids(make_game(["..#G"]))["moves"] is None
