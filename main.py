"""
JyotishRishi Astrology API - Final Updated Version
FastAPI + Swiss Ephemeris (pyswisseph)
Fixes: CORS, City Search Blocking, Lat/Lon Updates
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os
import requests

# Importing your logic from astro_engine
from astro_engine import (
    get_ritu_ayan,
    get_guli_yamghant, get_abhijit, DISHA_SHOOL, TITHI_DEITY,
    get_vikram_samvat,
    calculate_ashtakoot,
    init_ephem, get_julian_day, local_to_ut, get_all_planets, get_lagna,
    get_house_cusps, get_planet_house, get_vimshottari_dasha,
    check_mangal_dosha, get_tithi, get_yoga, get_karana,
    get_sunrise_sunset,
)

# Initialize Ephemeris Path
EPHEM_PATH = os.environ.get('EPHEM_PATH', '')
init_ephem(EPHEM_PATH)

app = FastAPI(title='JyotishRishi Astrology API', version='1.1.0')

# --- CRITICAL: CORS FIX FOR MACBOOK/CHROME ---
# Yahan '*' ki jagah apne domain ko allow karna zyada secure hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class BirthData(BaseModel):
    dob: str = Field(..., example='1990-08-15')
    tob: str = Field(..., example='10:30')
    lat: float = Field(..., example=28.6139)
    lon: float = Field(..., example=77.2090)
    tz: float = Field(5.5)
    name: Optional[str] = None

class PanchangRequest(BaseModel):
    date: str = Field(..., example='2026-04-05')
    lat: float = Field(..., example=28.6139)
    lon: float = Field(..., example=77.2090)
    tz: float = Field(5.5)

class MatchMakingRequest(BaseModel):
    boy: BirthData
    girl: BirthData

# --- Helper Functions ---
def parse_birth(data: BirthData):
    try:
        y, mo, d = map(int, data.dob.split('-'))
        h, mi = map(int, data.tob.split(':'))
    except:
        raise HTTPException(400, 'Invalid dob or tob format')
    y_ut, mo_ut, d_ut, h_ut = local_to_ut(y, mo, d, h, mi, data.tz)
    jd = get_julian_day(y_ut, mo_ut, d_ut, h_ut)
    birth_dt = datetime(y, mo, d, h, mi)
    return jd, birth_dt

# --- ROUTES ---

@app.get('/')
def root():
    return {
        'api': 'JyotishRishi Astrology API',
        'status': 'Active',
        'endpoints': ['/birth-details', '/kundali', '/panchang', '/match-making', '/city-search']
    }

@app.get('/health')
def health():
    return {'status': 'ok', 'engine': 'Swiss Ephemeris (Lahiri Ayanamsa)'}

# --- NEW: CITY SEARCH FIX (To prevent CSP Block) ---
@app.get('/city-search')
def search_city(q: str):
    """
    Proxy function to fetch location data from server-side.
    This bypasses browser CSP blocks and allows Lat/Lon updates.
    """
    if not q or len(q) < 3:
        return []
    
    # Nominatim URL - server-to-server call is NOT blocked by browser
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=5"
    headers = {'User-Agent': 'JyotishRishiApp/1.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        return {"error": "Search failed", "details": str(e)}

@app.post('/birth-details')
def birth_details(data: BirthData):
    jd, birth_dt = parse_birth(data)
    try:
        planets = get_all_planets(jd)
        lagna = get_lagna(jd, data.lat, data.lon)
        moon = planets['Moon']
        dasha = get_vimshottari_dasha(jd, moon['longitude'], birth_dt)
        return {
            'name': data.name, 'dob': data.dob, 'tob': data.tob,
            'place': {'lat': data.lat, 'lon': data.lon, 'tz': data.tz},
            'lagna': lagna, 'moon_nakshatra': moon['nakshatra'],
            'moon_rashi': moon['rashi'], 'planets': planets,
            'vimshottari_dasha': dasha
        }
    except Exception as e:
        raise HTTPException(500, f'Calculation error: {str(e)}')

@app.post('/kundali')
def kundali(data: BirthData):
    jd, birth_dt = parse_birth(data)
    try:
        planets = get_all_planets(jd)
        lagna = get_lagna(jd, data.lat, data.lon)
        house_cusps = get_house_cusps(jd, data.lat, data.lon)
        planets_with_houses = {}
        for name, p in planets.items():
            house = get_planet_house(p['longitude'], lagna['longitude'])
            planets_with_houses[name] = {**p, 'house': house}
        
        mars_house = planets_with_houses['Mars']['house']
        mangal = check_mangal_dosha(mars_house)
        moon = planets['Moon']
        dasha = get_vimshottari_dasha(jd, moon['longitude'], birth_dt)
        
        return {
            'name': data.name, 'dob': data.dob, 'tob': data.tob,
            'place': {'lat': data.lat, 'lon': data.lon, 'tz': data.tz},
            'lagna': lagna, 'planets': planets_with_houses,
            'house_cusps': house_cusps, 'mangal_dosha': mangal,
            'vimshottari_dasha': dasha
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/panchang')
def panchang(req: PanchangRequest):
    try:
        y, mo, d = map(int, req.date.split('-'))
        h_ut = 12.0 - req.tz
        jd = get_julian_day(y, mo, d, h_ut)
        planets = get_all_planets(jd)
        sun_lon, moon_lon = planets['Sun']['longitude'], planets['Moon']['longitude']
        
        vs = get_vikram_samvat(y, mo, d)
        tithi = get_tithi(sun_lon, moon_lon)
        yoga = get_yoga(sun_lon, moon_lon)
        karana = get_karana(sun_lon, moon_lon)
        sun_info = get_sunrise_sunset(jd, req.lat, req.lon, req.tz)
        
        return {
            'date': req.date, 'place': {'lat': req.lat, 'lon': req.lon, 'tz': req.tz},
            'vikram_samvat': vs['vikram_samvat'], 'shaka_samvat': vs['shaka_samvat'], 'tithi': tithi,
            'nakshatra': {'name': planets['Moon']['nakshatra'], 'pada': planets['Moon']['pada'], 'lord': planets['Moon']['nakshatra_lord']},
            'yoga': yoga, 'karana': karana, 'sunrise': sun_info['sunrise'],
            'sunset': sun_info['sunset'], 'rahukaal': sun_info['rahukaal'],
            'weekday': sun_info['weekday'], 'sun_rashi': planets['Sun']['rashi'], 'disha_shool': DISHA_SHOOL.get(sun_info['weekday'], ''), 'abhijit_muhurat': get_abhijit(sun_info['sunrise'], sun_info['sunset']), **get_guli_yamghant(sun_info['sunrise'], sun_info['sunset'], sun_info['weekday']), 'ritu': get_ritu_ayan(mo, d)['ritu'], 'ayana': get_ritu_ayan(mo, d)['ayana'], 'tithi_deity': TITHI_DEITY.get(tithi['number'], ''), 'planets': planets
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/match-making')
def match_making(req: MatchMakingRequest):
    try:
        boy_jd, boy_dt = parse_birth(req.boy)
        girl_jd, girl_dt = parse_birth(req.girl)
        boy_planets, girl_planets = get_all_planets(boy_jd), get_all_planets(girl_jd)
        
        ashtakoot = calculate_ashtakoot(boy_planets['Moon']['nakshatra_num']-1, girl_planets['Moon']['nakshatra_num']-1)
        
        return {
            **ashtakoot,
            'boy': {'name': req.boy.name, 'nakshatra': boy_planets['Moon']['nakshatra']},
            'girl': {'name': req.girl.name, 'nakshatra': girl_planets['Moon']['nakshatra']}
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/nakshatra')
def get_nakshatra(data: BirthData):
    jd, _ = parse_birth(data)
    planets = get_all_planets(jd)
    moon = planets['Moon']
    return {'nakshatra': moon['nakshatra'], 'lord': moon['nakshatra_lord'], 'rashi': moon['rashi']}