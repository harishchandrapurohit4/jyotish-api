"""
=============================================================
ASTRO OPINION ULTIMATE — Enhanced Additions for Jyotish API
=============================================================
Yeh 3 naye endpoints add karta hai existing jyotish-api mein:
  POST /gochar       — Sade Sati, Dhaya, Gochar analysis
  POST /muhurat      — Advanced Muhurat calculation
  POST /ai-prediction — Grah-based predictions
  POST /full-kundli  — Sab ek saath

Existing main.py mein import karke router add karo.
=============================================================
"""

import swisseph as swe
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

# ─── Models ───────────────────────────────────────────────────────────────────

class GocharRequest(BaseModel):
    moon_sign: int          # natal moon rashi number 1-12
    lat: float = 23.0225
    lon: float = 72.5714
    tz: float = 5.5
    date: Optional[str] = None  # YYYY-MM-DD, default today

class MuhuratRequest(BaseModel):
    tithi: int              # 1-30
    nakshatra: str          # nakshatra name
    weekday: str            # Monday, Tuesday etc.
    purpose: Optional[str] = "general"  # marriage, business, travel, general

class PredictionRequest(BaseModel):
    dob: str                # YYYY-MM-DD
    tob: str                # HH:MM
    lat: float
    lon: float
    tz: float = 5.5

class FullKundliRequest(BaseModel):
    dob: str
    tob: str
    lat: float
    lon: float
    tz: float = 5.5

# ─── Constants ────────────────────────────────────────────────────────────────

RASHI_NAMES = [
    'Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
    'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen'
]

NAKSHATRA_NAMES = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha',
    'Purva Bhadrapada','Uttara Bhadrapada','Revati'
]

PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 'Venus': swe.VENUS,
    'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
}

SHUBH_NAKSHATRA = ['Rohini','Pushya','Hasta','Chitra','Swati','Uttara Phalguni',
                    'Uttara Ashadha','Uttara Bhadrapada','Punarvasu','Shravana','Dhanishtha','Revati']

ASHUBH_NAKSHATRA = ['Bharani','Ardra','Ashlesha','Magha','Mula','Jyeshtha',
                     'Krittika','Vishakha','Shatabhisha']

ASHUBH_TITHI = [4, 8, 9, 12, 14, 30]  # Chaturthi, Ashtami, Navami, etc.

WEEKDAY_SHUBH = {
    'Monday': ['marriage','travel','medical'],
    'Wednesday': ['business','education','writing'],
    'Thursday': ['all','education','spiritual'],
    'Friday': ['marriage','fashion','art'],
}

WEEKDAY_ASHUBH = {
    'Tuesday': ['marriage','start'],
    'Saturday': ['new_start','travel'],
}

# ─── Helper Functions ──────────────────────────────────────────────────────────

def get_jd(date_str: str, time_str: str = "00:00", tz: float = 5.5):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    ut = dt.hour + dt.minute/60 - tz
    return swe.julday(dt.year, dt.month, dt.day, ut)

