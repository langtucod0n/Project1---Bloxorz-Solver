from __future__ import annotations

from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game

# Khai báo các hằng số orientation
STANDING = 0
LYING_H = 1
LYING_V = 2

class State(NamedTuple):
    orient: int
    r: int
    c: int
    bridges: int = 0
    split: tuple | None = None

    # Bảng chuyển orientation (mục 0.3) - định nghĩa ở MỘT chỗ duy nhất.
    # (orient, action) -> (orient_mới, dr, dc)
    # Lấy ô bên trái/trên cùng để làm ô gốc *
TRANSITIONS: dict[tuple[int, str], tuple[int, int, int]] = {
    (STANDING, "U"): (LYING_V, -2, 0),
    (STANDING, "D"): (LYING_V, 1, 0),
    (STANDING, "L"): (LYING_H, 0, -2),
    (STANDING, "R"): (LYING_H, 0, 1),
    (LYING_H, "U"): (LYING_H, -1, 0),
    (LYING_H, "D"): (LYING_H, 1, 0),
    (LYING_H, "L"): (STANDING, 0, -1),
    (LYING_H, "R"): (STANDING, 0, 2),
    (LYING_V, "U"): (STANDING, -1, 0),
    (LYING_V, "D"): (STANDING, 2, 0),
    (LYING_V, "L"): (LYING_V, 0, -1),
    (LYING_V, "R"): (LYING_V, 0, 1),
}

OPPOSITE = {"U": "D", "D": "U", "L": "R", "R": "L"}

def cells(s: State) -> tuple[tuple[int, int], ...]:
# Các ô block đang chiếm. Chạy được cả với trạng thái thô ngoài bàn.
    if s.split:
        # Split states may carry metadata after the coordinate pairs.
        return tuple(cell for cell in s.split[:2] if len(cell) == 2)
        
    if s.orient == STANDING:
        return ((s.r, s.c),)
        
    if s.orient == LYING_H:
        return ((s.r, s.c), (s.r, s.c + 1))
        
    return ((s.r, s.c), (s.r + 1, s.c))

def _freeze(x):
#list -> tuple đệ quy, để State sau khi đọc từ JSON vẫn hashable
#Tránh lặp lại vô tận khi sử dụng thuật toán tìm kiếm
    if isinstance(x, list):
        return tuple(_freeze(i) for i in x)

    return x

def state_to_dict(s: State, game: "Game") -> dict:
    #Xuất dữ liệu ra ngoài (lưu file, vẽ GUI, xuất log).
    return {
        "orient": s.orient,
        "r": s.r,
        "c": s.c,
        "cells": [list(p) for p in cells(s)],
        "bridges": s.bridges,
        "split": s.split,          # TV3 sẽ chốt định dạng riêng
        "status": game.status(s),
    }

def state_from_dict(d: dict) -> State:
    #Đọc dữ liệu vào trong (nạp file save, đọc test case).
    return State(
        orient=d["orient"],
        r=d["r"],
        c=d["c"],
        bridges=d.get("bridges", 0),
        split=_freeze(d.get("split")),
    )