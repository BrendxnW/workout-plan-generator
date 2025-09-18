from transformers import pipeline
from src.parse_user_input import ParseInput
from src.sql_backend import fetch_by_block

PUSH = {"chest", "triceps", "shoulders"}
PULL = {"biceps", "lats", "middle_back", "lower_back", "traps", "forearms", "neck"}
LEGS = {"quadriceps", "hamstrings", "glutes", "calves", "abductors", "adductors"}
CORE = {"abdominals", "lower_back"}
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

DEFAULT_SPLITS = {
    2: ["upper", "lower"],
    3: {
        "beginner": ["push", "pull", "legs"],
        "intermediate": ["chest_triceps", "back_biceps", "legs_shoulders"],
        "expert": ["chest_triceps", "back_biceps", "legs_shoulders"]
    },
    4: {
        "beginner": ["push", "pull", "legs", "full"],
        "intermediate": ["chest_triceps", "back_biceps", "shoulders", "legs"],
        "expert": ["chest_triceps", "back_biceps", "shoulders", "legs"]
    },
    5: {
        "beginner": ["push", "pull", "legs", "upper", "lower"],
        "intermediate": ["chest_triceps", "back_shoulders", "chest_biceps", "legs", "back_arms"],
        "expert": ["chest_triceps", "back_shoulders", "chest_biceps", "legs", "back_arms"]
    },
    6: {
        "beginner":     ["push", "pull", "legs", "push", "pull", "legs"],
        "intermediate": ["chest_triceps", "back_biceps", "legs", "shoulders", "upper", "lower"],
        "expert":       ["chest_triceps", "back_biceps", "legs", "shoulders", "upper", "lower"],
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


class WorkoutPlanner:
    def __init__(self, text):
        self.text = text
        self.parsed = ParseInput(text).parse()
        self.pipe = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1", device=0)

    def _repeat_or_trim(self, seq, n):
        return [seq[i % len(seq)] for i in range(n)]

    def plan_workout(self):
        print("DEBUG parsed:", self.parsed)

        days_raw = self.parsed.get("num_days") or self.parsed.get("days") or 3
        try:
            days = int(days_raw)
        except Exception:
            days = 3
        days = max(1, min(days, 7))

        diff = (self.parsed.get("difficulty") or "beginner").strip().lower()
        if diff == "advanced":
            diff = "expert"

        explicit_splits = self.parsed.get("explicit_splits") or []
        if explicit_splits:
            return self._repeat_or_trim(explicit_splits, days)

        defaults = DEFAULT_SPLITS.get(days)
        if isinstance(defaults, list):
            plan = defaults
        elif isinstance(defaults, dict):
            plan = defaults.get(diff) or defaults.get("beginner")
        else:
            plan = DEFAULT_SPLITS[3]["beginner"]

        return self._repeat_or_trim(plan, days)


if __name__ == "__main__":
    print(ParseInput("can you make me a 5 day expert workout").parse())

    WP = WorkoutPlanner("can you make me a 5 day expert workout")
    print(WP.plan_workout())
