import copy
import json
from pathlib import Path

import pytest

from game.game import Game
from game.level_loader import LevelError, load_level, validate_level
from game.state import LYING_H, LYING_V, STANDING, State, state_from_dict, state_to_dict
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
    ok(switches=[{"cell": [0, 1], "type": "split", "split_to": [[1, 1], [2, 3]]}])


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


# ===========================================================================
# ĐỢT 2: split, cube đơn, hành động S, ghép khối
# ===========================================================================
BOARD = ["......", "......", "......", "......", ".....G"]   # 5x6, goal (4,5)


def sp(cell, a, b):
    return {"cell": list(cell), "type": "split", "split_to": [list(a), list(b)]}


def sps(p0, p1, act=0, bridges=0):
    #State đang split, cube điều khiển là `act`
    p = (p0, p1)[act]
    return State(STANDING, p[0], p[1], bridges, (p0, p1, act))


SPLIT_SW = [sp((1, 1), (3, 0), (3, 3))]


# --- kích hoạt split --------------------------------------------------------
def test_split_khoi_dung_tach():
    g = Game(lv(BOARD, switches=SPLIT_SW))
    s, st = g.step(State(LYING_H, 1, 2, 0), "L")           # đứng xuống (1,1)
    assert st == "PLAYING"
    assert s == State(STANDING, 3, 0, 0, ((3, 0), (3, 3), 0))


def test_split_khoi_nam_de_khong_tach():
    g = Game(lv(BOARD, switches=SPLIT_SW))
    s, _ = g.step(State(STANDING, 1, 0, 0), "R")           # nằm (1,1)-(1,2)
    assert s.split is None and s.orient == LYING_H


def test_split_dung_lai_va_nhieu_cong_tac():                   # P5
    g = Game(lv(BOARD, switches=[sp((1, 1), (3, 0), (3, 3)), sp((0, 4), (2, 0), (4, 3))]))
    s, _ = g.step(State(LYING_H, 1, 2, 0), "L")
    assert s.split == ((3, 0), (3, 3), 0)
    s, _ = g.step(State(LYING_H, 0, 5, 0), "L")            # đứng xuống (0,4)
    assert s.split == ((2, 0), (4, 3), 0)
    # dùng lại được: đứng xuống công tắc lần nữa thì tách lần nữa
    s2, _ = g.step(State(LYING_H, 1, 2, 0), "L")
    assert s2.split == ((3, 0), (3, 3), 0)


def test_split_khong_kich_hoat_luc_teleport():                # P3
    g = Game(lv(BOARD, bridges=[br(0, [[4, 4]])],
                switches=[sp((1, 1), (3, 0), (3, 3)), sw((3, 0))]))
    s, _ = g.step(State(LYING_H, 1, 2, 0), "L")
    assert s.split is not None and s.bridges == 0


# --- actions / S ------------------------------------------------------------
def test_actions_khi_split_co_S_theo_thu_tu():
    g = Game(lv(BOARD, switches=SPLIT_SW))
    assert g.actions(sps((3, 0), (3, 3))) == ["U", "D", "R", "S"]   # L ra ngoài bàn bị lọc
    assert "S" not in g.actions(g.initial_state())


def test_S_khi_khong_split_loi():
    g = Game(lv(BOARD))
    with pytest.raises(ValueError):
        g.result(g.initial_state(), "S")
    with pytest.raises(ValueError):
        g.step(g.initial_state(), "S")


def test_S_doi_cube_khong_kich_hoat_khong_doi_cau():
    g = Game(lv(BOARD, bridges=[br(0, [[4, 4]])], switches=[sw((3, 3))]))
    s = sps((3, 0), (3, 3), 0)                              # cube 1 đang đứng trên soft
    s2, st = g.step(s, "S")
    assert st == "PLAYING" and s2.split == ((3, 0), (3, 3), 1)
    assert (s2.r, s2.c) == (3, 3) and s2.bridges == 0 and s2.orient == STANDING
    assert g.step(s2, "S")[0] == s                           # đổi lại


# --- cube lăn, rơi, goal ----------------------------------------------------
def test_cube_lan_bon_huong():
    g = Game(lv(BOARD))
    s = sps((2, 2), (4, 0))
    for a, rc in (("U", (1, 2)), ("D", (3, 2)), ("L", (2, 1)), ("R", (2, 3))):
        s2, st = g.step(s, a)
        assert st == "PLAYING" and (s2.r, s2.c) == rc and s2.split == (rc, (4, 0), 0)


