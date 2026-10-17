import pytest

from game.game import Game
from game.level_loader import LevelError, validate_level
from game.state import LYING_H, STANDING, State, state_from_dict, state_to_dict
from tools.check_levels import bfs

LEGEND = {".": "floor", "#": "void", "G": "goal", "F": "fragile"}


def lv(grid, start=(0, 0), bridges=None, switches=None):
    d = {"version": 1, "id": "T", "grid": grid, "start": list(start), "legend": LEGEND}
    if bridges is not None:
        d["bridges"] = bridges
    if switches is not None:
        d["switches"] = switches
    return d


def br(i, cells, open_=False):
    return {"id": i, "cells": cells, "open": open_}


def sw(cell, type_="soft", targets=(0,), mode="toggle", **kw):
    return {"cell": list(cell), "type": type_, "targets": list(targets), "mode": mode, **kw}


def play(g, moves):
    s = g.initial_state()
    for a in moves:
        s, st = g.step(s, a)
    return s, st


# --- Fragile ---------------------------------------------------------------
def test_fragile_dung_thua_nam_an_toan():
    g = Game(lv(["...F.", "....G"], bridges=[br(0, [[1, 3]], True)]))
    assert g.status(State(STANDING, 0, 3, 1)) == "LOST"
    assert g.status(State(LYING_H, 0, 2, 1)) == "PLAYING"     # nằm đè fragile: được


# --- Bridges ---------------------------------------------------------------
def test_cau_dong_la_void_cau_mo_la_floor():
    for ch in ".#":                               # ký tự grid không quan trọng
        g = Game(lv(["." + ch + ".G"], bridges=[br(0, [[0, 1]], False)]))
        assert g.tile(0, 1) == "void"
        assert g.tile(0, 1, State(STANDING, 0, 0, 1)) == "floor"
        assert "R" not in g.actions(g.initial_state())
    g = Game(lv(["." + ch + ".G"], bridges=[br(0, [[0, 1]], True)]))
    assert g.tile(0, 1) == "floor" and g.initial_state().bridges == 1


def test_trang_thai_dau_theo_open():
    g = Game(lv(["....G"], bridges=[br(0, [[0, 1]], True), br(1, [[0, 2]], False)]))
    assert g.initial_state().bridges == 0b01


# --- Soft ------------------------------------------------------------------
GRID = ["......", "......", "..G..."]


def test_soft_nam_va_dung_deu_kich_hoat():
    g = Game(lv(GRID, bridges=[br(0, [[2, 5]])], switches=[sw((0, 2))]))
    s, _ = g.step(State(STANDING, 0, 0, 0), "R")           # nằm (0,1)-(0,2): chạm
    assert s.bridges == 1
    s, _ = g.step(State(LYING_H, 0, 1, 0), "R")            # đứng (0,3)? không; (0,1)R -> (0,3)
    assert s.bridges == 0
    s, _ = g.step(State(LYING_H, 0, 0, 0), "R")            # đứng (0,2)
    assert s.orient == STANDING and s.bridges == 1


def test_soft_cac_mode():
    def run(mode, **kw):
        g = Game(lv(GRID, bridges=[br(0, [[2, 5]], True)], switches=[sw((0, 1), mode=mode, **kw)]))
        s, _ = g.step(State(STANDING, 0, 0, 1), "R")        # nằm (0,1)-(0,2)
        s1, _ = g.step(s, "L")                              # đứng (0,0)
        s2, _ = g.step(State(STANDING, 0, 0, s1.bridges), "R")
        return s.bridges, s2.bridges
    assert run("toggle") == (0, 1)
    assert run("open") == (1, 1)
    assert run("close") == (0, 0)
    assert run("permanent") == (1, 1)                       # state mặc định true = open
    assert run("permanent", state=True) == (1, 1)
    assert run("permanent", state=False) == (0, 0)


# --- Heavy -----------------------------------------------------------------
def test_heavy_chi_khi_dung_thang():
    g = Game(lv(GRID, bridges=[br(0, [[2, 5]])], switches=[sw((0, 2), "heavy")]))
    s, _ = g.step(State(STANDING, 0, 0, 0), "R")           # nằm đè (0,2)
    assert s.bridges == 0
    s, _ = g.step(State(LYING_H, 0, 0, 0), "R")            # đứng (0,2)
    assert s.bridges == 1
    g2 = Game(lv(GRID, bridges=[br(0, [[2, 5]], True)], switches=[sw((0, 1), "heavy")]))
    s, _ = g2.step(State(STANDING, 0, 0, 1), "R")          # nằm đè (0,1): không đổi
    assert s.bridges == 1


# --- Nhiều đích / nhiều công tắc -------------------------------------------
def test_mot_cong_tac_nhieu_cau():
    g = Game(lv(GRID, bridges=[br(0, [[2, 4]]), br(1, [[2, 5]], True)],
                switches=[sw((0, 1), targets=(0, 1))]))
    s, _ = g.step(State(STANDING, 0, 0, 0b10), "R")
    assert s.bridges == 0b01


def test_nhieu_cong_tac_mot_cau():
    g = Game(lv(GRID, bridges=[br(0, [[2, 5]])],
                switches=[sw((0, 1), mode="open"), sw((0, 3), mode="close")]))
    s, _ = g.step(State(STANDING, 0, 0, 0), "R")
    assert s.bridges == 1
    s, _ = g.step(State(STANDING, 0, 2, 1), "R")           # nằm (0,3)-(0,4)
    assert s.bridges == 0


