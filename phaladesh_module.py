"""
================================================================================
PHALADESH MODULE - JyotishRishi Platform
================================================================================
Drop this file at: /root/jyotish-api/phaladesh_module.py

Provides comprehensive Mahadasha Phaladesh by combining:
  - Tatkalika + Panchadha Maitri (uses existing PF, RL from astro_engine)
  - Lajjitadi Avastha (6 special states)
  - Phaladesh Synthesis Engine (final score + verdict + Hindi paragraph)

Reference: BPHS + Phalit Jyotish (Acharya Harishchandra Purohit)
================================================================================
"""

# Import existing constants from astro_engine
from astro_engine import PF, RL


# Planet index mapping (matches server's PF/RL indexing)
# Server uses: 0=Sun, 1=Moon, 2=Jupiter, 3=Mars, 4=Mercury, 5=Venus, 6=Saturn

PLANET_INDEX = {
    "Sun": 0, "Surya": 0,
    "Moon": 1, "Chandra": 1,
    "Jupiter": 2, "Guru": 2,
    "Mars": 3, "Mangal": 3,
    "Mercury": 4, "Budh": 4,
    "Venus": 5, "Shukra": 5,
    "Saturn": 6, "Shani": 6,
}

PLANET_HINDI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु"
}


# ============================================================================
# 1. TATKALIKA MAITRI
# ============================================================================
TATKALIKA_MITRA_HOUSES = {2, 3, 4, 10, 11, 12}

def tatkalika_maitri(rashi_a, rashi_b):
    house = ((rashi_b - rashi_a) % 12) + 1
    return 2 if house in TATKALIKA_MITRA_HOUSES else 0


# ============================================================================
# 2. PANCHADHA MAITRI
# ============================================================================
PANCHADHA_LEVELS = {0: "Adhi Shatru", 1: "Shatru", 2: "Sama", 3: "Mitra", 4: "Adhi Mitra"}
PANCHADHA_HINDI = {0: "अधि शत्रु", 1: "शत्रु", 2: "सम", 3: "मित्र", 4: "अधि मित्र"}
PANCHADHA_COLOR = {0: "#ef4444", 1: "#f97316", 2: "#9ca3af", 3: "#3b82f6", 4: "#22c55e"}
PANCHADHA_SCORE = {0: -2, 1: -1, 2: 0, 3: 1, 4: 2}


def combine_naisargik_tatkalika(naisargik_val, tatkalika_val):
    if naisargik_val == 2 and tatkalika_val == 2: return 4
    elif naisargik_val == 2 and tatkalika_val == 0: return 2
    elif naisargik_val == 1 and tatkalika_val == 2: return 3
    elif naisargik_val == 1 and tatkalika_val == 0: return 1
    elif naisargik_val == 0 and tatkalika_val == 2: return 2
    else: return 0


def panchadha_maitri(graha_a_idx, graha_a_rashi, graha_b_idx, graha_b_rashi):
    naisargik_val = PF[graha_a_idx][graha_b_idx]
    tatkalika_val = tatkalika_maitri(graha_a_rashi, graha_b_rashi)
    panchadha_level = combine_naisargik_tatkalika(naisargik_val, tatkalika_val)
    return {
        "naisargik": ["Shatru", "Sama", "Mitra"][naisargik_val],
        "tatkalika": "Mitra" if tatkalika_val == 2 else "Shatru",
        "panchadha": PANCHADHA_LEVELS[panchadha_level],
        "panchadha_hindi": PANCHADHA_HINDI[panchadha_level],
        "color": PANCHADHA_COLOR[panchadha_level],
        "score": PANCHADHA_SCORE[panchadha_level],
        "level": panchadha_level,
    }


def calculate_panchadha_for_chart(planets_data):
    positions = {}
    for name, data in planets_data.items():
        if name in PLANET_INDEX:
            idx = PLANET_INDEX[name]
            lon = data.get("longitude", 0) if isinstance(data, dict) else data
            positions[name] = {"idx": idx, "rashi": int(lon / 30) % 12}
    matrix = {}
    for graha_a, info_a in positions.items():
        matrix[graha_a] = {}
        for graha_b, info_b in positions.items():
            if graha_a == graha_b:
                continue
            matrix[graha_a][graha_b] = panchadha_maitri(
                info_a["idx"], info_a["rashi"], info_b["idx"], info_b["rashi"]
            )
    return matrix


