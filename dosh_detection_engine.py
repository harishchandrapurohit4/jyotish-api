"""
Classical Dosh Detection Engine
================================
Detects 10 classical doshas based on BPHS + traditional jyotish:

RAHU-YUTI DOSHAS (within ±8° conjunction):
1. Surya + Rahu = Pitra Dosh / Grahan Dosh
2. Chandra + Rahu = Matru Dosh / Grahan Dosh
3. Chandra + Mangal = Bhadra (Chandra-Mangal) Dosh
4. Rahu + Budh = Jad Dosh
5. Rahu + Guru = Guru Chandal Dosh
6. Rahu + Shukra = Lampat Dosh
7. Rahu + Shani = Pishach / Nadimukh Dosh

ADDITIONAL DOSHAS:
8. Manglik Dosh (Mars in 1/4/7/8/12)
9. Kaal Sarp Dosh (all planets between Rahu-Ketu)
10. Sade Sati / Dhaiya (Saturn in Moon's 12/1/2 or 4/8)
"""

from typing import Dict, List, Optional


# Conjunction orb (degrees) - close conjunction = strongest
CONJUNCTION_ORB = 8.0


def calc_orb(lon1: float, lon2: float) -> float:
    """Calculate angular distance between 2 longitudes (handles 360° wrap)"""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def is_conjunction(p1: Dict, p2: Dict, same_rashi: bool = True) -> Dict:
    """
    Check if two planets are in conjunction.
    
    Returns: {is_conjunct: bool, orb: float, same_rashi: bool, same_house: bool}
    """
    lon1 = p1.get('longitude', 0)
    lon2 = p2.get('longitude', 0)
    rashi1 = p1.get('rashi_num', 0)
    rashi2 = p2.get('rashi_num', 0)
    house1 = p1.get('house', 0)
    house2 = p2.get('house', 0)
    
    orb = calc_orb(lon1, lon2)
    
    # User wants: conjunction + same rashi
    rashi_match = (rashi1 == rashi2)
    house_match = (house1 == house2)
    
    is_conj = (orb <= CONJUNCTION_ORB) and (rashi_match if same_rashi else True)
    
    return {
        'is_conjunct': is_conj,
        'orb': round(orb, 2),
        'same_rashi': rashi_match,
        'same_house': house_match,
        'house': house1 if house_match else None,
    }


