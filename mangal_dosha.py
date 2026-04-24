"""
Mangal Dosha Complete Analysis
==============================
Classical Mangal Dosha check from 3 references:
  1. Lagna (Ascendant)
  2. Chandra rashi (Moon sign as lagna)
  3. Navamsha D9 Lagna

Bhang (cancellation) rules from Parashar Light classical references:
  1. Mangal अस्त / दुर्बल (nich/shatru/vakri) / शुभ ग्रह से दृष्ट
  2. Panchak (1,2,4,8,12) में Chandra/Guru/Budh के साथ युति या उनसे दृष्ट
  3. Mangal + Budh युति या दृष्टि
  4. बली Guru या Shukra Lagna/7th में; या Mangal वक्री/नीच/शत्रु राशि में
  5. Rashi exceptions: Mesh-1, Vrishchik-4, Makar-7, Karka-8, Kumbh/Sinh-12
  6. Mangal चलित चक्र में सन्धि में हो (निर्बल)
"""

from typing import Any


# Rashi numbers (1-12): Mesh=1, Vrishabh=2, ..., Meena=12
MANGAL_DOSHA_BHAVS = [1, 4, 7, 8, 12]

# Rashi exception — per aapke Parashar Light reference
# Mangal in these (bhav, rashi) combos → no dosha
MANGAL_RASHI_EXCEPTIONS = {
    1: [1],          # Mesh
    4: [8],          # Vrishchik
    7: [10],         # Makar
    8: [4],          # Karka
    12: [5, 11],     # Sinh, Kumbh
}

RASHI_NAMES_HI = [
    "", "मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन",
]

BHAV_ORDINALS_HI = [
    "", "प्रथम", "द्वितीय", "तृतीय", "चतुर्थ", "पंचम", "षष्ठ",
    "सप्तम", "अष्टम", "नवम", "दशम", "एकादश", "द्वादश",
]

# Mangal weak definitions
NICHA_RASHI_MARS = 4          # Karka (debilitation)
SHATRU_RASHIS_MARS = [3, 6, 2, 7]  # Mithun, Kanya (Budh) + Vrishabh, Tula (Shukra)

# Shubh grahas for drishti check
SHUBH_GRAHAS = {"Moon", "Mercury", "Jupiter", "Venus"}
PAAP_GRAHAS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


# -----------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------
def _bhav_from_ref(graha_rashi: int, ref_rashi: int) -> int:
    """How many houses is graha_rashi from ref_rashi (1-based, 1..12)."""
    return ((graha_rashi - ref_rashi) % 12) + 1


def _has_drishti(drishta_rashi: int, drashya_rashi: int, graha: str) -> bool:
    """
    Check if `drishta` graha (at drishta_rashi) sees `drashya_rashi`.
    All grahas see 7th. Mangal also 4th, 8th. Guru 5th, 9th. Shani 3rd, 10th.
    """
    diff = ((drashya_rashi - drishta_rashi) % 12) + 1
    if diff == 7:
        return True
    if graha == "Mars" and diff in (4, 8):
        return True
    if graha == "Jupiter" and diff in (5, 9):
        return True
    if graha == "Saturn" and diff in (3, 10):
        return True
    return False


def _is_mars_weak(mars_data: dict) -> tuple[bool, list[str]]:
    """
    Check if Mangal is weak.
    Weak = nich rashi, shatru rashi, or vakri (retrograde).
    Returns (is_weak, list_of_reasons).
    """
    reasons = []
    rashi_num = mars_data.get("rashi_num", 0)
    retrograde = mars_data.get("retrograde", False)

    if rashi_num == NICHA_RASHI_MARS:
        reasons.append(f"मंगल {RASHI_NAMES_HI[NICHA_RASHI_MARS]} राशि (नीच) में है")
    if rashi_num in SHATRU_RASHIS_MARS:
        reasons.append(f"मंगल {RASHI_NAMES_HI[rashi_num]} राशि (शत्रु राशि) में है")
    if retrograde:
        reasons.append("मंगल वक्री है")

    return len(reasons) > 0, reasons


