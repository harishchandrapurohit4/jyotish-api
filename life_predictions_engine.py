"""
Life Predictions Engine
Calculates 8 life areas with realistic BPHS-based scoring
"""

# Rashi lords (1-indexed, like astro_engine)
RASHI_LORDS = {
    1: 'mars', 2: 'venus', 3: 'mercury', 4: 'moon',
    5: 'sun', 6: 'mercury', 7: 'venus', 8: 'mars',
    9: 'jupiter', 10: 'saturn', 11: 'saturn', 12: 'jupiter'
}

EXALTATION = {
    'sun': 1, 'moon': 2, 'mars': 10, 'mercury': 6,
    'jupiter': 4, 'venus': 12, 'saturn': 7
}

DEBILITATION = {
    'sun': 7, 'moon': 8, 'mars': 4, 'mercury': 12,
    'jupiter': 10, 'venus': 6, 'saturn': 1
}

OWN_RASHIS = {
    'sun': [5], 'moon': [4], 'mars': [1, 8],
    'mercury': [3, 6], 'jupiter': [9, 12],
    'venus': [2, 7], 'saturn': [10, 11]
}


def get_house_rashi(lagna_rashi, house):
    """Get rashi number for a given house from lagna"""
    return ((lagna_rashi - 1 + house - 1) % 12) + 1


def calculate_house(planet_rashi, lagna_rashi):
    """Calculate which house the planet is in"""
    return ((planet_rashi - lagna_rashi + 12) % 12) + 1


def is_kendra(house):
    return house in [1, 4, 7, 10]


def is_trikona(house):
    return house in [1, 5, 9]


def is_dusthana(house):
    return house in [6, 8, 12]


def get_planet_rashi(planets, planet_name):
    """Get rashi of a planet (case-insensitive)"""
    name_lower = planet_name.lower()
    if name_lower in planets:
        return planets[name_lower].get('rashi', 0)
    # Try title case
    name_title = planet_name.title()
    if name_title in planets:
        return planets[name_title].get('rashi', 0)
    return 0


def planet_strength(planets, planet_name, lagna_rashi):
    """
    Get planet's strength score (0-100)
    Considers: exaltation, own sign, kendra/trikona placement, dusthana
    """
    name_lower = planet_name.lower()
    rashi = get_planet_rashi(planets, planet_name)
    if rashi == 0:
        return 30  # neutral if not found
    
    score = 30  # baseline
    
    # Exalted
    if rashi == EXALTATION.get(name_lower):
        score += 30
    # Own sign
    elif rashi in OWN_RASHIS.get(name_lower, []):
        score += 20
    # Debilitated
    elif rashi == DEBILITATION.get(name_lower):
        score -= 25
    
    # House placement
    house = calculate_house(rashi, lagna_rashi)
    if is_kendra(house):
        score += 15
    elif is_trikona(house):
        score += 20
    elif is_dusthana(house):
        score -= 20
    
    return max(0, min(100, score))


def score_to_stars(score, strict=False):
    """
    Convert 0-100 score to 1-5 stars realistically
    strict=True for tougher scoring
    """
    if strict:
        if score >= 80: return 5
        if score >= 65: return 4
        if score >= 50: return 3
        if score >= 35: return 2
        return 1
    else:
        if score >= 75: return 5
        if score >= 60: return 4
        if score >= 45: return 3
        if score >= 30: return 2
        return 1


