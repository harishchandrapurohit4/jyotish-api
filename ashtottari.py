"""
Ashtottari Dasha System
Reference: Brihat Parashara Hora Shastra (BPHS) - Page 431-433
Total: 108 years, 8 Mahadashas (No Ketu)
"""

# Ashtottari Dasha lords with years (Total = 108)
ASHTOTTARI_LORDS = [
    ('Sun', 6),
    ('Moon', 15),
    ('Mars', 8),
    ('Mercury', 17),
    ('Saturn', 10),
    ('Jupiter', 19),
    ('Rahu', 12),
    ('Venus', 21)
]

ASHTOTTARI_TOTAL = 108

# Nakshatra mapping for Aardradi (Aardra-based) - when grah in Lagna
# Each lord rules specific nakshatras (varies: Pap=4 nakshatras, Shubh=3 nakshatras)
ASHTOTTARI_NAKSHATRAS_AARDRADI = {
    'Sun': ['Ardra', 'Punarvasu', 'Pushya'],          # 3 nakshatras
    'Moon': ['Magha', 'P.Phalguni', 'U.Phalguni', 'Hasta'],  # 4 (with Ashlesha)
    'Mars': ['Hasta', 'Chitra', 'Swati', 'Vishakha'],  # 4 (Pap)
    'Mercury': ['Anuradha', 'Jyeshtha', 'Mool'],       # 3
    'Saturn': ['P.Ashadha', 'U.Ashadha', 'Abhijit', 'Shravan'],  # 4 (Pap)
    'Jupiter': ['Dhanishta', 'Shatabhisha', 'P.Bhadra'],  # 3
    'Rahu': ['U.Bhadra', 'Revati', 'Ashwini', 'Bharani'],  # 4 (Pap)
    'Venus': ['Krittika', 'Rohini', 'Mrigashira']      # 3
}

# Aardra is index 5, so Aardradi starts from there
# Standard nakshatra order (0-indexed)
NAKSHATRA_ORDER = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira',
    'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
    'Magha', 'P.Phalguni', 'U.Phalguni', 'Hasta',
    'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mool', 'P.Ashadha', 'U.Ashadha',
    'Shravana', 'Dhanishta', 'Shatabhisha',
    'P.Bhadra', 'U.Bhadra', 'Revati'
]

# Nakshatra to Dasha Lord mapping (Aardradi system)
# Index 5 = Aardra (Sun starts)
NAKSHATRA_TO_LORD_AARDRADI = {
    5: ('Sun', 0),     # Ardra - 1st nakshatra of Sun
    6: ('Sun', 1),     # Punarvasu - 2nd
    7: ('Sun', 2),     # Pushya - 3rd (Sun ends)
    8: ('Moon', 0),    # Ashlesha - some include this with Moon
    9: ('Moon', 0),    # Magha - 1st of Moon
    10: ('Moon', 1),   # P.Phalguni - 2nd
    11: ('Moon', 2),   # U.Phalguni - 3rd
    12: ('Moon', 3),   # Hasta - 4th (Moon ends)
    13: ('Mars', 0),   # Chitra
    14: ('Mars', 1),   # Swati
    15: ('Mars', 2),   # Vishakha
    16: ('Mercury', 0), # Anuradha
    17: ('Mercury', 1), # Jyeshtha
    18: ('Mercury', 2), # Mool
    19: ('Saturn', 0), # P.Ashadha
    20: ('Saturn', 1), # U.Ashadha
    21: ('Saturn', 2), # Shravan (Abhijit ke saath)
    22: ('Jupiter', 0), # Dhanishta
    23: ('Jupiter', 1), # Shatabhisha
    24: ('Jupiter', 2), # P.Bhadra
    25: ('Rahu', 0),   # U.Bhadra
    26: ('Rahu', 1),   # Revati
    0: ('Rahu', 2),    # Ashwini
    1: ('Rahu', 3),    # Bharani
    2: ('Venus', 0),   # Krittika
    3: ('Venus', 1),   # Rohini
    4: ('Venus', 2)    # Mrigashira
}

def get_ashtottari_lord_years(lord_name):
    """Get total years for a dasha lord"""
    for lord, years in ASHTOTTARI_LORDS:
        if lord == lord_name:
            return years
    return 0

def get_next_lord(current_lord):
    """Get next lord in Ashtottari sequence"""
    for i, (lord, years) in enumerate(ASHTOTTARI_LORDS):
        if lord == current_lord:
            next_i = (i + 1) % len(ASHTOTTARI_LORDS)
            return ASHTOTTARI_LORDS[next_i]
    return ASHTOTTARI_LORDS[0]

