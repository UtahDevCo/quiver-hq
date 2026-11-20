#!/usr/bin/env bash
# run-masked.sh <photo> <outdir>
# For shots where the sheet is small in frame: paint everything outside the sheet
# paper-white, then upload, calibrate and trace. Sheet outline comes from
# Tracefinity's detected corners when it finds them, else from the dot-grid hull.
# Calibration: dot grid when it resolves, else the detected corners mapped through
# the measured sheet size (the torn notebook page is 282.75 x 211.05 mm, not A4).
set -uo pipefail
photo=$1 out=$2
api=${TF_API:-http://localhost:3900/api}
here=$(cd "$(dirname "$0")" && pwd)
SHEET_L=${SHEET_L:-282.75} SHEET_S=${SHEET_S:-211.05}
mkdir -p "$out"
for f in grid_corners.py mask_sheet.py sheet_corners.py; do docker cp -q "$here/$f" tracefinity:/tmp/$f; done

# 1. raw upload: detected corners + dot hull, in the 2048 frame
curl -sf -F "image=@${photo};type=image/jpeg" "$api/upload" > "$out/raw-upload.json" || { echo "upload failed"; exit 1; }
rsid=$(jq -r .session_id "$out/raw-upload.json")
fw=$(jq -r .image_width "$out/raw-upload.json")
docker exec tracefinity python3 -I /tmp/grid_corners.py "/app/storage/default/uploads/$rsid.jpg" 5 /tmp/g.jpg > "$out/raw-grid.json" 2>/dev/null || echo '{}' > "$out/raw-grid.json"
curl -s -X DELETE "$api/sessions/$rsid" >/dev/null

if [ "$(jq '.detected_corners != null' "$out/raw-upload.json")" = true ]; then
  jq -c '[.detected_corners[] | [.x, .y]]' "$out/raw-upload.json" > "$out/sheet-poly.json"; grow=-4; src=detected
elif [ "$(jq '(.hull // []) | length > 2' "$out/raw-grid.json")" = true ]; then
  jq -c '.hull' "$out/raw-grid.json" > "$out/sheet-poly.json"; grow=12; src=dot-hull
else
  echo "no sheet outline found"; exit 1
fi

# 2. mask outside the sheet and upload the masked photo
docker cp -q "$photo" tracefinity:/tmp/photo.jpg
docker cp -q "$out/sheet-poly.json" tracefinity:/tmp/poly.json
docker exec tracefinity python3 -I /tmp/mask_sheet.py /tmp/photo.jpg "$fw" /tmp/poly.json "$grow" /tmp/masked.jpg >/dev/null
docker cp -q tracefinity:/tmp/masked.jpg "$out/masked.jpg"
curl -sf -F "image=@$out/masked.jpg;type=image/jpeg" "$api/upload" > "$out/upload.json" || { echo "masked upload failed"; exit 1; }
sid=$(jq -r .session_id "$out/upload.json"); echo "$sid" > "$out/session_id"

# 3. calibrate
if docker exec tracefinity python3 -I /tmp/grid_corners.py "/app/storage/default/uploads/$sid.jpg" 5 /tmp/g.jpg > "$out/grid.json" 2>/dev/null \
   && [ "$(jq '.n_dots > 200 and .rms_px < 1.2' "$out/grid.json")" = true ]; then
  cal="dot-grid ($(jq -c '[.n_dots, .rms_px]' "$out/grid.json"))"
elif [ "$src" = detected ]; then
  docker cp -q "$out/raw-upload.json" tracefinity:/tmp/u.json
  docker exec tracefinity python3 -I /tmp/sheet_corners.py /tmp/u.json "$SHEET_L" "$SHEET_S" > "$out/grid.json"
  cal="sheet size ${SHEET_L}x${SHEET_S}"
else
  echo "no calibration: dots did not resolve and no sheet corners"; exit 1
fi
jq -c '{corners: .corners, paper_size: "a4"}' "$out/grid.json" \
  | curl -s -H 'content-type: application/json' -d @- "$api/sessions/$sid/corners" > "$out/corners.json"
echo "outline=$src calibration=$cal scale=$(jq .scale_factor "$out/corners.json") warnings=$(jq -c '[.warnings[]?.code]' "$out/corners.json")"

# 4. trace
for tracer in ${TRACER_LIST:-isnet inspyrenet}; do
  jq -n --arg t "$tracer" '{tracer:$t}' \
    | curl -s -H 'content-type: application/json' -d @- "$api/sessions/$sid/trace" > "$out/trace-$tracer.json"
  echo "$tracer: polygons=$(jq '.polygons|length' "$out/trace-$tracer.json" 2>/dev/null || head -c 200 "$out/trace-$tracer.json")"
done
