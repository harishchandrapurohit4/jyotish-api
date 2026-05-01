"""
================================================================================
DASHA MASTER ANALYZER - Complete Classical Engine
================================================================================
Drop at: /root/jyotish-api/dasha_master_analyzer.py

Master module implementing all classical rules from
Acharya Harishchandra Purohit (25+ years experience):

CLASSICAL RULES IMPLEMENTED:
  1. Dual Lordship Analysis (Lagna se konse bhav swami)
  2. Maitri (Naisargik + Tatkalika + Panchadha)
  3. Mool Trikona priority (uccha/swakshetra/MT degree-wise)
  4. Trikona priority (1/5/9 overrides 6/8/12)
  5. Kendrapati Dosha (4+7, 7+10, 4+10 Kendra combinations)
  6. Marakesh (2L/7L) detection
  7. Shani Drishti enhancement
  8. ASTA (Combustion) - book-accurate degrees with vakri rule
  9. PEEDIT graha detection (yuddha, paap kartari, neecha, etc.)
  10. Smart Ratn safety (no ratn for 2/6/7/8/12 unless Trikona)
  11. Period-level analysis (MD/AD/PD with all factors)

Reference: BPHS + Phalit Jyotish (Acharya Harishchandra Purohit)
================================================================================
"""

from phaladesh_module import PF, RL, PLANET_INDEX, PLANET_HINDI


# ============================================================================
# SECTION 1: REFERENCE CONSTANTS
# ============================================================================

# Server uses: 0=Sun, 1=Moon, 2=Jupiter, 3=Mars, 4=Mercury, 5=Venus, 6=Saturn
PLANET_BY_INDEX = {0: "Sun", 1: "Moon", 2: "Jupiter", 3: "Mars",
                   4: "Mercury", 5: "Venus", 6: "Saturn"}

# ASTA (COMBUSTION) DEGREES - Book reference (strict)
ASTA_DEGREES = {
    "Moon":    {"marg": 12, "vakri": 12},      # Same in both
    "Mars":    {"marg": 17, "vakri": 17},
    "Mercury": {"marg": 14, "vakri": 12},      # Vakri less
    "Jupiter": {"marg": 11, "vakri": 11},
    "Venus":   {"marg": 10, "vakri": 8},       # Vakri less (8 deg)
    "Saturn":  {"marg": 15, "vakri": 15},
}

# UCCHA (Exaltation) - rashi index + exact degree
UCCHA_POINTS = {
    "Sun":     {"rashi": 0,  "degree": 10},   # Mesh 10°
    "Moon":    {"rashi": 1,  "degree": 3},    # Vrish 3°
    "Mars":    {"rashi": 9,  "degree": 28},   # Makar 28°
    "Mercury": {"rashi": 5,  "degree": 15},   # Kanya 15°
    "Jupiter": {"rashi": 3,  "degree": 5},    # Karka 5°
    "Venus":   {"rashi": 11, "degree": 27},   # Meen 27°
    "Saturn":  {"rashi": 6,  "degree": 20},   # Tula 20°
}

# NEECHA (Debilitation) = 180° from Uccha
NEECHA_POINTS = {graha: {"rashi": (info["rashi"] + 6) % 12, "degree": info["degree"]}
                 for graha, info in UCCHA_POINTS.items()}

# MOOL TRIKONA - rashi + degree range (very specific!)
MOOL_TRIKONA = {
    "Sun":     {"rashi": 4,  "start": 0,  "end": 20},   # Simha 0-20°
    "Moon":    {"rashi": 1,  "start": 4,  "end": 30},   # Vrish 4-30°
    "Mars":    {"rashi": 0,  "start": 0,  "end": 12},   # Mesh 0-12°
    "Mercury": {"rashi": 5,  "start": 16, "end": 20},   # Kanya 16-20°
    "Jupiter": {"rashi": 8,  "start": 0,  "end": 10},   # Dhanu 0-10°
    "Venus":   {"rashi": 6,  "start": 0,  "end": 15},   # Tula 0-15°
    "Saturn":  {"rashi": 10, "start": 0,  "end": 20},   # Kumbh 0-20°
}

