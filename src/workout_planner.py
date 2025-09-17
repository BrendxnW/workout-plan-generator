from transformers import pipeline
from parse_user_input import ParseInput
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

def get_pipeline():
    zs_pipe = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1", device=0)
    return zs_pipe

class WorkoutPlanner:
    def __init__(self, text):
        self.text = text
        self.parsed = ParseInput(text).parse()

    def plan_workout(self):
        zs = get_pipeline()
        days = int(self.parsed.get("num_days", 3))
        diff = self.parsed.get("difficulty")

        zs
        return


if __name__ == "__main__":

    test = "can you make me a 4 day beginner workout"
    WP = WorkoutPlanner(test)
    plan = WP.plan_workout(test)
    print(plan)
