from src.parse_user_input import ParseInput
from src.sql_backend import fetch_by_block, DB_PATH, fetch_by_muscles_balanced

PUSH = {"chest", "triceps", "shoulders"}
PULL = {"biceps", "lats", "middle_back", "lower_back"}
LEGS = {"quadriceps", "hamstrings", "glutes", "calves", "abductors", "adductors"}
CORE = {"abdominals", "lower_back"}
BLOCK_SPLITS = {"push", "pull", "legs", "upper", "lower", "full"}

DEFAULT_SPLITS = {
    2: ["upper", "rest", "rest", "lower", "rest", "rest", "rest"],
    3: {
        "beginner": ["push", "rest", "pull", "rest", "legs", "rest", "rest"],
        "intermediate": ["chest_triceps", "rest", "back_biceps", "rest", "legs_shoulders", "rest", "rest"],
        "expert": ["chest_triceps", "rest", "back_biceps", "rest", "legs_shoulders", "rest", "rest"]
    },
    4: {
        "beginner": ["push", "pull", "legs", "full"],
        "intermediate": ["chest_triceps", "rest", "back_biceps", "rest", "shoulders", "legs", "rest"],
        "expert": ["chest_triceps", "rest", "back_biceps", "rest", "shoulders", "legs", "rest"]
    },
    5: {
        "beginner": ["push", "pull", "legs", "upper", "lower"],
        "intermediate": ["chest_triceps", "back_shoulders", "rest",  "chest_biceps", "legs", "back_arms", "rest"],
        "expert": ["chest_triceps", "back_shoulders", "rest",  "chest_biceps", "legs", "back_arms", "rest"]
    },
    6: {
        "beginner":     ["push", "pull", "legs", "push", "pull", "legs"],
        "intermediate": ["chest_triceps", "back_biceps", "legs", "shoulders", "rest", "upper", "lower"],
        "expert":       ["chest_triceps", "back_biceps", "legs", "shoulders", "rest", "upper", "lower"],
    },
    7: {
        "beginner":     ["push", "pull", "legs", "push", "pull", "legs", "full"],
        "intermediate": ["chest_triceps", "back_biceps", "legs", "shoulders", "upper", "lower", "full"],
        "expert":       ["chest_triceps", "back_biceps", "legs", "shoulders", "upper", "lower", "full"],
    },
}

COMBO_GROUPS = {
    "chest_triceps":   ["chest", "triceps"],
    "back_biceps":     ["lats", "middle_back", "lower_back", "traps", "biceps", "forearms"],
    "legs_shoulders":  ["quadriceps", "hamstrings", "glutes", "calves", "shoulders"],
    "chest_shoulders": ["chest", "shoulders", "triceps"],
    "back_traps":      ["lats", "middle_back", "lower_back", "traps"],
    "back_rear_delts": ["lats", "middle_back", "lower_back", "rear_delts", "traps"],
    "arms":            ["biceps", "triceps", "forearms"],
    "chest_biceps":    ["chest", "biceps"],
    "back_triceps":    ["lats", "middle_back", "triceps"],
    "shoulders":       ["shoulders", "traps", "rear_delts"],
    "back_shoulders":  ["lats", "middle_back", "shoulders", "traps"],
    "legs":            ["quadriceps", "hamstrings", "glutes", "calves", "abductors", "adductors"],
    "legs_arms":       ["quadriceps", "hamstrings", "glutes", "biceps", "triceps"],
    "upper": ["chest","shoulders","triceps","biceps","lats","middle_back","traps","forearms"],
    "lower": ["quadriceps","hamstrings","glutes","calves","abductors","adductors"],
    "push":  ["chest","shoulders","triceps"],
    "pull":  ["lats","middle_back","lower_back","biceps","traps","forearms"],
    "full":  ["chest","triceps","shoulders","biceps","lats","middle_back","lower_back","traps",
              "forearms","quadriceps","hamstrings","glutes","calves","abductors","adductors","abdominals"],
}

MUSCLE_QUOTAS = {
    "chest": (3, 5),
    "lats": (3, 5), "middle_back": (2, 4), "lower_back": (1, 2),
    "quadriceps": (3, 5), "hamstrings": (3, 5), "glutes": (2, 4),

    "shoulders": (2, 4), "biceps": (2, 3), "triceps": (2, 3),

    "traps": (1, 2), "rear_delts": (1, 2), "forearms": (1, 2),
    "calves": (1, 2), "abductors": (0, 1), "adductors": (0, 1),
    "abdominals": (1, 2),

    "_default": (1, 2),
}

class WorkoutPlanner:
    def __init__(self, source, **overrides):
        parsed = dict(source) if isinstance(source, dict) else ParseInput(source).parse()
        for k, v in (overrides or {}).items():
            if v not in (None, "", []):
                parsed[k] = v

        days_raw = parsed.get("num_days") or parsed.get("days") or 3
        try:
            days = int(days_raw)
        except:
            days = 3
        parsed["days"] = max(1, min(days, 7))

        diff = (parsed.get("difficulty") or "beginner").strip().lower()
        if diff == "advanced": diff = "expert"
        parsed["difficulty"] = diff
        parsed["equipment"] = parsed.get("equipment") or ["barbell", "dumbbell", "bodyweight", "cable"]
        self.parsed = parsed

    def _resolve_week_split(self):
        days = self.parsed["days"]
        diff = self.parsed["difficulty"]
        explicit = self.parsed.get("explicit_splits") or []

        if explicit:
            week = list(explicit)
        else:
            default = DEFAULT_SPLITS.get(days)
            if isinstance(default, list):
                week = default
            elif isinstance(default, dict):
                week = default.get(diff) or next(iter(default.values()))
            else:
                week = DEFAULT_SPLITS[3]["beginner"]

        if len(week) < 7:
            week = week + ["rest"] * (7 - len(week))
        return week[:7]

    def _fetch_for_split(self, split, equipment, difficulty, limit):
        if split == "rest":
            return []

        if split in BLOCK_SPLITS:
            return fetch_by_block(split, equipment, difficulty, limit, DB_PATH) or []

        muscle = COMBO_GROUPS.get(split, [])
        if not muscle:
            return []
        return fetch_by_muscles_balanced(muscle, equipment, difficulty, 3,4, DB_PATH) or []

    def plan_workout(self, limit=4):
        print("DEBUG parsed:", self.parsed)

        week = self._resolve_week_split()
        equip = self.parsed["equipment"]
        diff = self.parsed["difficulty"]

        plan = []
        for day, split in enumerate(week, 1):
            exs = self._fetch_for_split(split, equip, diff, limit)
            plan.append({"day": day, "split": split, "exercises": exs})
        return plan


if __name__ == "__main__":
    print(ParseInput("can you make me a 5 day expert workout").parse())

    WP = WorkoutPlanner("can you make me a 5 day expert workout")
    print(WP.plan_workout())
