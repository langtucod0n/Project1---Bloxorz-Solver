"""Test API backend (TV5): phát lại lời giải qua /api/move và /api/switch_control.

Chạy: cd Source && pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient

from server.app import app
from solvers.bfs import bfs
from solvers.loader import load_game

client = TestClient(app)

ALL_LEVELS = [f"L{i:02d}" for i in range(1, 17)]


def replay_via_api(level_id, moves):
    """Gửi từng nước đi lên API như giao diện, trả về status cuối."""
    client.post("/api/load", json={"level_id": level_id})
    body = None
    for m in moves:
        if m == "S":
            res = client.post("/api/switch_control", json={})
        else:
            res = client.post("/api/move", json={"direction": m})
        assert res.status_code == 200, f"nước {m!r}: {res.status_code} {res.json()}"
        body = res.json()
    return body["status"]


@pytest.mark.parametrize("level_id", ALL_LEVELS)
def test_bfs_solution_replays_to_win(level_id):
    moves = bfs(load_game(level_id))["moves"]
    assert replay_via_api(level_id, moves) == "WON"


def test_switch_control_requires_loaded_split_state():
    client.post("/api/load", json={"level_id": "L01"})
    res = client.post("/api/switch_control", json={})
    assert res.status_code == 400        # khối chưa tách
