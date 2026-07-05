"""
Baseline - Non Adaptive Learning SD
Load soal dari JSON
"""

from flask import Flask, request, jsonify, send_from_directory
import json, os, random

app = Flask(__name__, static_folder="static", template_folder="static")

# Load soal dari JSON
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "questions.json")
QUESTIONS = []

def load_questions():
    global QUESTIONS
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            QUESTIONS = json.load(f)
        print(f"✅ Loaded {len(QUESTIONS)} questions from JSON")
    except Exception as e:
        print("Error loading questions:", e)

load_questions()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/api/next-question/<sid>")
def next_question(sid):
    """Soal random atau sequential (non-adaptive)"""
    if not QUESTIONS:
        return jsonify({"error": "No questions available"})
    q = random.choice(QUESTIONS)
    return jsonify(q)

@app.post("/api/answer/<sid>")
def answer(sid):
    data = request.json
    correct = str(data.get("selected")).strip().lower() == str(data.get("answer")).strip().lower()
    return jsonify({
        "correct": correct,
        "message": "Benar!" if correct else f"Salah. Jawaban benar: {data.get('answer')}"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
