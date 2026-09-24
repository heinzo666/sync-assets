#!/bin/bash
export PATH="$HOME/nodenv/bin:$PATH"
mkdir -p $HOME/qpw && cd $HOME/qpw
RAW=https://raw.githubusercontent.com/heinzo666/sync-assets/main/lab
for f in hg_qpreg_core.py qdm_pod.cjs qdsign4.js; do [ -f $f ] || timeout 60 curl -fsSL "$RAW/$f?v=1790210915" -o $f; done
wc -c hg_qpreg_core.py qdm_pod.cjs qdsign4.js 2>/dev/null
echo NODE=$($HOME/nodenv/bin/node -v 2>&1)
$HOME/qpv/bin/python -c 'import numpy,PIL,requests;print("DEPS_OK")' 2>&1 | tail -1
$HOME/qpv/bin/python -u hg_qpreg_core.py lab/qreg_hgt011200.json > rzz.txt 2>&1
echo "PY_EXIT=$?"
echo ---TAIL---
tail -c 3000 rzz.txt
