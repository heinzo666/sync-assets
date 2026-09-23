#!/bin/bash
echo "HOST=$(hostname)"
for t in python3 python node nodejs npm php perl ruby git tar unzip jq crontab mysql; do p=$(command -v $t 2>/dev/null); echo "$t=${p:-MISSING}"; done
ls -d /opt/alt/python*/usr/bin/python3* 2>/dev/null | head -3
php -v 2>&1 | head -1
python3 -V 2>&1 | head -1
node -v 2>&1 | head -1
echo TOOLS_DONE