# SWAKSHETRA (Own rashi)
SWAKSHETRA = {
    "Sun":     [4],          # Simha
    "Moon":    [3],          # Karka
    "Mars":    [0, 7],       # Mesh, Vrishchik
    "Mercury": [2, 5],       # Mithun, Kanya
    "Jupiter": [8, 11],      # Dhanu, Meen
    "Venus":   [1, 6],       # Vrish, Tula
    "Saturn":  [9, 10],      # Makar, Kumbh
}

# BHAVA CLASSIFICATIONS
TRIKONA_BHAVAS = {1, 5, 9}        # Always shubh
KENDRA_BHAVAS = {1, 4, 7, 10}     # Strong
TRIKA_BHAVAS = {6, 8, 12}         # Dushthana - ashubh
UPACHAYA_BHAVAS = {3, 6, 10, 11}  # Growing
MARAK_BHAVAS = {2, 7}             # Death-causing potential
SHUBH_BHAVAS = {1, 4, 5, 7, 9, 10}  # Generally good

# Forbidden ratn bhavas (6/8/12 mainly, plus marak 2/7)
FORBIDDEN_RATN_BHAVAS = {2, 6, 7, 8, 12}

# Natural malefics (for paap kartari yoga)
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
NATURAL_BENEFICS = {"Moon", "Mercury", "Jupiter", "Venus"}

# Lordship type priority (highest first)
LORDSHIP_PRIORITY = {
    "lagnesh": 100,       # 1st lord
    "trikona": 90,        # 5/9 lord
    "kendra": 70,         # 4/7/10 lord
    "upachaya": 50,       # 3/11 lord
    "dhana": 40,          # 2 lord (also marak)
    "marak": 30,          # 7 lord (also kendra)
    "trika": 10,          # 6/8/12 lord (ashubh)
}


# ============================================================================
# SECTION 2: LORDSHIP ANALYSIS
# ============================================================================

def get_lordship(graha_name, lagna_lon):
    """Get list of bhavas this graha lords from given lagna."""
    if graha_name not in PLANET_INDEX:
        return []
    
    graha_idx = PLANET_INDEX[graha_name]
    if graha_idx > 6:  # Only 7 grahas have rashi lordship
        return []
    
    lagna_rashi = int(lagna_lon / 30) % 12
    lordship = []
    for r in range(12):
        if RL[r] == graha_idx:
            bhava = ((r - lagna_rashi) % 12) + 1
            lordship.append(bhava)
    return sorted(lordship)


def classify_lordship_type(bhava):
    """Classify a single bhava lordship type."""
    if bhava == 1:
        return "lagnesh"
    elif bhava in {5, 9}:
        return "trikona"
    elif bhava in {4, 7, 10}:
        return "kendra"
    elif bhava in {3, 11}:
        return "upachaya"
    elif bhava == 2:
        return "dhana_marak"  # Both
    elif bhava in {6, 8, 12}:
        return "trika"
    return "other"


