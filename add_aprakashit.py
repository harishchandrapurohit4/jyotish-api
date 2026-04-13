content = open('/root/jyotish-api/main.py').read()

aprakashit_code = """
# ═══ APRAKASHIT GRAHAS (5 Surya Mahadosha) ═══
def get_aprakashit_grahas(sun_longitude):
    try:
        # 1. Dhoom = Sun + 4°13'20" = Sun + 4.2222°
        dhoom = (sun_longitude + 4.2222) % 360
        
        # 2. Vyatipaata = 12 Rashi (360) - Dhoom
        vyatipaata = (360 - dhoom) % 360
        
        # 3. Parivesh = Vyatipaata + 6 Rashi (180)
        parivesh = (vyatipaata + 180) % 360
        
        # 4. Indrachap = 12 Rashi (360) - Parivesh
        indrachap = (360 - parivesh) % 360
        
        # 5. Upaketu = Indrachap + 16°40' = 16.6667°
        upaketu = (indrachap + 16.6667) % 360
        
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
                   'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        
        def lon_to_rashi(lon):
            sign = int(lon / 30)
            degree = lon % 30
            d = int(degree)
            m = int((degree - d) * 60)
            return {'longitude': round(lon, 4), 'rashi': RASHI_N[sign], 
                    'rashi_num': sign + 1, 'degree': f\"{d}°{m}'\"}
        
        return {
            'dhoom': lon_to_rashi(dhoom),
            'vyatipaata': lon_to_rashi(vyatipaata),
            'parivesh': lon_to_rashi(parivesh),
            'indrachap': lon_to_rashi(indrachap),
            'upaketu': lon_to_rashi(upaketu),
            'note': 'Ye paanch Surya ke Mahadosha hain — Aprakashak Graha'
        }
    except Exception as e:
        return {'error': str(e)}

def get_gulik(jd, sunrise_jd, day_of_week, is_day_birth):
    try:
        import swisseph as swe
        # Day of week: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        # Gulik khand order for day: Sun=6, Mon=5, Tue=4, Wed=3, Thu=2, Fri=1, Sat=0
        # Each khand = daylight/8
        DAY_GULIK_KHAND = {0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0}
        NIGHT_GULIK_KHAND = {0:1, 1:0, 2:6, 3:5, 4:4, 5:3, 6:2}
        
        if is_day_birth:
            khand = DAY_GULIK_KHAND[day_of_week]
            day_duration = 0.5  # approximate 12 hours
            gulik_jd = sunrise_jd + (khand * day_duration / 8)
        else:
            khand = NIGHT_GULIK_KHAND[day_of_week]
            sunset_jd = sunrise_jd + 0.5
            night_duration = 0.5
            gulik_jd = sunset_jd + (khand * night_duration / 8)
        
        # Get lagna at gulik time
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(gulik_jd)
        # Simple approximation: use Sun position + time offset
        sun_lon = swe.calc_ut(gulik_jd, swe.SUN)[0][0]
        gulik_lon = (sun_lon - ayanamsa) % 360
        
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya',
                   'Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        sign = int(gulik_lon / 30)
        degree = gulik_lon % 30
        
        return {
            'gulik_lagna': RASHI_N[sign],
            'gulik_lagna_num': sign + 1,
            'gulik_degree': round(degree, 2),
            'khand': khand
        }
    except Exception as e:
        return {'error': str(e)}
"""

if 'get_aprakashit_grahas' not in content:
    content = content.replace(
        "def get_all_graha_avastha",
        aprakashit_code + "\ndef get_all_graha_avastha"
    )
    print("Aprakashit code added!")
else:
    print("Already exists!")

# Update kundali endpoint to include aprakashit
old = "        naam = getattr(data, 'name', '') or ''\n        graha_avastha = get_shayanadi_phal_with_naam(graha_avastha_raw, naam)"
new = """        naam = getattr(data, 'name', '') or ''
        graha_avastha = get_shayanadi_phal_with_naam(graha_avastha_raw, naam)
        # Aprakashit Grahas
        sun_lon_tropical = planets_with_houses.get('Sun', {}).get('longitude', 0)
        import swisseph as swe
        ayanamsa = swe.get_ayanamsa_ut(jd)
        sun_lon_sid = (sun_lon_tropical - ayanamsa + ayanamsa) % 360
        aprakashit = get_aprakashit_grahas(sun_lon_sid)"""

if old in content:
    content = content.replace(old, new)
    print("Endpoint updated!")
else:
    print("NOT FOUND - trying alternate")

# Update return
old_return = "'graha_avastha': graha_avastha, 'special_lagnas': special_lagnas"
new_return = "'graha_avastha': graha_avastha, 'special_lagnas': special_lagnas, 'aprakashit_grahas': aprakashit"
content = content.replace(old_return, new_return)
print("Return updated!")

open('/root/jyotish-api/main.py', 'w').write(content)
print("Done!")
