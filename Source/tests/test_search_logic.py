"""Thử logic UCS/A* trên game giả (chạy được cả khi chưa nối game thật)."""
from tests.fake_game import Game
from tests.search_checks import check_same_cost_and_valid_path, check_heuristic

LEVELS = [(["........", ".......#", "...G....", ".#.....#"], (0, 0)),
          ([".....##", ".FFF...", ".FFFG..", "#......"], (0, 0)),
          (["......", ".FFFF.", ".FFFF.", "..G..."], (0, 0))]

def test_same_cost_and_valid_path():
    for grid, st in LEVELS:
        check_same_cost_and_valid_path(Game(grid, st))

def test_heuristics_admissible_and_consistent():
    for grid, st in LEVELS:
        check_heuristic(Game(grid, st))