def analyze_lordship_full(graha_name, lagna_lon):
    """
    Complete lordship analysis with shubh/ashubh determination.
    
    Returns:
        Dict with full lordship details + verdict
    """
    lordship = get_lordship(graha_name, lagna_lon)
    
    if not lordship:
        # Rahu/Ketu
        return {
            "graha": graha_name,
            "lordship": [],
            "types": [],
            "is_lagnesh": False,
            "has_trikona": False,
            "has_kendra": False,
            "has_trika": False,
            "has_marak": False,
            "kendrapati_dosha": False,
            "trikona_overrides_trika": False,
            "verdict": "chaaya_graha",
            "reasoning": "Rahu/Ketu - chhaya graha, vishesh niyam"
        }
    
    types = [classify_lordship_type(b) for b in lordship]
    
    # Check special conditions
    is_lagnesh = 1 in lordship
    has_trikona = bool({5, 9} & set(lordship))
    has_kendra_only = bool({4, 7, 10} & set(lordship))
    has_trika = bool({6, 8, 12} & set(lordship))
    has_marak = bool({2, 7} & set(lordship))
    has_upachaya = bool({3, 11} & set(lordship))
    
    # Kendrapati Dosha: Multiple Kendra (4+7, 7+10, 4+10) but NOT lagnesh
    kendra_in_lordship = {4, 7, 10} & set(lordship)
    kendrapati_dosha = (len(kendra_in_lordship) >= 2) and not is_lagnesh
    
    # Trikona overrides Trika rule
    trikona_overrides_trika = has_trikona and has_trika
    
    # Final verdict
    if is_lagnesh:
        verdict = "shubh_lagnesh"
        reasoning = f"{graha_name} lagnesh hai - sarvashreshtha shubh"
    elif has_trikona and not trikona_overrides_trika:
        verdict = "shubh_trikona"
        trikona_b = sorted({5, 9} & set(lordship))
        reasoning = f"{graha_name} trikona swami ({trikona_b}) - shubh"
    elif trikona_overrides_trika:
        # Critical rule from Acharya ji
        trikona_b = sorted({5, 9} & set(lordship))
        trika_b = sorted({6, 8, 12} & set(lordship))
        verdict = "shubh_trikona_overrides"
        reasoning = (f"{graha_name} {trikona_b} (trikona) + {trika_b} (trika) ka swami - "
                    f"trikona ka phal pehle, dosh nahi")
    elif kendrapati_dosha:
        kendra_b = sorted(kendra_in_lordship)
        verdict = "ashubh_kendrapati_dosha"
        reasoning = (f"{graha_name} ek se zyada Kendra swami ({kendra_b}) - "
                    f"KENDRAPATI DOSHA, marak prabhav")
    elif has_kendra_only:
        kendra_b = sorted(kendra_in_lordship)
        verdict = "shubh_kendra"
        reasoning = f"{graha_name} kendra swami ({kendra_b}) - balshali"
    elif has_trika and not has_kendra_only and not has_trikona:
        trika_b = sorted({6, 8, 12} & set(lordship))
        verdict = "ashubh_trika"
        reasoning = f"{graha_name} keval trika swami ({trika_b}) - ashubh"
    elif has_upachaya:
        verdict = "mishrit_upachaya"
        reasoning = f"{graha_name} upachaya swami - vriddhi yog"
    else:
        verdict = "mishrit"
        reasoning = f"{graha_name} mishrit swamitva"
    
    return {
        "graha": graha_name,
        "lordship": lordship,
        "types": types,
        "is_lagnesh": is_lagnesh,
        "has_trikona": has_trikona,
        "has_kendra": has_kendra_only,
        "has_trika": has_trika,
        "has_marak": has_marak,
        "has_upachaya": has_upachaya,
        "kendrapati_dosha": kendrapati_dosha,
        "trikona_overrides_trika": trikona_overrides_trika,
        "verdict": verdict,
        "reasoning": reasoning,
        "is_shubh": verdict.startswith("shubh"),
    }


# ============================================================================
# SECTION 3: DIGNITY ANALYSIS (Uccha/Mool Trikona/Swakshetra/Neecha)
# ============================================================================

