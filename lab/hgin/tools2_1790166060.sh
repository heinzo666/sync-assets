#!/bin/bash
echo "== paths =="
for t in python3 python2 python node nodejs npm curl wget git tar unzip php crontab mysql mysqldump; do p=$(command -v $t 2>/dev/null); echo "$t=$p"; done
echo "== alt-python =="
ls -d /opt/alt/python*/usr/bin/python3* 2>/dev/null | head -5
echo "== ea-node =="
ls -d /opt/alt/*/lve/*node* 2>/dev/null | head -5 ; ls ~/nodevenv 2>/dev/null | head
echo "== osrelease =="
cat /etc/redhat-release 2>/dev/null || cat /etc/os-release 2>/dev/null | head -3
echo DONE_TOOLS
