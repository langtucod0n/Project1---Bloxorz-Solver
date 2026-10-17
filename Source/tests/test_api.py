import pytest
from fastapi.testclient import TestClient

from server.app import app, session

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_session():
    session.level_id = session.game = session.state = None


def test_levels():
    r = client.get("/api/levels")
    assert r.status_code == 200
    assert r.json()["levels"] == ["L01", "L02", "L03", "L04", "L05"]


def test_load_returns_level_and_state():
    r = client.post("/api/load", json={"level_id": "L01"})
    assert r.status_code == 200
    body = r.json()
    assert body["level"]["grid"] and body["state"]["status"] == "PLAYING"
    assert body["state"]["cells"] == [[0, 0]]


@pytest.mark.parametrize("level_id", ["NOPE", "../README", "..\\x"])
def test_load_unknown_level(level_id):
    assert client.post("/api/load", json={"level_id": level_id}).status_code == 404


def test_move_before_load():
    assert client.post("/api/move", json={"direction": "R"}).status_code == 409


def test_move_and_bad_direction():
    client.post("/api/load", json={"level_id": "L01"})
    r = client.post("/api/move", json={"direction": "R"})
    assert r.status_code == 200 and r.json()["state"]["orient"] == 1
    assert client.post("/api/move", json={"direction": "X"}).status_code == 400


def test_move_off_board_reports_lost_and_keeps_state():
    client.post("/api/load", json={"level_id": "L01"})
    r = client.post("/api/move", json={"direction": "U"})
    assert r.status_code == 200 and r.json()["status"] == "LOST"
    # ván vẫn ở trạng thái trước: đi tiếp hợp lệ
    assert client.post("/api/move", json={"direction": "R"}).json()["status"] == "PLAYING"


def test_winning_then_move_rejected():
    client.post("/api/load", json={"level_id": "L02"})
    sol = client.post("/api/solve", json={"algorithm": "bfs", "level_id": "L02"}).json()["moves"]
    for d in sol:
        r = client.post("/api/move", json={"direction": d})
    assert r.json()["status"] == "WON"
    assert client.post("/api/move", json={"direction": "R"}).status_code == 409


@pytest.mark.parametrize("algo", ["bfs", "ids", "dfs"])
def test_solve(algo):
    r = client.post("/api/solve", json={"algorithm": algo, "level_id": "L03"})
    assert r.status_code == 200
    body = r.json()
    assert body["solved"] and body["moves"]
    assert set(body["metrics"]) == {"expanded", "time", "peak_memory", "length"}
    assert body["metrics"]["length"] == len(body["moves"])


def test_solve_errors():
    assert client.post("/api/solve", json={"algorithm": "x", "level_id": "L01"}).status_code == 400
    assert client.post("/api/solve", json={"algorithm": "bfs", "level_id": "NOPE"}).status_code == 404
    assert client.post("/api/solve", json={"algorithm": "bfs"}).status_code == 422


def test_switch_control_not_implemented():
    assert client.post("/api/switch_control").status_code == 501


def test_solve_timeout_returns_504():
    r = client.post("/api/solve", json={"algorithm": "bfs", "level_id": "L05", "timeout": 0.001})
    assert r.status_code == 504


def test_solve_rejects_bad_timeout():
    assert client.post("/api/solve", json={"algorithm": "bfs", "level_id": "L01", "timeout": -1}).status_code == 422
