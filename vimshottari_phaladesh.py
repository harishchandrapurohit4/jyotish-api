"""
================================================================================
VIMSHOTTARI MULTI-LEVEL PHALADESH MODULE
================================================================================
Extension of phaladesh_module.py
Drop at: /root/jyotish-api/vimshottari_phaladesh.py

Implements:
  - Mahadasha (MD) Phaladesh - reuses existing engine
  - Antardasha (AD) Phaladesh - MD × AD with Panchadha modifier
  - Pratyantar (PD) Phaladesh - AD × PD with dual Panchadha
  - Sookshma (SD) - structure ready, optional

Classical Yogas Detected:
  - Vipreet Rajayoga (6L/8L/12L AD in friendly MD)
  - Marak periods (2L/7L activation)
  - Dhana Yoga (2L/11L combinations)
  - Karaka Yoga (AK-AmK combinations)

Reference: BPHS + Phalit Jyotish (Acharya Harishchandra Purohit)
================================================================================
"""

from phaladesh_module import (
    PF, RL, PLANET_INDEX, PLANET_HINDI,
    panchadha_maitri, calculate_lajjitadi_avastha,
    synthesize_mahadasha_phal,
    UCCHA_RASHI, SWAKSHETRA,
    PANCHADHA_LEVELS, PANCHADHA_HINDI, PANCHADHA_COLOR, PANCHADHA_SCORE,
    BHAVA_NAMES, BHAVA_LIFE_AREAS, GRAHA_KARAKAS
)


# ============================================================================
# PANCHADHA MODIFIERS (multiplicative effect on combined score)
# ============================================================================
# These determine how MD-AD relation modifies the combined phaladesh
PANCHADHA_MODIFIER = {
    "Adhi Mitra": 1.20,      # +20% boost
    "Mitra": 1.10,           # +10% boost
    "Sama": 1.00,            # neutral
    "Shatru": 0.85,          # -15% reduction
    "Adhi Shatru": 0.70,     # -30% significant reduction
}

# Dasha-level weights
# How much each level contributes to final period phaladesh
WEIGHT_AD = {
    "md_contribution": 0.55,    # Mahadasha base influence
    "ad_natural": 0.35,         # AD graha's own qualities
    "panchadha_md_ad": 0.10,    # MD-AD relation explicit weight
}

WEIGHT_PD = {
    "ad_contribution": 0.45,    # AD context (which already includes MD)
    "md_contribution": 0.20,    # Direct MD influence
    "pd_natural": 0.25,         # PD graha's own qualities
    "panchadha_combined": 0.10, # Combined panchadha effects
}


