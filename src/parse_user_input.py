from transformers import pipeline
import torch
import re


WORD2NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
DIFFICULTY_LABELS = ['beginner', 'intermediate', 'expert']
SPLIT_LABELS = ['push', 'pull', 'leg', 'upper', 'lower', 'full', 'chest', 'arm', 'bicep', 'tricep', 'shoulder', 'back', 'abs']
ROTATION = ['push', 'pull', 'legs']
EQUIPMENTS = ['bodyweight', 'cable', 'machine', 'sled', 'ropes', 'barbell', 'dumbbell', 'kettlebell', 'bands']
DEFAULT_EQUP = ["barbell","dumbbell","bodyweight","cable"]
MUSCLE_LABELS = ['abdominals', 'abductors', 'adductors', 'biceps', 'calves', 'chest', 'forearms', 'glutes',
'hamstrings', 'lats', 'lower back', 'middle back', 'neck', 'quadriceps', 'traps', 'triceps', 'shoulders']
SPECDAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
NEG_CUES = r"\b(can't|cannot|won't|no|except|but\s+not|not\s+on)\b"
DAY_ALIASES = {
    "mon":"monday","monday":"monday",
    "tue":"tuesday","tues":"tuesday","tuesday":"tuesday",
    "wed":"wednesday","weds":"wednesday","wednesday":"wednesday",
    "thu":"thursday","thur":"thursday","thurs":"thursday","thursday":"thursday",
    "fri":"friday","friday":"friday",
    "sat":"saturday","saturday":"saturday",
    "sun":"sunday","sunday":"sunday",
}
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

    def classify_difficulty(self):
        d = self.text
        dif = self.pipe(d, candidate_labels=DIFFICULTY_LABELS)
        top_label = dif["labels"][0]
        return top_label

    def extract_equipment(self, threshold=0.3):
        e = self.text
        equip = self.pipe(e, candidate_labels=EQUIPMENTS)
        if not equip or "labels" not in equip:
            return DEFAULT_EQUP

        chosen = [label for label, score in zip(equip["labels"], equip["scores"]) if score >= threshold]
        return chosen or DEFAULT_EQUP

    def specific_days(self, threshold=0.3):
        sd = self.text

        hits = set()
        for alias, canon in DAY_ALIASES.items():
            if re.search(rf"\b{alias}\b", sd):
                hits.add(canon)

        if hits:
            is_negative = re.search(NEG_CUES, sd) is not None
            if is_negative:
                unavailable = sorted(hits)
                available = [d for d in SPECDAYS if d not in unavailable]
                return {"available": available, "unavailable": unavailable}
            else:
                return {"available": sorted(hits), "unavailable": []}

        spec_day = self.pipe(sd, candidate_labels=SPECDAYS, multi_label=True)
        chosen = [label for label, score in zip(spec_day["labels"], spec_day["scores"]) if score >= threshold]
        if not chosen:
            return {"available": SPECDAYS[:], "unavailable": []}
        return {"available": chosen, "unavailable": []}

    def parse(self):
        final = {"days": self.extract_days(),
                 "split": self.classify_split(),
                 "difficulty": self.classify_difficulty(),
                 "equipment": self.extract_equipment(),
                 "specific_days": self.specific_days()
                 }
        return final


if __name__ == "__main__":

    test = "Can you create me a leg day expert workout."
    test2 = "Can you create me a 4 day workout for beginner and i can't workout on tuesday?"
    test3 = "Can you create me a arm day beginner workout but I only have dumbbells"

    UI = ParseInput(test)

    finalize = UI.parse()
    print(finalize)