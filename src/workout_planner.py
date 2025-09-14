from transformers import pipeline
from parse_user_input import ParseInput

PUSH = {"chest", "triceps", "shoulders"}
PULL = {"biceps", "lats", "middle_back", "lower_back", "traps", "forearms", "neck"}
LEGS = {"quadriceps", "hamstrings", "glutes", "calves", "abductors", "adductors"}
CORE = {"abdominals", "lower_back"}
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class WorkoutPlanner:
    def __init__(self, text):
        self.pipe = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1", device=0)
        self.input = ParseInput.parse(text)

    def plan_workout(self):
        plan = []
        for days in

        return plan