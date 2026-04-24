"""
BPHS Chapter 53 - Dasha Avasthaein
8 states for currently running dasha planets
"""

# Planet rashi constants (1-12)
EXALTATION_RASHI = {
    'Sun': 1, 'Moon': 2, 'Mars': 10, 'Mercury': 6,
    'Jupiter': 4, 'Venus': 12, 'Saturn': 7,
    'Rahu': 3, 'Ketu': 9,
}

DEBILITATION_RASHI = {
    'Sun': 7, 'Moon': 8, 'Mars': 4, 'Mercury': 12,
    'Jupiter': 10, 'Venus': 6, 'Saturn': 1,
    'Rahu': 9, 'Ketu': 3,
}

OWN_RASHI = {
    'Sun': [5], 'Moon': [4], 'Mars': [1, 8], 'Mercury': [3, 6],
    'Jupiter': [9, 12], 'Venus': [2, 7], 'Saturn': [10, 11],
    'Rahu': [], 'Ketu': [],
}

FRIEND_RASHI = {
    'Sun': [1, 4, 5, 8, 9, 12],
    'Moon': [1, 2, 3, 4, 5, 6, 7, 8, 9, 12],
    'Mars': [1, 4, 5, 8, 9, 12],
    'Mercury': [2, 3, 6, 7, 10, 11],
    'Jupiter': [1, 4, 5, 8, 9, 12],
    'Venus': [2, 3, 6, 7, 10, 11, 12],
    'Saturn': [2, 3, 6, 7, 10, 11],
    'Rahu': [2, 3, 6, 7, 10, 11],
    'Ketu': [2, 3, 6, 7, 10, 11],
}


def get_navamsha_rashi(longitude):
    """Calculate navamsha (D9) rashi from longitude (0-360)"""
    rashi_num = int(longitude / 30) + 1
    deg_in_rashi = longitude % 30
    navamsha_index = int(deg_in_rashi / (30.0 / 9))
    
    # Movable (1,4,7,10): start from same sign
    # Fixed (2,5,8,11): start from 9th
    # Dual (3,6,9,12): start from 5th
    if rashi_num in [1, 4, 7, 10]:
        start_rashi = rashi_num
    elif rashi_num in [2, 5, 8, 11]:
        start_rashi = ((rashi_num - 1 + 8) % 12) + 1
    else:
        start_rashi = ((rashi_num - 1 + 4) % 12) + 1
    
    return ((start_rashi - 1 + navamsha_index) % 12) + 1


