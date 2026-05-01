"""
Dashakoot Milan v3 - Final
=============================
Includes:
- 8 Koots calculation (Ashtakoot 36)
- Naadi/Bhakoot/Gana dosha display (score = 0 when dosha)
- Bhang reasons (separate, premium-only)
- Mangal Dosha CLASSICAL with paap counting + cancellation
- Specific upay per dosha
"""

import swisseph as swe
from datetime import datetime
from typing import Dict, List

# Import classical mangal dosha
import sys
sys.path.insert(0, '/root/jyotish-api')
from mangal_dosha_classical import compare_mangal_dosha

RASHI_NAMES = ['Mesh', 'Vrishabh', 'Mithun', 'Kark', 'Simha', 'Kanya',
               'Tula', 'Vrishchik', 'Dhanu', 'Makar', 'Kumbh', 'Meen']

RASHI_HINDI = ['मेष', 'वृषभ', 'मिथुन', 'कर्क', 'सिंह', 'कन्या',
               'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Aardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mool', 'Purvashadha', 'Uttarashadha', 'Shravan', 'Dhanishtha', 'Shatabhisha',
    'Purvabhadrapada', 'Uttarabhadrapada', 'Revati'
]

# ============================================================================
# 1. VARNA
# ============================================================================
VARNA_MAP = {
    3: 'Brahmin', 7: 'Brahmin', 11: 'Brahmin',
    0: 'Kshatriya', 4: 'Kshatriya', 8: 'Kshatriya',
    1: 'Vaishya', 5: 'Vaishya', 9: 'Vaishya',
    2: 'Shudra', 6: 'Shudra', 10: 'Shudra',
}
VARNA_RANK = {'Brahmin': 4, 'Kshatriya': 3, 'Vaishya': 2, 'Shudra': 1}


def calc_varna(boy_rashi_idx, girl_rashi_idx):
    boy_v = VARNA_MAP[boy_rashi_idx]
    girl_v = VARNA_MAP[girl_rashi_idx]
    if VARNA_RANK[boy_v] >= VARNA_RANK[girl_v]:
        return {'name': 'Varna', 'hindi': 'वर्ण', 'meaning': 'वर्ण मेल',
                'boy_value': boy_v, 'girl_value': girl_v,
                'score': 1, 'max': 1, 'is_shubh': True,
                'phaladesh': f"वर का वर्ण ({boy_v}) वधु ({girl_v}) से उच्च — शुभ",
                'dosha': None, 'bhang': False}
    return {'name': 'Varna', 'hindi': 'वर्ण', 'meaning': 'वर्ण मेल',
            'boy_value': boy_v, 'girl_value': girl_v,
            'score': 0, 'max': 1, 'is_shubh': False,
            'phaladesh': "वर्ण अनुकूल नहीं", 'dosha': None, 'bhang': False}


# ============================================================================
# 2. VASHYA
# ============================================================================
VASHYA_LOOKUP = {0: 'Chatushpad', 1: 'Chatushpad', 2: 'Manav', 3: 'Jalachar',
                 4: 'Vanachar', 5: 'Manav', 6: 'Manav', 7: 'Keet',
                 8: 'Manav', 9: 'Chatushpad', 10: 'Manav', 11: 'Jalachar'}

VASHYA_COMPATIBILITY = {
    'Manav': {'Manav': 2, 'Chatushpad': 1, 'Jalachar': 1, 'Vanachar': 0, 'Keet': 1},
    'Chatushpad': {'Manav': 1, 'Chatushpad': 2, 'Jalachar': 0.5, 'Vanachar': 1, 'Keet': 1},
    'Jalachar': {'Manav': 1, 'Chatushpad': 0.5, 'Jalachar': 2, 'Vanachar': 0, 'Keet': 0.5},
    'Vanachar': {'Manav': 0, 'Chatushpad': 1, 'Jalachar': 0, 'Vanachar': 2, 'Keet': 0},
    'Keet': {'Manav': 1, 'Chatushpad': 1, 'Jalachar': 0.5, 'Vanachar': 0, 'Keet': 2},
}


