import sqlite3, os, csv
from werkzeug.security import generate_password_hash
import config
def get_conn():
    conn = sqlite3.connect(config.SQLITE_PATH); conn.row_factory = sqlite3.Row; return conn
def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password_hash TEXT, role TEXT DEFAULT 'farmer', phone TEXT, state TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS prices(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, crop TEXT, mandi TEXT, state TEXT, min_price INTEGER, max_price INTEGER, modal_price INTEGER, arrivals_quintals INTEGER, rainfall_mm REAL, msp_rs_per_quintal INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, crop TEXT, mandi TEXT, target_date TEXT, predicted_price REAL, horizon_days INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, crop TEXT, mandi TEXT, target_price REAL, channel TEXT, status TEXT DEFAULT 'saved', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    # seed admin + demo farmer
    if not c.execute("SELECT 1 FROM users WHERE email='admin@kisan.local'").fetchone():
        c.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)", ("Admin","admin@kisan.local",generate_password_hash("admin123"),"admin"))
    if not c.execute("SELECT 1 FROM users WHERE email='ram@kisan.local'").fetchone():
        c.execute("INSERT INTO users(name,email,password_hash,role,state) VALUES(?,?,?,?,?)", ("Ram Patil","ram@kisan.local",generate_password_hash("ram123"),"farmer","Maharashtra"))
    # seed prices from CSV once
    if c.execute("SELECT COUNT(*) FROM prices").fetchone()[0]==0:
        path=os.path.join(os.path.dirname(__file__),"data","crop_prices.csv")
        with open(path, newline="", encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
            c.executemany("INSERT INTO prices(date,crop,mandi,state,min_price,max_price,modal_price,arrivals_quintals,rainfall_mm,msp_rs_per_quintal) VALUES(?,?,?,?,?,?,?,?,?,?)",
                [(r["date"],r["crop"],r["mandi"],r["state"],r["min_price"],r["max_price"],r["modal_price"],r["arrivals_quintals"],r["rainfall_mm"],r["msp_rs_per_quintal"]) for r in rows])
        print(f"Seeded {len(rows)} price rows")
    conn.commit(); conn.close()
if __name__=="__main__":
    init_db(); print("DB ready:", config.SQLITE_PATH)