def get_lagnesh_panchadha(planets_data, lagna_lon):
    lagna_rashi = int(lagna_lon / 30) % 12
    lagnesh_idx = RL[lagna_rashi]
    lagnesh_name = None
    for name, idx in PLANET_INDEX.items():
        if idx == lagnesh_idx and name in ("Sun", "Moon", "Mars", "Mercury",
                                           "Jupiter", "Venus", "Saturn"):
            lagnesh_name = name
            break
    if not lagnesh_name or lagnesh_name not in planets_data:
        return {}, lagnesh_name
    lagnesh_data = planets_data[lagnesh_name]
    lagnesh_rashi = int(lagnesh_data.get("longitude", 0) / 30) % 12
    result = {}
    for graha_name, graha_data in planets_data.items():
        if graha_name not in PLANET_INDEX or graha_name == lagnesh_name:
            continue
        graha_idx = PLANET_INDEX[graha_name]
        graha_rashi = int(graha_data.get("longitude", 0) / 30) % 12
        result[graha_name] = panchadha_maitri(
            graha_idx, graha_rashi, lagnesh_idx, lagnesh_rashi
        )
    return result, lagnesh_name


# ============================================================================
# 3. LAJJITADI AVASTHA
# ============================================================================
WATERY_RASHIS = {3, 7, 11}
# Swakshetra (own rashi) per planet index (server indexing)
# 0=Sun, 1=Moon, 2=Jupiter, 3=Mars, 4=Mercury, 5=Venus, 6=Saturn
SWAKSHETRA = {
    0: {4},          # Sun - Simha
    1: {3},          # Moon - Karka
    2: {8, 11},      # Jupiter - Dhanu, Meen
    3: {0, 7},       # Mars - Mesh, Vrishchik
    4: {2, 5},       # Mercury - Mithun, Kanya
    5: {1, 6},       # Venus - Vrish, Tula
    6: {9, 10}       # Saturn - Makar, Kumbh
}
# Uccha (exaltation) per planet
UCCHA_RASHI = {
    0: 0,    # Sun - Mesh
    1: 1,    # Moon - Vrish
    2: 3,    # Jupiter - Karka
    3: 9,    # Mars - Makar
    4: 5,    # Mercury - Kanya
    5: 11,   # Venus - Meen
    6: 6     # Saturn - Tula
}