def calc_vashya(boy_idx, girl_idx):
    boy_v = VASHYA_LOOKUP[boy_idx]
    girl_v = VASHYA_LOOKUP[girl_idx]
    score = VASHYA_COMPATIBILITY.get(boy_v, {}).get(girl_v, 0)
    return {'name': 'Vashya', 'hindi': 'वश्य', 'meaning': 'सन्तान सुख',
            'boy_value': boy_v, 'girl_value': girl_v,
            'score': score, 'max': 2, 'is_shubh': score >= 1,
            'phaladesh': f"वर ({boy_v}) व वधु ({girl_v}) का वश्य {'पूर्ण' if score == 2 else 'मध्यम' if score >= 1 else 'अनुकूल नहीं'}",
            'dosha': None, 'bhang': False}


# ============================================================================
# 3. TARA
# ============================================================================
def calc_tara(boy_nak, girl_nak):
    diff_b_to_g = ((girl_nak - boy_nak) % 27) + 1
    diff_g_to_b = ((boy_nak - girl_nak) % 27) + 1
    tara1 = diff_b_to_g % 9 or 9
    tara2 = diff_g_to_b % 9 or 9
    g1 = tara1 in [2, 4, 6, 8, 9]
    g2 = tara2 in [2, 4, 6, 8, 9]
    if g1 and g2:
        score, ph = 3, "दोनों की तारा अनुकूल"
    elif g1 or g2:
        score, ph = 1.5, "एक तारा अनुकूल, दूसरी मध्यम"
    else:
        score, ph = 0, "दोनों की तारा प्रतिकूल"
    return {'name': 'Tara', 'hindi': 'तारा (दिनम्)', 'meaning': 'भाग्य व आयु',
            'boy_value': f"Tara {tara2}", 'girl_value': f"Tara {tara1}",
            'score': score, 'max': 3, 'is_shubh': score >= 1.5,
            'phaladesh': ph, 'dosha': None, 'bhang': False}


# ============================================================================
# 4. YONI
# ============================================================================
YONI_LOOKUP = ['Ashwa', 'Gaja', 'Mesh', 'Sarp', 'Sarp', 'Shwan', 'Marjar',
               'Mesh', 'Marjar', 'Mushak', 'Mushak', 'Gau', 'Mahish',
               'Vyaghra', 'Mahish', 'Vyaghra', 'Mrig', 'Mrig', 'Shwan',
               'Vanara', 'Nakul', 'Vanara', 'Sinh', 'Ashwa', 'Sinh',
               'Gau', 'Gaja']

YONI_FRIEND = {'Ashwa': ['Mahish'], 'Gaja': ['Mesh'], 'Mesh': ['Gaja', 'Marjar'],
               'Sarp': ['Vanara'], 'Shwan': ['Mrig'], 'Marjar': ['Mushak', 'Mesh'],
               'Mushak': ['Marjar'], 'Gau': ['Vyaghra'], 'Mahish': ['Ashwa'],
               'Vyaghra': ['Gau', 'Sinh'], 'Mrig': ['Shwan'], 'Vanara': ['Sarp', 'Nakul'],
               'Nakul': ['Vanara'], 'Sinh': ['Vyaghra']}

YONI_ENEMY = {'Ashwa': ['Mahish'], 'Gaja': ['Sinh'], 'Mesh': ['Vanara'],
              'Sarp': ['Nakul'], 'Shwan': ['Mrig'], 'Marjar': ['Mushak'],
              'Mushak': ['Marjar'], 'Gau': ['Vyaghra'], 'Mahish': ['Ashwa'],
              'Vyaghra': ['Gau'], 'Mrig': ['Shwan'], 'Vanara': ['Mesh'],
              'Nakul': ['Sarp'], 'Sinh': ['Gaja']}


