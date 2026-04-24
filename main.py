from astro_additions import os
import router as astro_router
from avakhada import get_avakhada

import math as _math

PARAM_NEECHA = {"sun":280,"moon":213,"mars":118,"mercury":345,"jupiter":275,"venus":177,"saturn":20}
NAISARGIK_BAL = {"sun":60,"moon":51.43,"venus":42.85,"jupiter":34.28,"mercury":25.71,"mars":17.14,"saturn":8.57}
SHADBALA_MIN = {"sun":390,"moon":360,"mars":300,"mercury":420,"jupiter":390,"venus":330,"saturn":300}
DIGBAL_STRONG = {"sun":10,"moon":4,"mars":10,"mercury":1,"jupiter":1,"venus":4,"saturn":7}
MITRA = {"sun":["moon","mars","jupiter"],"moon":["sun","mercury"],"mars":["sun","moon","jupiter"],"mercury":["sun","venus"],"jupiter":["sun","moon","mars"],"venus":["mercury","saturn"],"saturn":["mercury","venus"]}
SHATRU = {"sun":["venus","saturn"],"moon":[],"mars":["mercury"],"mercury":["moon"],"jupiter":["mercury","venus"],"venus":["sun","moon"],"saturn":["sun","moon","mars"]}
MOOLTRIKONA = {"sun":4,"moon":1,"mars":0,"mercury":5,"jupiter":8,"venus":6,"saturn":9}
SWAKSHETRA = {"sun":[4],"moon":[3],"mars":[0,7],"mercury":[2,5],"jupiter":[8,11],"venus":[1,6],"saturn":[9,10]}

def _uchcha_bal(planet, lon):
    neecha = PARAM_NEECHA.get(planet, 0)
    diff = abs(lon % 360 - neecha)
    if diff > 180: diff = 360 - diff
    return round(min(diff / 3, 60), 2)

def _saptavarga_pts(planet, rashi):
    pts = {"mooltrikona":45,"swakshetra":30,"adhimittra":22.5,"mitra":15,"sama":7.5,"shatru":3.75,"adhi_shatru":1.875}
    if rashi == MOOLTRIKONA.get(planet): return pts["mooltrikona"]
    if rashi in SWAKSHETRA.get(planet, []): return pts["swakshetra"]
    RASHI_LORD = {0:"mars",1:"venus",2:"mercury",3:"moon",4:"sun",5:"mercury",6:"venus",7:"mars",8:"jupiter",9:"saturn",10:"saturn",11:"jupiter"}
    lord = RASHI_LORD.get(rashi,"")
    if lord in MITRA.get(planet,[]): return pts["mitra"]
    if lord in SHATRU.get(planet,[]): return pts["shatru"]
    return pts["sama"]

def _saptavarga_bal(planet, lon):
    total = 0
    for d in [1,2,3,7,9,12,30]:
        base = int((lon % 360) / 30)
        frac = (lon % 360) % 30
        part = int(frac / (30/d))
        vr = (base + part) % 12
        total += _saptavarga_pts(planet, vr)
    return round(total, 2)

def _dig_bal(planet, house_num):
    strong = DIGBAL_STRONG.get(planet, 1)
    diff = abs(house_num - strong)
    if diff > 6: diff = 12 - diff
    return round(max(0, (6 - diff) * 10), 2)

def _paksha_bal(planet, moon_lon, sun_lon):
    SHUBHA = ["moon","mercury","jupiter","venus"]
    diff = (moon_lon - sun_lon) % 360
    if diff > 180: diff = 360 - diff
    paksha = round(diff / 3, 2)
    return paksha if planet in SHUBHA else round(60 - paksha, 2)

def _aspect_str(p1_lon, p2_lon):
    diff = (p2_lon - p1_lon) % 360
    r = diff / 30
    if 6.5<=r<=7.5: return 60
    if 4.5<=r<=5.5 or 7.5<=r<=9.5: return 45
    if 3.5<=r<=4.5 or 9.5<=r<=10.5: return 30
    return 0

def _drik_bal(planet, lon, all_pos):
    SHUBHA = ["moon","mercury","jupiter","venus"]
    PAPA = ["sun","mars","saturn"]
    s, p = 0, 0
    for other, olon in all_pos.items():
        if other == planet: continue
        asp = _aspect_str(olon, lon)
        if asp > 0:
            if other in SHUBHA: s += asp
            elif other in PAPA: p += asp
    return round((s/4) - (p/4), 2)

def calculate_shadbala_all(planets_data, birth_hour, sunrise_hour, sunset_hour, moon_lon, sun_lon):
    """
    planets_data: dict of {planet_name: {"lon": float, "house": int, "vakri": bool}}
    Returns shadbala result for all planets
    """
    all_pos = {k: v["lon"] for k,v in planets_data.items()}
    result = {}
    for planet, data in planets_data.items():
        lon = data.get("lon", 0)
        house = data.get("house", 1)
        ub = _uchcha_bal(planet, lon)
        sb = _saptavarga_bal(planet, lon)
        sthana = round(ub + sb, 2)
        dig = _dig_bal(planet, house)
        paksha = _paksha_bal(planet, moon_lon, sun_lon)
        naisargik = NAISARGIK_BAL.get(planet, 0)
        cheshta = round(min(60, abs(lon % 30) * 2), 2)
        drik = _drik_bal(planet, lon, all_pos)
        total = round(sthana + dig + paksha + naisargik + cheshta + drik, 2)
        mn = SHADBALA_MIN.get(planet, 300)
        ishta = round(_math.sqrt(abs(ub * cheshta)), 2)
        kashta = round(_math.sqrt(abs((60-ub)*(60-cheshta))), 2)
        result[planet] = {
            "shadbala_virupas": total,
            "shadbala_rupas": round(total/60, 3),
            "minimum": mn,
            "strength": "strong" if total>=mn else ("medium" if total>=mn*0.75 else "weak"),
            "breakdown": {"sthana":sthana,"uchcha":ub,"saptavarga":sb,"dig":dig,"paksha_kala":paksha,"naisargik":naisargik,"cheshta":cheshta,"drik":drik},
            "ishta_phala": ishta,
            "kashta_phala": kashta
        }
    return result

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
    get_house_cusps, get_planet_house, get_vimshottari_dasha, get_yogini_dasha,
    check_mangal_dosha, get_tithi, get_yoga, get_karana,
    get_sunrise_sunset,
)


# Local modules (custom astrology logic)
from bhav_chalit import calculate_full_chalit_chakra
from mangal_dosha import analyze_mangal_dosha
from dasha_avastha import calculate_all_dasha_avasthaein

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
        dasha = get_vimshottari_dasha(jd, moon["longitude"], birth_dt)
        yogini = get_yogini_dasha(jd, moon["longitude"], birth_dt)
        return {
            'name': data.name, 'dob': data.dob, 'tob': data.tob,
            'place': {'lat': data.lat, 'lon': data.lon, 'tz': data.tz},
            'lagna': lagna, 'moon_nakshatra': moon['nakshatra'],
            'moon_rashi': moon['rashi'], 'planets': planets,
            'vimshottari_dasha': dasha, 'yogini_dasha': yogini
        }
    except Exception as e:
        raise HTTPException(500, f'Calculation error: {str(e)}')