def detect_rahu_yuti_doshas(planets: Dict) -> List[Dict]:
    """
    Detect all 7 Rahu-yuti classical doshas.
    Each dosha needs conjunction within ±8° AND same rashi.
    """
    doshas = []
    
    rahu = planets.get('Rahu')
    if not rahu:
        return doshas
    
    sun = planets.get('Sun')
    moon = planets.get('Moon')
    mars = planets.get('Mars')
    mercury = planets.get('Mercury')
    jupiter = planets.get('Jupiter')
    venus = planets.get('Venus')
    saturn = planets.get('Saturn')
    
    # 1. SURYA + RAHU = Pitra/Grahan Dosh
    if sun:
        check = is_conjunction(sun, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'pitra_dosh',
                'name': 'Pitra Dosh / Surya Grahan Dosh',
                'name_hindi': 'पितृ दोष / सूर्य ग्रहण दोष',
                'planets': 'सूर्य + राहु',
                'planets_en': 'Sun + Rahu',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'very_high' if check['orb'] < 3 else 'high',
                'phal_hindi': 'पिता के स्वास्थ्य, धन और प्रतिष्ठा पर प्रभाव। पूर्वजों के अधूरे कार्यों का बोझ। संतान सुख में बाधा। आत्मविश्वास की कमी।',
                'phal_english': 'Affects father\'s health, wealth, reputation. Burden of ancestors\' incomplete deeds. Issues with progeny.',
                'shlok': 'सूर्य राहु संगते पितृ दोषं भवेत्',
                'remedies': [
                    'पितृ पक्ष में श्राद्ध एवं तर्पण',
                    'सूर्य को अर्घ्य प्रति दिन',
                    'गायत्री मंत्र जाप - 108 बार',
                    'रविवार को व्रत',
                    'पितरों के नाम से दान',
                    'Tripindi shraddh in Trimbakeshwar/Gaya',
                ],
            })
    
    # 2. CHANDRA + RAHU = Matru/Grahan Dosh
    if moon:
        check = is_conjunction(moon, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'matru_grahan_dosh',
                'name': 'Matru Dosh / Chandra Grahan Dosh',
                'name_hindi': 'मातृ दोष / चन्द्र ग्रहण दोष',
                'planets': 'चन्द्र + राहु',
                'planets_en': 'Moon + Rahu',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'very_high' if check['orb'] < 3 else 'high',
                'phal_hindi': 'माता को कष्ट। मानसिक अशांति, चिंता, अनिद्रा। मन में भय एवं भ्रम। निर्णय लेने में कठिनाई। बुरे स्वप्न।',
                'phal_english': 'Affects mother. Mental anxiety, sleeplessness, fear, indecision, bad dreams.',
                'shlok': 'चन्द्र राहु योगात् मातृ कष्टं भवेत्',
                'remedies': [
                    'सोमवार व्रत',
                    'चन्द्र मंत्र: ॐ श्रीं श्रीं चन्द्रमसे नमः - 108 बार',
                    'चांदी का चंद्र दान',
                    'दूध, चावल, सफेद वस्त्र दान',
                    'माता की सेवा एवं आशीर्वाद',
                    'मोती धारण (white pearl)',
                ],
            })
    
    # 3. CHANDRA + MANGAL = Bhadra Dosh (Chandra-Mangal Yog/Dosh)
    if moon and mars:
        check = is_conjunction(moon, mars)
        if check['is_conjunct']:
            doshas.append({
                'id': 'chandra_mangal_dosh',
                'name': 'Chandra-Mangal Bhadra Dosh',
                'name_hindi': 'चन्द्र-मंगल भद्रा दोष',
                'planets': 'चन्द्र + मंगल',
                'planets_en': 'Moon + Mars',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'medium' if check['orb'] > 5 else 'high',
                'phal_hindi': 'अति क्रोध, उग्र स्वभाव। रक्त सम्बन्धी रोग। माता को कष्ट। मानसिक तनाव। दुर्घटना का योग। पारिवारिक कलह।',
                'phal_english': 'Excessive anger, blood disorders, accidents, family discord, mental stress.',
                'shlok': 'चन्द्र मंगल योगे क्रोधाधिक्यं भवेत्',
                'note_hindi': 'विशेष: यदि शुभ ग्रह की दृष्टि हो तो यह "चन्द्र-मंगल योग" बन सकता है जो धन देता है।',
                'remedies': [
                    'हनुमान चालीसा - दैनिक पाठ',
                    'मंगलवार व्रत',
                    'मंगल मंत्र: ॐ क्रां क्रीं क्रौं सः भौमाय नमः',
                    'लाल मसूर, गुड़ दान',
                    'क्रोध पर नियंत्रण',
                    'मूंगा रत्न (coral) धारण',
                ],
            })
    
    # 4. RAHU + BUDH = Jad Dosh
    if mercury:
        check = is_conjunction(mercury, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'jad_dosh',
                'name': 'Jad Dosh',
                'name_hindi': 'जड़ दोष',
                'planets': 'राहु + बुध',
                'planets_en': 'Rahu + Mercury',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'high',
                'phal_hindi': 'जड़ बुद्धि, पढ़ाई में कठिनाई। निर्णय में भ्रम। वाणी दोष। व्यापार में हानि। चालाकी एवं धोखाधड़ी का शिकार।',
                'phal_english': 'Learning difficulties, confused decisions, speech defects, business losses, deception.',
                'shlok': 'बुध राहु योगे जड़त्वं वाक्दोषं च',
                'remedies': [
                    'गणेश पूजा - दैनिक',
                    'बुध मंत्र: ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः - 108 बार',
                    'बुधवार व्रत',
                    'हरा वस्त्र, मूंग दाल दान',
                    'पन्ना रत्न (emerald)',
                    'विद्या के लिए सरस्वती मंत्र',
                ],
            })
    
    # 5. RAHU + GURU = Guru Chandal Dosh
    if jupiter:
        check = is_conjunction(jupiter, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'guru_chandal_dosh',
                'name': 'Guru Chandal Dosh',
                'name_hindi': 'गुरु चांडाल दोष',
                'planets': 'राहु + गुरु',
                'planets_en': 'Rahu + Jupiter',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'very_high' if check['orb'] < 3 else 'high',
                'phal_hindi': 'गुरु अपमान। धर्म से विमुख। संतान सुख में बाधा। शिक्षा में रुकावट। आर्थिक अस्थिरता। गलत मार्गदर्शन।',
                'phal_english': 'Disrespect to teachers, deviation from dharma, child issues, educational obstacles, financial instability.',
                'shlok': 'गुरु राहु योगे चांडाल दोषं महान्',
                'remedies': [
                    'गुरुवार व्रत',
                    'गुरु मंत्र: ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः',
                    'विष्णु सहस्रनाम पाठ',
                    'पीपल वृक्ष पूजा',
                    'पीला वस्त्र, चना दाल, हल्दी दान',
                    'पुखराज रत्न (yellow sapphire)',
                    'गुरु की सेवा',
                ],
            })
    
    # 6. RAHU + SHUKRA = Lampat Dosh
    if venus:
        check = is_conjunction(venus, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'lampat_dosh',
                'name': 'Lampat Dosh',
                'name_hindi': 'लंपट दोष',
                'planets': 'राहु + शुक्र',
                'planets_en': 'Rahu + Venus',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'high',
                'phal_hindi': 'चरित्र दोष। व्यभिचार की प्रवृत्ति। विवाहेतर सम्बन्ध। पारिवारिक कलह। यौन रोग। संबंधों में अस्थिरता।',
                'phal_english': 'Character flaws, extra-marital tendencies, family discord, relationship instability, sexual health issues.',
                'shlok': 'शुक्र राहु संगते लंपटो जायते',
                'remedies': [
                    'शुक्रवार व्रत',
                    'लक्ष्मी पूजा',
                    'शुक्र मंत्र: ॐ द्रां द्रीं द्रौं सः शुक्राय नमः',
                    'सफेद वस्त्र, चांदी, घी दान',
                    'हीरा या ओपल (no for everyone - check chart)',
                    'चरित्र की पवित्रता',
                    'पत्नी/पति की सेवा',
                ],
            })
    
    # 7. RAHU + SHANI = Pishach / Nadimukh Dosh
    if saturn:
        check = is_conjunction(saturn, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'pishach_dosh',
                'name': 'Pishach / Nadimukh Dosh',
                'name_hindi': 'पिशाच / नदीमुख दोष',
                'planets': 'राहु + शनि',
                'planets_en': 'Rahu + Saturn',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'very_high' if check['orb'] < 3 else 'high',
                'phal_hindi': 'भय, paranoia, गुप्त रोग। मानसिक रोग। दुष्ट प्रवृत्ति। नशे का व्यसन। अकाल मृत्यु का योग। बुरे स्वप्न।',
                'phal_english': 'Fear, paranoia, hidden diseases, mental disorders, addictions, bad dreams, evil tendencies.',
                'shlok': 'शनि राहु योगे पिशाच भयं भवेत्',
                'remedies': [
                    'शनिवार व्रत',
                    'हनुमान चालीसा - 11 बार',
                    'शनि मंत्र: ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः',
                    'काला तिल, उड़द दाल, सरसों तेल दान',
                    'नीलम रत्न (blue sapphire) - only after testing',
                    'भैरव पूजा',
                    'गरीबों की सेवा',
                ],
            })
    

    # 8. RAHU + MANGAL = Angarak Dosh
    if mars:
        check = is_conjunction(mars, rahu)
        if check['is_conjunct']:
            doshas.append({
                'id': 'angarak_dosh',
                'name': 'Angarak Dosh',
                'name_hindi': 'अंगारक दोष',
                'planets': 'राहु + मंगल',
                'planets_en': 'Rahu + Mars',
                'house': check['house'],
                'orb': check['orb'],
                'severity': 'very_high' if check['orb'] < 3 else 'high',
                'phal_hindi': 'अति उग्र क्रोध, हिंसक प्रवृत्ति। दुर्घटना का योग। रक्त सम्बन्धी रोग। अकस्मात् हानि। शत्रु से कष्ट। आग, हथियार से भय।',
                'phal_english': 'Extreme aggression, accidents, blood disorders, sudden losses, enemy troubles, fire/weapon dangers.',
                'shlok': 'राहु मंगल योगे अंगारक दोषं भीषणम्',
                'remedies': [
                    'मंगलवार व्रत',
                    'हनुमान चालीसा - दैनिक 11 बार',
                    'मंगल मंत्र: ॐ क्रां क्रीं क्रौं सः भौमाय नमः - 108 बार',
                    'राहु मंत्र: ॐ रां राहवे नमः',
                    'सुंदरकांड पाठ',
                    'गुड़, मसूर दाल, लाल वस्त्र दान',
                    'मूंगा रत्न (coral) धारण - after testing',
                    'क्रोध पर नियंत्रण आवश्यक',
                    'हनुमान जी की पूजा',
                ],
            })

    return doshas