def calc_yoni(boy_nak, girl_nak):
    boy_y = YONI_LOOKUP[boy_nak % 27]
    girl_y = YONI_LOOKUP[girl_nak % 27]
    if boy_y == girl_y:
        score, ph = 4, f"दोनों की योनि समान ({boy_y}) — शुभ"
    elif girl_y in YONI_FRIEND.get(boy_y, []):
        score, ph = 3, f"योनि मित्रवत्"
    elif girl_y in YONI_ENEMY.get(boy_y, []):
        score, ph = 0, f"योनि शत्रुवत्"
    else:
        score, ph = 2, "योनि सम"
    return {'name': 'Yoni', 'hindi': 'योनि', 'meaning': 'शारीरिक मेल',
            'boy_value': boy_y, 'girl_value': girl_y,
            'score': score, 'max': 4, 'is_shubh': score >= 2,
            'phaladesh': ph, 'dosha': None, 'bhang': False}


# ============================================================================
# 5. GRAHA MAITRI
# ============================================================================
RASHI_LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
               'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']

GRAHA_FRIENDSHIP = {
    'Sun': {'friends': ['Moon', 'Mars', 'Jupiter'], 'enemies': ['Venus', 'Saturn']},
    'Moon': {'friends': ['Sun', 'Mercury'], 'enemies': []},
    'Mars': {'friends': ['Sun', 'Moon', 'Jupiter'], 'enemies': ['Mercury']},
    'Mercury': {'friends': ['Sun', 'Venus'], 'enemies': ['Moon']},
    'Jupiter': {'friends': ['Sun', 'Moon', 'Mars'], 'enemies': ['Mercury', 'Venus']},
    'Venus': {'friends': ['Mercury', 'Saturn'], 'enemies': ['Sun', 'Moon']},
    'Saturn': {'friends': ['Mercury', 'Venus'], 'enemies': ['Sun', 'Moon', 'Mars']},
}


def get_friendship(g1, g2):
    if g1 == g2:
        return 'same'
    info = GRAHA_FRIENDSHIP.get(g1, {})
    if g2 in info.get('friends', []):
        return 'friend'
    if g2 in info.get('enemies', []):
        return 'enemy'
    return 'neutral'


def calc_graha_maitri(boy_idx, girl_idx):
    boy_l = RASHI_LORDS[boy_idx]
    girl_l = RASHI_LORDS[girl_idx]
    f1 = get_friendship(boy_l, girl_l)
    f2 = get_friendship(girl_l, boy_l)
    if boy_l == girl_l:
        score, ph = 5, f"राशीश समान ({boy_l}) — पूर्ण मैत्री"
    elif f1 == 'friend' and f2 == 'friend':
        score, ph = 5, f"राशीश ({boy_l}, {girl_l}) मित्र"
    elif f1 == 'friend' or f2 == 'friend':
        score, ph = 4, "एक की मित्रता"
    elif f1 == 'enemy' and f2 == 'enemy':
        score, ph = 0, f"राशीश ({boy_l}, {girl_l}) शत्रु"
    else:
        score, ph = 3, "मध्यम मैत्री"
    return {'name': 'GrahaMaitri', 'hindi': 'राश्याधिपति', 'meaning': 'धन धान्य',
            'boy_value': boy_l, 'girl_value': girl_l,
            'score': score, 'max': 5, 'is_shubh': score >= 3,
            'phaladesh': ph, 'dosha': None, 'bhang': False}


# ============================================================================
# 6. GANA
# ============================================================================
GANA_MAP = {
    'Ashwini': 'Deva', 'Mrigashira': 'Deva', 'Punarvasu': 'Deva',
    'Pushya': 'Deva', 'Hasta': 'Deva', 'Swati': 'Deva',
    'Anuradha': 'Deva', 'Shravan': 'Deva', 'Revati': 'Deva',
    'Bharani': 'Manushya', 'Rohini': 'Manushya', 'Aardra': 'Manushya',
    'Purva Phalguni': 'Manushya', 'Uttara Phalguni': 'Manushya',
    'Purvashadha': 'Manushya', 'Uttarashadha': 'Manushya',
    'Purvabhadrapada': 'Manushya', 'Uttarabhadrapada': 'Manushya',
    'Krittika': 'Rakshasa', 'Ashlesha': 'Rakshasa', 'Magha': 'Rakshasa',
    'Chitra': 'Rakshasa', 'Vishakha': 'Rakshasa', 'Jyeshtha': 'Rakshasa',
    'Mool': 'Rakshasa', 'Dhanishtha': 'Rakshasa', 'Shatabhisha': 'Rakshasa',
}


