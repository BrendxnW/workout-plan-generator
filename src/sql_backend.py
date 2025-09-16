from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().parents[1]/ "data" / "workouts.db"

SPLIT_FLAGS = {"push", "pull", "legs", "upper", "lower", "full"}

def connect(db_path):
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def _diff_allowed(difficulty):
    if difficulty == "beginner":
        diff_allowed = "beginner"
    if difficulty == "intermediate":
        diff_allowed = ("intermediate","beginner")
    return ("expert","intermediate","beginner")

def _query_exercises(where_sql, where_params, equipment, difficulty, limit, db_path):
    eq_list = equipment or ["barbell","dumbbell","bodyweight","cable"]
    diffs = _diff_allowed(difficulty)

    placeholders_eq = ",".join("?" * len(eq_list))
    placeholders_diff = ",".join("?" * len(diffs))

    sql = f"""
            SELECT e.id, e.name, e.muscle, e.equipment, e.difficulty
                FROM exercise e
            {where_sql}
            AND e.equipment IN ({placeholders_eq})
            AND e.difficulty IN ({placeholders_diff}
            LIMIT ?
"""

    params = where_params + eq_list + list(diffs) + [limit]
    with connect(db_path) as con:
        rows = con.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

def fetch_by_block(block, equipment, difficulty, limit, db_path):
    if block not in SPLIT_FLAGS:
        raise ValueError(f"Invalid block: {block}")

    where_sql = "JOIN exercise_splits s ON s.exercise_id = e.id WHERE s.split = ?"
    where_params = [block]
    return _query_exercises(where_sql, where_params, equipment, difficulty, limit, db_path)


def fetch_by_muscles(muscles, equipment, difficulty, limit, db_path):
    placeholder_mus = ",".join("?" * len(muscles))
    where_sql = f"WHERE e.muscle IN ({placeholder_mus})"
    where_params = muscles
    return _query_exercises(where_sql, where_params, equipment, difficulty, limit, db_path)