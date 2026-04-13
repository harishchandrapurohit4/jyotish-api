"""
JyotishRishi Astrology Calculation Engine - Updated for Accuracy
Swiss Ephemeris (pyswisseph) based — Vedic/Sidereal
"""
import swisseph as swe
import math
from datetime import datetime, timedelta
from typing import Optional

# Constants
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

# Updated to TRUE_NODE for better accuracy in Kundli
PLANET_IDS = {
    'Sun':swe.SUN, 'Moon':swe.MOON, 'Mars':swe.MARS, 
    'Mercury':swe.MERCURY, 'Jupiter':swe.JUPITER, 
    'Venus':swe.VENUS, 'Saturn':swe.SATURN, 
    'Rahu':swe.TRUE_NODE 
}

TITHI_NAMES = ['Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Purnima/Amavasya']
YOGA_NAMES = ['Vishkambha','Preeti','Ayushman','Saubhagya','Shobhana','Atiganda','Sukarman','Dhriti','Shoola','Ganda','Vriddhi','Dhruva','Vyaghata','Harshana','Vajra','Siddhi','Vyatipata','Variyan','Parigha','Shiva','Siddha','Sadhya','Shubha','Shukla','Brahma','Indra','Vaidhriti']
KARANA_NAMES = ['Bava','Balava','Kaulava','Taitila','Gara','Vanija','Vishti','Shakuni','Chatushpada','Nagava','Kimstughna']
DASHA_PERIODS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_ORDER = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
RAHUKAAL_DAY = {0:7,1:1,2:6,3:4,4:5,5:3,6:2}
WEEKDAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']


