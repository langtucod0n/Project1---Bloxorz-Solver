from pathlib import Path
from game.game import Game
from game.level_loader import load_level

LEVEL_DIR = Path(__file__).resolve().parents[1] / "levels"

def load_game(level_id):
    return Game(load_level(LEVEL_DIR / f"{level_id}.json"))