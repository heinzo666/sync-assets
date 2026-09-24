#!/usr/bin/env python3
"""HG-side QP registration core (no browser): stdlib + requests + Pillow + local node signer.
Args: <creds json path in repo>   Env expected: HOME, PATH includes nodenv."""
import base64 as b64m
import io, json, os, random, secrets, subprocess, sys, time

B = "https://app.quantumproxies.io"
REPO = "heinzo666/sync-assets"


def gh_fetch_text(path):
    tok = open(os.path.expanduser("~/.ghr_tk")).read().strip()
    import urllib.request
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{path}",
                                 headers={"Authorization": "Bearer " + tok,
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=35) as r:
        d = json.loads(r.read().decode())
    return b64m.b64decode(d["content"]).decode()


def put_out(name, text):
    tok = open(os.path.expanduser("~/.ghr_tk")).read().strip()
    import urllib.request
    url = f"https://api.github.com/repos/{REPO}/contents/lab/hgout/{name}"
    sha = None
    try:
        req0 = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
        with urllib.request.urlopen(req0, timeout=25) as r:
            sha = json.loads(r.read().decode()).get("sha")
    except Exception:
        pass
    body = {"message": "qp res", "content": b64m.b64encode(text.encode()).decode()}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, method="PUT", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


# ---- captcha helpers ----
def dec(u):
    return b64m.b64decode(u.split(",", 1)[1])


