"""Kisan Mandi Bhav — Crop Price Prediction (Flask, 100% free stack).
Run with: python run.py   (NOT python app.py)
Dataset: realistic SYNTHETIC data modelled on Agmarknet/eNAM patterns — NOT live Agmarknet data.
"""
import os, json, math
import numpy as np, pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import db, config
from weather import get_weather

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
BASE = os.path.dirname(os.path.abspath(__file__))
DF = pd.read_csv(os.path.join(BASE,"data","crop_prices.csv"), parse_dates=["date"])
CROPS = sorted(DF.crop.unique()); MANDIS = sorted(DF.mandi.unique())
MSP = DF.groupby("crop")["msp_rs_per_quintal"].max().to_dict()
try:
    BUNDLE = joblib.load(os.path.join(BASE,"models","best_model.pkl"))
    MODEL = BUNDLE["model"]; FEATS = BUNDLE["features"]; BEST_NAME = BUNDLE.get("best_name","Ridge")
except Exception as e:
    MODEL=None; FEATS=[]; BEST_NAME="not trained yet"; print("Model not loaded:",e)
try:
    METRICS = json.load(open(os.path.join(BASE,"outputs","metrics.json")))
except Exception:
    METRICS={"best_model":BEST_NAME,"metrics":{}}
MAPE = METRICS.get("metrics",{}).get(METRICS.get("best_model",""),{}).get("MAPE",7.0)

def forecast(crop, mandi, weeks=4):
    """Iterative weekly forecast using last known prices as lags."""
    s = DF[(DF.crop==crop)&(DF.mandi==mandi)].sort_values("date")
    if len(s)<10: return []
    hist = list(s.modal_price.values.astype(float))
    last_date = s.date.max()
    rain = float(s.rainfall_mm.tail(8).mean()); arr = float(s.arrivals_quintals.tail(8).mean())
    msp = int(MSP.get(crop,0) or 0)
    out=[]
    for w in range(1, weeks+1):
        target = last_date + pd.Timedelta(weeks=w)
        lag1=hist[-1]; lag7=hist[-7] if len(hist)>=7 else hist[0]; lag30=hist[-4] if len(hist)>=4 else hist[0]
        roll7=float(np.mean(hist[-2:])); roll30=float(np.mean(hist[-4:]))
        row={"lag_1":lag1,"lag_7":lag7,"lag_30":lag30,"roll_7":roll7,"roll_30":roll30,
             "rainfall_mm":rain,"arrivals_quintals":arr,"month":int(target.month),
             "month_sin":float(np.sin(2*np.pi*target.month/12)),"month_cos":float(np.cos(2*np.pi*target.month/12)),
             "crop_code":BUNDLE["crop_map"][crop],"mandi_code":BUNDLE["mandi_map"][mandi],"msp_rs_per_quintal":msp}
        x=pd.DataFrame([[row[f] for f in FEATS]], columns=FEATS)
        pred=float(MODEL.predict(x)[0]) if MODEL is not None else lag1
        pred=max(100, round(pred))
        hist.append(pred)
        out.append({"week":w,"date":target.strftime("%Y-%m-%d"),"days":w*7,"price":pred,
                    "low":round(pred*(1-MAPE/100)),"high":round(pred*(1+MAPE/100))})
    return out

def current_user():
    if "user_id" not in session: return None
    conn=db.get_conn(); u=conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone(); conn.close()
    return u

@app.route("/")
def home():
    conn=db.get_conn()
    kpi=dict(crops=len(CROPS), mandis=len(MANDIS), rows=len(DF),
             predictions=conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0],
             farmers=conn.execute("SELECT COUNT(*) FROM users WHERE role='farmer'").fetchone()[0])
    conn.close()
    latest=DF.sort_values("date").groupby("crop").tail(1)[["crop","mandi","modal_price","date"]].to_dict("records")
    return render_template("home.html", kpi=kpi, latest=latest, metrics=METRICS, user=current_user(), crops=CROPS, mandis=MANDIS)

