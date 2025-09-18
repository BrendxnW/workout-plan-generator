from flask import Flask, render_template, request
from src.workout_planner import WorkoutPlanner

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    user_text = request.form.get("prompt", "").strip()
    difficulty = request.form.get("difficulty", "").strip().lower()
    num_days = request.form.get("num_days", "3").strip()

    switched = f"{user_text} difficulty={difficulty} num_days={num_days}"
    wp = WorkoutPlanner(switched)
    plan = wp.plan_workout()

    return render_template("results.html",
                           plan=plan,
                           difficulty=difficulty or "beginner",
                           num_days=int(num_days),
                           user_text=user_text)


if __name__ == "__main__":
    app.run(debug=True)