def get_planet_positions(jd: float) -> dict:
    positions = {}
    for name, pid in PLANET_IDS.items():
        swe.set_ephe_path("/root/jyotish-api/ephe")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        res = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL|swe.FLG_SPEED)[0]
        lon = res[0]
        if name == 'Rahu':
            lon = lon % 360
        rashi_num = int(lon / 30) + 1
        nak_num = int(lon * 27 / 360)
        positions[name] = {
            'longitude': round(lon, 4),
            'rashi': RASHI_NAMES[(rashi_num - 1) % 12],
            'rashi_num': rashi_num,
            'nakshatra': NAKSHATRA_NAMES[nak_num % 27],
            'retrograde': res[3] < 0 if len(res) > 3 else False,
            'degree_in_rashi': round(lon % 30, 4),
        }
    # Ketu = Rahu + 180
    rahu_lon = positions['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    ketu_rashi_num = int(ketu_lon / 30) + 1
    ketu_nak = int(ketu_lon * 27 / 360)
    positions['Ketu'] = {
        'longitude': round(ketu_lon, 4),
        'rashi': RASHI_NAMES[(ketu_rashi_num - 1) % 12],
        'rashi_num': ketu_rashi_num,
        'nakshatra': NAKSHATRA_NAMES[ketu_nak % 27],
        'retrograde': True,
        'degree_in_rashi': round(ketu_lon % 30, 4),
    }
    return positions

# ─── Gochar Analysis ─────────────────────────────────────────────────────────

def analyze_gochar(moon_sign: int, transit_positions: dict) -> dict:
    """
    Natal moon sign ke hisaab se current grah ki sthiti analyze karo
    moon_sign: 1-12 (natal)
    """
    results = {}

    # Saturn — Sade Sati & Dhaya
    saturn_sign = transit_positions['Saturn']['rashi_num']
    saturn_diff = (saturn_sign - moon_sign) % 12
    if saturn_diff == 0:
        sade_sati = "Peak Sade Sati (Chandra pe Shani)"
    elif saturn_diff == 11:
        sade_sati = "Sade Sati Start (12th se)"
    elif saturn_diff == 1:
        sade_sati = "Sade Sati End (2nd mein)"
    elif saturn_diff == 4:
        sade_sati = "Ardha Sade Sati (Dhaya) — 4th Shani"
    elif saturn_diff == 7:
        sade_sati = "Ardha Sade Sati (Dhaya) — 7th Shani"
    else:
        sade_sati = "Normal — Sade Sati nahi"

    results['sade_sati'] = {
        'status': sade_sati,
        'saturn_rashi': transit_positions['Saturn']['rashi'],
        'moon_rashi': RASHI_NAMES[(moon_sign - 1) % 12],
        'tip': "Shani ki pooja karein, Shanivaar ko tel daan karein" if "Sade Sati" in sade_sati or "Dhaya" in sade_sati else "Koi vishesh upay ki zaroorat nahi"
    }

    # Jupiter — Guru Gochar
    guru_sign = transit_positions['Jupiter']['rashi_num']
    guru_diff = (guru_sign - moon_sign) % 12
    if guru_diff in [1, 4, 7, 10]:
        guru_status = "Shubh — Guru anukoola sthiti mein"
    elif guru_diff in [3, 6, 8, 12]:
        guru_status = "Madhyam — Guru ka saadharan prabhav"
    else:
        guru_status = "Prabal — Guru ka vishesh prabhav"

    results['guru_gochar'] = {
        'status': guru_status,
        'jupiter_rashi': transit_positions['Jupiter']['rashi'],
        'diff_house': guru_diff if guru_diff != 0 else 12,
    }

    # Rahu-Ketu axis
    rahu_sign = transit_positions['Rahu']['rashi_num']
    rahu_diff = (rahu_sign - moon_sign) % 12
    if rahu_diff in [1, 5, 9]:
        rahu_status = "Shubh Rahu sthiti"
    elif rahu_diff in [8, 12, 4]:
        rahu_status = "Rahu se savdhaan — unexpected changes possible"
    else:
        rahu_status = "Normal Rahu sthiti"

    results['rahu_ketu'] = {
        'status': rahu_status,
        'rahu_rashi': transit_positions['Rahu']['rashi'],
        'ketu_rashi': transit_positions['Ketu']['rashi'],
    }

    # Overall summary
    all_statuses = [results['sade_sati']['status'], results['guru_gochar']['status']]
    if any('Sade Sati' in s or 'Dhaya' in s for s in all_statuses):
        overall = "Kashtkaal — Dhairya rakhen, Shani upay karein"
    elif 'Shubh' in results['guru_gochar']['status']:
        overall = "Shubh kaal — Naye kaam shuru karne ka sahi samay"
    else:
        overall = "Madhyam kaal — Sambhal ke chalein"

    results['overall'] = overall
    results['transit_date'] = datetime.now().strftime('%Y-%m-%d')

    return results

# ─── Muhurat Analysis ─────────────────────────────────────────────────────────

def analyze_muhurat(tithi: int, nakshatra: str, weekday: str, purpose: str) -> dict:
    issues = []
    positives = []
    score = 50  # base score

    # Tithi check
    if tithi in ASHUBH_TITHI:
        issues.append(f"Tithi {tithi} ashubh hai — avoid karo")
        score -= 20
    elif tithi in [2, 3, 5, 7, 10, 11, 13]:
        positives.append("Tithi shubh hai")
        score += 15

    # Nakshatra check
    if nakshatra in SHUBH_NAKSHATRA:
        positives.append(f"{nakshatra} nakshatra shubh hai")
        score += 20
        if nakshatra == 'Pushya':
            positives.append("Pushya nakshatra — sarva karya siddhi")
            score += 10
    elif nakshatra in ASHUBH_NAKSHATRA:
        issues.append(f"{nakshatra} nakshatra ashubh hai")
        score -= 15

    # Weekday check
    if weekday in WEEKDAY_SHUBH:
        shubh_purposes = WEEKDAY_SHUBH[weekday]
        if purpose in shubh_purposes or 'all' in shubh_purposes:
            positives.append(f"{weekday} is karya ke liye shubh")
            score += 15
    if weekday in WEEKDAY_ASHUBH:
        ashubh_purposes = WEEKDAY_ASHUBH[weekday]
        if purpose in ashubh_purposes or 'all' in ashubh_purposes:
            issues.append(f"{weekday} is karya ke liye thik nahi")
            score -= 15

    # Final verdict
    score = max(0, min(100, score))
    if score >= 75:
        verdict = "Ati Shubh Muhurat ✅"
    elif score >= 55:
        verdict = "Shubh Muhurat ✅"
    elif score >= 40:
        verdict = "Sadharan Muhurat — chale to kaam chalega"
    else:
        verdict = "Ashubh Muhurat ❌ — aur din dekhein"

    return {
        'verdict': verdict,
        'score': score,
        'tithi': tithi,
        'nakshatra': nakshatra,
        'weekday': weekday,
        'purpose': purpose,
        'positives': positives,
        'issues': issues,
        'suggestion': "Guru, Shukra, Budh din prefer karein" if score < 55 else "Yeh muhurat accha hai!"
    }

# ─── AI Prediction ─────────────────────────────────────────────────────────────

def generate_predictions(planets: dict) -> dict:
    predictions = {
        'career': [],
        'health': [],
        'finance': [],
        'relationship': [],
        'general': [],
        'remedies': [],
    }

    # Saturn analysis
    if planets.get('Saturn', {}).get('retrograde'):
        predictions['career'].append("Shani vakri — kaam mein delay sambhav, dhairya rakhen")
        predictions['remedies'].append("Shanivaar ko sarson ka tel Shani mandir mein charhaen")

    saturn_rashi = planets.get('Saturn', {}).get('rashi', '')
    if saturn_rashi in ['Mesh', 'Kark', 'Simha']:
        predictions['career'].append("Shani neech/shatru rashi — mehnat zyada, fal der se")

    # Moon analysis
    moon_rashi = planets.get('Moon', {}).get('rashi', '')
    if moon_rashi == 'Vrishchik':
        predictions['health'].append("Chandra neech — emotional stress, mental peace pe dhyan")
        predictions['remedies'].append("Somvaar ko Shiv puja karein, doodh charhaen")
    elif moon_rashi in ['Vrishabh', 'Kark']:
        predictions['general'].append("Chandra uchch/swakshetra — mann prasann, kaary safal")

    # Jupiter analysis
    jupiter_rashi = planets.get('Jupiter', {}).get('rashi', '')
    if jupiter_rashi in ['Kark', 'Dhanu', 'Meen']:
        predictions['finance'].append("Guru shubh sthiti — dhan labh sambhav, vivek se kharch karein")
    elif jupiter_rashi in ['Makar', 'Mithun']:
        predictions['finance'].append("Guru neech/shatru — bade financial decisions avoid karein")

    if planets.get('Jupiter', {}).get('retrograde'):
        predictions['general'].append("Guru vakri — spiritual chintan ka samay, bade kaam rok lo")

    # Venus analysis
    venus_rashi = planets.get('Venus', {}).get('rashi', '')
    if venus_rashi in ['Vrishabh', 'Tula', 'Meen']:
        predictions['relationship'].append("Shukra shubh — prem sambandh mein meethas, vivah ke liye anukoola")
    elif venus_rashi in ['Kanya', 'Vrishchik']:
        predictions['relationship'].append("Shukra kashta — sambandho mein sambhal, misunderstanding se bachein")

    # Mars analysis
    mars_rashi = planets.get('Mars', {}).get('rashi', '')
    if mars_rashi in ['Mesh', 'Vrishchik', 'Makar']:
        predictions['career'].append("Mangal uchch/swakshetra — energy high, naye projects lein")
    elif mars_rashi == 'Kark':
        predictions['health'].append("Mangal neech — aakramakta control mein rakhen, BP check karein")

    if planets.get('Mars', {}).get('retrograde'):
        predictions['general'].append("Mangal vakri — naye kaam na shuru karein, purana kaam complete karein")

    # Rahu-Ketu
    rahu_rashi = planets.get('Rahu', {}).get('rashi', '')
    if rahu_rashi in ['Vrishabh', 'Mithun']:
        predictions['finance'].append("Rahu dhan sthaan — achanak dhan labh ya kharcha, savdhan rahein")

    # Mercury
    if planets.get('Mercury', {}).get('retrograde'):
        predictions['general'].append("Budh vakri — communication mistakes sambhav, documents double-check karein")
        predictions['career'].append("Contracts sign karne se bachein jab tak Budh margi na ho")

    # Sun
    sun_rashi = planets.get('Sun', {}).get('rashi', '')
    if sun_rashi in ['Mesh', 'Simha', 'Dhanu']:
        predictions['career'].append("Surya shubh — government kaam, authority se help milegi")

    # Add default if empty
    for key in predictions:
        if not predictions[key] and key != 'remedies':
            predictions[key].append("Graha sthiti sadharan — regular effort se success milegi")

    if not predictions['remedies']:
        predictions['remedies'].append("Nityapuja, Gayatri mantra — 108 baar pratidin")

    return predictions

# ─── API Endpoints ────────────────────────────────────────────────────────────

@router.post("/gochar")
def gochar_endpoint(req: GocharRequest):
    """
    Natal moon sign ke aadhar par current grah gochar analyze karo
    Sade Sati, Dhaya, Guru Gochar, Rahu-Ketu sthiti
    """
    date_str = req.date or datetime.now().strftime('%Y-%m-%d')
    jd = get_jd(date_str, "00:00", req.tz)
    transit = get_planet_positions(jd)
    result = analyze_gochar(req.moon_sign, transit)
    result['transit_positions'] = {
        k: {'rashi': v['rashi'], 'nakshatra': v['nakshatra'], 'retrograde': v['retrograde']}
        for k, v in transit.items()
    }
    try:
        from astro_engine import get_gochar_phal_with_vedh
        transit_lons = {k: v.get('longitude', v.get('degree', v.get('lon', 0))) for k, v in transit.items()}
        result['gochar_phal'] = get_gochar_phal_with_vedh(req.moon_sign, transit_lons)
    except Exception as ge:
        result['gochar_phal'] = {"error": str(ge)}
    return result

@router.post("/muhurat")
def muhurat_endpoint(req: MuhuratRequest):
    """
    Tithi + Nakshatra + Weekday + Purpose ke aadhar par Muhurat check karo
    Purposes: marriage, business, travel, education, medical, general
    """
    return analyze_muhurat(req.tithi, req.nakshatra, req.weekday, req.purpose)

@router.post("/ai-prediction")
def prediction_endpoint(req: PredictionRequest):
    """
    Birth details se grah position nikalo aur predictions do
    Career, Health, Finance, Relationship
    """
    jd = get_jd(req.dob, req.tob, req.tz)
    planets = get_planet_positions(jd)
    predictions = generate_predictions(planets)
    return {
        'planets': planets,
        'predictions': predictions,
        'note': 'Yeh predictions grah sthiti ke aadhar par hain. Expert se confirm karein.'
    }

@router.post("/full-kundli")
def full_kundli_endpoint(req: FullKundliRequest):
    """
    Ek hi call mein sab kuch:
    Planets + Gochar + AI Predictions + Muhurat status
    """
    from datetime import date
    jd = get_jd(req.dob, req.tob, req.tz)
    planets = get_planet_positions(jd)

    # Moon sign natal
    moon_sign = planets['Moon']['rashi_num']

    # Gochar (current date)
    today_str = date.today().strftime('%Y-%m-%d')
    today_jd = get_jd(today_str, "00:00", req.tz)
    transit = get_planet_positions(today_jd)
    gochar = analyze_gochar(moon_sign, transit)

    # AI predictions
    predictions = generate_predictions(planets)

    return {
        'natal_planets': planets,
        'moon_sign': planets['Moon']['rashi'],
        'moon_sign_num': moon_sign,
        'gochar': gochar,
        'predictions': predictions,
        'note': 'Full analysis — Gochar + AI Predictions combined'
    }
