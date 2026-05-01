"""
Mangal Dosha Classical Analysis
================================
Authentic Vedic method with paap grah counting + cancellation

Logic:
- Boy: Count UNIQUE paap grahas in {1,4,7,8,12 from Lagna OR Chandra} OR {7 from Shukra}
- Girl: Count UNIQUE paap grahas in {1,4,7,8,12 from Lagna OR Chandra} OR {7 from Guru}
- Compare boy vs girl
- Equal: Cancelled (vivah safe)
- Boy > Girl: Vivah possible
- Girl > Boy: Astrologer consultation MUST

Paap grahas: Sun, Mars, Saturn, Rahu, Ketu (5 total)
"""

import swisseph as swe
from datetime import datetime
from typing import Dict, List

PAAP_GRAHAS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']

PAAP_HINDI = {
    'Sun': 'सूर्य',
    'Mars': 'मंगल',
    'Saturn': 'शनि',
    'Rahu': 'राहु',
    'Ketu': 'केतु'
}

PLANET_IDS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE  # Rahu = Mean Node
}

RASHI_NAMES = ['Mesh', 'Vrishabh', 'Mithun', 'Kark', 'Simha', 'Kanya',
               'Tula', 'Vrishchik', 'Dhanu', 'Makar', 'Kumbh', 'Meen']

RASHI_HINDI = ['मेष', 'वृषभ', 'मिथुन', 'कर्क', 'सिंह', 'कन्या',
               'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']


def get_planet_positions(birth_data: dict) -> dict:
    """
    Get all planet positions and Lagna for a birth chart
    Returns: {
        'lagna_idx': 0-11,
        'planets': {
            'Sun': rashi_idx,
            'Moon': rashi_idx,
            'Mars': rashi_idx,
            ...
        }
    }
    """
    dt = datetime.strptime(f"{birth_data['date']} {birth_data['time']}", "%Y-%m-%d %H:%M")
    ut_hour = dt.hour + dt.minute / 60.0 - birth_data.get('timezone', 5.5)
    
    swe.set_ephe_path('/root/jyotish-api/ephe')
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(dt.year, dt.month, dt.day, ut_hour)
    
    # Lagna
    lat = birth_data['latitude']
    lon = birth_data['longitude']
    houses = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    lagna_lon = houses[0][0] % 360
    lagna_idx = int(lagna_lon / 30)
    
    # Planets
    planets = {}
    for name, pid in PLANET_IDS.items():
        lon_p = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0][0] % 360
        planets[name] = int(lon_p / 30)
    
    # Ketu = Rahu + 180
    planets['Ketu'] = (planets['Rahu'] + 6) % 12
    
    return {
        'lagna_idx': lagna_idx,
        'planets': planets
    }


def count_paaps_in_bhavs(planets: dict, reference_idx: int, target_bhavs: list) -> List[dict]:
    """
    Count paap grahas in given bhavs from reference point
    Returns list of {paap_name, bhav, reference}
    """
    results = []
    for paap in PAAP_GRAHAS:
        if paap not in planets:
            continue
        paap_idx = planets[paap]
        bhav = ((paap_idx - reference_idx) % 12) + 1
        if bhav in target_bhavs:
            results.append({
                'paap': paap,
                'paap_hindi': PAAP_HINDI[paap],
                'bhav': bhav,
                'rashi': RASHI_NAMES[paap_idx]
            })
    return results


