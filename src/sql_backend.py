from pathlib import Path
import sqlite3
import random


DB_PATH = Path(__file__).resolve().parents[1]/ "data" / "workouts.db"

SPLIT_FLAGS = {"push", "pull", "legs", "upper", "lower", "full"}

def connect(db_path):
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def _diff_allowed(difficulty):
    difficulty = (difficulty or "beginner").lower()
    if difficulty == "expert":
        return "expert", "intermediate", "beginner"
    if difficulty == "intermediate":
        return "intermediate", "beginner"
    return ("beginner",)

def _pick_count():
    return random.randint(3, 4)

def fetch_for_muscle(
    muscle: str,
    equipment,
    difficulty: str,
    max_per: int,
    db_path
):

    eq_list = equipment or ["barbell", "dumbbell", "bodyweight", "cable"]
    diffs = _diff_allowed(difficulty)

    placeholders_eq   = ",".join("?" * len(eq_list))
    placeholders_diff = ",".join("?" * len(diffs))

    sql = f"""
        SELECT e.id, e.name, e.muscle, e.equipment, e.difficulty
        FROM exercise e
        WHERE e.muscle = ?
          AND e.equipment IN ({placeholders_eq})
          AND e.difficulty IN ({placeholders_diff})
        ORDER BY CASE e.difficulty
                   WHEN ? THEN 1
                   WHEN ? THEN 2
                   WHEN ? THEN 3
                   ELSE 999
                 END, RANDOM()
        LIMIT ?
    """

    pref = list(diffs) + ["expert","intermediate","beginner"]
    seen = set(); pref = [x for x in pref if not (x in seen or seen.add(x))][:3]
    while len(pref) < 3:
        pref.append("beginner")

    params = [muscle, *eq_list, *diffs, *pref, max_per]
    with connect(db_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

def fetch_by_muscle_quota(muscle, equipment, difficulty, db_path),


def fetch_by_muscles_balanced(
    muscles,
    equipment,
    difficulty: str,
    db_path
):
    """
    For each muscle in order, return 3–5 (configurable) exercises.
    If fewer exist, return as many as available.
    Ensures per-muscle balance.
    """
    out = []
    for m in muscles:
        want = _pick_count()
        rows = fetch_for_muscle(m, equipment, difficulty, want, db_path)
        out.extend(rows[:want])
    return out

def _query_exercises(where_sql, where_params, equipment, difficulty, limit, db_path):
    eq_list = equipment or ["barbell", "dumbbell", "bodyweight", "cable"]
    diffs = _diff_allowed(difficulty)

    placeholders_eq = ",".join("?" * len(eq_list))
    placeholders_diff = ",".join("?" * len(diffs))

    sql = f"""
           SELECT e.id, e.name, e.muscle, e.equipment, e.difficulty
           FROM exercise e
           {where_sql}
           AND e.equipment IN ({placeholders_eq})
           AND e.difficulty IN ({placeholders_diff})
           ORDER BY RANDOM()
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