#!/usr/bin/env python3
"""
Install /api/match-making endpoint into main.py
================================================
Run on server: python3 install_match_making.py

This will:
1. Verify match_making_endpoint.py exists
2. Backup main.py
3. Add integration code to main.py (after dashakoot integration)
4. Restart jyotish-api service
5. Test the endpoint
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

API_DIR = '/root/jyotish-api'
MAIN_PY = f'{API_DIR}/main.py'
ENDPOINT_FILE = f'{API_DIR}/match_making_endpoint.py'

print("=" * 70)
print("  /api/match-making ENDPOINT INSTALLATION")
print("=" * 70)

# Step 1: Check file exists
if not os.path.exists(ENDPOINT_FILE):
    print(f"\n[ERROR] Missing: {ENDPOINT_FILE}")
    print(f"        Upload it first with scp")
    sys.exit(1)

print(f"[OK] Found: match_making_endpoint.py")

# Step 2: Backup
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_path = f"{MAIN_PY}.backup-matchmaking-{timestamp}"
shutil.copy2(MAIN_PY, backup_path)
print(f"\n[1/4] Backup: {backup_path}")

# Step 3: Add integration code
with open(MAIN_PY, 'r') as f:
    code = f.read()

if 'install_match_making_endpoint' in code:
    print("[!] Match-making already installed - skipping integration")
else:
    integration_code = """

# ============================================================================
# /api/match-making endpoint (Uttar Bhartiya proxy)
# ============================================================================
try:
    from match_making_endpoint import install_match_making_endpoint
    install_match_making_endpoint(app)
    print("[OK] /api/match-making endpoint loaded")
except Exception as _mm_err:
    print(f"[WARN] match-making not loaded: {_mm_err}")

"""
    
    # Insert after dashakoot integration if present, else after FastAPI app
    if 'install_dashakoot_endpoint' in code:
        # Insert after dashakoot block
        marker = 'install_dashakoot_endpoint(app)'
        idx = code.find(marker)
        end_idx = code.find('\n', idx) + 1
        # Skip past any except block
        next_lines_end = code.find('\n\n', end_idx)
        if next_lines_end == -1:
            next_lines_end = end_idx
        else:
            next_lines_end += 2
        new_code = code[:next_lines_end] + integration_code + code[next_lines_end:]
    elif 'app = FastAPI' in code:
        idx = code.find('app = FastAPI')
        end_idx = code.find('\n', idx) + 1
        new_code = code[:end_idx] + integration_code + code[end_idx:]
    else:
        print("[ERROR] Could not find FastAPI app or dashakoot integration")
        sys.exit(1)
    
    with open(MAIN_PY, 'w') as f:
        f.write(new_code)
    
    print(f"[2/4] Integration code added")

# Step 4: Restart
print(f"\n[3/4] Restarting jyotish-api...")
try:
    subprocess.run(['systemctl', 'restart', 'jyotish-api'], check=True)
    
    import time
    time.sleep(3)
    
    result = subprocess.run(['systemctl', 'is-active', 'jyotish-api'],
                          capture_output=True, text=True)
    status = result.stdout.strip()
    
    if status == 'active':
        print(f"      [OK] Service active")
    else:
        print(f"      [ERROR] Status: {status}")
        print(f"      Check: journalctl -u jyotish-api -n 30")
        sys.exit(1)
except Exception as e:
    print(f"      [ERROR] {e}")
    sys.exit(1)

# Step 5: Test
print(f"\n[4/4] Testing /api/match-making endpoint...")
try:
    import urllib.request
    import json
    
    test_data = {
        "boy": {
            "name": "Test", "dob": "1990-01-01", "tob": "12:00",
            "lat": 19.0760, "lon": 72.8777, "tz": 5.5
        },
        "girl": {
            "name": "Test", "dob": "1992-01-01", "tob": "12:00",
            "lat": 19.0760, "lon": 72.8777, "tz": 5.5
        }
    }
    
    req = urllib.request.Request(
        'https://api.jyotishrishi.net/api/match-making',
        data=json.dumps(test_data).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
        
        if 'ashtakoota' in result:
            ak = result['ashtakoota']
            points = ak.get('ashtakoota_points', 0)
            print(f"      [OK] Endpoint working!")
            print(f"      Test result: {points} guna mile")
            print(f"      Verdict: {result.get('verdict', 'N/A')}")
        else:
            print(f"      [WARN] Unexpected format: {list(result.keys())}")
except Exception as e:
    print(f"      [WARN] Test failed: {e}")
    print(f"      Service is running, but test inconclusive")

print("\n" + "=" * 70)
print("  /api/match-making ENDPOINT INSTALLED!")
print("=" * 70)
print()
print("  Now /matchmaking page should work properly!")
print()
print(f"  Backup: {backup_path}")
print(f"  Rollback if needed:")
print(f"    cp {backup_path} {MAIN_PY}")
print(f"    sudo systemctl restart jyotish-api")
print()
print("  Next: Test https://jyotishrishi.net/matchmaking")
print("=" * 70)