def calc_gana(boy_nak, girl_nak):
    bnak = NAKSHATRA_NAMES[boy_nak]
    gnak = NAKSHATRA_NAMES[girl_nak]
    bg = GANA_MAP.get(bnak, 'Manushya')
    gg = GANA_MAP.get(gnak, 'Manushya')
    dosha = None
    if bg == gg:
        score, ph = 6, f"समान गण ({bg}) — पूर्ण शुभ"
    elif {bg, gg} == {'Deva', 'Manushya'}:
        score, ph = 5, "देव-मनुष्य — शुभ"
    elif {bg, gg} == {'Manushya', 'Rakshasa'}:
        score, ph = 0, "मनुष्य-राक्षस गण विरोध"
        dosha = "Gana Dosha (Manushya-Rakshasa)"
    elif {bg, gg} == {'Deva', 'Rakshasa'}:
        score, ph = 1, "देव-राक्षस गण विरोध"
        dosha = "Gana Dosha (Deva-Rakshasa)"
    else:
        score, ph = 3, "मध्यम"
    return {'name': 'Gana', 'hindi': 'गण', 'meaning': 'मानसिक अनुकूलता',
            'boy_value': bg, 'girl_value': gg,
            'score': score, 'max': 6, 'is_shubh': score >= 3,
            'phaladesh': ph, 'dosha': dosha, 'bhang': False}


# ============================================================================
# 7. BHAKOOT
# ============================================================================
def calc_bhakoot(boy_idx, girl_idx):
    diff = ((girl_idx - boy_idx) % 12) + 1
    diff_r = ((boy_idx - girl_idx) % 12) + 1
    is_dosha = False
    dosha_name = None
    if diff in [6, 8] or diff_r in [6, 8]:
        is_dosha = True
        dosha_name = "Bhakoot Dosha (6/8 — Shadashtak)"
    elif diff in [5, 9] or diff_r in [5, 9]:
        is_dosha = True
        dosha_name = "Bhakoot Dosha (5/9 — Navpancham)"
    elif diff in [2, 12] or diff_r in [2, 12]:
        is_dosha = True
        dosha_name = "Bhakoot Dosha (2/12 — Dwirdwadash)"
    
    boy_l = RASHI_LORDS[boy_idx]
    girl_l = RASHI_LORDS[girl_idx]
    bhang = False
    bhang_reason = None
    if is_dosha:
        if boy_l == girl_l:
            bhang = True
            bhang_reason = f"दोनों राशियों का स्वामी एक ({boy_l}) — दोष भंग"
        elif get_friendship(boy_l, girl_l) == 'friend':
            bhang = True
            bhang_reason = f"राशीश ({boy_l}, {girl_l}) मित्र — दोष भंग"
    
    score = 7 if not is_dosha else 0
    ph = "भकूट दोष नहीं — शुभ" if not is_dosha else dosha_name
    return {'name': 'Bhakoot', 'hindi': 'भकूट (राशि)', 'meaning': 'राशि स्थिति',
            'boy_value': RASHI_NAMES[boy_idx], 'girl_value': RASHI_NAMES[girl_idx],
            'score': score, 'max': 7, 'is_shubh': not is_dosha,
            'phaladesh': ph, 'dosha': dosha_name, 'bhang': bhang,
            'bhang_reason': bhang_reason,
            'upay': "विष्णु सहस्त्रनाम पाठ, राशि स्वामी मंत्र जप" if is_dosha else None}


