# 🌾 Kisan Mandi Bhav — Crop Price Prediction

**MCA 4th Semester Internship Project | Data Science | 100% FREE stack**

Indian farmers don't know future mandi price, sell at the wrong time, and middlemen profit. This project predicts mandi prices for 7 / 15 / 30 days, finds the best mandi, compares price with MSP, and advises **Sell Now vs Wait** — in simple Hinglish, farmer-friendly.

## ⚠️ Honest data note (viva me yehi bolna)
Dataset is **realistic SYNTHETIC data modelled on Agmarknet / eNAM patterns** (weekly modal prices, 2022-01 to 2025-10, 19,200 rows, 8 crops, 12 mandis). **It is NOT live Agmarknet data.** Generate it again any time: `python data/generate_dataset.py` (seeded, reproducible).

## What is inside
- **Dataset:** `data/crop_prices.csv` — 19,200 rows, 8 crops (Onion, Tomato, Potato, Wheat, Rice/Paddy, Soybean, Cotton, Chilli), 12 mandis (Nashik, Lasalgaon, Indore, Mandsaur, Kanpur, Ludhiana, Rajkot, Ahmedabad, Bengaluru, Kolhapur, Nagpur, Delhi Azadpur), modal/min/max price ₹/quintal, arrivals, rainfall, MSP, season.
- **ML:** `scripts/train_models.py` — lag 1/7/30, rolling mean 7/30, month, rainfall, arrivals. Time-based split (train < 2025-01-01, test ≥ 2025-01-01). 5 models + naive baseline compared. Best model saved to `models/best_model.pkl`. Real metrics in `outputs/metrics.json` — see below, never invent other numbers.
- **Flask app:** Farmer register/login, Admin login, Predict, Best Mandi Finder, Profit Calculator, MSP comparison, Crop Recommendation, Free Alerts (Gmail SMTP / Telegram config via env vars + demo outbox in `alerts/outbox/`), Weather (Open-Meteo, free, no key), Map (Leaflet + OpenStreetMap, no Google key), Admin dashboard with add/edit/delete.
- **Excel + Power BI:** `excel/Kisan_Mandi_Bhav_Dashboard.xlsx`, `powerbi/powerbi_data.csv` + DAX measures + guide. **No .pbix file** — .pbix can only be made inside Power BI Desktop, guide is included.
- **Docs:** Internship Report (docx + PDF), Presentation (pptx), `VIVA_DEMO_SCRIPT.md`.

## How to run (laptop)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python data/generate_dataset.py
python scripts/train_models.py
python run.py
```
Open **http://127.0.0.1:5000**
- Admin demo: `admin@kisan.local` / `admin123`
- Farmer demo: `ram@kisan.local` / `ram123`

**Run command is `python run.py` — NOT `python app.py`.**

## Database
Default is **SQLite (`app.db`)** — runs without XAMPP, and this is what was tested. MySQL schema is in `schema.sql`; set `DB_TYPE=mysql` + MySQL env vars to use it. **MySQL was NOT live-tested — check it on XAMPP before viva** and fall back to SQLite demo if it fails.

## Free hosting — Netlify samajh lo (IMPORTANT)
**Netlify sirf static frontend host karta hai. Flask + ML backend Netlify par NAHI chalega.**
- Frontend (static demo): `frontend-static/` → Netlify (free, `netlify.toml` included).
- Backend (Flask + ML): free on **Render** (`render.yaml` included) or **Google Cloud Run** (free tier: 2M requests/month). Deploy backend first, then put its URL in the Netlify frontend — frontend calls `YOUR_BACKEND_URL/api/predict`.
- Google Cloud Run guide: `DEPLOY.md`. Cloud Run needs a billing account/card even in free tier; Render free tier needs no card but sleeps after inactivity.

## 100% FREE — kya paid nahi hai
No OpenAI/ChatGPT API, no Twilio, no Google Maps key, no paid weather API. Models: Ridge, Random Forest, GradientBoosting, XGBoost, LightGBM (all open-source). Weather: Open-Meteo (no key). Map: Leaflet + OpenStreetMap. Alerts: Gmail SMTP (free) / Telegram Bot (free) / demo outbox file.

## Results (REAL, from the actual training run — see outputs/metrics.json)
- Best model: **Ridge** — R² 0.9759, RMSE ₹481.61/quintal, MAE ₹289.1, MAPE 7.05% (test set, time-based split: train < 2025-01-01, test ≥ 2025-01-01)
- Ridge: R² 0.9759, RMSE ₹481.61, MAE ₹289.1, MAPE 7.05%
- RandomForest: R² 0.9752, RMSE ₹488.07, MAE ₹285.69, MAPE 6.73%
- GradientBoosting: R² 0.9757, RMSE ₹483.28, MAE ₹282.21, MAPE 6.7%
- XGBoost: R² 0.9743, RMSE ₹496.81, MAE ₹284.39, MAPE 6.61%
- LightGBM: R² 0.9746, RMSE ₹493.84, MAE ₹283.47, MAPE 6.61%
- Naive_Lag1_Baseline: R² 0.9619, RMSE ₹605.16, MAE ₹356.29, MAPE 8.51%
- Best model, R², RMSE, MAE, MAPE are in `outputs/metrics.json` and in the Report.

## Limitations (viva me honest raho)
- Synthetic data, not live Agmarknet — real deployment needs live Agmarknet API/data pipeline.
- Weekly prices; daily volatility is smoothed. Lag features dominate — R² is high partly because last week's price predicts this week well.
- Weather is Open-Meteo forecast / dataset rainfall fallback; no paid weather source.
- Alerts in demo outbox are files, not real SMS — real SMS needs a paid gateway, which this project deliberately avoids.
