"""
================================================================================
MARAK & UPAY MODULE
================================================================================
Drop at: /root/jyotish-api/marak_upay.py

Implements Classical Rules from Acharya Harishchandra Purohit:
  1. Graha Peeda - 6/8/12 from dasha swami  
  2. Marakesh detection - 2L/7L from Lagna
  3. Shani drishti - enhances marak bal
  4. Smart Upay - never recommend ratn for 2/6/7/8/12 lords
  5. Forbidden gemstones list

Reference: BPHS + Phalit Jyotish (Acharya Harishchandra Purohit)
================================================================================
"""

from phaladesh_module import PF, RL, PLANET_INDEX, PLANET_HINDI


# ============================================================================
# CLASSICAL CONSTANTS
# ============================================================================

# Bhavas where graha peeda happens (from dasha graha)
PEEDA_BHAVAS_FROM_GRAHA = {6, 8, 12}

# Marak bhavas (from lagna)
MARAK_BHAVAS = {2, 7}

# Forbidden bhava lords (don't suggest ratn for these)
FORBIDDEN_RATN_BHAVAS = {2, 6, 7, 8, 12}

# Allowed bhava lords for upay/ratn
ALLOWED_RATN_BHAVAS = {1, 3, 4, 5, 9, 10, 11}


# ============================================================================
# RATN (GEMSTONE) MAPPING - per graha
# ============================================================================
GRAHA_RATNA = {
    "Sun": {
        "ratna": "Manik (Ruby)", "hindi": "माणिक्य",
        "weight": "3-5 ratti", "metal": "Tamba/Sona (Copper/Gold)",
        "finger": "Anamika (Ring finger)", "day": "Sunday morning",
        "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः"
    },
    "Moon": {
        "ratna": "Moti (Pearl)", "hindi": "मोती",
        "weight": "4-6 ratti", "metal": "Chandi (Silver)",
        "finger": "Kanishtha (Little finger)", "day": "Monday evening",
        "mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः"
    },
    "Mars": {
        "ratna": "Moonga (Coral)", "hindi": "मूंगा",
        "weight": "6-8 ratti", "metal": "Tamba/Sona (Copper/Gold)",
        "finger": "Anamika (Ring finger)", "day": "Tuesday morning",
        "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः"
    },
    "Mercury": {
        "ratna": "Panna (Emerald)", "hindi": "पन्ना",
        "weight": "3-5 ratti", "metal": "Sona (Gold)",
        "finger": "Kanishtha (Little finger)", "day": "Wednesday morning",
        "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः"
    },
    "Jupiter": {
        "ratna": "Pukhraj (Yellow Sapphire)", "hindi": "पुखराज",
        "weight": "5-7 ratti", "metal": "Sona (Gold)",
        "finger": "Tarjani (Index finger)", "day": "Thursday morning",
        "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः"
    },
    "Venus": {
        "ratna": "Heera (Diamond)", "hindi": "हीरा",
        "weight": "0.25-1 ratti", "metal": "Chandi/Platinum",
        "finger": "Madhyama (Middle finger)", "day": "Friday morning",
        "mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः"
    },
    "Saturn": {
        "ratna": "Neelam (Blue Sapphire)", "hindi": "नीलम",
        "weight": "5-7 ratti", "metal": "Loha/Panchdhatu (Iron)",
        "finger": "Madhyama (Middle finger)", "day": "Saturday evening",
        "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः"
    },
    "Rahu": {
        "ratna": "Gomed (Hessonite)", "hindi": "गोमेद",
        "weight": "5-7 ratti", "metal": "Chandi (Silver)",
        "finger": "Madhyama (Middle finger)", "day": "Saturday evening",
        "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः"
    },
    "Ketu": {
        "ratna": "Lehsuniya (Cat's Eye)", "hindi": "लहसुनिया",
        "weight": "5-7 ratti", "metal": "Chandi (Silver)",
        "finger": "Madhyama (Middle finger)", "day": "Saturday evening",
        "mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः"
    },
}


