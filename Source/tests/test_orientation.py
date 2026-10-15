import pytest

from game.game import Game
from game.state import LYING_H, LYING_V, STANDING, State

LEGEND = {".": "floor", "#": "void", "G": "goal", "F": "fragile"}

# Bàn 12x12 toàn ô floor (goal ở góc dưới phải) để mọi nước đi từ (5, 5) đều hợp lệ.
GRID = ["." * 12] * 11 + ["." * 11 + "G"]
GAME = Game({"version": 1, "id": "T", "grid": GRID, "start": [5, 5], "legend": LEGEND})

NAME = {STANDING: "STANDING", LYING_H: "LYING_H", LYING_V: "LYING_V"}

# (orient, action, trạng thái mong đợi)
CASES = [
    (STANDING, "U", State(LYING_V, 3, 5)),
    (STANDING, "D", State(LYING_V, 6, 5)),
    (STANDING, "L", State(LYING_H, 5, 3)),
    (STANDING, "R", State(LYING_H, 5, 6)),
    (LYING_H, "U", State(LYING_H, 4, 5)),
    (LYING_H, "D", State(LYING_H, 6, 5)),
    (LYING_H, "L", State(STANDING, 5, 4)),
    (LYING_H, "R", State(STANDING, 5, 7)),
    (LYING_V, "U", State(STANDING, 4, 5)),
    (LYING_V, "D", State(STANDING, 7, 5)),
    (LYING_V, "L", State(LYING_V, 5, 4)),
    (LYING_V, "R", State(LYING_V, 5, 6)),
]


@pytest.mark.parametrize(
    "orient,action,expected",
    CASES,
    ids=[f"{NAME[o]}-{a}" for o, a, _ in CASES],
)
def test_orientation_transition(orient, action, expected):
    assert GAME.result(State(orient, 5, 5), action) == expected