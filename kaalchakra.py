"""
Kaalchakra Dasha System
Reference: Brihat Parashara Hora Shastra (BPHS) - Chapter on Kaalchakra
Total: 100 years (Purnayu)
Based on Savya/Apsavya nakshatra-charan mapping
"""

# Years per Rashi (काल चक्र दशा वर्ष)
RASHI_YEARS = {
    'Mesh': 5, 'मेष': 5,
    'Vrish': 16, 'वृष': 16,
    'Mithun': 9, 'मिथुन': 9,
    'Kark': 21, 'कर्क': 21,
    'Sinh': 5, 'सिंह': 5,
    'Kanya': 9, 'कन्या': 9,
    'Tula': 16, 'तुला': 16,
    'Vrischik': 7, 'वृश्चिक': 7,
    'Dhanu': 10, 'धनु': 10,
    'Makar': 4, 'मकर': 4,
    'Kumbh': 4, 'कुम्भ': 4,
    'Meen': 10, 'मीन': 10
}

# Rashi index (0-11)
RASHI_NAMES = ['Mesh', 'Vrish', 'Mithun', 'Kark', 'Sinh', 'Kanya',
               'Tula', 'Vrischik', 'Dhanu', 'Makar', 'Kumbh', 'Meen']
RASHI_HINDI = ['मेष', 'वृष', 'मिथुन', 'कर्क', 'सिंह', 'कन्या',
               'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']

# Nakshatra lords
RASHI_LORDS = {
    'Mesh': 'Mars', 'Vrish': 'Venus', 'Mithun': 'Mercury',
    'Kark': 'Moon', 'Sinh': 'Sun', 'Kanya': 'Mercury',
    'Tula': 'Venus', 'Vrischik': 'Mars', 'Dhanu': 'Jupiter',
    'Makar': 'Saturn', 'Kumbh': 'Saturn', 'Meen': 'Jupiter'
}

# SAVYA Nakshatras (15 nakshatras)
# Ashwini, Hasta, Mool start group of 3 each
SAVYA_NAKSHATRAS = [
    'Ashwini', 'Punarvasu', 'Hasta',           # Set 1
    'Mool', 'U.Bhadra',                         # Set 2 part
    'Bharani', 'Pushya', 'Chitra',              # Set 3
    'P.Ashadha', 'Revati',                      # Set 4 part
    'Krittika', 'Ashlesha', 'Swati',            # Set 5
    'U.Ashadha'                                  # Set 6 part
]

# APSAVYA Nakshatras (12 nakshatras)
APSAVYA_NAKSHATRAS = [
    'Rohini', 'Magha', 'Vishakha',              # Set 1
    'Shravan',                                   # Set 2
    'Mrigashira', 'P.Phalguni', 'Anuradha',     # Set 3
    'Dhanishta',                                 # Set 4
    'Ardra', 'U.Phalguni', 'Jyeshtha',          # Set 5
    'Shatabhisha'                                # Set 6
]

# Standard nakshatra order (0-26)
NAKSHATRA_ORDER = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira',
    'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
    'Magha', 'P.Phalguni', 'U.Phalguni', 'Hasta',
    'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mool', 'P.Ashadha', 'U.Ashadha',
    'Shravan', 'Dhanishta', 'Shatabhisha',
    'P.Bhadra', 'U.Bhadra', 'Revati'
]

