"""
Bhav Spasht aur Chalit Kundli - Sripati method
===============================================
Source: IGNOU Jyotish Shastra textbook, Unit 4
        (Bhav Sadhan evam Chalit Chakra Nirman, sections 4.3.4 and 4.3.5)

Classical Sripati method:
  Input  -> Spasht Lagna + Spasht Dashmalagna (both in decimal degrees)
  Output -> All 12 bhav spashts + 12 sandhis + chalit positions for grahas

Implementation note:
  Uses integer vikala (1/3600 of a degree) for exact arithmetic.
  Book example matches to the last vikala.
"""

from typing import Dict, Any


# Constants (all in vikala = seconds of arc)
VIKALA_PER_DEGREE = 3600
VIKALA_PER_RASHI = 30 * VIKALA_PER_DEGREE        # 108,000
VIKALA_PER_CIRCLE = 12 * VIKALA_PER_RASHI        # 1,296,000
SIX_RASHI_VIKALA = 6 * VIKALA_PER_RASHI          # 648,000


# -----------------------------------------------------------------
# Conversion helpers
# -----------------------------------------------------------------
def deg_to_vikala(degrees: float) -> int:
    """Convert decimal degrees [0, 360) to integer vikala."""
    return int(round((degrees % 360) * VIKALA_PER_DEGREE))


def vikala_to_deg(vikala: int) -> float:
    """Convert integer vikala to decimal degrees [0, 360)."""
    return (vikala % VIKALA_PER_CIRCLE) / VIKALA_PER_DEGREE


