"""
/api/match-making endpoint
==========================
Proxy endpoint to fix existing Uttar Bhartiya Matchmaking page

Frontend at /matchmaking calls /api/match-making
This endpoint internally uses dashakoot_milan logic
Returns format expected by frontend (Matchmaking.tsx)

Frontend expects:
{
  "ashtakoota": {
    "varna": {male_koot, female_koot, received_points, total_points},
    "vashya": {...},
    "tara": {...},
    "yoni": {...},
    "maitri": {...},
    "gana": {...},
    "bhakoot": {...},
    "nadi": {...},
    "ashtakoota_points": int
  },
  "mangal_dosha": {
    "male_has_dosha": bool,
    "female_has_dosha": bool,
    "description": str
  }
}
"""

from fastapi import HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, '/root/jyotish-api')

from dashakoot import dashakoot_milan, get_rashi_nakshatra_from_birth


class PersonInput(BaseModel):
    name: str = "Unknown"
    dob: str  # YYYY-MM-DD
    tob: str  # HH:MM
    lat: float
    lon: float
    tz: float = 5.5


class MatchMakingRequest(BaseModel):
    boy: PersonInput
    girl: PersonInput


def install_match_making_endpoint(app):
    """
    Install /api/match-making endpoint that proxies to dashakoot_milan
    Returns format expected by existing frontend
    """
    
    @app.post('/api/match-making')
    def match_making_endpoint(req: MatchMakingRequest):
        try:
            # Get rashi & nakshatra for both
            boy_info = get_rashi_nakshatra_from_birth(
                req.boy.dob, req.boy.tob,
                req.boy.lat, req.boy.lon, req.boy.tz
            )
            girl_info = get_rashi_nakshatra_from_birth(
                req.girl.dob, req.girl.tob,
                req.girl.lat, req.girl.lon, req.girl.tz
            )
            
            # Build birth details for Mangal Dosha
            boy_birth = {
                'date': req.boy.dob, 'time': req.boy.tob,
                'latitude': req.boy.lat, 'longitude': req.boy.lon,
                'timezone': req.boy.tz
            }
            girl_birth = {
                'date': req.girl.dob, 'time': req.girl.tob,
                'latitude': req.girl.lat, 'longitude': req.girl.lon,
                'timezone': req.girl.tz
            }
            
            # Calculate dashakoot
            milan = dashakoot_milan(boy_info, girl_info, boy_birth, girl_birth)
            
            # Convert to frontend's expected format
            koots = milan['koots']
            koot_map = {k['name']: k for k in koots}
            
            def koot_to_api(koot_name: str, frontend_name: str) -> dict:
                """Convert internal koot to API format"""
                k = koot_map.get(koot_name, {})
                return {
                    'male_koot': k.get('boy_value', '—'),
                    'female_koot': k.get('girl_value', '—'),
                    'received_points': k.get('score', 0),
                    'total_points': k.get('max', 0)
                }
            
            ashtakoota = {
                'varna': koot_to_api('Varna', 'varna'),
                'vashya': koot_to_api('Vashya', 'vashya'),
                'tara': koot_to_api('Tara', 'tara'),
                'yoni': koot_to_api('Yoni', 'yoni'),
                'maitri': koot_to_api('GrahaMaitri', 'maitri'),
                'gana': koot_to_api('Gana', 'gana'),
                'bhakoot': koot_to_api('Bhakoot', 'bhakoot'),
                'nadi': koot_to_api('Naadi', 'nadi'),
                'ashtakoota_points': milan['total_score']
            }
            
            # Mangal Dosha summary
            mangal = milan.get('mangal_analysis', {})
            mangal_dosha = {
                'male_has_dosha': bool(mangal.get('boy_dosha', {}).get('has_dosha', False)) if mangal else False,
                'female_has_dosha': bool(mangal.get('girl_dosha', {}).get('has_dosha', False)) if mangal else False,
                'description': mangal.get('verdict_hindi', '') if mangal else 'Mangal Dosha analysis not available'
            }
            
            return {
                'ashtakoota': ashtakoota,
                'mangal_dosha': mangal_dosha,
                # Bonus: include classical mangal analysis for advanced display
                'mangal_classical': mangal,
                'verdict': milan['verdict'],
                'verdict_color': milan['verdict_color'],
                'doshas_present': milan['doshas_present']
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Match-making error: {str(e)}")
    
    return app