def detect_manglik_dosh(planets: Dict) -> Optional[Dict]:
    """Detect Mangal Dosh (Manglik) - Mars in 1/4/7/8/12 from Lagna"""
    mars = planets.get('Mars')
    if not mars:
        return None
    
    house = mars.get('house', 0)
    rashi_num = mars.get('rashi_num', 0)
    
    # Manglik houses
    MANGLIK_HOUSES = [1, 4, 7, 8, 12]
    
    # Sampat exception (Mars exalted/own sign in these houses)
    SAMPAT_EXCEPTIONS = {1: 0, 4: 7, 7: 0, 8: 7, 12: 8}  # rashi_num where Mars is OK
    
    if house not in MANGLIK_HOUSES:
        return None
    
    # Check Sampat exception
    sampat_rashi = SAMPAT_EXCEPTIONS.get(house)
    if sampat_rashi is not None and rashi_num == sampat_rashi:
        return {
            'id': 'manglik_sampat',
            'name': 'Mangal Dosh - Sampat',
            'name_hindi': 'मंगल दोष - सम्पात',
            'planets': 'मंगल',
            'house': house,
            'severity': 'low',
            'phal_hindi': 'मंगल अपनी स्वराशि/उच्च राशि में है। दोष सम्पात हो जाता है। विवाह में बाधा नहीं।',
            'remedies': ['विशेष उपाय की आवश्यकता नहीं', 'मंगलवार व्रत वैकल्पिक'],
        }
    
    severity_map = {1: 'high', 4: 'medium', 7: 'very_high', 8: 'very_high', 12: 'high'}
    
    return {
        'id': 'manglik_dosh',
        'name': 'Mangal Dosh (Manglik)',
        'name_hindi': 'मंगल दोष (मांगलिक)',
        'planets': 'मंगल',
        'planets_en': 'Mars',
        'house': house,
        'severity': severity_map.get(house, 'high'),
        'phal_hindi': f'मंगल {house}वें भाव में है। वैवाहिक जीवन पर प्रभाव। पति/पत्नी से कलह। विवाह में देरी। रक्त सम्बन्धी समस्याएं।',
        'phal_english': f'Mars in {house}th house. Affects marriage, spouse relationship, blood disorders, delays in marriage.',
        'shlok': 'लग्ने व्यये पाताले जामित्रे चाष्टमे कुजे, कन्या भर्तृविनाशस्तु भर्ता वा प्रमीयते',
        'remedies': [
            'मंगलवार व्रत',
            'हनुमान चालीसा दैनिक',
            'मंगल मंत्र: ॐ क्रां क्रीं क्रौं सः भौमाय नमः - 108 बार',
            'मंगल यंत्र पूजा',
            'लाल वस्त्र, गुड़, मूंगा दान',
            'मंगल की शान्ति विधि विवाह से पूर्व',
            'मांगलिक से ही विवाह (preferred)',
        ],
    }


