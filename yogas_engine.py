"""
═══════════════════════════════════════════════════════════════════
YOGAS DETECTION ENGINE
═══════════════════════════════════════════════════════════════════
Source: Brihat Parashara Hora Shastra (विविधयोगाध्याय)
Hindi Vyakhya: Pandit Suresh Mishra
Curated by: Pandit Harishchandra Purohit (Jyotish Rishi)

This module detects classical Vedic yogas from a kundli chart.
Returns list of detected yogas with classical references.
═══════════════════════════════════════════════════════════════════
"""

from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

PLANETS = {
    'Sun': 'सूर्य',
    'Moon': 'चन्द्रमा',
    'Mars': 'मंगल',
    'Mercury': 'बुध',
    'Jupiter': 'गुरु',
    'Venus': 'शुक्र',
    'Saturn': 'शनि',
    'Rahu': 'राहु',
    'Ketu': 'केतु'
}

SHUBH_GRAHAS = ['Jupiter', 'Venus', 'Mercury', 'Moon']  # शुभ ग्रह
PAAP_GRAHAS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']  # पाप ग्रह

# Exaltation rashis (उच्च राशि)
EXALTATION = {
    'Sun': 1,        # मेष
    'Moon': 2,       # वृषभ
    'Mars': 10,      # मकर
    'Mercury': 6,    # कन्या
    'Jupiter': 4,    # कर्क
    'Venus': 12,     # मीन
    'Saturn': 7,     # तुला
}

# Debilitation rashis (नीच राशि)
DEBILITATION = {
    'Sun': 7,        # तुला
    'Moon': 8,       # वृश्चिक
    'Mars': 4,       # कर्क
    'Mercury': 12,   # मीन
    'Jupiter': 10,   # मकर
    'Venus': 6,      # कन्या
    'Saturn': 1,     # मेष
}

# Own rashis (स्व राशि)
OWN_RASHIS = {
    'Sun': [5],
    'Moon': [4],
    'Mars': [1, 8],
    'Mercury': [3, 6],
    'Jupiter': [9, 12],
    'Venus': [2, 7],
    'Saturn': [10, 11],
}

# Rashi lords (राशि स्वामी)
RASHI_LORDS = {
    1: 'Mars', 2: 'Venus', 3: 'Mercury', 4: 'Moon',
    5: 'Sun', 6: 'Mercury', 7: 'Venus', 8: 'Mars',
    9: 'Jupiter', 10: 'Saturn', 11: 'Saturn', 12: 'Jupiter'
}

# Friendship table (नैसर्गिक मित्रता)
FRIENDSHIP = {
    'Sun':     {'friends': ['Moon', 'Mars', 'Jupiter'], 'enemies': ['Venus', 'Saturn']},
    'Moon':    {'friends': ['Sun', 'Mercury'], 'enemies': []},
    'Mars':    {'friends': ['Sun', 'Moon', 'Jupiter'], 'enemies': ['Mercury']},
    'Mercury': {'friends': ['Sun', 'Venus'], 'enemies': ['Moon']},
    'Jupiter': {'friends': ['Sun', 'Moon', 'Mars'], 'enemies': ['Mercury', 'Venus']},
    'Venus':   {'friends': ['Mercury', 'Saturn'], 'enemies': ['Sun', 'Moon']},
    'Saturn':  {'friends': ['Mercury', 'Venus'], 'enemies': ['Sun', 'Moon', 'Mars']},
}

# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def calculate_house_from(planet_rashi: int, reference_rashi: int) -> int:
    """Calculate which house a planet is in from a reference point."""
    diff = (planet_rashi - reference_rashi) % 12
    return diff + 1  # 1-indexed

def is_in_kendra_from(planet_rashi: int, reference_rashi: int) -> bool:
    """Check if planet is in Kendra (1, 4, 7, 10) from reference."""
    house = calculate_house_from(planet_rashi, reference_rashi)
    return house in [1, 4, 7, 10]

def is_in_trikona_from(planet_rashi: int, reference_rashi: int) -> bool:
    """Check if planet is in Trikona (1, 5, 9) from reference."""
    house = calculate_house_from(planet_rashi, reference_rashi)
    return house in [1, 5, 9]

