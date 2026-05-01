"""
Dashakoot Milan API Endpoint v2
With Mangal Dosha integration
"""

from fastapi import HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, '/root/jyotish-api')

# Import from updated dashakoot.py
from dashakoot import (
    dashakoot_milan,
    get_rashi_nakshatra_from_birth,
    RASHI_NAMES,
    NAKSHATRA_NAMES
)


class BirthDetails(BaseModel):
    name: str = "Unknown"
    date: str
    time: str
    latitude: float
    longitude: float
    timezone: float = 5.5


class DashakootRequest(BaseModel):
    boy: BirthDetails
    girl: BirthDetails


def install_dashakoot_endpoint(app):
    
    @app.post('/dashakoot-milan')
    def dashakoot_milan_endpoint(req: DashakootRequest):
        try:
            # Calculate rashi & nakshatra
            boy_info = get_rashi_nakshatra_from_birth(
                req.boy.date, req.boy.time,
                req.boy.latitude, req.boy.longitude,
                req.boy.timezone
            )
            girl_info = get_rashi_nakshatra_from_birth(
                req.girl.date, req.girl.time,
                req.girl.latitude, req.girl.longitude,
                req.girl.timezone
            )

            # Build birth details for Mangal calculation
            boy_birth = {
                'date': req.boy.date,
                'time': req.boy.time,
                'latitude': req.boy.latitude,
                'longitude': req.boy.longitude,
                'timezone': req.boy.timezone
            }
            girl_birth = {
                'date': req.girl.date,
                'time': req.girl.time,
                'latitude': req.girl.latitude,
                'longitude': req.girl.longitude,
                'timezone': req.girl.timezone
            }

            # Calculate full Dashakoot with Mangal Dosha
            milan = dashakoot_milan(boy_info, girl_info, boy_birth, girl_birth)

            return {
                'success': True,
                'boy': {
                    'name': req.boy.name,
                    'rashi': boy_info['rashi_name'],
                    'rashi_hindi': boy_info['rashi_hindi'],
                    'nakshatra': boy_info['nakshatra_name'],
                    'pada': boy_info['pada']
                },
                'girl': {
                    'name': req.girl.name,
                    'rashi': girl_info['rashi_name'],
                    'rashi_hindi': girl_info['rashi_hindi'],
                    'nakshatra': girl_info['nakshatra_name'],
                    'pada': girl_info['pada']
                },
                'milan': milan
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Dashakoot error: {str(e)}")

    @app.post('/dashakoot-milan-quick')
    def dashakoot_milan_quick(boy_rashi: int, girl_rashi: int,
                               boy_nakshatra: int, girl_nakshatra: int):
        try:
            boy_info = {'rashi_idx': boy_rashi, 'nakshatra_idx': boy_nakshatra}
            girl_info = {'rashi_idx': girl_rashi, 'nakshatra_idx': girl_nakshatra}
            milan = dashakoot_milan(boy_info, girl_info)
            return {
                'success': True,
                'boy': {'rashi': RASHI_NAMES[boy_rashi], 'nakshatra': NAKSHATRA_NAMES[boy_nakshatra]},
                'girl': {'rashi': RASHI_NAMES[girl_rashi], 'nakshatra': NAKSHATRA_NAMES[girl_nakshatra]},
                'milan': milan
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app