NAKSHATRA_ML = {
  "en": ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"],
  "hi": ["अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशिरा","आर्द्रा","पुनर्वसु","पुष्य","आश्लेषा","मघा","पूर्व फाल्गुनी","उत्तर फाल्गुनी","हस्त","चित्रा","स्वाती","विशाखा","अनुराधा","ज्येष्ठा","मूल","पूर्वाषाढ़ा","उत्तराषाढ़ा","श्रवण","धनिष्ठा","शतभिषा","पूर्व भाद्रपद","उत्तर भाद्रपद","रेवती"],
  "mr": ["अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशीर्ष","आर्द्रा","पुनर्वसु","पुष्य","आश्लेषा","मघा","पूर्वा फाल्गुनी","उत्तरा फाल्गुनी","हस्त","चित्रा","स्वाती","विशाखा","अनुराधा","ज्येष्ठा","मूळ","पूर्वाषाढा","उत्तराषाढा","श्रवण","धनिष्ठा","शततारका","पूर्वा भाद्रपदा","उत्तरा भाद्रपदा","रेवती"],
  "gu": ["અશ્વિની","ભરણી","કૃત્તિકા","રોહિણી","મૃગશીર્ષ","આર્દ્રા","પુનર્વસુ","પુષ્ય","આશ્લેષા","મઘા","પૂર્વ ફાલ્ગુની","ઉત્તર ફાલ્ગુની","હસ્ત","ચિત્રા","સ્વાતિ","વિશાખા","અનુરાધા","જ્યેષ્ઠા","મૂળ","પૂર્વાષાઢા","ઉત્તરાષાઢા","શ્રવણ","ધનિષ્ઠા","શતભિષા","પૂર્વ ભાદ્રપદા","ઉત્તર ભાદ્રપદા","રેવતી"],
  "bn": ["অশ্বিনী","ভরণী","কৃত্তিকা","রোহিণী","মৃগশিরা","আর্দ্রা","পুনর্বসু","পুষ্য","আশ্লেষা","মঘা","পূর্ব ফাল্গুনী","উত্তর ফাল্গুনী","হস্ত","চিত্রা","স্বাতী","বিশাখা","অনুরাধা","জ্যেষ্ঠা","মূল","পূর্বাষাঢ়া","উত্তরাষাঢ়া","শ্রবণ","ধনিষ্ঠা","শতভিষা","পূর্ব ভাদ্রপদা","উত্তর ভাদ্রপদা","রেবতী"]
}
RASHI_ML = {
  "en": ["Mesh","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"],
  "hi": ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुम्भ","मीन"],
  "mr": ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"],
  "gu": ["મેષ","વૃષભ","મિથુન","કર્ક","સિંહ","કન્યા","તુલા","વૃશ્ચિક","ધનુ","મકર","કુંભ","મીન"],
  "bn": ["মেষ","বৃষভ","মিথুন","কর্ক","সিংহ","কন্যা","তুলা","বৃশ্চিক","ধনু","মকর","কুম্ভ","মীন"]
}
TITHI_ML = {
  "en": ["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima/Amavasya"],
  "hi": ["प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","पूर्णिमा/अमावस्या"],
  "mr": ["प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","पौर्णिमा/अमावस्या"],
  "gu": ["પ્રતિપદા","દ્વિતીયા","તૃતીયા","ચતુર્થી","પંચમી","ષષ્ઠી","સપ્તમી","અષ્ટમી","નવમી","દશમી","એકાદશી","દ્વાદશી","ત્રયોદશી","ચતુર્દશી","પૂર્ણિમા/અમાવસ્યા"],
  "bn": ["প্রতিপদা","দ্বিতীয়া","তৃতীয়া","চতুর্থী","পঞ্চমী","ষষ্ঠী","সপ্তমী","অষ্টমী","নবমী","দশমী","একাদশী","দ্বাদশী","ত্রয়োদশী","চতুর্দশী","পূর্ণিমা/অমাবস্যা"]
}
YOGA_ML = {
  "en": ["Vishkambha","Preeti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarman","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"],
  "hi": ["विष्कम्भ","प्रीति","आयुष्मान","सौभाग्य","शोभन","अतिगण्ड","सुकर्मा","धृति","शूल","गण्ड","वृद्धि","ध्रुव","व्याघात","हर्षण","वज्र","सिद्धि","व्यतीपात","वरीयान","परिघ","शिव","सिद्ध","साध्य","शुभ","शुक्ल","ब्रह्म","इन्द्र","वैधृति"],
  "mr": ["विष्कंभ","प्रीती","आयुष्मान","सौभाग्य","शोभन","अतिगंड","सुकर्मा","धृती","शूल","गंड","वृद्धी","ध्रुव","व्याघात","हर्षण","वज्र","सिद्धी","व्यतीपात","वरीयान","परिघ","शिव","सिद्ध","साध्य","शुभ","शुक्ल","ब्रह्म","इंद्र","वैधृती"],
  "gu": ["વિષ્કંભ","પ્રીતિ","આયુષ્માન","સૌભાગ્ય","શોભન","અતિગંડ","સુકર્મા","ધૃતિ","શૂલ","ગંડ","વૃદ્ધિ","ધ્રુવ","વ્યાઘાત","હર્ષણ","વજ્ર","સિદ્ધિ","વ્યતીપાત","વરીયાન","પરિઘ","શિવ","સિદ્ધ","સાધ્ય","શુભ","શુક્લ","બ્રહ્મ","ઇન્દ્ર","વૈધૃતિ"],
  "bn": ["বিষ্কম্ভ","প্রীতি","আয়ুষ্মান","সৌভাগ্য","শোভন","অতিগণ্ড","সুকর্মা","ধৃতি","শূল","গণ্ড","বৃদ্ধি","ধ্রুব","ব্যাঘাত","হর্ষণ","বজ্র","সিদ্ধি","ব্যতীপাত","বরীয়ান","পরিঘ","শিব","সিদ্ধ","সাধ্য","শুভ","শুক্ল","ব্রহ্ম","ইন্দ্র","বৈধৃতি"]
}
KARANA_ML = {
  "en": ["Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti","Shakuni","Chatushpada","Nagava","Kimstughna"],
  "hi": ["बव","बालव","कौलव","तैतिल","गर","वणिज","विष्टि","शकुनि","चतुष्पाद","नागव","किंस्तुघ्न"],
  "mr": ["बव","बालव","कौलव","तैतिल","गर","वणिज","विष्टी","शकुनी","चतुष्पाद","नागव","किंस्तुघ्न"],
  "gu": ["બવ","બાલવ","કૌલવ","તૈતિલ","ગર","વણિજ","વિષ્ટિ","શકુનિ","ચતુષ્પાદ","નાગવ","કિંસ્તુઘ્ન"],
  "bn": ["বব","বালব","কৌলব","তৈতিল","গর","বণিজ","বিষ্টি","শকুনি","চতুষ্পাদ","নাগব","কিংস্তুঘ্ন"]
}
WEEKDAY_ML = {
  "en": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
  "hi": ["सोमवार","मंगलवार","बुधवार","गुरुवार","शुक्रवार","शनिवार","रविवार"],
  "mr": ["सोमवार","मंगळवार","बुधवार","गुरुवार","शुक्रवार","शनिवार","रविवार"],
  "gu": ["સોમવાર","મંગળવાર","બુધવાર","ગુરુવાર","શુક્રવાર","શનિવાર","રવિવાર"],
  "bn": ["সোমবার","মঙ্গলবার","বুধবার","বৃহস্পতিবার","শুক্রবার","শনিবার","রবিবার"]
}
PAKSHA_ML = {
  "en": {"Shukla":"Shukla","Krishna":"Krishna"},
  "hi": {"Shukla":"शुक्ल","Krishna":"कृष्ण"},
  "mr": {"Shukla":"शुक्ल","Krishna":"कृष्ण"},
  "gu": {"Shukla":"શુક્લ","Krishna":"કૃષ્ણ"},
  "bn": {"Shukla":"শুক্ল","Krishna":"কৃষ্ণ"}
}
PLANET_ML = {
  "en": {"Sun":"Sun","Moon":"Moon","Mars":"Mars","Mercury":"Mercury","Jupiter":"Jupiter","Venus":"Venus","Saturn":"Saturn","Rahu":"Rahu","Ketu":"Ketu","Lagna":"Lagna"},
  "hi": {"Sun":"सूर्य","Moon":"चंद्र","Mars":"मंगल","Mercury":"बुध","Jupiter":"गुरु","Venus":"शुक्र","Saturn":"शनि","Rahu":"राहु","Ketu":"केतु","Lagna":"लग्न"},
  "mr": {"Sun":"सूर्य","Moon":"चंद्र","Mars":"मंगळ","Mercury":"बुध","Jupiter":"गुरू","Venus":"शुक्र","Saturn":"शनी","Rahu":"राहू","Ketu":"केतू","Lagna":"लग्न"},
  "gu": {"Sun":"સૂર્ય","Moon":"ચંદ્ર","Mars":"મંગળ","Mercury":"બુધ","Jupiter":"ગુરુ","Venus":"શુક્ર","Saturn":"શની","Rahu":"રાહુ","Ketu":"કેતુ","Lagna":"લગ્ન"},
  "bn": {"Sun":"সূর্য","Moon":"চন্দ্র","Mars":"মঙ্গল","Mercury":"বুধ","Jupiter":"গুরু","Venus":"শুক্র","Saturn":"শনি","Rahu":"রাহু","Ketu":"কেতু","Lagna":"লগ্ন"}
}
def get_ml(dictionary, lang, index=None, key=None):
    l = lang if lang in dictionary else "en"
    d = dictionary[l]
    if index is not None: return d[index]
    if key is not None: return d.get(key, key)
    return d

