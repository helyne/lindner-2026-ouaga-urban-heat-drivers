#!/usr/bin/env bash
# Wait for tau=15 to finish, compare tau=10 vs tau=15, then start full run.
# Output paths are separate — nothing gets overwritten.
#   Sensitivity results: outputs/gccm/sensitivity/tau/
#   Full run results:    outputs/gccm/main/

set -euo pipefail
cd /Users/helyne/code/climatematch/ouaga-urban-heat-drivers

TAU15_SUMMARY="outputs/gccm/sensitivity/tau/tau15/summary.csv"
TAU10_SUMMARY="outputs/gccm/sensitivity/tau/tau10/summary.csv"

echo "=== Waiting for tau=15 to finish ==="
while ! [ -f "$TAU15_SUMMARY" ]; do
  sleep 60
  echo "  $(date '+%H:%M') — still waiting for $TAU15_SUMMARY ..."
done
echo "  tau=15 complete at $(date '+%H:%M')"

echo ""
echo "=== Step 1: Compare tau=10 vs tau=15 ==="
echo ""
echo "--- tau=10 summary ---"
cat "$TAU10_SUMMARY"
echo ""
echo "--- tau=15 summary ---"
cat "$TAU15_SUMMARY"
echo ""

# Extract DEM rho values for quick comparison
echo "--- DEM negative control comparison ---"
echo "tau=10:"
grep "DEM" "$TAU10_SUMMARY" | awk -F',' '{printf "  pred->LST = %s, LST->pred = %s, direction = %s\n", $4, $5, $NF}'
echo "tau=15:"
grep "DEM" "$TAU15_SUMMARY" | awk -F',' '{printf "  pred->LST = %s, LST->pred = %s, direction = %s\n", $4, $5, $NF}'

echo ""
echo "=== Step 2: Starting full 8-predictor run at tau=10 ==="
echo "Output directory: outputs/gccm/main/"
echo "This will NOT overwrite sensitivity results."
echo ""

Rscript R/gccm_analysis.R --tau=10 2>&1

echo ""
echo "=== Full run complete ==="
