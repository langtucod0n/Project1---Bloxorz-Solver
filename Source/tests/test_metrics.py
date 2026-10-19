from game.game import Game
from solvers.metrics import run_solver

LEGEND = {".": "floor", "#": "void", "G": "goal", "F": "fragile"}


def make_game(grid, start=(0, 0)):
    return Game({"version": 1, "id": "T", "grid": grid, "start": list(start), "legend": LEGEND})


def fake_solver(game):
    return {"moves": ["R", "D"], "expanded": 7}


def fail_solver(game):
    return {"moves": None, "expanded": 3}


def test_result_structure():
    res = run_solver(fake_solver, make_game(["...G"]))
    assert set(res) == {"moves", "expanded", "time", "peak_memory", "length"}
    assert res["moves"] == ["R", "D"]
    assert res["expanded"] == 7
    assert res["length"] == 2
    assert res["time"] >= 0
    assert res["peak_memory"] >= 0


def test_no_solution_has_no_length():
    res = run_solver(fail_solver, make_game(["...G"]))
    assert res["moves"] is None
    assert res["length"] is None


def test_peak_memory_grows_with_allocation():
    def hungry(game):
        data = [0] * 1_000_000
        return {"moves": [], "expanded": len(data) and 1}

    res = run_solver(hungry, make_game(["...G"]))
    assert res["peak_memory"] > 1_000_000