def _check_single_reference(
    ref_name: str,
    ref_rashi: int,
    mars_rashi: int,
    planets_by_name: dict,
    mars_data: dict,
    is_chalit_sandhi: bool,
) -> dict:
    """
    Check Mangal Dosha from a single reference (Lagna / Chandra / Navamsha).
    Returns dosha status + bhang reasons.
    """
    bhav = _bhav_from_ref(mars_rashi, ref_rashi)
    has_dosha_bhav = bhav in MANGAL_DOSHA_BHAVS

    result = {
        "reference": ref_name,
        "bhav": bhav,
        "bhav_name": BHAV_ORDINALS_HI[bhav],
        "has_dosha_from_placement": has_dosha_bhav,
        "bhang_reasons": [],
        "final_has_dosha": has_dosha_bhav,
    }

    if not has_dosha_bhav:
        return result

    bhang_reasons = []

    # ---- Rule 5: Rashi exceptions (check first — strongest) ----
    if bhav in MANGAL_RASHI_EXCEPTIONS:
        if mars_rashi in MANGAL_RASHI_EXCEPTIONS[bhav]:
            bhang_reasons.append(
                f"मंगल {BHAV_ORDINALS_HI[bhav]} भाव में "
                f"{RASHI_NAMES_HI[mars_rashi]} राशि (स्वक्षेत्र/मित्र) में स्थित है"
            )

    # ---- Rule 6: Chalit sandhi ----
    if is_chalit_sandhi:
        bhang_reasons.append("मंगल चलित चक्र में सन्धि में है (निर्बल)")

    # ---- Rule 1: Mangal ast or weak ----
    sun_data = planets_by_name.get("Sun", {})
    sun_rashi = sun_data.get("rashi_num", 0)
    sun_lon = sun_data.get("longitude", -999)
    mars_lon = mars_data.get("longitude", -999)
    if sun_rashi == mars_rashi and sun_lon >= 0 and mars_lon >= 0:
        # Within 17° of Sun → ast (combust)
        diff = min(abs(sun_lon - mars_lon), 360 - abs(sun_lon - mars_lon))
        if diff < 17:
            bhang_reasons.append(f"मंगल सूर्य के अस्त (combust) में है ({diff:.1f}°)")

    is_weak, weak_reasons = _is_mars_weak(mars_data)
    if is_weak:
        bhang_reasons.extend(weak_reasons)

    # ---- Rules 2, 3: Yuti / drishti with Chandra, Guru, Budh ----
    for graha_name in ["Moon", "Jupiter", "Mercury"]:
        g = planets_by_name.get(graha_name, {})
        g_rashi = g.get("rashi_num", 0)
        if not g_rashi:
            continue
        graha_hi = {"Moon": "चन्द्रमा", "Jupiter": "बृहस्पति", "Mercury": "बुध"}[graha_name]

        # Yuti (same rashi)
        if g_rashi == mars_rashi:
            bhang_reasons.append(f"मंगल {graha_hi} के साथ युति में है")
            continue

        # Drishti
        if _has_drishti(g_rashi, mars_rashi, graha_name):
            bhang_reasons.append(f"{graha_hi} की दृष्टि मंगल पर है")

    # ---- Rule 4: Strong Guru/Shukra in Lagna/7th ----
    # (Lagna/7th of this reference — so from ref_rashi, count 1st and 7th)
    lagna_rashi = ref_rashi
    saptam_rashi = ((ref_rashi - 1 + 6) % 12) + 1
    for graha_name in ["Jupiter", "Venus"]:
        g = planets_by_name.get(graha_name, {})
        g_rashi = g.get("rashi_num", 0)
        if g_rashi in (lagna_rashi, saptam_rashi):
            graha_hi = {"Jupiter": "बृहस्पति", "Venus": "शुक्र"}[graha_name]
            # Simple bali check — not in debilitation/shatru
            if _is_bali(graha_name, g.get("rashi_num", 0)):
                bhav_of = 1 if g_rashi == lagna_rashi else 7
                bhang_reasons.append(
                    f"बली {graha_hi} {BHAV_ORDINALS_HI[bhav_of]} भाव में स्थित है"
                )

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for r in bhang_reasons:
        if r not in seen:
            deduped.append(r)
            seen.add(r)

    result["bhang_reasons"] = deduped
    result["final_has_dosha"] = (len(deduped) == 0)
    return result


def _is_bali(graha_name: str, rashi_num: int) -> bool:
    """Simple strength check — not in debilitation or shatru rashi."""
    if graha_name == "Jupiter":
        # Debilitated in Makar (10); shatru: Vrishabh(2), Mithun(3), Kanya(6), Tula(7)
        return rashi_num not in [10, 2, 3, 6, 7]
    if graha_name == "Venus":
        # Debilitated in Kanya (6); shatru: Karka(4), Sinh(5)
        return rashi_num not in [6, 4, 5]
    return True


