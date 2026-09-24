#!/bin/bash
export PATH="$HOME/nodenv/bin:$PATH"
cd $HOME/qpw || mkdir -p $HOME/qpw && cd $HOME/qpw
RAW=https://raw.githubusercontent.com/heinzo666/sync-assets/main/lab
for f in hg_qpreg_core.py qdm_pod.cjs qdsign4.js; do timeout 60 curl -fsSL "$RAW/$f?v=1790211698" -o $f; done
wc -c hg_qpreg_core.py | head -1
$HOME/qpv/bin/pip install --no-input --disable-pip-version-check numpy==1.26.4 2>&1 | tail -2
echo "PIP_RC=$?"
$HOME/qpv/bin/python -c 'import numpy;print("NUMPY",numpy.__version__)' 2>&1 | tail -1
$HOME/qpv/bin/python -u hg_qpreg_core.py lab/qreg_hgt011200.json > rz4.txt 2>&1
echo "PY_EXIT=$?"
tail -c 3400 rz4.txt