# ═══ GRAHA AVASTHA ═══
AVASTHA_NAMES = ['Shayan','Upaveshan','Netrapani','Prakashana','Gamana','Agamana','Samavaas','Aagam','Bhojan','Nritya','Kautuk','Nidra']
GRAHA_NUM = {'Sun':1,'Moon':2,'Mars':3,'Mercury':4,'Jupiter':5,'Venus':6,'Saturn':7,'Rahu':8,'Ketu':9}
ASTA_DEGREES = {'Moon':12,'Mars':17,'Mercury':14,'Jupiter':11,'Venus':10,'Saturn':15}
UCCHA = {'Sun':'Mesh','Moon':'Vrishabh','Mars':'Makar','Mercury':'Kanya','Jupiter':'Kark','Venus':'Meen','Saturn':'Tula','Rahu':'Mithun','Ketu':'Dhanu'}
NEECHA = {'Sun':'Tula','Moon':'Vrishchik','Mars':'Kark','Mercury':'Meen','Jupiter':'Makar','Venus':'Kanya','Saturn':'Mesh'}
SWAGRUHI = {'Sun':['Simha'],'Moon':['Kark'],'Mars':['Mesh','Vrishchik'],'Mercury':['Mithun','Kanya'],'Jupiter':['Dhanu','Meen'],'Venus':['Vrishabh','Tula'],'Saturn':['Makar','Kumbh']}

def get_baladi_avastha(degree_in_rashi, is_odd_rashi=True):
    d = degree_in_rashi % 30
    if is_odd_rashi:
        if d < 6: return ('Baal', 25)
        elif d < 12: return ('Kumar', 50)
        elif d < 18: return ('Yuva', 100)
        elif d < 24: return ('Vriddha', 75)
        else: return ('Mrit', 0)
    else:
        if d < 6: return ('Mrit', 0)
        elif d < 12: return ('Vriddha', 75)
        elif d < 18: return ('Yuva', 100)
        elif d < 24: return ('Kumar', 50)
        else: return ('Baal', 25)

def check_asta(planet_name, planet_lon, sun_lon):
    if planet_name in ['Sun','Rahu','Ketu','Ascendant']: return False
    diff = abs(planet_lon - sun_lon)
    if diff > 180: diff = 360 - diff
    return diff <= ASTA_DEGREES.get(planet_name, 15)

def get_deeptadi_avastha(planet_name, rashi):
    if UCCHA.get(planet_name) == rashi: return 'Deeept (Uccha)'
    if NEECHA.get(planet_name) == rashi: return 'Khal (Neecha)'
    if rashi in SWAGRUHI.get(planet_name, []): return 'Swastha (Swagruhi)'
    return 'Shaant (Madhyam)'

def get_shayanadi_avastha(nak_num, graha_name, navamsha_num, lagna_rashi_num, janma_nak_num):
    try:
        graha_num = GRAHA_NUM.get(graha_name, 1)
        total = (nak_num * graha_num * navamsha_num) + lagna_rashi_num + janma_nak_num
        shesha = total % 12
        if shesha == 0: shesha = 12
        return AVASTHA_NAMES[shesha - 1]
    except: return 'Shayan'