def vikala_to_dms(vikala: int) -> Dict[str, int]:
    """Break total vikala into rashi/ansh/kala/vikala components."""
    v = vikala % VIKALA_PER_CIRCLE
    vk = v % 60
    v //= 60
    kala = v % 60
    v //= 60
    ansh = v % 30
    rashi = (v // 30) % 12
    return {"rashi": rashi, "ansh": ansh, "kala": kala, "vikala": vk}


def dms_to_deg(rashi: int, ansh: int, kala: int, vikala: int) -> float:
    """Convert rashi|ansh|kala|vikala to decimal degrees."""
    return rashi * 30 + ansh + kala / 60 + vikala / 3600


# -----------------------------------------------------------------
# Core calculation — Bhav Spasht (Sripati)
# -----------------------------------------------------------------
def calculate_bhav_spasht(lagna_deg: float, dashmalagna_deg: float) -> Dict[str, Any]:
    """
    Compute 12 Sripati bhav spashts + 12 sandhis.

    Args:
        lagna_deg:        Spasht Lagna in decimal degrees (nirayana).
        dashmalagna_deg:  Spasht Dashmalagna in decimal degrees (nirayana).

    Returns:
        {
          'bhavs':       {1..12: decimal degrees},
          'sandhis':     {1..12: decimal degrees},   # sandhi[i] = boundary between bhav i and i+1
          'bhavs_dms':   {1..12: {rashi, ansh, kala, vikala}},
          'sandhis_dms': {1..12: {rashi, ansh, kala, vikala}},
          'shashtyansh_deg': float,
          'shesh_fal_deg':   float,
        }
    """
    lagna_v = deg_to_vikala(lagna_deg)
    dashm_v = deg_to_vikala(dashmalagna_deg)

    chaturth_v = (dashm_v + SIX_RASHI_VIKALA) % VIKALA_PER_CIRCLE
    saptam_v = (lagna_v + SIX_RASHI_VIKALA) % VIKALA_PER_CIRCLE

    # Shashtyansh = (Chaturth - Lagna) / 6   -> span of each half-bhav for 1..4
    arc_1_to_4 = (chaturth_v - lagna_v) % VIKALA_PER_CIRCLE
    shashtyansh_v = arc_1_to_4 // 6

    # Shesh fal = (Saptam - Chaturth) / 6     -> span of each half-bhav for 4..7
    arc_4_to_7 = (saptam_v - chaturth_v) % VIKALA_PER_CIRCLE
    shesh_fal_v = arc_4_to_7 // 6

    bhavs_v: Dict[int, int] = {1: lagna_v}
    sandhis_v: Dict[int, int] = {}

    # Bhavs 1 -> 4: keep adding shashtyansh
    current = lagna_v
    for i in range(1, 4):
        current = (current + shashtyansh_v) % VIKALA_PER_CIRCLE
        sandhis_v[i] = current
        current = (current + shashtyansh_v) % VIKALA_PER_CIRCLE
        bhavs_v[i + 1] = current

    # Bhavs 4 -> 7: keep adding shesh_fal
    for i in range(4, 7):
        current = (current + shesh_fal_v) % VIKALA_PER_CIRCLE
        sandhis_v[i] = current
        current = (current + shesh_fal_v) % VIKALA_PER_CIRCLE
        bhavs_v[i + 1] = current

    # Bhavs 7 -> 12 and their sandhis = bhavs/sandhis 1 -> 6 shifted by 6 rashis
    for i in range(7, 13):
        bhavs_v[i] = (bhavs_v[i - 6] + SIX_RASHI_VIKALA) % VIKALA_PER_CIRCLE
        sandhis_v[i] = (sandhis_v[i - 6] + SIX_RASHI_VIKALA) % VIKALA_PER_CIRCLE

    return {
        "bhavs": {i: vikala_to_deg(v) for i, v in bhavs_v.items()},
        "sandhis": {i: vikala_to_deg(v) for i, v in sandhis_v.items()},
        "bhavs_dms": {i: vikala_to_dms(v) for i, v in bhavs_v.items()},
        "sandhis_dms": {i: vikala_to_dms(v) for i, v in sandhis_v.items()},
        "shashtyansh_deg": vikala_to_deg(shashtyansh_v),
        "shesh_fal_deg": vikala_to_deg(shesh_fal_v),
    }


# -----------------------------------------------------------------
# Chalit Kundli — which bhav does each graha fall in?
# -----------------------------------------------------------------
def _in_arc(longitude: float, start: float, end: float) -> bool:
    """True if `longitude` lies in the arc (start, end] going forward mod 360."""
    longitude %= 360
    start %= 360
    end %= 360
    if start < end:
        return start < longitude <= end
    # wraparound across 0°
    return longitude > start or longitude <= end


def calculate_chalit_bhav(graha_deg: float, bhav_spasht: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return the chalit bhav of a graha per Nियम 1 of section 4.3.5.

    The 12 sandhis partition the ecliptic into 12 arcs;
    bhav `i` is the arc from sandhi[i-1] to sandhi[i] (sandhi[12] wraps to bhav 1).
    """
    sandhis = bhav_spasht["sandhis"]

    for i in range(1, 13):
        gata = sandhis[12] if i == 1 else sandhis[i - 1]
        agrim = sandhis[i]
        if _in_arc(graha_deg, gata, agrim):
            return {
                "bhav": i,
                "gata_sandhi_deg": gata,
                "agrim_sandhi_deg": agrim,
                "graha_deg": graha_deg % 360,
            }

    # Fallback (should not hit)
    return {
        "bhav": 1,
        "gata_sandhi_deg": sandhis[12],
        "agrim_sandhi_deg": sandhis[1],
        "graha_deg": graha_deg % 360,
    }


def calculate_vishopak_bal(graha_deg: float, chalit_info: Dict[str, Any]) -> float:
    """
    Vishopak Bal (section 4.3 last para):
        (distance from nearest sandhi) * 20 / (half-bhav span)

    Bhav-middle graha = full vishopak (close to 20), sandhi-me graha = 0.
    """
    gata = chalit_info["gata_sandhi_deg"]
    agrim = chalit_info["agrim_sandhi_deg"]
    g = graha_deg % 360

    span = (agrim - gata) % 360
    dist_from_gata = (g - gata) % 360
    # Distance from the nearer sandhi, normalized by half-span
    half = span / 2
    dist_from_nearest = min(dist_from_gata, span - dist_from_gata)
    return (dist_from_nearest / half) * 20 if half > 0 else 0.0


def calculate_full_chalit_chakra(
    lagna_deg: float,
    dashmalagna_deg: float,
    graha_positions: Dict[str, float],
) -> Dict[str, Any]:
    """
    End-to-end: build bhav spasht + chalit placement + vishopak bal for all grahas.

    graha_positions: {'Sun': 338.35833, 'Moon': 359.44, ...}  (decimal degrees, nirayana)
    """
    bhav_spasht = calculate_bhav_spasht(lagna_deg, dashmalagna_deg)

    chalit: Dict[str, Dict[str, Any]] = {}
    for graha, deg in graha_positions.items():
        info = calculate_chalit_bhav(deg, bhav_spasht)
        info["vishopak_bal"] = calculate_vishopak_bal(deg, info)
        chalit[graha] = info

    return {
        "bhav_spasht": bhav_spasht,
        "chalit_positions": chalit,
    }


# -----------------------------------------------------------------
# Self-test against the book example
# -----------------------------------------------------------------
def _run_book_verification():
    """IGNOU textbook page 123 example."""
    # Lagna:       2|15|3|22
    # Dashmalagna: 11|12|4|16
    lagna = dms_to_deg(2, 15, 3, 22)
    dashm = dms_to_deg(11, 12, 4, 16)

    result = calculate_bhav_spasht(lagna, dashm)

    expected_bhavs = {
        1:  (2, 15, 3, 22),
        2:  (3, 14, 3, 40),
        3:  (4, 13, 3, 58),
        4:  (5, 12, 4, 16),
        5:  (6, 13, 3, 58),
        6:  (7, 14, 3, 40),
        7:  (8, 15, 3, 22),
        8:  (9, 14, 3, 40),
        9:  (10, 13, 3, 58),
        10: (11, 12, 4, 16),
        11: (0, 13, 3, 58),
        12: (1, 14, 3, 40),
    }

    print("Bhav Spasht verification:")
    print("-" * 70)
    all_ok = True
    for i in range(1, 13):
        got = result["bhavs_dms"][i]
        exp = expected_bhavs[i]
        ok = (got["rashi"], got["ansh"], got["kala"], got["vikala"]) == exp
        all_ok = all_ok and ok
        mark = "OK" if ok else "MISMATCH"
        print(f"  Bhav {i:2}: got {got['rashi']}|{got['ansh']:2}|{got['kala']:2}|"
              f"{got['vikala']:2}  expected {exp[0]}|{exp[1]:2}|{exp[2]:2}|{exp[3]:2}  [{mark}]")
    print("-" * 70)
    print("Shashtyansh:", result["shashtyansh_deg"], "deg")
    print("Shesh fal:  ", result["shesh_fal_deg"], "deg")
    print("ALL MATCH" if all_ok else "FAILED")
    return all_ok


if __name__ == "__main__":
    _run_book_verification()