def calculate_ashtottari_dasha(nakshatra_index, nakshatra_pada, moon_longitude):
    """
    Calculate Ashtottari Mahadasha sequence
    
    Args:
        nakshatra_index: 0-26 (Ashwini=0)
        nakshatra_pada: 1-4 (charan)
        moon_longitude: Moon's longitude in degrees
    
    Returns:
        List of dasha periods with start/end times
    """
    # Find current dasha lord based on Janma Nakshatra
    if nakshatra_index not in NAKSHATRA_TO_LORD_AARDRADI:
        return []
    
    lord_info = NAKSHATRA_TO_LORD_AARDRADI[nakshatra_index]
    current_lord = lord_info[0]
    nakshatra_position = lord_info[1]  # Position within lord's nakshatras
    
    # Calculate elapsed portion in current nakshatra
    nakshatra_size = 13.333333  # 360/27
    nakshatra_start = nakshatra_index * nakshatra_size
    elapsed_in_nakshatra = (moon_longitude - nakshatra_start) % nakshatra_size
    elapsed_fraction = elapsed_in_nakshatra / nakshatra_size
    
    # Get total nakshatras for current lord
    lord_nakshatras = ASHTOTTARI_NAKSHATRAS_AARDRADI.get(current_lord, [])
    total_lord_nakshatras = len(lord_nakshatras) if lord_nakshatras else 3
    
    # Calculate Bhukt (consumed) and Bhogya (remaining)
    lord_total_years = get_ashtottari_lord_years(current_lord)
    
    # Each nakshatra under a lord gets equal share
    years_per_nakshatra = lord_total_years / total_lord_nakshatras
    
    # Bhukt = previous full nakshatras + portion of current
    bhukt_years = (nakshatra_position * years_per_nakshatra) + (elapsed_fraction * years_per_nakshatra)
    bhogya_years = lord_total_years - bhukt_years
    
    return {
        'starting_lord': current_lord,
        'bhukt_years': round(bhukt_years, 4),
        'bhogya_years': round(bhogya_years, 4),
        'lord_total_years': lord_total_years,
        'sequence': calculate_dasha_sequence(current_lord, bhogya_years)
    }

def calculate_dasha_sequence(starting_lord, bhogya_years, total_cycle=108):
    """Calculate full dasha sequence starting with bhogya of starting lord"""
    sequence = []
    
    # First entry: bhogya years of starting lord
    sequence.append({
        'lord': starting_lord,
        'years': round(bhogya_years, 4),
        'is_bhogya': True
    })
    
    # Continue with full periods of next lords
    current = starting_lord
    accumulated = bhogya_years
    
    while accumulated < total_cycle:
        next_lord_info = get_next_lord(current)
        next_lord, next_years = next_lord_info
        
        if accumulated + next_years > total_cycle:
            # Last partial period
            remaining = total_cycle - accumulated
            sequence.append({
                'lord': next_lord,
                'years': round(remaining, 4),
                'is_bhogya': False
            })
            break
        
        sequence.append({
            'lord': next_lord,
            'years': next_years,
            'is_bhogya': False
        })
        
        accumulated += next_years
        current = next_lord
    
    return sequence

def years_to_ymd(years):
    """Convert decimal years to Years/Months/Days"""
    y = int(years)
    rem_months = (years - y) * 12
    m = int(rem_months)
    rem_days = (rem_months - m) * 30
    d = int(rem_days)
    return {'y': y, 'm': m, 'd': d}

def add_years_to_date(date_str, years):
    """Add decimal years to a date string YYYY-MM-DD"""
    from datetime import datetime, timedelta
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    days = years * 365.2425
    new_dt = dt + timedelta(days=days)
    return new_dt.strftime('%Y-%m-%d')

def check_ashtottari_applicable(paksha, birth_hour, sunrise_hour, sunset_hour):
    """
    Check if Ashtottari should be applied based on:
    - Krishna Paksha + Day birth (sunrise to sunset)
    - Shukla Paksha + Night birth (sunset to next sunrise)
    """
    is_day = sunrise_hour <= birth_hour < sunset_hour
    
    if paksha.lower() in ['krishna', 'krsna', 'k']:
        return is_day  # Krishna + Day = Apply
    elif paksha.lower() in ['shukla', 'shukl', 's']:
        return not is_day  # Shukla + Night = Apply
    
    return False

def get_full_ashtottari(moon_data, birth_date_str, paksha=None, birth_hour=12, sunrise=6, sunset=18):
    """
    Main function: Get complete Ashtottari dasha calculation
    
    Args:
        moon_data: Dict with 'nakshatra_num' (1-27), 'pada' (1-4), 'longitude' (degrees)
        birth_date_str: 'YYYY-MM-DD'
        paksha: 'krishna' or 'shukla'
        birth_hour: 0-24 in local time
        sunrise: hour of sunrise
        sunset: hour of sunset
    """
    nakshatra_idx = moon_data.get('nakshatra_num', 1) - 1  # Convert to 0-indexed
    nakshatra_pada = moon_data.get('pada', 1)
    moon_lon = moon_data.get('longitude', 0)
    
    # Calculate dasha
    dasha_data = calculate_ashtottari_dasha(nakshatra_idx, nakshatra_pada, moon_lon)
    
    # Build dasha periods with dates
    current_date = birth_date_str
    periods = []
    
    for entry in dasha_data['sequence']:
        end_date = add_years_to_date(current_date, entry['years'])
        ymd = years_to_ymd(entry['years'])
        
        periods.append({
            'lord': entry['lord'],
            'years': entry['years'],
            'duration': f"{ymd['y']}Y {ymd['m']}M {ymd['d']}D",
            'start_date': current_date,
            'end_date': end_date,
            'is_bhogya': entry['is_bhogya']
        })
        
        current_date = end_date
    
    # Check applicability
    is_applicable = None
    if paksha:
        is_applicable = check_ashtottari_applicable(paksha, birth_hour, sunrise, sunset)
    
    return {
        'system': 'Ashtottari Dasha',
        'total_years': 108,
        'starting_lord': dasha_data['starting_lord'],
        'bhukt_years': dasha_data['bhukt_years'],
        'bhogya_years': dasha_data['bhogya_years'],
        'is_primarily_applicable': is_applicable,
        'application_rule': 'Krishna Paksha + Day birth OR Shukla Paksha + Night birth',
        'periods': periods
    }