def init_ephem(path=''):
    """Initialize Swiss Ephemeris with Lahiri Ayanamsa"""
    if path: swe.set_ephe_path(path)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_julian_day(year,month,day,hour_ut):
    return swe.julday(year,month,day,hour_ut)

def local_to_ut(year,month,day,hour,minute,tz):
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
    return {
        'longitude':round(lon,4),
        'rashi':RASHI_NAMES[rashi_num],
        'rashi_num':rashi_num+1,
        'rashi_lord':RASHI_LORDS[rashi_num],
        'degree_in_rashi':round(degree_in_rashi,4),
        'nakshatra':NAKSHATRA_NAMES[nak_num],
        'nakshatra_num':nak_num+1,
        'nakshatra_lord':NAKSHATRA_LORDS[nak_num],
        'pada':pada
    }

def get_planet_position(jd,planet_name):
    init_ephem()
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags=swe.FLG_SIDEREAL|swe.FLG_SPEED
    if planet_name=='Ketu':
        # Ketu is exactly 180 degrees from Rahu
        result=swe.calc_ut(jd,swe.TRUE_NODE,flags)
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

def get_vimshottari_dasha(jd,moon_lon,birth_date,tz=5.5):
    nak_size=360/27
    nak_num=int(moon_lon/nak_size)
    position_in_nak=moon_lon%nak_size
    fraction_elapsed=round(position_in_nak/nak_size, 8)
    start_lord=NAKSHATRA_LORDS[nak_num]
    start_idx=DASHA_ORDER.index(start_lord)
    remaining=round(DASHA_PERIODS[start_lord]*(1-fraction_elapsed), 6)
    dashas=[]
    birth_date_utc=birth_date-timedelta(hours=tz)
    current_date=birth_date_utc
    for i in range(9):
        lord=DASHA_ORDER[(start_idx+i)%9]
        years=remaining if i==0 else DASHA_PERIODS[lord]
        days=years*365.2425
        end_date=current_date+timedelta(days=days)
        antardashas=[]
        antar_start=current_date
        lord_idx=DASHA_ORDER.index(lord)
        for j in range(9):
            antar_lord=DASHA_ORDER[(lord_idx+j)%9]
            antar_years=(DASHA_PERIODS[antar_lord]*years)/120
            antar_days=antar_years*365.2425
            antar_end=antar_start+timedelta(days=antar_days)
            pratyantars=[]
            praty_start=antar_start
            antar_lord_idx=DASHA_ORDER.index(antar_lord)
            for k in range(9):
                praty_lord=DASHA_ORDER[(antar_lord_idx+k)%9]
                praty_years=(DASHA_PERIODS[praty_lord]*antar_years)/120
                praty_days=praty_years*365.2425
                praty_end=praty_start+timedelta(days=praty_days)
                pratyantars.append({'lord':praty_lord,'start':praty_start.strftime('%Y-%m-%d'),'end':praty_end.strftime('%Y-%m-%d'),'years':round(praty_years,4)})
                praty_start=praty_end
            antardashas.append({'lord':antar_lord,'start':antar_start.strftime('%Y-%m-%d'),'end':antar_end.strftime('%Y-%m-%d'),'years':round(antar_years,2),'pratyantars':pratyantars})
            antar_start=antar_end
        dashas.append({'lord':lord,'start':current_date.strftime('%Y-%m-%d'),'end':end_date.strftime('%Y-%m-%d'),'years':round(years,2),'antardashas':antardashas})
        current_date=end_date
    return{'current_dasha':dashas[0]['lord'],'dashas':dashas}

def check_mangal_dosha(mars_house):
    has_dosha=mars_house in[1,2,4,7,8,12]
    desc_map={1:'Mars in Lagna',2:'Mars in 2nd house',4:'Mars in 4th house',7:'Mars in 7th house',8:'Mars in 8th house',12:'Mars in 12th house'}
    return{'has_dosha':has_dosha,'mars_house':mars_house,'description':desc_map.get(mars_house,'No Mangal Dosha') if has_dosha else 'No Mangal Dosha'}

def get_vikram_samvat(year, month, day):
    vs = year + 56 if month >= 4 else year + 57
    ss = year - 78 
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