def check_mangal_dosha_classical(birth_data: dict, person: str = 'boy') -> dict:
    """
    Classical Mangal Dosha check with proper paap counting
    
    Boy: Lagna/Chandra (1,4,7,8,12) + Shukra (7) ← 7th from Venus
    Girl: Lagna/Chandra (1,4,7,8,12) + Guru (7) ← 7th from Jupiter
    
    UNIQUE paap count - same paap multiple positions = 1 count
    """
    chart = get_planet_positions(birth_data)
    lagna_idx = chart['lagna_idx']
    planets = chart['planets']
    
    chandra_idx = planets['Moon']
    
    # Reference points based on gender
    if person == 'boy':
        third_ref_idx = planets['Venus']  # Shukra
        third_ref_name = 'Shukra'
        third_ref_hindi = 'शुक्र'
    else:  # girl
        third_ref_idx = planets['Jupiter']  # Guru
        third_ref_name = 'Guru'
        third_ref_hindi = 'गुरु'
    
    # Check from Lagna (1,4,7,8,12)
    from_lagna = count_paaps_in_bhavs(planets, lagna_idx, [1, 4, 7, 8, 12])
    
    # Check from Chandra (1,4,7,8,12)
    from_chandra = count_paaps_in_bhavs(planets, chandra_idx, [1, 4, 7, 8, 12])
    
    # Check from Shukra/Guru (only 7th)
    from_third = count_paaps_in_bhavs(planets, third_ref_idx, [7])
    
    # Combine UNIQUE paaps (same paap counted only once)
    unique_paaps = {}
    
    for entry in from_lagna:
        paap_name = entry['paap']
        if paap_name not in unique_paaps:
            unique_paaps[paap_name] = {
                'paap': paap_name,
                'paap_hindi': PAAP_HINDI[paap_name],
                'rashi': entry['rashi'],
                'positions': []
            }
        unique_paaps[paap_name]['positions'].append(f"लग्न से {entry['bhav']}वें भाव")
    
    for entry in from_chandra:
        paap_name = entry['paap']
        if paap_name not in unique_paaps:
            unique_paaps[paap_name] = {
                'paap': paap_name,
                'paap_hindi': PAAP_HINDI[paap_name],
                'rashi': entry['rashi'],
                'positions': []
            }
        unique_paaps[paap_name]['positions'].append(f"चंद्र से {entry['bhav']}वें भाव")
    
    for entry in from_third:
        paap_name = entry['paap']
        if paap_name not in unique_paaps:
            unique_paaps[paap_name] = {
                'paap': paap_name,
                'paap_hindi': PAAP_HINDI[paap_name],
                'rashi': entry['rashi'],
                'positions': []
            }
        unique_paaps[paap_name]['positions'].append(f"{third_ref_hindi} से {entry['bhav']}वें भाव")
    
    paap_list = list(unique_paaps.values())
    paap_count = len(paap_list)
    
    # Bhang conditions (classical) - for premium display
    bhang_conditions = []
    mars_idx = planets['Mars']
    
    if paap_count > 0:
        # Mars in own sign (Mesh/Vrishchik)
        if mars_idx in [0, 7]:
            bhang_conditions.append(f"मंगल स्वराशि ({RASHI_HINDI[mars_idx]}) में है — दोष शान्त")
        # Mars in exaltation
        if mars_idx == 9:
            bhang_conditions.append("मंगल उच्च राशि (मकर) में — दोष भंग")
        # Mars-Jupiter conjunction or close
        if abs(mars_idx - planets['Jupiter']) <= 1 or abs(mars_idx - planets['Jupiter']) >= 11:
            bhang_conditions.append("मंगल-गुरु साथ या समीप — दोष शान्त")
        # Mars in Kendra/Trikona from Moon
        mars_from_moon = ((mars_idx - chandra_idx) % 12) + 1
        if mars_from_moon in [1, 4, 5, 7, 9, 10]:
            bhang_conditions.append(f"मंगल चंद्र से शुभ स्थान ({mars_from_moon}वें) में — आंशिक भंग")
    
    return {
        'person': person,
        'paap_count': paap_count,
        'paap_details': paap_list,
        'lagna_rashi': RASHI_NAMES[lagna_idx],
        'chandra_rashi': RASHI_NAMES[chandra_idx],
        'mars_rashi': RASHI_NAMES[mars_idx],
        f'{third_ref_name.lower()}_rashi': RASHI_NAMES[third_ref_idx],
        'has_dosha': paap_count > 0,
        'severity': 'High' if paap_count >= 3 else ('Medium' if paap_count >= 1 else 'None'),
        'bhang_conditions': bhang_conditions,
        'has_bhang': len(bhang_conditions) > 0
    }