def calculate_career(planets, lagna_rashi, yogas_ids):
    """Career = 10th house + lord + Sun + relevant yogas"""
    score = 40  # baseline (medium)
    reasons = []
    
    # 10th house lord
    tenth_rashi = get_house_rashi(lagna_rashi, 10)
    tenth_lord = RASHI_LORDS[tenth_rashi]
    lord_strength = planet_strength(planets, tenth_lord, lagna_rashi)
    score += (lord_strength - 30) * 0.4
    if lord_strength > 60:
        reasons.append(f'10th lord ({tenth_lord}) bali')
    
    # Sun strength (raj karak)
    sun_strength = planet_strength(planets, 'sun', lagna_rashi)
    score += (sun_strength - 30) * 0.2
    
    # Yogas affecting career
    career_yogas = ['ruchaka', 'shasha', 'hamsa', 'shrinath', 'mridang', 'budh_aditya', 'gaja_kesari']
    matched = [y for y in career_yogas if y in yogas_ids]
    score += len(matched) * 5
    if matched:
        reasons.append(f'Yogas: {", ".join(matched[:2])}')
    
    # Lagnesh strength
    lagnesh = RASHI_LORDS[lagna_rashi]
    lagnesh_strength = planet_strength(planets, lagnesh, lagna_rashi)
    score += (lagnesh_strength - 30) * 0.2
    
    return {
        'score': max(20, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_marriage(planets, lagna_rashi, yogas_ids):
    """Marriage = 7th house + lord + Venus + Manglik check"""
    score = 45
    reasons = []
    
    # 7th lord
    seventh_rashi = get_house_rashi(lagna_rashi, 7)
    seventh_lord = RASHI_LORDS[seventh_rashi]
    lord_strength = planet_strength(planets, seventh_lord, lagna_rashi)
    score += (lord_strength - 30) * 0.4
    
    # Venus (karak)
    venus_strength = planet_strength(planets, 'venus', lagna_rashi)
    score += (venus_strength - 30) * 0.3
    
    # Manglik check
    mars_rashi = get_planet_rashi(planets, 'mars')
    if mars_rashi:
        mars_house = calculate_house(mars_rashi, lagna_rashi)
        if mars_house in [1, 4, 7, 8, 12]:
            # Manglik
            if mars_rashi in OWN_RASHIS.get('mars', []) or mars_rashi == EXALTATION.get('mars'):
                score -= 5  # cancelled
                reasons.append('Manglik but cancelled')
            else:
                score -= 12
                reasons.append('Manglik dosha present')
    
    # Vipareet yogas help
    if 'vipareet_harsha' in yogas_ids or 'vipareet_vimala' in yogas_ids:
        score += 5
    
    return {
        'score': max(15, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_love(planets, lagna_rashi, yogas_ids):
    """Love = 5th house + Venus"""
    score = 45
    reasons = []
    
    fifth_rashi = get_house_rashi(lagna_rashi, 5)
    fifth_lord = RASHI_LORDS[fifth_rashi]
    lord_strength = planet_strength(planets, fifth_lord, lagna_rashi)
    score += (lord_strength - 30) * 0.4
    
    venus_strength = planet_strength(planets, 'venus', lagna_rashi)
    score += (venus_strength - 30) * 0.3
    
    return {
        'score': max(15, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons
    }


def calculate_health(planets, lagna_rashi, yogas_ids):
    """Health = Lagna + Lagnesh + 6th house"""
    score = 50
    reasons = []
    
    # Lagnesh strength
    lagnesh = RASHI_LORDS[lagna_rashi]
    lagnesh_strength = planet_strength(planets, lagnesh, lagna_rashi)
    score += (lagnesh_strength - 30) * 0.5
    if lagnesh_strength < 30:
        reasons.append(f'Lagnesh ({lagnesh}) weak')
    
    # 6th lord (disease) - Vipareet good
    sixth_rashi = get_house_rashi(lagna_rashi, 6)
    sixth_lord = RASHI_LORDS[sixth_rashi]
    sixth_lord_rashi = get_planet_rashi(planets, sixth_lord)
    if sixth_lord_rashi:
        sixth_house = calculate_house(sixth_lord_rashi, lagna_rashi)
        if is_dusthana(sixth_house):
            score += 10  # vipareet
            reasons.append('Vipareet for health')
    
    return {
        'score': max(20, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_education(planets, lagna_rashi, yogas_ids):
    """Education = 4th, 5th, Mercury, Jupiter"""
    score = 40
    reasons = []
    
    # 4th lord
    fourth_rashi = get_house_rashi(lagna_rashi, 4)
    fourth_lord = RASHI_LORDS[fourth_rashi]
    lord_strength = planet_strength(planets, fourth_lord, lagna_rashi)
    score += (lord_strength - 30) * 0.25
    
    # Mercury (intelligence)
    mercury_strength = planet_strength(planets, 'mercury', lagna_rashi)
    score += (mercury_strength - 30) * 0.3
    
    # Jupiter (wisdom)
    jupiter_strength = planet_strength(planets, 'jupiter', lagna_rashi)
    score += (jupiter_strength - 30) * 0.3
    
    # Education yogas
    edu_yogas = ['budh_aditya', 'sharada', 'bhadra', 'saraswati']
    matched = [y for y in edu_yogas if y in yogas_ids]
    score += len(matched) * 7
    if matched:
        reasons.append(f'Yogas: {", ".join(matched[:2])}')
    
    return {
        'score': max(20, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_children(planets, lagna_rashi, yogas_ids):
    """Children = 5th house + Jupiter"""
    score = 45
    reasons = []
    
    fifth_rashi = get_house_rashi(lagna_rashi, 5)
    fifth_lord = RASHI_LORDS[fifth_rashi]
    lord_strength = planet_strength(planets, fifth_lord, lagna_rashi)
    score += (lord_strength - 30) * 0.4
    
    # Jupiter (santan karak)
    jupiter_strength = planet_strength(planets, 'jupiter', lagna_rashi)
    score += (jupiter_strength - 30) * 0.4
    
    # Jupiter in 5th house = bonus
    jupiter_rashi = get_planet_rashi(planets, 'jupiter')
    if jupiter_rashi:
        j_house = calculate_house(jupiter_rashi, lagna_rashi)
        if j_house == 5:
            score += 10
            reasons.append('Jupiter in 5th')
    
    return {
        'score': max(15, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_wealth(planets, lagna_rashi, yogas_ids):
    """Wealth = 2nd, 11th, Jupiter, dhana yogas"""
    score = 40
    reasons = []
    
    # 2nd lord
    second_rashi = get_house_rashi(lagna_rashi, 2)
    second_lord = RASHI_LORDS[second_rashi]
    score += (planet_strength(planets, second_lord, lagna_rashi) - 30) * 0.2
    
    # 11th lord
    eleventh_rashi = get_house_rashi(lagna_rashi, 11)
    eleventh_lord = RASHI_LORDS[eleventh_rashi]
    score += (planet_strength(planets, eleventh_lord, lagna_rashi) - 30) * 0.25
    
    # Jupiter (dhana karak)
    jupiter_strength = planet_strength(planets, 'jupiter', lagna_rashi)
    score += (jupiter_strength - 30) * 0.2
    
    # Wealth yogas
    wealth_yogas = ['chandra_mangal', 'shankh', 'lakshmi', 'vipareet_harsha', 'vipareet_vimala', 'vipareet_sarala']
    matched = [y for y in wealth_yogas if y in yogas_ids]
    score += len(matched) * 6
    if matched:
        reasons.append(f'Wealth yogas: {", ".join(matched[:2])}')
    
    return {
        'score': max(20, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_property(planets, lagna_rashi, yogas_ids):
    """Property = 4th house + Mars"""
    score = 40
    reasons = []
    
    fourth_rashi = get_house_rashi(lagna_rashi, 4)
    fourth_lord = RASHI_LORDS[fourth_rashi]
    lord_strength = planet_strength(planets, fourth_lord, lagna_rashi)
    score += (lord_strength - 30) * 0.4
    
    # Mars (property karak)
    mars_strength = planet_strength(planets, 'mars', lagna_rashi)
    score += (mars_strength - 30) * 0.3
    
    return {
        'score': max(20, min(95, int(score))),
        'stars': score_to_stars(score),
        'reasons': reasons[:3]
    }


def calculate_all_life_areas(planets, lagna_rashi, yogas_ids):
    """Calculate all 8 life areas"""
    return {
        'career': calculate_career(planets, lagna_rashi, yogas_ids),
        'marriage': calculate_marriage(planets, lagna_rashi, yogas_ids),
        'love': calculate_love(planets, lagna_rashi, yogas_ids),
        'health': calculate_health(planets, lagna_rashi, yogas_ids),
        'education': calculate_education(planets, lagna_rashi, yogas_ids),
        'children': calculate_children(planets, lagna_rashi, yogas_ids),
        'wealth': calculate_wealth(planets, lagna_rashi, yogas_ids),
        'property': calculate_property(planets, lagna_rashi, yogas_ids)
    }