# -----------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------
def analyze_mangal_dosha(
    jatak_name: str,
    lagna_rashi_num: int,
    chandra_rashi_num: int,
    navamsha_lagna_rashi_num: int,
    mars_data: dict,
    navamsha_mars_rashi_num: int,
    planets_by_name: dict,
    mars_chalit_vishopak: float | None = None,
) -> dict:
    """
    Complete Mangal Dosha analysis.

    Args:
        jatak_name: Name of the native (for personalized output)
        lagna_rashi_num: 1-12, Ascendant rashi
        chandra_rashi_num: 1-12, Moon rashi
        navamsha_lagna_rashi_num: 1-12, D9 Ascendant rashi
        mars_data: {longitude, rashi_num, retrograde, ...} from /kundali planets
        navamsha_mars_rashi_num: 1-12, Mars rashi in D9
        planets_by_name: Full planets dict with rashi_num for each
        mars_chalit_vishopak: Vishopak Bal (0-20); if < 2 → sandhi in chalit

    Returns:
        Complete dosha analysis with personalized Hindi output.
    """
    mars_rashi = mars_data.get("rashi_num", 0)

    # Chalit sandhi check — vishopak_bal < 2.0 means very close to sandhi
    is_chalit_sandhi = (
        mars_chalit_vishopak is not None and mars_chalit_vishopak < 2.0
    )

    # Check from all 3 references
    checks = []

    # From Lagna
    checks.append(_check_single_reference(
        "लग्न", lagna_rashi_num, mars_rashi,
        planets_by_name, mars_data, is_chalit_sandhi,
    ))

    # From Chandra (uses same mars position, just different ref)
    checks.append(_check_single_reference(
        "चन्द्र राशि", chandra_rashi_num, mars_rashi,
        planets_by_name, mars_data, is_chalit_sandhi,
    ))

    # From Navamsha — uses navamsha Mars rashi
    navamsha_check = _check_single_reference(
        "नवमांश लग्न", navamsha_lagna_rashi_num, navamsha_mars_rashi_num,
        planets_by_name, mars_data, is_chalit_sandhi,
    )
    checks.append(navamsha_check)

    # Final verdict: dosha only if it exists in ALL 3 references after bhang
    active_dosha_refs = [c for c in checks if c["final_has_dosha"]]
    has_final_dosha = len(active_dosha_refs) > 0

    # Build personalized summary
    name = jatak_name or "जातक"
    if not has_final_dosha:
        dosha_placements = [c for c in checks if c["has_dosha_from_placement"]]
        if not dosha_placements:
            summary = (
                f"{name} की कुण्डली में मंगल किसी भी सन्दर्भ से 1, 4, 7, 8, 12 "
                f"भाव में नहीं है। अतः मंगल दोष नहीं है।"
            )
            verdict = "no_dosha"
        else:
            summary = (
                f"{name} की कुण्डली में मंगल दोष नहीं है। "
                f"{len(dosha_placements)} सन्दर्भ से दोष बन रहा था, परन्तु शास्त्रीय "
                f"भंग नियमों के अनुसार समाप्त हो गया है।"
            )
            verdict = "cancelled"
    else:
        summary = (
            f"{name} की कुण्डली में मंगल दोष है। "
            f"{len(active_dosha_refs)} सन्दर्भ से दोष सक्रिय है।"
        )
        verdict = "active"

    return {
        "jatak_name": name,
        "has_mangal_dosha": has_final_dosha,
        "verdict": verdict,
        "summary": summary,
        "checks": checks,
        "mars_position": {
            "rashi": RASHI_NAMES_HI[mars_rashi] if mars_rashi else "",
            "rashi_num": mars_rashi,
            "longitude": mars_data.get("longitude"),
            "retrograde": mars_data.get("retrograde", False),
            "chalit_vishopak": mars_chalit_vishopak,
            "in_chalit_sandhi": is_chalit_sandhi,
        },
        "references_used": ["लग्न", "चन्द्र राशि", "नवमांश लग्न"],
    }


# -----------------------------------------------------------------
# Self-test
# -----------------------------------------------------------------
def _test():
    """Test with the example birth: 4 May 1979 Mumbai."""
    # From earlier kundali call: Lagna Mesh (1), Mars in Meena (12)
    planets = {
        "Sun": {"rashi_num": 1, "longitude": 19.40, "retrograde": False},
        "Moon": {"rashi_num": 4, "longitude": 107.62, "retrograde": False},
        "Mars": {"rashi_num": 12, "longitude": 357.22, "retrograde": False},
        "Mercury": {"rashi_num": 12, "longitude": 355.48, "retrograde": False},
        "Jupiter": {"rashi_num": 4, "longitude": 94.0, "retrograde": False},
        "Venus": {"rashi_num": 2, "longitude": 35.0, "retrograde": False},
        "Saturn": {"rashi_num": 5, "longitude": 130.0, "retrograde": False},
    }

    result = analyze_mangal_dosha(
        jatak_name="टेस्ट जातक",
        lagna_rashi_num=1,  # Mesh lagna (early morning birth)
        chandra_rashi_num=4,  # Karka
        navamsha_lagna_rashi_num=1,  # assume same for test
        mars_data=planets["Mars"],
        navamsha_mars_rashi_num=12,
        planets_by_name=planets,
        mars_chalit_vishopak=5.0,  # not in sandhi
    )

    print("=" * 70)
    print(f"Has Mangal Dosha: {result['has_mangal_dosha']}")
    print(f"Verdict: {result['verdict']}")
    print(f"Summary: {result['summary']}")
    print("-" * 70)
    for c in result["checks"]:
        print(f"\n[{c['reference']}] Bhav: {c['bhav']} ({c['bhav_name']})")
        print(f"  Dosha from placement: {c['has_dosha_from_placement']}")
        print(f"  Final dosha: {c['final_has_dosha']}")
        if c["bhang_reasons"]:
            print("  Bhang reasons:")
            for r in c["bhang_reasons"]:
                print(f"    • {r}")
    print("=" * 70)


if __name__ == "__main__":
    _test()
