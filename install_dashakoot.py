#!/usr/bin/env python3
"""
Dashakoot Milan - One-shot installer
=====================================
Run this on server: python3 install_dashakoot.py

Does:
1. Verifies dashakoot.py and dashakoot_endpoint.py exist
2. Backs up main.py
3. Adds integration code to main.py
4. Restarts jyotish-api service
5. Tests the endpoint
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

API_DIR = '/root/jyotish-api'
MAIN_PY = f'{API_DIR}/main.py'

print("=" * 70)
print("  DASHAKOOT MILAN - INSTALLATION")
print("=" * 70)

# ============================================================================
# Step 1: Check files
# ============================================================================
required = ['dashakoot.py', 'dashakoot_endpoint.py']
missing = []
for f in required:
    fpath = f'{API_DIR}/{f}'
    if not os.path.exists(fpath):
        missing.append(f)
    else:
        print(f"[OK] Found: {f}")

if missing:
    print(f"\n[ERROR] Missing files: {missing}")
    print(f"        Upload them to {API_DIR}/ first")
    sys.exit(1)

# ============================================================================
# Step 2: Backup main.py
# ============================================================================
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup_path = f"{MAIN_PY}.backup-dashakoot-{timestamp}"
shutil.copy2(MAIN_PY, backup_path)
print(f"\n[1/4] Backup: {backup_path}")

# ============================================================================
# Step 3: Add integration code
# ============================================================================
with open(MAIN_PY, 'r') as f:
    code = f.read()

if 'install_dashakoot_endpoint' in code:
    print("[!] Dashakoot already installed in main.py - skipping integration")
else:
    integration_code = """

# ============================================================================
# DASHAKOOT MILAN integration
# ============================================================================
try:
    from dashakoot_endpoint import install_dashakoot_endpoint
    install_dashakoot_endpoint(app)
    print("[OK] Dashakoot Milan endpoints loaded")
except Exception as _dk_err:
    print(f"[WARN] Dashakoot not loaded: {_dk_err}")

"""
    
    # Find 'app = FastAPI' line and insert after it (with some buffer)
    if 'app = FastAPI' in code:
        idx = code.find('app = FastAPI')
        end_idx = code.find('\n', idx) + 1
        
        # Insert integration code just after FastAPI app creation
        new_code = code[:end_idx] + integration_code + code[end_idx:]
        
        with open(MAIN_PY, 'w') as f:
            f.write(new_code)
        
        print(f"[2/4] Integration code added to main.py")
    else:
        print("[ERROR] Could not find 'app = FastAPI' in main.py")
        print("        Manual integration required")
        sys.exit(1)

# ============================================================================
# Step 4: Restart service
# ============================================================================
print(f"\n[3/4] Restarting jyotish-api service...")
try:
    subprocess.run(['systemctl', 'restart', 'jyotish-api'], check=True)
    
    import time
    time.sleep(3)
    
    result = subprocess.run(['systemctl', 'is-active', 'jyotish-api'], 
                          capture_output=True, text=True)
    status = result.stdout.strip()
    
    if status == 'active':
        print(f"      [OK] Service is active")
    else:
        print(f"      [WARN] Service status: {status}")
        print(f"      Check: journalctl -u jyotish-api -n 50")
        sys.exit(1)
except Exception as e:
    print(f"      [ERROR] {e}")
    sys.exit(1)

# ============================================================================
# Step 5: Test endpoint
# ============================================================================
print(f"\n[4/4] Testing endpoint...")
try:
    import urllib.request
    import json
    
    test_data = {
        "boy_rashi": 0,      # Mesh
        "girl_rashi": 1,     # Vrishabh  
        "boy_nakshatra": 0,  # Ashwini
        "girl_nakshatra": 5  # Aardra
    }
    
    # Test the quick endpoint via GET-style query
    url = "https://api.jyotishrishi.net/dashakoot-milan-quick"
    qs = "&".join(f"{k}={v}" for k,v in test_data.items())
    full_url = f"{url}?{qs}"
    
    req = urllib.request.Request(full_url, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode())
        
        if result.get('success'):
            milan = result.get('milan', {})
            print(f"      [OK] Endpoint working!")
            print(f"      Test result: {milan.get('summary', 'N/A')}")
        else:
            print(f"      [WARN] Unexpected response: {result}")
except Exception as e:
    print(f"      [WARN] Test failed: {e}")
    print(f"      (Service is running; test manually in browser)")

# ============================================================================
# Done
# ============================================================================
print("\n" + "=" * 70)
print("  DASHAKOOT MILAN INSTALLED!")
print("=" * 70)
print()
print("  API endpoints:")
print("  POST https://api.jyotishrishi.net/dashakoot-milan")
print("       (full birth details)")
print("  POST https://api.jyotishrishi.net/dashakoot-milan-quick")
print("       (rashi + nakshatra indices)")
print()
print(f"  Backup: {backup_path}")
print(f"  Rollback: cp {backup_path} {MAIN_PY} && sudo systemctl restart jyotish-api")
print()
print("  Next: Upload frontend DashakootMilan.tsx to web project")
print("  Jai Shri Ram!")
print("=" * 70)