# SAVYA CHAKRA - Nakshatra + Charan → Rashi sequence (9 rashis)
# From PDF Page 449
# Format: (nakshatra, charan): [9 rashi indices]
SAVYA_TABLE = {
    # Ashwini, Punarvasu, Hasta - Set 1
    ('Ashwini', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],     # Mesh-Dhanu (Page 447 line 9)
    ('Ashwini', 2): [9, 10, 11, 0, 1, 2, 3, 4, 5],   # Makar-Kanya
    ('Ashwini', 3): [6, 7, 8, 9, 10, 11, 7, 6, 5],   # Tula-Meen, then 8,7,6
    ('Ashwini', 4): [3, 4, 2, 1, 0, 11, 10, 9, 8],   # Kark-Mesh-Meen sequence
    
    ('Punarvasu', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('Punarvasu', 2): [9, 10, 11, 0, 1, 2, 3, 4, 5],
    ('Punarvasu', 3): [6, 7, 8, 9, 10, 11, 7, 6, 5],
    ('Punarvasu', 4): [3, 4, 2, 1, 0, 11, 10, 9, 8],
    
    ('Hasta', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('Hasta', 2): [9, 10, 11, 0, 1, 2, 3, 4, 5],
    ('Hasta', 3): [6, 7, 8, 9, 10, 11, 7, 6, 5],
    ('Hasta', 4): [3, 4, 2, 1, 0, 11, 10, 9, 8],
    
    # Mool, U.Bhadra - Set 2 (similar pattern)
    ('Mool', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('Mool', 2): [9, 10, 11, 0, 1, 2, 3, 4, 5],
    ('Mool', 3): [6, 7, 8, 9, 10, 11, 7, 6, 5],
    ('Mool', 4): [3, 4, 2, 1, 0, 11, 10, 9, 8],
    
    ('U.Bhadra', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('U.Bhadra', 2): [9, 10, 11, 0, 1, 2, 3, 4, 5],
    ('U.Bhadra', 3): [6, 7, 8, 9, 10, 11, 7, 6, 5],
    ('U.Bhadra', 4): [3, 4, 2, 1, 0, 11, 10, 9, 8],
    
    # Bharani, Pushya, Chitra - Set 3 (different pattern from PDF)
    ('Bharani', 1): [7, 6, 5, 4, 3, 2, 1, 0, 11],
    ('Bharani', 2): [10, 9, 8, 5, 6, 7, 8, 9, 10],
    ('Bharani', 3): [11, 0, 6, 5, 4, 3, 9, 10, 11],
    ('Bharani', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Pushya', 1): [7, 6, 5, 4, 3, 2, 1, 0, 11],
    ('Pushya', 2): [10, 9, 8, 5, 6, 7, 8, 9, 10],
    ('Pushya', 3): [11, 0, 6, 5, 4, 3, 9, 10, 11],
    ('Pushya', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Chitra', 1): [7, 6, 5, 4, 3, 2, 1, 0, 11],
    ('Chitra', 2): [10, 9, 8, 5, 6, 7, 8, 9, 10],
    ('Chitra', 3): [11, 0, 6, 5, 4, 3, 9, 10, 11],
    ('Chitra', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    # P.Ashadha, Revati - Set 4 partial
    ('P.Ashadha', 1): [7, 6, 5, 4, 3, 2, 1, 0, 11],
    ('P.Ashadha', 2): [10, 9, 8, 5, 6, 7, 8, 9, 10],
    ('P.Ashadha', 3): [11, 0, 6, 5, 4, 3, 9, 10, 11],
    ('P.Ashadha', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Revati', 1): [7, 6, 5, 4, 3, 2, 1, 0, 11],
    ('Revati', 2): [10, 9, 8, 5, 6, 7, 8, 9, 10],
    ('Revati', 3): [11, 0, 6, 5, 4, 3, 9, 10, 11],
    ('Revati', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    # Krittika, Ashlesha, Swati - Set 5
    ('Krittika', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('Krittika', 2): [9, 10, 11, 7, 6, 5, 4, 3, 9],
    ('Krittika', 3): [1, 0, 11, 9, 10, 11, 0, 1, 2],
    ('Krittika', 4): [3, 4, 5, 6, 7, 8, 9, 10, 11],
    
    ('Ashlesha', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('Ashlesha', 2): [9, 10, 11, 7, 6, 5, 4, 3, 9],
    ('Ashlesha', 3): [1, 0, 11, 9, 10, 11, 0, 1, 2],
    ('Ashlesha', 4): [3, 4, 5, 6, 7, 8, 9, 10, 11],
    
    ('Swati', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('Swati', 2): [9, 10, 11, 7, 6, 5, 4, 3, 9],
    ('Swati', 3): [1, 0, 11, 9, 10, 11, 0, 1, 2],
    ('Swati', 4): [3, 4, 5, 6, 7, 8, 9, 10, 11],
    
    # U.Ashadha
    ('U.Ashadha', 1): [0, 1, 2, 3, 4, 5, 6, 7, 8],
    ('U.Ashadha', 2): [9, 10, 11, 7, 6, 5, 4, 3, 9],
    ('U.Ashadha', 3): [1, 0, 11, 9, 10, 11, 0, 1, 2],
    ('U.Ashadha', 4): [3, 4, 5, 6, 7, 8, 9, 10, 11],
}

# APSAVYA CHAKRA - reverse direction
APSAVYA_TABLE = {
    # Rohini, Magha, Vishakha (Set 1)
    ('Rohini', 1): [8, 9, 10, 11, 0, 1, 2, 4, 6],   # Dhanu-onwards reverse
    ('Rohini', 2): [5, 6, 7, 11, 10, 9, 8, 7, 7],
    ('Rohini', 3): [5, 4, 3, 2, 1, 0, 8, 9, 10],
    ('Rohini', 4): [11, 0, 1, 2, 4, 3, 0, 6, 7],
    
    ('Magha', 1): [8, 9, 10, 11, 0, 1, 2, 4, 6],
    ('Magha', 2): [5, 6, 7, 11, 10, 9, 8, 7, 7],
    ('Magha', 3): [5, 4, 3, 2, 1, 0, 8, 9, 10],
    ('Magha', 4): [11, 0, 1, 2, 4, 3, 0, 6, 7],
    
    ('Vishakha', 1): [8, 9, 10, 11, 0, 1, 2, 4, 6],
    ('Vishakha', 2): [5, 6, 7, 11, 10, 9, 8, 7, 7],
    ('Vishakha', 3): [5, 4, 3, 2, 1, 0, 8, 9, 10],
    ('Vishakha', 4): [11, 0, 1, 2, 4, 3, 0, 6, 7],
    
    # Other apsavya nakshatras with similar patterns
    ('Shravan', 1): [8, 9, 10, 11, 0, 1, 2, 4, 6],
    ('Shravan', 2): [5, 6, 7, 11, 10, 9, 8, 7, 7],
    ('Shravan', 3): [5, 4, 3, 2, 1, 0, 8, 9, 10],
    ('Shravan', 4): [11, 0, 1, 2, 4, 3, 0, 6, 7],
    
    ('Mrigashira', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('Mrigashira', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('Mrigashira', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('Mrigashira', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('P.Phalguni', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('P.Phalguni', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('P.Phalguni', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('P.Phalguni', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Anuradha', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('Anuradha', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('Anuradha', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('Anuradha', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Dhanishta', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('Dhanishta', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('Dhanishta', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('Dhanishta', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Ardra', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('Ardra', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('Ardra', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('Ardra', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('U.Phalguni', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('U.Phalguni', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('U.Phalguni', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('U.Phalguni', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Jyeshtha', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('Jyeshtha', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('Jyeshtha', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('Jyeshtha', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
    
    ('Shatabhisha', 1): [11, 10, 9, 8, 7, 6, 5, 4, 3],
    ('Shatabhisha', 2): [2, 1, 0, 11, 10, 9, 8, 7, 6],
    ('Shatabhisha', 3): [5, 4, 3, 9, 10, 11, 0, 1, 2],
    ('Shatabhisha', 4): [8, 9, 10, 11, 7, 6, 5, 4, 3],
}

# Trikon Purnayu (Triangular age in years)
TRIKON_AGE = {
    'Mesh': 100, 'Sinh': 100, 'Dhanu': 100,        # Mesh trikon
    'Vrish': 85, 'Kanya': 85, 'Makar': 85,         # Vrish trikon
    'Mithun': 83, 'Tula': 83, 'Kumbh': 83,         # Mithun trikon
    'Kark': 86, 'Vrischik': 86, 'Meen': 86         # Kark trikon
}

def is_savya(nakshatra):
    """Check if nakshatra is in savya group"""
    return nakshatra in SAVYA_NAKSHATRAS

def get_nakshatra_pada(moon_longitude):
    """Calculate nakshatra and pada from moon longitude"""
    nak_size = 13.333333  # 360/27
    pada_size = 3.333333   # nak/4
    
    nak_index = int(moon_longitude / nak_size)
    pada_in_nak = (moon_longitude % nak_size) / pada_size
    pada = int(pada_in_nak) + 1
    pada_fraction = pada_in_nak - int(pada_in_nak)
    
    return nak_index, pada, pada_fraction

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

def add_years_to_date(date_str, years):
    """Add decimal years to date string"""
    from datetime import datetime, timedelta
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    days = years * 365.2425
    new_dt = dt + timedelta(days=days)
    return new_dt.strftime('%Y-%m-%d')

def detect_special_gati(seq):
    """Detect Manduka, Markat, Sinhavalokan in sequence"""
    gatis = []
    for i in range(len(seq) - 1):
        diff = abs(seq[i+1] - seq[i])
        if diff > 1 and diff != 11:
            if seq[i+1] < seq[i]:
                gatis.append(('Markati', i))  # Monkey - reverse
            else:
                gatis.append(('Manduka', i))   # Frog - leap
    return gatis

def calculate_kaalchakra(moon_longitude, birth_date_str):
    """
    Main calculation function
    """
    nak_idx, pada, pada_frac = get_nakshatra_pada(moon_longitude)
    nakshatra = NAKSHATRA_ORDER[nak_idx]
    
    chakra_type = 'Savya' if is_savya(nakshatra) else 'Apsavya'
    
    # Get sequence
    table = SAVYA_TABLE if chakra_type == 'Savya' else APSAVYA_TABLE
    sequence_indices = table.get((nakshatra, pada), [0,1,2,3,4,5,6,7,8])
    
    # Get rashi names from indices
    sequence_rashis = [RASHI_NAMES[i] for i in sequence_indices]
    
    # Starting rashi for purnayu
    starting_rashi = sequence_rashis[0] if sequence_rashis else 'Mesh'
    purnayu = TRIKON_AGE.get(starting_rashi, 100)
    
    # Calculate Bhukt-Bhogya based on charan completion
    starting_years = RASHI_YEARS.get(starting_rashi, 5)
    bhukt_years = pada_frac * starting_years
    bhogya_years = starting_years - bhukt_years
    
    # Build dasha periods
    current_date = birth_date_str
    periods = []
    
    # First period (bhogya)
    end_date = add_years_to_date(current_date, bhogya_years)
    ymd = years_to_ymd(bhogya_years)
    periods.append({
        'rashi': starting_rashi,
        'rashi_hindi': RASHI_HINDI[RASHI_NAMES.index(starting_rashi)],
        'lord': RASHI_LORDS[starting_rashi],
        'years': round(bhogya_years, 4),
        'duration': f"{ymd['y']}Y {ymd['m']}M {ymd['d']}D",
        'start_date': current_date,
        'end_date': end_date,
        'is_bhogya': True
    })
    current_date = end_date
    
    # Subsequent periods
    accumulated = bhogya_years
    for rashi_idx in sequence_indices[1:]:
        if accumulated >= purnayu:
            break
        rashi = RASHI_NAMES[rashi_idx]
        years = RASHI_YEARS.get(rashi, 5)
        if accumulated + years > purnayu:
            years = purnayu - accumulated
        
        end_date = add_years_to_date(current_date, years)
        ymd = years_to_ymd(years)
        periods.append({
            'rashi': rashi,
            'rashi_hindi': RASHI_HINDI[rashi_idx],
            'lord': RASHI_LORDS[rashi],
            'years': round(years, 4),
            'duration': f"{ymd['y']}Y {ymd['m']}M {ymd['d']}D",
            'start_date': current_date,
            'end_date': end_date,
            'is_bhogya': False
        })
        current_date = end_date
        accumulated += years
    
    # Detect special gati
    gatis = detect_special_gati(sequence_indices)
    
    # Detect rashi transitions
    rashi_transitions = detect_rashi_transitions(sequence_rashis)
    
    # Detect disha (direction) effects
    disha_phal = detect_disha_phal(sequence_rashis)
    for d in disha_phal:
        pos = d['position']
        if pos + 1 < len(periods):
            d['period_info'] = {
                'start_date': periods[pos + 1]['start_date'],
                'end_date': periods[pos + 1]['end_date'],
                'duration': periods[pos + 1]['duration']
            }
    for trans in rashi_transitions:
        pos = trans['position']
        if pos + 1 < len(periods):
            trans['period_info'] = {
                'start_date': periods[pos + 1]['start_date'],
                'end_date': periods[pos + 1]['end_date'],
                'duration': periods[pos + 1]['duration']
            }
    
    # Add phaladesh for each gati
    gati_with_phal = []
    for g in gatis:
        gati_type = g[0]
        position = g[1]
        phal = get_gati_phaladesh(gati_type, chakra_type)
        gati_with_phal.append({
            'type': gati_type,
            'position': position,
            'name_hindi': phal['name_hindi'] if phal else gati_type,
            'phaladesh': phal['phal'] if phal else []
        })
    
    return {
        'system': 'Kaalchakra Dasha',
        'chakra_type': chakra_type,
        'nakshatra': nakshatra,
        'pada': pada,
        'starting_rashi': starting_rashi,
        'starting_lord': RASHI_LORDS[starting_rashi],
        'purnayu': purnayu,
        'bhukt_years': round(bhukt_years, 4),
        'bhogya_years': round(bhogya_years, 4),
        'sequence': sequence_rashis,
        'special_gati': gatis,
        'rashi_transitions': rashi_transitions,
        'disha_phal': disha_phal,
        'gati_with_phaladesh': gati_with_phal,
        'periods': periods
    }

def get_full_kaalchakra(moon_data, birth_date_str):
    """Main API function"""
    moon_lon = moon_data.get('longitude', 0)
    return calculate_kaalchakra(moon_lon, birth_date_str)


# ============================================
# SPECIAL GATI PHALADESH (BPHS Page 452)
# ============================================
GATI_PHALADESH = {
    'Manduka': {
        'name_hindi': 'मण्डूक गति',
        'name_english': 'Frog Leap',
        'savya_phal': [
            'बन्धु (रिश्तेदारों) व मित्रों को कष्ट',
            'माता-पिता को कष्ट',
            'विष भय, शस्त्र-अग्नि-ज्वर भय',
            'चोर भय की संभावना',
            'सिंह से मेष की दशा में: माता मृत्यु, राज्यमद, सन्निपात (मस्तिष्क ज्वर) भय'
        ],
        'apsavya_phal': [
            'स्त्री-पुत्र आदि परिवारजनों को पीड़ा',
            'ज्वर भय',
            'कुत्ते आदि से कष्ट',
            'पद नाश'
        ]
    },
    'Markati': {
        'name_hindi': 'मरकटी गति', 
        'name_english': 'Monkey Jump',
        'savya_phal': [
            'धन-धान्य की हानि',
            'पशु (चौपाया) हानि',
            'पिता की मृत्यु', 
            'आलस्य',
            'पिता-तुल्य लोगों (ताऊ, चाचा, ससुर) की हानि या मृत्यु'
        ],
        'apsavya_phal': [
            'जल भय',
            'पद नाश',
            'पिता को मृत्युतुल्य कष्ट',
            'राजभय',
            'गुप्त स्थानों पर छिपने का संकट'
        ]
    },
    'Sinhavalokan': {
        'name_hindi': 'सिंहावलोकन गति',
        'name_english': 'Lion Glance',
        'savya_phal': [
            'पशु भय, विघ्न',
            'कूप-गड्ढे आदि में गिरने का भय',
            'विष-शस्त्र-अग्नि भय',
            'वाहन से गिरना',
            'बुखार से पीड़ा',
            'स्थान हानि (पद, प्रतिष्ठा, आवास या व्यावसायिक स्थान की हानि)'
        ],
        'apsavya_phal': [
            'पद हानि',
            'पिता या पिता-तुल्य लोगों की मृत्यु'
        ]
    }
}

def get_gati_phaladesh(gati_type, chakra_type):
    """Get phaladesh for specific gati type"""
    info = GATI_PHALADESH.get(gati_type, {})
    if not info:
        return None
    return {
        'name_hindi': info.get('name_hindi'),
        'name_english': info.get('name_english'),
        'phal': info.get('savya_phal' if chakra_type == 'Savya' else 'apsavya_phal', [])
    }


# ============================================
# RASHI TRANSITION PHALADESH (BPHS Page 453)
# ============================================
RASHI_TRANSITION_PHALADESH = {
    ('Meen', 'Vrischik'): {
        'sanskrit': 'मीनात् वृश्चिके याते ज्वरो भवति निश्चितः',
        'phal': 'ज्वर (fever) निश्चित होगा',
        'english': 'Definite fever',
        'severity': 'medium'
    },
    ('Kanya', 'Kark'): {
        'sanskrit': 'कन्यात् कर्कटे याते भ्रातृबन्धुविनाशनम्',
        'phal': 'भ्राता-बन्धु का विनाश (भाई-बहन या रिश्तेदारों की हानि)',
        'english': 'Loss of brothers/relatives',
        'severity': 'high'
    },
    ('Sinh', 'Mithun'): {
        'sanskrit': 'सिंहात् मिथुने याते स्त्रिया व्याधिर्भवेद्ध्रुवम्',
        'phal': 'स्त्री को निश्चित व्याधि (पत्नी या स्त्री वर्ग को रोग)',
        'english': 'Wife/woman illness certain',
        'severity': 'medium'
    },
    ('Kark', 'Sinh'): {
        'sanskrit': 'कर्कटाच्च हरौ याते वधो भवति देहिनाम्',
        'phal': 'मनुष्यों की मृत्यु (वध) - किसी प्रिय की हानि',
        'english': 'Death of dear ones',
        'severity': 'very_high'
    },
    ('Dhanu', 'Mesh'): {
        'sanskrit': 'चापान्मेषे गते पुनः पितृबन्धुमृतिं विद्यात्',
        'phal': 'पितृ-बन्धु की मृत्यु, विद्या नाश (शिक्षा में बाधा)',
        'english': 'Death of fatherly relatives, education obstruction',
        'severity': 'high'
    }
}

def detect_rashi_transitions(sequence):
    """Detect significant rashi transitions in sequence"""
    transitions = []
    for i in range(len(sequence) - 1):
        from_rashi = sequence[i]
        to_rashi = sequence[i + 1]
        key = (from_rashi, to_rashi)
        if key in RASHI_TRANSITION_PHALADESH:
            transitions.append({
                'position': i,
                'from_rashi': from_rashi,
                'to_rashi': to_rashi,
                'data': RASHI_TRANSITION_PHALADESH[key]
            })
    return transitions


# ============================================
# DISHA-ANUSAR PHAL (BPHS Page 454)
# Direction-based effects of dasha transitions
# ============================================
DISHA_PHALADESH = {
    ('Kanya', 'Kark'): {
        'disha': 'पूर्व',
        'disha_english': 'East',
        'phal': 'पूर्व दिशा में विशेष शुभ फल। उत्तर दिशा की यात्रा लाभदायक।',
        'shubh_disha': ['पूर्व', 'उत्तर'],
        'avoid_disha': [],
        'type': 'shubh'
    },
    ('Sinh', 'Mithun'): {
        'disha': 'नैऋत्य',
        'disha_english': 'South-West',
        'phal': 'पूर्व में हानि। बिना कार्य के नैऋत्य कोण की यात्रा सुखदायक।',
        'shubh_disha': ['नैऋत्य'],
        'avoid_disha': ['पूर्व'],
        'type': 'mixed'
    },
    ('Kark', 'Sinh'): {
        'disha': 'दक्षिण',
        'disha_english': 'South',
        'phal': 'दक्षिण दिशा में कार्य हानि। दक्षिण से पश्चिम लौटना पड़ता है।',
        'shubh_disha': ['पश्चिम'],
        'avoid_disha': ['दक्षिण'],
        'type': 'ashubh'
    },
    ('Meen', 'Vrischik'): {
        'disha': 'उत्तर',
        'disha_english': 'North',
        'phal': 'उत्तर दिशा में संकट। यात्रा से बचना चाहिए।',
        'shubh_disha': [],
        'avoid_disha': ['उत्तर'],
        'type': 'ashubh'
    },
    ('Dhanu', 'Makar'): {
        'disha': 'उत्तर',
        'disha_english': 'North',
        'phal': 'उत्तर दिशा में संकट निश्चित से आता है।',
        'shubh_disha': [],
        'avoid_disha': ['उत्तर'],
        'type': 'ashubh'
    },
    ('Dhanu', 'Mesh'): {
        'disha': 'यात्रा',
        'disha_english': 'Travel',
        'phal': 'यात्रा में रोग, बन्धन या मृत्यु हो सकती है। यात्रा से बचें।',
        'shubh_disha': [],
        'avoid_disha': ['यात्रा'],
        'type': 'very_ashubh'
    },
    ('Dhanu', 'Vrischik'): {
        'disha': 'सुख',
        'disha_english': 'Happiness',
        'phal': 'सुख-सम्पत्ति व स्त्री लाभ। यह दशा शुभ है।',
        'shubh_disha': ['सर्व'],
        'avoid_disha': [],
        'type': 'shubh'
    },
    ('Sinh', 'Kark'): {
        'disha': 'पश्चिम',
        'disha_english': 'West',
        'phal': 'पश्चिम दिशा की यात्रा स्थगित करनी चाहिए।',
        'shubh_disha': [],
        'avoid_disha': ['पश्चिम'],
        'type': 'ashubh'
    }
}

def detect_disha_phal(sequence):
    """Detect direction-based effects from sequence transitions"""
    disha_results = []
    for i in range(len(sequence) - 1):
        from_rashi = sequence[i]
        to_rashi = sequence[i + 1]
        key = (from_rashi, to_rashi)
        if key in DISHA_PHALADESH:
            disha_results.append({
                'position': i,
                'from_rashi': from_rashi,
                'to_rashi': to_rashi,
                'data': DISHA_PHALADESH[key]
            })
    return disha_results