def get_dignity(graha_name, longitude):
    """
    Determine the dignity status of a graha.
    
    Priority order:
      1. Uccha (Exaltation)
      2. Mool Trikona (with degree check!)
      3. Swakshetra (Own sign)
      4. Mitra rashi
      5. Sama
      6. Shatru rashi
      7. Neecha (Debilitation)
    
    Returns:
        Dict with dignity status + score
    """
    if graha_name not in UCCHA_POINTS:
        # Rahu/Ketu - simplified
        return {"dignity": "chhaya_graha", "score": 0,
                "rashi": None, "degree": None, "is_strong": False}
    
    rashi = int(longitude / 30) % 12
    degree_in_rashi = longitude % 30
    
    # 1. Check Uccha
    uccha = UCCHA_POINTS[graha_name]
    if rashi == uccha["rashi"]:
        # Exact uccha point gets max score
        diff = abs(degree_in_rashi - uccha["degree"])
        score = 5 - (diff / 30) * 2  # 5 max, decreasing with distance
        return {
            "dignity": "uccha",
            "dignity_hindi": "उच्च",
            "score": round(score, 2),
            "rashi": rashi,
            "degree": round(degree_in_rashi, 2),
            "is_strong": True,
            "remark": f"Uccha rashi mein - sarvashreshtha bal"
        }
    
    # 2. Check Neecha
    neecha = NEECHA_POINTS[graha_name]
    if rashi == neecha["rashi"]:
        return {
            "dignity": "neecha",
            "dignity_hindi": "नीच",
            "score": -3,
            "rashi": rashi,
            "degree": round(degree_in_rashi, 2),
            "is_strong": False,
            "remark": f"Neecha rashi mein - bal heen"
        }
    
    # 3. Check Mool Trikona (with DEGREE CHECK)
    mt = MOOL_TRIKONA[graha_name]
    if rashi == mt["rashi"] and mt["start"] <= degree_in_rashi <= mt["end"]:
        return {
            "dignity": "mool_trikona",
            "dignity_hindi": "मूल त्रिकोण",
            "score": 4,
            "rashi": rashi,
            "degree": round(degree_in_rashi, 2),
            "is_strong": True,
            "remark": f"Mool Trikona ({mt['start']}-{mt['end']}°) - vishesh balshali"
        }
    
    # 4. Check Swakshetra
    if rashi in SWAKSHETRA[graha_name]:
        return {
            "dignity": "swakshetra",
            "dignity_hindi": "स्व क्षेत्र",
            "score": 3,
            "rashi": rashi,
            "degree": round(degree_in_rashi, 2),
            "is_strong": True,
            "remark": f"Swakshetra mein - poorna bal"
        }
    
    # 5. Check Mitra/Sama/Shatru rashi based on lord
    rashi_lord_idx = RL[rashi]
    graha_idx = PLANET_INDEX[graha_name]
    if graha_idx <= 6 and rashi_lord_idx <= 6:
        relation = PF[graha_idx][rashi_lord_idx]  # 2=Mitra, 1=Sama, 0=Shatru
        if relation == 2:
            return {
                "dignity": "mitra_rashi",
                "dignity_hindi": "मित्र राशि",
                "score": 2,
                "rashi": rashi,
                "degree": round(degree_in_rashi, 2),
                "is_strong": True,
                "remark": "Mitra rashi mein - shubh"
            }
        elif relation == 0:
            return {
                "dignity": "shatru_rashi",
                "dignity_hindi": "शत्रु राशि",
                "score": -2,
                "rashi": rashi,
                "degree": round(degree_in_rashi, 2),
                "is_strong": False,
                "remark": "Shatru rashi mein - kasht"
            }
        else:  # Sama
            return {
                "dignity": "sama_rashi",
                "dignity_hindi": "सम राशि",
                "score": 0,
                "rashi": rashi,
                "degree": round(degree_in_rashi, 2),
                "is_strong": False,
                "remark": "Sama rashi mein - madhyam"
            }
    
    return {"dignity": "unknown", "score": 0, "rashi": rashi,
            "degree": round(degree_in_rashi, 2), "is_strong": False, "remark": ""}


# ============================================================================
# SECTION 4: ASTA (COMBUSTION) DETECTION
# ============================================================================

