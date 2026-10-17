"""Chạy solver trong tiến trình riêng để có thể dừng khi quá thời gian."""
import multiprocessing as mp
import os

DEFAULT_TIMEOUT = float(os.environ.get("BLOXORZ_SOLVE_TIMEOUT", "10"))


class SolveTimeout(Exception):
    pass


def _worker(conn, algorithm: str, level: dict) -> None:
    try:
        from game.game import Game
        from solvers.metrics import run_solver
        from solvers.registry import ALGORITHMS

        conn.send(("ok", run_solver(ALGORITHMS[algorithm], Game(level))))
    except Exception as e:  # báo lỗi về tiến trình cha thay vì chết im lặng
        conn.send(("error", f"{type(e).__name__}: {e}"))
    finally:
        conn.close()


def solve_with_timeout(algorithm: str, level: dict, timeout: float | None = None) -> dict:
    """Trả kết quả của run_solver. Raise SolveTimeout nếu quá hạn, RuntimeError nếu solver lỗi."""
    timeout = DEFAULT_TIMEOUT if timeout is None else timeout
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_worker, args=(child, algorithm, level), daemon=True)
    proc.start()
    child.close()
    try:
        if not parent.poll(timeout):
            raise SolveTimeout(f"Quá {timeout:g}s mà chưa giải xong")
        kind, payload = parent.recv()
    except EOFError:
        raise RuntimeError("Tiến trình giải bị dừng đột ngột") from None
    finally:
        parent.close()
        if proc.is_alive():
            proc.terminate()
        proc.join()
    if kind == "error":
        raise RuntimeError(payload)
    return payload