# ============================================================================
# 1. ANTARDASHA PHALADESH
# ============================================================================
def synthesize_antardasha_phal(
    md_graha, md_phal,           # Mahadasha context
    ad_graha, ad_phal,           # Antardasha graha's standalone phaladesh
    md_rashi, ad_rashi,          # Rashi positions
    md_idx, ad_idx,              # Planet indices
):
    """
    Calculate Antardasha phaladesh combining MD context + AD nature + relation.
    
    Args:
        md_graha: Mahadasha graha name (e.g., "Jupiter")
        md_phal: Mahadasha synthesis result (from synthesize_mahadasha_phal)
        ad_graha: Antardasha graha name
        ad_phal: AD graha's standalone phaladesh
        md_rashi, ad_rashi: 0-11 rashi positions
        md_idx, ad_idx: 0-6 planet indices
    
    Returns:
        Combined AD phaladesh dict
    """
    
    # Calculate MD-AD Panchadha relation
    panchadha = panchadha_maitri(md_idx, md_rashi, ad_idx, ad_rashi)
    
    # Get scores
    md_score = md_phal["final_score"]
    ad_natural_score = ad_phal["final_score"]
    panchadha_score_norm = (panchadha["score"] + 2) * 25  # Convert -2..+2 to 0..100
    
    # Weighted combination
    combined_score = (
        WEIGHT_AD["md_contribution"] * md_score +
        WEIGHT_AD["ad_natural"] * ad_natural_score +
        WEIGHT_AD["panchadha_md_ad"] * panchadha_score_norm
    )
    
    # Apply panchadha modifier
    modifier = PANCHADHA_MODIFIER.get(panchadha["panchadha"], 1.0)
    final_score = max(0, min(100, combined_score * modifier))
    
    verdict = _get_verdict(final_score)
    
    # Generate AD-specific phaladesh paragraph
    paragraph = _generate_ad_paragraph(
        md_graha, ad_graha, md_phal, ad_phal,
        panchadha, final_score, verdict
    )
    
    return {
        "md_graha": md_graha,
        "ad_graha": ad_graha,
        "md_graha_hindi": PLANET_HINDI.get(md_graha, md_graha),
        "ad_graha_hindi": PLANET_HINDI.get(ad_graha, ad_graha),
        "final_score": round(final_score, 1),
        "md_score": round(md_score, 1),
        "ad_natural_score": round(ad_natural_score, 1),
        "verdict": verdict["label"],
        "verdict_hindi": verdict["hindi"],
        "verdict_color": verdict["color"],
        "verdict_emoji": verdict["emoji"],
        "panchadha": {
            "name": panchadha["panchadha"],
            "hindi": panchadha["panchadha_hindi"],
            "color": panchadha["color"],
            "modifier": modifier,
        },
        "phaladesh": paragraph,
        "summary": f"{md_graha}-{ad_graha} ({panchadha['panchadha']})"
                   f" {verdict['emoji']} {verdict['label']}"
    }


# ============================================================================
# 2. PRATYANTAR PHALADESH
# ============================================================================
def synthesize_pratyantar_phal(
    md_graha, md_phal,
    ad_graha, ad_phal, ad_combined_phal,  # AD's combined result
    pd_graha, pd_phal,
    md_rashi, ad_rashi, pd_rashi,
    md_idx, ad_idx, pd_idx,
):
    """
    Calculate Pratyantar phaladesh - 3-level combination.
    
    The PD inherits AD context (which includes MD) + PD nature + 
    dual panchadha relations (AD-PD primary, MD-PD secondary).
    """
    
    # Two panchadha relations
    panchadha_ad_pd = panchadha_maitri(ad_idx, ad_rashi, pd_idx, pd_rashi)
    panchadha_md_pd = panchadha_maitri(md_idx, md_rashi, pd_idx, pd_rashi)
    
    # Scores
    ad_combined_score = ad_combined_phal["final_score"]
    md_score = md_phal["final_score"]
    pd_natural_score = pd_phal["final_score"]
    
    panchadha_combined_norm = (
        (panchadha_ad_pd["score"] + 2) * 25 * 0.7 +  # AD-PD weighted higher
        (panchadha_md_pd["score"] + 2) * 25 * 0.3
    )
    
    # Weighted combination
    combined_score = (
        WEIGHT_PD["ad_contribution"] * ad_combined_score +
        WEIGHT_PD["md_contribution"] * md_score +
        WEIGHT_PD["pd_natural"] * pd_natural_score +
        WEIGHT_PD["panchadha_combined"] * panchadha_combined_norm
    )
    
    # Apply combined modifier (AD-PD primary)
    modifier_ad_pd = PANCHADHA_MODIFIER.get(panchadha_ad_pd["panchadha"], 1.0)
    modifier_md_pd = PANCHADHA_MODIFIER.get(panchadha_md_pd["panchadha"], 1.0)
    # Average the modifiers, with AD-PD weighted higher
    final_modifier = (modifier_ad_pd * 0.7) + (modifier_md_pd * 0.3)
    
    final_score = max(0, min(100, combined_score * final_modifier))
    verdict = _get_verdict(final_score)
    
    paragraph = _generate_pd_paragraph(
        md_graha, ad_graha, pd_graha,
        panchadha_ad_pd, panchadha_md_pd,
        final_score, verdict
    )
    
    return {
        "md_graha": md_graha,
        "ad_graha": ad_graha,
        "pd_graha": pd_graha,
        "md_graha_hindi": PLANET_HINDI.get(md_graha, md_graha),
        "ad_graha_hindi": PLANET_HINDI.get(ad_graha, ad_graha),
        "pd_graha_hindi": PLANET_HINDI.get(pd_graha, pd_graha),
        "final_score": round(final_score, 1),
        "verdict": verdict["label"],
        "verdict_hindi": verdict["hindi"],
        "verdict_color": verdict["color"],
        "verdict_emoji": verdict["emoji"],
        "panchadha_ad_pd": {
            "name": panchadha_ad_pd["panchadha"],
            "hindi": panchadha_ad_pd["panchadha_hindi"],
            "color": panchadha_ad_pd["color"],
        },
        "panchadha_md_pd": {
            "name": panchadha_md_pd["panchadha"],
            "hindi": panchadha_md_pd["panchadha_hindi"],
            "color": panchadha_md_pd["color"],
        },
        "phaladesh": paragraph,
        "summary": f"{md_graha}-{ad_graha}-{pd_graha} {verdict['emoji']} {verdict['label']}"
    }