def is_exalted(planet: str, rashi: int) -> bool:
    """Check if planet is in exaltation."""
    return EXALTATION.get(planet) == rashi

def is_debilitated(planet: str, rashi: int) -> bool:
    """Check if planet is in debilitation."""
    return DEBILITATION.get(planet) == rashi

def is_in_own_rashi(planet: str, rashi: int) -> bool:
    """Check if planet is in its own rashi."""
    return rashi in OWN_RASHIS.get(planet, [])

def get_friendship(planet1: str, planet2: str) -> str:
    """Get friendship relation between two planets."""
    if planet1 == planet2:
        return 'self'
    if planet2 in FRIENDSHIP[planet1]['friends']:
        return 'friend'
    if planet2 in FRIENDSHIP[planet1]['enemies']:
        return 'enemy'
    return 'neutral'

def has_drishti(from_planet_house: int, to_house: int) -> bool:
    """Check if a planet has drishti on a house."""
    # All planets aspect 7th
    if (to_house - from_planet_house) % 12 == 6:
        return True
    return False

# ═══════════════════════════════════════════════════════════════════
# YOGA DETECTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def detect_gaja_kesari(chart: Dict) -> Optional[Dict]:
    """
    गजकेसरी योग
    चन्द्रमा से केन्द्र में गुरु
    
    Reference: BPHS विविधयोगाध्याय श्लोक 3-4 (पृष्ठ 261)
    """
    moon_rashi = chart['planets']['Moon']['rashi']
    jupiter_rashi = chart['planets']['Jupiter']['rashi']
    
    if is_in_kendra_from(jupiter_rashi, moon_rashi):
        # Check Jupiter is not debilitated
        if not is_debilitated('Jupiter', jupiter_rashi):
            return {
                'id': 'gaja_kesari',
                'detected': True,
                'reason': 'चन्द्रमा से केन्द्र में गुरु स्थित हैं',
                'strength': 'strong' if is_exalted('Jupiter', jupiter_rashi) or is_in_own_rashi('Jupiter', jupiter_rashi) else 'medium'
            }
    return None

def detect_amala(chart: Dict) -> Optional[Dict]:
    """
    अमला योग
    लग्न या चन्द्र से 10वें भाव में बलवान शुभ ग्रह
    
    Reference: BPHS विविधयोगाध्याय श्लोक 5-6 (पृष्ठ 261)
    """
    lagna_rashi = chart['lagna']['rashi']
    moon_rashi = chart['planets']['Moon']['rashi']
    
    # Check 10th from Lagna
    tenth_from_lagna = ((lagna_rashi + 9 - 1) % 12) + 1
    # Check 10th from Moon
    tenth_from_moon = ((moon_rashi + 9 - 1) % 12) + 1
    
    for planet in SHUBH_GRAHAS:
        planet_rashi = chart['planets'][planet]['rashi']
        if planet_rashi == tenth_from_lagna or planet_rashi == tenth_from_moon:
            # Check planet is strong (own rashi or exalted)
            if is_in_own_rashi(planet, planet_rashi) or is_exalted(planet, planet_rashi):
                return {
                    'id': 'amala',
                    'detected': True,
                    'reason': f'{PLANETS[planet]} दशम भाव में बली स्थिति में',
                    'strength': 'strong'
                }
    return None

def detect_ruchaka(chart: Dict) -> Optional[Dict]:
    """
    रुचक योग (पंच महापुरुष — मंगल)
    मंगल केन्द्र में स्व राशि या उच्च का
    """
    mars_rashi = chart['planets']['Mars']['rashi']
    lagna_rashi = chart['lagna']['rashi']
    
    if is_in_kendra_from(mars_rashi, lagna_rashi):
        if is_exalted('Mars', mars_rashi) or is_in_own_rashi('Mars', mars_rashi):
            return {
                'id': 'ruchaka',
                'detected': True,
                'reason': 'मंगल केन्द्र में स्वराशि/उच्च का है',
                'strength': 'strong'
            }
    return None