NAAM_AKSHAR_ANK = {'a':1,'aa':1,'i':2,'ii':2,'u':3,'uu':3,'e':4,'ai':4,'o':5,'au':5,'k':1,'kh':2,'g':3,'gh':4,'ch':5,'c':5,'j':2,'jh':3,'t':3,'th':4,'d':4,'dh':2,'n':2,'p':3,'ph':4,'f':4,'b':5,'bh':1,'m':2,'y':3,'r':4,'l':5,'v':1,'w':1,'sh':2,'s':4,'h':5,'ksh':1,'tr':4}
GRAHA_DHRUVANK = {'Sun':5,'Moon':2,'Mars':2,'Mercury':3,'Jupiter':5,'Venus':3,'Saturn':3,'Rahu':0,'Ketu':0}
SHAYANADI_PHAL_ALL = {
'Sun':{'Shayan':'Apach, mandagni, pittashool, gupt rog, pair mein sujan','Upaveshan':'Karigar kaarya, garibi, vidyaheen, dukhi, doosron ka sevak','Netrapani':'5,9,7,10 bhaav — balwaan dhani. Anya bhaav — nishthur netrarogi','Prakashana':'Punyavaan, dharmic, dhani, daani, rajsi kul','Gamana':'Sadaiv pravas, rogyukt, nidra bhay krodhadi se yukt','Agamana':'Kroor, durbuddhi, kushal, dambhi, kanjoos, parastr mein rat','Samavaas':'Dharmic, dhani, anek vidyaaon se yukt, sundar netra, pavitra aacharan','Aagam':'Sadaiv dukhi, moorkh, kurup kintu dhani','Bhojan':'Stri putra dhan se rahit, jodo mein peeda, sir mein vishesh peeda','Nritya':'Pundit, sundar, vakvatur, shoolrogi, dharmic va dhani','Kautuk':'Utsaahi, mahan putra ka pita, daani, do patniyon wala','Nidra':'Sadaiv pravas, ling guda rogi, daridra, viklang, ati krodhi'},
'Moon':{'Shayan':'Swabhimani, sardi se jaldi prabhavit, kamuk, dhannaashak','Upaveshan':'Rogi, nirdhana, chalaak, kanjoos, mand buddhi','Netrapani':'Bade rog wala, dusht, bahut bolne wala, chalaak, kukaarmi','Prakashana':'Dhani, lamba majboot sharir, kanjoos, teertha premi','Gamana':'Dhanhin, kroorkaarmi, netrogi, shoolrogi, bhayaatur','Agamana':'Swabhimani, pairo mein peeda, gupt paapi, deen, mayavi','Samavaas':'Daani, dharmic, rajpujya, dhani, vaahna sukhi','Aagam':'Vaachal, dharmic, krishnapaksh mein do patniyon wala','Bhojan':'Pushta bimb — sukhi dhani. Ksheen bimb — sarp jal bhay','Nritya':'Balwaan — taktatvar dhani bhogi. Ksheen — rogi durbala','Kautuk':'Dhani, bahut putron wala, daani, anek vidyaaon ka jignasu','Nidra':'Klesh uthaane wala, paapi, rogi, sarvatra maara maara phirta'},
'Mars':{'Shayan':'Sharir par ghav, tvacha ke vividh rog. Lagnasth — pehli santan naash','Upaveshan':'Bahut nikrisht, dhani, kathor, nirdaya, paapi, rogi, viklang','Netrapani':'Lagna mein — netraheen, daridra. Anya — sharirik shithilta','Prakashana':'Dhani, jaldi tushtane wala, buddhimaan, baayein aankh mein chot','Gamana':'Sharir par ghav, stri se kalah, nirdhana, guda rogi','Agamana':'Dhani, aadar yukt, dharmik, prabhu kripa paatr','Samavaas':'Dharmik, adhik sampatti, uchvasth — bahut satva wala','Aagam':'Daksh dhani, bhogi, yash, swastha','Bhojan':'Mitha khane mein ruchi, apmaanit, mahakrodhi, ati utsaahi dhani','Nritya':'Rajpaksh se dhan labh, daani, bhogi, sukhi','Kautuk':'Mitron putron stri se yukt, anek sampattiyon wala, do patni','Nidra':'Dhanraihit, moorkh, mahakrodhi, neecharaagham'},
'Mercury':{'Shayan':'Bhookh se peedit, lumpat, dhoorta','Upaveshan':'Vaagmi, gunvaan, kavya karne wala, pavitra aacharan','Netrapani':'Pairon mein rog, vidya vinay se heen, putra bhi nasht','Prakashana':'Daansheel, dhani, anek vidyaaon se yukt, vedaarth ka gyata','Gamana':'Kaaryakushal, adhik lalchi, stri ke vash mein, kamdukhi','Agamana':'Paapaacharan, neech sangati, do putron wala','Samavaas':'Dhani, dharmic, chirarogi, samarthan prapt karne wala','Aagam':'Paapaacharan, neech sangati se dhan, gupt sthaaon mein rog','Bhojan':'Vaad vivaad se dhanhaani, raja bhay, shir mein rog','Nritya':'Dhani, vidwaan, kavi, prasannachit, sukhi','Kautuk':'Sabka priya, sangeetgya, tvacha mein rog','Nidra':'Bada rog, alpayu, vaad-vivadi, dhanhaani'},
'Jupiter':{'Shayan':'Kamzor swar, dukhi, atyadhik gora, lambi thuddi, shatruon se bhay','Upaveshan':'Dukhi, bahut bolne wala, muh haath pair mein ghav, rajbhay','Netrapani':'Shir mein rog, dhani, neech varn se priti, sangeet nritya premi','Prakashana':'Gunvaan, tejasvi, dhani. 1.10 mein — jagadguru athva raja','Gamana':'Paapi, laalchi, anek mitron wala, vidwaan, pravasik, dhani','Agamana':'Achhi patni wala, gunvaan, lokapriya','Samavaas':'Raja ka sevak ya sahyogi, vidwaan, sundar, kushal vakta dhani','Aagam':'Dharmik, shastraakar, naukr-chaakron va santan sukh yukt','Bhojan':'Maans bhakshan mein ruchi, dhani, kaamuk, santan ka sukh','Nritya':'Raja se sammaan, dhani, shaastragy, vyaakaran shastr ka gyata','Kautuk':'Dhani, apne kul mein agragany, ati aishwaryashali, shakti wala','Nidra':'Sab kaaryon mein moorkhta, garibi, ghar mein punay nahin'},
'Venus':{'Shayan':'Bahut krodhi, dant rogi, nirdhana, bahut lumpat','Upaveshan':'Balwaan, dharmik, dhani, daayein bhaag mein ghav, jodo mein dard','Netrapani':'Netra nasht, 1.7.10 mein — atyadhik garibi va sarvanash','Prakashana':'Kaavyashastr va sangeet ka vidwaan, dhani, dharmic, vaahan yukt','Gamana':'Maata jeevit nahi, baalpan mein rog, apne logon ka viyog','Agamana':'Pairon mein rog, sadaiv utsaahit, bada kalaakaar, dhani','Samavaas':'Raja ka ati vishwaspaatr, sab kaaryon mein kushal, shoolrog','Aagam':'Dhanhaani, stri sukh mein bahut anugrah, bhay yukt','Bhojan':'Kam paachan shakti, doosron ki naukri, bahut dhan kamaane wala','Nritya':'Kushal vakta, vidwaan, kavi, dhani, kaamuk, swabhimani','Kautuk':'Anek prakaar ke sukhon se yukt, maha rikshta, prasann rahne wala','Nidra':'Doosron ki naukri, ninda, veer, adhik bolne wala, bechain'},
'Saturn':{'Shayan':'Bhookh pyaas se peedit, ayushy prathm bhaag rogi, baad mein bhaagyavaan','Upaveshan':'Mote suze ya vaayuvikaar, daad aadi, rajpaksh se dhanhaani','Netrapani':'Moorakh hote hue bhi panditon ki tarah maany, dhani, dharmic','Prakashana':'Raja ka vishesh krupa paatr, dharmik, pandit, pavitra','Gamana':'Mahadhani, anek putron wala, pandit, gunvaan, shreshthi manushya','Agamana':'Pairon mein sujan, ati krodhi, kanjoos, par ninda karne wala','Samavaas':'Putra va dhan se yukt, seekhne padhne ko tatpar, anek ratnon se yukt','Aagam':'Lagna mein — bahut krodhi, rogi, saanp aadi sarispuon ke sambandh','Bhojan':'Apach, mandagni, bawaaseer, vayu shool, netrogi','Nritya':'Dhani, dharmic, vividh sampattiyon se yukt, sab sukh pane wala','Kautuk':'Raja ka vishwaspaatr, kaaryudaksh, dharmic, pandit','Nidra':'Dhani, vidwaan, pavitra aacharan, pittashool, do patniyon wala'},
'Rahu':{'Shayan':'Sadaiv mahan dukh va klesh. Mithun Sinh Vrishabh mein — sab sukh','Upaveshan':'Pairon mein rog, daad tvacharog, dhanhaani, bahut ghamandi','Netrapani':'Aankhon mein rog, dushton serpaaon shatruon va choron ka bhay','Prakashana':'Dharmik, sadaiv desh videshon mein, utsaahi, saatvik, rajkarmachaari','Gamana':'Bahut santaanon wala, vidwaan, dhani, daani, rajmaanya','Agamana':'Krodhi, dhan va buddhi se rahit, chalaak, kanjoos, kaamuk','Samavaas':'Vidwaan, kanjoos, anek gunon wala, dharmic, dhan yukt','Aagam':'Sab prakaar ke dukhon se yukt, mitron bandhuo ka naash','Bhojan':'Bhojan mein mushkil, viklang, mand buddhi, stri putra sukh se rahit','Nritya':'Dhani, bahut putron wala, daani, pandit, pittashool','Kautuk':'Sab gunon se yukt, nana dhano se dhani','Nidra':'Jeevan mein bahut shok, stri putron ko paane wala, dhairyashali'},
'Ketu':{'Shayan':'1.2.3.6 raashiyon mein dhanvarddhak. Anya raashiyon mein rogvarddhak','Upaveshan':'Tvacharogdayak, shatru raja chor aadi sarpdi ki shanka se peedit','Netrapani':'Netra mein rog, dushton sarpaadon se peedit, rajadi se peeda','Prakashana':'Dharmik, dhani, sadaiv pravas, utsaahi, rajsevak','Gamana':'Bahut putra, bahut dhan, vidwaan, gunvaan, daani','Agamana':'Anek rog, dhan ki haani, dant ghaati, mahaarogi, par nindak','Samavaas':'Vaachal, bahut garvita, dhoorta vidyaa visharad','Aagam':'Paap kaaryon mein agragany, bandhuo se vivaad, shatru rog peedit','Bhojan':'Sadaiv bhookh se peedit, daridra, rogi, maara maara phirta','Nritya':'Rog ke kaaran viklang, bahut palak jhapakne wali aankhein','Kautuk':'Apne star se gira hua, duraachari, dariddi, bhramak','Nidra':'Dhana dhaanya ka khub sukh, gunon va kalaaon se yukt hokar jeevan'},
}

