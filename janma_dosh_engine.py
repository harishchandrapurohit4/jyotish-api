"""
Janma Dosh Engine - Birth-Time Doshas
======================================
Phase 1 (THIS SESSION): Gandmool + Mool Nakshatra Dosh - DEEP

References:
- BPHS (Brihat Parashara Hora Shastra) - Adhyay 4 (Nakshatra Vichar)
- Muhurta Chintamani - Gandant Prakaran
- Narad Samhita - Nakshatra Phal

Critical for बच्चे ki kundli - sabse pehle parents yahi poochte hain.
"""

from typing import Dict, List, Optional


# ===========================================
# GANDMOOL NAKSHATRAS (6 total)
# ===========================================
# Yeh 6 nakshatras "sandhi" (junction) par padte hain:
# - Ashwini (1)    : Mesha rashi shuru
# - Ashlesha (9)   : Karka rashi ant
# - Magha (10)     : Simha rashi shuru
# - Jyeshtha (18)  : Vrishchik rashi ant
# - Mool (19)      : Dhanu rashi shuru
# - Revati (27)    : Meena rashi ant

GANDMOOL_NAKSHATRAS = {
    1: {  # Ashwini
        "name": "Ashwini",
        "name_hindi": "अश्विनी",
        "lord": "Ketu",
        "rashi_position": "Mesha rashi ka aarambh",
        "type": "Adi-Gand",  # Beginning gand
        "severity": "medium",
        "deity": "Ashwini Kumar",
    },
    9: {  # Ashlesha
        "name": "Ashlesha",
        "name_hindi": "आश्लेषा",
        "lord": "Mercury",
        "rashi_position": "Karka rashi ka ant",
        "type": "Anta-Gand",  # End gand
        "severity": "high",
        "deity": "Sarp (Naag)",
    },
    10: {  # Magha
        "name": "Magha",
        "name_hindi": "मघा",
        "lord": "Ketu",
        "rashi_position": "Simha rashi ka aarambh",
        "type": "Adi-Gand",
        "severity": "medium",
        "deity": "Pitr",
    },
    18: {  # Jyeshtha
        "name": "Jyeshtha",
        "name_hindi": "ज्येष्ठा",
        "lord": "Mercury",
        "rashi_position": "Vrishchik rashi ka ant",
        "type": "Anta-Gand",
        "severity": "high",
        "deity": "Indra",
    },
    19: {  # Mool - SABSE IMPORTANT
        "name": "Mool",
        "name_hindi": "मूल",
        "lord": "Ketu",
        "rashi_position": "Dhanu rashi ka aarambh",
        "type": "Adi-Gand",
        "severity": "very_high",  # Highest severity for Mool
        "deity": "Nirriti (Rakshas)",
    },
    27: {  # Revati
        "name": "Revati",
        "name_hindi": "रेवती",
        "lord": "Mercury",
        "rashi_position": "Meena rashi ka ant",
        "type": "Anta-Gand",
        "severity": "medium",
        "deity": "Pushan",
    },
}


# ===========================================
# MOOL NAKSHATRA - CHARAN-WISE EFFECTS (BPHS)
# ===========================================
# Mool ke 4 charans, har charan ka alag phal:
# Reference: Muhurta Chintamani 2.7

MOOL_CHARAN_EFFECTS = {
    1: {
        "charan": 1,
        "severity": "very_high",
        "affects": "Pita (Father)",
        "phal_hindi": "मूल नक्षत्र के प्रथम चरण में जन्मे बालक से पिता को अत्यंत कष्ट होता है। पिता के स्वास्थ्य, धन तथा प्रतिष्ठा पर प्रभाव पड़ता है।",
        "phal_english": "Birth in 1st charan of Mool causes severe affliction to father - health, wealth, and reputation affected.",
        "shlok": "मूले मूलं विनाशाय",  # "Mool destroys the root (father)"
        "shlok_meaning": "मूल नक्षत्र मूल (पिता/वंश) का नाश करता है",
        "shanti_essential": True,
    },
    2: {
        "charan": 2,
        "severity": "high",
        "affects": "Mata (Mother)",
        "phal_hindi": "द्वितीय चरण में जन्म से माता को कष्ट तथा आर्थिक हानि का योग बनता है।",
        "phal_english": "Birth in 2nd charan affects mother's health and causes financial losses.",
        "shlok": "द्वितीये मातृनाशाय",
        "shlok_meaning": "दूसरा चरण माता के लिए कष्टकारी",
        "shanti_essential": True,
    },
    3: {
        "charan": 3,
        "severity": "medium",
        "affects": "Dhan-Sampatti (Wealth)",
        "phal_hindi": "तृतीय चरण में जन्मे जातक को धन सम्पत्ति की हानि एवं कुटुम्ब में अशांति का सामना करना पड़ता है।",
        "phal_english": "Birth in 3rd charan brings wealth loss and family discord.",
        "shlok": "तृतीये धननाशाय",
        "shlok_meaning": "तीसरा चरण धन हानिकारक",
        "shanti_essential": True,
    },
    4: {
        "charan": 4,
        "severity": "low",  # Sabse कम severity
        "affects": "Self (Mild)",
        "phal_hindi": "चतुर्थ चरण शुभ माना गया है। जातक स्वयं तेजस्वी, बुद्धिमान तथा भाग्यशाली होता है। केवल सामान्य शान्ति कर्म पर्याप्त है।",
        "phal_english": "4th charan is considered auspicious - native is brilliant, wise, and fortunate. Only basic shanti needed.",
        "shlok": "चतुर्थे शुभदं भवेत्",
        "shlok_meaning": "चौथा चरण शुभ फलदायक",
        "shanti_essential": False,  # Optional only
    },
}