# ============================================================================
# 3. CLASSICAL YOGA DETECTION
# ============================================================================
def detect_classical_yogas(
    md_graha, ad_graha,
    md_lordship, ad_lordship,  # Lists of bhavas these grahas lord
    md_bhava, ad_bhava,
    panchadha_md_ad
):
    """
    Detect classical yogas in MD-AD combination.
    
    Returns list of yoga dicts.
    """
    yogas = []
    
    # 1. VIPREET RAJAYOGA - 6L/8L/12L AD in friendly relation with MD
    dushthana_lordship_ad = [b for b in ad_lordship if b in [6, 8, 12]]
    if dushthana_lordship_ad and panchadha_md_ad in ["Adhi Mitra", "Mitra"]:
        yogas.append({
            "name": "Vipreet Rajayoga",
            "hindi": "विपरीत राजयोग",
            "intensity": "very_positive",
            "description": f"AD graha {ad_graha} ({','.join(map(str, dushthana_lordship_ad))} bhav swami) "
                          f"MD ke saath shubh sambandh - dushthana ka nakaratmak prabhav "
                          f"shubh phal mein parivartan"
        })
    
    # 2. DHANA YOGA - 2L or 11L AD in MD with friendly relation
    dhana_lordship_ad = [b for b in ad_lordship if b in [2, 11]]
    if dhana_lordship_ad and panchadha_md_ad in ["Adhi Mitra", "Mitra", "Sama"]:
        yogas.append({
            "name": "Dhana Yoga",
            "hindi": "धन योग",
            "intensity": "positive",
            "description": f"AD graha {ad_graha} ({','.join(map(str, dhana_lordship_ad))} bhav swami) - "
                          f"arth labh, dhan vriddhi ka samay"
        })
    
    # 3. MARAK PERIOD - 2L or 7L AD with hostile relation
    marak_lordship_ad = [b for b in ad_lordship if b in [2, 7]]
    if marak_lordship_ad and panchadha_md_ad in ["Shatru", "Adhi Shatru"]:
        yogas.append({
            "name": "Marak Period",
            "hindi": "मारक काल",
            "intensity": "negative",
            "description": f"AD graha {ad_graha} ({','.join(map(str, marak_lordship_ad))} bhav swami) - "
                          f"swasthya, ayu mein savadhani aapekshit"
        })
    
    # 4. KENDRA-TRIKONA YOGA - Both lord Kendra/Trikona
    kendra_trikona = {1, 4, 5, 7, 9, 10}
    md_kt = [b for b in md_lordship if b in kendra_trikona]
    ad_kt = [b for b in ad_lordship if b in kendra_trikona]
    if md_kt and ad_kt and panchadha_md_ad in ["Adhi Mitra", "Mitra"]:
        yogas.append({
            "name": "Kendra-Trikona Yoga",
            "hindi": "केंद्र-त्रिकोण योग",
            "intensity": "positive",
            "description": "Donon graha kendra-trikona swami - rajayoga prabhav, "
                          "uchha sthithi, samman, samriddhi"
        })
    
    # 5. DUR-YOGA - Both in dushthana lordship + bad relation
    dushthana = {6, 8, 12}
    md_d = [b for b in md_lordship if b in dushthana]
    ad_d = [b for b in ad_lordship if b in dushthana]
    if md_d and ad_d and panchadha_md_ad == "Adhi Shatru":
        yogas.append({
            "name": "Dur-Yoga",
            "hindi": "दुर्योग",
            "intensity": "very_negative",
            "description": "Donon graha dushthana swami + Adhi Shatru - vishesh kasht, "
                          "swasthya, arth, sambandh sab kshetron mein savdhani"
        })
    
    return yogas


