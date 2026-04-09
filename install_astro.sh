#!/bin/bash
# ================================================================
# JyotishRishi API — Astro Opinion Ultimate Install Script
# DigitalOcean server pe chalao: bash install_astro.sh
# ================================================================

echo "🚀 Astro Opinion Ultimate — Installing..."

# Step 1 — File copy karo
cp /tmp/astro_additions.py /root/jyotish-api/astro_additions.py
echo "✅ astro_additions.py copied"

# Step 2 — main.py mein router add karo
cd /root/jyotish-api

# Check if already added
if grep -q "astro_additions" main.py; then
    echo "⚠️  Already added — skipping"
else
    # main.py ke end mein router include karo
    python3 - << 'PYEOF'
content = open('main.py').read()

# Add import at top
if 'from astro_additions import router as astro_router' not in content:
    content = 'from astro_additions import router as astro_router\n' + content

# Add router include before last line
if 'app.include_router(astro_router)' not in content:
    content = content.rstrip() + '\n\napp.include_router(astro_router)\n'

open('main.py', 'w').write(content)
print("✅ main.py updated")
PYEOF
fi

# Step 3 — Restart service
systemctl restart jyotish-api
sleep 2
systemctl status jyotish-api --no-pager | head -5

echo ""
echo "🎉 Done! Test karo:"
echo "curl -X POST http://139.59.43.115:8000/gochar -H 'Content-Type: application/json' -d '{\"moon_sign\": 5}'"
echo "curl -X POST http://139.59.43.115:8000/muhurat -H 'Content-Type: application/json' -d '{\"tithi\": 5, \"nakshatra\": \"Rohini\", \"weekday\": \"Monday\"}'"
echo "curl -X POST http://139.59.43.115:8000/ai-prediction -H 'Content-Type: application/json' -d '{\"dob\": \"1979-05-04\", \"tob\": \"23:55\", \"lat\": 19.076, \"lon\": 72.877, \"tz\": 5.5}'"