def get_naam_akshar_ank(naam):
    if not naam: return 1
    naam = naam.lower().strip()
    for akshar in sorted(NAAM_AKSHAR_ANK.keys(), key=len, reverse=True):
        if naam.startswith(akshar):
            return NAAM_AKSHAR_ANK[akshar]
    return 1

def get_naam_cheshta(avastha_name, graha_name, naam):
    try:
        avastha_num = AVASTHA_NAMES.index(avastha_name) + 1
        naam_ank = get_naam_akshar_ank(naam)
        dhruvank = GRAHA_DHRUVANK.get(graha_name, 3)
        total = (avastha_num * avastha_num * naam_ank) + dhruvank
        shesha = total % 12
        final = shesha % 3
        if final == 1: return 'Drishti (Madhyam Phal)'
        elif final == 2: return 'Cheshta (Sampurna Phal)'
        else: return 'Vicheeshta (Matra Phal)'
    except: return 'Cheshta (Sampurna Phal)'

def get_shayanadi_phal_with_naam(graha_avastha_result, naam=''):
    enriched = {}
    for planet, data in graha_avastha_result.items():
        enriched[planet] = dict(data)
        shayanadi = data.get('shayanadi', 'Shayan')
        enriched[planet]['shayanadi_phal'] = SHAYANADI_PHAL_ALL.get(planet, {}).get(shayanadi, '')
        if naam:
            enriched[planet]['naam_cheshta'] = get_naam_cheshta(shayanadi, planet, naam)
    return enriched


# ═══ APRAKASHIT GRAHAS (5 Surya Mahadosha) ═══

def get_gulik_spasht(jd, birth_dt, birth_hour, lat, lon, tz):
    """
    Classical Gulik calculation per Brihat Parashara Hora Shastra.
    Uses REAL sunrise/sunset from Swiss Ephemeris (no hardcoding).
    
    Args:
        jd: Julian Day of birth
        birth_dt: datetime.date object
        birth_hour: Birth hour in local time (decimal)
        lat, lon: Birth place coordinates
        tz: Timezone offset (e.g., 5.5 for IST)
    
    Returns:
        dict with gulik_lagna, gulik_lagna_num, gulik_degree, khand, is_day_birth
    """
    try:
        import swisseph as swe
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Day of week: 0=Sun, 1=Mon, ..., 6=Sat
        # Python weekday(): Mon=0, Tue=1, ..., Sun=6
        dow_map = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:0}
        day_of_week = dow_map[birth_dt.weekday()]
        
        # Brihat Parashara: Shani's khand position (0-indexed) per day
        DAY_GULIK = {
            0: 6,   # Ravi (Sun) → 7th khand
            1: 5,   # Som (Mon) → 6th khand
            2: 4,   # Mangal (Tue) → 5th khand
            3: 3,   # Budh (Wed) → 4th khand
            4: 2,   # Guru (Thu) → 3rd khand
            5: 1,   # Shukra (Fri) → 2nd khand
            6: 0    # Shani (Sat) → 1st khand
        }
        
        # Night: 5th var from current var starts, then Shani's position
        NIGHT_GULIK = {
            0: 2,   # Ravi → 3rd khand (5th var=Guru, then Shukra, Shani)
            1: 1,   # Som → 2nd khand (5th=Shukra, then Shani)
            2: 0,   # Mangal → 1st khand (5th=Shani)
            3: 6,   # Budh → 7th khand (5th=Ravi, wrap)
            4: 5,   # Guru → 6th khand (5th=Som)
            5: 4,   # Shukra → 5th khand (5th=Mangal)
            6: 3    # Shani → 4th khand (5th=Budh)
        }
        
        # Get UTC JD for the birth date's 00:00 local time
        # Birth JD is already provided
        
        # Calculate REAL sunrise/sunset using Swiss Ephemeris
        geopos = (lon, lat, 0)
        
        # Sunrise: Search from previous midnight
        utc_midnight_jd = jd - (birth_hour / 24.0) + (tz / 24.0) * 0 - (birth_hour - 0) / 24.0
        # Simpler: use the day's start in UTC
        # birth_hour is local, tz is offset, so UTC hour = birth_hour - tz
        # For sunrise search, start a bit before the expected sunrise
        
        # Use swe.rise_trans for accuracy
        # Search window: start 24 hours before birth JD
        search_start_jd = jd - 1.0  # 1 day before birth
        
        # Find sunrise
        ret, sunrise_info = swe.rise_trans(
            search_start_jd, swe.SUN,
            swe.CALC_RISE | swe.BIT_HINDU_RISING,
            (lon, lat, 0)
        )
        sunrise_jd_utc = sunrise_info[0] if ret >= 0 else jd - 0.25
        
        # Find sunset (after sunrise)
        ret, sunset_info = swe.rise_trans(
            sunrise_jd_utc, swe.SUN,
            swe.CALC_SET | swe.BIT_HINDU_RISING,
            (lon, lat, 0)
        )
        sunset_jd_utc = sunset_info[0] if ret >= 0 else sunrise_jd_utc + 0.5
        
        # Find next sunrise (for night duration)
        ret, next_sunrise_info = swe.rise_trans(
            sunset_jd_utc, swe.SUN,
            swe.CALC_RISE | swe.BIT_HINDU_RISING,
            (lon, lat, 0)
        )
        next_sunrise_jd_utc = next_sunrise_info[0] if ret >= 0 else sunset_jd_utc + 0.5
        
        # Actual durations
        day_duration = sunset_jd_utc - sunrise_jd_utc  # In days (fraction)
        night_duration = next_sunrise_jd_utc - sunset_jd_utc
        
        # Determine if birth is day or night
        # Convert birth JD to compare: birth_jd_utc = jd (already UTC for proper comparison)
        # The passed `jd` should be the UTC Julian Day at birth moment
        birth_jd_utc = jd
        
        is_day_birth = sunrise_jd_utc <= birth_jd_utc <= sunset_jd_utc
        
        # Calculate Gulik JD
        if is_day_birth:
            khand = DAY_GULIK[day_of_week]
            gulik_jd = sunrise_jd_utc + (khand * day_duration / 8)
        else:
            khand = NIGHT_GULIK[day_of_week]
            gulik_jd = sunset_jd_utc + (khand * night_duration / 8)
        
        # Get ascendant at Gulik time
        cusps, ascmc = swe.houses(gulik_jd, lat, lon, b'P')
        ayanamsa = swe.get_ayanamsa_ut(gulik_jd)
        gulik_lon = (ascmc[0] - ayanamsa) % 360
        
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
                   'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        sign = int(gulik_lon / 30)
        degree = gulik_lon % 30
        d = int(degree)
        m = int((degree - d) * 60)
        
        return {
            'gulik_lagna': RASHI_N[sign],
            'gulik_lagna_num': sign + 1,
            'gulik_degree': f"{d}deg{m}min",
            'khand': khand + 1,  # Return 1-indexed for user display
            'is_day_birth': is_day_birth,
            'day_duration_hours': round(day_duration * 24, 2),
            'night_duration_hours': round(night_duration * 24, 2),
            'sunrise_local': round(((sunrise_jd_utc + 0.5) % 1) * 24 + tz, 2) % 24,
            'sunset_local': round(((sunset_jd_utc + 0.5) % 1) * 24 + tz, 2) % 24
        }
    except Exception as e:
        return {'error': str(e)}


