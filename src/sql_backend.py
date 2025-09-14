from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().parents[1]/ "data" / "workouts.db"

SPLIT_FLAGS = {"push", "pull", "legs", "upper", "lower", "full"}

def connect(db_path):
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def fetch_by_block(block, equipment, difficulty, limit, db_path):
    if block not in SPLIT_FLAGS:
        raise ValueError(f"Invalid block: {block}")

    eq_list = equipment or ["barbell","dumbbell","bodyweight","cable"]

    if difficulty == "beginner":
        diff_allowed = "beginner"
    elif difficulty == "intermediate":
        diff_allowed = ("intermediate","beginner")
    else:
        diff_allowed = ("expert","intermediate","beginner")

    placeholders_eq = ",".join("?" * len(eq_list))
    placeholders_diff = ",".join("?" * len(diff_allowed))

    sql = f"""
        SELECT e.id, e.name, e.muscle, e.equipment, e.difficulty
            FROM exercise e
            JOIN exercise_splits s ON s.exercise_id = e.id
        WHERE s.split = ?
            AND e.equipment IN ({placeholders_eq})
            AND e.difficulty IN ({placeholders_diff}
        LIMIT?
    """

    params = [block] + eq_list + list(diff_allowed) + [limit]
    with connect(db_path) as con:
        rows = con.execute(sql, params).fetchall()
        return [dict(r) for r in rows]