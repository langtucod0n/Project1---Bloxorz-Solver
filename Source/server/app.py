"""API backend: nối giao diện 3D với Python. Luật chơi và solver nằm trong game/ và solvers/."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from game.game import Game
from game.level_loader import LevelError, load_level
from game.state import State, state_to_dict
from solvers.registry import ALGORITHMS

LEVELS_DIR = Path(__file__).resolve().parent.parent / "levels"

app = FastAPI(title="Bloxorz Solver API")


class LoadRequest(BaseModel):
    level_id: str


class MoveRequest(BaseModel):
    direction: str


class SolveRequest(BaseModel):
    algorithm: str
    level_id: str


class Session:
    """Ván chơi hiện tại (một người chơi một lúc)."""

    def __init__(self):
        self.level_id: str | None = None
        self.game: Game | None = None
        self.state: State | None = None


session = Session()


def level_path(level_id: str) -> Path:
    # level_id chỉ được là tên file, tránh đường dẫn kiểu ../
    path = LEVELS_DIR / f"{level_id}.json"
    if Path(level_id).name != level_id or not path.is_file():
        raise HTTPException(404, f"Màn không tồn tại: {level_id!r}")
    return path


def open_level(level_id: str) -> tuple[dict, Game]:
    path = level_path(level_id)
    try:
        level = load_level(path)
        return level, Game(level)
    except LevelError as e:
        raise HTTPException(500, f"Màn {level_id!r} không hợp lệ: {e}") from e


@app.get("/api/levels")
def list_levels():
    return {"levels": sorted(p.stem for p in LEVELS_DIR.glob("*.json"))}


@app.post("/api/load")
def load(req: LoadRequest):
    level, game = open_level(req.level_id)
    session.level_id, session.game, session.state = req.level_id, game, game.initial_state()
    return {
        "level_id": req.level_id,
        "level": level,
        "state": state_to_dict(session.state, game),
    }


@app.post("/api/move")
def move(req: MoveRequest):
    if session.game is None:
        raise HTTPException(409, "Chưa nạp màn nào. Gọi /api/load trước.")
    if req.direction not in Game.ACTIONS:
        raise HTTPException(400, f"Hướng không hợp lệ: {req.direction!r}. Dùng U, D, L hoặc R.")
    if session.game.status(session.state) != "PLAYING":
        raise HTTPException(409, "Ván đã kết thúc. Gọi /api/load để chơi lại.")
    new_state, status = session.game.step(session.state, req.direction)
    if status != "LOST":
        # LOST: trả trạng thái thô để GUI vẽ khối rơi, ván vẫn giữ ở trạng thái trước đó
        session.state = new_state
    return {"state": state_to_dict(new_state, session.game), "status": status}


@app.post("/api/switch_control")
def switch_control():
    # Cơ chế tách khối chưa có trong Game (thuộc TV3).
    raise HTTPException(501, "Chưa hỗ trợ đổi khối điều khiển.")


@app.post("/api/solve")
def solve(req: SolveRequest):
    if req.algorithm not in ALGORITHMS:
        raise HTTPException(400, f"Thuật toán không hợp lệ: {req.algorithm!r}. Có: {sorted(ALGORITHMS)}")
    solver = ALGORITHMS[req.algorithm]
    if solver is None:
        raise HTTPException(501, f"Thuật toán {req.algorithm!r} chưa được cài đặt.")
    from solvers.metrics import run_solver

    _, game = open_level(req.level_id)
    result = run_solver(solver, game)
    moves = result.pop("moves")
    return {
        "algorithm": req.algorithm,
        "level_id": req.level_id,
        "solved": moves is not None,
        "moves": moves,
        "metrics": result,
    }
