#!/bin/bash
export PATH="$HOME/nodenv/bin:$PATH"
mkdir -p $HOME/qpw && cd $HOME/qpw
for i in $(seq 80); do [ -x $HOME/nodenv/bin/node ] && break; sleep 7; done
echo "node=$($HOME/nodenv/bin/node -v 2>&1)"
RAW=https://raw.githubusercontent.com/heinzo666/sync-assets/main/lab
[ -f hg_qpreg_core.py ] || timeout 45 curl -fsSL "$RAW/hg_qpreg_core.py?v=1790209474" -o hg_qpreg_core.py
[ -f qdm_pod.cjs ] || timeout 75 curl -fsSL "$RAW/qdm_pod.cjs?v=1790209474" -o qdm_pod.cjs
[ -f qdsign4.js ] || timeout 25 curl -fsSL "$RAW/qdsign4.js?v=1790209474" -o qdsign4.js
wc -c hg_qpreg_core.py qdm_pod.cjs qdsign4.js
$HOME/qpv/bin/pip -q install numpy 2>/dev/null || true
$HOME/qpv/bin/python -u hg_qpreg_core.py lab/qreg_hgt011200.json > r2.txt 2>&1
tail -c 2600 r2.txt
