
import sys,time,json,os,re,subprocess
em,pw,tag,num,act_id=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]
import glob as _g
cands=_g.glob("/tmp/pw/**/chrome-headless-shell", recursive=True)+_g.glob("/tmp/pw/**/headless_shell", recursive=True)
CH=sorted(cands)[0] if cands else None
NK=os.environ.get("NK","")
def sms(path):
    return subprocess.run(["curl","-sL","--max-time","25","--socks5-hostname","127.0.0.1:19050",
      "-H",f"Authorization: Bearer {NK}", f"https://www.numberotp.com{path}"],
      capture_output=True,text=True).stdout
from playwright.sync_api import sync_playwright
ROUNDS=int(os.environ.get("ROUNDS","16"))
with sync_playwright() as pl:
  b=pl.chromium.launch(headless=True,executable_path=CH,args=["--no-sandbox","--disable-dev-shm-usage"])
  ctx=b.new_context(locale="en-US",user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131 Safari/537.36")
  pg=ctx.new_page()
  out={"tag":tag,"email":em,"num":num}
  print("[ip]",pg.goto("https://api.ipify.org",wait_until="domcontentloaded",timeout=45000).text()[:40],flush=True)
  def ev(code,a=None):
     for _ in range(6):
       try:return pg.evaluate(code,a) if a is not None else pg.evaluate(code)
       except Exception as ex:
         if "context" in str(ex):time.sleep(2);continue
         return {"err":str(ex)[:80]}
     return {"err":"ctx"}
  dash=False
  for rnd in range(ROUNDS):
    try:
      pg.goto("https://app.quantumproxies.io/login",wait_until="domcontentloaded",timeout=80000)
      pg.wait_for_timeout(3400)
      ins=[e.get_attribute('name') for e in pg.query_selector_all('input')]
      if not any(n=='email' for n in ins):
          # allow page settle / challenge variant
          pg.reload(wait_until="domcontentloaded"); pg.wait_for_timeout(2600)
          ins=[e.get_attribute('name') for e in pg.query_selector_all('input')]
          if not any(n=='email' for n in ins):
             print(f"[r{rnd}] no-form reload-wait",flush=True); time.sleep(12); continue
      pg.fill("input[name=email]",em); pg.fill("input[name=password]",pw)
      rm=pg.query_selector("input[name=rememberMe]")
      if rm and not rm.is_checked():
          try:rm.check(timeout=2500)
          except Exception:pass
      time.sleep(0.9)
      pg.evaluate("()=>{const f=document.querySelector('form'); f&&f.requestSubmit();}")
      t0=time.time();ok=False
      while time.time()-t0<55:
        time.sleep(1)
        try:
            cur=str(pg.url)
            if "/dashboard" in cur: ok=True;break
        except Exception:pass
      print(f"[r{rnd}] {'DASH' if ok else 'miss'} url={str(pg.url)[-26:]}",flush=True)
      if ok: dash=True; break
      time.sleep(6)
    except Exception as ex:
      print("exc",type(ex).__name__,str(ex)[:70],flush=True); time.sleep(4)
  out["dashboard"]=dash
  if dash:
    time.sleep(2.5)
    sent=None
    for path,body in [
        ("/api/v1/phone-number-verification/send-otp",{"phoneNumber":num}),
        ("/api/v1/user/phone-number-verification/send-otp",{"phoneNumber":num})]:
       payload=ev("""async({path,b})=>{const s=JSON.stringify(b);let g=null;
          try{g=window.qdGuard?window.qdGuard.sign(s):null;}catch(e){}
          const h={'content-type':'application/json','accept':'application/json,*/*'};
          if(g){h['X-QD-TS']=String(g.ts);h['X-QD-Token']=g.token;}
          const r=await fetch(path,{method:'POST',credentials:'include',headers:h,body:s});
          return {code:r.status,body:(await r.text()).slice(0,600)};}""",{"path":path,"b":body})
       txt=(payload.get('body') or "").replace(' ','')
       print("[sendotp]",path,'->',txt[:200],flush=True)
       if '"success"' in txt: sent=path;break
       time.sleep(3)
    out["sent"]=sent
    otp=None
    if sent:
      dl=time.time()+170
      while time.time()<dl:
        j=sms(f"/v1/activations/{act_id}")
        try:
           dd=json.loads(j).get("data") or {}
           code=dd.get("otp") or dd.get("code")
           full=str(dd.get("full_sms") or dd.get("sms") or "")
           st=dd.get("status")
           if not code:
              m=re.search(r"\b(\d{4,8})\b", full)
              code=m.group(1) if m else None
           print("[poll]",st,code,flush=True)
           if code: otp=code; break
        except Exception: pass
        time.sleep(5)
    out["otp"]=bool(otp)
    vres=None
    if otp:
      for vp in ["/api/v1/phone-number-verification/verify-otp","/api/v1/user/phone-number-verification/verify-otp"]:
         vr=ev("""async({path,b})=>{const s=JSON.stringify(b);let g=null;
            try{g=window.qdGuard?window.qdGuard.sign(s):null;}catch(e){}
            const h={'content-type':'application/json','accept':'application/json,*/*'};
            if(g){h['X-QD-TS']=String(g.ts);h['X-QD-Token']=g.token;}
            const r=await fetch(path,{method:'POST',credentials:'include',headers:h,body:s});
            return {code:r.status,body:(await r.text()).slice(0,700)};}""",{"path":vp,"b":{"otp":otp}})
         print("[verify]",vp,json.dumps(vr)[:240],flush=True)
         if '"success"' in ((vr.get('body') or '').replace(' ','')): vres=vp;break
         time.sleep(2)
    out["verified"]=vres
    cl=ev("""async()=>{const s=JSON.stringify({});let g=null;
      try{g=window.qdGuard?window.qdGuard.sign(s):null;}catch(e){}
      const h={'content-type':'application/json','accept':'application/json,*/*'};
      if(g){h['X-QD-TS']=String(g.ts);h['X-QD-Token']=g.token;}
      const r=await fetch('/api/v1/user/free-trial/claim',{method:'POST',credentials:'include',headers:h,body:s});
      return {code:r.status,rb:(await r.text()).slice(0,1000)};}""")
    ft=ev("""async()=>{const r=await fetch('/api/v1/user/free-trial/status',{credentials:'include',headers:{accept:'application/json,*/*'}});return r.status+'|'+((await r.text())||'').slice(0,1400);}""")
    wl={}
    for pref in ["/api/v1/residential-basic/whitelist","/api/v1/user/residential-basic/whitelist",
                 "/api/v1/residential-premium/locations","/api/v1/residential-basic/topup"]:
        wl[pref]=ev("""async(p)=>{const r=await fetch(p,{credentials:'include',headers:{accept:'application/json,*/*'}});return {code:r.status,body:(await r.text()).slice(0,1200)};}""",pref)
    out.update({"claim":cl,"ft":ft,"wl":wl})
    try:pass
    except Exception:pass
    try:pass
    except Exception:pass
  open(f"{R}/workspace-root/work/qpfactory/login_results.jsonl","a").write(json.dumps(out)+"\n")
  slim={k:v for k,v in out.items() if k!='wl'}
  print(json.dumps(slim,indent=1)[:1600])
  b.close()