def calculate_lajjitadi_avastha(planet_name, planets_data, lagna_lon):
    if planet_name not in PLANET_INDEX:
        return []
    p_idx = PLANET_INDEX[planet_name]
    p_data = planets_data.get(planet_name, {})
    if not isinstance(p_data, dict) or "longitude" not in p_data:
        return []
    p_rashi = int(p_data["longitude"] / 30) % 12
    lagna_rashi = int(lagna_lon / 30) % 12
    p_bhava = ((p_rashi - lagna_rashi) % 12) + 1
    
    same_rashi = []
    for other_name, other_data in planets_data.items():
        if other_name == planet_name:
            continue
        if isinstance(other_data, dict) and "longitude" in other_data:
            other_rashi = int(other_data["longitude"] / 30) % 12
            if other_rashi == p_rashi:
                same_rashi.append(other_name)
    
    avasthas = []
    
    # 1. LAJJITA
    if p_bhava == 5:
        bad = {"Rahu", "Ketu", "Sun", "Surya", "Saturn", "Shani", "Mars", "Mangal"}
        if any(c in bad for c in same_rashi):
            avasthas.append({"name": "Lajjita", "hindi": "लज्जिता",
                "meaning": "Embarrassed - Phal kshina hota hai", "intensity": "negative"})
    
    # 2. GARVITA
    is_uccha = (p_rashi == UCCHA_RASHI.get(p_idx))
    is_swakshetra = (p_rashi in SWAKSHETRA.get(p_idx, set()))
    if is_uccha or is_swakshetra:
        avasthas.append({"name": "Garvita", "hindi": "गर्विता",
            "meaning": f"Proud - {'Uccha' if is_uccha else 'Swakshetra'}",
            "intensity": "positive"})
    
    # 3. KSHUDHITA
    rashi_lord_idx = RL[p_rashi]
    if rashi_lord_idx != p_idx and rashi_lord_idx <= 6:
        if PF[p_idx][rashi_lord_idx] == 0:
            for other in same_rashi:
                if other in PLANET_INDEX:
                    if PF[p_idx][PLANET_INDEX[other]] == 0:
                        avasthas.append({"name": "Kshudhita", "hindi": "क्षुधिता",
                            "meaning": "Hungry - Phal heena, dukh denewala",
                            "intensity": "negative"})
                        break
    
    # 4. TRUSHITA
    if p_rashi in WATERY_RASHIS:
        for other in same_rashi:
            if other in PLANET_INDEX:
                if PF[p_idx][PLANET_INDEX[other]] == 0:
                    avasthas.append({"name": "Trushita", "hindi": "तृषिता",
                        "meaning": "Thirsty - Manasik kasht", "intensity": "negative"})
                    break
    
    # 5. MUDITA
    if rashi_lord_idx != p_idx and rashi_lord_idx <= 6:
        if PF[p_idx][rashi_lord_idx] == 2:
            for other in same_rashi:
                if other in PLANET_INDEX:
                    if PF[p_idx][PLANET_INDEX[other]] == 2:
                        avasthas.append({"name": "Mudita", "hindi": "मुदिता",
                            "meaning": "Delighted - Sukh aur samriddhi",
                            "intensity": "positive"})
                        break
    
    # 6. KSHOBHITA
    has_sun = any(s in ("Sun", "Surya") for s in same_rashi)
    has_enemy = False
    for other in same_rashi:
        if other in PLANET_INDEX and other not in ("Sun", "Surya"):
            if PF[p_idx][PLANET_INDEX[other]] == 0:
                has_enemy = True
                break
    if has_sun and has_enemy and planet_name not in ("Sun", "Surya"):
        avasthas.append({"name": "Kshobhita", "hindi": "क्षोभिता",
            "meaning": "Agitated - Ashanti, vyatha", "intensity": "negative"})
    
    return avasthas


# ============================================================================
# 4. PHALADESH SYNTHESIS - Score Constants
# ============================================================================
WEIGHT_BALADI = 15
WEIGHT_DEEPTADI = 20
WEIGHT_PANCHADHA = 20
WEIGHT_LAJJITADI = 10
WEIGHT_BHAVA = 15
WEIGHT_SPECIAL = 10
WEIGHT_CHESHTA = 5
WEIGHT_SHAYANADI = 5

DEEPTADI_SCORES = {
    "Deepta": 3, "Deeept": 3, "Swastha": 2, "Pramudita": 2, "Mudita": 2,
    "Shanta": 1, "Shaant": 1, "Shakta": 1, "Peedita": -1,
    "Deena": -2, "Vikala": -2, "Khala": -3, "Khal": -3,
}
LAJJITADI_SCORES = {
    "Garvita": 3, "Mudita": 2, "Lajjita": -2,
    "Kshudhita": -2, "Trushita": -1, "Kshobhita": -3,
}
CHESHTA_SCORES = {"Cheshta": 2, "Drishti": 1, "Vicheeshta": 0}
SHAYANADI_SCORES = {
    "Shayan": -1, "Upaveshan": 0, "Netrapani": 1, "Prakashana": 2,
    "Gamana": 1, "Agamana": 0, "Samavaas": 1, "Aagam": 1, "Sabha": 2,
    "Aagama": 0, "Bhojan": 1, "Nritya": 2, "Kautuk": 2, "Kautuka": 2,
    "Nidra": -2, "Nidraa": -2,
}
BHAVA_SCORES = {1: 2, 2: 1, 3: 0, 4: 2, 5: 3, 6: -1,
                7: 2, 8: -2, 9: 3, 10: 2, 11: 1, 12: -1}