def detect_bhadra(chart: Dict) -> Optional[Dict]:
    """भद्र योग (पंच महापुरुष — बुध)"""
    mercury_rashi = chart['planets']['Mercury']['rashi']
    lagna_rashi = chart['lagna']['rashi']
    
    if is_in_kendra_from(mercury_rashi, lagna_rashi):
        if is_exalted('Mercury', mercury_rashi) or is_in_own_rashi('Mercury', mercury_rashi):
            return {
                'id': 'bhadra',
                'detected': True,
                'reason': 'बुध केन्द्र में स्वराशि/उच्च का है',
                'strength': 'strong'
            }
    return None

def detect_hamsa(chart: Dict) -> Optional[Dict]:
    """हंस योग (पंच महापुरुष — गुरु)"""
    jupiter_rashi = chart['planets']['Jupiter']['rashi']
    lagna_rashi = chart['lagna']['rashi']
    
    if is_in_kendra_from(jupiter_rashi, lagna_rashi):
        if is_exalted('Jupiter', jupiter_rashi) or is_in_own_rashi('Jupiter', jupiter_rashi):
            return {
                'id': 'hamsa',
                'detected': True,
                'reason': 'गुरु केन्द्र में स्वराशि/उच्च का है',
                'strength': 'strong'
            }
    return None

def detect_malavya(chart: Dict) -> Optional[Dict]:
    """मालव्य योग (पंच महापुरुष — शुक्र)"""
    venus_rashi = chart['planets']['Venus']['rashi']
    lagna_rashi = chart['lagna']['rashi']
    
    if is_in_kendra_from(venus_rashi, lagna_rashi):
        if is_exalted('Venus', venus_rashi) or is_in_own_rashi('Venus', venus_rashi):
            return {
                'id': 'malavya',
                'detected': True,
                'reason': 'शुक्र केन्द्र में स्वराशि/उच्च का है',
                'strength': 'strong'
            }
    return None

def detect_shasha(chart: Dict) -> Optional[Dict]:
    """शश योग (पंच महापुरुष — शनि)"""
    saturn_rashi = chart['planets']['Saturn']['rashi']
    lagna_rashi = chart['lagna']['rashi']
    
    if is_in_kendra_from(saturn_rashi, lagna_rashi):
        if is_exalted('Saturn', saturn_rashi) or is_in_own_rashi('Saturn', saturn_rashi):
            return {
                'id': 'shasha',
                'detected': True,
                'reason': 'शनि केन्द्र में स्वराशि/उच्च का है',
                'strength': 'strong'
            }
    return None

def detect_budh_aditya(chart: Dict) -> Optional[Dict]:
    """
    बुधादित्य योग
    सूर्य + बुध एक भाव में
    """
    sun_rashi = chart['planets']['Sun']['rashi']
    mercury_rashi = chart['planets']['Mercury']['rashi']
    
    if sun_rashi == mercury_rashi:
        return {
            'id': 'budh_aditya',
            'detected': True,
            'reason': 'सूर्य व बुध एक ही भाव में स्थित हैं',
            'strength': 'medium'
        }
    return None

def detect_chandra_mangal(chart: Dict) -> Optional[Dict]:
    """
    चन्द्र-मंगल योग
    चन्द्र + मंगल एक भाव में
    """
    moon_rashi = chart['planets']['Moon']['rashi']
    mars_rashi = chart['planets']['Mars']['rashi']
    
    if moon_rashi == mars_rashi:
        return {
            'id': 'chandra_mangal',
            'detected': True,
            'reason': 'चन्द्रमा व मंगल एक ही भाव में स्थित हैं',
            'strength': 'medium'
        }
    return None

