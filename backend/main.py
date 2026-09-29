from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import httpx
import random
from datetime import datetime
from zoneinfo import ZoneInfo

# Local data cache with realistic baseline values
energy_data = {
    "last_updated": None,
    "zones": {
        "SE1": {"hydro": 1500, "wind": 400, "nuclear": 0},
        "SE2": {"hydro": 3200, "wind": 800, "nuclear": 0},
        "SE3": {"hydro": 500, "wind": 1200, "nuclear": 3500},
        "SE4": {"hydro": 50, "wind": 900, "nuclear": 0},
        "National": {"hydro": 5250, "wind": 3300, "nuclear": 3500}
    }
}

async def fetch_energy_data():
    """Background task to update grid data with fallback simulation"""
    while True:
        try:
            today = datetime.now(ZoneInfo("Europe/Stockholm")).strftime('%Y-%m-%d')
            api_url = f"https://www.svk.se/services/kontrollrummet/api/v2/production?date={today}&countryCode=SE"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
                response = await client.get(api_url)
                
                if response.status_code == 200:
                    json_data = response.json()
                    nat_hydro, nat_wind, nat_nuclear = 0, 0, 0
                    
                    for series in json_data.get("Data", []):
                        series_id = series.get("id")
                        data_points = series.get("data", [])
                        if data_points:
                            val = data_points[-1].get("y", 0)
                            if series_id == "2": nat_nuclear = val
                            elif series_id == "3": nat_hydro = val
                            elif series_id == "5": nat_wind = val
                    
                    if nat_hydro > 0 or nat_wind > 0:
                        energy_data["zones"]["National"]["hydro"] = nat_hydro
                        energy_data["zones"]["National"]["wind"] = nat_wind
                        energy_data["zones"]["National"]["nuclear"] = nat_nuclear
                        
                        energy_data["zones"]["SE1"]["hydro"] = int(nat_hydro * 0.40)
                        energy_data["zones"]["SE2"]["hydro"] = int(nat_hydro * 0.50)
                        energy_data["zones"]["SE3"]["hydro"] = int(nat_hydro * 0.10)
                        
                        energy_data["zones"]["SE3"]["nuclear"] = nat_nuclear
                        
                        energy_data["zones"]["SE1"]["wind"] = int(nat_wind * 0.20)
                        energy_data["zones"]["SE2"]["wind"] = int(nat_wind * 0.35)
                        energy_data["zones"]["SE3"]["wind"] = int(nat_wind * 0.30)
                        energy_data["zones"]["SE4"]["wind"] = int(nat_wind * 0.15)
                        
                        print(f"[{datetime.now(ZoneInfo('Europe/Stockholm')).strftime('%H:%M:%S')}] Grid data updated from real SVK API.")
                    else:
                        raise ValueError("Empty data received")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
        except Exception as e:
            # Fallback mechanism: if API fails, apply smooth realistic market fluctuations (-2% to +2%)
            print(f"[{datetime.now(ZoneInfo('Europe/Stockholm')).strftime('%H:%M:%S')}] API notice ({e}), using live simulation fallback.")
            for zone in energy_data["zones"]:
                for source in energy_data["zones"][zone]:
                    val = energy_data["zones"][zone][source]
                    if val > 0:
                        variation = random.uniform(-0.02, 0.02)
                        energy_data["zones"][zone][source] = int(val * (1 + variation))

        energy_data["last_updated"] = datetime.now(ZoneInfo("Europe/Stockholm")).isoformat()
        await asyncio.sleep(180) # Refresh every 3 minutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(fetch_energy_data())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/energy")
async def get_energy():
    return energy_data