"""
NAADI CORRECTION PATCH
=======================
Critical fix for classical Naadi mapping

Apply this on server:
  cd /root/jyotish-api
  python3 fix_naadi.py

This will:
1. Backup current dashakoot.py
2. Replace NAADI_MAP with correct classical mapping
3. Restart service
"""

import shutil
from datetime import datetime

DASHAKOOT_FILE = '/root/jyotish-api/dashakoot.py'

# Backup
backup = f"{DASHAKOOT_FILE}.before-naadi-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(DASHAKOOT_FILE, backup)
print(f"[1/3] Backup: {backup}")

# Read
with open(DASHAKOOT_FILE, 'r') as f:
    code = f.read()

# OLD wrong mapping
old_naadi = "NAADI_MAP = ['Adi', 'Madhya', 'Antya'] * 9"

# NEW correct mapping
new_naadi = """# Classical Naadi mapping (PURVA KALAMRUTAM authority)
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
]"""

if old_naadi in code:
    code = code.replace(old_naadi, new_naadi)
    with open(DASHAKOOT_FILE, 'w') as f:
        f.write(code)
    print(f"[2/3] NAADI_MAP corrected!")
else:
    # Check if already fixed
    if "Adi',      # 0  - Ashwini" in code:
        print("[!] Already fixed - no change needed")
    else:
        print("[ERROR] Could not find NAADI_MAP pattern!")
        print("        Manual fix required")
        exit(1)

# Restart
import subprocess
print(f"[3/3] Restarting jyotish-api...")
subprocess.run(['sudo', 'systemctl', 'restart', 'jyotish-api'], check=True)

import time
time.sleep(3)

result = subprocess.run(['sudo', 'systemctl', 'is-active', 'jyotish-api'],
                       capture_output=True, text=True)
status = result.stdout.strip()
if status == 'active':
    print(f"      [OK] Service active")
else:
    print(f"      [WARN] Status: {status}")

print("\n" + "="*60)
print("  NAADI FIX APPLIED!")
print("="*60)
print(f"  Test: Ashlesha + Shravan should now show Antya-Antya (Dosha!)")
print(f"  Backup: {backup}")
print(f"  Rollback if needed:")
print(f"    cp {backup} {DASHAKOOT_FILE}")
print(f"    sudo systemctl restart jyotish-api")
print("="*60)