# ===========================================
# OTHER GANDMOOL CHARAN EFFECTS
# ===========================================

GANDMOOL_GENERAL_EFFECTS = {
    "Ashwini": {
        1: {"affects": "Self - mild", "severity": "low"},
        2: {"affects": "Mama (Maternal Uncle)", "severity": "medium"},
        3: {"affects": "Family", "severity": "medium"},
        4: {"affects": "Auspicious", "severity": "low"},
    },
    "Ashlesha": {
        1: {"affects": "Self/Mata", "severity": "high"},
        2: {"affects": "Sasur (Father-in-law)", "severity": "high"},
        3: {"affects": "Saas (Mother-in-law)", "severity": "very_high"},  # Worst
        4: {"affects": "Wealth", "severity": "high"},
    },
    "Magha": {
        1: {"affects": "Mata", "severity": "very_high"},  # Worst
        2: {"affects": "Pita", "severity": "high"},
        3: {"affects": "Family wealth", "severity": "medium"},
        4: {"affects": "Auspicious", "severity": "low"},
    },
    "Jyeshtha": {
        1: {"affects": "Bade Bhai (Elder Brother)", "severity": "high"},
        2: {"affects": "Choti Behen (Younger Sister)", "severity": "medium"},
        3: {"affects": "Mama", "severity": "high"},
        4: {"affects": "Self", "severity": "very_high"},  # Worst
    },
    "Revati": {
        1: {"affects": "Auspicious", "severity": "low"},
        2: {"affects": "Self", "severity": "medium"},
        3: {"affects": "Family", "severity": "medium"},
        4: {"affects": "Pita", "severity": "very_high"},  # Worst
    },
}


# ===========================================
# SHANTI VIDHI DETAILS
# ===========================================

GANDMOOL_SHANTI_VIDHI = {
    "when": "27वें दिन (27th day after birth) jab wahi nakshatra dobara aaye",
    "alternate_when": "Yadi 27th day possible nahi to phir kabhi bhi same nakshatra par",
    "duration": "1 din ki vidhi",
    "place": "Ghar mein ya kisi tirth sthal par",
    "essential_items": [
        "Kalash (108 chhid wala) - tambe ka",
        "Saptamrit (gangajal, milk, dahi, ghee, honey, sugar, water)",
        "Panchgavya",
        "Brahman bhojan (minimum 5 brahman)",
        "Daan items: Til, vastra, swarn, gau-daan",
    ],
    "main_mantra": {
        "for_mool": "ॐ निर्ऋतये नमः - 108 baar (Mool ki devi Nirriti)",
        "for_ashlesha_jyeshtha": "ॐ सर्पाय नमः / ॐ ऐन्द्राय नमः",
        "for_ashwini_revati": "ॐ अश्विनीकुमाराभ्यां नमः",
        "for_magha": "ॐ पितृभ्यो नमः",
    },
    "main_puja": "Gandmool/Mool Shanti Yagna",
    "havan_samidha": "Palash (for Mool), Dhak ki samidha",
    "ahuti_count": 108,
    "father_restriction": "Pita ko 27 din tak bachche ka mukh nahi dekhna chahiye (especially for Mool 1st charan)",
    "post_shanti": "Shanti ke baad pita darshan kar sakte hain",
}


# ===========================================
# DETECTION FUNCTIONS
# ===========================================

