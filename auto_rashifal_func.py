import swisseph as swe
from datetime import datetime
import google.generativeai as genai
import json as jsonlib

RASHI_NAMES = ['Mesh','Vrishabh','Mithun','Kark','Simha','Kanya','Tula','Vrishchik','Dhanu','Makar','Kumbh','Meen']
RASHI_HI = ['मेष','वृषभ','मिथुन','कर्क','सिंह','कन्या','तुला','वृश्चिक','धनु','मकर','कुम्भ','मीन']
PEAK = {'Sun':(1,10),'Mars':(1,10),'Mercury':(0,30),'Moon':(0,30),'Jupiter':(10,20),'Venus':(10,20),'Saturn':(21,30),'Rahu':(21,30),'Ketu':(21,30)}
