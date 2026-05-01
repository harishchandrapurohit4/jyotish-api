"""
Janma Dosh Endpoint - Gandmool + Mool Detection
================================================
Drop-in module for /janma-dosh endpoint.

Note: Pratyantar dasha is NOT here - it's already built into 
astro_engine.get_vimshottari_dasha() as 3-level structure.

Usage in main.py (after match-making block):
    try:
        from janma_dosh_endpoint import install_endpoint
        install_endpoint(app)
        print("[OK] Janma Dosh endpoint loaded")
    except Exception as _jd_err:
        print(f"[WARN] Janma Dosh not loaded: {_jd_err}")
"""

from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field

from janma_dosh_engine import detect_all_janma_doshas


class JanmaDoshRequest(BaseModel):
    """Request for janma nakshatra dosh detection"""
    nakshatra_number: int = Field(..., ge=1, le=27, example=19,
                                   description="Janma nakshatra (1=Ashwini, 27=Revati)")
    charan: int = Field(..., ge=1, le=4, example=1,
                        description="Nakshatra charan/pada (1-4)")
    name: Optional[str] = Field(None, example="Bachche ka naam")


def install_endpoint(app):
    """Install /janma-dosh endpoint on the FastAPI app."""
    
    @app.post('/janma-dosh')
    def janma_dosh_endpoint(data: JanmaDoshRequest):
        """
        Detect Gandmool / Mool nakshatra dosh from birth nakshatra + charan.
        
        BPHS-based with:
        - 6 Gandmool nakshatras (Ashwini, Ashlesha, Magha, Jyeshtha, Mool, Revati)
        - Mool charan-wise effects (1=Pita, 2=Mata, 3=Dhan, 4=Shubh)
        - Sanskrit shloks with meanings
        - Complete shanti vidhi (27th day puja, mantras, daan items)
        """
        try:
            result = detect_all_janma_doshas({
                "nakshatra_number": data.nakshatra_number,
                "charan": data.charan,
            })
            
            if result["total_doshas_found"] == 0:
                result["summary_hindi"] = "कोई गंडमूल/मूल दोष नहीं है। शुभ नक्षत्र में जन्म।"
                result["summary_english"] = "No Gandmool/Mool dosh detected."
            else:
                dosh = result["doshas"][0]
                result["summary_hindi"] = (
                    f"{dosh['nakshatra_hindi']} नक्षत्र के {dosh['charan']} चरण में जन्म। "
                    f"{dosh['affects']} पर प्रभाव। शान्ति विधि आवश्यक।"
                )
                result["summary_english"] = (
                    f"Born in {dosh['nakshatra']} nakshatra, charan {dosh['charan']}. "
                    f"Affects: {dosh['affects']}. Shanti vidhi recommended."
                )
            
            if data.name:
                result["name"] = data.name
            
            return result
        
        except Exception as e:
            raise HTTPException(500, f'Janma dosh error: {str(e)}')
    
    print("[OK] /janma-dosh endpoint registered")