SPECIAL_SCORES = {
    "Uccha": 3, "Mool_Trikona": 2, "Swakshetra": 2, "Mitra_Rashi": 1,
    "Sama_Rashi": 0, "Shatru_Rashi": -1, "Neecha": -3,
    "Asta": -2, "Vakri": 1,
}


def baladi_to_score(phal_percent):
    if phal_percent >= 100: return 2
    elif phal_percent >= 75: return 1
    elif phal_percent >= 50: return 0
    elif phal_percent >= 25: return -1
    else: return -2


GRAHA_KARAKAS = {
    "Sun": ["Pita", "Aatma", "Pratishtha", "Sarkari kaam", "Health"],
    "Moon": ["Mata", "Mann", "Manasik shanti", "Tarl padarth", "Janta"],
    "Mars": ["Bhai", "Saahas", "Bhumi", "Sena", "Shatru-vijay"],
    "Mercury": ["Buddhi", "Vyapar", "Vidya", "Lekhan", "Sandesh"],
    "Jupiter": ["Dharma", "Gyan", "Putra", "Guru", "Dhan"],
    "Venus": ["Patni", "Kala", "Vahan", "Sukh", "Bhog"],
    "Saturn": ["Sevak", "Krishi", "Karma", "Vairagya", "Lambi yatra"],
    "Rahu": ["Videsh", "Maya", "Achanak labh/haani", "Aushadhi"],
    "Ketu": ["Moksha", "Adhyatma", "Tantra", "Vichitra ghatnaayein"],
}
BHAVA_LIFE_AREAS = {
    1: "Swayam, swasthya, swabhav", 2: "Dhan, kutumb, vaani",
    3: "Bhai-behan, parakram", 4: "Mata, ghar, sukh, vahan",
    5: "Putra, vidya, buddhi", 6: "Shatru, rog, rin, sevak",
    7: "Patni/Pati, vyapar, vidaayi", 8: "Aayu, gupt baatein, achanak",
    9: "Dharma, bhagya, pita", 10: "Karma, naukri, pratishtha",
    11: "Labha, mitra, badi behnein", 12: "Vyaya, moksha, videsh",
}
BHAVA_NAMES = ["Lagna", "Dhana", "Bhratru", "Sukha", "Putra", "Shatru",
               "Kalatra", "Ayush", "Dharma", "Karma", "Labha", "Vyaya"]


