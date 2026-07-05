"""
Baseline - Non Adaptive Learning SD
Menggunakan seed_questions.py dari proyek utama
"""

from flask import Flask, request, jsonify, send_from_directory
import random, os

app = Flask(__name__, static_folder="static", template_folder="static")

# Load soal dari seed_questions
QUESTIONS = []

def load_questions_from_seed():
    global QUESTIONS
    try:
        from seed_questions import seed
        from database import init_db, get_conn

        init_db()
        seed()  # Jalankan seeding soal

        # Ambil semua soal dari database
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM questions").fetchall()
            for row in rows:
                r = dict(row)
                qtype = r.get("question_type", "pilgan")
                question = {
                    "id": r["id"],
                    "kc": r["kc_id"],
                    "q": r["question"],
                    "type": qtype,
                    "answer": r["answer"]
                }
                if qtype == "pilgan":
                    question["options"] = [r["opt_a"], r["opt_b"], r["opt_c"], r["opt_d"]]
                else:
                    question["options"] = []
                QUESTIONS.append(question)
        print(f"✅ Loaded {len(QUESTIONS)} questions from seed_questions.py")
    except Exception as e:
        print("Error loading questions:", e)
        # Fallback soal sederhana
        QUESTIONS.append({"id":1, "kc":"KC-B1", "q":"1 + 1 = ?", "options":["1","2","3","4"], "answer":"2", "type":"pilgan"})

# Jalankan saat startup
load_questions_from_seed()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Tambahkan variabel global
current_index = 0

@app.get("/api/next-question/<sid>")
def next_question(sid):
    """Non-adaptive: soal urut (sequential)"""
    global current_index
    if not QUESTIONS:
        return jsonify({"error": "No questions available"})
    
    q = QUESTIONS[current_index % len(QUESTIONS)]  # urut berulang
    current_index += 1
    return jsonify(q)

@app.post("/api/answer/<sid>")
def answer(sid):
    """Proses jawaban (sama seperti adaptive)"""
    data = request.json
    correct = str(data.get("selected")).strip().lower() == str(data.get("answer")).strip().lower()
    return jsonify({
        "correct": correct,
        "message": "Benar!" if correct else f"Salah. Jawaban benar: {data.get('answer')}"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
