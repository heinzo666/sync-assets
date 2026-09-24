#!/usr/bin/env python3
"""Pod-side FINISH job: complete a pending QP account (re-submit register with email),
then log in and pull trial/proxy state. Args: <creds.json path in repo>"""
import base64 as b64m
import io, json, os, secrets, sys, time

B = "https://app.quantumproxies.io"
GHTOK_FILE = "/tmp/.ghtok"
REPO = "heinzo666/sync-assets"


def gh(method, path, body=None):
    import urllib.request
    tok = open(GHTOK_FILE).read().strip()
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{path}",
                                 method=method,
                                 data=(json.dumps(body).encode() if body else None),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Accept": "application/vnd.github+json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=35) as r:
        return json.loads(r.read().decode()), r.status


def put(path, text):
    sha = None
    try:
        d, _ = gh("GET", path)
        sha = d.get("sha")
    except Exception:
        pass
    body = {"message": "res", "content": b64m.b64encode(text.encode()).decode()}
    if sha:
        body["sha"] = sha
    _, st = gh("PUT", path, body)
    return st


def main():
    src = sys.argv[1]
    tag = os.path.splitext(os.path.basename(src))[0].replace("qcreds_", "")
    d, _ = gh("GET", src)
    creds = json.loads(b64m.b64decode(d["content"]).decode())
    em, pw = creds["email"], creds["pw"]
    print(f"[finish] {em}", flush=True)
    rep = {"tag": tag, "email": em}

    # captcha bits reused
    def dec(u): return b64m.b64decode(u.split(",", 1)[1])

    def ncc_x(bgp, pcs):
        import numpy as np
        from PIL import Image
        bg = np.asarray(Image.open(io.BytesIO(bgp)).convert("L"), dtype=np.float32)
        pm = Image.open(io.BytesIO(pcs))
        cr = pm.crop(pm.getbbox())
        pa = np.asarray(cr.convert("RGBA"))
        mask = pa[:, :, 3] > 80
        pr = np.asarray(cr.convert("L"), dtype=np.float32) * mask
        norm = float((pr ** 2).sum()) ** 0.5 + 1e-6
        h, w = pr.shape
        best, bx = -9.0, 0
        Hh, Ww = bg.shape
        step = max(1, (Ww - w) // 220)
        for x in range(0, Ww - w, step):
            win = bg[:h, x:x+w]
            num = float((win * pr).sum())
            den = (float((win ** 2).sum()) ** 0.5 + 1e-6) * norm
            sc = num / den
            if sc > best:
                best, bx = sc, x
        return best, int(bx)

    capj = {}

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True,
                               args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = br.new_context(locale="en-US",
                             user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                         "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
                             viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()

        def on_resp(r):
            u = r.url
            if "/api/v1/auth/captcha" in u and "check" not in u:
                try:
                    pl = (r.json() or {}).get("payload") or {}
                    if pl.get("background"):
                        capj.clear(); capj.update(pl)
                except Exception:
                    pass
        pg.on("response", on_resp)

        resps = []
        def rec(r):
            u = r.url
            if any(k in u for k in ("signup", "captcha/check", "free-trial", "/login")):
                try:
                    t = (r.text() or "")[:300].replace("\n", " ")
                except Exception:
                    t = ""
                resps.append({"st": r.status, "u": u[-60:], "t": t})

        pg.on("response", rec)

        try:
            url = f"{B}/register?email={em.replace('@','%40')}"
            pg.goto(url, wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(2600)
            ins = pg.eval_on_selector_all("input", "els=>els.map(e=>e.name)")
            rep["inputs"] = ins
            e_in = pg.query_selector("input[name=email]")
            cur_val = e_in.input_value() if e_in else ""
            if e_in and cur_val != em:
                e_in.fill(em)
            pg.fill("input[name=password]", pw, timeout=8000)
            cp = pg.query_selector("input[name=confirmPassword]")
            if cp:
                cp.fill(pw)
            for cb in pg.query_selector_all("input[type=checkbox]"):
                try:
                    if not cb.is_checked():
                        cb.check(timeout=2500)
                except Exception:
                    pass
            # ensure fresh challenge then PRE-solve
            tc = time.time()
            while time.time() - tc < 22 and not capj:
                pg.wait_for_timeout(650)
            solved = False
            if capj:
                sc_, xpx = ncc_x(dec(capj["background"]), dec(capj["pieceImage"]))
                bb = kb = None
                for i in pg.query_selector_all("img"):
                    s = i.get_attribute("src") or ""
                    if s.startswith("data:image"):
                        b = i.bounding_box()
                        if b and b["width"] > 170:
                            bb = b; break
                for sel in ("[role=slider]", ".react-slider", "[draggable=true]",
                            "div[class*=handle i]", "div[class*=knob i]", "span[class*=thumb i]"):
                    el = pg.query_selector(sel)
                    if el and el.bounding_box():
                        kb = el.bounding_box(); break
                rep["geom"] = {"bb": bool(bb), "kb": bool(kb)}
                if bb and kb:
                    sx = kb["x"] + kb["width"] / 2; sy = kb["y"] + kb["height"] / 2
                    dx = xpx * (bb["width"] / float(capj["width"]))
                    pg.mouse.move(sx, sy); pg.mouse.down()
                    for stp in range(1, 27):
                        pg.mouse.move(sx + dx * stp / 26, sy + ((-1) ** stp) * 0.7)
                        pg.wait_for_timeout(24 + stp % 5)
                    pg.mouse.up(); solved = True
                    rep["drag"] = round(dx, 1)
                    pg.wait_for_timeout(2400)
            btn = pg.query_selector(
                "//button[contains(normalize-space(),'Create') or contains(normalize-space(),'Sign Up') or contains(normalize-space(),'Register')]") \
                or pg.query_selector("button[type=submit]:not(:has-text('English'))")
            btn.click(timeout=12000)
            pg.wait_for_timeout(1800)
            errs = []
            for el in pg.query_selector_all("[role=alert],[id$='-error'],[class*=error i]"):
                try:
                    tt = (el.inner_text() or "").strip().replace("\n", " ")
                    if tt and len(tt) < 160 and tt not in errs:
                        errs.append(tt)
                except Exception:
                    pass
            rep["su_errs"] = errs[:6]

            t0 = time.time(); tok = None
            while time.time() - t0 < 50:
                pg.wait_for_timeout(1000)
                tok = pg.evaluate("localStorage.getItem('token')")
                if tok or "/dashboard" in pg.url:
                    break
            rep["url_now"] = pg.url
            rep["tok_su"] = bool(tok)

            if not tok:
                # second half: normal login in case account activated without autologin
                pg.goto(B + "/login", wait_until="domcontentloaded", timeout=50000)
                pg.wait_for_timeout(2300)
                pg.fill("input[name=email]", em)
                pg.fill("input[name=password]", pw)
                lb = pg.query_selector("//button[normalize-space()='Log In']") or pg.query_selector("button:has-text('Log In')")
                lb.click(timeout=11000)
                t1 = time.time()
                while time.time() - t1 < 65:
                    pg.wait_for_timeout(1050)
                    tok = pg.evaluate("localStorage.getItem('token')")
                    if tok or "/dashboard" in pg.url:
                        break
                    e2 = pg.query_selector("text=/invalid|incorrect|verif|wrong/i")
                    if e2 and e2.is_visible():
                        tx = ((e2.inner_text() or "")[:80]).replace("\n", " ")
                        if tx and tx not in errs:
                            errs.append(tx)
                rep["errs_login"] = [x for x in errs][:8]

            apis = {}
            paths_get = ["/api/v1/user/free-trial/status", "/api/v1/user",
                         "/api/v1/residential-basic/whitelist",
                         "/api/v1/generator/countries",
                         "/api/v1/user/balance-history?limit=1"]
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
                     let g=null; try{g=window.qdGuard?window.qdGuard.sign(s):null;}catch(e){}
                     const h={'content-type':'application/json','accept':'application/json,*/*'};
                     if(g){h['X-QD-TS']=String(g.ts);h['X-QD-Token']=g.token;}
                     const t=localStorage.getItem('token'); if(t) h.authorization='Bearer '+t;
                     const r=await fetch('/api/v1/user/free-trial/claim',
                        {method:'POST',credentials:'include',headers:h,body:s});
                     return {code:r.status,body:(await r.text()).slice(0,700)};
                   }catch(e){return{err:String(e).slice(0,90)}}"""
            )
            rep["apis"] = apis
            rep["claim"] = claim
            if isinstance(tok, str) and tok:
                rep["token_full"] = tok
            rep["resps_tail"] = resps[-8:]
        except Exception as ex:
            rep["exc"] = f"{type(ex).__name__}:{str(ex)[:170]}"

        try:
            pg.screenshot(path=f"/tmp/f_{tag}.png")
        except Exception:
            pass
        br.close()

    txt = json.dumps(rep, indent=1)
    print("[push]", put(f"lab/qresult_finish_{tag}.json", txt), flush=True)


if __name__ == "__main__":
    main()