def detect_kemadruma(chart: Dict) -> Optional[Dict]:
    """
    केमद्रुम योग (अशुभ)
    चन्द्रमा से 2 व 12 दोनों भाव खाली
    """
    moon_rashi = chart['planets']['Moon']['rashi']
    second_from_moon = (moon_rashi % 12) + 1
    twelfth_from_moon = ((moon_rashi - 2) % 12) + 1
    
    second_empty = True
    twelfth_empty = True
    
    for planet, data in chart['planets'].items():
        if planet == 'Moon':
            continue
        if data['rashi'] == second_from_moon:
            second_empty = False
        if data['rashi'] == twelfth_from_moon:
            twelfth_empty = False
    
    if second_empty and twelfth_empty:
        return {
            'id': 'kemadruma',
            'detected': True,
            'reason': 'चन्द्रमा से 2 व 12 दोनों भाव खाली हैं',
            'strength': 'caution'
        }
    return None

def detect_vipareet_raj(chart: Dict) -> List[Dict]:
    """
    विपरीत राज योग (BPHS Classical Definition)
    
    हर्ष — 6th lord in 6, 8, or 12 (any dusthana)
    सरला — 8th lord in 6, 8, or 12 (any dusthana)
    विमल — 12th lord in 6, 8, or 12 (any dusthana)
    """
    detected = []
    lagna_rashi = chart['lagna']['rashi']
    
    # Get lords of 6, 8, 12 from Lagna
    sixth_lord_rashi = (lagna_rashi + 5 - 1) % 12 + 1
    eighth_lord_rashi = (lagna_rashi + 7 - 1) % 12 + 1
    twelfth_lord_rashi = (lagna_rashi + 11 - 1) % 12 + 1
    
    sixth_lord = RASHI_LORDS[sixth_lord_rashi]
    eighth_lord = RASHI_LORDS[eighth_lord_rashi]
    twelfth_lord = RASHI_LORDS[twelfth_lord_rashi]
    
    # Where are these lords placed?
    sixth_lord_placed = chart['planets'][sixth_lord]['rashi']
    eighth_lord_placed = chart['planets'][eighth_lord]['rashi']
    twelfth_lord_placed = chart['planets'][twelfth_lord]['rashi']
    
    house_of_sixth_lord = calculate_house_from(sixth_lord_placed, lagna_rashi)
    house_of_eighth_lord = calculate_house_from(eighth_lord_placed, lagna_rashi)
    house_of_twelfth_lord = calculate_house_from(twelfth_lord_placed, lagna_rashi)
    
    DUSTHANAS = [6, 8, 12]
    
    # हर्ष योग — 6th lord in any dusthana (6, 8, 12)
    if house_of_sixth_lord in DUSTHANAS:
        detected.append({
            'id': 'vipareet_harsha',
            'detected': True,
            'reason': f'षष्ठेश ({PLANETS[sixth_lord]}) {house_of_sixth_lord}वें भाव में स्थित (दुःस्थान)',
            'strength': 'strong'
        })
    
    # सरला योग — 8th lord in any dusthana (6, 8, 12)
    if house_of_eighth_lord in DUSTHANAS:
        detected.append({
            'id': 'sarala',
            'detected': True,
            'reason': f'अष्टमेश ({PLANETS[eighth_lord]}) {house_of_eighth_lord}वें भाव में स्थित (दुःस्थान)',
            'strength': 'strong'
        })
    
    # विमल योग — 12th lord in any dusthana (6, 8, 12)
    if house_of_twelfth_lord in DUSTHANAS:
        detected.append({
            'id': 'vipareet_vimala',
            'detected': True,
            'reason': f'द्वादशेश ({PLANETS[twelfth_lord]}) {house_of_twelfth_lord}वें भाव में स्थित (दुःस्थान)',
            'strength': 'strong'
        })
    
    return detected

def detect_neech_bhanga(chart: Dict) -> List[Dict]:
    """
    नीच भंग राज योग
    Multiple conditions for cancellation of debilitation
    """
    detected = []
    lagna_rashi = chart['lagna']['rashi']
    
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        planet_rashi = chart['planets'][planet]['rashi']
        
        if is_debilitated(planet, planet_rashi):
            # Condition 1: Lord of debilitation rashi is in Kendra from Lagna or Moon
            debil_rashi_lord = RASHI_LORDS[planet_rashi]
            lord_rashi = chart['planets'][debil_rashi_lord]['rashi']
            
            if is_in_kendra_from(lord_rashi, lagna_rashi):
                detected.append({
                    'id': f'neech_bhanga_{planet.lower()}',
                    'detected': True,
                    'reason': f'{PLANETS[planet]} नीच का है, परन्तु नीचभंग राजयोग बन रहा है',
                    'strength': 'medium'
                })
    
    return detected

