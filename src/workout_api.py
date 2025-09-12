import requests
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()

API_KEY = os.environ.get("EXERCISE_API")
BASE_URL = os.environ.get("EXERCISE_BASE_URL")

all_exercise = []

exercise_type = [
    "cardio",
    "olympic weightlifting",
    "plyometrics",
    "powerlifting",
    "strength",
    "stretching",
    "strongman",
        ]


muscle = [
    "abdominals",
    "abductors",
    "adductors",
    "biceps",
    "calves",
    "chest",
    "forearms",
    "glutes",
    "hamstrings",
    "lats",
    "lower back",
    "middle back",
    "neck",
    "quadriceps",
    "traps",
    "triceps",
      ]


difficulty = [
    "beginner",
    "intermediate",
    "expert",
]


headers = {"X-Api-Key": API_KEY}
session = requests.Session()
session.headers.update(headers)


for ex_type in exercise_type:
    for musc in muscle:
        for dif in difficulty:
            params = {
            "type" : ex_type,
            "muscle" : musc,
            "difficulty" : dif,
            }

            r = session.get(BASE_URL, params=params, timeout=20)
            r.raise_for_status()
            data = r.json() if r.text else []

            for it in data:
                key = (it.get("name", "").lower(), it.get("muscle"), it.get("type"))

                if not any(
                        (e.get("name", "").lower(), e.get("muscle"), e.get("type")) == key
                    for e in all_exercise
                ):
                    all_exercise.append(it)

            time.sleep(0.2)

print(f"Fetched {len(all_exercise)} unique exercises!")

with open("../data/exercise_db.json", "w", encoding="utf-8") as f:
    json.dump(all_exercise, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    s = requests.Session()
    s.headers.update({"X-Api-Key": API_KEY})
    test_params = {"type": "strength", "muscle": "chest", "difficulty": "beginner"}
    r = s.get(BASE_URL, params=test_params, timeout=10)
    print("Smoke test:", r.status_code, "items:", len(r.json()))

