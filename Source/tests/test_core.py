import json
from pathlib import Path

import pytest

from game.game import Game
from game.level_loader import LevelError, load_level, validate_level
from game.state import (
    LYING_H, LYING_V, OPPOSITE, STANDING, State, TRANSITIONS,
    cells, state_from_dict, state_to_dict,
)

LEGEND = {".": "floor", "#": "void", "G": "goal", "F": "fragile"}
LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels"


def make_game(grid, start=(0, 0)):
    return Game({"version": 1, "id": "T", "grid": grid, "start": list(start), "legend": LEGEND})


# --- A2: 12 cặp chuyển orientation ---------------------------------------
# (orient, action) -> trạng thái mong đợi, bắt đầu từ (5, 5)
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
BIG = make_game(["." * 12] * 11 + ["." * 11 + "G"], (5, 5))  # bàn đủ rộng, không void


@pytest.mark.parametrize("orient,action,expected", CASES)
def test_12_transitions(orient, action, expected):
    assert BIG.result(State(orient, 5, 5), action) == expected


def test_transition_table_has_12_entries():
    assert len(TRANSITIONS) == 12


@pytest.mark.parametrize("orient,action,_", CASES)
def test_transition_reversible(orient, action, _):
    new_orient, dr, dc = TRANSITIONS[(orient, action)]
    back_orient, bdr, bdc = TRANSITIONS[(new_orient, OPPOSITE[action])]
    assert (back_orient, dr + bdr, dc + bdc) == (orient, 0, 0)


# --- A3: hợp lệ / thắng / thua --------------------------------------------
def test_out_of_board_and_void_invalid():
    g = make_game(["..#", "...", "..G"])
    s = g.initial_state()
    assert g.actions(s) == ["D"]          # U, L ra ngoài; R đè lên void (0,2)
    with pytest.raises(ValueError):
        g.result(s, "U")
    with pytest.raises(ValueError):
        g.result(s, "R")
    with pytest.raises(ValueError):
        g.result(s, "X")


def test_fragile_standing_lost_lying_safe():
    g = make_game(["...", ".F.", "..G"], (0, 1))
    _, status = g.step(State(STANDING, 0, 1), "D")   # nằm dọc (1,1)-(2,1): qua F
    assert status == "PLAYING"
    _, status = g.step(State(LYING_V, 0, 1), "D")    # đứng lên tại (2,1) -> floor
    assert status == "PLAYING"
    f = make_game(["...", "...", ".FG"], (0, 1))
    _, status = f.step(State(LYING_V, 0, 1), "D")    # đứng lên tại (2,1) = F
    assert status == "LOST"
    assert "D" not in f.actions(State(LYING_V, 0, 1))


def test_win_only_when_standing_on_goal():
    g = make_game(["...G"])
    s, status = g.step(State(LYING_H, 0, 1), "R")    # đứng tại (0,3) = G
    assert status == "WON" and g.is_goal(s)
    lying = State(LYING_H, 0, 2)                      # nằm qua goal
    assert g.status(lying) == "PLAYING" and not g.is_goal(lying)


def test_lost_step_returns_raw_state():
    g = make_game(["..G"])
    s2, status = g.step(g.initial_state(), "U")
    assert status == "LOST" and s2 == State(LYING_V, -2, 0)
    assert cells(s2) == ((-2, 0), (-1, 0))            # cells chạy được ngoài bàn


# --- A5: bất biến, hash, thứ tự, JSON ---------------------------------------
def test_result_does_not_mutate():
    g = make_game(["..G", "...", "..."])
    s = g.initial_state()
    before = tuple(s)
    g.result(s, "R")
    assert tuple(s) == before


def test_hash_equality():
    assert State(0, 1, 2) == State(0, 1, 2)
    assert hash(State(0, 1, 2)) == hash(State(0, 1, 2))
    assert len({State(0, 1, 2), State(0, 1, 2), State(1, 1, 2)}) == 2


def test_actions_never_lead_to_fall_and_fixed_order():
    g = Game(load_level(LEVELS_DIR / "L05.json"))
    stack, seen = [g.initial_state()], set()
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        acts = g.actions(s)
        assert acts == g.actions(s)
        assert acts == [a for a in "UDLR" if a in acts]       # đúng thứ tự U, D, L, R
        for a in acts:
            s2, status = g.step(s, a)
            assert status != "LOST"
            stack.append(s2)


def test_cells_three_orientations():
    assert cells(State(STANDING, 2, 3)) == ((2, 3),)
    assert cells(State(LYING_H, 2, 3)) == ((2, 3), (2, 4))
    assert cells(State(LYING_V, 2, 3)) == ((2, 3), (3, 3))


def test_state_json_roundtrip():
    g = make_game(["...G"])
    for s in (State(STANDING, 0, 0), State(LYING_H, 0, 1), State(0, 0, 0, bridges=5, split=((0, 0), (0, 1), 0))):
        d = json.loads(json.dumps(state_to_dict(s, g)))     # đi qua JSON thật
        assert state_from_dict(d) == s


def test_state_dict_matches_example():
    g = make_game(["...G"])
    d = state_to_dict(State(LYING_H, 0, 2), g)
    assert d == {"orient": 1, "r": 0, "c": 2, "cells": [[0, 2], [0, 3]],
                 "bridges": 0, "split": None, "status": "PLAYING"}


def test_board_info():
    g = make_game(["...#.", "...G.", "....."])
    assert (g.rows, g.cols, g.goal) == (3, 5, (1, 3))
    assert g.tile(0, 3) == "void" and g.tile(1, 3) == "goal" and g.tile(0, 0) == "floor"
    assert g.tile(-1, 0) == "void" and g.tile(3, 0) == "void" and g.tile(0, 5) == "void"


# --- A4: loader ---------------------------------------------------------------
def test_loader_errors():
    base = {"grid": ["..G"], "start": [0, 0], "legend": LEGEND}
    validate_level(base)
    for bad in (
        {**base, "grid": ["..G", ".."]},           # không chữ nhật
        {**base, "grid": ["..?"]},                  # ký tự lạ
        {**base, "grid": ["..."]},                  # không có goal
        {**base, "grid": ["G.G"]},                  # 2 goal
        {**base, "start": [5, 5]},                  # start ngoài bàn
        {**base, "grid": ["#.G"]},                  # start là void
        {**base, "grid": ["F.G"]},                  # start là fragile
    ):
        with pytest.raises(LevelError):
            validate_level(bad)


def test_loader_ignores_unknown_keys():
    validate_level({"grid": ["..G"], "start": [0, 0], "legend": LEGEND, "future_key": 123})


@pytest.mark.parametrize("path", sorted(LEVELS_DIR.glob("L*.json")), ids=lambda p: p.name)
def test_every_level_is_solvable(path):
    from tools.check_levels import bfs
    assert bfs(Game(load_level(path))) is not None


@pytest.mark.parametrize("path", sorted(LEVELS_DIR.glob("L*.json")), ids=lambda p: p.name)
def test_play_solution_to_win(path):
    """Mục E: gọi step liên tục theo lời giải BFS thì chơi hết màn, kết thúc WON."""
    from tools.check_levels import bfs
    g = Game(load_level(path))
    s = g.initial_state()
    for i, a in enumerate(bfs(g)):
        s, status = g.step(s, a)
        assert status == ("WON" if i == len(bfs(g)) - 1 else "PLAYING")
    assert g.is_goal(s)