def test_cube_roi_void_ngoai_ban_cau_dong_fragile():
    g = Game(lv(["......", "..#...", "..F..G"], bridges=[br(0, [[0, 1]])]))
    assert g.step(sps((0, 0), (2, 5)), "U")[1] == "LOST"      # ngoài bàn
    assert g.step(sps((1, 1), (2, 5)), "R")[1] == "LOST"      # void (1,2)
    assert g.step(sps((0, 0), (2, 5)), "R")[1] == "LOST"      # cầu đóng (0,1)
    assert g.step(sps((1, 1), (2, 5)), "D")[1] == "PLAYING"   # (2,1) floor
    s, st = g.step(sps((2, 1), (2, 5)), "R")                   # fragile (2,2)
    assert st == "LOST" and s.bridges == 0
    assert "R" not in g.actions(sps((2, 1), (2, 5)))
    with pytest.raises(ValueError):
        g.result(sps((2, 1), (2, 5)), "R")


def test_cube_tren_goal_khong_thang():
    g = Game(lv(BOARD))
    s = sps((4, 5), (0, 0))
    assert g.status(s) == "PLAYING" and not g.is_goal(s)
    assert g.step(sps((3, 5), (0, 0)), "D")[1] == "PLAYING"


def test_P1_cube_lan_vao_cube_kia():
    g = Game(lv(BOARD))
    s = sps((2, 2), (2, 3))                                   # dựng tay (ghép bình thường không để kề nhau)
    assert "R" not in g.actions(s)
    for f in (g.result, g.step):
        with pytest.raises(ValueError):
            f(s, "R")


# --- công tắc với cube ------------------------------------------------------
def test_cube_soft_den_kich_hoat_dung_yen_thi_khong():
    g = Game(lv(BOARD, bridges=[br(0, [[4, 4]])], switches=[sw((2, 2))]))
    s, _ = g.step(sps((2, 1), (0, 0)), "R")                    # cube 0 đến soft
    assert s.bridges == 1
    s, _ = g.step(sps((2, 2), (0, 0), 1, bridges=1), "R")      # cube 1 di chuyển, cube 0 đứng yên trên soft
    assert s.bridges == 1


def test_cube_khong_kich_hoat_heavy_va_split():
    g = Game(lv(BOARD, bridges=[br(0, [[4, 4]])], switches=[sw((2, 2), "heavy")]))
    assert g.step(sps((2, 1), (0, 0)), "R")[0].bridges == 0
    g = Game(lv(BOARD, switches=[sp((2, 2), (0, 5), (4, 0))]))
    s, _ = g.step(sps((2, 1), (0, 0)), "R")
    assert s.split == ((2, 2), (0, 0), 0)                      # không tách lại


# --- ghép -------------------------------------------------------------------
def test_ghep_cung_hang_cung_cot():
    g = Game(lv(BOARD, bridges=[br(0, [[4, 4]], True)]))
    s, _ = g.step(sps((2, 2), (2, 4), bridges=1), "R")
    assert s == State(LYING_H, 2, 3, 1) and s.split is None
    s, _ = g.step(sps((2, 2), (4, 2)), "D")
    assert s == State(LYING_V, 3, 2, 0)
    s, _ = g.step(sps((3, 2), (1, 2)), "U")                    # cube 0 ở dưới: min hàng = 1
    assert s == State(LYING_V, 1, 2, 0)
    s, _ = g.step(sps((2, 4), (2, 2), 0), "L")                 # cube 0 ở phải: min cột = 3? (2,3),(2,2)
    assert s == State(LYING_H, 2, 2, 0)


def test_ghep_xay_ra_sau_B3():
    g = Game(lv(BOARD, bridges=[br(0, [[4, 4]])], switches=[sw((2, 3))]))
    s, _ = g.step(sps((2, 2), (2, 4)), "R")                    # soft vừa đến + ghép cùng một nước
    assert s == State(LYING_H, 2, 3, 1)


def test_sau_ghep_thang_binh_thuong():
    g = Game(lv(BOARD))
    s, _ = g.step(sps((4, 2), (4, 4)), "R")                    # ghép LYING_H (4,3)
    assert s == State(LYING_H, 4, 3, 0)
    s, st = g.step(s, "R")                                     # đứng (4,5) = goal
    assert st == "WON" and g.is_goal(s)


# --- P4 ---------------------------------------------------------------------
def test_P4_khoi_nam_dong_cau_duoi_chinh_no():
    g = Game(lv(["......G."], bridges=[br(0, [[0, 2]], True)], switches=[sw((0, 1), mode="close")]))
    s0 = g.initial_state()
    assert s0.bridges == 1
    assert "R" not in g.actions(s0)
    with pytest.raises(ValueError):
        g.result(s0, "R")
    s, st = g.step(s0, "R")
    assert st == "LOST" and s == State(LYING_H, 0, 1, 0)       # bridges ĐÃ ĐỔI (khác rơi ở B2)


