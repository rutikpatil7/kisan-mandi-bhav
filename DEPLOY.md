# Free Deployment Guide — Kisan Mandi Bhav

## 1. Netlify — ONLY static frontend (samajh lo!)
Netlify cannot run Python/Flask/ML. It hosts `frontend-static/index.html` only.
Steps: Netlify > Add new site > Import from Git / drag-drop `frontend-static/` folder > site live at `https://<name>.netlify.app`.
Then open the site, paste your backend URL, and Predict works via API.

## 2. Render (free, no card) — Backend
1. Push code to GitHub. 2. Render > New Web Service > pick repo. 3. Build: `pip install -r requirements.txt`, Start: `gunicorn --bind 0.0.0.0:$PORT app:app` (render.yaml already has this). 4. Copy the `https://...onrender.com` URL into the Netlify frontend.
Note: free Render sleeps after ~15 min idle; first load takes ~30-60 sec.

## 3. Google Cloud Run (free tier) — Backend
```bash
gcloud run deploy kisan-mandi-bhav --source . --region us-central1 --allow-unauthenticated
```
Free tier: 2M requests/month, 180,000 vCPU-seconds, 360,000 GiB-seconds (always-free allowance). Needs a billing account/card even in free tier — money is charged only above the free limit. Copy the Cloud Run URL into the Netlify frontend.

## 4. Local demo (viva — safest)
`python run.py` on your laptop, open http://127.0.0.1:5000. No internet needed except weather (falls back to dataset rainfall offline).