def synthesize_mahadasha_phal(graha_name, graha_data, avastha_data,
                                panchadha_data, lajjitadi_data,
                                bhava_position, bhava_lordship=None,
                                special_position=None):
    components = {}
    total_score = 0
    
    # 1. BALADI
    baladi_pct = avastha_data.get("baladi_percent", 75)
    baladi_score = baladi_to_score(baladi_pct)
    bal_contrib = (baladi_score / 2) * WEIGHT_BALADI
    components["baladi"] = {
        "name": avastha_data.get("baladi", "Unknown"),
        "percent": baladi_pct, "score": baladi_score,
        "contribution": round(bal_contrib, 1),
        "remark": _baladi_remark(baladi_score)
    }
    total_score += bal_contrib
    
    # 2. DEEPTADI
    deeptadi_name = avastha_data.get("deeptadi", "Shaant")
    deeptadi_clean = deeptadi_name.split("(")[0].strip()
    dpt_score = DEEPTADI_SCORES.get(deeptadi_clean, 0)
    dpt_contrib = (dpt_score / 3) * WEIGHT_DEEPTADI
    components["deeptadi"] = {
        "name": deeptadi_name, "score": dpt_score,
        "contribution": round(dpt_contrib, 1),
        "remark": _deeptadi_remark(dpt_score)
    }
    total_score += dpt_contrib
    
    # 3. PANCHADHA
    pan_score = panchadha_data.get("score", 0)
    pan_contrib = (pan_score / 2) * WEIGHT_PANCHADHA
    components["panchadha"] = {
        "name": panchadha_data.get("panchadha", "Sama"),
        "hindi": panchadha_data.get("panchadha_hindi", ""),
        "score": pan_score, "contribution": round(pan_contrib, 1),
        "remark": _panchadha_remark(pan_score)
    }
    total_score += pan_contrib
    
    # 4. LAJJITADI
    if lajjitadi_data:
        scores = [LAJJITADI_SCORES.get(l["name"], 0) for l in lajjitadi_data]
        max_score = max(scores, key=abs) if scores else 0
        names = [l["hindi"] + f" ({l['name']})" for l in lajjitadi_data]
        lj_contrib = (max_score / 3) * WEIGHT_LAJJITADI
        components["lajjitadi"] = {
            "names": names, "score": max_score,
            "contribution": round(lj_contrib, 1),
            "remark": _lajjitadi_remark(max_score)
        }
        total_score += lj_contrib
    else:
        components["lajjitadi"] = {"names": [], "score": 0, "contribution": 0,
                                    "remark": "Koi vishesh avastha nahi"}
    
    # 5. BHAVA
    bh_score = BHAVA_SCORES.get(bhava_position, 0)
    bh_contrib = (bh_score / 3) * WEIGHT_BHAVA
    components["bhava"] = {
        "position": bhava_position,
        "name": BHAVA_NAMES[bhava_position - 1] if 1 <= bhava_position <= 12 else "Unknown",
        "score": bh_score, "contribution": round(bh_contrib, 1),
        "remark": _bhava_remark(bhava_position)
    }
    total_score += bh_contrib
    
    # 6. SPECIAL
    if special_position:
        sp_score = SPECIAL_SCORES.get(special_position, 0)
        sp_contrib = (sp_score / 3) * WEIGHT_SPECIAL
        components["special"] = {
            "name": special_position, "score": sp_score,
            "contribution": round(sp_contrib, 1),
            "remark": _special_remark(special_position)
        }
        total_score += sp_contrib
    
    # 7. ASTA
    if avastha_data.get("is_asta", False):
        asta_contrib = (-2 / 3) * WEIGHT_SPECIAL
        components["asta"] = {
            "is_asta": True, "contribution": round(asta_contrib, 1),
            "remark": "Asta (Combust) - phal mein significant kami"
        }
        total_score += asta_contrib
    
    # 8. CHESHTA
    cheshta = avastha_data.get("cheshta", "Drishti")
    cheshta_clean = cheshta.split("(")[0].strip()
    ch_score = CHESHTA_SCORES.get(cheshta_clean, 0)
    ch_contrib = (ch_score / 2) * WEIGHT_CHESHTA
    components["cheshta"] = {
        "name": cheshta, "score": ch_score,
        "contribution": round(ch_contrib, 1),
        "remark": _cheshta_remark(ch_score)
    }
    total_score += ch_contrib
    
    # 9. SHAYANADI
    shayanadi = avastha_data.get("shayanadi", "Aagam")
    sh_score = SHAYANADI_SCORES.get(shayanadi, 0)
    sh_contrib = (sh_score / 2) * WEIGHT_SHAYANADI
    components["shayanadi"] = {
        "name": shayanadi, "score": sh_score,
        "contribution": round(sh_contrib, 1)
    }
    total_score += sh_contrib
    
    # FINAL
    final_score = max(0, min(100, 50 + total_score / 2))
    verdict = _get_verdict(final_score)
    phaladesh_text = _generate_phaladesh_paragraph(
        graha_name, components, final_score, verdict, bhava_position
    )
    areas = {
        "graha_karakas": GRAHA_KARAKAS.get(graha_name, []),
        "current_bhava": BHAVA_LIFE_AREAS.get(bhava_position, ""),
        "lordship_bhavas": [BHAVA_LIFE_AREAS.get(b, "") for b in (bhava_lordship or [])]
    }
    return {
        "graha": graha_name,
        "graha_hindi": PLANET_HINDI.get(graha_name, graha_name),
        "final_score": round(final_score, 1),
        "raw_score": round(total_score, 1),
        "verdict": verdict["label"],
        "verdict_hindi": verdict["hindi"],
        "verdict_color": verdict["color"],
        "verdict_emoji": verdict["emoji"],
        "components": components,
        "phaladesh": phaladesh_text,
        "life_areas": areas,
        "summary": f"{graha_name} - {verdict['emoji']} {verdict['label']} "
                   f"({components['panchadha']['name']} with Lagnesh, "
                   f"{bhava_position}{_ordinal(bhava_position)} bhav)"
    }


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