@app.route("/predict", methods=["GET","POST"])
def predict():
    result=None; crop=request.values.get("crop","Onion"); mandi=request.values.get("mandi","Nashik")
    if request.method=="POST":
        fc=forecast(crop, mandi, weeks=5)
        by={f["days"]:f for f in fc}
        p7=by.get(7); p15=by.get(14); p30=by.get(28)
        cur=float(DF[(DF.crop==crop)&(DF.mandi==mandi)].sort_values("date").modal_price.iloc[-1])
        change30=((p30["price"]-cur)/cur*100) if p30 else 0
        advice=("WAIT — price may rise, selling later could earn more." if change30>5 else
                "SELL NOW — price may fall, selling now is safer." if change30<-5 else
                "HOLD / SELL — price looks stable in next 30 days.")
        advice_hi=("RUKO — bhav badh sakta hai." if change30>5 else "ABHI BECHO — bhav gir sakta hai." if change30<-5 else "Bhav stable hai — bech sakte ho.")
        result=dict(crop=crop, mandi=mandi, current=round(cur), p7=p7, p15=p15, p30=p30, change30=round(change30,1), advice=advice, advice_hi=advice_hi, forecast=fc)
        if "user_id" in session:
            conn=db.get_conn(); conn.execute("INSERT INTO predictions(user_id,crop,mandi,target_date,predicted_price,horizon_days) VALUES(?,?,?,?,?,?)",(session["user_id"],crop,mandi,p30["date"],p30["price"],30)); conn.commit(); conn.close()
    hist=DF[(DF.crop==crop)&(DF.mandi==mandi)].sort_values("date").tail(52)
    chart={"dates":hist.date.dt.strftime("%Y-%m-%d").tolist(),"prices":hist.modal_price.tolist()}
    return render_template("predict.html", crops=CROPS, mandis=MANDIS, crop=crop, mandi=mandi, result=result, chart=chart, user=current_user())

@app.route("/mandi", methods=["GET","POST"])
def mandi_finder():
    crop=request.values.get("crop","Onion"); quintals=float(request.values.get("quintals",10) or 10)
    transport=float(request.values.get("transport",100) or 100)  # Rs per quintal
    rows=[]
    for m in MANDIS:
        fc=forecast(crop,m,weeks=2); p=fc[1]["price"] if len(fc)>1 else 0
        cur=float(DF[(DF.crop==crop)&(DF.mandi==m)].sort_values("date").modal_price.iloc[-1])
        rows.append({"mandi":m,"current":round(cur),"predicted_15d":p,"net_per_quintal":round(p-transport),"total_profit":round((p-transport)*quintals)})
    rows.sort(key=lambda r:-r["total_profit"])
    return render_template("mandi.html", crops=CROPS, crop=crop, quintals=quintals, transport=transport, rows=rows, user=current_user())

@app.route("/profit", methods=["GET","POST"])
def profit():
    result=None
    if request.method=="POST":
        q=float(request.form.get("quintals",10)); price=float(request.form.get("price",2000))
        trans=float(request.form.get("transport",1000)); other=float(request.form.get("other",500))
        gross=q*price; total_cost=trans+other; net=gross-total_cost
        result=dict(quintals=q,price=price,gross=round(gross),cost=round(total_cost),net=round(net),per_quintal=round(net/q) if q else 0)
    return render_template("profit.html", result=result, crops=CROPS, user=current_user())

@app.route("/msp")
def msp_page():
    rows=[]
    for crop in CROPS:
        s=DF[DF.crop==crop]; latest=s.sort_values("date").groupby("mandi").tail(1)
        avg=float(latest.modal_price.mean()); msp=int(MSP.get(crop,0) or 0)
        rows.append({"crop":crop,"avg_price":round(avg),"msp":msp,"diff":round(avg-msp) if msp else None,"above":(avg>msp) if msp else None})
    return render_template("msp.html", rows=rows, user=current_user())

@app.route("/recommend")
def recommend():
    recs=[]
    for crop in CROPS:
        s=DF[DF.crop==crop].sort_values("date")
        recent=s.tail(26).modal_price.mean(); prev=s.iloc[-52:-26].modal_price.mean() if len(s)>=52 else recent
        trend=(recent/prev-1)*100 if prev else 0
        vol=float(s.tail(52).modal_price.pct_change().std()*100)
        score=round(trend - vol*0.3,1)
        recs.append({"crop":crop,"avg_price":round(recent),"trend_pct":round(trend,1),"volatility":round(vol,1),"score":score,"msp":int(MSP.get(crop,0) or 0)})
    recs.sort(key=lambda r:-r["score"])
    return render_template("recommend.html", recs=recs, user=current_user())

@app.route("/weather")
def weather_page():
    mandi=request.args.get("mandi","Nashik")
    return render_template("weather.html", mandis=MANDIS, mandi=mandi, w=get_weather(mandi), user=current_user())

@app.route("/map")
def map_page():
    pts=DF.groupby(["mandi","state","latitude","longitude"])["modal_price"].mean().reset_index().to_dict("records")
    return render_template("map.html", points=pts, user=current_user())