# ============================================================================
# DAAN (DONATION) MAPPING - per graha (always safe to recommend)
# ============================================================================
GRAHA_DAAN = {
    "Sun": ["Gehu (Wheat)", "Gud (Jaggery)", "Tamba (Copper)", "Lal vastra (Red cloth)"],
    "Moon": ["Chawal (Rice)", "Doodh (Milk)", "Chandi (Silver)", "Safed vastra (White cloth)"],
    "Mars": ["Masoor dal", "Lal vastra", "Tamba", "Gud", "Mistri (Sugar)"],
    "Mercury": ["Moong dal", "Hari sabzi (Green vegetables)", "Hara vastra"],
    "Jupiter": ["Chana dal", "Haldi (Turmeric)", "Pita vastra (Yellow cloth)", "Sona"],
    "Venus": ["Chawal", "Mistri", "Safed phool", "Itr (Perfume)", "Ghee"],
    "Saturn": ["Til (Black sesame)", "Sarson tel (Mustard oil)", "Kala vastra", "Loha"],
    "Rahu": ["Til", "Kambal (Blanket)", "Nariyal (Coconut)", "Naga puja"],
    "Ketu": ["Til", "Saptdhan", "Kambal", "Ganesh ji ki puja"]
}


# ============================================================================
# PUJA RECOMMENDATIONS - per graha (always safe)
# ============================================================================
GRAHA_PUJA = {
    "Sun": "Aditya Hridaya Stotra ka path, Surya namaskar, Surya ko arghya",
    "Moon": "Shiv puja, Maha Mrityunjaya jaap, Chandra ko arghya",
    "Mars": "Hanuman Chalisa, Sundar Kand, Mangal stotra",
    "Mercury": "Vishnu sahasranama, Budh stotra, Ganesh puja",
    "Jupiter": "Vishnu sahasranama, Guru stotra, Brihaspati puja, peepal seva",
    "Venus": "Lakshmi stotra, Durga puja, Shukra stotra",
    "Saturn": "Hanuman Chalisa, Shani stotra, Shani Mahatmya",
    "Rahu": "Durga Saptashati, Bhairav puja, Naga puja",
    "Ketu": "Ganesh Atharvashirsha, Ketu stotra, Kalki avatar puja"
}


# ============================================================================
# 1. GRAHA PEEDA DETECTION
# ============================================================================
def detect_graha_peeda(dasha_graha, dasha_rashi, planets_data, lagna_lon):
    """
    Detect which grahas are causing peeda in this dasha.
    
    Rule: Grahas in 6th, 8th, 12th from dasha graha cause peeda.
    
    Args:
        dasha_graha: Mahadasha or Antardasha graha name
        dasha_rashi: Rashi of dasha graha (0-11)
        planets_data: All planets with longitudes
        lagna_lon: Lagna longitude
    
    Returns:
        List of peeda-causing graha details
    """
    peeda_grahas = []
    lagna_rashi = int(lagna_lon / 30) % 12
    
    for graha_name, graha_data in planets_data.items():
        if graha_name == dasha_graha:
            continue
        if not isinstance(graha_data, dict) or "longitude" not in graha_data:
            continue
        
        graha_rashi = int(graha_data["longitude"] / 30) % 12
        
        # Calculate house from dasha graha
        house_from_dasha = ((graha_rashi - dasha_rashi) % 12) + 1
        
        if house_from_dasha in PEEDA_BHAVAS_FROM_GRAHA:
            # Calculate bhava from lagna
            bhava_from_lagna = ((graha_rashi - lagna_rashi) % 12) + 1
            
            peeda_type = {
                6: "Shatru bhav (rog, rin, shatru)",
                8: "Mrityu sthan (vighna, kasht)",
                12: "Vyaya bhav (vyay, haani)"
            }
            
            peeda_grahas.append({
                "graha": graha_name,
                "graha_hindi": PLANET_HINDI.get(graha_name, graha_name),
                "house_from_dasha": house_from_dasha,
                "bhava_from_lagna": bhava_from_lagna,
                "peeda_type": peeda_type[house_from_dasha],
                "intensity": "moderate" if house_from_dasha == 6 else "strong"
            })
    
    return peeda_grahas