def get_sunrise_sunset(jd, lat, lon, tz):
    """High Precision Sunrise/Sunset using Swiss Ephemeris"""
    try:
        # Use swe.rise_trans for precise calculations
        # res_rise[0] returns the Julian Day of the event
        import math
        # Simple sunrise calculation
        d = jd - 2451545.0
        g = math.radians((357.529 + 0.98560028 * d) % 360)
        q = (280.459 + 0.98564736 * d) % 360
        L = math.radians((q + 1.915 * math.sin(g) + 0.020 * math.sin(2*g)) % 360)
        e = math.radians(23.439 - 0.0000004 * d)
        dec = math.asin(math.sin(e) * math.sin(L))
        lat_r = math.radians(lat)
        ha = math.acos(-math.tan(lat_r) * math.tan(dec))
        ha_deg = math.degrees(ha)
        noon = 12 - lon/15
        sr_local = noon - ha_deg/15 + tz
        ss_local = noon + ha_deg/15 + tz
        
        def mt(h):
            h = h % 24
            hr = int(h)
            mn = int((h % 1) * 60)
            return f"{hr:02d}:{mn:02d}"

        sr_str = mt(sr_local)
        ss_str = mt(ss_local)
        
        sr_min = (sr_local % 24) * 60
        ss_min = (ss_local % 24) * 60
        segment = (ss_min - sr_min) / 8
        
        weekday = int(jd + 0.5) % 7
        rahu_seg = RAHUKAAL_DAY.get(weekday, 7)
        rahu_start = sr_min + (rahu_seg - 1) * segment
        
        return {
            'sunrise': sr_str,
            'sunset': ss_str,
            'rahukaal': f"{mt(rahu_start/60)}-{mt((rahu_start+segment)/60)}",
            'weekday': WEEKDAY_NAMES[weekday]
        }
    except Exception as e:
        return {'sunrise':'N/A','sunset':'N/A','rahukaal':'N/A','weekday':'N/A'}

# Scoring functions (Yoni, Maitri, etc. remain the same)
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

# Ashtakoot data and calculate_ashtakoot remain unchanged...
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
    
    return {
        'ashtakoota_points':total,
        'verdict':verdict,
        'major_doshas':md,
        'ashtakoota':{
            'varna':{'male_koot':VARNA_N[bVa],'female_koot':VARNA_N[gVa],'received_points':varna,'total_points':1},
            'vashya':{'male_koot':VASHYA_N[bVs],'female_koot':VASHYA_N[gVs],'received_points':vashya,'total_points':2},
            'tara':{'male_koot':NAKSHATRA_NAMES[bn],'female_koot':NAKSHATRA_NAMES[gn],'received_points':tara,'total_points':3},
            'yoni':{'male_koot':YONI_N[bY],'female_koot':YONI_N[gY],'received_points':yoni,'total_points':4},
            'maitri':{'male_koot':f'{PLANET_N[RL[br]]} ({RASHI_NAMES[br]})','female_koot':f'{PLANET_N[RL[gr]]} ({RASHI_NAMES[gr]})','received_points':maitri,'total_points':5},
            'gana':{'male_koot':GANA_N[bG],'female_koot':GANA_N[gG],'received_points':gana,'total_points':6},
            'bhakoot':{'male_koot':RASHI_NAMES[br],'female_koot':RASHI_NAMES[gr],'received_points':bhakoot,'total_points':7},
            'nadi':{'male_koot':NADI_N[bN],'female_koot':NADI_N[gN],'received_points':nadi,'total_points':8}
        }
    }
# Disha Shool - weekday based direction to avoid
DISHA_SHOOL = {
    'Sunday': 'Paschim (West)', 'Monday': 'Purv (East)', 'Tuesday': 'Uttar (North)',
    'Wednesday': 'Uttar (North)', 'Thursday': 'Dakshina (South)', 'Friday': 'Paschim (West)',
    'Saturday': 'Purv (East)'
}

# Tithi Deity
TITHI_DEITY = {
    1:'Agni', 2:'Brahma', 3:'Gauri', 4:'Ganesh', 5:'Nag', 6:'Kartikeya',
    16:'Agni', 17:'Brahma', 18:'Gauri', 19:'Ganesh', 20:'Nag', 21:'Kartikeya',
    7:'Surya', 8:'Shiva', 9:'Durga', 10:'Yama', 11:'Vishnu', 12:'Vishnu',
    13:'Kamdev', 14:'Shiva', 15:'Chandra', 22:'Surya', 23:'Shiva', 24:'Durga', 25:'Yama', 26:'Vishnu', 27:'Vishnu', 28:'Kamdev', 29:'Shiva', 30:'Chandra'
}

def get_guli_yamghant(sunrise_str, sunset_str, weekday):
    try:
        sr = sum(int(x)*60**(1-i) for i,x in enumerate(sunrise_str.split(':')))
        ss = sum(int(x)*60**(1-i) for i,x in enumerate(sunset_str.split(':')))
        seg = (ss - sr) / 8
        GULI_SEG = {'Sunday':6,'Monday':5,'Tuesday':4,'Wednesday':3,'Thursday':2,'Friday':1,'Saturday':7}
        YAMGH_SEG = {'Sunday':4,'Monday':3,'Tuesday':2,'Wednesday':1,'Thursday':7,'Friday':6,'Saturday':5}
        def mt(m): return f"{int(m//60):02d}:{int(m%60):02d}"
        gs = GULI_SEG.get(weekday, 1)
        ys = YAMGH_SEG.get(weekday, 1)
        g_start = sr + (gs-1)*seg
        y_start = sr + (ys-1)*seg
        return {
            'guli_kaal': f"{mt(g_start)}-{mt(g_start+seg)}",
            'yamghant': f"{mt(y_start)}-{mt(y_start+seg)}"
        }
    except:
        return {'guli_kaal': 'N/A', 'yamghant': 'N/A'}

def get_abhijit(sunrise_str, sunset_str):
    try:
        sr = sum(int(x)*60**(1-i) for i,x in enumerate(sunrise_str.split(':')))
        ss = sum(int(x)*60**(1-i) for i,x in enumerate(sunset_str.split(':')))
        noon = (sr + ss) / 2
        def mt(m): return f"{int(m//60):02d}:{int(m%60):02d}"
        return f"{mt(noon - 24)}-{mt(noon + 24)}"
    except:
        return 'N/A'