def detect_gandmool_dosh(nakshatra_number: int, charan: int) -> Optional[Dict]:
    """
    Detect Gandmool dosh from janma nakshatra.
    
    Args:
        nakshatra_number: 1-27 (Ashwini=1, Revati=27)
        charan: 1-4
    
    Returns:
        Dosh dict if Gandmool, else None
    """
    if nakshatra_number not in GANDMOOL_NAKSHATRAS:
        return None
    
    nak_info = GANDMOOL_NAKSHATRAS[nakshatra_number]
    nak_name = nak_info["name"]
    
    # Mool ka special handling - separate function
    if nak_name == "Mool":
        return None  # Will be handled by detect_mool_dosh
    
    charan_info = GANDMOOL_GENERAL_EFFECTS.get(nak_name, {}).get(charan, {})
    
    return {
        "dosh_name": "Gandmool Nakshatra Dosh",
        "dosh_name_hindi": "गंडमूल नक्षत्र दोष",
        "is_present": True,
        "nakshatra": nak_name,
        "nakshatra_hindi": nak_info["name_hindi"],
        "charan": charan,
        "type": nak_info["type"],
        "severity": charan_info.get("severity", nak_info["severity"]),
        "affects": charan_info.get("affects", "General family"),
        "deity": nak_info["deity"],
        "lord": nak_info["lord"],
        "phal_hindi": _get_gandmool_phal(nak_name, charan),
        "shanti_required": True,
        "shanti_vidhi": GANDMOOL_SHANTI_VIDHI,
        "is_mool": False,
    }


def detect_mool_dosh(nakshatra_number: int, charan: int) -> Optional[Dict]:
    """
    Detect specifically Mool Nakshatra Dosh - HIGHEST priority.
    
    Args:
        nakshatra_number: should be 19 for Mool
        charan: 1-4
    
    Returns:
        Detailed Mool dosh dict
    """
    if nakshatra_number != 19:
        return None
    
    charan_data = MOOL_CHARAN_EFFECTS.get(charan)
    if not charan_data:
        return None
    
    return {
        "dosh_name": "Mool Nakshatra Dosh",
        "dosh_name_hindi": "मूल नक्षत्र दोष",
        "is_present": True,
        "is_mool": True,
        "nakshatra": "Mool",
        "nakshatra_hindi": "मूल",
        "charan": charan,
        "severity": charan_data["severity"],
        "affects": charan_data["affects"],
        "deity": "Nirriti (निर्ऋति)",
        "lord": "Ketu",
        "type": "Adi-Gand (most severe)",
        "phal_hindi": charan_data["phal_hindi"],
        "phal_english": charan_data["phal_english"],
        "shlok": charan_data["shlok"],
        "shlok_meaning": charan_data["shlok_meaning"],
        "shanti_required": charan_data["shanti_essential"],
        "shanti_vidhi": GANDMOOL_SHANTI_VIDHI,
        "warning": "मूल नक्षत्र का प्रथम चरण सर्वाधिक कष्टकारी है - तत्काल शान्ति आवश्यक",
        "special_remedies": [
            "27वें दिन Mool Shanti Yagna",
            "Palash ki samidha se havan",
            "Nirriti devi mantra: ॐ निर्ऋतये नमः - 108 baar",
            "Til, vastra, swarn daan",
            "Pita 27 din tak darshan na kare (1st charan only)",
            "Nakshatra-suchak ratna dharan: Cat's Eye (Ketu ratna)",
        ],
    }


def _get_gandmool_phal(nakshatra_name: str, charan: int) -> str:
    """Generate phal description in Hindi"""
    charan_info = GANDMOOL_GENERAL_EFFECTS.get(nakshatra_name, {}).get(charan, {})
    affects = charan_info.get("affects", "general")
    severity = charan_info.get("severity", "medium")
    
    severity_text = {
        "very_high": "अत्यधिक कष्टकारी",
        "high": "कष्टकारी",
        "medium": "मध्यम प्रभाव",
        "low": "अल्प/शुभ प्रभाव",
    }.get(severity, "मध्यम")
    
    return (
        f"{nakshatra_name} नक्षत्र के {charan} चरण में जन्म होने से {affects} पर "
        f"{severity_text} प्रभाव पड़ता है। 27वें दिन गंडमूल शान्ति विधि अवश्य करवायें।"
    )


def detect_all_janma_doshas(birth_data: Dict) -> Dict:
    """
    Master function - detects all janma doshas.
    Currently implements: Gandmool + Mool
    
    Args:
        birth_data: {
            "nakshatra_number": 1-27,
            "charan": 1-4,
            ... other birth data
        }
    
    Returns:
        Complete dosh analysis
    """
    nak_num = birth_data.get("nakshatra_number")
    charan = birth_data.get("charan", 1)
    
    result = {
        "total_doshas_found": 0,
        "highest_severity": "none",
        "doshas": [],
        "shanti_required": False,
    }
    
    # Check Mool first (highest priority)
    mool = detect_mool_dosh(nak_num, charan)
    if mool:
        result["doshas"].append(mool)
        result["total_doshas_found"] += 1
        result["highest_severity"] = mool["severity"]
        result["shanti_required"] = mool["shanti_required"]
    else:
        # Check other Gandmool
        gandmool = detect_gandmool_dosh(nak_num, charan)
        if gandmool:
            result["doshas"].append(gandmool)
            result["total_doshas_found"] += 1
            result["highest_severity"] = gandmool["severity"]
            result["shanti_required"] = True
    
    return result
