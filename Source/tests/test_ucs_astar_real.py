"""Chạy UCS/A* trên các màn thật L01-L05. Cần nối load_game với level_loader của TV2."""
import pytest
from tests.search_checks import check_same_cost_and_valid_path, check_heuristic
from solvers.loader import load_game

LEVEL_IDS = ["L01", "L02", "L03", "L04", "L05"]


@pytest.mark.parametrize("lid", LEVEL_IDS)
def test_real_levels(lid):
    try:
        game = load_game(lid)
    except NotImplementedError:
        pytest.skip("chưa nối load_game")
    check_same_cost_and_valid_path(game)
    check_heuristic(game)
