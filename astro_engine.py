"""
JyotishRishi Astrology Calculation Engine
Swiss Ephemeris (pyswisseph) based — Vedic/Sidereal
"""
import swisseph as swe
import math
from datetime import datetime, timedelta
from typing import Optional

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati',
]
NAKSHATRA_LORDS = [
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury',
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury',
    'Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury',
]
RASHI_NAMES = ['Mesh','Vrishabha','Mithuna','Karka','Simha','Kanya','Tula','Vrishchika','Dhanu','Makara','Kumbha','Meena']
RASHI_LORDS = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
PLANET_IDS = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN,'Rahu':swe.MEAN_NODE}
TITHI_NAMES = ['Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Purnima/Amavasya']
YOGA_NAMES = ['Vishkambha','Preeti','Ayushman','Saubhagya','Shobhana','Atiganda','Sukarman','Dhriti','Shoola','Ganda','Vriddhi','Dhruva','Vyaghata','Harshana','Vajra','Siddhi','Vyatipata','Variyan','Parigha','Shiva','Siddha','Sadhya','Shubha','Shukla','Brahma','Indra','Vaidhriti']
KARANA_NAMES = ['Bava','Balava','Kaulava','Taitila','Gara','Vanija','Vishti','Shakuni','Chatushpada','Nagava','Kimstughna']
DASHA_PERIODS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
RAHUKAAL_DAY = {0:7,1:1,2:6,3:4,4:5,5:3,6:2}
WEEKDAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def init_ephem(path=''):
    if path: swe.set_ephe_path(path)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_julian_day(year,month,day,hour_ut):
    return swe.julday(year,month,day,hour_ut)

def local_to_ut(year,month,day,hour,minute,tz):
    from datetime import datetime,timedelta
    total_minutes=hour*60+minute-tz*60
    base_date=datetime(year,month,day)+timedelta(minutes=total_minutes)
    ut_hour=base_date.hour+base_date.minute/60.0
    return base_date.year,base_date.month,base_date.day,ut_hour

def get_longitude_info(lon):
    lon=lon%360
    rashi_num=int(lon/30)
    degree_in_rashi=lon%30
    nak_size=360/27
    nak_num=int(lon/nak_size)
    pada=int((lon%nak_size)/(nak_size/4))+1
    return {'longitude':round(lon,4),'rashi':RASHI_NAMES[rashi_num],'rashi_num':rashi_num+1,'rashi_lord':RASHI_LORDS[rashi_num],'degree_in_rashi':round(degree_in_rashi,4),'nakshatra':NAKSHATRA_NAMES[nak_num],'nakshatra_num':nak_num+1,'nakshatra_lord':NAKSHATRA_LORDS[nak_num],'pada':pada}

def get_planet_position(jd,planet_name):
    flags=swe.FLG_SIDEREAL|swe.FLG_SPEED
    if planet_name=='Ketu':
        result=swe.calc_ut(jd,swe.MEAN_NODE,flags)
        lon=(result[0][0]+180)%360
        speed=result[0][3]
    else:
        result=swe.calc_ut(jd,PLANET_IDS[planet_name],flags)
        lon=result[0][0]
        speed=result[0][3]
    info=get_longitude_info(lon)
    info['planet']=planet_name
    info['speed']=round(speed,4)
    info['retrograde']=speed<0
    return info

def get_all_planets(jd):
    planets={}
    for name in list(PLANET_IDS.keys())+['Ketu']:
        planets[name]=get_planet_position(jd,name)
    return planets

def get_lagna(jd,lat,lon):
    cusps,ascmc=swe.houses(jd,lat,lon,b'P')
    asc_tropical=ascmc[0]
    ayanamsa=swe.get_ayanamsa_ut(jd)
    asc_sidereal=(asc_tropical-ayanamsa)%360
    info=get_longitude_info(asc_sidereal)
    info['ayanamsa']=round(ayanamsa,4)
    return info