# ═══════════════════════════════════════════════════════════════════
# MASTER DETECTION FUNCTION
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 7 NEW YOGAS DETECTION FUNCTIONS
# Source: BPHS Chapter 34 (Vividha Yogadhyaya)
# Pages 265-267 from PDF
# ═══════════════════════════════════════════════════════════


def detect_shankh(chart):
    """
    शंख योग — 5th + 6th lord in kendra mutual aspect
    OR Lagnesh + 10th lord in moveable rashi (chara) + 9th lord strong
    """
    lagna_rashi = chart['lagna']['rashi']
    
    fifth_lord_rashi = (lagna_rashi + 4 - 1) % 12 + 1
    sixth_lord_rashi = (lagna_rashi + 5 - 1) % 12 + 1
    ninth_lord_rashi = (lagna_rashi + 8 - 1) % 12 + 1
    tenth_lord_rashi = (lagna_rashi + 9 - 1) % 12 + 1
    
    fifth_lord = RASHI_LORDS[fifth_lord_rashi]
    sixth_lord = RASHI_LORDS[sixth_lord_rashi]
    ninth_lord = RASHI_LORDS[ninth_lord_rashi]
    tenth_lord = RASHI_LORDS[tenth_lord_rashi]
    lagnesh = RASHI_LORDS[lagna_rashi]
    
    fifth_in = chart['planets'][fifth_lord]['rashi']
    sixth_in = chart['planets'][sixth_lord]['rashi']
    lagnesh_in = chart['planets'][lagnesh]['rashi']
    tenth_in = chart['planets'][tenth_lord]['rashi']
    
    house_fifth = calculate_house_from(fifth_in, lagna_rashi)
    house_sixth = calculate_house_from(sixth_in, lagna_rashi)
    house_lagnesh = calculate_house_from(lagnesh_in, lagna_rashi)
    house_tenth = calculate_house_from(tenth_in, lagna_rashi)
    
    KENDRA = [1, 4, 7, 10]
    CHARA_RASHIS = [1, 4, 7, 10]  # Mesh, Karka, Tula, Makara
    
    # Method 1: 5th & 6th lord in kendra mutually
    if house_fifth in KENDRA and house_sixth in KENDRA:
        return {
            'id': 'shankh',
            'detected': True,
            'reason': f'पंचमेश ({PLANETS[fifth_lord]}) व षष्ठेश ({PLANETS[sixth_lord]}) केन्द्र में परस्पर स्थित',
            'strength': 'strong'
        }
    
    # Method 2: Lagnesh + 10th lord in chara rashi + 9th lord strong
    if (lagnesh_in in CHARA_RASHIS and tenth_in in CHARA_RASHIS):
        return {
            'id': 'shankh',
            'detected': True,
            'reason': f'लग्नेश ({PLANETS[lagnesh]}) व दशमेश ({PLANETS[tenth_lord]}) चर राशि में स्थित',
            'strength': 'medium'
        }
    
    return None


def detect_bheri(chart):
    """
    भेरी योग — 10th lord strong + planets in 1, 2, 7, 12
    OR 9th lord strong + Lagnesh + Venus in kendra
    """
    lagna_rashi = chart['lagna']['rashi']
    
    ninth_lord_rashi = (lagna_rashi + 8 - 1) % 12 + 1
    tenth_lord_rashi = (lagna_rashi + 9 - 1) % 12 + 1
    
    ninth_lord = RASHI_LORDS[ninth_lord_rashi]
    tenth_lord = RASHI_LORDS[tenth_lord_rashi]
    lagnesh = RASHI_LORDS[lagna_rashi]
    
    ninth_in = chart['planets'][ninth_lord]['rashi']
    lagnesh_in = chart['planets'][lagnesh]['rashi']
    venus_in = chart['planets']['Venus']['rashi']
    
    house_ninth = calculate_house_from(ninth_in, lagna_rashi)
    house_lagnesh = calculate_house_from(lagnesh_in, lagna_rashi)
    house_venus = calculate_house_from(venus_in, lagna_rashi)
    
    KENDRA = [1, 4, 7, 10]
    
    # 9th lord strong + Lagnesh + Venus all in kendra
    if (house_ninth in KENDRA and 
        house_lagnesh in KENDRA and 
        house_venus in KENDRA):
        return {
            'id': 'bheri',
            'detected': True,
            'reason': f'नवमेश, लग्नेश व शुक्र तीनों केन्द्र में स्थित',
            'strength': 'strong'
        }
    
    return None


