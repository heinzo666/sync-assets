#!/bin/bash
echo "WHO $(id)"
which pip3 pip python3 || true
python3 -m pip --version 2>&1 | head -1
python3 -m ensurepip --version 2>&1 | head -1
ls /opt/alt/python*/usr/bin/pip* 2>/dev/null | head -5
for pp in /opt/alt/python39/usr/bin/pip3 /opt/alt/python311/usr/bin/pip3 /usr/local/bin/pip3; do [ -x "$pp" ] && echo FOUND:$pp; done
echo "--net--"
timeout 20 curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org/simple/ 
timeout 20 curl -sS -o /dev/null -w '%{http_code} %{remote_ip}\n' https://app.mailhook.co/
timeout 16 curl -sS https://api.ipify.org; echo
df -h $HOME | tail -1
quota -s 2>/dev/null | tail -3 || true
echo PIP_PROBE_DONE