def test_P4_cube_dung_yen_tren_cau_bi_dong():
    g = Game(lv(BOARD, bridges=[br(0, [[3, 3]], True)], switches=[sw((2, 2), mode="close")]))
    s0 = sps((2, 1), (3, 3), bridges=1)
    assert "R" not in g.actions(s0)
    with pytest.raises(ValueError):
        g.result(s0, "R")
    s, st = g.step(s0, "R")
    assert st == "LOST" and s.bridges == 0 and (s.r, s.c) == (2, 2)


# --- fragile + cầu qua step -------------------------------------------------
def test_fragile_cau_qua_step():
    g = Game(lv(["...F.", "....G"], bridges=[br(0, [[1, 3]], True)]))
    s, st = g.step(State(STANDING, 0, 1, 1), "R")              # nằm đè (0,2)-(0,3): an toàn
    assert st == "PLAYING" and s.bridges == 1
    s, st = g.step(s, "R")                                      # đứng (0,4)? nằm (0,2) R -> đứng (0,4)
    assert st == "PLAYING"
    s, st = g.step(State(LYING_H, 0, 1, 1), "R")               # đứng (0,3) = fragile
    assert st == "LOST" and s == State(STANDING, 0, 3, 1)


# --- hash / JSON ------------------------------------------------------------
def test_state_split_hash_va_json():
    a, b = sps((1, 1), (3, 3), 0), sps((1, 1), (3, 3), 1)
    assert a != b and len({a, b}) == 2
    c = sps((1, 1), (3, 3), 0, bridges=1)
    assert a != c and len({a, c}) == 2
    g = Game(lv(BOARD))
    for s in (a, b, c):
        assert state_from_dict(json.loads(json.dumps(state_to_dict(s, g)))) == s


# --- loader (đợt 2) ---------------------------------------------------------
def test_loader_start_tren_cau_dong():
    with pytest.raises(LevelError):
        validate_level(lv(GRID, start=(0, 1), bridges=[br(0, [[0, 1]])]))
    validate_level(lv(GRID, start=(0, 1), bridges=[br(0, [[0, 1]], True)]))


def test_loader_split_to_trung_cau_hoac_ke_nhau():
    with pytest.raises(LevelError):
        validate_level(lv(GRID, bridges=[br(0, [[1, 3]])], switches=[sp((0, 1), (1, 3), (1, 0))]))
    validate_level(lv(GRID, bridges=[br(0, [[1, 4]])], switches=[sp((0, 1), (1, 3), (1, 0))]))
    for pair in (((1, 1), (1, 2)), ((1, 1), (2, 1))):           # kề nhau
        with pytest.raises(LevelError):
            validate_level(lv(GRID, switches=[sp((0, 1), *pair)]))
    validate_level(lv(GRID, switches=[sp((0, 1), (1, 1), (1, 3))]))


def test_loader_mode_bat_buoc():
    no_mode = {"cell": [0, 1], "type": "soft", "targets": [0]}
    with pytest.raises(LevelError):
        validate_level(lv(GRID, bridges=[br(0, [[2, 5]])], switches=[no_mode]))
    validate_level(lv(GRID, bridges=[br(0, [[2, 5]])], switches=[{**no_mode, "mode": "toggle"}]))


# --- BFS với split ----------------------------------------------------------
def solve(level):
    g = Game(level)
    sol = bfs(g)
    assert sol is not None
    return g, sol


ROW9 = "....G...."          # đứng thường chỉ ở cột 0,3,6 nên goal cột 4 không tới được nếu không tách


def test_bfs_split_roi_ghep_roi_thang():
    lvl = lv(["........G"], switches=[sp((0, 3), (0, 5), (0, 7))])
    assert bfs(Game(lv(["........G"]))) is None
    g, sol = solve(lvl)
    assert "S" not in sol and play(g, sol)[1] == "WON"


def test_bfs_bat_buoc_dung_S():
    lvl = lv([ROW9], bridges=[br(0, [[0, 6]])],
             switches=[sp((0, 3), (0, 5), (0, 8)), sw((0, 7), mode="open")])
    g, sol = solve(lvl)
    assert "S" in sol and play(g, sol)[1] == "WON"


def test_bfs_split_va_soft_toggle_mo_cau_cho_cube():
    lvl = lv([ROW9], bridges=[br(0, [[0, 6]])],
             switches=[sp((0, 3), (0, 8), (0, 5)), sw((0, 7))])
    g, sol = solve(lvl)
    assert "S" not in sol and play(g, sol)[1] == "WON"


