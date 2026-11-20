# VIVA DEMO SCRIPT — Kisan Mandi Bhav (Crop Price Prediction)

**Time: ~10 minutes. Run `python run.py` BEFORE the viva. Open http://127.0.0.1:5000.**

## 1. Opening (1 min) — say this
"Sir/Ma'am, mera project Kisan Mandi Bhav hai. India me kisan ko pata nahi hota kal uski fasal ka mandi me kya bhav milega, isliye wo galat time par bech deta hai. Mera system 7, 15 aur 30 din ka bhav predict karta hai, best mandi batata hai, aur Sell Now ya Wait ki salah deta hai."

## 2. Home page (1 min)
Show KPI cards (8 crops, 12 mandis, 19,200 records), latest prices table, and the model line (best model + real R²/RMSE from outputs/metrics.json — read the numbers from the screen, don't memorise a different number).

## 3. Predict demo (3 min) — the main demo
Click Predict > Crop: **Onion**, Mandi: **Nashik** > Predict.
Say: "Current price ye hai, 7 din baad ye, 15 din baad ye, 30 din baad ye — range ke saath. Agar 30-day change +5% se zyada hai to system 'Wait' bolega, -5% se kam hai to 'Sell Now'."
Scroll to the 52-week trend chart.

## 4. Best Mandi + Profit (2 min)
Best Mandi: Onion, 10 quintals, transport ₹100/quintal > Compare. Say the top mandi name and total profit from the screen.
Profit Calculator: 10 quintals × ₹2000, transport ₹1000, other ₹500 > Calculate > read net profit.

## 5. MSP + Crop Advice + Alerts (2 min)
MSP page: show which crops are above/below MSP. Crop Advice: top recommended crop.
Alerts: save one alert (Onion, Nashik, ₹2500, Email) and say: "Alert free hai — Gmail/Telegram se, koi Twilio ya paid SMS nahi. Demo me alert `alerts/outbox/` me file ke roop me save hota hai."

## 6. Admin (1 min)
Login: admin@kisan.local / admin123. Show KPI cards, farmers list, Add Price Row, delete one demo row if asked.

## 7. Closing — models & honesty (1 min)
" Maine 5 models compare kiye — Ridge, Random Forest, GradientBoosting, XGBoost, LightGBM — plus ek naive baseline. Time-based split use kiya, train 2025 se pehle, test 2025 ke baad. Best model aur metrics `outputs/metrics.json` me hain."

## ❌ What NOT to claim
- Do NOT say data is live Agmarknet data. Say: "Synthetic data hai, Agmarknet pattern par banaya hai."
- Do NOT say Netlify hosts the full Flask app. Say: "Netlify sirf static frontend host karta hai, backend Render / Cloud Run par free me hai."
- Do NOT say alerts send real SMS. Say: "Free email/Telegram + demo outbox, no paid SMS."
- Do NOT say MySQL was live-tested. Say: "SQLite test kiya hai, MySQL XAMPP par check karna hai, schema.sql diya hai."
- Do NOT claim a .pbix file exists. Say: "Power BI guide diya hai, .pbix Power BI Desktop me banega."
- Do NOT invent R²/RMSE numbers — read them from `outputs/metrics.json` / the home page.

## If something fails in viva
- App won't start → `python run.py` again, check port 5000 free.
- Weather shows offline → say "Open-Meteo offline hai, dataset rainfall fallback chal raha hai."
- MySQL error → use SQLite demo (default), it needs no XAMPP.
