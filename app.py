"""
Baseline - Non Adaptive
Menggunakan fungsi get_random_question dari database
"""

from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder="static", template_folder="static")

# Import dari proyek utama
from database import init_db, get_random_question, get_conn
from seed_questions import seed

# Inisialisasi
def init_baseline():
    init_db()
    # Jalankan seeding jika belum ada soal
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if count == 0:
        seed()
    print("✅ Baseline initialized with questions from database")

init_baseline()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/api/next-question/<sid>")
def next_question(sid):
    """Non-adaptive: ambil soal random dari database"""
    q = get_random_question(None)  # None = ambil dari semua KC
    if not q:
        q = {"q": "Soal tidak ditemukan", "options": ["A","B","C","D"], "answer": "A"}
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