def detect_mridang(chart):
    """
    मृदंग योग — Exalted planet's navamsha lord in kendra/trikona + Lagnesh strong
    Simplified: Any planet in own/exalted in kendra or trikona + Lagnesh balwan
    """
    lagna_rashi = chart['lagna']['rashi']
    lagnesh = RASHI_LORDS[lagna_rashi]
    lagnesh_in = chart['planets'][lagnesh]['rashi']
    house_lagnesh = calculate_house_from(lagnesh_in, lagna_rashi)
    
    KENDRA_TRIKONA = [1, 4, 5, 7, 9, 10]
    EXALTATION = {'Sun': 1, 'Moon': 2, 'Mars': 10, 'Mercury': 6, 
                  'Jupiter': 4, 'Venus': 12, 'Saturn': 7}
    OWN_RASHIS = {'Sun': [5], 'Moon': [4], 'Mars': [1, 8], 
                  'Mercury': [3, 6], 'Jupiter': [9, 12], 
                  'Venus': [2, 7], 'Saturn': [10, 11]}
    
    if house_lagnesh not in KENDRA_TRIKONA:
        return None
    
    for planet, exalt_rashi in EXALTATION.items():
        p_rashi = chart['planets'][planet]['rashi']
        p_house = calculate_house_from(p_rashi, lagna_rashi)
        
        is_strong = (p_rashi == exalt_rashi or 
                    p_rashi in OWN_RASHIS.get(planet, []))
        
        if is_strong and p_house in KENDRA_TRIKONA:
            return {
                'id': 'mridang',
                'detected': True,
                'reason': f'{PLANETS[planet]} स्वराशि/उच्च में केन्द्र-त्रिकोण में, लग्नेश बली',
                'strength': 'strong'
            }
    
    return None


def detect_shrinath(chart):
    """
    श्रीनाथ योग — 7th lord in 10th + 9th & 10th lords together + 7th lord exalted
    """
    lagna_rashi = chart['lagna']['rashi']
    
    seventh_lord_rashi = (lagna_rashi + 6 - 1) % 12 + 1
    ninth_lord_rashi = (lagna_rashi + 8 - 1) % 12 + 1
    tenth_lord_rashi = (lagna_rashi + 9 - 1) % 12 + 1
    
    seventh_lord = RASHI_LORDS[seventh_lord_rashi]
    ninth_lord = RASHI_LORDS[ninth_lord_rashi]
    tenth_lord = RASHI_LORDS[tenth_lord_rashi]
    
    seventh_in = chart['planets'][seventh_lord]['rashi']
    ninth_in = chart['planets'][ninth_lord]['rashi']
    tenth_in = chart['planets'][tenth_lord]['rashi']
    
    house_seventh = calculate_house_from(seventh_in, lagna_rashi)
    
    EXALTATION = {'Sun': 1, 'Moon': 2, 'Mars': 10, 'Mercury': 6, 
                  'Jupiter': 4, 'Venus': 12, 'Saturn': 7}
    
    # 7th lord in 10th + 9th & 10th lords same rashi + 7th lord exalted
    seventh_exalted = (seventh_in == EXALTATION.get(seventh_lord))
    nine_ten_together = (ninth_in == tenth_in)
    
    if house_seventh == 10 and nine_ten_together and seventh_exalted:
        return {
            'id': 'shrinath',
            'detected': True,
            'reason': f'सप्तमेश ({PLANETS[seventh_lord]}) उच्च होकर 10वें में, नवमेश-दशमेश साथ',
            'strength': 'strong'
        }
    
    return None