def _baladi_remark(score):
    return ["Mrit - phal heena", "Baal - phal kshina", "Kumar - madhyam phal",
            "Vriddha - phal mein kuch kami", "Yuva - phal sampurna"][score + 2]


def _deeptadi_remark(score):
    if score >= 3: return "Sarvashreshtha avastha"
    elif score >= 2: return "Uttam phal"
    elif score >= 1: return "Madhyam phal"
    elif score == 0: return "Sthir phal"
    elif score >= -1: return "Kuch peeda"
    elif score >= -2: return "Phal mein kami"
    else: return "Atyant nyun phal"


def _panchadha_remark(score):
    if score >= 2: return "Lagnesh ke Adhi Mitra - sarvottam"
    elif score >= 1: return "Lagnesh ke Mitra - shubh"
    elif score == 0: return "Sama bhav - tatastha"
    elif score >= -1: return "Lagnesh ke Shatru - kasht"
    else: return "Adhi Shatru - vishesh kasht"


def _lajjitadi_remark(score):
    if score >= 3: return "Garvita - sarvashreshtha vishesh avastha"
    elif score >= 2: return "Mudita - shubh vishesh sthiti"
    elif score == 0: return "Vishesh avastha nahi"
    elif score >= -2: return "Negative special state"
    else: return "Atyant nakaratmak avastha"


def _bhava_remark(b):
    if b in [1, 5, 9]: return f"{BHAVA_NAMES[b-1]} bhav (Trikona) - shubh"
    elif b in [4, 7, 10]: return f"{BHAVA_NAMES[b-1]} bhav (Kendra) - balshali"
    elif b in [3, 11]: return f"{BHAVA_NAMES[b-1]} bhav (Upachaya) - vriddhi"
    elif b == 6: return "Shatru bhav - rog/rin/shatru"
    elif b == 8: return "Ayush bhav - kasht/vighna"
    elif b == 12: return "Vyaya bhav - vyay/moksha"
    elif b == 2: return "Dhana bhav - kutumb"
    return f"{BHAVA_NAMES[b-1]} bhav"


def _special_remark(name):
    return {
        "Uccha": "Uccha rashi mein - sarvashreshtha bal",
        "Swakshetra": "Swakshetra mein - poorna bal",
        "Mool_Trikona": "Mool trikona mein - vishesh balshali",
        "Mitra_Rashi": "Mitra rashi mein - shubh",
        "Shatru_Rashi": "Shatru rashi mein - kasht",
        "Neecha": "Neecha rashi mein - bal heen",
        "Asta": "Asta - prakash heen", "Vakri": "Vakri - vishesh prabhav"
    }.get(name, "")


def _cheshta_remark(score):
    if score >= 2: return "Cheshta - sampurna phal"
    elif score >= 1: return "Drishti - madhyam phal"
    else: return "Vicheeshta - matra phal"


def _ordinal(n):
    return {1: "st", 2: "nd", 3: "rd"}.get(n, "th")


def _generate_phaladesh_paragraph(graha, components, score, verdict, bhava):
    paras = []
    paras.append(f"{graha} ki Mahadasha aapke liye {verdict['hindi']} rahegi ({score:.0f}/100 score).")
    bal = components["baladi"]
    deep = components["deeptadi"]
    paras.append(f"Graha {bal['name']} avastha ({bal['percent']}% bal) mein hai aur "
                f"{deep['name']} avastha mein hai - {deep['remark']}.")
    pan = components["panchadha"]
    paras.append(f"Lagnesh ke saath {pan['hindi']} ({pan['name']}) sambandh - {pan['remark']}.")
    bh = components["bhava"]
    paras.append(f"Yeh graha {bh['position']}{_ordinal(bh['position'])} bhav "
                f"({bh['name']}) mein hai - {bh['remark']}.")
    if "special" in components:
        paras.append(f"Vishesh sthiti: {components['special']['remark']}.")
    if "asta" in components:
        paras.append("Graha Asta (combust) hai - prakash kshina, phal mein kami.")
    lj = components["lajjitadi"]
    if lj["names"]:
        paras.append(f"Lajjitadi avastha: {', '.join(lj['names'])} - {lj['remark']}.")
    if score >= 65:
        paras.append("Yeh dasha aapke important kaaryon ke liye anukool hai. "
                    "Naye prayatna, nivesh aur yojnaayein iss period mein labhdayak hongi.")
    elif score >= 45:
        paras.append("Yeh dasha mishrit phal degi - kuch kshetron mein labh, kuch mein kasht. "
                    "Soch-samajh kar nirnay lein aur dhairya rakhein.")
    else:
        paras.append("Iss dasha mein savadhani aapekshit hai. Bade nirnay tal dein, "
                    "swasthya ka dhyan rakhein, aur upay/daan-dharma karein.")
    return " ".join(paras)


