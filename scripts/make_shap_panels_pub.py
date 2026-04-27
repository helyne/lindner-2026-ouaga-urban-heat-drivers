"""
SHAP panels — publication style.

This script applies the shared figure style to SHAP summary plots.
It requires the XGBoost model and test data, so it must be run after
the models notebook (notebooks/models.ipynb) has been executed, or
with pre-saved SHAP values.

Usage
-----
    # Option 1: Run after saving shap_values from the notebook
    python scripts/make_shap_panels_pub.py

    # Option 2: Paste the apply_style() block into the notebook before
    #           calling shap.summary_plot()

If you just want to apply the style inside the notebook, add these lines
before any shap.summary_plot() call:

    import sys
    sys.path.insert(0, "../scripts")
    from figure_style import apply_style
    apply_style()

Output
------
    figures/pub/shap_bar.png
    figures/pub/shap_beeswarm.png
"""

import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import shap

# Shared style
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_style import apply_style, FONT, FIG_DIR

apply_style()

# ---------------------------------------------------------------------------
# Paths — adapt if your model/data live elsewhere
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Try to load pre-saved SHAP values (fastest path)
shap_path = DATA_DIR / "shap_values.npz"
model_path = DATA_DIR / "ouaga_xgb_model.pkl"
stack_path = DATA_DIR / "ouaga_aligned_stack.tif"

FEATURE_NAMES = [
    "NDVI", "NDBI", "BSI", "DEM",
    "distance_to_water", "distance_to_roads",
    "built_density", "green_density",
]

if shap_path.exists():
    print(f"Loading pre-saved SHAP values from {shap_path}")
    data = np.load(shap_path)
    shap_values = data["shap_values"]
    X_test = data["X_test"]
else:
    print("No pre-saved SHAP values found.")
    print(f"Looking for model at {model_path}")

    if not model_path.exists():
        print(
            "\nTo use this script, either:\n"
            "  1. Save SHAP values from the notebook:\n"
            "       np.savez('data/processed/shap_values.npz',\n"
            "                shap_values=shap_values, X_test=X_test)\n"
            "  2. Or just paste these lines into the notebook before plotting:\n"
            "       import sys; sys.path.insert(0, '../scripts')\n"
            "       from figure_style import apply_style; apply_style()\n"
        )
        sys.exit(0)

    import rasterio
    from sklearn.model_selection import train_test_split

    model = joblib.load(model_path)

    with rasterio.open(stack_path) as src:
        X = src.read()

    X_2d = X.reshape(X.shape[0], -1).T
    y_1d = X_2d[:, -1]  # hotspot band
    X_features = X_2d[:, :8]

    valid = ~np.isnan(X_features).any(axis=1) & ~np.isnan(y_1d)
    X_clean = X_features[valid]
    y_clean = y_1d[valid]

    _, X_test, _, _ = train_test_split(
        X_clean, y_clean, test_size=0.3, random_state=42
    )

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    np.savez(
        shap_path, shap_values=shap_values, X_test=X_test
    )
    print(f"Saved SHAP values to {shap_path}")


# ---------------------------------------------------------------------------
# Bar plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
shap.summary_plot(
    shap_values, X_test,
    feature_names=FEATURE_NAMES,
    plot_type="bar",
    show=False,
)
plt.tight_layout()
out = FIG_DIR / "shap_bar.png"
plt.savefig(out)
plt.close()
print(f"Saved: {out}")

# ---------------------------------------------------------------------------
# Beeswarm plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
shap.summary_plot(
    shap_values, X_test,
    feature_names=FEATURE_NAMES,
    show=False,
)
plt.tight_layout()
out = FIG_DIR / "shap_beeswarm.png"
plt.savefig(out)
plt.close()
print(f"Saved: {out}")