# ============================================================================
# 2. MARAKESH DETECTION
# ============================================================================
def detect_marakesh(planets_data, lagna_lon):
    """
    Identify Marakesh grahas (2nd & 7th bhav swamis).
    
    Returns:
        Dict with marakesh info
    """
    lagna_rashi = int(lagna_lon / 30) % 12
    
    # Find 2nd and 7th bhav rashis
    second_rashi = (lagna_rashi + 1) % 12
    seventh_rashi = (lagna_rashi + 6) % 12
    
    second_lord_idx = RL[second_rashi]
    seventh_lord_idx = RL[seventh_rashi]
    
    # Get planet names
    PLANET_BY_INDEX = {0: "Sun", 1: "Moon", 2: "Jupiter", 3: "Mars",
                       4: "Mercury", 5: "Venus", 6: "Saturn"}
    
    second_lord = PLANET_BY_INDEX.get(second_lord_idx)
    seventh_lord = PLANET_BY_INDEX.get(seventh_lord_idx)
    
    return {
        "marakesh_grahas": list({second_lord, seventh_lord} - {None}),
        "second_lord": second_lord,
        "seventh_lord": seventh_lord,
        "second_rashi": second_rashi,
        "seventh_rashi": seventh_rashi,
    }


def is_marakesh(graha_name, marakesh_info):
    """Check if a graha is Marakesh."""
    return graha_name in marakesh_info["marakesh_grahas"]


# ============================================================================
# 3. SHANI DRISHTI ENHANCEMENT
# ============================================================================
def check_shani_drishti_on_marak(planets_data, lagna_lon, marakesh_info):
    """
    Check if Shani has drishti on:
      - 2nd bhav
      - 7th bhav
      - Marakesh grahas
    
    Shani's drishti: 3rd, 7th, 10th from its position
    
    Returns:
        Dict with drishti enhancements
    """
    lagna_rashi = int(lagna_lon / 30) % 12
    
    if "Saturn" not in planets_data:
        return {"shani_drishti_active": False}
    
    saturn_data = planets_data["Saturn"]
    if not isinstance(saturn_data, dict) or "longitude" not in saturn_data:
        return {"shani_drishti_active": False}
    
    saturn_rashi = int(saturn_data["longitude"] / 30) % 12
    
    # Shani's special drishtis: 3rd, 7th, 10th from itself
    shani_aspects = {
        (saturn_rashi + 2) % 12,   # 3rd
        (saturn_rashi + 6) % 12,   # 7th
        (saturn_rashi + 9) % 12,   # 10th
    }
    
    # Check 2nd bhav rashi
    second_rashi = (lagna_rashi + 1) % 12
    seventh_rashi = (lagna_rashi + 6) % 12
    
    drishti_on_2nd = second_rashi in shani_aspects
    drishti_on_7th = seventh_rashi in shani_aspects
    
    # Check drishti on marakesh grahas
    marakesh_with_drishti = []
    for marak_graha in marakesh_info["marakesh_grahas"]:
        if marak_graha in planets_data:
            marak_data = planets_data[marak_graha]
            if isinstance(marak_data, dict) and "longitude" in marak_data:
                marak_rashi = int(marak_data["longitude"] / 30) % 12
                if marak_rashi in shani_aspects:
                    marakesh_with_drishti.append(marak_graha)
    
    has_enhancement = drishti_on_2nd or drishti_on_7th or marakesh_with_drishti
    
    return {
        "shani_drishti_active": has_enhancement,
        "drishti_on_2nd": drishti_on_2nd,
        "drishti_on_7th": drishti_on_7th,
        "marakesh_with_shani_drishti": marakesh_with_drishti,
        "intensity": "prabal" if has_enhancement else "samanya"
    }