def test_bfs_ket_thuc_khi_khong_giai_duoc():
    # cầu không bao giờ mở được; có split, S và công tắc: BFS phải dừng với None
    lvl = lv([ROW9], bridges=[br(0, [[0, 6]])],
             switches=[sp((0, 3), (0, 5), (0, 8)), sw((0, 7), mode="close")])
    assert bfs(Game(lvl)) is None


# ===========================================================================
# ĐỢT 3: bộ màn chơi L06–L16
# ===========================================================================
LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels"

# id -> (nhóm, cơ chế, cách bỏ cơ chế để kiểm, số nước BFS, số nước khi bỏ cơ chế (None = không giải được))
# "cơ chế" tính lại từ dữ liệu màn và phải khớp đúng bảng này (test_d3_co_che_khop_bang).
LEVELS_D3 = {
    "L06": ("fragile", "fragile", "fragile", 9, 6),
    "L07": ("fragile", "fragile", "fragile", 10, 7),
    "L08": ("fragile", "fragile", "fragile", 6, 5),
    "L09": ("công tắc & cầu", "soft toggle bridge", "switches", 10, None),
    "L10": ("công tắc & cầu", "soft heavy open close multi_switch bridge", "switches", 16, None),
    "L11": ("công tắc & cầu", "soft permanent permanent_false multi_target multi_switch bridge", "switches", 18, None),
    "L12": ("công tắc & cầu", "soft toggle multi_switch bridge", "switches", 17, None),
    "L13": ("split", "split", "split", 9, None),
    "L14": ("split", "split soft open bridge S", "split", 9, None),
    "L15": ("split", "split soft heavy toggle close multi_switch bridge S", "split", 13, None),
    "L16": ("split", "split soft permanent fragile bridge", "split", 14, None),
}
# màn có fragile trong nhóm split: ô fragile phải nằm ngoài tầm cube (mục 5 dispatch)
D3_IDS = sorted(LEVELS_D3)


def d3_level(id_):
    return load_level(LEVELS_DIR / f"{id_}.json")


def bo_co_che(level, kind):
    #Bản bỏ cơ chế (không ghi file): fragile -> '.', switches -> [], split -> xoá công tắc split
    l = copy.deepcopy(level)
    if kind == "fragile":
        l["grid"] = [row.replace("F", ".") for row in l["grid"]]
    elif kind == "switches":
        l["switches"] = []
    else:
        l["switches"] = [s for s in l["switches"] if s["type"] != "split"]
    return l


def co_che(level, sol):
    #Tập cơ chế suy ra từ dữ liệu màn + lời giải BFS
    tags = set()
    if any("F" in row for row in level["grid"]):
        tags.add("fragile")
    if level["bridges"]:
        tags.add("bridge")
    dem = {}
    for s in level["switches"]:
        tags.add(s["type"])
        if s["type"] == "split":
            continue
        tags.add(s["mode"])
        if s["mode"] == "permanent" and s.get("state", True) is False:
            tags.add("permanent_false")
        if len(s["targets"]) > 1:
            tags.add("multi_target")
        for t in s["targets"]:
            dem[t] = dem.get(t, 0) + 1
    if any(n >= 2 for n in dem.values()):
        tags.add("multi_switch")
    if "S" in sol:
        tags.add("S")
    return tags


def test_d3_bang_metadata_day_du():
    files = sorted(p.stem for p in LEVELS_DIR.glob("L*.json") if int(p.stem[1:]) >= 6)
    assert files == D3_IDS                                    # không thiếu, không thừa
    assert files == [f"L{n:02d}" for n in range(6, 6 + len(files))]   # liên tục, không nhảy số


@pytest.mark.parametrize("id_", D3_IDS)
def test_d3_validate_id_version(id_):
    level = d3_level(id_)                                     # load_level đã gọi validate_level
    validate_level(level)
    assert level["id"] == id_ and level["version"] == 1
    assert "switches" in level and "bridges" in level
    assert sum(row.count("G") for row in level["grid"]) == 1


@pytest.mark.parametrize("id_", D3_IDS)
def test_d3_giai_duoc_va_phat_lai_toi_won(id_):
    g = Game(d3_level(id_))
    sol = bfs(g)
    assert sol is not None and 6 <= len(sol) <= 25
    assert len(sol) == LEVELS_D3[id_][3]
    s = g.initial_state()
    for i, a in enumerate(sol):
        s, st = g.step(s, a)
        assert st == ("WON" if i == len(sol) - 1 else "PLAYING")
    assert g.is_goal(s)


