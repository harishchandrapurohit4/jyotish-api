from astro_additions import router as astro_router
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
    NAKSHATRA_ML, RASHI_ML, TITHI_ML, YOGA_ML, KARANA_ML, WEEKDAY_ML, PAKSHA_ML, PLANET_ML, get_ml,
    get_moonrise_moonset,
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
    lang: Optional[str] = "en"

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
        from astro_engine import NAKSHATRA_ML, RASHI_ML, TITHI_ML, YOGA_ML, KARANA_ML, WEEKDAY_ML, PAKSHA_ML, get_ml
        y, mo, d = map(int, req.date.split('-'))
        h_ut = 12.0 - req.tz
        jd = get_julian_day(y, mo, d, h_ut)
        planets = get_all_planets(jd)
        sun_lon, moon_lon = planets['Sun']['longitude'], planets['Moon']['longitude']
        lang = getattr(req, 'lang', 'en') or 'en'
        vs = get_vikram_samvat(y, mo, d)
        tithi_raw = get_tithi(sun_lon, moon_lon)
        yoga_raw = get_yoga(sun_lon, moon_lon)
        karana_raw = get_karana(sun_lon, moon_lon)
        sun_info = get_sunrise_sunset(jd, req.lat, req.lon, req.tz)
        WDAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        wd_idx = WDAYS.index(sun_info['weekday']) if sun_info['weekday'] in WDAYS else 6
        nak_idx = planets['Moon']['nakshatra_num'] - 1
        sun_rashi_idx = planets['Sun']['rashi_num'] - 1
        tithi_idx = (tithi_raw['number'] - 1) % 15
        paksha_en = tithi_raw['paksha']
        tithi = {**tithi_raw, 'name': get_ml(TITHI_ML, lang, index=tithi_idx), 'paksha': get_ml(PAKSHA_ML, lang, key=paksha_en), 'display': get_ml(PAKSHA_ML, lang, key=paksha_en) + ' ' + get_ml(TITHI_ML, lang, index=tithi_idx)}
        yoga = {**yoga_raw, 'name': get_ml(YOGA_ML, lang, index=yoga_raw['number']-1)}
        karana = {**karana_raw, 'name': get_ml(KARANA_ML, lang, index=karana_raw['number'] % 11)}
        return {
            'date': req.date, 'place': {'lat': req.lat, 'lon': req.lon, 'tz': req.tz}, 'lang': lang,
            'vikram_samvat': vs['vikram_samvat'], 'shaka_samvat': vs['shaka_samvat'], 'tithi': tithi,
            'nakshatra': {'name': get_ml(NAKSHATRA_ML, lang, index=nak_idx), 'pada': planets['Moon']['pada'], 'lord': planets['Moon']['nakshatra_lord']},
            'yoga': yoga, 'karana': karana, 'sunrise': sun_info['sunrise'],
            'sunset': sun_info['sunset'], 'rahukaal': sun_info['rahukaal'],
            'weekday': get_ml(WEEKDAY_ML, lang, index=wd_idx),
            'sun_rashi': get_ml(RASHI_ML, lang, index=sun_rashi_idx),
            'disha_shool': DISHA_SHOOL.get(sun_info['weekday'], ''),
            'abhijit_muhurat': get_abhijit(sun_info['sunrise'], sun_info['sunset']),
            **get_guli_yamghant(sun_info['sunrise'], sun_info['sunset'], sun_info['weekday']),
            'ritu': get_ritu_ayan(mo, d)['ritu'], 'ayana': get_ritu_ayan(mo, d)['ayana'],
            **get_moonrise_moonset(jd, req.lat, req.lon, req.tz),
            'tithi_deity': TITHI_DEITY.get(tithi_raw['number'], ''), 'planets': planets
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

app.include_router(astro_router)

@app.post('/gochar')
def get_gochar(data: dict):
    try:
        moon_sign = data.get('moon_sign', 1)
        import swisseph as swe
        from datetime import datetime
        swe.set_ephe_path('/root/jyotish-api/ephe')
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        dt = datetime.utcnow()
        jd_now = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
        SIGNS = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        NAKS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
        pids = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN,'Rahu':swe.MEAN_NODE}
        planets = {}
        for name, pid in pids.items():
            lon = swe.calc_ut(jd_now, pid, swe.FLG_SIDEREAL)[0][0] % 360
            spd = swe.calc_ut(jd_now, pid, swe.FLG_SIDEREAL|swe.FLG_SPEED)[0][3]
            planets[name] = {'longitude': lon, 'rashi': SIGNS[int(lon/30)], 'nakshatra': NAKS[int(lon*27/360)], 'retrograde': spd < 0}
        ketu_lon = (planets['Rahu']['longitude'] + 180) % 360
        planets['Ketu'] = {'longitude': ketu_lon, 'rashi': SIGNS[int(ketu_lon/30)], 'nakshatra': NAKS[int(ketu_lon*27/360)], 'retrograde': False}
        sat_rashi = int(planets['Saturn']['longitude']/30)
        jup_rashi = int(planets['Jupiter']['longitude']/30)
        rahu_rashi = int(planets['Rahu']['longitude']/30)
        ketu_rashi = int(planets['Ketu']['longitude']/30)
        moon_sign_idx = moon_sign - 1
        sat_diff = (sat_rashi - moon_sign_idx) % 12
        sade_sati = sat_diff in [11, 0, 1]
        dhaya = sat_diff in [3, 7]
        if sade_sati:
            sati_status = 'Peak Sade Sati' if sat_diff == 0 else 'Sade Sati'
            sati_tip = 'Shani ki pooja karein'
        elif dhaya:
            sati_status = 'Dhaya'
            sati_tip = 'Hanuman Chalisa padhein'
        else:
            sati_status = 'Shubh'
            sati_tip = None
        jup_diff = (jup_rashi - moon_sign_idx) % 12
        guru_shubh = jup_diff in [1, 2, 4, 5, 7, 8, 9, 11]
        guru_status = 'Shubh — Guru ka ashirvaad' if guru_shubh else 'Madhyam'
        overall = 'Kashtkaal' if sade_sati or dhaya else 'Shubh Kaal'
        transit_positions = {name: {'rashi': p['rashi'], 'nakshatra': p['nakshatra'], 'retrograde': p['retrograde']} for name, p in planets.items()}
        try:
            transit_lons = {name: planets[name]['longitude'] for name in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu']}
            gochar_phal = get_gochar_phal_with_vedh(moon_sign, transit_lons)
        except Exception as ge:
            gochar_phal = {'error': str(ge)}
        return {'gochar_phal': gochar_phal, 'overall': overall, 'sade_sati': {'status': sati_status, 'saturn_rashi': SIGNS[sat_rashi], 'moon_rashi': SIGNS[moon_sign_idx], 'tip': sati_tip}, 'guru_gochar': {'status': guru_status, 'jupiter_rashi': SIGNS[jup_rashi], 'diff_house': jup_diff}, 'rahu_ketu': {'rahu_rashi': SIGNS[rahu_rashi], 'ketu_rashi': SIGNS[ketu_rashi]}, 'transit_positions': transit_positions, 'transit_date': dt.strftime('%Y-%m-%d')}
    except Exception as e:
        raise HTTPException(500, str(e))



NAKSHATRA_LORD = {
    'Ashwini':('Ketu',7,'Bhoora'),'Bharani':('Shukra',6,'Safed'),'Krittika':('Surya',1,'Lal'),
    'Rohini':('Chandra',2,'Safed'),'Mrigashira':('Mangal',9,'Lal'),'Ardra':('Rahu',4,'Neela'),
    'Punarvasu':('Guru',3,'Peela'),'Pushya':('Shani',8,'Kala'),'Ashlesha':('Budh',5,'Hara'),
    'Magha':('Ketu',7,'Bhoora'),'Purva Phalguni':('Shukra',6,'Gulabi'),'Uttara Phalguni':('Surya',1,'Narangi'),
    'Hasta':('Chandra',2,'Safed'),'Chitra':('Mangal',9,'Lal'),'Swati':('Rahu',4,'Neela'),
    'Vishakha':('Guru',3,'Peela'),'Anuradha':('Shani',8,'Neela'),'Jyeshtha':('Budh',5,'Hara'),
    'Mula':('Ketu',7,'Bhoora'),'Purva Ashadha':('Shukra',6,'Safed'),'Uttara Ashadha':('Surya',1,'Lal'),
    'Shravana':('Chandra',2,'Safed'),'Dhanishtha':('Mangal',9,'Lal'),'Shatabhisha':('Rahu',4,'Neela'),
    'Purva Bhadrapada':('Guru',3,'Peela'),'Uttara Bhadrapada':('Shani',8,'Kala'),'Revati':('Budh',5,'Hara'),
}
GRAHA_ANK = {'Sun':(1,'Narangi'),'Moon':(2,'Safed'),'Jupiter':(3,'Peela'),'Rahu':(4,'Neela'),'Mercury':(5,'Hara'),'Venus':(6,'Gulabi'),'Ketu':(7,'Bhoora'),'Saturn':(8,'Kala'),'Mars':(9,'Lal')}
PEAK2 = {'Sun':(1,10),'Mars':(1,10),'Mercury':(0,30),'Moon':(0,30),'Jupiter':(10,20),'Venus':(10,20),'Saturn':(21,30),'Rahu':(21,30),'Ketu':(21,30)}

def get_shubh_ank_rang(transit, period='daily'):
    moon_nak = transit.get('Moon',{}).get('nakshatra','Shravana')
    nak_info = NAKSHATRA_LORD.get(moon_nak, ('Chandra',2,'Safed'))
    chandra_ank, chandra_rang = nak_info[1], nak_info[2]
    strongest = None
    strongest_score = -1
    for g, td in transit.items():
        if g in ['Moon','Ketu']: continue
        deg = td.get('degree_in_rashi',0)
        pk = PEAK2.get(g,(0,30))
        if pk[0] <= deg <= pk[1]:
            ank, rang = GRAHA_ANK.get(g,(1,'Lal'))
            if ank > strongest_score:
                strongest_score = ank
                strongest = (g, ank, rang)
    if strongest:
        return f"{chandra_ank}, {strongest[1]}", f"{chandra_rang}, {strongest[2]}"
    return str(chandra_ank), chandra_rang


@app.post('/auto-rashifal')
def generate_auto_rashifal(data: dict):
    try:
        import swisseph as swe
        from datetime import datetime
        import google.generativeai as genai
        import json as jsonlib
        rashi_num = data.get('rashi_num', 1)
        period = data.get('period', 'daily')
        RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        swe.set_ephe_path('/root/jyotish-api/ephe')
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        dt = datetime.utcnow()
        jd = swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60.0)
        pids = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN,'Rahu':swe.MEAN_NODE}
        transit = {}
        for name,pid in pids.items():
            lon = swe.calc_ut(jd,pid,swe.FLG_SIDEREAL)[0][0]%360
            spd = swe.calc_ut(jd,pid,swe.FLG_SIDEREAL|swe.FLG_SPEED)[0][3]
            transit[name] = {'longitude':lon,'rashi':RASHI[int(lon/30)],'degree_in_rashi':round(lon%30,2),'retrograde':spd<0}
        kl = (transit['Rahu']['longitude']+180)%360
        transit['Ketu'] = {'longitude':kl,'rashi':RASHI[int(kl/30)],'degree_in_rashi':round(kl%30,2),'retrograde':True}
        PEAK = {'Sun':(1,10),'Mars':(1,10),'Mercury':(0,30),'Moon':(0,30),'Jupiter':(10,20),'Venus':(10,20),'Saturn':(21,30),'Rahu':(21,30),'Ketu':(21,30)}
        lines = []
        for g,td in transit.items():
            deg = td['degree_in_rashi']
            pk = PEAK.get(g,(0,30))
            sh = 'Poora Phal' if pk[0]<=deg<=pk[1] else ('Kam Phal' if deg<pk[0] else 'Madhyam Phal')
            bh = ((int(td['longitude']/30)-(rashi_num-1))%12)+1
            rt = ' Vakri' if td['retrograde'] else ''
            lines.append(f"{g}: {td['rashi']} {deg:.1f}deg Bhav-{bh} {sh}{rt}")

        rn = RASHI[rashi_num-1]
        moon = transit['Moon']
        if period=='daily':
            pinst = 'Aaj ke din ka dainik rashifal likho.'
            pctx = f'Chandra {moon["rashi"]} mein {moon["degree_in_rashi"]:.1f} degree.'
        elif period=='weekly':
            pinst = 'Is hafte ka saptahik rashifal likho.'
            pctx = 'Is hafte ke graha gochar.'
        else:
            pinst = 'Is saal 2026 ka varshik rashifal likho.'
            pctx = 'Varshik gochar.'
        lang_name = {'hi':'Hindi','en':'English','mr':'Marathi','gu':'Gujarati','bn':'Bengali'}.get(data.get('lang','hi'),'Hindi')
        prompt = f"""Tu expert Vedic Jyotishi hai. {rn} rashi ke liye {pinst}
Gochar: {chr(10).join(lines)}
{pctx}
Rules: Sun/Mars 1-10=Poora, Jupiter/Venus 10-20=Poora, Saturn/Rahu 21-30=Poora, Mercury/Moon sab jagah.
Sirf JSON: {{"general":"...","love":"...","career":"...","finance":"...","health":"...","score_love":3,"score_career":4,"score_finance":3,"score_health":4}}
{lang_name} mein. IMPORTANT: Sirf {lang_name} script mein likho. Hindi ya Roman script bilkul mat use karo. Pure {lang_name} mein response do."""
        import google.generativeai as genai
        genai.configure(api_key='AIzaSyDJ2QBG9E2Ka1AFdXG-HG1OFXlX1M2QlUg')
        gmodel = genai.GenerativeModel('gemini-2.5-flash')
        resp = gmodel.generate_content(prompt)
        text = resp.text.strip().replace('```json','').replace('```','').strip()
        rashifal = jsonlib.loads(text)
        shubh_ank,shubh_rang=get_shubh_ank_rang(transit,period)
        try:
            from supabase import create_client
            sb = create_client('https://nugivfxtdhmyxefsyyoo.supabase.co','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51Z2l2Znh0ZGhteXhlZnN5eW9vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTE2MzkxOSwiZXhwIjoyMDkwNzM5OTE5fQ.7yjJ6lDZvGVRVlF2gA5jZr7cgep7wHl8O7L7DZ2Xl5U')
            today = dt.strftime('%Y-%m-%d')
            lang = data.get('lang','hi')
            sb.table('daily_horoscopes').upsert({'rashi':rn,'date':today,'lang':lang,'general':rashifal.get('general',''),'love':rashifal.get('love',''),'career':rashifal.get('career',''),'finance':rashifal.get('finance',''),'health':rashifal.get('health',''),'score_love':rashifal.get('score_love',3),'score_career':rashifal.get('score_career',3),'score_finance':rashifal.get('score_finance',3),'score_health':rashifal.get('score_health',3),'lucky_color':shubh_rang,'lucky_number':str(shubh_ank)},on_conflict='rashi,date,lang').execute()
        except Exception as se:
            pass
        return {'rashi':rn,'period':period,'rashifal':rashifal,'shubh_ank':shubh_ank,'shubh_rang':shubh_rang,'transit_date':dt.strftime('%Y-%m-%d')}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/trading-signal')