def ncc_x_pure(bgp, pcs):
    """No-numpy fallback: coarse L1 correlation."""
    from PIL import Image
    bg = Image.open(io.BytesIO(bgp)).convert("L")
    pc = Image.open(io.BytesIO(pcs))
    cr = pc.crop(pc.getbbox()).convert("RGBA")
    Ww, Hh = bg.size
    w, h = cr.size
    bgl = list(bg.getdata())
    prr = []
    for i in range(w * h):
        r, g, b, a = cr.getdata()[i]
        prr.append((0.299*r+0.587*g+0.114*b) if a > 80 else None)
    best, bx = -9e18, 0
    step = max(1, (Ww - w)//160)
    for x0 in range(0, Ww - w, step):
        acc = 0.0
        idx = 0
        for y in range(h):
            row = y * Ww
            base = row + x0
            for xx in range(w):
                v = prr[idx]; idx += 1
                if v is not None:
                    d = bgl[base + xx] - v
                    acc -= d*d
        if acc > best:
            best, bx = acc, x0
    return float(best), int(bx)


def ncc_x(bgp, pcs):
    try:
        import numpy as np
    except Exception:
        return ncc_x_pure(bgp, pcs)
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


def mk_trace(xe):
    t = int(time.time() * 1000); dur = 1800 + random.randrange(900)
    st = max(0, xe - 70 - random.randrange(50)); ov = random.randrange(15, 60)
    out = []
    import math
    def ez(i):
        i /= 90.0
        return 3 * i * i - 2 * i * i * i
    for i in range(91):
        jx = st + (xe + ov - st) * ez(i) + (random.randrange(160) - 80) / 170.0 * (1 - i / 92.0)
        tt = t + int(dur * i / 88) + random.randrange(11) - 5
        if out and tt <= out[-1]["t"]:
            tt = out[-1]["t"] + 1 + random.randrange(13)
        out.append({"x": round(jx, 2), "t": tt})
    out.append({"x": float(max(0, xe)), "t": out[-1]["t"] + 10 + random.randrange(24)})
    return out[:400]


def main():
    cred_path = sys.argv[1]
    home = os.path.expanduser("~")
    nodebin = os.path.join(home, "nodenv", "bin", "node")
    guardjs = os.path.join(home, "qpw", "qdm_pod.cjs")
    signjs = os.path.join(home, "qpw", "qdsign4.js")

    tokfile = os.path.join(home, ".ghr_tk")
    cj = json.loads(gh_fetch_text(cred_path)) if not os.path.exists("/tmp/"+os.path.basename(cred_path)) \
        else json.load(open("/tmp/" + os.path.basename(cred_path)))
    em, pw = cj["email"], cj["pw"]
    print("[start]", em, flush=True)

    # ensure js assets present locally on box
    for src, dstp in (("lab/qdm_pod.cjs", guardjs), ("lab/qdsign4.js", signjs)):
        if not os.path.exists(dstp):
            txt = gh_fetch_text(src)
            open(dstp, "w").write(txt)

    def sign(body_str):
        env = {**os.environ, "QD_GUARD": guardjs}
        r = subprocess.run([nodebin, signjs, body_str], env=env,
                           capture_output=True, text=True, timeout=40)
        for ln in (r.stdout or "").splitlines():
            if ln.startswith("RESULT"):
                d = json.loads(ln.replace("RESULT ", ""))
                return {"X-QD-TS": str(d["ts"]), "X-QD-Token": d["token"]}
        print("[signfail]", (r.stderr or "")[:150], flush=True)
        return {}

    import requests
    s = requests.Session()
    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    s.headers.update({"user-agent": UA})
    rep = {"tag": cj.get("tag"), "email": em}

    try:
        s.get(B + "/register", timeout=45)
    except Exception as ex:
        print("[warm-exc]", type(ex).__name__, flush=True)

    cap = {}
    for k in range(8):
        try:
            g = s.get(B + "/api/v1/auth/captcha", params={"cache": "no-store"},
                      headers={"accept": "*/*", "referer": B + "/register"}, timeout=45)
            if g.status_code == 200:
                cap = g.json().get("payload") or {}
                break
            time.sleep(7)
        except Exception as ex:
            print(f"[cap{k}]", type(ex).__name__, flush=True)
            time.sleep(7)
    if not cap:
        rep["stage"] = "captcha_unreachable"
        print("CAP_FAIL", flush=True)
        put_out(f"qpres_{cj.get('tag','na')}_{int(time.time())}.txt",
                json.dumps(rep))
        return

    rr, hx = ncc_x(dec(cap["background"]), dec(cap["pieceImage"]))
    W, PWpx = int(cap["width"]), int(cap["piece"])
    tx = max(0, min(W - PWpx, int(hx)))
    tr = mk_trace(tx)
    payload = {"email": em, "password": pw,
               "captcha": {"token": cap["token"], "x": tx, "trace": tr}}
    body = json.dumps(payload, separators=(",", ":"))
    sig = sign(body)
    think = 1.8 + random.randrange(140) / 100.0
    time.sleep(think)
    r = s.post(B + "/api/v1/auth/signup", data=body.encode(),
               headers={**sig, "content-type": "application/json",
                        "origin": B, "referer": B + "/register"},
               timeout=65)
    rep["reg_status"] = r.status_code
    rep["reg_body"] = (r.text or "")[:300].replace("\n", " ")
    print("[reg]", r.status_code, rep["reg_body"][:200], flush=True)

    ok = '"response"' in (r.text or "").replace(" ", "")
    rep["registered"] = ok
    if ok:
        # attempt immediate login-action replication
        act = "7e73abdbb0e547db14bdf3ada96646b53b903e35a2"
        dev = secrets.token_hex(16)
        arr = [em, pw, "", True, "QP", dev]
        abody = json.dumps(arr)
        asig = sign(abody)
        lg = s.post(B + "/login", data=abody.encode(),
                    headers={**asig, "content-type": "application/json",
                             "next-action": act, "accept": "text/x-component",
                             "origin": B, "referer": B + "/login"}, timeout=55)
        rep["login_status"] = lg.status_code
        rep["login_body"] = (lg.text or "")[:240].replace("\n", " ")
        tk = None
        import re as _re
        m = _re.search(r'"token"\s*:\s*"([^"]{12,})"', lg.text or "")
        if m:
            tk = m.group(1)
        rep["token_got"] = bool(tk)
        if tk:
            rep["token_preview"] = tk[:34]
        print("[login]", lg.status_code, rep["login_body"][:160], flush=True)

        # status endpoints via cookie session (works only when authorized)
        for pth in ("/api/v1/user/free-trial/status", "/api/v1/user"):
            try:
                q = s.get(B + pth, headers={"accept": "application/json,*/*"}, timeout=35)
                rep[pth] = f"{q.status_code}:{(q.text or '')[:160]}"
            except Exception as ex:
                rep[pth] = f"exc:{type(ex).__name__}"
    rep["done_at"] = int(time.time())

    out_name = f"qpres_{cj.get('tag','na')}_{int(time.time())}.json"
    st = put_out(out_name, json.dumps(rep, indent=1))
    print("[push]", out_name, st, flush=True)
    print(json.dumps(rep)[:500], flush=True)


if __name__ == "__main__":
    main()