@pytest.mark.parametrize("id_", D3_IDS)
def test_d3_bat_buoc_dung_co_che(id_):
    _, _, kind, n, n_bo = LEVELS_D3[id_]
    level = d3_level(id_)
    sol_bo = bfs(Game(bo_co_che(level, kind)))
    if kind == "fragile":
        assert sol_bo is not None and len(sol_bo) < n         # bỏ fragile thì NGẮN HƠN
    else:
        assert sol_bo is None or len(sol_bo) > n              # không giải được hoặc dài hơn
    assert (None if sol_bo is None else len(sol_bo)) == n_bo


@pytest.mark.parametrize("id_", D3_IDS)
def test_d3_co_che_khop_bang(id_):
    level = d3_level(id_)
    assert co_che(level, bfs(Game(level))) == set(LEVELS_D3[id_][1].split())


def test_d3_phu_co_che_ca_bo():
    tags = set()
    for id_ in D3_IDS:
        level = d3_level(id_)
        tags |= co_che(level, bfs(Game(level)))
    need = {"fragile", "soft", "heavy", "toggle", "open", "close", "permanent", "permanent_false",
            "split", "S", "multi_target", "multi_switch"}
    assert need <= tags, need - tags


def test_d3_heavy_phai_dung_thang_L10():
    level = d3_level("L10")
    g = Game(level)
    sol = bfs(g)
    heavy = next(tuple(s["cell"]) for s in level["switches"] if s["type"] == "heavy")
    s, mo = g.initial_state(), None
    for a in sol:
        s2, _ = g.step(s, a)
        if mo is None and s2.bridges != s.bridges:
            mo = s2                                           # lần đầu cầu đổi: do heavy
        s = s2
    assert mo.orient == STANDING and (mo.r, mo.c) == heavy
    # nếu nằm đè cũng mở được (soft) thì có lời giải ngắn hơn: heavy thật sự buộc phải đứng
    soft = copy.deepcopy(level)
    next(s for s in soft["switches"] if s["type"] == "heavy")["type"] = "soft"
    assert len(bfs(Game(soft))) < len(sol)


def test_d3_L11_bay_va_nhieu_cau():
    level = d3_level("L11")
    sol = bfs(Game(level))
    # công tắc điều khiển 2 cầu; chỉ điều khiển cầu 0 thì không giải được
    mot_cau = copy.deepcopy(level)
    mot_cau["switches"][0]["targets"] = [0]
    assert bfs(Game(mot_cau)) is None
    # công tắc state:false là bẫy: bỏ nó thì lời giải ngắn hơn
    khong_bay = copy.deepcopy(level)
    khong_bay["switches"] = khong_bay["switches"][:1]
    assert len(bfs(Game(khong_bay))) < len(sol)


@pytest.mark.parametrize("id_", [i for i in D3_IDS if "split" in LEVELS_D3[i][1].split()])
def test_d3_split_bo_split_khong_giai_duoc(id_):
    # màn nào dùng soft cho cube thì bỏ split là hết đường
    assert bfs(Game(bo_co_che(d3_level(id_), "split"))) is None


def test_d3_split_ket_hop_fragile_ngoai_tam_cube():
    # liệt kê trong báo cáo/spec: L16 là màn split duy nhất có fragile
    co = [i for i in D3_IDS if "split" in LEVELS_D3[i][1].split() and "fragile" in LEVELS_D3[i][1].split()]
    assert co == ["L16"]
    level = d3_level("L16")
    grid = level["grid"]
    cau = {tuple(c) for b in level["bridges"] for c in b["cells"]}
    ke = lambda r, c: [(r + dr, c + dc) for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))]
    # loang từ hai ô split_to qua mọi ô không void (ô cầu coi như đi được)
    sp_ = next(s for s in level["switches"] if s["type"] == "split")
    thay = {tuple(p) for p in sp_["split_to"]}
    todo = list(thay)
    while todo:
        r, c = todo.pop()
        for q in ke(r, c):
            if 0 <= q[0] < len(grid) and 0 <= q[1] < len(grid[0]) and q not in thay \
                    and (grid[q[0]][q[1]] != "#" or q in cau) and grid[q[0]][q[1]] != "F":
                thay.add(q)
                todo.append(q)
    fragile = {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "F"}
    assert fragile and not (fragile & thay)
    # kể cả coi fragile là đi được, cube vẫn không chạm tới: ô kề fragile cũng không thuộc vùng cube
    assert not any(q in thay for f in fragile for q in ke(*f))
