"""Free weather helper — Open-Meteo, no API key. Falls back to dataset rainfall if offline."""
import requests
from config import OPEN_METEO_URL
MANDI_COORDS = {"Nashik":(20.0,73.8),"Lasalgaon":(20.1,74.2),"Indore":(22.7,75.9),"Mandsaur":(24.1,75.1),
 "Kanpur":(26.4,80.3),"Ludhiana":(30.9,75.9),"Rajkot":(22.3,70.8),"Ahmedabad":(23.0,72.6),
 "Bengaluru":(13.0,77.6),"Kolhapur":(16.7,74.2),"Nagpur":(21.1,79.1),"Delhi Azadpur":(28.7,77.2)}
def get_weather(mandi):
    lat, lon = MANDI_COORDS.get(mandi,(20.0,73.8))
    try:
        r = requests.get(OPEN_METEO_URL, params={"latitude":lat,"longitude":lon,"daily":"temperature_2m_max,precipitation_sum","forecast_days":7,"timezone":"Asia/Kolkata"}, timeout=6)
        r.raise_for_status(); d = r.json().get("daily",{})
        return {"source":"Open-Meteo (free, no key)","days":d.get("time",[]),"rain_mm":d.get("precipitation_sum",[]),"temp_max":d.get("temperature_2m_max",[])}
    except Exception as e:
        return {"source":"Offline fallback — dataset rainfall (no internet / API down)","error":str(e),"days":[],"rain_mm":[],"temp_max":[]}
