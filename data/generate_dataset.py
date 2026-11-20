"""Generate realistic SYNTHETIC mandi price data modelled on Agmarknet/eNAM patterns.
NOT live Agmarknet data. Weekly modal prices, 2022-01 to 2025-10.
Seeded (42) for reproducibility. Run: python data/generate_dataset.py
"""
import numpy as np, pandas as pd, os
np.random.seed(42)
CROPS = {
    "Onion":   dict(base=1850, msp=0,    season_peak=11, vol=0.28, rain_sens=-0.25),
    "Tomato":  dict(base=1250, msp=0,    season_peak=7,  vol=0.38, rain_sens=-0.35),
    "Potato":  dict(base=1450, msp=0,    season_peak=2,  vol=0.20, rain_sens=-0.10),
    "Wheat":   dict(base=2350, msp=2275, season_peak=4,  vol=0.08, rain_sens=0.05),
    "Rice/Paddy": dict(base=2300, msp=2183, season_peak=10, vol=0.10, rain_sens=0.08),
    "Soybean": dict(base=4950, msp=4892, season_peak=10, vol=0.16, rain_sens=0.12),
    "Cotton":  dict(base=6650, msp=6620, season_peak=11, vol=0.14, rain_sens=0.10),
    "Chilli":  dict(base=8800, msp=0,    season_peak=3,  vol=0.26, rain_sens=-0.15),
}
MANDIS = [
    ("Nashik","Maharashtra",20.0,73.8),("Lasalgaon","Maharashtra",20.1,74.2),
    ("Indore","Madhya Pradesh",22.7,75.9),("Mandsaur","Madhya Pradesh",24.1,75.1),
    ("Kanpur","Uttar Pradesh",26.4,80.3),("Ludhiana","Punjab",30.9,75.9),
    ("Rajkot","Gujarat",22.3,70.8),("Ahmedabad","Gujarat",23.0,72.6),
    ("Bengaluru","Karnataka",13.0,77.6),("Kolhapur","Maharashtra",16.7,74.2),
    ("Nagpur","Maharashtra",21.1,79.1),("Delhi Azadpur","Delhi",28.7,77.2),
]
# mandi price premium (transport / demand)
PREMIUM = {"Nashik":0.98,"Lasalgaon":0.96,"Indore":1.0,"Mandsaur":0.99,"Kanpur":1.03,
 "Ludhiana":1.04,"Rajkot":1.01,"Ahmedabad":1.02,"Bengaluru":1.08,"Kolhapur":1.0,
 "Nagpur":1.01,"Delhi Azadpur":1.10}
dates = pd.date_range("2022-01-03","2025-10-27",freq="W-MON")
rows=[]
for crop, c in CROPS.items():
    for mandi, state, lat, lon in MANDIS:
        # random walk with seasonality, trend, rainfall effect
        price = c["base"]*PREMIUM[mandi]
        for i, d in enumerate(dates):
            month=d.month
            seasonal = 1 + 0.18*np.sin(2*np.pi*(month-c["season_peak"])/12) + 0.07*np.sin(2*np.pi*(month/12)*2)
            trend = 1 + 0.045*(d.year-2022) + 0.003*i/52  # ~4-5% yearly inflation
            # rainfall: monsoon Jun-Sep high, winter low
            rain = max(0, np.random.normal(18 if month in (6,7,8,9) else 4 if month in (11,12,1) else 8, 9))
            rain_effect = 1 + c["rain_sens"]*(rain-10)/60
            shock = np.random.normal(0, c["vol"]*0.35)
            # occasional spike (e.g. onion shortage)
            if np.random.rand()<0.012: shock += np.random.choice([0.25,0.35])
            price = price*0.92 + (c["base"]*PREMIUM[mandi]*seasonal*trend*rain_effect)*0.08
            modal = max(200, price*(1+shock))
            modal = round(modal/10)*10
            mn = round(modal*np.random.uniform(0.88,0.95)/10)*10
            mx = round(modal*np.random.uniform(1.05,1.14)/10)*10
            arrivals = int(max(20, np.random.normal(1200,450)*(1+0.3*np.sin(2*np.pi*(month-c["season_peak"])/12))))
            rows.append(dict(date=d.strftime("%Y-%m-%d"), crop=crop, mandi=mandi, state=state,
                latitude=lat, longitude=lon, min_price=mn, max_price=mx, modal_price=modal,
                arrivals_quintals=arrivals, rainfall_mm=round(float(rain),1),
                month=month, season="Kharif" if month in (6,7,8,9,10) else "Rabi" if month in (11,12,1,2,3) else "Summer",
                msp_rs_per_quintal=c["msp"]))
df=pd.DataFrame(rows)
os.makedirs(os.path.dirname(__file__),exist_ok=True)
df.to_csv(os.path.join(os.path.dirname(__file__),"crop_prices.csv"),index=False)
print(f"rows={len(df)} crops={df.crop.nunique()} mandis={df.mandi.nunique()} range={df.date.min()} to {df.date.max()}")
print(df.groupby('crop')['modal_price'].mean().round(0).to_dict())