def compare_mangal_dosha(boy_data: dict, girl_data: dict) -> dict:
    """
    CLASSICAL CANCELLATION LOGIC
    
    Compare boy vs girl paap counts
    - Equal → Cancelled (vivah safe)
    - Boy > Girl → Vivah possible
    - Girl > Boy → Astrologer consultation MUST
    """
    boy_dosha = check_mangal_dosha_classical(boy_data, 'boy')
    girl_dosha = check_mangal_dosha_classical(girl_data, 'girl')
    
    boy_count = boy_dosha['paap_count']
    girl_count = girl_dosha['paap_count']
    
    # Cancellation logic
    if boy_count == 0 and girl_count == 0:
        status = 'NO_DOSHA'
        verdict_hindi = '✅ दोनों कुंडलियों में मंगल दोष नहीं है'
        verdict_en = 'No Mangal Dosha in either chart'
        recommendation = 'विवाह योग्य — कोई बाधा नहीं'
        color = 'green'
        cancelled_count = 0
        remaining_side = None
        remaining_count = 0
    elif boy_count == girl_count:
        status = 'CANCELLED'
        verdict_hindi = f'✅ दोनों कुंडलियों में बराबर पाप ({boy_count}={girl_count}) — दोष भंग'
        verdict_en = f'Equal dosha ({boy_count}={girl_count}) - CANCELLED'
        recommendation = 'विवाह कर सकते हैं — दोष भंग हो रहा है'
        color = 'green'
        cancelled_count = boy_count
        remaining_side = None
        remaining_count = 0
    elif boy_count > girl_count:
        status = 'BOY_HIGHER'
        diff = boy_count - girl_count
        verdict_hindi = f'⚠️ वर की कुंडली में अधिक पाप ({boy_count} vs {girl_count}) — विवाह संभव'
        verdict_en = f'Boy higher ({boy_count} vs {girl_count}) - Marriage possible'
        recommendation = 'विवाह कर सकते हैं — वर पक्ष में दोष अधिक होने पर भी ग्राह्य'
        color = 'yellow'
        cancelled_count = girl_count
        remaining_side = 'boy'
        remaining_count = diff
    else:  # girl_count > boy_count
        status = 'GIRL_HIGHER'
        diff = girl_count - boy_count
        verdict_hindi = f'🚨 वधु की कुंडली में अधिक पाप ({girl_count} vs {boy_count}) — ज्योतिष परामर्श अनिवार्य'
        verdict_en = f'Girl higher ({girl_count} vs {boy_count}) - Astrologer consultation MUST'
        recommendation = 'ज्योतिषाचार्य परामर्श अवश्य लें — विशेष उपाय आवश्यक'
        color = 'red'
        cancelled_count = boy_count
        remaining_side = 'girl'
        remaining_count = diff
    
    return {
        'boy_dosha': boy_dosha,
        'girl_dosha': girl_dosha,
        'boy_count': boy_count,
        'girl_count': girl_count,
        'status': status,
        'verdict_hindi': verdict_hindi,
        'verdict_en': verdict_en,
        'recommendation': recommendation,
        'color': color,
        'cancelled_count': cancelled_count,
        'remaining_side': remaining_side,
        'remaining_count': remaining_count,
        'has_dosha': boy_count > 0 or girl_count > 0,
        'is_serious': status == 'GIRL_HIGHER',
        'upay': _generate_upay(boy_dosha, girl_dosha, status)
    }


def _generate_upay(boy_dosha, girl_dosha, status):
    """Generate specific upay based on which paaps are present"""
    upay_list = []
    
    # Common upay
    upay_list.append("मंगलवार को हनुमान चालीसा 11 बार पाठ")
    
    # Specific upay based on remaining paaps
    if status == 'GIRL_HIGHER':
        upay_list.append("कन्या के लिए: मंगल दोष शान्ति पूजा (विशेष)")
        upay_list.append("कुम्भ विवाह या अश्वत्थ विवाह करवाएं")
    
    if status in ['BOY_HIGHER', 'GIRL_HIGHER']:
        # Check which paaps are common
        all_paaps = set()
        for p in boy_dosha.get('paap_details', []):
            all_paaps.add(p['paap'])
        for p in girl_dosha.get('paap_details', []):
            all_paaps.add(p['paap'])
        
        if 'Sun' in all_paaps:
            upay_list.append("सूर्य उपाय: रविवार को सूर्य अर्घ्य, आदित्य हृदय स्तोत्र")
        if 'Mars' in all_paaps:
            upay_list.append("मंगल उपाय: मंगलवार व्रत, मंगल यंत्र धारण")
        if 'Saturn' in all_paaps:
            upay_list.append("शनि उपाय: शनिवार हनुमान पूजा, सरसों तेल दान")
        if 'Rahu' in all_paaps:
            upay_list.append("राहु उपाय: राहु मंत्र जाप, गोमेद धारण")
        if 'Ketu' in all_paaps:
            upay_list.append("केतु उपाय: केतु मंत्र, लहसुनिया धारण")
    
    return upay_list