def get_house_cusps(jd,lat,lon):
    cusps,ascmc=swe.houses(jd,lat,lon,b'P')
    ayanamsa=swe.get_ayanamsa_ut(jd)
    result=[]
    for i in range(12):
        sid_lon=(cusps[i]-ayanamsa)%360
        info=get_longitude_info(sid_lon)
        info['house']=i+1
        result.append(info)
    return result

def get_planet_house(planet_lon,lagna_lon):
    lagna_rashi=int(lagna_lon/30)
    planet_rashi=int(planet_lon/30)
    return((planet_rashi-lagna_rashi)%12)+1

def get_vimshottari_dasha(jd,moon_lon,birth_date):
    nak_size=360/27
    nak_num=int(moon_lon/nak_size)
    position_in_nak=moon_lon%nak_size
    fraction_elapsed=position_in_nak/nak_size
    start_lord=NAKSHATRA_LORDS[nak_num]
    start_idx=DASHA_ORDER.index(start_lord)
    remaining=DASHA_PERIODS[start_lord]*(1-fraction_elapsed)
    dashas=[]
    current_date=birth_date
    for i in range(9):
        lord=DASHA_ORDER[(start_idx+i)%9]
        years=remaining if i==0 else DASHA_PERIODS[lord]
        days=years*365.25
        end_date=current_date+timedelta(days=days)
        # Antardasha calculation
        antardashas=[]
        antar_start=current_date
        lord_idx=DASHA_ORDER.index(lord)
        for j in range(9):
            antar_lord=DASHA_ORDER[(lord_idx+j)%9]
            antar_years=(DASHA_PERIODS[antar_lord]*years)/120
            antar_days=antar_years*365.25
            antar_end=antar_start+timedelta(days=antar_days)
            antardashas.append({'lord':antar_lord,'start':antar_start.strftime('%Y-%m-%d'),'end':antar_end.strftime('%Y-%m-%d'),'years':round(antar_years,2)})
            antar_start=antar_end
        dashas.append({'lord':lord,'start':current_date.strftime('%Y-%m-%d'),'end':end_date.strftime('%Y-%m-%d'),'years':round(years,2),'antardashas':antardashas})
        current_date=end_date
    return{'current_dasha':dashas[0]['lord'],'dashas':dashas}

def check_mangal_dosha(mars_house):
    has_dosha=mars_house in[1,2,4,7,8,12]
    desc_map={1:'Mars in Lagna',2:'Mars in 2nd house',4:'Mars in 4th house',7:'Mars in 7th house',8:'Mars in 8th house',12:'Mars in 12th house'}
    return{'has_dosha':has_dosha,'mars_house':mars_house,'description':desc_map.get(mars_house,'No Mangal Dosha') if has_dosha else 'No Mangal Dosha'}

def get_vikram_samvat(year, month, day):
    """Calculate Vikram Samvat and Shaka Samvat"""
    # Vikram Samvat = Gregorian + 56/57 (57 after mid-April)
    vs = year + 56 if month >= 4 else year + 57
    ss = year - 78  # Shaka Samvat
    masa_names = ['Chaitra','Vaishakha','Jyeshtha','Ashadha','Shravana','Bhadrapada','Ashwina','Kartika','Margashirsha','Pausha','Magha','Phalguna']
    masa = masa_names[(month - 4) % 12] if month >= 4 else masa_names[(month + 8) % 12]
    return {'vikram_samvat': vs, 'shaka_samvat': ss, 'masa': masa}

def get_tithi(sun_lon,moon_lon):
    diff=(moon_lon-sun_lon)%360
    tithi_num=int(diff/12)+1
    paksha='Shukla' if tithi_num<=15 else 'Krishna'
    return{'number':tithi_num,'name':TITHI_NAMES[(tithi_num-1)%15],'paksha':paksha,'display':f'{paksha} {TITHI_NAMES[(tithi_num-1)%15]}'}

def get_yoga(sun_lon,moon_lon):
    total=(sun_lon+moon_lon)%360
    yoga_num=int(total/(360/27))
    return{'number':yoga_num+1,'name':YOGA_NAMES[yoga_num]}