# ============================================================================
# MAIN API HELPER
# ============================================================================
def get_full_phaladesh_analysis(planets_data, lagna_data, current_dasha_graha=None,
                                  avastha_data_map=None):
    """Main API helper - call this from /mahadasha-phaladesh endpoint."""
    lagna_lon = lagna_data.get("longitude", 0) if isinstance(lagna_data, dict) else lagna_data
    lagna_rashi = int(lagna_lon / 30) % 12
    
    panchadha_matrix = calculate_panchadha_for_chart(planets_data)
    lagnesh_panchadha, lagnesh_name = get_lagnesh_panchadha(planets_data, lagna_lon)
    
    lajjitadi = {}
    for planet_name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        if planet_name in planets_data:
            lajjitadi[planet_name] = calculate_lajjitadi_avastha(
                planet_name, planets_data, lagna_lon
            )
    
    phaladesh_per_graha = {}
    grahas_to_analyze = [current_dasha_graha] if current_dasha_graha else [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
    ]
    
    for graha in grahas_to_analyze:
        if graha not in planets_data:
            continue
        graha_data = planets_data[graha]
        graha_rashi = int(graha_data.get("longitude", 0) / 30) % 12
        bhava_pos = ((graha_rashi - lagna_rashi) % 12) + 1
        
        if avastha_data_map and graha in avastha_data_map:
            avastha = avastha_data_map[graha]
        else:
            avastha = {"baladi": "Yuva", "baladi_percent": 100,
                       "deeptadi": "Shaant", "shayanadi": "Aagam",
                       "cheshta": "Drishti", "is_asta": False}
        
        special = None
        graha_idx = PLANET_INDEX.get(graha)
        if graha_idx is not None:
            if graha_rashi == UCCHA_RASHI.get(graha_idx):
                special = "Uccha"
            elif graha_rashi in SWAKSHETRA.get(graha_idx, set()):
                special = "Swakshetra"
            elif (graha_rashi + 6) % 12 == UCCHA_RASHI.get(graha_idx):
                special = "Neecha"
        
        lordship = []
        if graha_idx is not None and graha_idx <= 6:
            for r in range(12):
                if RL[r] == graha_idx:
                    bhava = ((r - lagna_rashi) % 12) + 1
                    lordship.append(bhava)
        
        panchadha_with_lagnesh = lagnesh_panchadha.get(graha, {
            "panchadha": "Sama", "panchadha_hindi": "सम", "score": 0
        })
        
        result = synthesize_mahadasha_phal(
            graha_name=graha, graha_data=graha_data,
            avastha_data=avastha, panchadha_data=panchadha_with_lagnesh,
            lajjitadi_data=lajjitadi.get(graha, []),
            bhava_position=bhava_pos, bhava_lordship=lordship,
            special_position=special
        )
        phaladesh_per_graha[graha] = result
    
    return {
        "lagnesh": lagnesh_name,
        "lagnesh_hindi": PLANET_HINDI.get(lagnesh_name, ""),
        "panchadha_matrix": panchadha_matrix,
        "lagnesh_panchadha": lagnesh_panchadha,
        "lajjitadi_avastha": lajjitadi,
        "phaladesh": phaladesh_per_graha,
        "reference": "BPHS Adhyaya 3 (Maitri) + 45 (Lajjitadi) + Phalit Jyotish"
    }