# ============================================================================
# 8. NAADI
# ============================================================================
# Classical Naadi mapping (PURVA KALAMRUTAM authority)
# Adi: Ashwini, Aardra, Punarvasu, U.Phalguni, Hasta, Jyeshtha, Mool, Shatabhisha, P.Bhadrapada
# Madhya: Bharani, Mrigashira, Pushya, P.Phalguni, Chitra, Anuradha, P.Ashadha, Dhanishtha, U.Bhadrapada
# Antya: Krittika, Rohini, Ashlesha, Magha, Swati, Vishakha, U.Ashadha, Shravan, Revati
NAADI_MAP = [
    'Adi',      # 0  - Ashwini
    'Madhya',   # 1  - Bharani
    'Antya',    # 2  - Krittika
    'Antya',    # 3  - Rohini
    'Madhya',   # 4  - Mrigashira
    'Adi',      # 5  - Aardra
    'Adi',      # 6  - Punarvasu
    'Madhya',   # 7  - Pushya
    'Antya',    # 8  - Ashlesha
    'Antya',    # 9  - Magha
    'Madhya',   # 10 - Purva Phalguni
    'Adi',      # 11 - Uttara Phalguni
    'Adi',      # 12 - Hasta
    'Madhya',   # 13 - Chitra
    'Antya',    # 14 - Swati
    'Antya',    # 15 - Vishakha
    'Madhya',   # 16 - Anuradha
    'Adi',      # 17 - Jyeshtha
    'Adi',      # 18 - Mool
    'Madhya',   # 19 - Purvashadha
    'Antya',    # 20 - Uttarashadha
    'Antya',    # 21 - Shravan
    'Madhya',   # 22 - Dhanishtha
    'Adi',      # 23 - Shatabhisha
    'Adi',      # 24 - Purvabhadrapada
    'Madhya',   # 25 - Uttarabhadrapada
    'Antya',    # 26 - Revati
]

NAADI_BHANG_NAKSHATRAS = ['Vishakha', 'Anuradha', 'Dhanishtha', 'Revati',
                          'Hasta', 'Swati', 'Aardra', 'Purvabhadrapada',
                          'Uttarabhadrapada', 'Rohini', 'Shravan', 'Pushya', 'Magha']


def calc_naadi(boy_nak, girl_nak, boy_rashi, girl_rashi):
    boy_n = NAADI_MAP[boy_nak]
    girl_n = NAADI_MAP[girl_nak]
    if boy_n != girl_n:
        return {'name': 'Naadi', 'hindi': 'नाड़ी', 'meaning': 'सन्तान व आरोग्य',
                'boy_value': boy_n, 'girl_value': girl_n,
                'score': 8, 'max': 8, 'is_shubh': True,
                'phaladesh': f"नाड़ी अलग ({boy_n}-{girl_n}) — पूर्ण शुभ",
                'dosha': None, 'bhang': False, 'bhang_reason': None, 'upay': None}
    
    # Same naadi = dosha
    bhang_conds = []
    if boy_rashi == girl_rashi and boy_nak != girl_nak:
        bhang_conds.append("एक राशि भिन्न नक्षत्र")
    if boy_nak == girl_nak:
        bhang_conds.append("एक नक्षत्र — चरण भेद")
    bnak = NAKSHATRA_NAMES[boy_nak]
    gnak = NAKSHATRA_NAMES[girl_nak]
    if bnak in NAADI_BHANG_NAKSHATRAS:
        bhang_conds.append(f"वर का नक्षत्र ({bnak}) भंग नक्षत्र")
    if gnak in NAADI_BHANG_NAKSHATRAS:
        bhang_conds.append(f"वधु का नक्षत्र ({gnak}) भंग नक्षत्र")
    boy_l = RASHI_LORDS[boy_rashi]
    girl_l = RASHI_LORDS[girl_rashi]
    if boy_l == girl_l:
        bhang_conds.append(f"राशि स्वामी एक ({boy_l})")
    elif get_friendship(boy_l, girl_l) == 'friend':
        bhang_conds.append(f"राशीश ({boy_l}, {girl_l}) मित्र")
    
    return {'name': 'Naadi', 'hindi': 'नाड़ी', 'meaning': 'सन्तान व आरोग्य',
            'boy_value': boy_n, 'girl_value': girl_n,
            'score': 0, 'max': 8, 'is_shubh': False,
            'phaladesh': f"नाड़ी दोष ({boy_n}-{girl_n}) — सावधानी",
            'dosha': f"Naadi Dosha (समान {boy_n} नाड़ी)",
            'bhang': len(bhang_conds) > 0,
            'bhang_reason': "; ".join(bhang_conds) if bhang_conds else None,
            'upay': "नाड़ी शान्ति पूजा, महामृत्युंजय जप 1.25 लाख"}



