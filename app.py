"""
Baseline - Non Adaptive
Menggunakan fungsi get_random_question dari database
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import random
from database import init_db, get_random_question, get_conn, get_student, get_mastered_kcs, get_all_kc_states, get_random_question_by_topic

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

from database import get_student, get_all_kc_states, get_mastered_kcs

# ====================== TOPICS & PROGRESS ======================
@app.get("/api/student/<sid>")
def get_student_info(sid):
    student = get_student(sid)
    if not student:
        return jsonify({"error": "Siswa tidak ditemukan"}), 404
    return jsonify(student)

@app.get("/api/topics/<sid>")
def get_topics(sid):
    """BASELINE: Semua topik terbuka (tidak ada yang di-lock)"""
    try:
        mastered_kcs = get_mastered_kcs(sid)  # dari database.py
        
        topics = [
            {
                "id": "bilangan", 
                "label": "Bilangan", 
                "n_mastered": 0, 
                "n_total": 8, 
                "locked": False,      # ← PASTIKAN FALSE
                "completed": False
            },
            {
                "id": "operasi", 
                "label": "Operasi Bilangan", 
                "n_mastered": 0, 
                "n_total": 12, 
                "locked": False,
                "completed": False
            },
            {
                "id": "geometri", 
                "label": "Geometri", 
                "n_mastered": 0, 
                "n_total": 6, 
                "locked": False,
                "completed": False
            },
            {
                "id": "pengukuran", 
                "label": "Pengukuran", 
                "n_mastered": 0, 
                "n_total": 5, 
                "locked": False,
                "completed": False
            },
            {
                "id": "pola", 
                "label": "Pola & Aljabar", 
                "n_mastered": 0, 
                "n_total": 4, 
                "locked": False,
                "completed": False
            },
        ]
        
        # Update progress real dari database
        for t in topics:
            # Hitung berdasarkan KC yang sudah dimaster (opsional)
            t["n_mastered"] = sum(1 for kc in mastered_kcs if kc.lower().startswith(t["id"][:3]))
            t["completed"] = t["n_mastered"] >= t["n_total"] * 0.8
        
        return jsonify(topics)
        
    except Exception as e:
        print("Topics Error:", str(e))
        # Fallback: tetap return semua topik terbuka
        return jsonify([
            {"id": "bilangan", "label": "Bilangan", "n_mastered": 0, "n_total": 8, "locked": False, "completed": False},
            {"id": "operasi", "label": "Operasi Bilangan", "n_mastered": 0, "n_total": 12, "locked": False, "completed": False},
            {"id": "geometri", "label": "Geometri", "n_mastered": 0, "n_total": 6, "locked": False, "completed": False},
            {"id": "pengukuran", "label": "Pengukuran", "n_mastered": 0, "n_total": 5, "locked": False, "completed": False},
            {"id": "pola", "label": "Pola & Aljabar", "n_mastered": 0, "n_total": 4, "locked": False, "completed": False},
        ])

# ====================== KC LIST (untuk tampilan topik) ======================
@app.get("/api/kcs/<topic_id>/<sid>")
def get_kcs(topic_id, sid):
    """Baseline: Tampilkan KC sesuai topik"""
    try:
        # Mapping topic ke prefix KC (sesuaikan dengan data seed kamu)
        topic_prefix = {
            "bilangan": "KC-B",
            "operasi": "KC-O",
            "geometri": "KC-G",
            "pengukuran": "KC-P",
            "pola": "KC-A"
        }.get(topic_id, "KC-")

        with get_conn() as conn:
            rows = conn.execute("""
                SELECT 
                    id as kc_id,
                    name,
                    COALESCE((SELECT p_know FROM kc_states 
                              WHERE student_id=? AND kc_id=knowledge_components.id), 0.0) as p_know,
                    COALESCE((SELECT is_mastered FROM kc_states 
                              WHERE student_id=? AND kc_id=knowledge_components.id), 0) as is_mastered
                FROM knowledge_components 
                WHERE id LIKE ? 
                ORDER BY id
            """, (sid, sid, f"{topic_prefix}%")).fetchall()
        
        kcs = [dict(r) for r in rows]
        for kc in kcs:
            kc["p_know"] = float(kc.get("p_know", 0))
            kc["is_mastered"] = bool(kc.get("is_mastered", 0))
            kc["locked"] = False

        # Fallback kalau belum ada KC di topik tersebut
        if not kcs:
            kcs = [{
                "kc_id": f"{topic_prefix}01",
                "name": f"Materi {topic_id.title()} Dasar",
                "p_know": 0.0,
                "is_mastered": False,
                "locked": False
            }]
        
        return jsonify(kcs)
    except Exception as e:
        print("KC Error:", str(e))
        return jsonify([])

@app.get("/api/progress/<sid>")
def get_progress(sid):
    """Progress keseluruhan"""
    try:
        states = get_all_kc_states(sid)
        total = len(states)
        mastered = sum(1 for s in states.values() if s.get("is_mastered"))
        stars = 0  # bisa dihitung dari interactions
        return jsonify({
            "pct": round((mastered / total * 100) if total else 0),
            "mastered": mastered,
            "total": total,
            "stars": stars
        })
    except:
        return jsonify({"pct": 0, "mastered": 0, "total": 0, "stars": 0})

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

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
    """Baseline - Ambil soal random sesuai topik"""
    try:
        topic = request.args.get("topic")
        
        # Mapping topik ke prefix KC
        kc_prefix = None
        if topic:
            prefix_map = {
                "bilangan": "KC-B",
                "operasi": "KC-O",
                "geometri": "KC-G",
                "pengukuran": "KC-P",
                "pola": "KC-A"
            }
            kc_prefix = prefix_map.get(topic)

        # Ambil soal
        q = get_random_question_by_topic(kc_prefix)
        
        if not q:
            # Fallback soal sederhana
            q = {
                "id": 999,
                "kc_id": "default",
                "type": "pilgan",
                "q": "Berapa hasil 2 + 3?",
                "options": ["4", "5", "6", "7"],
                "answer": "5",
                "kc_name": "Materi Dasar"
            }
        
        return jsonify(q)

    except Exception as e:
        import traceback
        error_msg = str(e)
        print("=== NEXT QUESTION ERROR ===")
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({"error": error_msg}), 500

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
