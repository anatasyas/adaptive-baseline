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
    
    from database import seed_ontology
    from seed_questions import seed

    print("🔄 Seeding ontology...")
    DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "math_grade1.json")
    
    if os.path.exists(DATA_PATH):
        seed_ontology(DATA_PATH)
    else:
        print("⚠️ math_grade1.json tidak ditemukan, menggunakan seeding default")
        seed_ontology()   # pakai default di database.py

    print("🔄 Seeding questions...")
    seed()

    print("✅ Baseline initialized successfully")

init_baseline()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.post("/api/register")
@app.post("/api/register")
def register():
    try:
        data = request.json or {}
        name = data.get("name", "Siswa").strip() or "Siswa"
        avatar = int(data.get("avatar", 1))
        sid = f"S{random.randint(10000,99999)}"
        
        # Simpan ke database kalau ada
        try:
            from database import create_student
            create_student(sid, name, avatar)
            print(f"✅ Siswa baru: {sid} - {name}")
        except Exception as db_err:
            print("Warning database:", db_err)
            # Tetap lanjut tanpa DB

        return jsonify({"student_id": sid, "name": name})
    except Exception as e:
        import traceback
        print("Register Error:", str(e))
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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

# ─── Admin Routes (Baseline) ─────────────────────────────────────────────
ADMIN_KEY = os.environ.get("ADMIN_KEY", "baseline2025")   # ← DIBEDA

def _check_admin(req):
    return req.args.get("key") == ADMIN_KEY

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