def detect_sharada(chart):
    """
    शारदा योग — 10th lord in 5th + Mercury in kendra + Sun in own rashi (Simha)
    OR Jupiter in trikona from Moon + Mars in 11th + Mercury 11th from Sun
    """
    lagna_rashi = chart['lagna']['rashi']
    
    tenth_lord_rashi = (lagna_rashi + 9 - 1) % 12 + 1
    tenth_lord = RASHI_LORDS[tenth_lord_rashi]
    tenth_in = chart['planets'][tenth_lord]['rashi']
    house_tenth = calculate_house_from(tenth_in, lagna_rashi)
    
    mercury_in = chart['planets']['Mercury']['rashi']
    house_mercury = calculate_house_from(mercury_in, lagna_rashi)
    
    sun_in = chart['planets']['Sun']['rashi']
    
    KENDRA = [1, 4, 7, 10]
    
    # Method 1: 10th lord in 5th + Mercury in kendra + Sun in Simha (own)
    if house_tenth == 5 and house_mercury in KENDRA and sun_in == 5:
        return {
            'id': 'sharada',
            'detected': True,
            'reason': f'दशमेश पंचम में, बुध केन्द्र में, सूर्य स्वराशि में',
            'strength': 'strong'
        }
    
    return None


def detect_matsya(chart):
    """
    मत्स्य योग — Shubh in 1 or 9 + Shubh+Paap in 5 + Paap in 4 or 8
    """
    lagna_rashi = chart['lagna']['rashi']
    
    SHUBH = ['Jupiter', 'Venus', 'Mercury', 'Moon']
    PAAP = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
    
    house_count = {}
    for planet, p_data in chart['planets'].items():
        h = calculate_house_from(p_data['rashi'], lagna_rashi)
        if h not in house_count:
            house_count[h] = {'shubh': 0, 'paap': 0}
        if planet in SHUBH:
            house_count[h]['shubh'] += 1
        elif planet in PAAP:
            house_count[h]['paap'] += 1
    
    # Conditions
    shubh_in_1_or_9 = (house_count.get(1, {}).get('shubh', 0) > 0 or 
                       house_count.get(9, {}).get('shubh', 0) > 0)
    
    h5 = house_count.get(5, {})
    mixed_in_5 = h5.get('shubh', 0) > 0 and h5.get('paap', 0) > 0
    
    paap_in_4_or_8 = (house_count.get(4, {}).get('paap', 0) > 0 or 
                      house_count.get(8, {}).get('paap', 0) > 0)
    
    if shubh_in_1_or_9 and mixed_in_5 and paap_in_4_or_8:
        return {
            'id': 'matsya',
            'detected': True,
            'reason': '1/9 में शुभ, 5 में शुभ-पाप मिश्र, 4/8 में पाप ग्रह',
            'strength': 'medium'
        }
    
    return None


def detect_kurma(chart):
    """
    कूर्म योग — Shubh in 5,6,7 + Paap in 1,3,11 + planets in own/exalted/mool/mitra
    """
    lagna_rashi = chart['lagna']['rashi']
    
    SHUBH = ['Jupiter', 'Venus', 'Mercury', 'Moon']
    PAAP = ['Sun', 'Mars', 'Saturn']
    
    house_count = {}
    for planet, p_data in chart['planets'].items():
        h = calculate_house_from(p_data['rashi'], lagna_rashi)
        if h not in house_count:
            house_count[h] = {'shubh': 0, 'paap': 0}
        if planet in SHUBH:
            house_count[h]['shubh'] += 1
        elif planet in PAAP:
            house_count[h]['paap'] += 1
    
    # Shubh in 5, 6, 7
    shubh_5 = house_count.get(5, {}).get('shubh', 0) > 0
    shubh_6 = house_count.get(6, {}).get('shubh', 0) > 0
    shubh_7 = house_count.get(7, {}).get('shubh', 0) > 0
    
    # Paap in 1, 3, 11
    paap_1 = house_count.get(1, {}).get('paap', 0) > 0
    paap_3 = house_count.get(3, {}).get('paap', 0) > 0
    paap_11 = house_count.get(11, {}).get('paap', 0) > 0
    
    if shubh_5 and shubh_6 and shubh_7 and paap_1 and paap_3 and paap_11:
        return {
            'id': 'kurma',
            'detected': True,
            'reason': '5,6,7 में शुभ ग्रह व 1,3,11 में पाप ग्रह स्थित',
            'strength': 'strong'
        }
    
    return None