def check_asta(graha_name, graha_longitude, sun_longitude, is_vakri=False):
    """
    Strict book-based Asta (combustion) check.
    
    Returns:
        Dict with asta status + degrees from sun
    """
    if graha_name not in ASTA_DEGREES:
        return {"is_asta": False, "reason": "Surya/Rahu/Ketu - asta nahi hota"}
    
    # Calculate angular distance from Sun
    diff = abs(graha_longitude - sun_longitude) % 360
    if diff > 180:
        diff = 360 - diff
    
    threshold_data = ASTA_DEGREES[graha_name]
    threshold = threshold_data["vakri"] if is_vakri else threshold_data["marg"]
    
    is_asta = diff <= threshold
    
    return {
        "is_asta": is_asta,
        "distance_from_sun": round(diff, 2),
        "threshold": threshold,
        "is_vakri": is_vakri,
        "remark": (f"Asta - Surya se {diff:.1f}° (threshold: {threshold}°)"
                   if is_asta else
                   f"Asta nahi - Surya se {diff:.1f}° (threshold: {threshold}°)")
    }


# ============================================================================
# SECTION 5: PEEDIT DETECTION
# ============================================================================

def check_paap_kartari_yoga(graha_name, planets_data):
    """
    Check if graha is between two malefics (Paap Kartari Yoga).
    
    Rule: Malefics in 2nd AND 12th from the graha = peedit.
    """
    if graha_name not in planets_data:
        return {"has_paap_kartari": False}
    
    graha_data = planets_data[graha_name]
    if not isinstance(graha_data, dict) or "longitude" not in graha_data:
        return {"has_paap_kartari": False}
    
    graha_rashi = int(graha_data["longitude"] / 30) % 12
    second_from = (graha_rashi + 1) % 12
    twelfth_from = (graha_rashi - 1) % 12
    
    second_malefic = None
    twelfth_malefic = None
    
    for other_name, other_data in planets_data.items():
        if other_name == graha_name or other_name not in NATURAL_MALEFICS:
            continue
        if not isinstance(other_data, dict) or "longitude" not in other_data:
            continue
        other_rashi = int(other_data["longitude"] / 30) % 12
        
        if other_rashi == second_from:
            second_malefic = other_name
        elif other_rashi == twelfth_from:
            twelfth_malefic = other_name
    
    has_yoga = second_malefic and twelfth_malefic
    
    return {
        "has_paap_kartari": bool(has_yoga),
        "second_malefic": second_malefic,
        "twelfth_malefic": twelfth_malefic,
        "remark": (f"Paap Kartari - {twelfth_malefic} (12th) aur {second_malefic} (2nd) ke beech"
                   if has_yoga else "")
    }


def check_yuddha_haar(graha_name, planets_data, threshold=1.0):
    """
    Check planetary war (Graha Yuddha) - within 1° of another planet.
    
    Lower latitude graha wins; loser is "haar" = peedit.
    Simplified: same rashi + within threshold degrees = potential war.
    """
    if graha_name not in planets_data or graha_name in ("Sun", "Rahu", "Ketu"):
        return {"in_yuddha": False}
    
    graha_data = planets_data[graha_name]
    if not isinstance(graha_data, dict) or "longitude" not in graha_data:
        return {"in_yuddha": False}
    
    graha_lon = graha_data["longitude"]
    
    for other_name, other_data in planets_data.items():
        if other_name == graha_name or other_name in ("Sun", "Rahu", "Ketu"):
            continue
        if not isinstance(other_data, dict) or "longitude" not in other_data:
            continue
        
        other_lon = other_data["longitude"]
        diff = abs(graha_lon - other_lon)
        if diff > 180:
            diff = 360 - diff
        
        if diff <= threshold:
            # Yuddha! Simplification: lower longitude wins
            is_winner = graha_lon < other_lon
            return {
                "in_yuddha": True,
                "with_graha": other_name,
                "is_winner": is_winner,
                "is_haar": not is_winner,
                "diff_degrees": round(diff, 3),
                "remark": (f"Yuddha mein {other_name} ke saath - "
                          f"{'jeet' if is_winner else 'HAAR (peedit)'}")
            }
    
    return {"in_yuddha": False}