# ============================================================================
# 9. MAHENDRA KOOT (1 point) — परस्पर प्रेम
# ============================================================================
MAHENDRA_FAVORABLE = {4, 7, 10, 13, 16, 19, 22, 25}

def calc_mahendra(boy_nak, girl_nak):
    """Mahendra Koot - count from boy's nakshatra to girl's"""
    count = ((girl_nak - boy_nak) % 27) + 1
    bnak = NAKSHATRA_NAMES[boy_nak]
    gnak = NAKSHATRA_NAMES[girl_nak]
    if count in MAHENDRA_FAVORABLE:
        return {
            'name': 'Mahendra', 'hindi': 'महेन्द्र', 'meaning': 'परस्पर प्रेम व सन्तान',
            'boy_value': bnak, 'girl_value': gnak,
            'score': 1, 'max': 1, 'is_shubh': True,
            'phaladesh': f"नक्षत्र गणना {count} — शुभ। परस्पर प्रेम व सन्तान सुख।",
            'dosha': None, 'bhang': False, 'bhang_reason': None, 'upay': None
        }
    return {
        'name': 'Mahendra', 'hindi': 'महेन्द्र', 'meaning': 'परस्पर प्रेम व सन्तान',
        'boy_value': bnak, 'girl_value': gnak,
        'score': 0, 'max': 1, 'is_shubh': False,
        'phaladesh': f"नक्षत्र गणना {count} — अशुभ। परस्पर प्रेम में कमी।",
        'dosha': "Mahendra Dosha",
        'bhang': True, 'bhang_reason': "महेन्द्र दोष भंग के लिए विशेष विचार आवश्यक",
        'upay': "महामृत्युंजय जप 1.25 लाख, दम्पति सूक्त पाठ, पारस्परिक प्रेम वर्धक मंत्र"
    }


# ============================================================================
# 10. STRIDIRGHA KOOT (3 points) — वैवाहिक दीर्घता
# ============================================================================
def calc_stridirgha(boy_nak, girl_nak):
    """Stridirgha Koot - girl's nakshatra should be far from boy's (>=14)"""
    count = ((girl_nak - boy_nak) % 27) + 1
    bnak = NAKSHATRA_NAMES[boy_nak]
    gnak = NAKSHATRA_NAMES[girl_nak]
    if count >= 14:
        return {
            'name': 'Stridirgha', 'hindi': 'स्त्रीदीर्घ', 'meaning': 'वैवाहिक दीर्घता',
            'boy_value': bnak, 'girl_value': gnak,
            'score': 3, 'max': 3, 'is_shubh': True,
            'phaladesh': f"नक्षत्र दूरी {count} — पूर्ण शुभ। वैवाहिक दीर्घता उत्तम।",
            'dosha': None, 'bhang': False, 'bhang_reason': None, 'upay': None
        }
    elif count >= 9:
        return {
            'name': 'Stridirgha', 'hindi': 'स्त्रीदीर्घ', 'meaning': 'वैवाहिक दीर्घता',
            'boy_value': bnak, 'girl_value': gnak,
            'score': 1.5, 'max': 3, 'is_shubh': True,
            'phaladesh': f"नक्षत्र दूरी {count} — मध्यम। सामान्य वैवाहिक जीवन।",
            'dosha': None, 'bhang': False, 'bhang_reason': None, 'upay': None
        }
    return {
        'name': 'Stridirgha', 'hindi': 'स्त्रीदीर्घ', 'meaning': 'वैवाहिक दीर्घता',
        'boy_value': bnak, 'girl_value': gnak,
        'score': 0, 'max': 3, 'is_shubh': False,
        'phaladesh': f"नक्षत्र दूरी {count} — अशुभ। वैवाहिक दीर्घता में बाधा।",
        'dosha': "Stridirgha Dosha",
        'bhang': True, 'bhang_reason': "स्त्रीदीर्घ दोष शान्ति विधि",
        'upay': "गुरु बृहस्पति जप 19000, मंगला गौरी व्रत, वैवाहिक दीर्घता मंत्र"
    }