def test_nam_de_hai_cong_tac_theo_thu_tu_khai_bao():
    g = Game(lv(GRID, bridges=[br(0, [[2, 5]])],
                switches=[sw((0, 1), mode="open"), sw((0, 2), mode="close")]))
    s, _ = g.step(State(STANDING, 0, 0, 0), "R")
    assert s.bridges == 0                                   # open rồi close


# --- B2: rơi thì không kích hoạt -------------------------------------------
def test_roi_khong_kich_hoat():
    g = Game(lv(["..#.", "..G."], bridges=[br(0, [[1, 3]])], switches=[sw((0, 1))]))
    s, st = g.step(State(STANDING, 0, 0, 0), "R")   # nằm (0,1)-(0,2): chạm công tắc nhưng (0,2) void
    assert st == "LOST" and s.bridges == 0
    with pytest.raises(ValueError):
        g.result(State(STANDING, 0, 0, 0), "R")


# --- Hash / equality / JSON ------------------------------------------------
def test_state_khac_bridges_la_khac():
    a, b = State(STANDING, 0, 0, 1), State(STANDING, 0, 0, 0)
    assert a != b and len({a, b}) == 2
    g = Game(lv(GRID))
    assert state_from_dict(state_to_dict(a, g)).bridges == 1


# --- Loader ----------------------------------------------------------------
def ok(**kw):
    validate_level(lv(GRID, **kw))


def bad(**kw):
    with pytest.raises(LevelError):
        validate_level(lv(GRID, **kw))


def test_loader_hop_le():
    ok()
    ok(bridges=[], switches=[])
    ok(bridges=[br(0, [[2, 5]])], switches=[sw((0, 1), mode="permanent"), sw((0, 2), mode="permanent", state=False)])
    ok(switches=[{"cell": [0, 1], "type": "split", "split_to": [[1, 1], [1, 2]]}])


@pytest.mark.parametrize("bridges", [
    [br(1, [[2, 5]])], [br(0, [[2, 5]]), br(0, [[2, 4]])],       # id sai / trùng
    [br(0, [])], [br(0, [[9, 9]])], [br(0, [[2, 2]])],           # rỗng / ngoài bàn / goal
    [{"id": 0, "cells": [[2, 5]], "open": 1}],                   # open không phải bool
    [br(0, [[2, 5]]), br(1, [[2, 5]])],                          # ô thuộc hai cầu
])
def test_loader_bridges_loi(bridges):
    bad(bridges=bridges)


def test_loader_cau_de_fragile():
    with pytest.raises(LevelError):
        validate_level(lv(["..F"] + ["..G"], bridges=[br(0, [[0, 2]])]))


@pytest.mark.parametrize("switches", [
    [sw((0, 1), targets=(5,))], [sw((0, 1), targets=())],         # cầu không tồn tại / rỗng
    [sw((9, 9))], [sw((0, 1), mode="xyz")], [sw((0, 1), type_="lạ")],
    [sw((2, 5))],                                                  # công tắc trùng ô cầu
    [sw((2, 2))],                                                  # không phải floor (goal)
    [sw((0, 1)), sw((0, 1))],                                      # trùng ô
    [{"cell": [0, 1], "type": "split", "split_to": [[1, 1], [1, 1]]}],
    [{"cell": [0, 1], "type": "split", "split_to": [[1, 1]]}],
    [{"cell": [0, 1], "type": "split", "split_to": [[1, 1], [2, 2]]}],   # goal
])
def test_loader_switches_loi(switches):
    bad(bridges=[br(0, [[2, 5]])], switches=switches)


# --- BFS giải được ----------------------------------------------------------
# hành lang 1 hàng: đứng ở cột 0,3,6; cầu ở cột 4 chắn đường tới goal (cột 6)
ROW = ["......G"]
CAU = [br(0, [[0, 4]])]


def solve_won(level):
    g = Game(level)
    sol = bfs(g)
    assert sol is not None
    assert play(g, sol)[1] == "WON"


def test_bfs_soft_toggle_mo_cau():
    assert bfs(Game(lv(ROW, bridges=CAU))) is None            # bỏ qua công tắc thì kẹt
    solve_won(lv(ROW, bridges=CAU, switches=[sw((0, 1))]))


def test_bfs_heavy_phai_dung_thang():
    solve_won(lv(ROW, bridges=CAU, switches=[sw((0, 3), "heavy")]))
    # cột 1 chỉ có thể nằm đè -> heavy không bao giờ kích hoạt
    assert bfs(Game(lv(ROW, bridges=CAU, switches=[sw((0, 1), "heavy")]))) is None


def test_bfs_permanent_close_open():
    solve_won(lv(ROW, bridges=CAU, switches=[sw((0, 1), mode="permanent")]))
    closed = [br(0, [[0, 4]], True)]
    assert bfs(Game(lv(ROW, bridges=closed, switches=[sw((0, 1), mode="permanent", state=False)]))) is None
    solve_won(lv(ROW, bridges=closed, switches=[
        sw((0, 1), mode="permanent", state=False), sw((0, 3), mode="permanent", state=True)]))
