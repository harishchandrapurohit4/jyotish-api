import re

SHADBALA_CODE = '''
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
'''

content = open('/root/jyotish-api/main.py').read()

# Add shadbala code after imports block
insert_after = 'from astro_additions import router as astro_router'
content = content.replace(insert_after, insert_after + '\n' + SHADBALA_CODE, 1)

# Find return statement in kundali endpoint and add shadbala
# Find planets dict in response - add shadbala before final return
old_return = 'return {"status": "success"'
new_shadbala_call = '''
    # Shadbala calculation
    try:
        _planets_for_bal = {}
        for _p in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
            _pdata = planets.get(_p, {})
            if _pdata:
                _planets_for_bal[_p] = {"lon": _pdata.get("longitude",0), "house": _pdata.get("house",1)}
        _sb_result = calculate_shadbala_all(_planets_for_bal, birth_hour_decimal, sunrise_decimal, sunset_decimal, planets.get("moon",{}).get("longitude",0), planets.get("sun",{}).get("longitude",0)) if _planets_for_bal else {}
    except Exception as _e:
        _sb_result = {"error": str(_e)}
    '''
content = content.replace(old_return, new_shadbala_call + old_return, 1)

# Add shadbala to return dict
old_ret2 = '"aprakashit_grahas":'
content = content.replace(old_ret2, '"shadbala": _sb_result,\n        "aprakashit_grahas":', 1)

open('/root/jyotish-api/main.py', 'w').write(content)
print("Shadbala added!")