def detect_kaal_sarp_dosh(planets: Dict) -> Optional[Dict]:
    """
    Detect Kaal Sarp Dosh - all planets between Rahu-Ketu axis.
    Returns dosh details with type (12 prakaar).
    """
    rahu = planets.get('Rahu')
    ketu = planets.get('Ketu')
    if not rahu or not ketu:
        return None
    
    rahu_lon = rahu.get('longitude', 0) % 360
    ketu_lon = ketu.get('longitude', 0) % 360
    
    # Get other planets (excluding Rahu, Ketu)
    other_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    other_lons = []
    for name in other_planets:
        p = planets.get(name)
        if p:
            other_lons.append(p.get('longitude', 0) % 360)
    
    if not other_lons:
        return None
    
    def in_arc(lon, from_deg, to_deg):
        """Check if lon is between from→to (going clockwise)"""
        if from_deg <= to_deg:
            return from_deg <= lon <= to_deg
        return lon >= from_deg or lon <= to_deg
    
    # Check both arcs
    arc1_all = all(in_arc(l, rahu_lon, ketu_lon) for l in other_lons)
    arc2_all = all(in_arc(l, ketu_lon, rahu_lon) for l in other_lons)
    
    if not (arc1_all or arc2_all):
        return None
    
    # Determine type based on Rahu's house
    rahu_house = rahu.get('house', 0)
    
    KAAL_SARP_TYPES = {
        1: ('Anant', 'अनंत', 'राहु प्रथम भाव में - मानसिक तनाव, संदेह'),
        2: ('Kulik', 'कुलिक', 'राहु द्वितीय भाव में - धन हानि, वाक् दोष'),
        3: ('Vasuki', 'वासुकि', 'राहु तृतीय भाव में - भाई बहन से कष्ट'),
        4: ('Shankhpal', 'शंखपाल', 'राहु चतुर्थ भाव में - माता, गृह सुख में बाधा'),
        5: ('Padma', 'पद्म', 'राहु पंचम भाव में - संतान सुख में बाधा, शिक्षा'),
        6: ('Mahapadma', 'महापद्म', 'राहु षष्ठ भाव में - शत्रु, रोग की प्रबलता'),
        7: ('Takshak', 'तक्षक', 'राहु सप्तम भाव में - विवाह, पार्टनरशिप में कष्ट'),
        8: ('Karkotaka', 'कर्कोटक', 'राहु अष्टम भाव में - दुर्घटना, अकाल मृत्यु भय'),
        9: ('Shankhachuda', 'शंखचूड़', 'राहु नवम भाव में - भाग्य, धर्म में बाधा'),
        10: ('Ghatak', 'घातक', 'राहु दशम भाव में - कर्म, करियर में बाधा'),
        11: ('Vishdhar', 'विषधर', 'राहु एकादश भाव में - लाभ में कमी, मित्र हानि'),
        12: ('Sheshnag', 'शेषनाग', 'राहु द्वादश भाव में - व्यय, मानसिक शांति में कमी'),
    }
    
    type_en, type_hi, phal = KAAL_SARP_TYPES.get(rahu_house, ('Unknown', 'अज्ञात', ''))
    
    return {
        'id': 'kaal_sarp_dosh',
        'name': f'Kaal Sarp Dosh - {type_en}',
        'name_hindi': f'काल सर्प दोष - {type_hi}',
        'planets': 'राहु + केतु (with all others between)',
        'planets_en': 'Rahu + Ketu axis',
        'severity': 'very_high',
        'type': type_en,
        'type_hindi': type_hi,
        'rahu_house': rahu_house,
        'phal_hindi': f'सभी ग्रह राहु-केतु के बीच में हैं। {phal} जीवन में बाधाएं, संघर्ष, देरी संभव।',
        'phal_english': f'All planets between Rahu-Ketu axis ({type_en} type). Life obstacles, struggles, delays.',
        'shlok': 'राहु केतु मध्य सर्व ग्रह स्थाने काल सर्प दोषं भवेत्',
        'remedies': [
            'काल सर्प दोष शान्ति पूजा - Trimbakeshwar/Ujjain/Kalahasti',
            'नाग पंचमी पर विशेष पूजा',
            'महामृत्युंजय मंत्र - 108 बार दैनिक',
            'भगवान शिव की पूजा',
            'राहु-केतु यंत्र पूजा',
            'सर्प की चांदी की प्रतिमा प्रवाहित करना',
            'काले तिल, मसूर, सरसों तेल दान',
            'गोमेद + लहसुनिया रत्न (after consultation)',
        ],
    }