def detect_all_yogas(chart: Dict) -> Dict:
    """
    Detect all yogas from a kundli chart.
    
    Args:
        chart: Dict with structure:
            {
                'lagna': {'rashi': 1-12, 'degree': 0-30},
                'planets': {
                    'Sun': {'rashi': 1-12, 'degree': 0-30, 'house': 1-12},
                    'Moon': {...},
                    ...
                }
            }
    
    Returns:
        Dict with detected yogas categorized
    """
    
    detected_yogas = []
    
    # Run all detection functions
    detectors = [
        detect_gaja_kesari,
        detect_amala,
        detect_ruchaka,
        detect_bhadra,
        detect_hamsa,
        detect_malavya,
        detect_shasha,
        detect_budh_aditya,
        detect_chandra_mangal,
        detect_kemadruma,
        detect_shankh,
        detect_bheri,
        detect_mridang,
        detect_shrinath,
        detect_sharada,
        detect_matsya,
        detect_kurma,
    ]
    
    for detector in detectors:
        result = detector(chart)
        if result:
            detected_yogas.append(result)
    
    # Multi-result detectors
    detected_yogas.extend(detect_vipareet_raj(chart))
    detected_yogas.extend(detect_neech_bhanga(chart))
    
    # Categorize
    summary = {
        'total_yogas': len(detected_yogas),
        'shubh_count': sum(1 for y in detected_yogas if y['id'] not in ['kemadruma']),
        'ashubh_count': sum(1 for y in detected_yogas if y['id'] in ['kemadruma']),
        'mahapurush_count': sum(1 for y in detected_yogas if y['id'] in ['ruchaka', 'bhadra', 'hamsa', 'malavya', 'shasha']),
        'raj_yoga_count': sum(1 for y in detected_yogas if 'raj' in y['id'] or y['id'] in ['sarala', 'vimal', 'harsha']),
        'detected_yogas': detected_yogas
    }
    
    return summary


# ═══════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Sample test chart
    sample_chart = {
        'lagna': {'rashi': 1, 'degree': 15},  # Mesh Lagna
        'planets': {
            'Sun': {'rashi': 1, 'degree': 10},      # Mesh
            'Moon': {'rashi': 4, 'degree': 5},      # Kark (Moon in own)
            'Mars': {'rashi': 1, 'degree': 20},     # Mesh (Mars in own)
            'Mercury': {'rashi': 12, 'degree': 25}, # Meen
            'Jupiter': {'rashi': 4, 'degree': 15},  # Kark (Jupiter exalted)
            'Venus': {'rashi': 2, 'degree': 10},    # Vrishabh (Venus own)
            'Saturn': {'rashi': 7, 'degree': 18},   # Tula (Saturn exalted)
            'Rahu': {'rashi': 3, 'degree': 5},
            'Ketu': {'rashi': 9, 'degree': 5},
        }
    }
    
    result = detect_all_yogas(sample_chart)
    
    print("═══════════════════════════════════════════")
    print(f"Total Yogas Detected: {result['total_yogas']}")
    print(f"Mahapurush Yogas: {result['mahapurush_count']}")
    print(f"Raj Yogas: {result['raj_yoga_count']}")
    print("═══════════════════════════════════════════\n")
    
    for yoga in result['detected_yogas']:
        print(f"✅ {yoga['id'].upper()}")
        print(f"   Reason: {yoga['reason']}")
        print(f"   Strength: {yoga['strength']}\n")