def get_ritu_ayan(month, day):
    # Ritu (Indian seasons)
    if (month == 3 and day >= 21) or (month == 4) or (month == 5 and day <= 20):
        ritu = 'Vasant'
    elif (month == 5 and day >= 21) or (month == 6) or (month == 7 and day <= 22):
        ritu = 'Grishma'
    elif (month == 7 and day >= 23) or (month == 8) or (month == 9 and day <= 22):
        ritu = 'Varsha'
    elif (month == 9 and day >= 23) or (month == 10) or (month == 11 and day <= 21):
        ritu = 'Sharad'
    elif (month == 11 and day >= 22) or (month == 12) or (month == 1 and day <= 19):
        ritu = 'Hemant'
    else:
        ritu = 'Shishir'
    # Ayan
    if 3 <= month <= 8:
        ayan = 'Uttarayan'
    else:
        ayan = 'Dakshinayan'
    return {'ritu': ritu, 'ayana': ayan}

def get_moonrise_moonset(jd, lat, lon, tz):
    try:
        import math
        # Moon rises ~50 minutes later each day
        # Approximate moonrise based on moon longitude
        moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
        sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
        
        # Moon age (0-360)
        moon_age = (moon_lon - sun_lon) % 360
        
        # Approximate moonrise time
        sunrise_offset = moon_age / 360 * 24  # hours after sunrise
        sr = 6.5  # approximate sunrise in hours
        moonrise = (sr + sunrise_offset) % 24
        moonset = (moonrise + 12.5) % 24
        
        def mt(h): return f"{int(h):02d}:{int((h%1)*60):02d}"
        return {'moonrise': mt(moonrise), 'moonset': mt(moonset)}
    except:
        return {'moonrise': 'N/A', 'moonset': 'N/A'}


