import argparse, json, sqlite3, sys
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS exercise (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    muscle TEXT,
    equipment TEXT,
    difficulty TEXT
);

CREATE TABLE IF NOT EXISTS exercise_splits (
    exercise_id INTEGER NOT NULL,
    split TEXT NOT NULL,
    PRIMARY KEY (exercise_id, split),
    FOREIGN KEY (exercise_id) References exercise(id) on DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_equipment ON exercise(equipment);
CREATE INDEX IF NOT EXISTS idx_diff      ON exercise(difficulty);
CREATE INDEX IF NOT EXISTS idx_split     ON exercise_splits(split);
"""

VALID_SPLITS = {"push", "pull", "legs", "upper", "lower", "full"}
def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data

def ensure_schema(con):
    con.executescript(SCHEMA)
    con.commit()

def upsert_exercise(cur, ex):
    name = ex.get("name")
    if not name:
        raise ValueError("Missing 'name' in exercise")
    muscle = ex.get("muscle")
    difficulty = ex.get("difficulty")
    equipment = ex.get("equipment")
    cur.execute(
        """
        INSERT OR IGNORE INTO exercise(name, muscle, equipment, difficulty)
        VALUES (?, ?, ?, ?)
        """,
        (name, muscle, equipment, difficulty),
    )
    cur.execute(
        """
        UPDATE exercise
           SET muscle=?, equipment=?, difficulty=?
         WHERE name=?
        """,
        (muscle, equipment, difficulty, name),
    )

    cur.execute("SELECT id FROM exercise WHERE name=?", (name,))
    return cur.fetchone()[0]

def upsert_split(cur, exercise_id, splits):
    if not splits:
        return
    if isinstance(splits, str):
        splits = [splits]
    clean = []
    for s in splits:
        if isinstance(s, str):
            s = s.strip().lower()
            if s in VALID_SPLITS:
                clean.append(s)
    for s in set(clean):
        cur.execute(
            """
            INSERT OR IGNORE INTO exercise_splits(exercise_id, split)
            VALUES (?, ?)
            """,
            (exercise_id, s),
        )

def migrate(json_path, db_path, overwrite):
    if overwrite and db_path.exists():
        db_path.unlink()
    elif db_path.exists() and not overwrite:
        print(f"[!] {db_path} exists. Use --overwrite to replace.", file=sys.stderr)
        sys.exit(1)

    records = load_json(json_path)
    con = sqlite3.connect(str(db_path))
    try:
        ensure_schema(con)
        cur = con.cursor()
        for ex in records:
            ex_id = upsert_exercise(cur, ex)
            upsert_split(cur, ex_id, ex.get("split"))
        con.commit()
    finally:
        con.close()

def main():
    ap = argparse.ArgumentParser(description="Migrate exercise_db.json -> SQLite")
    ap.add_argument("--json", required=True, help="Path to exercise_db.json")
    ap.add_argument("--db", default="data/workouts.db", help="SQLite DB output path")
    ap.add_argument("--overwrite", action="store_true", help="Replace existing DB")
    args = ap.parse_args()
    migrate(Path(args.json), Path(args.db), args.overwrite)
    print(f"Migration Complete -> {args.db}")

if __name__ == "__main__":
    main()