# ============================================================================
# 4. MARAK ANALYSIS - Combined check for a dasha graha
# ============================================================================
def analyze_marak_status(dasha_graha, planets_data, lagna_lon):
    """
    Comprehensive marak analysis for a dasha graha.
    
    Returns:
        {
            "is_marakesh": bool,
            "marak_type": "swami_2nd" / "swami_7th" / "both" / null,
            "shani_enhanced": bool,
            "warning_level": "none" / "mild" / "strong" / "severe",
            "warnings": [list of warning strings]
        }
    """
    marakesh_info = detect_marakesh(planets_data, lagna_lon)
    shani_info = check_shani_drishti_on_marak(planets_data, lagna_lon, marakesh_info)
    
    is_marak = is_marakesh(dasha_graha, marakesh_info)
    
    marak_type = None
    if dasha_graha == marakesh_info["second_lord"] and dasha_graha == marakesh_info["seventh_lord"]:
        marak_type = "both"
    elif dasha_graha == marakesh_info["second_lord"]:
        marak_type = "swami_2nd"
    elif dasha_graha == marakesh_info["seventh_lord"]:
        marak_type = "swami_7th"
    
    # Determine warning level
    if not is_marak:
        warning_level = "none"
        warnings = []
    elif is_marak and not shani_info["shani_drishti_active"]:
        warning_level = "mild"
        warnings = [
            f"{dasha_graha} marakesh hai (Lagna se {marak_type.replace('swami_', '')}) - "
            "swasthya, ayu mein samanya savadhani"
        ]
    elif is_marak and shani_info["shani_drishti_active"]:
        warning_level = "strong"
        warnings = [
            f"{dasha_graha} marakesh hai aur Shani ki drishti se MARAK BAL PRABAL hai",
            "Vishesh savadhani aapekshit - swasthya, ayu, accident",
            "Daan, puja, mantra-jaap zaroori"
        ]
        if dasha_graha in shani_info["marakesh_with_shani_drishti"]:
            warning_level = "severe"
            warnings.append("Shani ki dasha graha par seedhi drishti - atyant savdhan rahein")
    else:
        warning_level = "mild"
        warnings = []
    
    return {
        "dasha_graha": dasha_graha,
        "is_marakesh": is_marak,
        "marak_type": marak_type,
        "marakesh_info": marakesh_info,
        "shani_enhancement": shani_info,
        "warning_level": warning_level,
        "warnings": warnings,
    }


# ============================================================================
# 5. SMART UPAY RECOMMENDATIONS
# ============================================================================
def get_graha_lordship(graha_name, lagna_lon):
    """Get bhavas lorded by a graha."""
    if graha_name not in PLANET_INDEX:
        return []
    
    graha_idx = PLANET_INDEX[graha_name]
    if graha_idx > 6:  # Only 7 grahas have lordship
        return []
    
    lagna_rashi = int(lagna_lon / 30) % 12
    lordship = []
    for r in range(12):
        if RL[r] == graha_idx:
            bhava = ((r - lagna_rashi) % 12) + 1
            lordship.append(bhava)
    return lordship


def can_recommend_ratna(graha_name, lagna_lon):
    """
    Check if it's safe to recommend ratn for this graha.
    
    Rule: Don't suggest ratn if graha is lord of 2/6/7/8/12 bhavas.
    
    Returns:
        (allowed: bool, reason: str, lordship: list)
    """
    lordship = get_graha_lordship(graha_name, lagna_lon)
    
    if not lordship:
        # Rahu/Ketu - generally allowed for adhyatmic purposes
        return (True, "Chhaya graha - moksha karak", [])
    
    # Check if any lordship is forbidden
    forbidden_owned = [b for b in lordship if b in FORBIDDEN_RATN_BHAVAS]
    
    if forbidden_owned:
        return (
            False,
            f"{graha_name} {','.join(map(str, forbidden_owned))} bhav ka swami hai - "
            "ratn dharan SHASTROKT NAHI",
            lordship
        )
    
    return (
        True,
        f"{graha_name} {','.join(map(str, lordship))} bhav ka swami hai - ratn dharan shubh",
        lordship
    )


def get_smart_upay(graha_name, lagna_lon, marak_status=None):
    """
    Get safe, smart upay recommendations for a graha.
    
    Returns:
        Dict with daan, puja, mantra (always safe) + ratn (conditional)
    """
    upay = {
        "graha": graha_name,
        "graha_hindi": PLANET_HINDI.get(graha_name, graha_name),
        
        # Always safe
        "daan": GRAHA_DAAN.get(graha_name, []),
        "puja": GRAHA_PUJA.get(graha_name, ""),
        "mantra": GRAHA_RATNA.get(graha_name, {}).get("mantra", ""),
        
        # Conditional
        "ratna_recommendation": None,
        "ratna_warning": None,
    }
    
    # Check if ratn is safe
    can_wear, reason, lordship = can_recommend_ratna(graha_name, lagna_lon)
    
    if can_wear:
        ratna_info = GRAHA_RATNA.get(graha_name)
        if ratna_info:
            upay["ratna_recommendation"] = {
                "allowed": True,
                "reason": reason,
                "lordship": lordship,
                **ratna_info
            }
    else:
        upay["ratna_warning"] = {
            "allowed": False,
            "reason": reason,
            "lordship": lordship,
            "alternative": "Daan, puja, aur mantra-jaap karein - ratn dharan na karein"
        }
    
    # Add marak-specific warning
    if marak_status and marak_status.get("is_marakesh"):
        upay["marak_warning"] = {
            "is_marakesh": True,
            "marak_type": marak_status["marak_type"],
            "warning_level": marak_status["warning_level"],
            "messages": marak_status["warnings"],
            "extra_upay": [
                "Mahamrityunjaya mantra ka jaap",
                "Shiv ling pe jal arpan",
                "Brahmin ko bhojan",
                "Guru se mantra deeksha"
            ]
        }
    
    return upay


