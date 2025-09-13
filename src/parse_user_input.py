from transformers import pipeline
import torch
import re


WORD2NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
DIFFICULTY_LABELS = ['beginner', 'intermediate', 'expert']
SPLIT_LABELS = ['push', 'pull', 'leg', 'upper', 'lower', 'full', 'chest', 'arm', 'bicep', 'tricep', 'shoulder', 'back', 'abs']
ROTATION = ['push', 'pull', 'legs']
MUSCLE_LABELS = ['abdominals', 'abductors', 'adductors', 'biceps', 'calves', 'chest', 'forearms', 'glutes',
'hamstrings', 'lats', 'lower back', 'middle back', 'neck', 'quadriceps', 'traps', 'triceps', 'shoulders']
_CANON = {
    'leg': 'legs', 'legs': 'legs',
    'arm': 'arms', 'arms': 'arms',
    'bicep': 'biceps', 'biceps': 'biceps',
    'tricep': 'triceps', 'triceps': 'triceps',
    'shoulder': 'shoulders', 'shoulders': 'shoulders',
    'abdominal': 'abs', 'abdominals': 'abs', 'abs': 'abs'
}

class ParseInput:
    def __init__(self, text):
        self.pipe = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1", device=0)
        self.text = text.strip().lower()

    def extract_days(self):
        m = re.search(r"(one|two|three|four|five|six|seven|\d+)\s*-?\s*day?", self.text)
        if m:
            token = m.group(1)
            if token.isdigit():
                num_days = int(token)
            else:
                num_days = WORD2NUM[token]
        else:
            num_days = 1
        return num_days

    def classify_split(self):
        def _extract_explicit_splits(t: str):
            day_hits = re.findall(
                r"\b(push|pull|legs?|upper|lower|full|chest|back|shoulders?|arms?|biceps?|triceps?|abs)\s*(?:day|workout)?\b",
                t
            )

            list_hits = []
            for chunk in re.split(r"[.;\n]", t):
                if "/" in chunk or "," in chunk:
                    parts = re.split(r"[\/,]\s*", chunk)
                    for p in parts:
                        m = re.match(
                            r"\b(push|pull|legs?|upper|lower|full|chest|back|shoulders?|arms?|biceps?|triceps?|abs)\b",
                            p.strip()
                        )
                        if m:
                            list_hits.append(m.group(1))

            hits = day_hits + list_hits
            return [_CANON.get(h, h) for h in hits] if hits else []

        num_days = self.extract_days()
        t = self.text

        explicit = _extract_explicit_splits(t)
        if explicit:
            return [explicit[i % len(explicit)] for i in range(num_days)]

        res = self.pipe(t, candidate_labels=SPLIT_LABELS)
        top_label = _CANON.get(res["labels"][0], res["labels"][0])
        top_score = float(res["scores"][0])

        if top_score >= 0.60:
            return [top_label] * num_days

        return [ROTATION[i % len(ROTATION)] for i in range(num_days)]




    def classify_difficulty(self, text):
        d = self.text
        dif = self.pipe(d, candidate_labels=DIFFICULTY_LABELS)
        top_label = dif["label"][0]
        return top_label


    def detect_muscles_rules(self, text):
        ...
    def detect_muscles_ml(text):  # optional (zero-shot multi-label or embeddings)
        ...
    def finalize(intent_partial:dict):
        ...
    def parse(text):
        ...



if __name__ == "__main__":

    text = "Can you create me a 4 day beginner workout."

    UI = ParseInput(text)
    result = UI.classify_split()
    print(result)