def get_trading_signal(data: dict):
    try:
        import swisseph as swe
        from datetime import datetime
        init_ephem("/root/jyotish-api/ephe")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        dt=datetime.utcnow(); jd_now = swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60.0)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        moon_lon = swe.calc_ut(jd_now, swe.MOON, flags)[0][0] % 360
        mercury_lon = swe.calc_ut(jd_now, swe.MERCURY, flags)[0][0] % 360
        mercury_spd = swe.calc_ut(jd_now, swe.MERCURY, flags)[0][3]
        rahu_lon = swe.calc_ut(jd_now, swe.MEAN_NODE, flags)[0][0] % 360
        NAKSHATRA_NAMES = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
        RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        moon_nak = NAKSHATRA_NAMES[int(moon_lon / (360/27))]
        moon_rashi = RASHI[int(moon_lon/30)]
        mercury_rashi = RASHI[int(mercury_lon/30)]
        mercury_retro = mercury_spd < 0
        rahu_rashi = RASHI[int(rahu_lon/30)]
        rahu_active = abs(moon_lon - rahu_lon) < 30
        VOLATILE_NAK = ['Jyeshtha','Ardra','Ashlesha','Mula','Shatabhisha']
        BULLISH_NAK = ['Rohini','Pushya','Hasta','Anuradha','Revati','Shravana']
        BEARISH_NAK = ['Bharani','Krittika','Vishakha','Purva Ashadha','Purva Phalguni']
        if moon_nak in VOLATILE_NAK:
            signal = 'High Volatility — Bade trades avoid karein'
            strength = 'Bearish/Volatile'
        elif rahu_active:
            signal = 'Fake Breakout Possible — Rahu active hai'
            strength = 'Cautious'
        elif mercury_retro:
            signal = 'Mercury Vakri — Communication stocks avoid karein'
            strength = 'Neutral'
        elif moon_nak in BULLISH_NAK and not mercury_retro:
            signal = 'Bullish — Intraday buy ke liye acha din'
            strength = 'Bullish'
        elif moon_nak in BEARISH_NAK:
            signal = 'Bearish — Short selling consider karein'
            strength = 'Bearish'
        else:
            signal = 'Sideways Market — Wait and Watch'
            strength = 'Neutral'
        return {
            'signal': signal,
            'strength': strength,
            'moon_nakshatra': moon_nak,
            'moon_rashi': moon_rashi,
            'mercury_retrograde': mercury_retro,
            'rahu_active': rahu_active,
            'date': datetime.utcnow().strftime('%Y-%m-%d')
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/vastu')
def get_vastu(data: dict):
    try:
        direction = data.get('direction', 'N')
        room = data.get('room', 'general')
        VASTU_MAP = {
            'NE': {'best_for': ['Temple/Pooja room', 'Study room'], 'avoid': ['Toilet', 'Kitchen'], 'element': 'Water', 'deity': 'Ishaan', 'tip': 'Sabse pavitra disha — pooja ghar yahin banayein'},
            'N':  {'best_for': ['Living room', 'Office'], 'avoid': ['Heavy storage'], 'element': 'Water', 'deity': 'Kuber', 'tip': 'Dhan aur samriddhi ki disha'},
            'NW': {'best_for': ['Guest room', 'Garage'], 'avoid': ['Master bedroom'], 'element': 'Air', 'deity': 'Vayu', 'tip': 'Guests ke liye best direction'},
            'E':  {'best_for': ['Study', 'Living room'], 'avoid': ['Toilet'], 'element': 'Air', 'deity': 'Indra', 'tip': 'Sunrise direction — positive energy'},
            'W':  {'best_for': ['Dining room', 'Children room'], 'avoid': ['Main entrance'], 'element': 'Earth', 'deity': 'Varun', 'tip': 'Stability aur growth ke liye'},
            'SE': {'best_for': ['Kitchen'], 'avoid': ['Bedroom', 'Study'], 'element': 'Fire', 'deity': 'Agni', 'tip': 'Kitchen ke liye perfect — Agni ki disha'},
            'S':  {'best_for': ['Master bedroom'], 'avoid': ['Main door', 'Kitchen'], 'element': 'Earth', 'deity': 'Yama', 'tip': 'Heavy furniture yahin rakhen'},
            'SW': {'best_for': ['Master bedroom', 'Heavy storage'], 'avoid': ['Entrance', 'Pooja room'], 'element': 'Earth', 'deity': 'Nairutya', 'tip': 'Grih swami ka kamra yahin hona chahiye'},
        }
        info = VASTU_MAP.get(direction.upper(), VASTU_MAP['N'])
        return {
            'direction': direction.upper(),
            'room': room,
            'best_for': info['best_for'],
            'avoid': info['avoid'],
            'element': info['element'],
            'deity': info['deity'],
            'tip': info['tip']
        }
    except Exception as e:
        raise HTTPException(500, str(e))



# Navamsha Analysis Data
RASHI_HEIGHT = {
  'Mesh': 'Madhyam kad, strong build (5ft6in-5ft9in)',
  'Vrishabh': 'Thoda nata, bhari body, strong',
  'Mithun': 'Lamba patla (5ft10in+), flexible',
  'Karka': 'Madhyam, soft gol body',
  'Simha': 'Lamba, pratapshali gathan',
  'Kanya': 'Madhyam sundar, slim',
  'Tula': 'Lamba sundar, balanced',
  'Vrishchik': 'Madhyam muscular, strong',
  'Dhanu': 'Lamba athletic, active',
  'Makar': 'Madhyam se lamba, slim dry',
  'Kumbh': 'Lamba alag look, unique',
  'Meen': 'Nata madhyam, soft plump',
}

CHANDRA_RANG = {
  'Mesh': 'Gehra sawla, lal aabha',
  'Vrishabh': 'Gora saaf, safed aabha',
  'Mithun': 'Sawla, peeli harit aabha',
  'Karka': 'Gora, chandni jaisa rang',
  'Simha': 'Sona jaisi chamak, gehri',
  'Kanya': 'Sawla, hara aakar',
  'Tula': 'Gora, gulabi aabha',
  'Vrishchik': 'Sawla lal-bhura',
  'Dhanu': 'Gehri peeli chamak',
  'Makar': 'Saaf sawla, mitti rang',
  'Kumbh': 'Mixed, neeli aabha',
  'Meen': 'Gora, sea-green aabha',
}

NAVAMSHA_VIVAH = {
  'Mesh': 'Ugra, sahasik partner. Jaldi vivah sambhav. Mangal dosha dekhein.',
  'Vrishabh': 'Sundar, dhani partner. Sukhi vivah. Shukra prabhavit.',
  'Mithun': 'Buddhiman, vaachaal partner. Dost jaisa rishta.',
  'Karka': 'Caring, parivarik partner. Mata jaisi premi.',
  'Simha': 'Shaahi, ghamandi partner. Strong personality.',
  'Kanya': 'Vyavharik, alochak partner. Swasthya dhyan rakhein.',
  'Tula': 'Sundar, kalatmak partner. Achcha vivah yog.',
  'Vrishchik': 'Gehri, rahasyamayi partner. Intense relationship.',
  'Dhanu': 'Swatantra, dharmic partner. Travel lover.',
  'Makar': 'Mehanti, gambhir partner. Deri se vivah sambhav.',
  'Kumbh': 'Alag, adbhut partner. Unconventional relationship.',
  'Meen': 'Bhaavsuk, aatmik partner. Sensitive nature.',
}

NAVAMSHA_CAREER = {
  'Mesh': 'Sena, police, surgery, sports, engineering',
  'Vrishabh': 'Banking, krishi, kala, sangeet, food industry',
  'Mithun': 'Media, IT, lekhan, vyapar, communication',
  'Karka': 'Nursing, hotel, food, real estate, psychology',
  'Simha': 'Politics, management, government, entertainment',
  'Kanya': 'Medicine, accounts, teaching, analysis',
  'Tula': 'Law, fashion, diplomacy, kala, judiciary',
  'Vrishchik': 'Research, secret services, surgery, mining',
  'Dhanu': 'Teaching, law, dharma, travel, publishing',
  'Makar': 'Engineering, nirmaan, admin, government',
  'Kumbh': 'Technology, social work, science, astrology',
  'Meen': 'Adhyatma, kala, medicine, sea, healing',
}

RASHI_LORDS = {
  'Mesh': 'Mars', 'Vrishabh': 'Venus', 'Mithun': 'Mercury',
  'Karka': 'Moon', 'Simha': 'Sun', 'Kanya': 'Mercury',
  'Tula': 'Venus', 'Vrishchik': 'Mars', 'Dhanu': 'Jupiter',
  'Makar': 'Saturn', 'Kumbh': 'Saturn', 'Meen': 'Jupiter',
}

def get_navamsha_analysis(planets_data, lagna_vargas):
    try:
        d9_lagna = lagna_vargas.get('D9', {}) if isinstance(lagna_vargas, dict) else {}
        nav_lagna_sign = d9_lagna.get('sign', 'Mesh')
        moon_vargas = planets_data.get('Moon', {})
        moon_d9 = moon_vargas.get('D9', {}) if isinstance(moon_vargas, dict) else {}
        moon_nav_sign = moon_d9.get('sign', 'Karka')
        print(f"DEBUG: nav_lagna={nav_lagna_sign}, moon_nav={moon_nav_sign}")
        navamshesh = RASHI_LORDS.get(nav_lagna_sign, 'Mars')
        nav_lagna_num = lagna_vargas.get('D9', {}).get('sign_num', 1)
        navamshesh_d9 = planets_data.get(navamshesh, {}).get('D9', {})
        navamshesh_sign_num = navamshesh_d9.get('sign_num', 1)
        navamshesh_house = ((navamshesh_sign_num - nav_lagna_num) % 12) + 1
        graha_drishti = []
        for planet, vargas in planets_data.items():
            d9 = vargas.get('D9', {})
            sign_num = d9.get('sign_num', 0)
            if not sign_num: continue
            house = ((sign_num - nav_lagna_num) % 12) + 1
            aspects = []
            if planet in ['Mars']:
                aspects = [house, (house+3)%12 or 12, (house+6)%12 or 12, (house+7)%12 or 12]
            elif planet in ['Jupiter']:
                aspects = [house, (house+4)%12 or 12, (house+6)%12 or 12, (house+8)%12 or 12]
            elif planet in ['Saturn']:
                aspects = [house, (house+2)%12 or 12, (house+6)%12 or 12, (house+9)%12 or 12]
            else:
                aspects = [house, (house+6)%12 or 12]
            if 1 in aspects:
                graha_drishti.append({'planet': planet, 'from_house': house, 'type': 'Lagna par drishti'})
            if 7 in aspects:
                graha_drishti.append({'planet': planet, 'from_house': house, 'type': 'Saptam par drishti'})

        return {
            'navamsha_lagna': nav_lagna_sign,
            'navamsha_lagna_lord': navamshesh,
            'navamshesh_house': navamshesh_house,
            'chandra_navamsha': moon_nav_sign,
            'height_prediction': RASHI_HEIGHT.get(nav_lagna_sign, ''),
            'rang_prediction': CHANDRA_RANG.get(moon_nav_sign, ''),
            'vivah_phaladesh': NAVAMSHA_VIVAH.get(nav_lagna_sign, ''),
            'career_phaladesh': NAVAMSHA_CAREER.get(nav_lagna_sign, ''),
            'graha_drishti_d9': graha_drishti,
        }
    except Exception as e:
        return {'error': str(e)}

@app.post('/varga')
def get_varga_charts(data: dict):
    try:
        from astro_engine import get_all_vargas, get_karkamsha_lagna, get_pada_lagna, get_upapada_lagna
        import swisseph as swe
        dob = data.get('dob','1990-01-01')
        tob = data.get('tob','12:00')
        lat = float(data.get('lat', 23.0225))
        lon_in = float(data.get('lon', 72.5714))
        tz = float(data.get('tz', 5.5))
        year,month,day = map(int, dob.split('-'))
        hour,minute = map(int, tob.split(':'))
        ut_hour = hour + minute/60.0 - tz
        jd = swe.julday(year, month, day, ut_hour)
        init_ephem()
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        PLANETS = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN,'Rahu':swe.MEAN_NODE}
        planets_data = {}
        varga_results = {}
        for name, pid in PLANETS.items():
            lon_val = swe.calc_ut(jd, pid, flags)[0][0] % 360
            planets_data[name] = {'longitude': lon_val}
            varga_results[name] = get_all_vargas(lon_val)
        cusps, _ = swe.houses(jd, lat, lon_in, b'P')
        asc_lon = cusps[0] % 360
        house_cusps = [{'longitude': c % 360} for c in cusps]
        karkamsha = get_karkamsha_lagna(planets_data)
        pada = get_pada_lagna(asc_lon)
        upapada = get_upapada_lagna(house_cusps)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        asc_sid = (cusps[0] - ayanamsa) % 360
        lagna_vargas = get_all_vargas(asc_sid)
        navamsha_analysis = get_navamsha_analysis(varga_results, lagna_vargas)
        return {'varga_charts': varga_results, 'lagna_vargas': lagna_vargas, 'karkamsha_lagna': karkamsha, 'pada_lagna': pada, 'upapada_lagna': upapada, 'navamsha_analysis': navamsha_analysis}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get('/daily-rashifal')
