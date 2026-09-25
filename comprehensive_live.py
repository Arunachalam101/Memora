import subprocess, sys, time, requests, json, os
from datetime import date, datetime
p=subprocess.Popen([sys.executable,'app.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
BASE='http://127.0.0.1:5000'
def show(label,r):
    try: body=r.json()
    except Exception: body=r.text[:300]
    ok=200<=r.status_code<300
    print(f'{"PASS" if ok else "ERROR"} {label}: {r.status_code} {json.dumps(body,default=str)}')
    return body if isinstance(body,(dict,list)) else {}
def call(s,method,path,**kw):
    try: return show(method+' '+path, s.request(method,BASE+path,timeout=5,**kw))
    except Exception as e: print('ERROR',method,path,str(e)); return {}
for _ in range(30):
    try:
        if requests.get(BASE+'/',timeout=.2).status_code: break
    except Exception: pass
patient=requests.Session(); caregiver=requests.Session()
print('=== AUTHENTICATION ===')
r=patient.post(BASE+'/login',data={'name':'Priya Devi','pin':'1234'},allow_redirects=False); show('POST /login patient',r)
r=caregiver.post(BASE+'/login',data={'name':'Anil Sharma','pin':'5678'},allow_redirects=False); show('POST /login caregiver',r)
patients=call(caregiver,'GET','/api/users/patients')
ids=[]
if isinstance(patients,list): ids=[x.get('id') for x in patients if isinstance(x,dict)]
if isinstance(patients,dict): ids=[x.get('id') for x in patients.get('patients',[]) if isinstance(x,dict)]
patient_id=ids[0] if ids else 1
print('Using patient_id=',patient_id)
print('=== MEMORY ALBUM ===')
mem=call(patient,'GET','/api/memory/people')
p=call(patient,'POST','/api/memory/people',json={'patient_id':patient_id,'name':'Test Person','relationship':'Friend','notes':'Created by comprehensive test'})
pid=p.get('id') if isinstance(p,dict) else None
if pid:
    call(patient,'PUT',f'/api/memory/people/{pid}',json={'name':'Updated Person','relationship':'Friend','notes':'Updated'})
    call(patient,'DELETE',f'/api/memory/people/{pid}')
call(patient,'GET','/api/memory/people')
pl=call(patient,'POST','/api/memory/places',json={'patient_id':patient_id,'name':'Test Place','location':'Test City','description':'Created by comprehensive test','notes':'Test'})
plid=pl.get('id') if isinstance(pl,dict) else None
if plid:
    call(patient,'PUT',f'/api/memory/places/{plid}',json={'name':'Updated Place','location':'Updated City','description':'Updated','notes':'Updated'})
    call(patient,'DELETE',f'/api/memory/places/{plid}')
call(patient,'GET','/api/memory/places')
mm=call(patient,'POST','/api/memory/memories',json={'patient_id':patient_id,'title':'Test Memory','content':'A test memory','description':'Test description','category':'general','date':str(date.today())})
mid=mm.get('id') if isinstance(mm,dict) else None
if mid:
    call(patient,'PUT',f'/api/memory/memories/{mid}',json={'title':'Updated Memory','content':'Updated content','description':'Updated','category':'general','date':str(date.today())})
    call(patient,'DELETE',f'/api/memory/memories/{mid}')
call(patient,'GET','/api/memory/memories')
print('=== MOOD ===')
call(patient,'POST','/api/mood/entries',json={'patient_id':patient_id,'mood':'happy','notes':'Comprehensive test'})
call(patient,'GET','/api/mood/today'); call(patient,'GET','/api/mood/history')
print('=== REMINDERS ===')
rem=call(patient,'POST','/api/reminders',json={'user_id':patient_id,'title':'Test Reminder','description':'Comprehensive test','date':str(date.today()),'time':'12:00','category':'general'})
rid=rem.get('id') if isinstance(rem,dict) else None
call(patient,'GET',f'/api/reminders/{patient_id}')
if rid:
    call(patient,'PUT',f'/api/reminders/{rid}',json={'title':'Updated Reminder','description':'Updated','date':str(date.today()),'time':'13:00','category':'general'})
    call(patient,'DELETE',f'/api/reminders/{rid}')
print('=== SAFETY ===')
sos=call(patient,'POST','/api/safety/sos',json={'patient_id':patient_id,'location':'Test location','notes':'Test SOS'})
call(patient,'GET','/api/safety/alerts')
aid=sos.get('id') if isinstance(sos,dict) else None
if aid: call(patient,'POST',f'/api/safety/alerts/{aid}/resolve',json={})
print('=== GAMES / PROGRESS ===')
call(patient,'POST','/api/games/log',json={'user_id':patient_id,'game_type':'memory-match','score':80,'duration':30,'correct_answers':8,'total_questions':10})
call(patient,'GET',f'/api/progress/{patient_id}')
p.terminate(); p.wait(timeout=5)
