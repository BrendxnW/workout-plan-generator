import requests
import os
import json


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

for ex_type in exercise_type:
    for musc in muscle:
        for dif in difficulty:
            params = {
            "type" : exercise_type,
            "muscle" : muscle,
            "difficulty" : difficulty,
            }

headers = {
    "X-Api-Key": API_KEY,
}

response = requests.get(BASE_URL, params=params, headers=headers )