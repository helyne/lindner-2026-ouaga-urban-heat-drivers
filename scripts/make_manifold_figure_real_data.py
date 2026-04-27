"""
Build the LST manifold figure from the actual Ouagadougou raster.

Loads the aligned stack, aggregates 5x (matching the GCCM pipeline),
computes E=3 ring means at tau=1 for the LST band, and plots the
3D point cloud colored by urban zone.

Outputs: figures/gccm_explainer_manifold_v3_real_data.png

Parameters match the main_E3_tau1 GCCM run:
  AGG_FACTOR = 5  (150m pixels)
  E = 3           (3 rings)
  tau = 1         (ring spacing = 1 pixel = 150m)
"""

from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
import rasterio

# -- Configuration (matching main_E3_tau1 run) --------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ouaga_aligned_stack.tif"
AGG_FACTOR = 5
E = 3
TAU = 1
LST_BAND_INDEX = 8  # 0-indexed: NDVI,NDBI,BSI,DEM,d2w,d2r,built,green,LST,hotspot
BUILT_BAND_INDEX = 6
SEED = 42
N_SAMPLE = 4000  # subsample for plotting (full raster is ~35k valid pixels)

OUTPUT_PATH = PROJECT_ROOT / "figures" / "gccm_explainer_manifold_v3_real_data.png"

# -- Load and aggregate -------------------------------------------------------
print(f"Loading {RASTER_PATH}...")
with rasterio.open(RASTER_PATH) as src:
    lst_full = src.read(LST_BAND_INDEX + 1).astype(np.float64)  # rasterio is 1-indexed
    built_full = src.read(BUILT_BAND_INDEX + 1).astype(np.float64)

# Replace nodata (-inf) with NaN
lst_full[~np.isfinite(lst_full)] = np.nan
built_full[~np.isfinite(built_full)] = np.nan

print(f"  Original: {lst_full.shape[0]} x {lst_full.shape[1]} pixels")

