"""
Dashakoot Patch — adds Mahendra + Stridirgha + Naadi Bhang + Bhakoot Bhang
Classical logic from Muhurta Chintamani / Purva Kalamrutam
"""

# ═══ BHANG NAKSHATRAS (Purva Kalamrutam page 91-92) ═══
NAADI_BHANG_NAKSHATRAS = {
    'Vishakha','Anuradha','Dhanishtha','Revati','Hasta','Swati',
    'Ardra','Purva Bhadrapada','Uttara Bhadrapada','Rohini',
    'Shravana','Pushya','Magha'
}

# Mahendra favorable counts (classical: 4,7,10,13,16,19,22,25)
MAHENDRA_FAVORABLE = {4,7,10,13,16,19,22,25}


def _mahendra_score(boy_nak, girl_nak):
    """Mahendra Koot — 1 point. Counting from boy's nakshatra to girl's."""
    count = ((girl_nak - boy_nak) % 27) + 1
    if count in MAHENDRA_FAVORABLE:
        return 1, f"नक्षत्र गणना {count} — शुभ (परस्पर प्रेम)"
    return 0, f"नक्षत्र गणना {count} — अशुभ (प्रेम में कमी)"


def _stridirgha_score(boy_nak, girl_nak):
    """Stridirgha Koot — 3 points. Girl's nakshatra should be far from boy's."""
    count = ((girl_nak - boy_nak) % 27) + 1
    if count >= 14:
        return 3, f"नक्षत्र दूरी {count} — पूर्ण शुभ (वैवाहिक दीर्घता)"
    elif count >= 9:
        return 1.5, f"नक्षत्र दूरी {count} — मध्यम"
    return 0, f"नक्षत्र दूरी {count} — अशुभ (दूरी कम)"


def _naadi_bhang_check(boy_nak_name, girl_nak_name, br, gr, bn, gn, RL_arr, PF_arr):
    """Returns list of bhang reasons if same naadi"""
    bhang = []
    # 1. Same nakshatra (charana bhed)
    if bn == gn:
        bhang.append("एक ही नक्षत्र — चरण भेद से दोष शान्त")
    # 2. Same rashi different nakshatra
    if br == gr and bn != gn:
        bhang.append("एक राशि परन्तु भिन्न नक्षत्र — दोष शान्त")
    # 3. Special bhang nakshatras
    if boy_nak_name in NAADI_BHANG_NAKSHATRAS:
        bhang.append(f"वर का नक्षत्र ({boy_nak_name}) नाड़ी दोष भंग करता है")
    if girl_nak_name in NAADI_BHANG_NAKSHATRAS:
        bhang.append(f"वधु का नक्षत्र ({girl_nak_name}) नाड़ी दोष भंग करता है")
    # 4. Same rashi lord
    if RL_arr[br] == RL_arr[gr]:
        bhang.append(f"दोनों राशियों का स्वामी एक ही — दोष शान्त")
    # 5. Rashi lords friends
    elif PF_arr[RL_arr[br]][RL_arr[gr]] == 2 and PF_arr[RL_arr[gr]][RL_arr[br]] == 2:
        bhang.append("राशीश परस्पर मित्र — विशेष अनिष्टकारक नहीं")
    return bhang


def _bhakoot_bhang_check(br, gr, RL_arr, PF_arr):
    """Returns list of bhakoot bhang reasons"""
    bhang = []
    if RL_arr[br] == RL_arr[gr]:
        bhang.append("दोनों राशियों का स्वामी एक ही — भकूट दोष शान्त")
    elif PF_arr[RL_arr[br]][RL_arr[gr]] == 2 and PF_arr[RL_arr[gr]][RL_arr[br]] == 2:
        bhang.append("राशीश परस्पर मित्र — भकूट दोष शान्त")
    return bhang


