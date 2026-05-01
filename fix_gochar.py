#!/usr/bin/env python3
"""
Jyotishrishi - Classical Vedic Gochar Fix
==========================================
Author: Generated for Harishchandra Purohit
Date: 2026-04-25
Launch: 2026-04-26 (kal sham 6 baje)

This script fixes the off-by-one bug in astro_additions.py and applies
classical Brihat Parashara rules for:
- Saturn (Sade Sati & Dhaiya): bhav 12, 1, 2 = Sade Sati | bhav 4, 8 = Dhaiya
- Jupiter (Guru Gochar): bhav 2, 5, 7, 9, 11 = Shubh
- Rahu Gochar: bhav 3, 6, 10, 11 = Shubh

Usage:
    cd /root/jyotish-api
    python3 fix_gochar.py
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

FILE = '/root/jyotish-api/astro_additions.py'

# ============================================================================
# Step 1: Verify file exists
# ============================================================================
if not os.path.exists(FILE):
    print(f"ERROR: {FILE} not found!")
    print("Make sure you are in /root/jyotish-api directory")
    sys.exit(1)

print("=" * 70)
print("  JYOTISHRISHI - CLASSICAL VEDIC GOCHAR FIX")
print("=" * 70)

# ============================================================================
# Step 2: Create timestamped backup
# ============================================================================
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_path = f"{FILE}.backup-classical-{timestamp}"
shutil.copy2(FILE, backup_path)
print(f"\n[1/5] Backup created:")
print(f"      {backup_path}")

# ============================================================================
# Step 3: Read current code
# ============================================================================
with open(FILE, 'r') as f:
    code = f.read()

print(f"\n[2/5] Reading current code... ({len(code)} chars)")

# ============================================================================
# Step 4: Define old and new blocks
# ============================================================================

# OLD BLOCK 1: Saturn + Jupiter + Rahu sections (with bugs)
OLD_BLOCK = '''    # Saturn — Sade Sati & Dhaya
    saturn_sign = transit_positions['Saturn']['rashi_num']
    saturn_diff = (saturn_sign - moon_sign) % 12
    if saturn_diff == 0:
        sade_sati = "Peak Sade Sati (Chandra pe Shani)"
    elif saturn_diff == 11:
        sade_sati = "Sade Sati Start (12th se)"
    elif saturn_diff == 1:
        sade_sati = "Sade Sati End (2nd mein)"
    elif saturn_diff == 4:
        sade_sati = "Ardha Sade Sati (Dhaya) — 4th Shani"
    elif saturn_diff == 7:
        sade_sati = "Ardha Sade Sati (Dhaya) — 7th Shani"
    else:
        sade_sati = "Normal — Sade Sati nahi"

    results['sade_sati'] = {
        'status': sade_sati,
        'saturn_rashi': transit_positions['Saturn']['rashi'],
        'moon_rashi': RASHI_NAMES[(moon_sign - 1) % 12],
        'tip': "Shani ki pooja karein, Shanivaar ko tel daan karein" if "Sade Sati" in sade_sati or "Dhaya" in sade_sati else "Koi vishesh upay ki zaroorat nahi"
    }

    # Jupiter — Guru Gochar
    guru_sign = transit_positions['Jupiter']['rashi_num']
    guru_diff = (guru_sign - moon_sign) % 12
    if guru_diff in [1, 4, 7, 10]:
        guru_status = "Shubh — Guru anukoola sthiti mein"
    elif guru_diff in [3, 6, 8, 12]:
        guru_status = "Madhyam — Guru ka saadharan prabhav"
    else:
        guru_status = "Prabal — Guru ka vishesh prabhav"

    results['guru_gochar'] = {
        'status': guru_status,
        'jupiter_rashi': transit_positions['Jupiter']['rashi'],
        'diff_house': ((guru_sign - moon_sign) % 12) + 1,
    }

    # Rahu-Ketu axis
    rahu_sign = transit_positions['Rahu']['rashi_num']
    rahu_diff = (rahu_sign - moon_sign) % 12
    if rahu_diff in [1, 5, 9]:
        rahu_status = "Shubh Rahu sthiti"
    elif rahu_diff in [8, 12, 4]:
        rahu_status = "Rahu se savdhaan — unexpected changes possible"
    else:
        rahu_status = "Normal Rahu sthiti"

    results['rahu_ketu'] = {
        'status': rahu_status,
        'rahu_rashi': transit_positions['Rahu']['rashi'],
        'ketu_rashi': transit_positions['Ketu']['rashi'],
    }'''

# NEW BLOCK 1: Classical Brihat Parashara fix
NEW_BLOCK = '''    # Saturn - Sade Sati & Dhaiya (CLASSICAL Brihat Parashara)
    # Sade Sati: bhav 12, 1, 2 | Dhaiya: bhav 4 (Kantak), bhav 8 (Ashtam)
    saturn_sign = transit_positions['Saturn']['rashi_num']
    saturn_bhav = ((saturn_sign - moon_sign) % 12) + 1

    if saturn_bhav == 12:
        sade_sati = "Sade Sati Phase 1 - 12th Shani (vyaya, dhairya rakhein)"
    elif saturn_bhav == 1:
        sade_sati = "Sade Sati Peak - Chandra pe Shani (sabse kathin phase)"
    elif saturn_bhav == 2:
        sade_sati = "Sade Sati Phase 3 - 2nd Shani (dhana hani savdhaan)"
    elif saturn_bhav == 4:
        sade_sati = "Kantak Shani / Ardha Dhaiya - 4th bhav (sukh, vahan)"
    elif saturn_bhav == 8:
        sade_sati = "Ashtam Shani / Dhaiya - 8th bhav (rog, vyaya)"
    else:
        sade_sati = "Normal - Sade Sati ya Dhaiya nahi"

    is_kasht = saturn_bhav in [12, 1, 2, 4, 8]
    results['sade_sati'] = {
        'status': sade_sati,
        'saturn_rashi': transit_positions['Saturn']['rashi'],
        'moon_rashi': RASHI_NAMES[(moon_sign - 1) % 12],
        'saturn_bhav': saturn_bhav,
        'is_kasht': is_kasht,
        'tip': "Shanivaar ko tel daan, Shani chalisa, Hanuman puja karein" if is_kasht else "Koi vishesh upay ki zaroorat nahi"
    }

    # Jupiter - Guru Gochar (CLASSICAL Brihat Parashara)
    # Shubh: 2,5,7,9,11 | Ashubh: 3,6,10 | Madhyam: 1,4,8,12
    guru_sign = transit_positions['Jupiter']['rashi_num']
    guru_bhav = ((guru_sign - moon_sign) % 12) + 1

    if guru_bhav in [2, 5, 7, 9, 11]:
        guru_status = "Shubh Guru Gochar - " + str(guru_bhav) + "th bhav (anukool sthiti)"
        guru_is_shubh = True
    elif guru_bhav in [3, 6, 10]:
        guru_status = "Ashubh Guru Gochar - " + str(guru_bhav) + "th bhav (vighna sambhav)"
        guru_is_shubh = False
    else:
        guru_status = "Madhyam Guru Gochar - " + str(guru_bhav) + "th bhav (saadharan prabhav)"
        guru_is_shubh = False

    results['guru_gochar'] = {
        'status': guru_status,
        'jupiter_rashi': transit_positions['Jupiter']['rashi'],
        'diff_house': guru_bhav,
        'bhav': guru_bhav,
        'is_shubh': guru_is_shubh,
    }

    # Rahu-Ketu Gochar (CLASSICAL - Rahu shubh: 3,6,10,11)
    rahu_sign = transit_positions['Rahu']['rashi_num']
    rahu_bhav = ((rahu_sign - moon_sign) % 12) + 1
    ketu_bhav = ((rahu_bhav + 5) % 12) + 1

    if rahu_bhav in [3, 6, 10, 11]:
        rahu_status = "Shubh Rahu - " + str(rahu_bhav) + "th bhav (saahas, labh, karm vriddhi)"
    elif rahu_bhav in [1, 5, 9]:
        rahu_status = "Ashubh Rahu - " + str(rahu_bhav) + "th bhav (savdhaan rahein)"
    else:
        rahu_status = "Madhyam Rahu - " + str(rahu_bhav) + "th bhav (saadharan prabhav)"

    results['rahu_ketu'] = {
        'status': rahu_status,
        'rahu_rashi': transit_positions['Rahu']['rashi'],
        'ketu_rashi': transit_positions['Ketu']['rashi'],
        'rahu_bhav': rahu_bhav,
        'ketu_bhav': ketu_bhav,
    }'''

# OLD SUMMARY BLOCK
OLD_SUMMARY = '''    # Overall summary
    all_statuses = [results['sade_sati']['status'], results['guru_gochar']['status']]
    if any('Sade Sati' in s or 'Dhaya' in s for s in all_statuses):
        overall = "Kashtkaal — Dhairya rakhen, Shani upay karein"
    elif 'Shubh' in results['guru_gochar']['status']:
        overall = "Shubh kaal — Naye kaam shuru karne ka sahi samay"
    else:
        overall = "Madhyam kaal — Sambhal ke chalein"'''

# NEW SUMMARY BLOCK
NEW_SUMMARY = '''    # Overall summary (CLASSICAL based)
    is_kasht_flag = results['sade_sati'].get('is_kasht', False)
    is_guru_shubh_flag = results['guru_gochar'].get('is_shubh', False)

    if is_kasht_flag and not is_guru_shubh_flag:
        overall = "Kashtkaal - Dhairya rakhein, Shani upay zaroor karein"
    elif is_kasht_flag and is_guru_shubh_flag:
        overall = "Mishrit kaal - Shani kasht hai par Guru raksha kar rahe hain"
    elif is_guru_shubh_flag:
        overall = "Shubh kaal - Naye kaam shuru karne ka sahi samay"
    else:
        overall = "Madhyam kaal - Sambhal ke chalein, dhairya rakhein"'''

# ============================================================================
# Step 5: Apply replacements
# ============================================================================
print(f"\n[3/5] Applying classical fix...")

changes = 0
if OLD_BLOCK in code:
    code = code.replace(OLD_BLOCK, NEW_BLOCK)
    changes += 1
    print("      [OK] Saturn/Jupiter/Rahu blocks replaced")
else:
    print("      [WARN] Saturn/Jupiter/Rahu old block not found exactly")
    print("            (may have been partially modified - check manually)")

if OLD_SUMMARY in code:
    code = code.replace(OLD_SUMMARY, NEW_SUMMARY)
    changes += 1
    print("      [OK] Overall summary replaced")
else:
    print("      [WARN] Summary old block not found - skipping")

if changes == 0:
    print("\n[ERROR] No changes applied! File may already be fixed or modified differently.")
    print(f"        Backup saved at: {backup_path}")
    print("        Original file untouched.")
    sys.exit(1)

# Write back
with open(FILE, 'w') as f:
    f.write(code)

print(f"\n[4/5] File saved with {changes} replacement(s)")

# ============================================================================
# Step 6: Restart service
# ============================================================================
print(f"\n[5/5] Restarting jyotish-api service...")
try:
    subprocess.run(['systemctl', 'restart', 'jyotish-api'], check=True)
    print("      [OK] Service restarted")
    
    import time
    time.sleep(3)
    
    result = subprocess.run(['systemctl', 'is-active', 'jyotish-api'], 
                          capture_output=True, text=True)
    if result.stdout.strip() == 'active':
        print("      [OK] Service is active and running")
    else:
        print(f"      [WARN] Service status: {result.stdout.strip()}")
        print("              Check: systemctl status jyotish-api")
except Exception as e:
    print(f"      [ERROR] Could not restart: {e}")
    print("      Run manually: sudo systemctl restart jyotish-api")

# ============================================================================
# Done!
# ============================================================================
print("\n" + "=" * 70)
print("  CLASSICAL FIX APPLIED SUCCESSFULLY!")
print("=" * 70)
print()
print("  Verify in browser:")
print("  1. Open: https://jyotishrishi.net/gochar")
print("  2. Hard refresh: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)")
print("  3. Check Guru Gochar shows correct bhav (12 for Mithun-Kark)")
print()
print(f"  Backup location:")
print(f"  {backup_path}")
print()
print("  To rollback if needed:")
print(f"  cp {backup_path} {FILE}")
print(f"  sudo systemctl restart jyotish-api")
print()
print("  Jai Shri Ram! Shubh launch tomorrow!")
print("=" * 70)
