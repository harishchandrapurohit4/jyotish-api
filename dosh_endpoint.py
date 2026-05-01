"""
Dosh Detection Endpoint - Fixed version
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
import swisseph as swe

from astro_engine import init_ephem, get_all_planets, get_lagna, get_planet_house
from dosh_detection_engine import detect_all_doshas


class DoshCheckRequest(BaseModel):
    dob: str = Field(..., example="1990-08-15")
    tob: str = Field(..., example="10:30")
    lat: float = Field(..., example=28.6139)
    lon: float = Field(..., example=77.2090)
    tz: float = Field(5.5, example=5.5)
    name: Optional[str] = Field(None, example="Test")


def install_endpoint(app):
    @app.post("/dosh-check")
    def dosh_check_endpoint(data: DoshCheckRequest):
        try:
            EPHEM_PATH = os.environ.get("EPHEM_PATH", "")
            init_ephem(EPHEM_PATH)
            
            # Build JD using swisseph directly (matches other endpoints)
            local_dt = datetime.strptime(f"{data.dob} {data.tob}", "%Y-%m-%d %H:%M")
            utc_dt = local_dt - timedelta(hours=data.tz)
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
            
            # Get planets and lagna
            planets_raw = get_all_planets(jd)
            lagna = get_lagna(jd, data.lat, data.lon)
            
            # Add house numbers
            planets_with_houses = {}
            for name, p in planets_raw.items():
                house = get_planet_house(p["longitude"], lagna["longitude"])
                planets_with_houses[name] = {**p, "house": house}
            
            result = detect_all_doshas(planets_with_houses, lagna)
            
            if data.name:
                result["name"] = data.name
            
            result["birth_details"] = {
                "dob": data.dob, "tob": data.tob,
                "lat": data.lat, "lon": data.lon, "tz": data.tz,
            }
            
            return result
        except Exception as e:
            import traceback
            raise HTTPException(500, f"Dosh error: {str(e)} | {traceback.format_exc()[:500]}")
    
    print("[OK] /dosh-check endpoint registered")