def detect_sade_sati(planets: Dict) -> Optional[Dict]:
    """Detect Sade Sati (Saturn in Moon's 12/1/2) or Dhaiya (Saturn in Moon's 4/8)"""
    moon = planets.get('Moon')
    saturn = planets.get('Saturn')
    if not moon or not saturn:
        return None
    
    moon_rashi = moon.get('rashi_num', 0)
    saturn_rashi = saturn.get('rashi_num', 0)
    
    # Calculate Saturn's position from Moon
    diff = (saturn_rashi - moon_rashi) % 12
    
    if diff == 11:  # 12th from moon (start of Sade Sati)
        phase = 'पहला चरण - प्रारंभ'
        phase_en = 'First phase - Beginning'
        severity = 'medium'
    elif diff == 0:  # Same as moon (peak)
        phase = 'दूसरा चरण - शिखर'
        phase_en = 'Second phase - Peak'
        severity = 'very_high'
    elif diff == 1:  # 2nd from moon (end)
        phase = 'तीसरा चरण - अंत'
        phase_en = 'Third phase - End'
        severity = 'medium'
    elif diff == 3:  # 4th from moon (Dhaiya)
        return {
            'id': 'kantak_shani',
            'name': 'Kantak Shani (Dhaiya)',
            'name_hindi': 'कंटक शनि (ढैया)',
            'planets': 'शनि (चन्द्र से चतुर्थ)',
            'severity': 'high',
            'phal_hindi': 'कंटक शनि - माता, घर, वाहन में कष्ट। मानसिक तनाव।',
            'remedies': ['शनिवार व्रत', 'हनुमान चालीसा'],
        }
    elif diff == 7:  # 8th from moon (Ashtam Shani)
        return {
            'id': 'ashtam_shani',
            'name': 'Ashtam Shani (Dhaiya)',
            'name_hindi': 'अष्टम शनि (ढैया)',
            'planets': 'शनि (चन्द्र से अष्टम)',
            'severity': 'very_high',
            'phal_hindi': 'अष्टम शनि - दुर्घटना, स्वास्थ्य, गुप्त रोग का योग।',
            'remedies': ['शनि शान्ति', 'हनुमान पूजा', 'काले तिल दान'],
        }
    else:
        return None
    
    return {
        'id': 'sade_sati',
        'name': f'Sade Sati - {phase_en}',
        'name_hindi': f'साढ़े साती - {phase}',
        'planets': 'शनि (चन्द्र राशि से)',
        'planets_en': 'Saturn (from Moon rashi)',
        'severity': severity,
        'phase': phase,
        'phal_hindi': f'साढ़े साती चल रही है ({phase})। 7.5 वर्ष की अवधि। कठिन समय, धैर्य आवश्यक। आत्म-विकास का काल।',
        'phal_english': f'Sade Sati ongoing ({phase_en}). 7.5 year period. Challenging time, requires patience. Self-development phase.',
        'remedies': [
            'शनिवार व्रत',
            'हनुमान चालीसा दैनिक - 7 बार',
            'शनि मंत्र: ॐ शं शनैश्चराय नमः - 108 बार',
            'काले तिल, उड़द, सरसों तेल दान',
            'पीपल वृक्ष पूजा',
            'गरीबों, मजदूरों की सेवा',
            'महामृत्युंजय जाप',
            'नीलम रत्न (only after testing)',
        ],
    }