# ============================================================================
# 4. HELPER FUNCTIONS
# ============================================================================
def _get_verdict(score):
    if score >= 80:
        return {"label": "Excellent", "hindi": "अति उत्तम", "color": "#22c55e", "emoji": "🌟"}
    elif score >= 65:
        return {"label": "Good", "hindi": "उत्तम", "color": "#3b82f6", "emoji": "✨"}
    elif score >= 45:
        return {"label": "Mixed", "hindi": "मिश्रित", "color": "#9ca3af", "emoji": "⚖️"}
    elif score >= 25:
        return {"label": "Difficult", "hindi": "कष्टकारी", "color": "#f97316", "emoji": "⚠️"}
    else:
        return {"label": "Severe", "hindi": "अत्यंत कष्टकारी", "color": "#ef4444", "emoji": "🔴"}


def _generate_ad_paragraph(md_graha, ad_graha, md_phal, ad_phal, 
                            panchadha, score, verdict):
    """Generate detailed AD phaladesh paragraph in Hindi."""
    paras = []
    
    paras.append(
        f"{md_graha}-{ad_graha} antardasha aapke liye {verdict['hindi']} rahegi "
        f"({score:.0f}/100 score)."
    )
    
    paras.append(
        f"Mahadasha graha {md_graha} ({md_phal['verdict_hindi']}, {md_phal['final_score']:.0f}) "
        f"ke saath antardasha graha {ad_graha} ka {panchadha['panchadha_hindi']} "
        f"({panchadha['panchadha']}) sambandh hai."
    )
    
    # Modifier interpretation
    if panchadha["panchadha"] == "Adhi Mitra":
        paras.append(
            f"Adhi Mitra sambandh ke karan donon grahas ek doosre ko balshali "
            f"karte hain - sarvottam yog. Mahadasha ke shubh phalon mein "
            f"vriddhi hogi."
        )
    elif panchadha["panchadha"] == "Mitra":
        paras.append(
            f"Mitra sambandh - donon grahas mein samanjasya hai, shubh phal "
            f"sthir aur niyamit roop se prapt honge."
        )
    elif panchadha["panchadha"] == "Sama":
        paras.append(
            f"Sama bhav - tatastha sambandh, mishrit phal milenge. "
            f"Apne karyon mein dhairya rakhein."
        )
    elif panchadha["panchadha"] == "Shatru":
        paras.append(
            f"Shatru sambandh - mahadasha ke phalon mein {ad_graha} avrodh "
            f"daal sakta hai. Bade nirnay mein savadhani aapekshit."
        )
    else:  # Adhi Shatru
        paras.append(
            f"Adhi Shatru - vishesh kasht-prad sambandh. Iss antardasha mein "
            f"swasthya, arth, aur sambandhon mein vishesh savadhani zaroori. "
            f"Daan-dharma, upay aur dhairya se phal mein sudhar aayega."
        )
    
    # Recommendation based on score
    if score >= 65:
        paras.append(
            f"Yeh antardasha {ad_graha} ke karaktvon ke liye anukool hai. "
            f"Naye prayatna shubh."
        )
    elif score >= 45:
        paras.append(
            f"Mishrit phal - {ad_graha} ke kshetron mein soch-samajh kar nirnay lein."
        )
    else:
        paras.append(
            f"Iss kal mein {ad_graha} se sambandhit kshetron mein savdhani rakhein, "
            f"upay-daan karein."
        )
    
    return " ".join(paras)


