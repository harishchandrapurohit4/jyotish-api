content = open('/root/jyotish-api/main.py').read()

code = """
def get_gulik_spasht(jd, sunrise_jd, day_of_week, is_day_birth, lat, lon):
    try:
        import swisseph as swe
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        DAY_GULIK = {0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0}
        NIGHT_GULIK = {0:1, 1:0, 2:6, 3:5, 4:4, 5:3, 6:2}
        day_duration = 0.5
        if is_day_birth:
            khand = DAY_GULIK[day_of_week]
            gulik_jd = sunrise_jd + (khand * day_duration / 8)
        else:
            khand = NIGHT_GULIK[day_of_week]
            sunset_jd = sunrise_jd + day_duration
            gulik_jd = sunset_jd + (khand * day_duration / 8)
        cusps, ascmc = swe.houses(gulik_jd, lat, lon, b'P')
        ayanamsa = swe.get_ayanamsa_ut(gulik_jd)
        gulik_lon = (ascmc[0] - ayanamsa) % 360
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        sign = int(gulik_lon / 30)
        degree = gulik_lon % 30
        d = int(degree)
        m = int((degree - d) * 60)
        return {'gulik_lagna': RASHI_N[sign], 'gulik_lagna_num': sign+1, 'gulik_degree': str(d)+'deg'+str(m)+'min', 'khand': khand}
    except Exception as e:
        return {'error': str(e)}

def get_pranapada(sun_longitude, ishtkal_hours):
    try:
        RASHI_N = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
        pranapada_ishtkal = ishtkal_hours * 2.5
        plon_total = pranapada_ishtkal * 60
        rashi_count = int(plon_total / 1800)
        shesha_pal = plon_total % 1800
        ansh = shesha_pal / 30
        pranapada_lon = (sun_longitude + (rashi_count * 30) + ansh) % 360
        sign = int(pranapada_lon / 30)
        degree = pranapada_lon % 30
        d = int(degree)
        m = int((degree - d) * 60)
        return {'pranapada_lagna': RASHI_N[sign], 'pranapada_num': sign+1, 'pranapada_degree': str(d)+'deg'+str(m)+'min', 'longitude': round(pranapada_lon, 4)}
    except Exception as e:
        return {'error': str(e)}
"""

if 'get_gulik_spasht' not in content:
    content = content.replace("def get_aprakashit_grahas", code + "\ndef get_aprakashit_grahas")
    print("Gulik + Pranapada added!")
else:
    print("Already exists!")

old = "        aprakashit = get_aprakashit_grahas(sun_lon_sid)"
new = """        aprakashit = get_aprakashit_grahas(sun_lon_sid)
        import datetime
        dob_parts = data.dob.split('-')
        birth_dt = datetime.date(int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]))
        dow_map = {0:1,1:2,2:3,3:4,4:5,5:6,6:0}
        dow = dow_map[birth_dt.weekday()]
        birth_hour = int(data.tob.split(':')[0]) + int(data.tob.split(':')[1])/60
        sunrise_approx = 6.0
        is_day = sunrise_approx <= birth_hour <= 18.0
        sunrise_jd_approx = jd - (birth_hour/24) + ((sunrise_approx - data.tz)/24)
        gulik = get_gulik_spasht(jd, sunrise_jd_approx, dow, is_day, data.lat, data.lon)
        ishtkal = (birth_hour - sunrise_approx) if is_day else (birth_hour + 24 - 18.0)
        pranapada = get_pranapada(sun_lon_sid, ishtkal)"""

if old in content:
    content = content.replace(old, new)
    print("Endpoint updated!")
else:
    print("NOT FOUND")

old_r = "'aprakashit_grahas': aprakashit"
new_r = "'aprakashit_grahas': aprakashit, 'gulik': gulik, 'pranapada': pranapada"
content = content.replace(old_r, new_r)
print("Return updated!")

open('/root/jyotish-api/main.py', 'w').write(content)
print("Done!")
