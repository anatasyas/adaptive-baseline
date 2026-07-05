from flask import Flask, request, jsonify, send_from_directory
import random, os

app = Flask(__name__, static_folder="static")

# Data soal sederhana (bisa di-expand)
QUESTIONS = [
    {"id":1, "kc":"KC-B1", "q":"1 + 1 = ?", "options":["1","2","3","4"], "answer":"2"},
    {"id":2, "kc":"KC-B1", "q":"Ada berapa apel? 🍎🍎", "options":["1","2","3","4"], "answer":"2"},
]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/api/next-question")
def next_question():
    q = random.choice(QUESTIONS)
    return jsonify(q)

@app.post("/api/answer")
def answer():
    data = request.json
    correct = data["answer"] == data["selected"]
    return jsonify({
        "correct": correct,
        "message": "Benar!" if correct else "Salah"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