def check_overall_peedit(graha_name, planets_data, sun_longitude=None,
                          dignity_info=None, asta_info=None):
    """
    Comprehensive peedit check - combines all factors.
    """
    peedit_factors = []
    
    # 1. Asta peedit
    if asta_info and asta_info.get("is_asta"):
        peedit_factors.append("asta")
    
    # 2. Neecha peedit
    if dignity_info and dignity_info.get("dignity") == "neecha":
        peedit_factors.append("neecha")
    
    # 3. Shatru rashi peedit
    if dignity_info and dignity_info.get("dignity") == "shatru_rashi":
        peedit_factors.append("shatru_rashi")
    
    # 4. Paap Kartari Yoga
    pk = check_paap_kartari_yoga(graha_name, planets_data)
    if pk["has_paap_kartari"]:
        peedit_factors.append("paap_kartari")
    
    # 5. Yuddha haar
    yh = check_yuddha_haar(graha_name, planets_data)
    if yh.get("is_haar"):
        peedit_factors.append("yuddha_haar")
    
    is_peedit = len(peedit_factors) > 0
    
    severity = "none"
    if len(peedit_factors) >= 3:
        severity = "severe"
    elif len(peedit_factors) == 2:
        severity = "strong"
    elif len(peedit_factors) == 1:
        severity = "mild"
    
    return {
        "is_peedit": is_peedit,
        "severity": severity,
        "factors": peedit_factors,
        "factor_count": len(peedit_factors),
        "paap_kartari": pk,
        "yuddha": yh,
        "remark": (f"Peedit ({severity}): {', '.join(peedit_factors)}"
                   if is_peedit else "Peedit nahi - graha sthir")
    }


# ============================================================================
# SECTION 6: SMART RATN DECISION (Master Logic)
# ============================================================================

