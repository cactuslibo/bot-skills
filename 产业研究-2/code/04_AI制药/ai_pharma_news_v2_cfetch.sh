#!/bin/bash
# usage: cfetch.sh name url [sec]
n=$1; u=$2
if [ "$3" = sec ]; then UA="research-bot YOUR_EMAIL@example.com"; else UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"; fi
code=$(curl -sL -m 40 -A "$UA" -o raw/$n -w '%{http_code}' "$u")
echo "{\"t\":\"$(date -Iseconds)\",\"method\":\"curl\",\"url\":\"$u\",\"status\":$code,\"file\":\"raw/$n\"}" >> curl_log.jsonl
echo "$code $n $(wc -c < raw/$n)"
