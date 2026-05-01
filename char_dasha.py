"""
Jaimini Char Dasha System
Reference: Brihat Parashar Hora Shastra (BPHS)
+ Acharya Harish Purohit's book "ज्योतिष से आत्म दर्शन" Page 95-104

Rules:
- Lagna based dasha system
- Variable years per rashi (depends on lord position)
- Forward/Reverse counting based on rashi number
- Special rules for Aries-Sagittarius
"""

# Rashi names and order
RASHI_NAMES = ['Mesh', 'Vrish', 'Mithun', 'Kark', 'Sinh', 'Kanya',
               'Tula', 'Vrischik', 'Dhanu', 'Makar', 'Kumbh', 'Meen']
RASHI_HINDI = ['मेष', 'वृष', 'मिथुन', 'कर्क', 'सिंह', 'कन्या',
               'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']

# Rashi lords
RASHI_LORDS = {
    0: 'Mars',     # Mesh
    1: 'Venus',    # Vrish
    2: 'Mercury',  # Mithun
    3: 'Moon',     # Kark
    4: 'Sun',      # Sinh
    5: 'Mercury',  # Kanya
    6: 'Venus',    # Tula
    7: 'Mars',     # Vrischik (also Ketu)
    8: 'Jupiter',  # Dhanu
    9: 'Saturn',   # Makar
    10: 'Saturn',  # Kumbh (also Rahu)
    11: 'Jupiter'  # Meen
}

# Co-lords (for Vrischik=Ketu, Kumbh=Rahu)
RASHI_COLORDS = {
    7: 'Ketu',
    10: 'Rahu'
}

# Direction of counting per rashi (Acharya's book Page 95)
def get_counting_direction(rashi_idx):
    """
    Rashi 1, 2, 3 (Mesh, Vrish, Mithun)   = Forward (+1)
    Rashi 4, 5, 6 (Kark, Sinh, Kanya)     = Reverse (-1)
    Rashi 7, 8, 9 (Tula, Vrischik, Dhanu) = Forward (+1)
    Rashi 10, 11, 12 (Makar, Kumbh, Meen) = Reverse (-1)
    """
    rashi_num = rashi_idx + 1
    if rashi_num in [1, 2, 3, 7, 8, 9]:
        return 1  # Forward (Krama)
    else:
        return -1  # Reverse (Vilom)

def count_rashis(from_rashi, to_rashi, direction):
    """Count rashis from one to another in given direction"""
    if direction == 1:  # Forward
        if to_rashi >= from_rashi:
            count = to_rashi - from_rashi + 1
        else:
            count = (12 - from_rashi) + to_rashi + 1
    else:  # Reverse
        if from_rashi >= to_rashi:
            count = from_rashi - to_rashi + 1
        else:
            count = from_rashi + (12 - to_rashi) + 1
    return count

def calculate_dasha_years(rashi_idx, planet_positions):
    """
    Calculate years for a rashi based on its lord's position
    
    Method:
    1. Find rashi's lord
    2. Find which rashi the lord is in
    3. Count from rashi to lord's position (in correct direction)
    4. Count = years of dasha
    """
    lord = RASHI_LORDS[rashi_idx]
    
    # Get lord's position
    if lord not in planet_positions:
        return 7  # Default if missing
    
    lord_rashi = planet_positions[lord]['rashi_index']
    
    # Get counting direction for this rashi
    direction = get_counting_direction(rashi_idx)
    
    # Count from this rashi to lord's position
    years = count_rashis(rashi_idx, lord_rashi, direction)
    
    # Apply special rules:
    # If years > 12, subtract 12
    if years > 12:
        years -= 12
    
    # If years = 12, then 12 (special case)
    # If lord is in same rashi (years = 1), check exception
    
    return years

def get_rashi_index_from_longitude(longitude):
    """Convert longitude to rashi index (0-11)"""
    return int(longitude / 30) % 12

def add_years_to_date(date_str, years):
    """Add decimal years to date"""
    from datetime import datetime, timedelta
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    days = years * 365.2425
    new_dt = dt + timedelta(days=days)
    return new_dt.strftime('%Y-%m-%d')

def years_to_ymd(years):
    """Convert decimal years to Years/Months/Days"""
    if years < 0:
        return {'y': 0, 'm': 0, 'd': 0}
    y = int(years)
    rem_months = (years - y) * 12
    m = int(rem_months)
    rem_days = (rem_months - m) * 30
    d = int(rem_days)
    return {'y': y, 'm': m, 'd': d}

def calculate_char_dasha(lagna_longitude, planet_positions, birth_date_str):
    """
    Main Char Dasha calculation
    
    Args:
        lagna_longitude: Lagna position in degrees (0-360)
        planet_positions: dict of {planet_name: {longitude, rashi_index}}
        birth_date_str: 'YYYY-MM-DD'
    """
    # Get Lagna rashi
    lagna_rashi = get_rashi_index_from_longitude(lagna_longitude)
    
    # Determine starting direction (from lagna)
    starting_direction = get_counting_direction(lagna_rashi)
    
    # Build dasha sequence (12 rashis from lagna)
    dasha_sequence = []
    if starting_direction == 1:  # Forward
        for i in range(12):
            dasha_sequence.append((lagna_rashi + i) % 12)
    else:  # Reverse
        for i in range(12):
            dasha_sequence.append((lagna_rashi - i) % 12)
    
    # Calculate years for each rashi
    periods = []
    current_date = birth_date_str
    cumulative_years = 0
    
    for rashi_idx in dasha_sequence:
        years = calculate_dasha_years(rashi_idx, planet_positions)
        end_date = add_years_to_date(current_date, years)
        ymd = years_to_ymd(years)
        
        # Check if this is an inauspicious dasha (Acharya's note 179)
        is_inauspicious = rashi_idx in [4, 8, 9]  # Sinh, Dhanu, Makar
        
        periods.append({
            'rashi': RASHI_NAMES[rashi_idx],
            'rashi_hindi': RASHI_HINDI[rashi_idx],
            'lord': RASHI_LORDS[rashi_idx],
            'co_lord': RASHI_COLORDS.get(rashi_idx),
            'years': years,
            'duration': f"{ymd['y']}Y {ymd['m']}M {ymd['d']}D",
            'start_date': current_date,
            'end_date': end_date,
            'is_inauspicious': is_inauspicious,
            'note': 'अच्छी नहीं' if is_inauspicious else ''
        })
        
        current_date = end_date
        cumulative_years += years
    
    return {
        'system': 'Jaimini Char Dasha',
        'lagna_rashi': RASHI_NAMES[lagna_rashi],
        'lagna_rashi_hindi': RASHI_HINDI[lagna_rashi],
        'lagna_lord': RASHI_LORDS[lagna_rashi],
        'starting_direction': 'Krama (Forward)' if starting_direction == 1 else 'Vilom (Reverse)',
        'total_years': cumulative_years,
        'periods': periods,
        'reference': 'Acharya Harish Purohit Book Page 95-104 + BPHS'
    }

def get_full_char_dasha(lagna_data, planets_data, birth_date_str):
    """Main API function"""
    lagna_lon = lagna_data.get('longitude', 0) if isinstance(lagna_data, dict) else lagna_data
    
    # Build planet positions dict
    planet_positions = {}
    for planet_name, planet_info in planets_data.items():
        if isinstance(planet_info, dict) and 'longitude' in planet_info:
            lon = planet_info['longitude']
            planet_positions[planet_name] = {
                'longitude': lon,
                'rashi_index': int(lon / 30) % 12
            }
    
    return calculate_char_dasha(lagna_lon, planet_positions, birth_date_str)
