

# YOGAS DETECTION ENDPOINT
from yogas_engine import detect_all_yogas
import astro_engine as ae

class YogasRequest(BaseModel):
    date: str
    time: str
    latitude: float
    longitude: float
    timezone: float = 5.5

@app.post('/yogas')
def detect_yogas_endpoint(req: YogasRequest):
    try:
        parts = req.date.split('-')
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        time_parts = req.time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        ut_h = ae.local_to_ut(year, month, day, hour, minute, req.timezone)
        jd = ae.get_julian_day(year, month, day, ut_h)
        planets_data = ae.get_all_planets(jd)
        lagna_lon = ae.get_lagna(jd, req.latitude, req.longitude)
        lagna_rashi = int(lagna_lon / 30) + 1
        chart = {
            'lagna': {'rashi': lagna_rashi},
            'planets': {}
        }
        for planet_name, lon_data in planets_data.items():
            if isinstance(lon_data, dict):
                lon_val = lon_data.get('longitude', lon_data.get('lon', 0))
            else:
                lon_val = lon_data
            chart['planets'][planet_name] = {'rashi': int(lon_val / 30) + 1}
        result = detect_all_yogas(chart)
        result['lagna_rashi'] = lagna_rashi
        return result
    except Exception as e:
        import traceback
        return {
            'error': str(e),
            'traceback': traceback.format_exc()[:500],
            'total_yogas': 0,
            'detected_yogas': []
        }