@app.route("/alerts", methods=["GET","POST"])
def alerts():
    if request.method=="POST":
        crop=request.form.get("crop","Onion"); mandi=request.form.get("mandi","Nashik")
        target=float(request.form.get("target_price",2500)); channel=request.form.get("channel","email")
        os.makedirs(os.path.join(BASE,"alerts","outbox"),exist_ok=True)
        import datetime
        fn=os.path.join(BASE,"alerts","outbox",f"alert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(fn,"w") as f: f.write(f"ALERT (FREE demo outbox — no SMS/call sent)\nCrop: {crop}\nMandi: {mandi}\nTarget price: Rs {target}/quintal\nChannel: {channel} (Gmail SMTP / Telegram — configure via env vars, no credentials in code)\n")
        if "user_id" in session:
            conn=db.get_conn(); conn.execute("INSERT INTO alerts(user_id,crop,mandi,target_price,channel) VALUES(?,?,?,?,?)",(session["user_id"],crop,mandi,target,channel)); conn.commit(); conn.close()
        flash(f"Alert saved! File: {os.path.basename(fn)} — free demo outbox, no paid SMS used.")
        return redirect(url_for("alerts"))
    return render_template("alerts.html", crops=CROPS, mandis=MANDIS, user=current_user())

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=db.get_conn(); u=conn.execute("SELECT * FROM users WHERE email=?", (request.form.get("email"),)).fetchone(); conn.close()
        if u and check_password_hash(u["password_hash"], request.form.get("password","")):
            session["user_id"]=u["id"]; session["role"]=u["role"]; flash(f"Welcome, {u['name']}!")
            return redirect(url_for("admin") if u["role"]=="admin" else url_for("home"))
        flash("Wrong email or password.")
    return render_template("login.html", user=current_user())

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        conn=db.get_conn()
        try:
            conn.execute("INSERT INTO users(name,email,password_hash,role,phone,state) VALUES(?,?,?,?,?,?)",
                (request.form.get("name"), request.form.get("email"), generate_password_hash(request.form.get("password","")), "farmer", request.form.get("phone",""), request.form.get("state","")))
            conn.commit(); flash("Registered! Please login."); return redirect(url_for("login"))
        except Exception: flash("Email already registered.")
        finally: conn.close()
    return render_template("register.html", user=current_user())

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))

@app.route("/admin", methods=["GET","POST"])
def admin():
    u=current_user()
    if not u or u["role"]!="admin": flash("Admin login required. Demo: admin@kisan.local / admin123"); return redirect(url_for("login"))
    conn=db.get_conn()
    if request.method=="POST" and request.form.get("action")=="delete_price":
        conn.execute("DELETE FROM prices WHERE id=?", (request.form.get("price_id"),)); conn.commit(); flash("Price row deleted.")
    if request.method=="POST" and request.form.get("action")=="add_price":
        conn.execute("INSERT INTO prices(date,crop,mandi,state,min_price,max_price,modal_price,arrivals_quintals,rainfall_mm,msp_rs_per_quintal) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (request.form.get("date"),request.form.get("crop"),request.form.get("mandi"),request.form.get("state",""),request.form.get("min_price"),request.form.get("max_price"),request.form.get("modal_price"),request.form.get("arrivals",1000),request.form.get("rainfall",5),request.form.get("msp",0))); conn.commit(); flash("Price added.")
    kpi=dict(farmers=conn.execute("SELECT COUNT(*) FROM users WHERE role='farmer'").fetchone()[0],
             predictions=conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0],
             alerts=conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],
             prices=conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0])
    farmers=conn.execute("SELECT id,name,email,state FROM users WHERE role='farmer'").fetchall()
    prices=conn.execute("SELECT * FROM prices ORDER BY date DESC LIMIT 20").fetchall()
    preds=conn.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("admin.html", kpi=kpi, farmers=farmers, prices=prices, preds=preds, crops=CROPS, mandis=MANDIS, metrics=METRICS, user=u)

@app.route("/api/predict")
def api_predict():
    crop=request.args.get("crop","Onion"); mandi=request.args.get("mandi","Nashik")
    return jsonify({"crop":crop,"mandi":mandi,"forecast":forecast(crop,mandi,weeks=4),"model":BEST_NAME})

@app.route("/api/health")
def health():
    return jsonify({"status":"ok","model":BEST_NAME,"crops":len(CROPS),"mandis":len(MANDIS),"rows":len(DF)})

if __name__=="__main__":
    db.init_db(); app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