def get_pranapada(sun_longitude, ishtkal_ghadi_pal):
    """
    Pranapada calculation per Brihat Parashara.
    
    Args:
        sun_longitude: Sun's sidereal longitude in degrees
        ishtkal_ghadi_pal: Ishtkal in ghadi (decimal, 1 ghadi = 24 minutes)
    
    Formula:
        - Multiply ishtkal_ghadi × 4 (book says "ghati × 4")
        - Wait, book says ghadi × 5/2 gives ishtkal pal
        - 90 pran = 15 pal = 1 Pranapada rashi
        - Pranapada jd = (ishtkal × 60 pal) / 1800 rashi count
    """
    try:
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
                   'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        
        # ishtkal_ghadi is already in ghadi, convert to pal
        ishtkal_pal = ishtkal_ghadi_pal * 60  # 1 ghadi = 60 pal
        
        # Divide by 15 to get rashi count and remainder
        rashi_count = int(ishtkal_pal / 15)
        shesha_pal = ishtkal_pal % 15
        
        # Double the shesha pal to get degrees (book says "bache hue pal ko 2 se guna")
        ansh = shesha_pal * 2  # degrees
        
        # Add to Sun's longitude (for Chara rashi; different for others)
        # Book: "Sun Chara rashi → add 1.5.9 (1, 5, or 9 rashi)"
        # Simplified: Just direct addition (most common method)
        pranapada_lon = (sun_longitude + (rashi_count * 30) + ansh) % 360
        
        sign = int(pranapada_lon / 30)
        degree = pranapada_lon % 30
        d = int(degree)
        m = int((degree - d) * 60)
        
        return {
            'pranapada_lagna': RASHI_N[sign],
            'pranapada_num': sign + 1,
            'pranapada_degree': f"{d}deg{m}min",
            'longitude': round(pranapada_lon, 4)
        }
    except Exception as e:
        return {'error': str(e)}


def get_aprakashit_grahas(sun_longitude):
    try:
        # 1. Dhoom = Sun + 4°13'20" = Sun + 4.2222°
        dhoom = (sun_longitude + 4.2222) % 360
        
        # 2. Vyatipaata = 12 Rashi (360) - Dhoom
        vyatipaata = (360 - dhoom) % 360
        
        # 3. Parivesh = Vyatipaata + 6 Rashi (180)
        parivesh = (vyatipaata + 180) % 360
        
        # 4. Indrachap = 12 Rashi (360) - Parivesh
        indrachap = (360 - parivesh) % 360
        
        # 5. Upaketu = Indrachap + 16°40' = 16.6667°
        upaketu = (indrachap + 16.6667) % 360
        
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
                   'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        
        def lon_to_rashi(lon):
            sign = int(lon / 30)
            degree = lon % 30
            d = int(degree)
            m = int((degree - d) * 60)
            return {'longitude': round(lon, 4), 'rashi': RASHI_N[sign], 
                    'rashi_num': sign + 1, 'degree': f"{d}°{m}'"}
        
        return {
            'dhoom': lon_to_rashi(dhoom),
            'vyatipaata': lon_to_rashi(vyatipaata),
            'parivesh': lon_to_rashi(parivesh),
            'indrachap': lon_to_rashi(indrachap),
            'upaketu': lon_to_rashi(upaketu),
            'note': 'Ye paanch Surya ke Mahadosha hain — Aprakashak Graha'
        }
    except Exception as e:
        return {'error': str(e)}

def get_gulik(jd, sunrise_jd, day_of_week, is_day_birth):
    try:
        import swisseph as swe
        # Day of week: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        # Gulik khand order for day: Sun=6, Mon=5, Tue=4, Wed=3, Thu=2, Fri=1, Sat=0
        # Each khand = daylight/8
        DAY_GULIK_KHAND = {0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0}
        NIGHT_GULIK_KHAND = {0:1, 1:0, 2:6, 3:5, 4:4, 5:3, 6:2}
        
        if is_day_birth:
            khand = DAY_GULIK_KHAND[day_of_week]
            day_duration = 0.5  # approximate 12 hours
            gulik_jd = sunrise_jd + (khand * day_duration / 8)
        else:
            khand = NIGHT_GULIK_KHAND[day_of_week]
            sunset_jd = sunrise_jd + 0.5
            night_duration = 0.5
            gulik_jd = sunset_jd + (khand * night_duration / 8)
        
        # Get lagna at gulik time
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(gulik_jd)
        # Simple approximation: use Sun position + time offset
        sun_lon = swe.calc_ut(gulik_jd, swe.SUN)[0][0]
        gulik_lon = (sun_lon - ayanamsa) % 360
        
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
                   'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        sign = int(gulik_lon / 30)
        degree = gulik_lon % 30
        
        return {
            'gulik_lagna': RASHI_N[sign],
            'gulik_lagna_num': sign + 1,
            'gulik_degree': round(degree, 2),
            'khand': khand
        }
    except Exception as e:
        return {'error': str(e)}

