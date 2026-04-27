#!/usr/bin/env bash
# Build a self-contained submission zip.
#
# Combines git-tracked files (via git archive) with the data files needed
# to reproduce all figures without re-running the GEE pipeline.
#
# Usage:
#   bash scripts/build_submission_zip.sh
#
# Output:
#   submission.zip in the repository root

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

OUT="submission.zip"

echo "Building $OUT ..."

# Step 1: git archive (respects .gitattributes export-ignore)
git archive -o "$OUT" HEAD

# Step 2: Add the processed raster stack
zip -u "$OUT" data/processed/ouaga_aligned_stack.tif

# Step 3: Add GCCM results (CSVs only — notebooks regenerate the PNGs)
zip -u "$OUT" \
    outputs/gccm/main_E3_tau1/results.csv \
    outputs/gccm/main_E3_tau1/summary.csv

echo ""
echo "Done. Contents:"
unzip -l "$OUT" | tail -3
echo ""
echo "Total size: $(du -h "$OUT" | cut -f1)"
