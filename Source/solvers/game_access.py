"""Cho DUY NHAT code cua TV1 cham vao noi bo game cua TV2."""
from game.state import cells

def occupied(game, s):
    return cells(s)

def tile_kind(game, r, c):
    return game.tile(r, c)

def goal_pos(game):
    return game.goal

def is_split(s):
    return getattr(s, "split", None) is not None