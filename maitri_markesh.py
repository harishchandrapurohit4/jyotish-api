"""
Panchadha Maitri + Markesh Detection Module
Based on BPHS classical references
"""

# Planet indices: Sun=0, Moon=1, Mars=2, Mercury=3, Jupiter=4, Venus=5, Saturn=6
# Naisargik Maitri Matrix (Natural Friendship)
# 2=Mitra (Friend), 1=Sama (Neutral), 0=Shatru (Enemy)
NAISARGIK_PF = [
    [2, 2, 2, 2, 1, 0, 0],  # Sun
    [2, 2, 1, 1, 2, 1, 1],  # Moon
    [2, 2, 2, 2, 0, 0, 1],  # Mars
    [2, 2, 2, 2, 0, 1, 1],  # Mercury
    [2, 0, 1, 1, 2, 2, 1],  # Jupiter
    [1, 0, 1, 1, 2, 2, 2],  # Venus
    [0, 0, 1, 0, 2, 2, 2],  # Saturn
]

# Rashi Lord mapping
RASHI_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
# Mesha=Mars(2), Vrish=Venus(5), Mithun=Mercury(3), Karka=Moon(1)
# Sinha=Sun(0), Kanya=Mercury(3), Tula=Venus(5), Vrishchik=Mars(2)
# Dhanu=Jupiter(4), Makar=Saturn(6), Kumbh=Saturn(6), Meen=Jupiter(4)

PLANET_NAMES_HI = ['सूर्य', 'चन्द्र', 'मंगल', 'बुध', 'गुरु', 'शुक्र', 'शनि']
PLANET_NAMES_EN = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']


def get_house_distance(planet_house, target_house):
    """Calculate house distance from planet to target"""
    return ((target_house - planet_house) % 12) + 1


def calculate_tatkal_maitri(planet_idx, planet_house, all_planet_houses):
    """
    Tatkal Maitri (Temporary friendship) - BPHS
    Based on house position from given planet
    
    Houses 2,3,4,10,11,12 from planet = Mitra
    Houses 1,5,6,7,8,9 from planet = Shatru
    
    Returns dict {planet_idx: 'mitra' or 'shatru'}
    """
    result = {}
    for other_idx, other_house in all_planet_houses.items():
        if other_idx == planet_idx:
            continue
        distance = get_house_distance(planet_house, other_house)
        if distance in [2, 3, 4, 10, 11, 12]:
            result[other_idx] = 'mitra'
        else:  # 1, 5, 6, 7, 8, 9
            result[other_idx] = 'shatru'
    return result


def calculate_panchadha_maitri(planet_idx, planet_house, all_planet_houses):
    """
    Panchadha Maitri (5-fold friendship) = Naisargik + Tatkal combination
    
    Matrix:
    Naisargik \ Tatkal | Mitra      | Shatru
    -------------------|------------|------------
    Mitra (2)          | Adhimitra  | Sama
    Sama (1)           | Mitra      | Shatru
    Shatru (0)         | Sama       | Param Shatru
    
    Returns dict with 5 levels
    """
    if planet_idx >= 7:  # Rahu/Ketu - skip for now
        return {}
    
    tatkal = calculate_tatkal_maitri(planet_idx, planet_house, all_planet_houses)
    result = {}
    
    for other_idx, tatkal_rel in tatkal.items():
        if other_idx >= 7:  # Skip Rahu/Ketu
            continue
        
        naisargik_value = NAISARGIK_PF[planet_idx][other_idx]
        # 2=Mitra, 1=Sama, 0=Shatru
        
        if naisargik_value == 2 and tatkal_rel == 'mitra':
            relationship = 'adhimitra'
            level = 5
            hindi = 'अधि मित्र'
            color = 'green'
        elif naisargik_value == 2 and tatkal_rel == 'shatru':
            relationship = 'sama'
            level = 3
            hindi = 'सम'
            color = 'yellow'
        elif naisargik_value == 1 and tatkal_rel == 'mitra':
            relationship = 'mitra'
            level = 4
            hindi = 'मित्र'
            color = 'blue'
        elif naisargik_value == 1 and tatkal_rel == 'shatru':
            relationship = 'shatru'
            level = 2
            hindi = 'शत्रु'
            color = 'orange'
        elif naisargik_value == 0 and tatkal_rel == 'mitra':
            relationship = 'sama'
            level = 3
            hindi = 'सम'
            color = 'yellow'
        else:  # naisargik=0, tatkal='shatru'
            relationship = 'param_shatru'
            level = 1
            hindi = 'परम शत्रु'
            color = 'red'
        
        result[other_idx] = {
            'planet': PLANET_NAMES_EN[other_idx],
            'planet_hindi': PLANET_NAMES_HI[other_idx],
            'relationship': relationship,
            'hindi_name': hindi,
            'level': level,
            'color': color
        }
    
    return result