# Aggregate with mean (matching terra::aggregate(..., fun="mean"))
# Use block-mean: reshape into AGG x AGG blocks and take the mean
nrow, ncol = lst_full.shape
# Trim to exact multiple of AGG_FACTOR
nrow_trim = (nrow // AGG_FACTOR) * AGG_FACTOR
ncol_trim = (ncol // AGG_FACTOR) * AGG_FACTOR
lst_trim = lst_full[:nrow_trim, :ncol_trim]
built_trim = built_full[:nrow_trim, :ncol_trim]

# Block mean aggregation
lst_agg = np.nanmean(
    lst_trim.reshape(nrow_trim // AGG_FACTOR, AGG_FACTOR,
                     ncol_trim // AGG_FACTOR, AGG_FACTOR),
    axis=(1, 3)
)
built_agg = np.nanmean(
    built_trim.reshape(nrow_trim // AGG_FACTOR, AGG_FACTOR,
                       ncol_trim // AGG_FACTOR, AGG_FACTOR),
    axis=(1, 3)
)

print(f"  Aggregated ({AGG_FACTOR}x): {lst_agg.shape[0]} x {lst_agg.shape[1]} pixels")


# -- Compute ring means (Chebyshev distance rings) ----------------------------

def get_ring_mean(grid, row, col, ring_distance):
    """Mean of pixels at exactly `ring_distance` Chebyshev distance."""
    nrow, ncol = grid.shape
    values = []
    for r in range(max(0, row - ring_distance), min(nrow, row + ring_distance + 1)):
        for c in range(max(0, col - ring_distance), min(ncol, col + ring_distance + 1)):
            if max(abs(r - row), abs(c - col)) == ring_distance:
                val = grid[r, c]
                if not np.isnan(val):
                    values.append(val)
    if len(values) == 0:
        return np.nan
    return np.mean(values)


margin = E * TAU  # need E rings of space around each pixel
nrow_agg, ncol_agg = lst_agg.shape

print(f"\nComputing E={E} ring means (tau={TAU}) for valid pixels...")

ring_means = []  # (N, 3) array of ring means
pixel_lst = []   # LST value at each pixel
pixel_built = [] # built_density value at each pixel
pixel_coords = []

for r in range(margin, nrow_agg - margin):
    for c in range(margin, ncol_agg - margin):
        if np.isnan(lst_agg[r, c]):
            continue
        rings = []
        valid = True
        for ring_idx in range(1, E + 1):
            ring_dist = ring_idx * TAU
            mean_val = get_ring_mean(lst_agg, r, c, ring_dist)
            if np.isnan(mean_val):
                valid = False
                break
            rings.append(mean_val)
        if valid:
            ring_means.append(rings)
            pixel_lst.append(lst_agg[r, c])
            pixel_built.append(built_agg[r, c])
            pixel_coords.append((r, c))

ring_means = np.array(ring_means)
pixel_lst = np.array(pixel_lst)
pixel_built = np.array(pixel_built)
pixel_coords = np.array(pixel_coords)

print(f"  Valid pixels with complete rings: {len(ring_means)}")


# -- Define urban zones for coloring ------------------------------------------
# Classify into 4 zones by LST quartile. This produces even-sized groups
# that separate nicely in the manifold, matching the illustrative figure style.

lst_quartiles = np.percentile(pixel_lst, [25, 50, 75])

zones = np.full(len(pixel_lst), "", dtype=object)
zones[pixel_lst <= lst_quartiles[0]] = "Coolest 25%"
zones[(pixel_lst > lst_quartiles[0]) & (pixel_lst <= lst_quartiles[1])] = "Cool-moderate"
zones[(pixel_lst > lst_quartiles[1]) & (pixel_lst <= lst_quartiles[2])] = "Warm-moderate"
zones[pixel_lst > lst_quartiles[2]] = "Hottest 25%"

zone_names = [
    "Hottest 25%",
    "Warm-moderate",
    "Cool-moderate",
    "Coolest 25%",
]
zone_colors = {
    "Hottest 25%": "#e41a1c",      # red
    "Warm-moderate": "#ff7f00",     # orange
    "Cool-moderate": "#4daf4a",     # green
    "Coolest 25%": "#377eb8",       # blue
}

print(f"\nZone distribution:")
for z in zone_names:
    count = np.sum(zones == z)
    print(f"  {z.replace(chr(10), ' ')}: {count} ({100*count/len(zones):.0f}%)")


# -- Subsample for clean plotting ---------------------------------------------
np.random.seed(SEED)
if len(ring_means) > N_SAMPLE:
    idx = np.random.choice(len(ring_means), size=N_SAMPLE, replace=False)
    ring_plot = ring_means[idx]
    lst_plot = pixel_lst[idx]
    zones_plot = zones[idx]
else:
    ring_plot = ring_means
    lst_plot = pixel_lst
    zones_plot = zones

print(f"\nPlotting {len(ring_plot)} points (subsampled from {len(ring_means)})")


# -- Plot ---------------------------------------------------------------------
fig = plt.figure(figsize=(10, 9))
ax = fig.add_subplot(111, projection="3d")

# Plot each zone as a separate scatter for legend
for zone in zone_names:
    mask = zones_plot == zone
    if mask.sum() == 0:
        continue
    ax.scatter(
        ring_plot[mask, 0], ring_plot[mask, 1], ring_plot[mask, 2],
        c=zone_colors[zone], s=18, alpha=0.55,
        edgecolors="gray", linewidth=0.2,
        label=zone.replace("\n", " "),
    )

ax.set_xlabel("Ring 1 mean (LST °C)", fontsize=11, labelpad=8)
ax.set_ylabel("Ring 2 mean (LST °C)", fontsize=11, labelpad=8)
ax.set_zlabel("Ring 3 mean (LST °C)", fontsize=11, labelpad=8)
ax.set_title(
    "LST manifold: each pixel plotted by its 3 ring means\n"
    "(Ouagadougou, 150 m, E=3, τ=1)",
    fontsize=13, fontweight="bold", pad=15,
)
ax.legend(fontsize=9, loc="upper left", markerscale=1.5, framealpha=0.9)

# Set a good viewing angle
ax.view_init(elev=20, azim=315)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight", facecolor="white")
print(f"\nSaved: {OUTPUT_PATH}")
plt.close()


# -- Interactive plotly version ------------------------------------------------
# Opens in browser so you can rotate freely and find the best angle.
# Run with: python scripts/make_manifold_figure_real_data.py --interactive

if "--interactive" in __import__("sys").argv:
    import plotly.graph_objects as go

    fig = go.Figure()
    for zone in zone_names:
        mask = zones_plot == zone
        if mask.sum() == 0:
            continue
        fig.add_trace(go.Scatter3d(
            x=ring_plot[mask, 0],
            y=ring_plot[mask, 1],
            z=ring_plot[mask, 2],
            mode="markers",
            name=zone.replace("\n", " "),
            marker=dict(
                size=3,
                color=zone_colors[zone],
                opacity=0.6,
            ),
        ))

    fig.update_layout(
        title="LST manifold (Ouagadougou, 150 m, E=3, τ=1) — drag to rotate",
        scene=dict(
            xaxis_title="Ring 1 mean (LST °C)",
            yaxis_title="Ring 2 mean (LST °C)",
            zaxis_title="Ring 3 mean (LST °C)",
        ),
        width=900,
        height=700,
    )
    fig.show()
    print("Interactive plot opened in browser.")