def get_karana(sun_lon,moon_lon):
    diff=(moon_lon-sun_lon)%360
    karana_num=int(diff/6)
    name=KARANA_NAMES[(karana_num-1)%7] if 1<=karana_num<=56 else KARANA_NAMES[0]
    return{'number':karana_num+1,'name':name}

def get_sunrise_sunset(jd,lat,lon,tz):
    import math
    try:
        n=jd-2451545.0
        L=(280.46+0.9856474*n)%360
        g=math.radians((357.528+0.9856003*n)%360)
        lam=math.radians(L+1.915*math.sin(g)+0.020*math.sin(2*g))
        sin_dec=math.sin(math.radians(23.439))*math.sin(lam)
        dec=math.asin(sin_dec)
        cos_ha=(math.sin(math.radians(-0.833))-math.sin(math.radians(lat))*sin_dec)/(math.cos(math.radians(lat))*math.cos(dec))
        if abs(cos_ha)>1:
            weekday=int(jd+1.5)%7
            return{'sunrise':'N/A','sunset':'N/A','rahukaal':'N/A','weekday':WEEKDAY_NAMES[weekday]}
        ha=math.degrees(math.acos(cos_ha))
        B=math.radians(360/365*(n-81))
        eot=9.87*math.sin(2*B)-7.53*math.cos(B)-1.5*math.sin(B)
        noon_utc=720-4*lon-eot
        sunrise_utc=noon_utc-4*ha
        sunset_utc=noon_utc+4*ha
        sr=( sunrise_utc+tz*60)%(24*60)
        ss=(sunset_utc+tz*60)%(24*60)
        def mt(m):
            h=int(m//60)%24;mn=int(m%60);return f'{h:02d}:{mn:02d}'
        segment=(ss-sr)/8
        weekday=int(jd+1.5)%7
        rahu_seg=RAHUKAAL_DAY.get(weekday,7)
        rahu_start=sr+(rahu_seg-1)*segment
        return{'sunrise':mt(sr),'sunset':mt(ss),'rahukaal':f'{mt(rahu_start)}-{mt(rahu_start+segment)}','weekday':WEEKDAY_NAMES[weekday]}
    except Exception as e:
        return{'sunrise':'N/A','sunset':'N/A','rahukaal':'N/A','weekday':'N/A'}

def _yoni_score(b,g):
    if b==g:return 4
    for a,c,s in YE:
        if(b==a and g==c)or(b==c and g==a):return s
    return 2

def _maitri_score(br,gr):
    bl,gl=RL[br],RL[gr]
    if bl==gl:return 5
    bv,gv=PF[bl][gl],PF[gl][bl];s=bv+gv
    if s==4:return 5
    if s==3:return 4
    if s==2:return 3 if bv==1 and gv==1 else 1
    if s==1:return 0.5
    return 0

def _tara_score(bn,gn):
    A={2,4,6,8,9}
    gf=(((bn-gn+27)%27)%9+1)in A
    bf=(((gn-bn+27)%27)%9+1)in A
    return 3 if bf and gf else 1.5 if bf or gf else 0

def _bhakoot_score(br,gr):
    return 0 if((gr-br+12)%12+1)in{2,12,5,9,6,8} else 7

def _bhakoot_dosha_type(br,gr):
    v=(gr-br+12)%12+1
    if v in{2,12}:return'2-12 Dosha'
    if v in{5,9}:return'5-9 Dosha'
    if v in{6,8}:return'6-8 Dosha'
    return None

NR=[0,0,1,1,2,2,3,3,3,4,4,5,5,6,6,7,7,7,8,8,9,9,10,10,11,11,11]
RV=[2,1,0,3,2,1,0,3,2,1,0,3]
RVA=[0,0,1,2,3,1,1,4,1,0,1,2]
VC=[[2,1,1,0,1],[1,2,1,0,1],[1,1,2,0,1],[0,0,0,2,0],[1,1,1,0,2]]
NG=[0,1,2,1,0,1,0,0,2,2,1,1,0,2,0,2,0,2,2,1,1,0,2,2,1,1,0]
GC=[[6,5,1],[5,6,0],[1,0,6]]
NN=[0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2]
NY=[0,1,2,3,3,4,5,2,5,6,6,7,8,9,8,9,10,10,4,11,12,11,13,0,13,7,1]
YE=[(0,8,0),(1,13,0),(2,11,1),(3,12,0),(4,10,1),(5,6,1),(7,9,0)]
RL=[3,5,4,1,0,4,5,3,2,6,6,2]
PF=[[2,2,2,2,1,0,0],[2,2,1,1,2,1,1],[2,2,2,2,0,0,1],[2,2,2,2,0,1,1],[2,0,1,1,2,2,1],[1,0,1,1,2,2,2],[0,0,1,0,2,2,2]]
VARNA_N=['Shudra','Vaishya','Kshatriya','Brahmin']
VASHYA_N=['Chatushpad','Manav','Jalachar','Vanchar','Keet']
GANA_N=['Dev','Manav','Rakshasa']
NADI_N=['Aadi','Madhya','Antya']
YONI_N=['Ashwa','Gaja','Mesh','Sarpa','Shvan','Marjara','Mushika','Go','Mahisha','Vyaghra','Mriga','Vanara','Nakula','Simha']
PLANET_N=['Sun','Moon','Jupiter','Mars','Mercury','Venus','Saturn']

def calculate_ashtakoot(boy_nak,girl_nak):
    bn,gn=boy_nak,girl_nak
    br,gr=NR[bn],NR[gn]
    bVa,gVa=RV[br],RV[gr];varna=1 if bVa>=gVa else 0
    bVs,gVs=RVA[br],RVA[gr];vashya=VC[bVs][gVs]
    tara=_tara_score(bn,gn)
    bY,gY=NY[bn],NY[gn];yoni=_yoni_score(bY,gY)
    maitri=_maitri_score(br,gr)
    bG,gG=NG[bn],NG[gn];gana=GC[bG][gG]
    bhakoot=_bhakoot_score(br,gr);bhakoot_dosha=_bhakoot_dosha_type(br,gr)
    bN,gN=NN[bn],NN[gn];nadi=0 if bN==gN else 8;nadi_dosha=bN==gN
    total=varna+vashya+tara+yoni+maitri+gana+bhakoot+nadi
    md=[]
    if nadi_dosha:md.append('Nadi Dosha')
    if bhakoot_dosha:md.append(f'Bhakoot Dosha ({bhakoot_dosha})')
    if gana==0:md.append('Gana Dosha')
    if total>=32:verdict='Uttam Milan'
    elif total>=27:verdict='Shubh Milan'
    elif total>=21:verdict='Madhyam Milan'
    elif total>=18:verdict='Sadhaaran Milan'
    else:verdict='Ashubh Milan'
    return{'ashtakoota_points':total,'verdict':verdict,'major_doshas':md,'ashtakoota':{'varna':{'male_koot':VARNA_N[bVa],'female_koot':VARNA_N[gVa],'received_points':varna,'total_points':1},'vashya':{'male_koot':VASHYA_N[bVs],'female_koot':VASHYA_N[gVs],'received_points':vashya,'total_points':2},'tara':{'male_koot':NAKSHATRA_NAMES[bn],'female_koot':NAKSHATRA_NAMES[gn],'received_points':tara,'total_points':3},'yoni':{'male_koot':YONI_N[bY],'female_koot':YONI_N[gY],'received_points':yoni,'total_points':4},'maitri':{'male_koot':f'{PLANET_N[RL[br]]} ({RASHI_NAMES[br]})','female_koot':f'{PLANET_N[RL[gr]]} ({RASHI_NAMES[gr]})','received_points':maitri,'total_points':5},'gana':{'male_koot':GANA_N[bG],'female_koot':GANA_N[gG],'received_points':gana,'total_points':6},'bhakoot':{'male_koot':RASHI_NAMES[br],'female_koot':RASHI_NAMES[gr],'received_points':bhakoot,'total_points':7},'nadi':{'male_koot':NADI_N[bN],'female_koot':NADI_N[gN],'received_points':nadi,'total_points':8}}}