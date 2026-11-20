"""Run the app:  python run.py   (NOT python app.py)
Opens http://127.0.0.1:5000 — Admin demo: admin@kisan.local / admin123
"""
import db
from app import app
if __name__ == "__main__":
    db.init_db()
    print("Kisan Mandi Bhav running at http://127.0.0.1:5000")
    print("Admin demo: admin@kisan.local / admin123   |   Farmer demo: ram@kisan.local / ram123")
    app.run(host="0.0.0.0", port=5000, debug=False)
