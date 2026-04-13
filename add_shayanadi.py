content = open('/root/jyotish-api/main.py').read()

shayanadi_phal_code = """
NAAM_AKSHAR_ANK = {'a':1,'aa':1,'i':2,'ii':2,'u':3,'uu':3,'e':4,'ai':4,'o':5,'au':5,'k':1,'kh':2,'g':3,'gh':4,'ch':5,'c':5,'j':2,'jh':3,'t':3,'th':4,'d':4,'dh':2,'n':2,'p':3,'ph':4,'f':4,'b':5,'bh':1,'m':2,'y':3,'r':4,'l':5,'v':1,'w':1,'sh':2,'s':4,'h':5,'ksh':1,'tr':4}
GRAHA_DHRUVANK = {'Sun':5,'Moon':2,'Mars':2,'Mercury':3,'Jupiter':5,'Venus':3,'Saturn':3,'Rahu':0,'Ketu':0}
SHAYANADI_PHAL_ALL = {
'Sun':{'Shayan':'Apach, mandagni, pittashool, gupt rog, pair mein sujan','Upaveshan':'Karigar kaarya, garibi, vidyaheen, dukhi, doosron ka sevak','Netrapani':'5,9,7,10 bhaav — balwaan dhani. Anya bhaav — nishthur netrarogi','Prakashana':'Punyavaan, dharmic, dhani, daani, rajsi kul','Gamana':'Sadaiv pravas, rogyukt, nidra bhay krodhadi se yukt','Agamana':'Kroor, durbuddhi, kushal, dambhi, kanjoos, parastr mein rat','Samavaas':'Dharmic, dhani, anek vidyaaon se yukt, sundar netra, pavitra aacharan','Aagam':'Sadaiv dukhi, moorkh, kurup kintu dhani','Bhojan':'Stri putra dhan se rahit, jodo mein peeda, sir mein vishesh peeda','Nritya':'Pundit, sundar, vakvatur, shoolrogi, dharmic va dhani','Kautuk':'Utsaahi, mahan putra ka pita, daani, do patniyon wala','Nidra':'Sadaiv pravas, ling guda rogi, daridra, viklang, ati krodhi'},
'Moon':{'Shayan':'Swabhimani, sardi se jaldi prabhavit, kamuk, dhannaashak','Upaveshan':'Rogi, nirdhana, chalaak, kanjoos, mand buddhi','Netrapani':'Bade rog wala, dusht, bahut bolne wala, chalaak, kukaarmi','Prakashana':'Dhani, lamba majboot sharir, kanjoos, teertha premi','Gamana':'Dhanhin, kroorkaarmi, netrogi, shoolrogi, bhayaatur','Agamana':'Swabhimani, pairo mein peeda, gupt paapi, deen, mayavi','Samavaas':'Daani, dharmic, rajpujya, dhani, vaahna sukhi','Aagam':'Vaachal, dharmic, krishnapaksh mein do patniyon wala','Bhojan':'Pushta bimb — sukhi dhani. Ksheen bimb — sarp jal bhay','Nritya':'Balwaan — taktatvar dhani bhogi. Ksheen — rogi durbala','Kautuk':'Dhani, bahut putron wala, daani, anek vidyaaon ka jignasu','Nidra':'Klesh uthaane wala, paapi, rogi, sarvatra maara maara phirta'},
'Mars':{'Shayan':'Sharir par ghav, tvacha ke vividh rog. Lagnasth — pehli santan naash','Upaveshan':'Bahut nikrisht, dhani, kathor, nirdaya, paapi, rogi, viklang','Netrapani':'Lagna mein — netraheen, daridra. Anya — sharirik shithilta','Prakashana':'Dhani, jaldi tushtane wala, buddhimaan, baayein aankh mein chot','Gamana':'Sharir par ghav, stri se kalah, nirdhana, guda rogi','Agamana':'Dhani, aadar yukt, dharmik, prabhu kripa paatr','Samavaas':'Dharmik, adhik sampatti, uchvasth — bahut satva wala','Aagam':'Daksh dhani, bhogi, yash, swastha','Bhojan':'Mitha khane mein ruchi, apmaanit, mahakrodhi, ati utsaahi dhani','Nritya':'Rajpaksh se dhan labh, daani, bhogi, sukhi','Kautuk':'Mitron putron stri se yukt, anek sampattiyon wala, do patni','Nidra':'Dhanraihit, moorkh, mahakrodhi, neecharaagham'},
'Mercury':{'Shayan':'Bhookh se peedit, lumpat, dhoorta','Upaveshan':'Vaagmi, gunvaan, kavya karne wala, pavitra aacharan','Netrapani':'Pairon mein rog, vidya vinay se heen, putra bhi nasht','Prakashana':'Daansheel, dhani, anek vidyaaon se yukt, vedaarth ka gyata','Gamana':'Kaaryakushal, adhik lalchi, stri ke vash mein, kamdukhi','Agamana':'Paapaacharan, neech sangati, do putron wala','Samavaas':'Dhani, dharmic, chirarogi, samarthan prapt karne wala','Aagam':'Paapaacharan, neech sangati se dhan, gupt sthaaon mein rog','Bhojan':'Vaad vivaad se dhanhaani, raja bhay, shir mein rog','Nritya':'Dhani, vidwaan, kavi, prasannachit, sukhi','Kautuk':'Sabka priya, sangeetgya, tvacha mein rog','Nidra':'Bada rog, alpayu, vaad-vivadi, dhanhaani'},
'Jupiter':{'Shayan':'Kamzor swar, dukhi, atyadhik gora, lambi thuddi, shatruon se bhay','Upaveshan':'Dukhi, bahut bolne wala, muh haath pair mein ghav, rajbhay','Netrapani':'Shir mein rog, dhani, neech varn se priti, sangeet nritya premi','Prakashana':'Gunvaan, tejasvi, dhani. 1.10 mein — jagadguru athva raja','Gamana':'Paapi, laalchi, anek mitron wala, vidwaan, pravasik, dhani','Agamana':'Achhi patni wala, gunvaan, lokapriya','Samavaas':'Raja ka sevak ya sahyogi, vidwaan, sundar, kushal vakta dhani','Aagam':'Dharmik, shastraakar, naukr-chaakron va santan sukh yukt','Bhojan':'Maans bhakshan mein ruchi, dhani, kaamuk, santan ka sukh','Nritya':'Raja se sammaan, dhani, shaastragy, vyaakaran shastr ka gyata','Kautuk':'Dhani, apne kul mein agragany, ati aishwaryashali, shakti wala','Nidra':'Sab kaaryon mein moorkhta, garibi, ghar mein punay nahin'},
'Venus':{'Shayan':'Bahut krodhi, dant rogi, nirdhana, bahut lumpat','Upaveshan':'Balwaan, dharmik, dhani, daayein bhaag mein ghav, jodo mein dard','Netrapani':'Netra nasht, 1.7.10 mein — atyadhik garibi va sarvanash','Prakashana':'Kaavyashastr va sangeet ka vidwaan, dhani, dharmic, vaahan yukt','Gamana':'Maata jeevit nahi, baalpan mein rog, apne logon ka viyog','Agamana':'Pairon mein rog, sadaiv utsaahit, bada kalaakaar, dhani','Samavaas':'Raja ka ati vishwaspaatr, sab kaaryon mein kushal, shoolrog','Aagam':'Dhanhaani, stri sukh mein bahut anugrah, bhay yukt','Bhojan':'Kam paachan shakti, doosron ki naukri, bahut dhan kamaane wala','Nritya':'Kushal vakta, vidwaan, kavi, dhani, kaamuk, swabhimani','Kautuk':'Anek prakaar ke sukhon se yukt, maha rikshta, prasann rahne wala','Nidra':'Doosron ki naukri, ninda, veer, adhik bolne wala, bechain'},
'Saturn':{'Shayan':'Bhookh pyaas se peedit, ayushy prathm bhaag rogi, baad mein bhaagyavaan','Upaveshan':'Mote suze ya vaayuvikaar, daad aadi, rajpaksh se dhanhaani','Netrapani':'Moorakh hote hue bhi panditon ki tarah maany, dhani, dharmic','Prakashana':'Raja ka vishesh krupa paatr, dharmik, pandit, pavitra','Gamana':'Mahadhani, anek putron wala, pandit, gunvaan, shreshthi manushya','Agamana':'Pairon mein sujan, ati krodhi, kanjoos, par ninda karne wala','Samavaas':'Putra va dhan se yukt, seekhne padhne ko tatpar, anek ratnon se yukt','Aagam':'Lagna mein — bahut krodhi, rogi, saanp aadi sarispuon ke sambandh','Bhojan':'Apach, mandagni, bawaaseer, vayu shool, netrogi','Nritya':'Dhani, dharmic, vividh sampattiyon se yukt, sab sukh pane wala','Kautuk':'Raja ka vishwaspaatr, kaaryudaksh, dharmic, pandit','Nidra':'Dhani, vidwaan, pavitra aacharan, pittashool, do patniyon wala'},
'Rahu':{'Shayan':'Sadaiv mahan dukh va klesh. Mithun Sinh Vrishabh mein — sab sukh','Upaveshan':'Pairon mein rog, daad tvacharog, dhanhaani, bahut ghamandi','Netrapani':'Aankhon mein rog, dushton serpaaon shatruon va choron ka bhay','Prakashana':'Dharmik, sadaiv desh videshon mein, utsaahi, saatvik, rajkarmachaari','Gamana':'Bahut santaanon wala, vidwaan, dhani, daani, rajmaanya','Agamana':'Krodhi, dhan va buddhi se rahit, chalaak, kanjoos, kaamuk','Samavaas':'Vidwaan, kanjoos, anek gunon wala, dharmic, dhan yukt','Aagam':'Sab prakaar ke dukhon se yukt, mitron bandhuo ka naash','Bhojan':'Bhojan mein mushkil, viklang, mand buddhi, stri putra sukh se rahit','Nritya':'Dhani, bahut putron wala, daani, pandit, pittashool','Kautuk':'Sab gunon se yukt, nana dhano se dhani','Nidra':'Jeevan mein bahut shok, stri putron ko paane wala, dhairyashali'},
'Ketu':{'Shayan':'1.2.3.6 raashiyon mein dhanvarddhak. Anya raashiyon mein rogvarddhak','Upaveshan':'Tvacharogdayak, shatru raja chor aadi sarpdi ki shanka se peedit','Netrapani':'Netra mein rog, dushton sarpaadon se peedit, rajadi se peeda','Prakashana':'Dharmik, dhani, sadaiv pravas, utsaahi, rajsevak','Gamana':'Bahut putra, bahut dhan, vidwaan, gunvaan, daani','Agamana':'Anek rog, dhan ki haani, dant ghaati, mahaarogi, par nindak','Samavaas':'Vaachal, bahut garvita, dhoorta vidyaa visharad','Aagam':'Paap kaaryon mein agragany, bandhuo se vivaad, shatru rog peedit','Bhojan':'Sadaiv bhookh se peedit, daridra, rogi, maara maara phirta','Nritya':'Rog ke kaaran viklang, bahut palak jhapakne wali aankhein','Kautuk':'Apne star se gira hua, duraachari, dariddi, bhramak','Nidra':'Dhana dhaanya ka khub sukh, gunon va kalaaon se yukt hokar jeevan'},
}

def get_naam_akshar_ank(naam):
    if not naam: return 1
    naam = naam.lower().strip()
    for akshar in sorted(NAAM_AKSHAR_ANK.keys(), key=len, reverse=True):
        if naam.startswith(akshar):
            return NAAM_AKSHAR_ANK[akshar]
    return 1

def get_naam_cheshta(avastha_name, graha_name, naam):
    try:
        avastha_num = AVASTHA_NAMES.index(avastha_name) + 1
        naam_ank = get_naam_akshar_ank(naam)
        dhruvank = GRAHA_DHRUVANK.get(graha_name, 3)
        total = (avastha_num * avastha_num * naam_ank) + dhruvank
        shesha = total % 12
        final = shesha % 3
        if final == 1: return 'Drishti (Madhyam Phal)'
        elif final == 2: return 'Cheshta (Sampurna Phal)'
        else: return 'Vicheeshta (Matra Phal)'
    except: return 'Cheshta (Sampurna Phal)'

def get_shayanadi_phal_with_naam(graha_avastha_result, naam=''):
    enriched = {}
    for planet, data in graha_avastha_result.items():
        enriched[planet] = dict(data)
        shayanadi = data.get('shayanadi', 'Shayan')
        enriched[planet]['shayanadi_phal'] = SHAYANADI_PHAL_ALL.get(planet, {}).get(shayanadi, '')
        if naam:
            enriched[planet]['naam_cheshta'] = get_naam_cheshta(shayanadi, planet, naam)
    return enriched
"""

if 'SHAYANADI_PHAL_ALL' not in content:
    content = content.replace("def get_all_graha_avastha", shayanadi_phal_code + "\ndef get_all_graha_avastha")
    print("Added!")
else:
    print("Already exists!")

old_ga = "        graha_avastha_raw = get_all_graha_avastha(planets_with_houses, lagna, sun_lon)\n        naam = getattr(data, 'name', '') or ''\n        graha_avastha = get_shayanadi_phal_with_naam(graha_avastha_raw, naam)"
old_ga2 = "        graha_avastha = get_all_graha_avastha(planets_with_houses, lagna, sun_lon)"

if old_ga not in content and old_ga2 in content:
    content = content.replace(old_ga2, "        graha_avastha_raw = get_all_graha_avastha(planets_with_houses, lagna, sun_lon)\n        naam = getattr(data, 'name', '') or ''\n        graha_avastha = get_shayanadi_phal_with_naam(graha_avastha_raw, naam)")
    print("Endpoint updated!")

open('/root/jyotish-api/main.py', 'w').write(content)
print("Done!")