def detect_markesh(planets_data, lagna_rashi):
    """
    Markesh = 2nd or 7th house lord (mritu karaka)
    
    BPHS:
    - 2nd lord = Maraka (death-causer)
    - 7th lord = Maraka
    - These planets ki dasha mein kasht
    
    Returns list of markesh planets
    """
    # 2nd house = lagna + 1
    # 7th house = lagna + 6
    second_rashi = (lagna_rashi + 1) % 12
    seventh_rashi = (lagna_rashi + 6) % 12
    
    second_lord_idx = RASHI_LORD[second_rashi]
    seventh_lord_idx = RASHI_LORD[seventh_rashi]
    
    markesh_planets = set()
    markesh_planets.add(second_lord_idx)
    markesh_planets.add(seventh_lord_idx)
    
    return {
        'markesh_planets': [PLANET_NAMES_EN[p] for p in markesh_planets],
        'markesh_planets_hindi': [PLANET_NAMES_HI[p] for p in markesh_planets],
        'second_lord': PLANET_NAMES_EN[second_lord_idx],
        'seventh_lord': PLANET_NAMES_EN[seventh_lord_idx],
        'description': f'2nd house lord ({PLANET_NAMES_EN[second_lord_idx]}) and 7th house lord ({PLANET_NAMES_EN[seventh_lord_idx]}) are Markesh - their dasha periods may bring difficulties.'
    }


def is_markesh_period(planet_name, markesh_data):
    """Check if given planet is in markesh"""
    return planet_name in markesh_data.get('markesh_planets', [])


def calculate_full_maitri_analysis(planets_data, lagna_rashi):
    """
    Complete Panchadha Maitri analysis for all 7 planets
    Plus Markesh detection
    
    planets_data: dict like {'Sun': {'house': 1, 'rashi': 0}, ...}
    """
    # Build planet houses dict
    planet_house_map = {}
    for idx, name in enumerate(PLANET_NAMES_EN):
        if name in planets_data:
            planet_house_map[idx] = planets_data[name].get('house', 1)
    
    # Calculate Panchadha Maitri for each planet
    full_analysis = {}
    for idx in range(7):
        if idx not in planet_house_map:
            continue
        planet_name = PLANET_NAMES_EN[idx]
        relationships = calculate_panchadha_maitri(idx, planet_house_map[idx], planet_house_map)
        full_analysis[planet_name] = relationships
    
    # Markesh detection
    markesh = detect_markesh(planets_data, lagna_rashi)
    
    return {
        'panchadha_maitri': full_analysis,
        'markesh': markesh
    }


if __name__ == '__main__':
    # Test
    test_planets = {
        'Sun': {'house': 5, 'rashi': 4},
        'Moon': {'house': 11, 'rashi': 10},
        'Mars': {'house': 7, 'rashi': 6},
        'Mercury': {'house': 4, 'rashi': 3},
        'Jupiter': {'house': 9, 'rashi': 8},
        'Venus': {'house': 2, 'rashi': 1},
        'Saturn': {'house': 1, 'rashi': 0},
    }
    result = calculate_full_maitri_analysis(test_planets, lagna_rashi=0)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