# ============================================================================
# 6. MAIN ANALYSIS FUNCTION - For each dasha period
# ============================================================================
def get_complete_dasha_warnings_and_upay(
    dasha_graha,
    planets_data,
    lagna_lon,
):
    """
    Complete marak + upay analysis for a dasha graha.
    
    Use this in Mahadasha and Antardasha endpoints.
    
    Returns comprehensive analysis with warnings and safe upay.
    """
    # Get dasha graha rashi
    if dasha_graha not in planets_data:
        return None
    
    dasha_data = planets_data[dasha_graha]
    if not isinstance(dasha_data, dict) or "longitude" not in dasha_data:
        return None
    
    dasha_rashi = int(dasha_data["longitude"] / 30) % 12
    
    # 1. Graha peeda from 6/8/12
    peeda_grahas = detect_graha_peeda(dasha_graha, dasha_rashi, planets_data, lagna_lon)
    
    # 2. Marak analysis
    marak_status = analyze_marak_status(dasha_graha, planets_data, lagna_lon)
    
    # 3. Smart upay
    upay = get_smart_upay(dasha_graha, lagna_lon, marak_status)
    
    # 4. Generate summary paragraph
    summary = _generate_warning_paragraph(dasha_graha, peeda_grahas, marak_status, upay)
    
    return {
        "dasha_graha": dasha_graha,
        "dasha_graha_hindi": PLANET_HINDI.get(dasha_graha, dasha_graha),
        "peeda_grahas": peeda_grahas,
        "marak_analysis": marak_status,
        "upay": upay,
        "summary_paragraph": summary,
        "overall_warning_level": marak_status["warning_level"],
    }


def _generate_warning_paragraph(dasha_graha, peeda_grahas, marak_status, upay):
    """Generate Hindi summary paragraph."""
    paras = []
    
    # Peeda grahas
    if peeda_grahas:
        peeda_names = [f"{p['graha']} ({p['peeda_type']})" for p in peeda_grahas]
        paras.append(
            f"⚠️ {dasha_graha} ki dasha mein peeda denewale grahas: "
            f"{', '.join(peeda_names)}."
        )
    else:
        paras.append(
            f"✓ {dasha_graha} ke 6/8/12 sthan mein koi grah nahi - peeda nyun."
        )
    
    # Marak status
    if marak_status["is_marakesh"]:
        if marak_status["warning_level"] == "severe":
            paras.append(
                f"🔴 {dasha_graha} marakesh hai aur Shani ki seedhi drishti - "
                f"VISHESH savdhani! Swasthya, ayu, durghatna se bachein."
            )
        elif marak_status["warning_level"] == "strong":
            paras.append(
                f"⚠️ {dasha_graha} marakesh hai + Shani drishti se marak bal prabal - "
                f"savdhani aapekshit."
            )
        else:
            paras.append(
                f"⚠️ {dasha_graha} marakesh hai (lagna se {marak_status['marak_type'].replace('swami_', '')}) - "
                f"samanya savdhani."
            )
    
    # Upay
    if upay["ratna_recommendation"]:
        paras.append(
            f"💎 Ratn: {upay['ratna_recommendation']['ratna']} "
            f"({upay['ratna_recommendation']['hindi']}) - "
            f"shastrokt anukool."
        )
    elif upay["ratna_warning"]:
        paras.append(
            f"❌ Ratn dharan NA karein - {upay['ratna_warning']['reason']}."
        )
    
    # Daan/puja - always safe
    if upay["daan"]:
        paras.append(
            f"✅ Daan: {', '.join(upay['daan'][:3])}. Puja: {upay['puja']}"
        )
    
    return " ".join(paras)