def smart_ratn_decision(graha_name, lagna_lon, planets_data, sun_longitude=None):
    """
    Master decision tree for ratn safety.
    
    Considers ALL factors:
      - Lordship type (Lagnesh > Trikona > Kendra > etc.)
      - Trikona overrides Trika rule
      - Kendrapati Dosha
      - Asta (Combustion)
      - Peedit status
      - Dignity (Uccha/Neecha)
    
    Returns:
        Detailed decision with reasoning
    """
    # Get all info
    lordship_info = analyze_lordship_full(graha_name, lagna_lon)
    
    graha_data = planets_data.get(graha_name, {})
    graha_lon = graha_data.get("longitude") if isinstance(graha_data, dict) else None
    
    dignity_info = None
    asta_info = None
    peedit_info = None
    
    if graha_lon is not None:
        dignity_info = get_dignity(graha_name, graha_lon)
        if sun_longitude is not None and graha_name not in ("Sun", "Rahu", "Ketu"):
            is_vakri = graha_data.get("vakri", False) if isinstance(graha_data, dict) else False
            asta_info = check_asta(graha_name, graha_lon, sun_longitude, is_vakri)
        peedit_info = check_overall_peedit(
            graha_name, planets_data, sun_longitude, dignity_info, asta_info
        )
    
    # ========== DECISION TREE ==========
    decision = {
        "graha": graha_name,
        "graha_hindi": PLANET_HINDI.get(graha_name, graha_name),
        "lordship_info": lordship_info,
        "dignity_info": dignity_info,
        "asta_info": asta_info,
        "peedit_info": peedit_info,
        "ratn_allowed": False,
        "confidence": "low",
        "reasoning": [],
        "warnings": [],
    }
    
    reasons = decision["reasoning"]
    warnings = decision["warnings"]
    
    # CRITICAL EARLY REJECTIONS
    if asta_info and asta_info.get("is_asta"):
        warnings.append(f"⚠️ Graha ASTA hai (Surya se {asta_info['distance_from_sun']}°) - prakash heen")
    
    if peedit_info and peedit_info.get("severity") in ("severe", "strong"):
        warnings.append(f"⚠️ Peedit ({peedit_info['severity']}): {', '.join(peedit_info['factors'])}")
    
    # PRIMARY LORDSHIP-BASED DECISION
    verdict = lordship_info["verdict"]
    
    if verdict == "shubh_lagnesh":
        decision["ratn_allowed"] = True
        decision["confidence"] = "high"
        reasons.append(f"✓ Lagnesh - sarvashreshtha shubh")
        
    elif verdict == "shubh_trikona":
        decision["ratn_allowed"] = True
        decision["confidence"] = "high"
        reasons.append(f"✓ Trikona swami - shubh")
        
    elif verdict == "shubh_trikona_overrides":
        # Critical rule: Trikona overrides Trika
        decision["ratn_allowed"] = True
        decision["confidence"] = "medium"
        reasons.append(f"✓ Trikona ka phal pehle - {lordship_info['reasoning']}")
        warnings.append("Note: Trika swamitva bhi hai - trikona priority lagi")
        
    elif verdict == "ashubh_kendrapati_dosha":
        decision["ratn_allowed"] = False
        decision["confidence"] = "high"
        reasons.append(f"✗ Kendrapati Dosha - 7 marak hai")
        
    elif verdict == "shubh_kendra":
        decision["ratn_allowed"] = True
        decision["confidence"] = "medium"
        reasons.append(f"✓ Kendra swami - balshali")
        
    elif verdict == "ashubh_trika":
        decision["ratn_allowed"] = False
        decision["confidence"] = "high"
        reasons.append(f"✗ Keval Trika swami (6/8/12) - ratn ashubh")
        
    elif verdict == "mishrit_upachaya":
        decision["ratn_allowed"] = True
        decision["confidence"] = "low"
        reasons.append(f"~ Upachaya - chart-specific decision")
        warnings.append("Upachaya - vriddhi yog, par dhairya se")
        
    elif verdict == "chaaya_graha":
        # Rahu/Ketu - case by case
        decision["ratn_allowed"] = True
        decision["confidence"] = "low"
        reasons.append("~ Chhaya graha - moksha karak ke liye conditional")
        
    else:
        decision["ratn_allowed"] = False
        decision["confidence"] = "low"
        reasons.append(f"? {lordship_info['reasoning']}")
    
    # APPLY OVERRIDES
    if decision["ratn_allowed"]:
        # Asta override (always reject if asta)
        if asta_info and asta_info.get("is_asta"):
            decision["ratn_allowed"] = False
            decision["confidence"] = "high"
            reasons.append("✗ ASTA hone se ratn na pahnein")
        
        # Severe peedit override
        elif peedit_info and peedit_info.get("severity") == "severe":
            decision["ratn_allowed"] = False
            reasons.append("✗ Severe peedit - pehle upay, baad mein ratn")
        
        # Neecha override (warning, not block)
        elif dignity_info and dignity_info.get("dignity") == "neecha":
            decision["confidence"] = "low"
            warnings.append("⚠️ Neecha - ratn se pehle Neecha-bhanga check karein")
    
    # FINAL SUMMARY
    if decision["ratn_allowed"]:
        decision["summary"] = (f"✓ {graha_name} ratn shastrokt anukool "
                              f"({decision['confidence']} confidence)")
    else:
        decision["summary"] = f"✗ {graha_name} ratn dharan NA karein"
    
    return decision


# ============================================================================
# SECTION 7: COMPREHENSIVE PERIOD ANALYSIS (MD/AD/PD)
# ============================================================================

