"""
JyotishRishi Astrology API
FastAPI + Swiss Ephemeris (pyswisseph)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import os
from astro_engine import (
    init_ephem,get_julian_day,local_to_ut,get_all_planets,get_lagna,
    get_house_cusps,get_planet_house,get_vimshottari_dasha,
    check_mangal_dosha,get_tithi,get_yoga,get_karana,
    get_sunrise_sunset,calculate_ashtakoot,NAKSHATRA_NAMES,
)
EPHEM_PATH=os.environ.get('EPHEM_PATH','')
init_ephem(EPHEM_PATH)
app=FastAPI(title='JyotishRishi Astrology API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
class BirthData(BaseModel):
    dob:str=Field(...,example='1990-08-15')
    tob:str=Field(...,example='10:30')
    lat:float=Field(...,example=28.6139)
    lon:float=Field(...,example=77.2090)
    tz:float=Field(5.5)
    name:Optional[str]=None
class PanchangRequest(BaseModel):
    date:str=Field(...,example='2026-04-05')
    lat:float=Field(...,example=28.6139)
    lon:float=Field(...,example=77.2090)
    tz:float=Field(5.5)
class MatchMakingRequest(BaseModel):
    boy:BirthData
    girl:BirthData
def parse_birth(data:BirthData):
    try:
        y,mo,d=map(int,data.dob.split('-'))
        h,mi=map(int,data.tob.split(':'))
    except:
        raise HTTPException(400,'Invalid dob or tob format')
    y_ut,mo_ut,d_ut,h_ut=local_to_ut(y,mo,d,h,mi,data.tz)
    jd=get_julian_day(y_ut,mo_ut,d_ut,h_ut)
    birth_dt=datetime(y,mo,d,h,mi)
    return jd,birth_dt
@app.get('/')
def root():
    return{'api':'JyotishRishi Astrology API','version':'1.0.0','endpoints':['/birth-details','/kundali','/panchang','/match-making','/nakshatra','/health']}
@app.get('/health')
def health():
    return{'status':'ok','engine':'Swiss Ephemeris (Lahiri Ayanamsa)'}
@app.post('/birth-details')
def birth_details(data:BirthData):
    jd,birth_dt=parse_birth(data)
    try:
        planets=get_all_planets(jd)
        lagna=get_lagna(jd,data.lat,data.lon)
        moon=planets['Moon']
        dasha=get_vimshottari_dasha(jd,moon['longitude'],birth_dt)
        return{'name':data.name,'dob':data.dob,'tob':data.tob,'place':{'lat':data.lat,'lon':data.lon,'tz':data.tz},'lagna':lagna,'moon_nakshatra':moon['nakshatra'],'moon_nakshatra_num':moon['nakshatra_num'],'moon_nakshatra_lord':moon['nakshatra_lord'],'moon_rashi':moon['rashi'],'moon_rashi_num':moon['rashi_num'],'planets':planets,'vimshottari_dasha':dasha}
    except Exception as e:
        raise HTTPException(500,f'Calculation error: {str(e)}')
@app.post('/kundali')
def kundali(data:BirthData):
    jd,birth_dt=parse_birth(data)
    try:
        planets=get_all_planets(jd)
        lagna=get_lagna(jd,data.lat,data.lon)
        house_cusps=get_house_cusps(jd,data.lat,data.lon)
        planets_with_houses={}
        for name,p in planets.items():
            house=get_planet_house(p['longitude'],lagna['longitude'])
            planets_with_houses[name]={**p,'house':house}
        mars_house=planets_with_houses['Mars']['house']
        mangal=check_mangal_dosha(mars_house)
        moon=planets['Moon']
        dasha=get_vimshottari_dasha(jd,moon['longitude'],birth_dt)
        return{'name':data.name,'dob':data.dob,'tob':data.tob,'place':{'lat':data.lat,'lon':data.lon,'tz':data.tz},'lagna':lagna,'ayanamsa':lagna['ayanamsa'],'planets':planets_with_houses,'house_cusps':house_cusps,'mangal_dosha':mangal,'vimshottari_dasha':dasha}
    except Exception as e:
        raise HTTPException(500,f'Calculation error: {str(e)}')
@app.post('/panchang')
def panchang(req:PanchangRequest):
    try:
        y,mo,d=map(int,req.date.split('-'))
    except:
        raise HTTPException(400,'Invalid date format')
    try:
        h_ut=12.0-req.tz
        jd=get_julian_day(y,mo,d,h_ut)
        planets=get_all_planets(jd)
        sun_lon=planets['Sun']['longitude']
        moon_lon=planets['Moon']['longitude']
        tithi=get_tithi(sun_lon,moon_lon)
        yoga=get_yoga(sun_lon,moon_lon)
        karana=get_karana(sun_lon,moon_lon)
        sun_info=get_sunrise_sunset(jd,req.lat,req.lon,req.tz)
        return{'date':req.date,'place':{'lat':req.lat,'lon':req.lon,'tz':req.tz},'tithi':tithi,'nakshatra':{'name':planets['Moon']['nakshatra'],'num':planets['Moon']['nakshatra_num'],'lord':planets['Moon']['nakshatra_lord'],'pada':planets['Moon']['pada']},'yoga':yoga,'karana':karana,'sun':{'rashi':planets['Sun']['rashi'],'nakshatra':planets['Sun']['nakshatra']},'sunrise':sun_info['sunrise'],'sunset':sun_info['sunset'],'rahukaal':sun_info['rahukaal'],'weekday':sun_info['weekday'],'planets':{k:{'rashi':v['rashi'],'nakshatra':v['nakshatra'],'retrograde':v['retrograde']} for k,v in planets.items()}}
    except Exception as e:
        raise HTTPException(500,f'Calculation error: {str(e)}')
@app.post('/match-making')
def match_making(req:MatchMakingRequest):
    try:
        boy_jd,boy_dt=parse_birth(req.boy)
        girl_jd,girl_dt=parse_birth(req.girl)
        boy_planets=get_all_planets(boy_jd)
        girl_planets=get_all_planets(girl_jd)
        boy_moon_nak=boy_planets['Moon']['nakshatra_num']-1
        girl_moon_nak=girl_planets['Moon']['nakshatra_num']-1
        ashtakoot=calculate_ashtakoot(boy_moon_nak,girl_moon_nak)
        boy_lagna=get_lagna(boy_jd,req.boy.lat,req.boy.lon)
        girl_lagna=get_lagna(girl_jd,req.girl.lat,req.girl.lon)
        boy_mars_house=get_planet_house(boy_planets['Mars']['longitude'],boy_lagna['longitude'])
        girl_mars_house=get_planet_house(girl_planets['Mars']['longitude'],girl_lagna['longitude'])
        boy_mangal=check_mangal_dosha(boy_mars_house)
        girl_mangal=check_mangal_dosha(girl_mars_house)
        dosha_cancelled=boy_mangal['has_dosha'] and girl_mangal['has_dosha']
        if dosha_cancelled: mangal_desc='Both Mangalik — Dosha cancels!'
        elif boy_mangal['has_dosha']: mangal_desc=f"Boy is Mangalik: {boy_mangal['description']}"
        elif girl_mangal['has_dosha']: mangal_desc=f"Girl is Mangalik: {girl_mangal['description']}"
        else: mangal_desc='No Mangal Dosha'
        return{**ashtakoot,'boy':{'name':req.boy.name,'moon_nakshatra':boy_planets['Moon']['nakshatra'],'moon_rashi':boy_planets['Moon']['rashi']},'girl':{'name':req.girl.name,'moon_nakshatra':girl_planets['Moon']['nakshatra'],'moon_rashi':girl_planets['Moon']['rashi']},'mangal_dosha':{'male_has_dosha':boy_mangal['has_dosha'],'female_has_dosha':girl_mangal['has_dosha'],'dosha_cancelled':dosha_cancelled,'description':mangal_desc}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500,f'Calculation error: {str(e)}')
@app.post('/nakshatra')
def get_nakshatra(data:BirthData):
    jd,_=parse_birth(data)
    try:
        planets=get_all_planets(jd)
        moon=planets['Moon']
        return{'nakshatra':moon['nakshatra'],'nakshatra_num':moon['nakshatra_num'],'nakshatra_lord':moon['nakshatra_lord'],'pada':moon['pada'],'rashi':moon['rashi'],'rashi_num':moon['rashi_num']}
    except Exception as e:
        raise HTTPException(500,str(e))