def calculate_dashakoot(boy_nak, girl_nak,
                        NR, RV, RVA, VC, NG, GC, NN, NY, YE, RL, PF,
                        VARNA_N, VASHYA_N, GANA_N, NADI_N, YONI_N,
                        PLANET_N, NAKSHATRA_NAMES, RASHI_NAMES,
                        yoni_fn, maitri_fn, tara_fn, bhakoot_fn, bhakoot_dosha_fn):
    """Full Dashakoot — 10 koots, 40 points, classical bhang"""
    bn, gn = boy_nak, girl_nak
    br, gr = NR[bn], NR[gn]
    boy_nak_name = NAKSHATRA_NAMES[bn]
    girl_nak_name = NAKSHATRA_NAMES[gn]
    
    # Standard 8 koots
    bVa, gVa = RV[br], RV[gr]
    varna = 1 if bVa >= gVa else 0
    bVs, gVs = RVA[br], RVA[gr]
    vashya = VC[bVs][gVs]
    tara = tara_fn(bn, gn)
    bY, gY = NY[bn], NY[gn]
    yoni = yoni_fn(bY, gY)
    maitri = maitri_fn(br, gr)
    bG, gG = NG[bn], NG[gn]
    gana = GC[bG][gG]
    bhakoot = bhakoot_fn(br, gr)
    bhakoot_dosha = bhakoot_dosha_fn(br, gr)
    bN, gN = NN[bn], NN[gn]
    nadi = 0 if bN == gN else 8
    nadi_dosha = bN == gN
    
    # NEW: Mahendra + Stridirgha
    mahendra, mahendra_phal = _mahendra_score(bn, gn)
    stridirgha, stridirgha_phal = _stridirgha_score(bn, gn)
    
    # Bhang checks
    naadi_bhang = _naadi_bhang_check(boy_nak_name, girl_nak_name, br, gr, bn, gn, RL, PF) if nadi_dosha else []
    bhakoot_bhang = _bhakoot_bhang_check(br, gr, RL, PF) if bhakoot_dosha else []
    
    # Total out of 40
    total = varna + vashya + tara + yoni + maitri + gana + bhakoot + nadi + mahendra + stridirgha
    
    md = []
    if nadi_dosha:
        md.append('Nadi Dosha' + (' (भंग)' if naadi_bhang else ''))
    if bhakoot_dosha:
        md.append(f'Bhakoot Dosha ({bhakoot_dosha})' + (' (भंग)' if bhakoot_bhang else ''))
    if gana == 0:
        md.append('Gana Dosha')
    if mahendra == 0:
        md.append('Mahendra Dosha')
    if stridirgha == 0:
        md.append('Stridirgha Dosha')
    
    # Verdict (out of 40)
    if total >= 36:
        verdict = 'Uttam Milan'
    elif total >= 30:
        verdict = 'Shubh Milan'
    elif total >= 24:
        verdict = 'Madhyam Milan'
    elif total >= 20:
        verdict = 'Sadhaaran Milan'
    else:
        verdict = 'Ashubh Milan'
    
    return {
        'dashakoota_points': total,
        'ashtakoota_points': total,  # backwards compat
        'max_points': 40,
        'verdict': verdict,
        'major_doshas': md,
        'naadi_bhang_conditions': naadi_bhang,
        'bhakoot_bhang_conditions': bhakoot_bhang,
        'ashtakoota': {
            'varna': {'male_koot': VARNA_N[bVa], 'female_koot': VARNA_N[gVa], 'received_points': varna, 'total_points': 1},
            'vashya': {'male_koot': VASHYA_N[bVs], 'female_koot': VASHYA_N[gVs], 'received_points': vashya, 'total_points': 2},
            'tara': {'male_koot': boy_nak_name, 'female_koot': girl_nak_name, 'received_points': tara, 'total_points': 3},
            'yoni': {'male_koot': YONI_N[bY], 'female_koot': YONI_N[gY], 'received_points': yoni, 'total_points': 4},
            'maitri': {'male_koot': f'{PLANET_N[RL[br]]} ({RASHI_NAMES[br]})', 'female_koot': f'{PLANET_N[RL[gr]]} ({RASHI_NAMES[gr]})', 'received_points': maitri, 'total_points': 5},
            'gana': {'male_koot': GANA_N[bG], 'female_koot': GANA_N[gG], 'received_points': gana, 'total_points': 6},
            'bhakoot': {'male_koot': RASHI_NAMES[br], 'female_koot': RASHI_NAMES[gr], 'received_points': bhakoot, 'total_points': 7, 'bhang': bhakoot_bhang},
            'nadi': {'male_koot': NADI_N[bN], 'female_koot': NADI_N[gN], 'received_points': nadi, 'total_points': 8, 'bhang': naadi_bhang},
            'mahendra': {'male_koot': boy_nak_name, 'female_koot': girl_nak_name, 'received_points': mahendra, 'total_points': 1, 'phaladesh': mahendra_phal},
            'stridirgha': {'male_koot': boy_nak_name, 'female_koot': girl_nak_name, 'received_points': stridirgha, 'total_points': 3, 'phaladesh': stridirgha_phal}
        }
    }