def get_all_graha_avastha(planets_data, lagna_data, sun_lon):
    result = {}
    lagna_rashi_num = lagna_data.get('rashi_num', 1)
    moon = planets_data.get('Moon', {})
    janma_nak_num = moon.get('nakshatra_num', 1)
    for name, p in planets_data.items():
        if name == 'Ascendant': continue
        degree = p.get('degree_in_rashi', 0)
        rashi = p.get('rashi', 'Mesh')
        rashi_num = p.get('rashi_num', 1)
        nak_num = p.get('nakshatra_num', 1)
        lon = p.get('longitude', 0)
        nav_num = int((degree % 30) / (30/9)) + 1
        is_odd = rashi_num % 2 == 1
        baladi, phal_percent = get_baladi_avastha(degree, is_odd)
        asta = check_asta(name, lon, sun_lon)
        deeptadi = get_deeptadi_avastha(name, rashi)
        shayanadi = get_shayanadi_avastha(nak_num, name, nav_num, lagna_rashi_num, janma_nak_num)
        result[name] = {
            'baladi': baladi, 'baladi_phal_percent': phal_percent,
            'asta': asta, 'deeptadi': deeptadi, 'shayanadi': shayanadi,
            'rashi': rashi, 'degree': round(degree, 2),
        }
    return result

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
        dasha = get_vimshottari_dasha(jd, moon["longitude"], birth_dt)
        yogini = get_yogini_dasha(jd, moon["longitude"], birth_dt)
        
        sun_lon = planets_with_houses.get('Sun', {}).get('longitude', 0)
        graha_avastha_raw = get_all_graha_avastha(planets_with_houses, lagna, sun_lon)
        # Special Lagnas
        try:
            from astro_engine import get_all_special_lagnas
            import swisseph as swe
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            birth_time_hours = int(data.tob.split(':')[0]) + int(data.tob.split(':')[1])/60
            utc_offset = data.tz
            birth_time_utc = birth_time_hours - utc_offset
            sunrise_jd = jd - (birth_time_hours/24) + ((6 - utc_offset)/24)
            moon_data = planets_with_houses.get('Moon', {})
            moon_lon_sid = moon_data.get('longitude', 0)
            asc_sid = lagna.get('longitude', 0)
            asc_num = lagna.get('rashi_num', 1)
            special_lagnas = get_all_special_lagnas(jd, asc_sid, asc_num, moon_lon_sid, sunrise_jd, birth_time_hours, data.lat, data.lon)
        except Exception as e:
            special_lagnas = {'error': str(e)}
        naam = getattr(data, 'name', '') or ''
        graha_avastha = get_shayanadi_phal_with_naam(graha_avastha_raw, naam)
        # Aprakashit Grahas
        sun_lon_tropical = planets_with_houses.get('Sun', {}).get('longitude', 0)
        import swisseph as swe
        ayanamsa = swe.get_ayanamsa_ut(jd)
        sun_lon_sid = (sun_lon_tropical - ayanamsa + ayanamsa) % 360
        aprakashit = get_aprakashit_grahas(sun_lon_sid)
        moon_lon_sid = planets_with_houses.get("Moon",{}).get("longitude",0) % 360
        lagna_trop = planets_with_houses.get("Lagna",{}).get("longitude", lagna.get("degree",0) if isinstance(lagna,dict) else 0)
        lagna_lon_sid = (float(str(lagna_trop).replace("°","").split("d")[0]) if lagna_trop else 0)
        avakhada = get_avakhada(moon_lon_sid, lagna_lon_sid, sun_lon_sid)
        import datetime
        dob_parts = data.dob.split('-')
        birth_dt = datetime.date(int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]))
        birth_hour = int(data.tob.split(':')[0]) + int(data.tob.split(':')[1])/60
        
        # Classical Gulik via Brihat Parashara (real sunrise/sunset)
        gulik = get_gulik_spasht(jd, birth_dt, birth_hour, data.lat, data.lon, data.tz)
        
        # Pranapada with real sunrise-based ishtkal
        try:
            import swisseph as swe
            ret, sunrise_info = swe.rise_trans(
                jd - 1.0, swe.SUN,
                swe.CALC_RISE | swe.BIT_HINDU_RISING,
                (data.lon, data.lat, 0)
            )
            sunrise_jd_utc = sunrise_info[0] if ret >= 0 else jd - 0.25
            ishtkal_days = jd - sunrise_jd_utc
            ishtkal_hours = ishtkal_days * 24
            ishtkal_ghadi = ishtkal_hours * 2.5
            pranapada = get_pranapada(sun_lon_sid, ishtkal_ghadi)
        except Exception as e:
            pranapada = {'error': f'Pranapada calc failed: {e}'}
        
        # BPHS Chapter 53 - Dasha Avasthaein
        dasha_avastha = calculate_all_dasha_avasthaein(planets_with_houses)
        
        return {
            'name': data.name, 'dob': data.dob, 'tob': data.tob,
            'place': {'lat': data.lat, 'lon': data.lon, 'tz': data.tz},
            'lagna': lagna, 'planets': planets_with_houses,
            'house_cusps': house_cusps, 'mangal_dosha': mangal,
            'vimshottari_dasha': dasha, 'yogini_dasha': yogini, 'graha_avastha': graha_avastha, 'dasha_avastha': dasha_avastha, 'special_lagnas': special_lagnas, 'aprakashit_grahas': aprakashit, 'gulik': gulik, 'pranapada': pranapada, 'avakhada': avakhada, 'shadbala': calculate_shadbala_all({p.lower(): {'lon': planets[p]['longitude'], 'house': planets[p].get('house',1)} for p in planets if p.lower() in ['sun','moon','mars','mercury','jupiter','venus','saturn']}, 0, 6, 18, planets.get('moon',{}).get('longitude',0), planets.get('sun',{}).get('longitude',0))
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post('/panchang')
def panchang(req: PanchangRequest):
    try:
        from astro_engine import NAKSHATRA_ML, RASHI_ML, TITHI_ML, YOGA_ML, KARANA_ML, WEEKDAY_ML, PAKSHA_ML, get_ml, get_choghadiya
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
            'tithi_deity': TITHI_DEITY.get(tithi_raw['number'], ''), 'planets': planets, 'choghadiya': get_choghadiya(req.date, sun_info['sunrise'], sun_info['sunset'], wd_idx)
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
        
        boy_mars_house = boy_planets.get('Mars', {}).get('house', 0)
        girl_mars_house = girl_planets.get('Mars', {}).get('house', 0)
        boy_mangal = check_mangal_dosha(boy_mars_house)
        girl_mangal = check_mangal_dosha(girl_mars_house)
        return {
            **ashtakoot,
            'boy': {'name': req.boy.name, 'nakshatra': boy_planets['Moon']['nakshatra']},
            'girl': {'name': req.girl.name, 'nakshatra': girl_planets['Moon']['nakshatra']},
            'mangal_dosha': {'male_has_dosha': boy_mangal['has_dosha'], 'female_has_dosha': girl_mangal['has_dosha'], 'description': boy_mangal['description'] + ' | ' + girl_mangal['description']}
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
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
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


# ═══════════════════════════════════════
# VARGA PHALADESH DICTIONARIES
# ═══════════════════════════════════════

HORA_PHAL = {
  'Sun_hora': 'Surya Hora (Simha) — Purusha graha adhik. Dhan kamane mein mehnat, raj se labh, pitri sampatti.',
  'Moon_hora': 'Chandra Hora (Kark) — Stri graha adhik. Maa se sampatti, vyapar mein safalta, griha sukh.',
}

DREKKANA_PHAL = {
  'Mesh': 'Parakrami, sahasik, agresiv swabhav. Bhai-behen se sahyog.',
  'Vrishabh': 'Dhani, kalapremi, sthir swabhav. Bhai-behen sukhi.',
  'Mithun': 'Buddhiman, vaachaal, kaushal. Bhai-behen se maitri.',
  'Kark': 'Bhaavuk, parivarik, caring. Bhai-behen se sneh.',
  'Simha': 'Tejasvi, shahi, netritv shakti. Bhai-behen mein bada.',
  'Kanya': 'Vyavharik, kushal, mehanti. Bhai-behen se sahyog.',
  'Tula': 'Nyaypriy, kalatmak, santulit. Bhai-behen sukhi.',
  'Vrishchik': 'Niddar, gehri soch, rahasyamayi. Bhai-behen se tanav.',
  'Dhanu': 'Dharmik, gyanvan, udaar. Bhai-behen se prem.',
  'Makar': 'Mehanti, anushasit, gambhir. Bhai-behen mein zimmedari.',
  'Kumbh': 'Navachar, samajsevi, unique. Bhai-behen alag swabhav.',
  'Meen': 'Sahisnu, kalpanasheel, aatmik. Bhai-behen se prem.',
}

SAPTAMSHA_PHAL = {
  'Mesh': 'Santan sahasik, pratapshali. Pehli santan putra sambhav.',
  'Vrishabh': 'Santan sundar, dhani, kalatmak. Sukhi santan.',
  'Mithun': 'Santan buddhiman, vaachaal. Do santan sambhav.',
  'Kark': 'Santan caring, sensitive. Maa se adhik lagav.',
  'Simha': 'Santan tejasvi, rajyog. Prabhavshaali vyaktitv.',
  'Kanya': 'Santan mehanti, kushal. Vyavsay mein safal.',
  'Tula': 'Santan sundar, nyaypriy. Vivah sukhi.',
  'Vrishchik': 'Santan niddar, intense. Gupt gyan mein ruchi.',
  'Dhanu': 'Santan dharmik, gyanvan. Uchchi shiksha premi.',
  'Makar': 'Santan mehanti, gambhir. Deri se santan sambhav.',
  'Kumbh': 'Santan unique, navachar. Technology mein ruchi.',
  'Meen': 'Santan aatmik, kalapremi. Adhyatm mein ruchi.',
}

DWADASHAMSHA_PHAL = {
  'Mesh': 'Pita sahasik, mehanti. Pitri sampatti mein vivad sambhav.',
  'Vrishabh': 'Mata sundar, dhani. Mata se griha sukh.',
  'Mithun': 'Mata-pita buddhiman. Uchchi shiksha pradan.',
  'Kark': 'Mata bahut caring, poshak. Mata se vishesh prem.',
  'Simha': 'Pita pratapshali, rajyog. Pitri sampatti labh.',
  'Kanya': 'Mata-pita vyavharik. Swasthya mein dhyan.',
  'Tula': 'Mata sundar, nyaypriy. Sukhi parivar.',
  'Vrishchik': 'Pita intense, niddar. Pitri sampatti mein kuch kasht.',
  'Dhanu': 'Mata-pita dharmik, udaar. Dharmik parivar.',
  'Makar': 'Pita mehanti, anushasit. Sampatti mein vridhi.',
  'Kumbh': 'Mata-pita progressive. Alag soch wala parivar.',
  'Meen': 'Mata bahut sahisnu, aatmik. Mata ka aashirvaad.',
}

TRISHAAMSHA_PHAL = {
  'Mesh': 'Mangal Trishaamsha — Rog: Rakta vikar, chot, aagnay rog. Savdhan rahein.',
  'Vrishabh': 'Shukra Trishaamsha — Rog: Mukh, gala, thyroid. Swabhav: Kaamukata.',
  'Mithun': 'Shani Trishaamsha — Rog: Vaat, naadi rog. Vivah mein badhayein.',
  'Kark': 'Budh Trishaamsha — Rog: Pet, manasik tanav. Careful rahein.',
  'Simha': 'Shani Trishaamsha — Rog: Hriday, peeth. Anushasan zaroori.',
  'Kanya': 'Budh Trishaamsha — Rog: Peth, antra. Shuddh aahar.',
  'Tula': 'Shukra Trishaamsha — Rog: Kidney, mootra. Jal adhik piyen.',
  'Vrishchik': 'Mangal Trishaamsha — Rog: Gupt ang, operations. Niddar.',
  'Dhanu': 'Guru Trishaamsha — Rog: Kamar, jaangh. Vyayam zaroori.',
  'Makar': 'Shani Trishaamsha — Rog: Ghutne, haddi. Calcium len.',
  'Kumbh': 'Shani Trishaamsha — Rog: Paer, naadimandal. Yoga karen.',
  'Meen': 'Guru Trishaamsha — Rog: Paer, kapha. Meditation zaroori.',
}

def get_varga_phaladesh(varga_results, lagna_vargas):
    try:
        result = {}
        
        # D2 Hora Phaladesh
        sun_d2 = varga_results.get('Sun', {}).get('D2', {})
        moon_d2 = varga_results.get('Moon', {}).get('D2', {})
        sun_hora = sun_d2.get('sign', '')
        moon_hora = moon_d2.get('sign', '')
        sun_hora_count = sum(1 for p, v in varga_results.items() 
                            if v.get('D2', {}).get('sign', '') in ['Simha', 'Mesh', 'Mithun', 'Tula', 'Dhanu', 'Kumbh'])
        moon_hora_count = sum(1 for p, v in varga_results.items() 
                             if v.get('D2', {}).get('sign', '') in ['Kark', 'Vrishabh', 'Kanya', 'Vrishchik', 'Makar', 'Meen'])
        if sun_hora_count >= moon_hora_count:
            hora_phal = HORA_PHAL['Sun_hora']
        else:
            hora_phal = HORA_PHAL['Moon_hora']
        result['D2_hora'] = {
            'sun_hora_planets': sun_hora_count,
            'moon_hora_planets': moon_hora_count,
            'phaladesh': hora_phal
        }
        
        # D3 Drekkana Phaladesh
        d3_lagna = lagna_vargas.get('D3', {})
        d3_lagna_sign = d3_lagna.get('sign', 'Mesh')
        result['D3_drekkana'] = {
            'lagna': d3_lagna_sign,
            'phaladesh': DREKKANA_PHAL.get(d3_lagna_sign, '')
        }
        
        # D7 Saptamsha Phaladesh
        d7_lagna = lagna_vargas.get('D7', {})
        d7_lagna_sign = d7_lagna.get('sign', 'Mesh')
        result['D7_saptamsha'] = {
            'lagna': d7_lagna_sign,
            'phaladesh': SAPTAMSHA_PHAL.get(d7_lagna_sign, '')
        }
        
        # D12 Dwadashamsha Phaladesh
        d12_lagna = lagna_vargas.get('D12', {})
        d12_lagna_sign = d12_lagna.get('sign', 'Mesh')
        result['D12_dwadashamsha'] = {
            'lagna': d12_lagna_sign,
            'phaladesh': DWADASHAMSHA_PHAL.get(d12_lagna_sign, '')
        }
        
        # D30 Trishaamsha Phaladesh
        d30_lagna = lagna_vargas.get('D30', {})
        d30_lagna_sign = d30_lagna.get('sign', 'Mesh')
        result['D30_trishaamsha'] = {
            'lagna': d30_lagna_sign,
            'phaladesh': TRISHAAMSHA_PHAL.get(d30_lagna_sign, '')
        }
        
        return result
    except Exception as e:
        return {'error': str(e)}


def get_swamsha_lagna(varga_results, karkamsha_sign):
    # Swamsha = D9 chart with AK rashi as lagna
    # karkamsha_sign already calculated from /varga
    return {'swamsha_lagna': karkamsha_sign, 'note': 'Graha D9 ke anusaar, Lagna AK ki Navamsha rashi'}
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
        swamsha = get_swamsha_lagna(varga_results, karkamsha.get('karkamsha_lagna') if isinstance(karkamsha, dict) else karkamsha); return {'varga_charts': varga_results, 'lagna_vargas': lagna_vargas, 'karkamsha_lagna': karkamsha, 'pada_lagna': pada, 'upapada_lagna': upapada, 'navamsha_analysis': navamsha_analysis, 'varga_phaladesh': get_varga_phaladesh(varga_results, lagna_vargas), 'swamsha_lagna': swamsha}
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
        
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
        gmodel = genai.GenerativeModel('gemini-2.5-flash')
        resp = gmodel.generate_content(prompt)
        text = resp.text.strip().replace('```json','').replace('```','').strip()
        outlook = jsonlib.loads(text)
        return {'outlook': outlook, 'transit': transit}
    except Exception as e:
        raise HTTPException(500, str(e))

# ============================================================================
# Bhav Spasht + Chalit Chakra (Sripati method) — IGNOU Unit 4
# Integrates with existing /kundali endpoint shape (BirthData, parse_birth,
# get_lagna, get_all_planets), uses Swiss Ephemeris for Dashmalagna (MC).
# ============================================================================


class BhavChalitRequest(BaseModel):
    name: str = "Jatak"
    dob: str       # "YYYY-MM-DD"
    tob: str       # "HH:MM"
    lat: float
    lon: float
    timezone: float = 5.5
    place: str = ""


def _get_dashmalagna_longitude(jd: float, lat: float, lon: float) -> float:
    """Return nirayana (sidereal Lahiri) Dashmalagna / MC in decimal degrees."""
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus; we only need MC
    sayana_mc = ascmc[1]  # index 1 = MC
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return (sayana_mc - ayanamsa) % 360


@app.post('/bhav-chalit')
def bhav_chalit(data: BirthData):
    """
    Sripati method Bhav Spasht + Chalit Chakra.
    Takes the same BirthData as /kundali.
    """
    try:
        jd, birth_dt = parse_birth(data)
        lagna = get_lagna(jd, data.lat, data.lon)
        planets = get_all_planets(jd)
        dashm_deg = _get_dashmalagna_longitude(jd, data.lat, data.lon)

        graha_positions = {name: p['longitude'] for name, p in planets.items()}

        result = calculate_full_chalit_chakra(
            lagna_deg=lagna['longitude'],
            dashmalagna_deg=dashm_deg,
            graha_positions=graha_positions,
        )
        # Add inputs for debugging / frontend context
        result['inputs'] = {
            'lagna_deg': lagna['longitude'],
            'dashmalagna_deg': dashm_deg,
        }
        return result
    except Exception as e:
        raise HTTPException(500, f"bhav-chalit error: {str(e)}")

# ============================================================================
# Mangal Dosha Complete (v2) — with 3 references + 6 bhang rules + chalit
# Classical Parashar Light implementation
# ============================================================================


def _navamsha_rashi_num(longitude: float) -> int:
    """D9 (Navamsha) rashi number (1-12) from sidereal longitude."""
    # Each navamsha = 3°20' (3.3333°), 108 navamshas in zodiac, 9 per rashi
    navamsha_index = int(longitude / (30.0 / 9.0))  # 0-107
    return (navamsha_index % 12) + 1


@app.post('/mangal-dosha-full')
def mangal_dosha_full(data: BirthData):
    """
    Complete classical Mangal Dosha analysis from 3 references:
      - Lagna
      - Chandra rashi
      - Navamsha D9 Lagna
    With 6 bhang rules including chalit sandhi check.
    """
    try:
        jd, birth_dt = parse_birth(data)
        planets = get_all_planets(jd)
        lagna = get_lagna(jd, data.lat, data.lon)

        # Build planets_by_name with required fields
        planets_by_name = {}
        for name, p in planets.items():
            planets_by_name[name] = {
                "longitude": p.get("longitude", 0),
                "rashi_num": p.get("rashi_num", 0),
                "retrograde": p.get("retrograde", False),
            }

        mars_data = planets_by_name.get("Mars", {})
        moon_data = planets_by_name.get("Moon", {})

        # Navamsha calculations
        lagna_lon = lagna.get("longitude", 0)
        navamsha_lagna_num = _navamsha_rashi_num(lagna_lon)
        navamsha_mars_num = _navamsha_rashi_num(mars_data.get("longitude", 0))

        # Chalit — compute Mangal's vishopak bal from chalit chakra
        mars_chalit_vishopak = None
        try:
            import swisseph as swe
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            cusps, ascmc = swe.houses(jd, data.lat, data.lon, b'P')
            ayanamsa = swe.get_ayanamsa_ut(jd)
            dashm_deg = (ascmc[1] - ayanamsa) % 360

            graha_positions = {n: p["longitude"] for n, p in planets_by_name.items()}
            chalit_result = calculate_full_chalit_chakra(
                lagna_deg=lagna_lon,
                dashmalagna_deg=dashm_deg,
                graha_positions=graha_positions,
            )
            mars_chalit = chalit_result.get("chalit_positions", {}).get("Mars", {})
            mars_chalit_vishopak = mars_chalit.get("vishopak_bal")
        except Exception:
            pass

        # Run analysis
        result = analyze_mangal_dosha(
            jatak_name=data.name or "जातक",
            lagna_rashi_num=lagna.get("rashi_num", 1),
            chandra_rashi_num=moon_data.get("rashi_num", 1),
            navamsha_lagna_rashi_num=navamsha_lagna_num,
            mars_data=mars_data,
            navamsha_mars_rashi_num=navamsha_mars_num,
            planets_by_name=planets_by_name,
            mars_chalit_vishopak=mars_chalit_vishopak,
        )

        # Compute intensity score
        active_count = sum(1 for c in result["checks"] if c["final_has_dosha"])
        intensity_map = {0: "none", 1: "low", 2: "medium", 3: "high"}
        result["intensity"] = intensity_map[active_count]
        result["active_ref_count"] = active_count
        result["total_ref_count"] = 3

        return result
    except Exception as e:
        raise HTTPException(500, f"mangal-dosha error: {str(e)}")
