#!/usr/bin/env bash
# run-grid.sh <photo> <outdir> : upload, dot-grid corners, flatten as a4, trace with $TRACER_LIST (default isnet inspyrenet)
set -uo pipefail
photo=$1 out=$2
api=${TF_API:-http://localhost:3900/api}
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$out"
docker cp -q "$here/grid_corners.py" tracefinity:/tmp/grid_corners.py

curl -sf -F "image=@${photo};type=image/jpeg" "$api/upload" > "$out/upload.json" || { echo "upload failed"; exit 1; }
sid=$(jq -r .session_id "$out/upload.json")
echo "$sid" > "$out/session_id"

docker exec tracefinity python3 -I /tmp/grid_corners.py "/app/storage/default/uploads/$sid.jpg" 5 /tmp/grid-dbg.jpg > "$out/grid.json" 2> "$out/grid.err" \
  || { echo "grid fit failed: $(tail -1 "$out/grid.err")"; exit 1; }
docker cp -q tracefinity:/tmp/grid-dbg.jpg "$out/grid-debug.jpg"
echo "grid: $(jq -c 'del(.corners)' "$out/grid.json")"

jq -c '{corners: .corners, paper_size: "a4"}' "$out/grid.json" \
  | curl -s -H 'content-type: application/json' -d @- "$api/sessions/$sid/corners" > "$out/corners.json"
echo "scale=$(jq .scale_factor "$out/corners.json") warnings=$(jq -c '[.warnings[]?.code]' "$out/corners.json")"

for tracer in ${TRACER_LIST:-isnet inspyrenet}; do
  start=$(date +%s)
  jq -n --arg t "$tracer" '{tracer:$t}' \
    | curl -s -H 'content-type: application/json' -d @- "$api/sessions/$sid/trace" > "$out/trace-$tracer.json"
  echo "$tracer: $(( $(date +%s) - start ))s polygons=$(jq '.polygons|length' "$out/trace-$tracer.json" 2>/dev/null || head -c 200 "$out/trace-$tracer.json")"
done
