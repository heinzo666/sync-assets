#!/bin/bash
export PATH="$HOME/nodenv/bin:$PATH"
mkdir -p $HOME/qpw && cd $HOME/qpw
RAW=https://raw.githubusercontent.com/heinzo666/sync-assets/main/lab
for f in hg_qpreg_core.py qdm_pod.cjs qdsign4.js; do timeout 60 curl -fsSL "$RAW/$f?v=1790211465" -o $f; done
wc -c hg_qpreg_core.py qdm_pod.cjs qdsign4.js
NODE=$($HOME/nodenv/bin/node -v 2>&1); echo NODE=$NODE
$HOME/qpv/bin/python -u hg_qpreg_core.py lab/qreg_hgt011200.json > rz3.txt 2>&1
echo "PY_EXIT=$?"
tail -c 3200 rz3.txt
