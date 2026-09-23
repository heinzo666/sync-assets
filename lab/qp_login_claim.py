#!/usr/bin/env python3
"""Pod-side: log into an EXISTING QuantumProxies account (browser = genuine guard),
then pull user state: token, free-trial status/claim, proxy credentials, bandwidth."""
import json, os, sys, time

B = "https://app.quantumproxies.io"
GHTOK_FILE = "/tmp/.ghtok"
REPO = "heinzo666/sync-assets"


def gh(method, path, body=None):
    import urllib.request
    tok = open(GHTOK_FILE).read().strip()
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    req = urllib.request.Request(url, method=method,
                                 data=(json.dumps(body).encode() if body else None),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Accept": "application/vnd.github+json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode()), r.status


def put(path, text, msg="up"):
    import base64 as b64m
    sha = None
    try:
        d, _ = gh("GET", path)
        sha = d.get("sha")
    except Exception:
        pass
    body = {"message": msg, "content": b64m.b64encode(text.encode()).decode()}
    if sha:
        body["sha"] = sha
    try:
        _, st = gh("PUT", path, body)
        return st
    except Exception as ex:
        return f"ERR:{type(ex).__name__}"


def main():
    creds_path = sys.argv[1] if len(sys.argv) > 1 else "lab/qcreds.json"
    tag_out = os.path.splitext(os.path.basename(creds_path))[0]
    # fetch creds written by our side just before launching this task
    d, _ = gh("GET", creds_path)
    import base64 as b64m
    creds = json.loads(b64m.b64decode(d["content"]).decode())
    em, pw = creds["email"], creds["pw"]
    print(f"[start] {em}", flush=True)

    rep = {"email": em, "stages": {}}

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True,
                               args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = br.new_context(locale="en-US",
                             user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                         "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
                             viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()

        def swt(ms):
            try:
                pass
            finally:
                try:
                    pg.wait_for_timeout(ms)
                except Exception:
                    pass

        errs = []
        try:
            pg.goto(B + "/login", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(2800)
            pg.fill("input[name=email]", em, timeout=15000)
            pg.fill("input[name=password]", pw, timeout=8000)
            lb = pg.query_selector("//button[normalize-space()='Log In']") or \
                 pg.query_selector("button:has-text('Log In')")
            lb.click(timeout=12000)
            t0 = time.time(); tok = None
            while time.time() - t0 < 80:
                pg.wait_for_timeout(1100)
                tok = pg.evaluate("localStorage.getItem('token')")
                if tok or "/dashboard" in pg.url:
                    break
                e = pg.query_selector("text=/invalid|incorrect|verif|wrong/i")
                if e and e.is_visible():
                    tx = ((e.inner_text() or "")[:90]).replace("\n", " ")
                    if tx and tx not in errs:
                        errs.append(tx)
            rep["stages"]["url"] = pg.url
            rep["stages"]["errs"] = errs[:6]
            rep["stages"]["token"] = tok[:40] if isinstance(tok, str) else None
            print(f"[login] url={pg.url} tok={'Y' if tok else 'N'} errs={errs[:2]}", flush=True)

            apis = {}
            paths_get = ["/api/v1/user", "/api/v1/user/free-trial/status",
                         "/api/v1/residential-basic/whitelist",
                         "/api/v1/generator/countries",
                         "/api/v1/user/balance-history?limit=1",
                         "/api/v1/residential-basic/topup"]
            for a in paths_get:
                apis[a] = pg.evaluate(
                    """async (path)=>{try{
                       const t=localStorage.getItem('token');
                       const h=t?{authorization:'Bearer '+t,accept:'application/json,*/*'}
                               :{accept:'application/json,*/*'};
                       const r=await fetch(path,{credentials:'include',headers:h});
                       return {code:r.status,body:(await r.text()).slice(0,700)};}
                       catch(e){return{err:String(e).slice(0,70)}}}""", a)
            claim = pg.evaluate(
                """async ()=>{
                   try{
                     const s=JSON.stringify({});
                     let g=null;
                     try{g=window.qdGuard ? window.qdGuard.sign(s):null;}catch(e){}
                     const h={'content-type':'application/json','accept':'application/json,*/*'};
                     if(g){h['X-QD-TS']=String(g.ts);h['X-QD-Token']=g.token;}
                     const t=localStorage.getItem('token'); if(t) h.authorization='Bearer '+t;
                     const r=await fetch('/api/v1/user/free-trial/claim',
                        {method:'POST',credentials:'include',headers:h,body:s});
                     return {code:r.status,body:(await r.text()).slice(0,700)};
                   }catch(e){return{err:String(e).slice(0,90)}}"""
            )
            rep["stages"]["apis"] = apis
            rep["stages"]["claim"] = claim
            print("[claim]", json.dumps(claim)[:220], flush=True)
        except Exception as ex:
            rep["stages"]["exc"] = f"{type(ex).__name__}:{str(ex)[:160]}"

        try:
            pg.screenshot(path=f"/tmp/login_{tag_out}.png")
        except Exception:
            pass
        br.close()

    txt = json.dumps(rep, indent=1)
    st = put(f"lab/qresult_{tag_out}.json", txt, f"qres {tag_out}")
    print("[push]", st, flush=True)


if __name__ == "__main__":
    main()