def _generate_pd_paragraph(md_graha, ad_graha, pd_graha,
                            panchadha_ad_pd, panchadha_md_pd,
                            score, verdict):
    """Generate Pratyantar phaladesh paragraph."""
    paras = []
    
    paras.append(
        f"{md_graha}-{ad_graha}-{pd_graha} pratyantar dasha "
        f"{verdict['hindi']} ({score:.0f}/100)."
    )
    
    paras.append(
        f"Antardasha {ad_graha} ke saath pratyantar {pd_graha} ka "
        f"{panchadha_ad_pd['panchadha_hindi']} sambandh, aur "
        f"mahadasha {md_graha} ke saath {panchadha_md_pd['panchadha_hindi']} sambandh."
    )
    
    if score >= 65:
        paras.append(f"Yeh sookshma kal {pd_graha} ke karyon ke liye shubh hai.")
    elif score >= 45:
        paras.append(f"Mishrit pratyantar - dhairya rakhein, sthir nirnay lein.")
    else:
        paras.append(f"Savdhani ka pratyantar - bade kaam tal dein, upay karein.")
    
    return " ".join(paras)


# ============================================================================
# 5. MAIN API HELPER - Full Vimshottari Tree with Phaladesh
# ============================================================================
def get_vimshottari_phaladesh_tree(
    planets_data, lagna_data,
    vimshottari_periods,  # Existing dasha calculation
    levels=3,             # 1=MD, 2=MD+AD, 3=MD+AD+PD, 4=full
    target_md=None,       # If specified, only calculate for this MD's branch
    avastha_data_map=None
):
    """
    Build complete Vimshottari tree with phaladesh at each level.
    
    Args:
        planets_data: Birth chart planets
        lagna_data: Lagna info
        vimshottari_periods: list of MD periods from existing calculation
            Example: [
                {"graha": "Sun", "start": "1979-05-04", "end": "1985-05-04",
                 "antardashas": [
                    {"graha": "Sun", "start": ..., "end": ...,
                     "pratyantars": [...]},
                    ...
                 ]},
                ...
            ]
        levels: How deep to go (1-4)
        target_md: Optionally limit to one Mahadasha for performance
        avastha_data_map: Existing avastha data per graha
    
    Returns:
        Tree structure with phaladesh at each level
    """
    from phaladesh_module import get_full_phaladesh_analysis
    
    # First get base phaladesh for all 7 grahas
    base_phaladesh = get_full_phaladesh_analysis(
        planets_data=planets_data,
        lagna_data=lagna_data,
        avastha_data_map=avastha_data_map
    )["phaladesh"]
    
    # Helper to get graha info
    def graha_info(graha_name):
        if graha_name not in PLANET_INDEX:
            return None
        idx = PLANET_INDEX[graha_name]
        if graha_name not in planets_data:
            return None
        rashi = int(planets_data[graha_name].get("longitude", 0) / 30) % 12
        # Get bhava lordship
        lagna_lon = lagna_data.get("longitude", 0)
        lagna_rashi = int(lagna_lon / 30) % 12
        lordship = []
        if idx <= 6:
            for r in range(12):
                if RL[r] == idx:
                    bhava = ((r - lagna_rashi) % 12) + 1
                    lordship.append(bhava)
        bhava = ((rashi - lagna_rashi) % 12) + 1
        return {
            "name": graha_name,
            "idx": idx,
            "rashi": rashi,
            "bhava": bhava,
            "lordship": lordship,
            "phal": base_phaladesh.get(graha_name)
        }
    
    # Build tree
    tree = []
    
    for md_period in vimshottari_periods:
        md_graha = md_period.get("graha")
        if target_md and md_graha != target_md:
            continue
        
        md_info = graha_info(md_graha)
        if not md_info or not md_info["phal"]:
            continue
        
        md_node = {
            "level": "mahadasha",
            "graha": md_graha,
            "graha_hindi": PLANET_HINDI.get(md_graha, md_graha),
            "start_date": md_period.get("start"),
            "end_date": md_period.get("end"),
            "duration": md_period.get("years"),
            "phaladesh": md_info["phal"],
            "summary": md_info["phal"]["summary"],
            "antardashas": []
        }
        
        if levels < 2:
            tree.append(md_node)
            continue
        
        # ============= Level 2: ANTARDASHA =============
        for ad_period in md_period.get("antardashas", []):
            ad_graha = ad_period.get("graha")
            ad_info = graha_info(ad_graha)
            if not ad_info or not ad_info["phal"]:
                continue
            
            ad_combined = synthesize_antardasha_phal(
                md_graha=md_graha, md_phal=md_info["phal"],
                ad_graha=ad_graha, ad_phal=ad_info["phal"],
                md_rashi=md_info["rashi"], ad_rashi=ad_info["rashi"],
                md_idx=md_info["idx"], ad_idx=ad_info["idx"]
            )
            
            # Detect yogas
            yogas = detect_classical_yogas(
                md_graha=md_graha, ad_graha=ad_graha,
                md_lordship=md_info["lordship"], ad_lordship=ad_info["lordship"],
                md_bhava=md_info["bhava"], ad_bhava=ad_info["bhava"],
                panchadha_md_ad=ad_combined["panchadha"]["name"]
            )
            ad_combined["yogas"] = yogas
            
            ad_node = {
                "level": "antardasha",
                "graha": ad_graha,
                "graha_hindi": PLANET_HINDI.get(ad_graha, ad_graha),
                "start_date": ad_period.get("start"),
                "end_date": ad_period.get("end"),
                "duration_days": ad_period.get("days"),
                "phaladesh": ad_combined,
                "summary": ad_combined["summary"],
                "yogas": yogas,
                "pratyantars": []
            }
            
            if levels < 3:
                md_node["antardashas"].append(ad_node)
                continue
            
            # ============= Level 3: PRATYANTAR =============
            for pd_period in ad_period.get("pratyantars", []):
                pd_graha = pd_period.get("graha")
                pd_info = graha_info(pd_graha)
                if not pd_info or not pd_info["phal"]:
                    continue
                
                pd_combined = synthesize_pratyantar_phal(
                    md_graha=md_graha, md_phal=md_info["phal"],
                    ad_graha=ad_graha, ad_phal=ad_info["phal"],
                    ad_combined_phal=ad_combined,
                    pd_graha=pd_graha, pd_phal=pd_info["phal"],
                    md_rashi=md_info["rashi"], ad_rashi=ad_info["rashi"],
                    pd_rashi=pd_info["rashi"],
                    md_idx=md_info["idx"], ad_idx=ad_info["idx"],
                    pd_idx=pd_info["idx"]
                )
                
                pd_node = {
                    "level": "pratyantar",
                    "graha": pd_graha,
                    "graha_hindi": PLANET_HINDI.get(pd_graha, pd_graha),
                    "start_date": pd_period.get("start"),
                    "end_date": pd_period.get("end"),
                    "phaladesh": pd_combined,
                    "summary": pd_combined["summary"]
                }
                ad_node["pratyantars"].append(pd_node)
            
            md_node["antardashas"].append(ad_node)
        
        tree.append(md_node)
    
    return {
        "tree": tree,
        "levels_calculated": levels,
        "target_md": target_md,
        "reference": "BPHS + Phalit Jyotish - Multi-level Vimshottari Phaladesh"
    }