def calculate_dasha_avastha(planet_name, longitude, rashi_num=None, navamsha_rashi=None):
    """
    Calculate Dasha Avastha for a planet based on BPHS Chapter 53.
    
    Args:
        planet_name: 'Sun', 'Moon', 'Mars', etc.
        longitude: 0-360 degrees
        rashi_num: 1-12 (optional, calculated if not given)
        navamsha_rashi: 1-12 (optional, calculated if not given)
    
    Returns:
        dict with name, english_name, phal, color, icon, strength
    """
    if planet_name not in EXALTATION_RASHI:
        return {
            'name': 'अज्ञात',
            'english_name': 'Unknown',
            'phal': 'Data uplabdh nahi',
            'color': 'gray',
            'icon': '❓',
            'strength': 'medium',
        }
    
    # Auto-calculate if not provided
    if rashi_num is None:
        rashi_num = int(longitude / 30) + 1
    if navamsha_rashi is None:
        navamsha_rashi = get_navamsha_rashi(longitude)
    
    exalt_rashi = EXALTATION_RASHI[planet_name]
    debil_rashi = DEBILITATION_RASHI[planet_name]
    own_rashis = OWN_RASHI[planet_name]
    friend_rashis = FRIEND_RASHI[planet_name]
    
    degree_in_rashi = longitude % 30
    is_parmochgat = (rashi_num == exalt_rashi and abs(degree_in_rashi - 10) < 3)
    is_parm_neech = (rashi_num == debil_rashi and abs(degree_in_rashi - 10) < 3)
    
    is_own_navamsha = navamsha_rashi in own_rashis
    is_friend_navamsha = navamsha_rashi in friend_rashis
    is_exalt_navamsha = (navamsha_rashi == exalt_rashi)
    is_debil_navamsha = (navamsha_rashi == debil_rashi)
    is_enemy_navamsha = not (is_own_navamsha or is_friend_navamsha or is_exalt_navamsha)
    
    # === 8 Avasthaein (priority order) ===
    
    # 1. SAMPOORNA
    if is_parmochgat:
        return {
            'name': 'सम्पूर्णा',
            'english_name': 'Sampoorna',
            'phal': 'Rajya labh, bhautik sukh-prapti, shubh phal, Lakshmi kripa tatha bhare-poore parivar v makan ka sukh hota hai.',
            'color': 'yellow',
            'icon': '👑',
            'strength': 'very_high',
        }
    
    # 2. POORNA
    if rashi_num == exalt_rashi:
        return {
            'name': 'पूर्णा',
            'english_name': 'Poorna',
            'phal': 'Is dasha mein manushya ko bahut aishwarya arthat sansarik samruddhi prapt hoti hai.',
            'color': 'green',
            'icon': '⭐',
            'strength': 'very_high',
        }
    
    # 3. RIKTA
    if is_parm_neech:
        return {
            'name': 'रिक्ता',
            'english_name': 'Rikta',
            'phal': 'Is dasha mein anisht phal, bimari, vipatti, kasht tatha anyatha sambhav ho to mrityu tak hoti hai.',
            'color': 'red',
            'icon': '⚠️',
            'strength': 'very_low',
        }
    
    # 4. ADHAMA
    if rashi_num == debil_rashi and is_enemy_navamsha:
        return {
            'name': 'अधमा',
            'english_name': 'Adhama',
            'phal': 'Is dasha mein bhay, klesh, rog aadi badhte hain.',
            'color': 'red',
            'icon': '💀',
            'strength': 'very_low',
        }
    
    # 5. AROHINI
    if rashi_num == debil_rashi and (is_own_navamsha or is_friend_navamsha or is_exalt_navamsha):
        return {
            'name': 'आरोहिणी',
            'english_name': 'Arohini',
            'phal': 'Is dasha mein neech grah ke balabal v anyagraha yogaadi se aarohanaatmak arthat kramshah badhta hua phal hota hai.',
            'color': 'blue',
            'icon': '📈',
            'strength': 'medium',
        }
    
    # 6. AVAROHINI
    if rashi_num == exalt_rashi and is_debil_navamsha:
        return {
            'name': 'अवरोहिणी',
            'english_name': 'Avarohini',
            'phal': 'Naam ke anusaar phal deti hai. Arthat grah jitna adhik neech ke nikat hota jayega, tadnusaar hi shubh phalon mein avrod arthat nyoonta aati jayegi.',
            'color': 'orange',
            'icon': '📉',
            'strength': 'medium',
        }
    
    # 7. MADHYAMA
    if rashi_num in friend_rashis or rashi_num in own_rashis:
        return {
            'name': 'मध्यमा',
            'english_name': 'Madhyama',
            'phal': 'Yah dasha bhi grah ke balabalanusaar madhyam phal tatha dhan deti hai.',
            'color': 'cyan',
            'icon': '⚖️',
            'strength': 'medium',
        }
    
    # 8. RIKTA (Simple debilitation)
    if rashi_num == debil_rashi:
        return {
            'name': 'रिक्ता',
            'english_name': 'Rikta (Neechgat)',
            'phal': 'Grah neech rashi mein hone se durbal hai. Is dasha mein kashtprad phal milenge.',
            'color': 'red',
            'icon': '⚠️',
            'strength': 'low',
        }
    
    # Fallback - Shatru
    return {
        'name': 'सामान्य',
        'english_name': 'Samanya (Shatru)',
        'phal': 'Grah shatru rashi mein hai. Kuch shubh, kuch ashubh mishrit phal milega.',
        'color': 'gray',
        'icon': '⚪',
        'strength': 'low',
    }


def calculate_all_dasha_avasthaein(planets_data):
    """
    Calculate Dasha Avastha for all 9 planets.
    
    Args:
        planets_data: dict like {'Sun': {'longitude': X, ...}, 'Moon': {...}, ...}
    
    Returns:
        dict like {'Sun': {avastha result}, 'Moon': {...}, ...}
    """
    result = {}
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        if name in planets_data:
            p = planets_data[name]
            longitude = p.get('longitude', 0)
            rashi_num = p.get('rashi_num') or (int(longitude / 30) + 1)
            result[name] = calculate_dasha_avastha(
                planet_name=name,
                longitude=longitude,
                rashi_num=rashi_num,
            )
    return result


# Quick self-test
if __name__ == '__main__':
    # Test Moon at 120° (Leo)
    test_result = calculate_dasha_avastha('Moon', 120, rashi_num=5)
    print(f"Test - Moon in Leo: {test_result}")
    
    # Test Sun at 10° (Aries - exalted)
    test_result = calculate_dasha_avastha('Sun', 10, rashi_num=1)
    print(f"Test - Sun in Aries (exalted): {test_result}")
