"""Save/load .mz maze files and settings.json (tutorial preference)."""
import json, os
from config import *

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")


def save_maze(path, grid, start, end):
    with open(path, "w") as f:
        json.dump({"rows": len(grid), "cols": len(grid[0]), "grid": grid, "start": start, "end": end}, f)


def load_maze(path):
    """Returns (grid, start, end). Raises ValueError for a corrupt/invalid file."""
    try:
        with open(path) as f:
            d = json.load(f)
        grid = d["grid"]
        assert len(grid) == d["rows"] and all(len(r) == d["cols"] for r in grid)
        assert all(v in TERRAIN_NAMES for row in grid for v in row)
        s, e = d["start"], d["end"]
        s = tuple(s) if s else None
        e = tuple(e) if e else None
    except Exception as ex:
        raise ValueError("Not a valid MazeCraft .mz file") from ex
    return grid, s, e


def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            return {"show_tutorial": True, **json.load(f)}
    except Exception:
        return {"show_tutorial": True}


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except OSError:
        pass