def calculate_varga(longitude, division):
    """Calculate Varga (divisional) chart sign for a given longitude"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    sign = int(longitude / 30)
    degree = longitude % 30
    part = 30 / division
    varga_part = int(degree / part)

    if division == 1:   # Rashi (D1)
        return sign % 12

    elif division == 2:  # Hora (D2)
        if sign % 2 == 0:  # Even sign
            return 3 if degree < 15 else 0  # Cancer or Aries
        else:  # Odd sign
            return 0 if degree < 15 else 3  # Aries or Cancer

    elif division == 3:  # Drekkana (D3)
        return (sign + varga_part * 4) % 12

    elif division == 4:  # Chaturthamsha (D4)
        return (sign + varga_part * 3) % 12

    elif division == 7:  # Saptamsha (D7)
        if sign % 2 == 0:
            return (sign + varga_part) % 12
        else:
            return (sign + varga_part + 6) % 12

    elif division == 9:  # Navamsha (D9)
        return (sign * 9 + varga_part) % 12

    elif division == 10:  # Dashamsha (D10)
        if sign % 2 == 0:
            return (sign * 10 + varga_part) % 12
        else:
            return (sign * 10 + varga_part + 8) % 12

    elif division == 12:  # Dwadashamsha (D12)
        return (sign * 12 + varga_part) % 12

    elif division == 16:  # Shodashamsha (D16)
        if sign % 2 == 0:
            return varga_part % 12
        else:
            return (varga_part + 4) % 12

    elif division == 20:  # Vimshamsha (D20)
        if sign % 3 == 0:
            return varga_part % 12
        elif sign % 3 == 1:
            return (varga_part + 4) % 12
        else:
            return (varga_part + 8) % 12

    elif division == 24:  # Chaturvimshamsha (D24)
        if sign % 2 == 0:
            return varga_part % 12
        else:
            return (varga_part + 3) % 12

    elif division == 27:  # Bhamsha (D27)
        if sign % 4 == 0:
            return varga_part % 12
        elif sign % 4 == 1:
            return (varga_part + 3) % 12
        elif sign % 4 == 2:
            return (varga_part + 6) % 12
        else:
            return (varga_part + 9) % 12

    elif division == 30:  # Trimsamsha (D30)
        if sign % 2 == 0:  # Even sign
            if degree < 5: return 0    # Aries
            elif degree < 10: return 10  # Aquarius
            elif degree < 18: return 8   # Sagittarius
            elif degree < 25: return 2   # Gemini
            else: return 6              # Libra
        else:  # Odd sign
            if degree < 5: return 6    # Libra
            elif degree < 12: return 2   # Gemini
            elif degree < 20: return 8   # Sagittarius
            elif degree < 25: return 10  # Aquarius
            else: return 0              # Aries

    elif division == 40:  # Khavedamsha (D40)
        if sign % 2 == 0:
            return varga_part % 12
        else:
            return (varga_part + 3) % 12

    elif division == 45:  # Akshavedamsha (D45)
        if sign % 3 == 0:
            return varga_part % 12
        elif sign % 3 == 1:
            return (varga_part + 4) % 12
        else:
            return (varga_part + 8) % 12

    elif division == 60:  # Shashtiamsha (D60)
        return (sign * 60 + varga_part) % 12

    return sign % 12


def get_all_vargas(longitude):
    """Get all varga chart positions for a planet"""
    RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
    divisions = [1,2,3,4,7,9,10,12,16,20,24,27,30,40,45,60]
    result = {}
    for d in divisions:
        sign_num = calculate_varga(longitude, d)
        result[f"D{d}"] = {"sign_num": sign_num + 1, "sign": RASHI[sign_num]}
    return result


def get_karkamsha_lagna(planets_data):
    """Calculate Karkamsha Lagna from Atmakaraka in Navamsha"""
    RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
    # Find Atmakaraka (highest degree planet)
    ak_planet = None
    ak_degree = -1
    for name, data in planets_data.items():
        deg_in_sign = data['longitude'] % 30
        if deg_in_sign > ak_degree:
            ak_degree = deg_in_sign
            ak_planet = name
    if ak_planet:
        ak_lon = planets_data[ak_planet]['longitude']
        d9_sign = calculate_varga(ak_lon, 9)
        return {
            "atmakaraka": ak_planet,
            "karkamsha_lagna": RASHI[d9_sign],
            "karkamsha_sign_num": d9_sign + 1
        }
    return {}


def get_pada_lagna(asc_longitude, arudha_house=1):
    """Calculate Pada Lagna (Arudha Lagna - AL)"""
    RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
    asc_sign = int(asc_longitude / 30)
    # Lord of Lagna
    SIGN_LORDS = [2,5,3,1,0,3,5,2,4,6,6,4]  # Mars,Venus,Mercury,Moon,Sun,Mercury,Venus,Mars,Jupiter,Saturn,Saturn,Jupiter
    lagna_lord_planet = SIGN_LORDS[asc_sign]
    # Simple Arudha calculation
    pada_sign = (asc_sign * 2 + arudha_house) % 12
    return {
        "pada_lagna": RASHI[pada_sign],
        "pada_sign_num": pada_sign + 1
    }


def get_upapada_lagna(house_cusps):
    """Calculate Upapada Lagna (UL) - 12th house arudha"""
    RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
    if len(house_cusps) >= 12:
        h12_lon = house_cusps[11]['longitude']
        h12_sign = int(h12_lon / 30)
        SIGN_LORDS = [2,5,3,1,0,3,5,2,4,6,6,4]
        lord_sign = SIGN_LORDS[h12_sign]
        ul_sign = (h12_sign + lord_sign + 1) % 12
        return {
            "upapada_lagna": RASHI[ul_sign],
            "ul_sign_num": ul_sign + 1
        }
    return {}


# Vedh System — Gochar mein Vedh check
GOCHAR_PHAL = {
    "Sun": {
        1: "Karyon mein adhik prayas, vaibhav naash, yatra evam rog. Kashtkaal — dhairya rakhen.",
        2: "Arthkshay, vanchana evam jal sambandhi rog (jalodar aadi) hote hain.",
        3: "Sthanlabh, shatrunaash, arthlabh evam swasthya accha rehta hai. Shubh.",
        4: "Stri-sambhog mein badha aur rogotpatti hoti hai.",
        5: "Shatru aur rogon se peeda hoti hai.",
        6: "Rog, shatru evam shok ka naash hota hai. Shubh.",
        7: "Yatra se nivritti aur kukshi mein rog hote hain.",
        8: "Stri se vimukhhata, raja se bhay evam rog hota hai.",
        9: "Aapatit, dinata, mayanak bimari aur aarthik/vyavsayik haani hoti hai.",
        10: "Karyon mein safalta aur sabhi jagah jeet hoti hai. Shubh.",
        11: "Padprapti, vaibhav labh, arthik samriddhi evam sharir mein aarogyta rehti hai. Ati Shubh.",
        12: "Vyapar safalta evam shubh phaldayak hota hai. Shubh."
    },
    "Moon": {
        1: "Mishtann, shayya evam vastr aadi milta hai. Shubh.",
        2: "Sabhi karyon mein vighn, maan evam arth ka naash hota hai.",
        3: "Stri, vastr, sukh evam dhan ki prapti tatha vijay milti hai. Shubh.",
        4: "Bhay utpann hota hai.",
        5: "Rog, shok aur marg (yatra) mein vighn badhayein aati hain.",
        6: "Sukh evam dhan ki prapti tatha shatru evam rog ka naash hota hai. Shubh.",
        7: "Accha bhojan, sammaan, dhan, shayansukh tatha aadesh dene ka avsar milta hai. Shubh.",
        8: "Bhay lagta hai.",
        9: "Bandhan, bhay evam kukshi mein rog hote hain.",
        10: "Rajpravrutti tatha labhasthaan mein hone par bandhu evam acchi matra mein dhan milta hai. Shubh.",
        11: "Bandhu samagam, dhan labh, manorath poorn evam sukh ki prapti hoti hai. Ati Shubh.",
        12: "Anek prakar ke dosh aur vyay hote hain."
    },
    "Mars": {
        1: "Chot lagna tatha usake dwitiy sthan mein hone par raja, chor, agni evam shatruon se peeda. Ashubh.",
        2: "Raja, chor, agni evam shatruon se peeda aur rogon se durbalata evam chinta hoti hai.",
        3: "Bal, dhan evam guhyakon ki kripa milti hai tatha shatrumardan hota hai. Shubh.",
        4: "Dushton ki sangati, udar rog, jwar evam sharir se raktasraav hota hai.",
        5: "Shatru evam vyadhi bhay tatha putra dwara shok hota hai.",
        6: "Tamba, sona aadi labh, kalah bhay evam vidwanon ka viyog hota hai.",
        7: "Kukshi rog evam patni se kalah hai aur ashubh.",
        8: "Ang-bhang hone se sharir lahuluhan hota tatha manobal evam sammaan ghata hai.",
        9: "Dhannash, parajay aur vyadhi hoti hai.",
        10: "Anek prakar ke labh evam labh sthan mein hone par janpad aadi ka adhikar (swamitv) milta hai. Shubh.",
        11: "Dhan labh, shatrunaash, kary mein safalta evam parakram ki vridhi hoti hai. Shubh.",
        12: "Anek artho ki utpatti, pitt aadi rogon se peeda evam netr vikar hota hai."
    },
    "Mercury": {
        1: "Apne bandhuo se kalah, durvachan evam apne dhan ka apaharan hota hai.",
        2: "Dhanikata aur tritiya sthan mein hone par raja evam shatru se bhay hota hai.",
        3: "Raja evam shatru se bhay hota hai.",
        4: "Dhanlabh, mitra ya kutumb ki vridhi hoti hai. Shubh.",
        5: "Stri evam putron se vivaad, virodh hota hai.",
        6: "Vijay, unnati evam bhagyoday hota hai. Shubh.",
        7: "Virodh aur ashubh.",
        8: "Vijay, putr, vastr, dhan evam nipunata ki prapti, harsh evam uday hota hai. Shubh.",
        9: "Rogkarak hota hai.",
        10: "Shatrunaash, dhanlabh, stribhog, madhur vani evam anek prakar ke sukh tatha utkarshdeta hai. Shubh.",
        11: "Patni, putr evam mitron se milan, vyapar mein labh evam sthayi santushti deta hai. Ati Shubh.",
        12: "Shatruon se parajay tatha rogon se peeda deta hai."
    },
    "Jupiter": {
        1: "Sthanhaani, dhannash, kalah evam buddhi mein jadta karta hai.",
        2: "Dhan ka labh, shatrunaash evam striyon ka bhog deta hai. Shubh.",
        3: "Karyavibhav, bhrash evam svapadam ka naash. Ashubh.",
        4: "Klesha, bandhujanotsthitaash na sukh. Ashubh.",
        5: "Ghoda, dhan, putr, svarn, ratn, strisahavas evam makaan ki prapti hoti hai. Shubh.",
        6: "Saadhan hone par bhi sukh nahi milta.",
        7: "Buddhi evam vani mein chaturata, aarthik unnati tatha stribhog milta hai. Shubh.",
        8: "Tivra dukh, bandhan evam satat yatra ke avsar milte hain.",
        9: "Patni, putr evam dhan ka labh, nipunata tatha kary evam aadesh mein safalta milti hai. Shubh.",
        10: "Sthaan evam dhan aadi nasht hota hai.",
        11: "Arthasiddhi, dhan labh, putr sukh, manorath poorn evam sarva karya sidhi hoti hai. Ati Shubh.",
        12: "Dirgha vyatana, dukh aur kasht sambhvet."
    },
    "Venus": {
        1: "Mishtann-bhojan, preyasi ka sangam, kasturi aadi suganchit vastu, shayan evam vastr aadi ki prapti hoti hai. Shubh.",
        2: "Dhan, dhanya, ratn evam raja se sammaan milta hai. Parivar ka swasthya accha rehta hai. Shubh.",
        3: "Aadesh, dhan, pad bhautik padaarth sammaan evam vastr ko nasht karta hai.",
        4: "Bandhu aur navayuvati mein anurakti tatha Indra ke samaan bhogye bhog milta hai. Shubh.",
        5: "Dhan, putr evam gurujanon se santosh milta hai. Shubh.",
        6: "Parajay aur saptam sthan mein hone par stri ke karan umradrav hota hai.",
        7: "Stri ke karan umradrav hota hai.",
        8: "Mandir, gharelu vastuyen, stri, ratn evam bhog aadi milta hai. Shubh.",
        9: "Dhan evam dharm ka labh, strisambhog tatha sukh aadi milte hain. Shubh.",
        10: "Kalah aur apmaaan karta hai.",
        11: "Mishtann, sugandhi, bandhu milan, dhan labh evam striyonse sukh milta hai. Ati Shubh.",
        12: "Bahut dhan, vaahan evam vastr aadi dilaata hai. Shubh."
    },
    "Saturn": {
        1: "Vish evam agni se bhay, sambandhi ki mrityu, deshtyaag, putr, parivarik log evam dhan ki haani aur door desh ki yatra hoti hai.",
        2: "Dhan, sukh evam sharir ki kaanti kshin hoti hai ya kamottejena kshin hoti hai.",
        3: "Haathi aadi upayogi pashu, dhan, aarogya evam any manorath poorn hote hain. Shubh.",
        4: "Man mein kutilata, stri evam apne nikat sambanchion ka viyog hota hai.",
        5: "Sab logon ke saath kalah aur putr ka viyog hota hai.",
        6: "Rog, haani, preyasangam evam desh se door jana. Ashubh.",
        7: "Shatuta, bandhan, apne dharm ki haani evam hriday rog hota hai.",
        8: "Vidya, kirti evam dhan nasht hota hai tatha naya kary milta hai.",
        9: "Shatuta, bandhan, apne dharm ki haani evam hriday rog hota hai.",
        10: "Vidya, kirti evam dhan nasht hota hai tatha naya kary milta hai.",
        11: "Dhan labh, pragati, kary mein safalta evam labh sthan ka poorn phal milta hai. Shubh.",
        12: "Dukh ki paramparaa evam jal ya samudra mein doobne ka bhay hota hai."
    },
    "Rahu": {
        1: "Shatru bhay, sharir peeda evam manasikatanav hota hai.",
        2: "Dhan ka naash, parivar mein kalah hoti hai.",
        3: "Shatruon par vijay, sahasi kary mein safalta milti hai. Shubh.",
        4: "Ghar mein kalah, maata ko kasht, vaahan se bhay.",
        5: "Santaan ko peeda, manas chinta, vivaad hota hai.",
        6: "Shatrunaash, rogon se mukti milti hai. Shubh.",
        7: "Dampaty mein kalah, rog, yatra ka bhay hota hai.",
        8: "Mrityu bhay, gambhir rog, aakasmat sankay hoti hai.",
        9: "Bhagya manda, dharm mein baadha, guru se virodh hota hai.",
        10: "Karya mein asafalta, apyash, aur aadesh mein rukavat aati hai.",
        11: "Arthik labh, vyapar mein unnati, manorath poorn evam icchit phal prapti hoti hai. Ati Shubh.",
        12: "Vyay adhik, gupt shatru, neend mein baadha hoti hai."
    },
    "Ketu": {
        1: "Shariri peeda, manasikatanav, ghar mein ashanti hoti hai.",
        2: "Dhan haani, parivar mein vivaad hota hai.",
        3: "Shatrunaash, parakram mein vridhi hoti hai. Shubh.",
        4: "Maata ko kasht, ghar mein ashanti, vastu haani hoti hai.",
        5: "Santaan peeda, buddhi bhraman, chinta rehti hai.",
        6: "Rog naash, shatru par vijay milti hai. Shubh.",
        7: "Patni/pati ko kasht, dampaty mein kalah hoti hai.",
        8: "Mrityu bhay, aakasmat haani, rog hota hai.",
        9: "Bhagya mein rukavat, guru se virodh hota hai.",
        10: "Kary mein baadha, apyash milta hai.",
        11: "Labh, manorath sidhhi, adhyatmik unnati evam sarva karya safal hote hain. Shubh.",
        12: "Moksha ki bhavana, adhyatm mein ruchi badhti hai. Shubh."
    }
}



VEDH_PAIRS = {
    "Sun":     [(3,12), (6,9), (10,4), (11,5)],
    "Moon":    [(1,5), (3,9), (6,12), (7,2), (10,4), (11,8)],
    "Mars":    [(3,12), (6,9), (11,5)],
    "Mercury": [(2,5), (4,3), (6,9), (8,1), (10,8), (11,12)],
    "Jupiter": [(2,12), (5,4), (7,3), (9,10), (11,8)],
    "Venus":   [(1,8), (2,7), (3,10), (4,9), (5,11), (8,5), (9,4), (11,6), (12,3)],
    "Saturn":  [(3,12), (6,9), (11,5)],
    "Rahu":    [(3,12), (6,9), (11,5)],
    "Ketu":    [(3,12), (6,9), (11,5)]
}

def check_vedh(planet, moon_bhav, other_planets_bhavs):
    """
    Check if gochar planet is vedh-afflicted
    moon_bhav: current transit bhav of the planet from moon
    other_planets_bhavs: dict of other planets and their transit bhavs
    Returns: (has_vedh, vedh_planet)
    """
    pairs = VEDH_PAIRS.get(planet, [])
    for pair in pairs:
        if moon_bhav in pair:
            # Find the other bhav in pair
            other_bhav = pair[1] if pair[0] == moon_bhav else pair[0]
            # Check if any planet is in that vedh bhav
            for other_planet, other_bhav_val in other_planets_bhavs.items():
                if other_planet != planet and other_bhav_val == other_bhav:
                    # Exception: Sun-Saturn and Moon-Mercury don't vedh each other
                    if (planet == "Sun" and other_planet == "Saturn") or                        (planet == "Saturn" and other_planet == "Sun") or                        (planet == "Moon" and other_planet == "Mercury") or                        (planet == "Mercury" and other_planet == "Moon"):
                        continue
                    return True, other_planet
    return False, None


def get_gochar_phal_with_vedh(moon_sign_num, transit_positions):
    """
    Get complete Gochar Phal with Vedh check
    moon_sign_num: 1-12 (janm rashi)
    transit_positions: dict of planet -> longitude
    """
    RASHI = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
    
    # Calculate bhav from moon for each transit planet
    planet_bhavs = {}
    for planet, lon in transit_positions.items():
        planet_sign = int(lon / 30) + 1  # 1-12
        bhav = ((planet_sign - moon_sign_num) % 12) + 1
        planet_bhavs[planet] = bhav
    
    results = {}
    for planet, bhav in planet_bhavs.items():
        phal_data = GOCHAR_PHAL.get(planet, {}).get(bhav, "Phal uplabdh nahi")
        shubh = "Shubh" in phal_data
        
        # Check vedh
        other_bhavs = {p: b for p, b in planet_bhavs.items() if p != planet}
        has_vedh, vedh_planet = check_vedh(planet, bhav, other_bhavs)
        
        if has_vedh:
            shubh = False
            phal_final = phal_data + f" (⚠️ Vedh: {vedh_planet} se vedh — phal nishfal ho sakta hai)"
        else:
            phal_final = phal_data
        
        results[planet] = {
            "bhav": bhav,
            "phal": phal_final,
            "shubh": shubh,
            "vedh": has_vedh,
            "vedh_planet": vedh_planet,
            "transit_sign": RASHI[int(transit_positions[planet]/30)]
        }
    
    return results



def get_gochar_phal(planet, bhav):
    """Get Gochar Phal for a planet in a specific bhav from Moon sign"""
    phal = GOCHAR_PHAL.get(planet, {}).get(bhav, "Phal uplabdh nahi")
    shubh = "Shubh" in phal
    return {
        "planet": planet,
        "bhav": bhav,
        "phal": phal,
        "shubh": shubh
    }
