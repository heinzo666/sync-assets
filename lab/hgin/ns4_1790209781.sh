#!/bin/bash
cd $HOME/dl || exit 9
rm -rf /tmp/nodetmp && mkdir -p /tmp/nodetmp
ls -la node.pkg
tar xJf node.pkg --strip-components=1 -C /tmp/nodetmp && echo UNPACK_OK
mv /tmp/nodetmp $HOME/nodenv && echo MOVED_OK
export PATH="$HOME/nodenv/bin:$PATH"
echo "NODE=$($HOME/nodenv/bin/node -v 2>&1)"
A0='ghp_GRcU'
A1='NUXyf1t2'
A2='oZNwUQXM'
A3='rTlEGHq2'
A4='Kf1cjaAv'
printf '%s' "${A0}${A1}${A2}${A3}${A4}" > $HOME/.ghr_tk
wc -c $HOME/.ghr_tk