def get_daily_rashifal():
    try:
        import swisseph as swe
        from datetime import datetime
        init_ephem()
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        dt = datetime.utcnow()
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        lons = {}
        for name, pid in [('Sun',swe.SUN),('Moon',swe.MOON),('Mars',swe.MARS),('Mercury',swe.MERCURY),('Jupiter',swe.JUPITER),('Venus',swe.VENUS),('Saturn',swe.SATURN),('Rahu',swe.MEAN_NODE)]:
            lons[name] = swe.calc_ut(jd, pid, flags)[0][0] % 360
        lons['Ketu'] = (lons['Rahu'] + 180) % 360
        RASHI = ['Mesh','Vrishabh','Mithun','Karka','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        g = {k: int(v/30) for k,v in lons.items()}
        results = {}
        for rashi_idx in range(12):
            r = rashi_idx
            sun_h = (g['Sun']-r)%12+1
            moon_h = (g['Moon']-r)%12+1
            mars_h = (g['Mars']-r)%12+1
            jup_h = (g['Jupiter']-r)%12+1
            sat_h = (g['Saturn']-r)%12+1
            ven_h = (g['Venus']-r)%12+1
            mer_h = (g['Mercury']-r)%12+1
            rahu_h = (g['Rahu']-r)%12+1
            score = 0
            tips = []
            if jup_h in [1,2,4,5,7,9,10,11]: score+=2; tips.append('Guru shubh')
            if sat_h in [3,6,11]: score+=1; tips.append('Shani anukul')
            if sat_h in [1,2,4,7,8,10,12]: score-=1; tips.append('Shani dakdakhek')
            if moon_h in [1,4,7,10]: score+=1; tips.append('Chandra bal')
            if mars_h in [1,8]: score-=1; tips.append('Mangal savdhan')
            if ven_h in [1,2,4,5,7,11]: score+=1; tips.append('Shukra shubh')
            if rahu_h in [1,4,7,10]: score-=1; tips.append('Rahu savdhan')
            if sun_h in [1,4,7,10]: score+=1
            sade_sati = sat_h in [12,1,2]
            if sade_sati: score-=2; tips.append('Sade Sati')
            if score >= 3: overall = 'Ati Shubh'; stars = 5
            elif score >= 1: overall = 'Shubh'; stars = 4
            elif score == 0: overall = 'Madhyam'; stars = 3
            elif score >= -1: overall = 'Sadharan'; stars = 2
            else: overall = 'Kathin'; stars = 1
            PHAL = {
                'prem': 'Shubh' if ven_h in [1,5,7,11] else 'Madhyam',
                'career': 'Shubh' if jup_h in [2,6,10,11] and sat_h in [3,6,11] else 'Madhyam',
                'dhan': 'Shubh' if jup_h in [2,5,9,11] else 'Madhyam',
                'swasthya': 'Shubh' if mars_h not in [1,6,8] else 'Savdhan',
            }
            results[RASHI[rashi_idx]] = {
                'overall': overall,
                'stars': stars,
                'phal': PHAL,
                'tips': tips,
                'sade_sati': sade_sati,
                'date': dt.strftime('%Y-%m-%d')
            }
        return {'rashifal': results, 'graha_positions': {k: RASHI[v] for k,v in g.items()}, 'date': dt.strftime('%Y-%m-%d')}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/weekly-trading-outlook')
def get_weekly_trading_outlook(data: dict = {}):
    try:
        import swisseph as swe
        from datetime import datetime, timedelta
        import google.generativeai as genai
        import json as jsonlib
        
        swe.set_ephe_path('/root/jyotish-api/ephe')
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        dt = datetime.utcnow()
        jd = swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60.0)
        
        pids = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN}
        transit = {}
        for name,pid in pids.items():
            lon = swe.calc_ut(jd,pid,swe.FLG_SIDEREAL)[0][0]%360
            RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
            transit[name] = {'rashi':RASHI[int(lon/30)],'degree':round(lon%30,2)}
        
        lines = [f"{g}: {d['rashi']} {d['degree']}deg" for g,d in transit.items()]
        
        prompt = f"""Tu expert Vedic Jyotishi aur stock market analyst hai.
Current planetary positions:
{chr(10).join(lines)}

Aaj {datetime.now().strftime('%A')} hai.

Weekly trading outlook banao — har din ke liye:
- mood: bullish/bearish/volatile/neutral
- note: 1 line trading tip (Hindi mein)
- sectors: best sectors us din ke liye

Sirf JSON return karo (no markdown):
{{
  "monday": {{"mood":"bullish","note":"...","sectors":["IT","Banking"]}},
  "tuesday": {{"mood":"volatile","note":"...","sectors":["..."] }},
  "wednesday": {{"mood":"bearish","note":"...","sectors":["..."]}},
  "thursday": {{"mood":"bullish","note":"...","sectors":["..."]}},
  "friday": {{"mood":"bullish","note":"...","sectors":["..."]}},
  "saturday": {{"mood":"neutral","note":"...","sectors":["..."]}},
  "sunday": {{"mood":"neutral","note":"...","sectors":["..."]}}
}}"""
        
        genai.configure(api_key='AIzaSyDJ2QBG9E2Ka1AFdXG-HG1OFXlX1M2QlUg')
        gmodel = genai.GenerativeModel('gemini-2.5-flash')
        resp = gmodel.generate_content(prompt)
        text = resp.text.strip().replace('```json','').replace('```','').strip()
        outlook = jsonlib.loads(text)
        return {'outlook': outlook, 'transit': transit}
    except Exception as e:
        raise HTTPException(500, str(e))
