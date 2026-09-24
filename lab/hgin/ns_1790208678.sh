#!/bin/bash
set -u
export PATH="$HOME/nodenv/bin:$PATH"
DONE=$HOME/.nodeset_done
if [ ! -f "$DONE" ]; then
 {
 echo "[$(date -u +%FT%T)] setup start"
 getconf GNU_LIBC_VERSION
 ARCH=x64
 U=https://unofficial-builds.nodejs.org/download/release/v18.20.4/node-v18.20.4-linux-$ARCH-glibc217.tar.gz
 mkdir -p $HOME/dl && cd $HOME/dl
 if [ ! -s node.tgz ]; then timeout 180 curl -fsSL "$U" -o node.tgz && echo dl_ok $(stat -c%s node.tgz); fi
 rm -rf $HOME/nodenv && mkdir -p $HOME/nodenv
 tar xzf node.tgz --strip-components=1 -C $HOME/nodenv && echo untar_ok
 } >> $HOME/nodeset.log 2>&1
 touch $DONE
fi
{
echo "node_ver=$($HOME/nodenv/bin/node -v 2>&1)"
} >> $HOME/nodeset.log 2>&1
# deps venv (once)
[ -x $HOME/qpv/bin/python ] || { python3 -m venv $HOME/qpv >/dev/null 2>&1 && $HOME/qpv/bin/pip -q install pillow==9.5.0 requests >/dev/null 2>&1; }
{ echo "py=$([ -x $HOME/qpv/bin/python ] && echo yes || echo no) pil=$($HOME/qpv/bin/python -c 'import PIL,sys;print(PIL.__version__)' 2>&1|head -1)"; } >> $HOME/nodeset.log 2>&1
# connectivity probe to QP
$HOME/qpv/bin/python - <<'PY' 2>&1 | tail -6
try:
    import requests
    s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0 Chrome/131"
    r=s.get("https://app.quantumproxies.io/api/v1/auth/captcha",params={"cache":"no-store"},timeout=35,
            headers={"accept":"*/*","referer":"https://app.quantumproxies.io/register"})
    print("QP_CAP_ST",r.status_code,"len",len(r.text))
    j=r.json().get("payload") or {}
    print("keys",sorted(j.keys())[:10])
except Exception as e:
    print("QP_PROBE_ERR",type(e).__name__,str(e)[:140])
PY
echo NODESET_DONE