def detect_all_doshas(planets: Dict, lagna: Dict = None) -> Dict:
    """
    Master function - detect all 10+ classical doshas.
    
    Args:
        planets: Dict with planet data (must have rashi_num, longitude, house)
        lagna: Lagna info (optional)
    
    Returns:
        Complete dosh analysis with severity grouping
    """
    all_doshas = []
    
    # 1-7: Rahu yutis
    rahu_doshas = detect_rahu_yuti_doshas(planets)
    all_doshas.extend(rahu_doshas)
    
    # 8: Manglik
    manglik = detect_manglik_dosh(planets)
    if manglik:
        all_doshas.append(manglik)
    
    # 9: Kaal Sarp
    kaal_sarp = detect_kaal_sarp_dosh(planets)
    if kaal_sarp:
        all_doshas.append(kaal_sarp)
    
    # 10: Sade Sati
    sade_sati = detect_sade_sati(planets)
    if sade_sati:
        all_doshas.append(sade_sati)
    
    # Group by severity
    severity_order = {'very_high': 4, 'high': 3, 'medium': 2, 'low': 1}
    all_doshas.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 0), reverse=True)
    
    # Summary
    severity_count = {'very_high': 0, 'high': 0, 'medium': 0, 'low': 0}
    for d in all_doshas:
        sev = d.get('severity', 'low')
        severity_count[sev] = severity_count.get(sev, 0) + 1
    
    highest_severity = 'none'
    if severity_count['very_high'] > 0: highest_severity = 'very_high'
    elif severity_count['high'] > 0: highest_severity = 'high'
    elif severity_count['medium'] > 0: highest_severity = 'medium'
    elif severity_count['low'] > 0: highest_severity = 'low'
    
    return {
        'total_doshas': len(all_doshas),
        'highest_severity': highest_severity,
        'severity_count': severity_count,
        'doshas': all_doshas,
        'summary_hindi': _generate_summary(all_doshas),
        'summary_english': _generate_summary_en(all_doshas),
    }


def _generate_summary(doshas: List[Dict]) -> str:
    """Generate Hindi summary"""
    if not doshas:
        return 'कोई महत्वपूर्ण दोष नहीं पाया गया। शुभ कुंडली।'
    
    count = len(doshas)
    very_high = [d for d in doshas if d.get('severity') == 'very_high']
    
    if very_high:
        names = ', '.join([d['name_hindi'] for d in very_high[:3]])
        return f'{count} दोष पाए गए। मुख्य: {names}। शान्ति विधि अनुशंसित।'
    return f'{count} दोष पाए गए। शान्ति विधि से निवारण संभव।'


def _generate_summary_en(doshas: List[Dict]) -> str:
    """Generate English summary"""
    if not doshas:
        return 'No major doshas detected. Auspicious chart.'
    
    count = len(doshas)
    very_high = [d for d in doshas if d.get('severity') == 'very_high']
    
    if very_high:
        names = ', '.join([d['name'] for d in very_high[:3]])
        return f'{count} doshas detected. Critical: {names}. Shanti vidhi recommended.'
    return f'{count} doshas detected. Remedies available.'