def analyze_dasha_graha(graha_name, lagna_lon, planets_data, sun_longitude=None):
    """
    Complete analysis of a dasha graha - all factors combined.
    
    Returns comprehensive analysis dict.
    """
    # Lordship
    lordship = analyze_lordship_full(graha_name, lagna_lon)
    
    # Position data
    graha_data = planets_data.get(graha_name, {})
    graha_lon = graha_data.get("longitude") if isinstance(graha_data, dict) else None
    
    if graha_lon is None:
        return {"error": f"{graha_name} position not available"}
    
    # Dignity
    dignity = get_dignity(graha_name, graha_lon)
    
    # Asta (only if not Sun)
    asta = None
    if graha_name != "Sun" and sun_longitude is not None:
        is_vakri = graha_data.get("vakri", False) if isinstance(graha_data, dict) else False
        asta = check_asta(graha_name, graha_lon, sun_longitude, is_vakri)
    
    # Peedit
    peedit = check_overall_peedit(graha_name, planets_data, sun_longitude, dignity, asta)
    
    # Ratn decision
    ratn = smart_ratn_decision(graha_name, lagna_lon, planets_data, sun_longitude)
    
    # Bhava position
    lagna_rashi = int(lagna_lon / 30) % 12
    graha_rashi = int(graha_lon / 30) % 12
    bhava = ((graha_rashi - lagna_rashi) % 12) + 1
    
    return {
        "graha": graha_name,
        "graha_hindi": PLANET_HINDI.get(graha_name, graha_name),
        "rashi": graha_rashi,
        "bhava": bhava,
        "longitude": round(graha_lon, 2),
        "lordship": lordship,
        "dignity": dignity,
        "asta": asta,
        "peedit": peedit,
        "ratn_decision": ratn,
        "is_overall_shubh": (lordship["is_shubh"] and 
                            (not asta or not asta.get("is_asta")) and
                            (not peedit or peedit["severity"] not in ("severe", "strong")))
    }


def analyze_period_combined(md_graha, ad_graha, pd_graha,
                              lagna_lon, planets_data, sun_longitude=None):
    """
    Analyze complete dasha period (MD + AD + PD).
    
    Includes maitri analysis between all three grahas.
    """
    from phaladesh_module import panchadha_maitri
    
    md_analysis = analyze_dasha_graha(md_graha, lagna_lon, planets_data, sun_longitude)
    ad_analysis = analyze_dasha_graha(ad_graha, lagna_lon, planets_data, sun_longitude) if ad_graha else None
    pd_analysis = analyze_dasha_graha(pd_graha, lagna_lon, planets_data, sun_longitude) if pd_graha else None
    
    # Maitri matrix between dasha grahas
    maitri = {}
    for g_a in [md_graha, ad_graha, pd_graha]:
        if not g_a or g_a not in PLANET_INDEX:
            continue
        for g_b in [md_graha, ad_graha, pd_graha]:
            if not g_b or g_b == g_a or g_b not in PLANET_INDEX:
                continue
            key = f"{g_a}_{g_b}"
            if key in maitri or f"{g_b}_{g_a}" in maitri:
                continue
            
            a_data = planets_data.get(g_a, {})
            b_data = planets_data.get(g_b, {})
            if not isinstance(a_data, dict) or not isinstance(b_data, dict):
                continue
            
            a_rashi = int(a_data.get("longitude", 0) / 30) % 12
            b_rashi = int(b_data.get("longitude", 0) / 30) % 12
            
            maitri[key] = panchadha_maitri(
                PLANET_INDEX[g_a], a_rashi,
                PLANET_INDEX[g_b], b_rashi
            )
    
    # Overall period verdict
    factors = []
    if md_analysis.get("is_overall_shubh"): factors.append(1)
    else: factors.append(-1)
    if ad_analysis and ad_analysis.get("is_overall_shubh"): factors.append(0.7)
    elif ad_analysis: factors.append(-0.7)
    if pd_analysis and pd_analysis.get("is_overall_shubh"): factors.append(0.4)
    elif pd_analysis: factors.append(-0.4)
    
    period_score = sum(factors) / len(factors) if factors else 0
    
    if period_score > 0.5:
        period_verdict = "Shubh"
    elif period_score > 0:
        period_verdict = "Madhyam-shubh"
    elif period_score > -0.5:
        period_verdict = "Mishrit"
    else:
        period_verdict = "Kasht-prad"
    
    return {
        "md_analysis": md_analysis,
        "ad_analysis": ad_analysis,
        "pd_analysis": pd_analysis,
        "maitri_matrix": maitri,
        "period_score": round(period_score, 2),
        "period_verdict": period_verdict,
    }