# ============================================================================
# MASTER FUNCTION
# ============================================================================
def dashakoot_milan(boy_data, girl_data, boy_birth=None, girl_birth=None):
    boy_rashi = boy_data['rashi_idx']
    girl_rashi = girl_data['rashi_idx']
    boy_nak = boy_data['nakshatra_idx']
    girl_nak = girl_data['nakshatra_idx']
    
    koots = [
        calc_varna(boy_rashi, girl_rashi),
        calc_vashya(boy_rashi, girl_rashi),
        calc_tara(boy_nak, girl_nak),
        calc_yoni(boy_nak, girl_nak),
        calc_graha_maitri(boy_rashi, girl_rashi),
        calc_gana(boy_nak, girl_nak),
        calc_bhakoot(boy_rashi, girl_rashi),
        calc_naadi(boy_nak, girl_nak, boy_rashi, girl_rashi),
        calc_mahendra(boy_nak, girl_nak),
        calc_stridirgha(boy_nak, girl_nak)
    ]
    
    total = sum(k['score'] for k in koots)
    max_total = sum(k['max'] for k in koots)
    
    # Mangal Dosha CLASSICAL with cancellation
    mangal_analysis = None
    if boy_birth and girl_birth:
        try:
            mangal_analysis = compare_mangal_dosha(boy_birth, girl_birth)
        except Exception as e:
            mangal_analysis = {'error': str(e)}
    
    # Verdict
    if total >= 32:
        v, ven, vc = "Ati Uttam Mel (अति उत्तम मेल)", "Excellent Match", "green"
    elif total >= 26:
        v, ven, vc = "Uttam Mel (उत्तम मेल)", "Very Good Match", "green"
    elif total >= 20:
        v, ven, vc = "Madhyam Mel (मध्यम मेल)", "Average Match", "yellow"
    else:
        v, ven, vc = "Adham Mel (अधम मेल)", "Not Recommended", "red"
    
    # Doshas summary
    doshas = []
    for k in koots:
        if k.get('dosha'):
            doshas.append(k['dosha'])
    if mangal_analysis and mangal_analysis.get('has_dosha'):
        doshas.append(f"Mangal Dosha ({mangal_analysis['status']})")
    
    return {
        'total_score': round(total, 1),
        'max_score': max_total,
        'percentage': round((total / max_total) * 100, 1),
        'verdict': v,
        'verdict_en': ven,
        'verdict_color': vc,
        'koots': koots,
        'mangal_analysis': mangal_analysis,
        'doshas_present': doshas,
        'is_match_recommended': total >= 20 and (not mangal_analysis or mangal_analysis.get('status') != 'GIRL_HIGHER'),
        'summary': f"{total}/{max_total} guna - {v}",
        'guidance': "कम से कम 20 गुण आवश्यक (40 में से)। दोष होने पर भंग जांच आवश्यक।"
    }


def get_rashi_nakshatra_from_birth(birth_date, birth_time, latitude, longitude, timezone=5.5):
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    ut_hour = dt.hour + dt.minute / 60.0 - timezone
    swe.set_ephe_path('/root/jyotish-api/ephe')
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(dt.year, dt.month, dt.day, ut_hour)
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0] % 360
    rashi_idx = int(moon_lon / 30)
    nak_idx = int(moon_lon / (360 / 27))
    return {
        'rashi_idx': rashi_idx, 'rashi_name': RASHI_NAMES[rashi_idx],
        'rashi_hindi': RASHI_HINDI[rashi_idx],
        'nakshatra_idx': nak_idx, 'nakshatra_name': NAKSHATRA_NAMES[nak_idx],
        'moon_longitude': round(moon_lon, 2),
        'pada': int((moon_lon % (360/27)) / (360/108)) + 1
    }
