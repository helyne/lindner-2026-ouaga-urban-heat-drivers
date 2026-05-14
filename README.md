# Reversal of UHI Drivers in a Sahelian City: Low Built-Up Density Increases Heat in Ouagadougou

## Authors

**Elisabeth Lindner**¹, **Helyne Adamson**², **Ajadi Sodiq Abayomi**³, **Sharon Christa**⁴, **Daniel Fiifi Tawia Hagan**⁵

¹ Heidelberg Institute of Global Health (HIGH), Heidelberg University Hospital, Heidelberg University, Germany
² Independent Researcher, Germany
³ University of Manchester, United Kingdom
⁴ School of Computing, MIT Art Design and Technology University, Pune, India
⁵ Hydro-Climate Extremes Lab, Ghent University, Ghent, Belgium

## Abstract

Urban heat islands threaten fast-growing Sahelian cities, yet causal drivers of surface heating remain unknown. Here we combine machine-learning classification (XGBoost, Random Forest, SVM) with spatial causal inference to disentangle correlation from causation among hotspot drivers in Ouagadougou, Burkina Faso. XGBoost generalised best (F1 = 0.70, κ = 0.67) while SHAP analysis identified built-up density as the dominant predictor. Geographical convergent cross-mapping confirmed it as a unidirectional cause of surface temperature, while spectral indices showed only bidirectional coupling despite strong correlations. Opposite to humid tropical cities, lower built-up density increases hotspot risk due to exposed bare soil. These findings point to compact urban form as a heat mitigation strategy.

## Getting started

### Prerequisites

- Python 3.11+
- R >= 4.3 (for GCCM causal analysis only — see [`R/INSTALL.md`](R/INSTALL.md))
- A [Google Earth Engine](https://earthengine.google.com/) account (free for research use). See the [GEE access guide](https://developers.google.com/earth-engine/guides/access) and [`notebooks/reference/GEE_setup.ipynb`](notebooks/reference/GEE_setup.ipynb) for setup instructions.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/helyne/ouaga-urban-heat-drivers.git
   cd ouaga-urban-heat-drivers
   ```

2. Create a virtual environment and install the package + dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -e .
   ```
   This installs the project in editable mode (registers `src/` as an importable package) and pulls all dependencies pinned in `requirements.txt`. To also install development dependencies (e.g. `pytest` for running the test suite), use `pip install -e ".[dev]"` instead.

3. Authenticate with Google Earth Engine:
   ```bash
   earthengine authenticate
   ```
   Then initialize with your GEE cloud project ID. See [`notebooks/reference/GEE_setup.ipynb`](notebooks/reference/GEE_setup.ipynb) for a detailed walkthrough if this is your first time using GEE.

4. Download archived data and pre-fit models. See [Data access](#data-access) below.

### Project structure

```
config/
  processing.yaml    # All pipeline parameters (CRS, scale, dates, thresholds)

src/                 # Reusable Python library code (imported by notebooks/scripts)
  data.py            #   Configuration loading, raster-to-DataFrame conversion
  pipeline.py        #   GEE feature engineering, stacking, and download

R/                   # GCCM causal analysis (R scripts)
  gccm_config.R      #   Shared config (predictors, parameters, paths)
  gccm_analysis.R    #   Main GCCM analysis script
  INSTALL.md         #   R dependency installation instructions
renv.lock, renv/     # R package versions pinned via renv (companion to R/)

scripts/             # Standalone executables (publication figure generation, etc.)
  build_submission_zip.sh           # Builds the self-contained submission archive
  figure_style.py                   # Shared matplotlib styling and GCCM data paths
  make_gccm_convergence_pub.py      # Publication convergence figure
  make_gccm_asymmetry_pub.py        # Publication asymmetry figure
  generate_supplementary_figures.py # Supplementary figures S1–S4 + tables

notebooks/           # Analysis notebooks
  01_processing_pipeline  # GEE → aligned raster stack
  02_eda                  # Exploratory data analysis
  02_hotspot_detection    # LST hotspot map
  03_models               # ML models, SHAP, susceptibility maps
  04_causal_analysis      # GCCM convergence + asymmetry figures
  Heatwave/               # ERA5 daily temperature retrieval + 2024 Ouaga case study
  reference/GEE_setup.ipynb  # First-time GEE setup walkthrough
  README.md               # Explains canonical vs. methodology-exploration notebooks
  # Plus methodology exploration notebooks (DEM/, Distance_measures/, Hotspots/,
  # NDVI_NDBI_BSI/, models.ipynb, 00_quick_start.ipynb, download_individual_bands.ipynb)
  # documenting the reasoning behind choices in src/pipeline.py. See notebooks/README.md.

outputs/             # Analysis results
  gccm/main_E3_tau1/ #   The canonical publication GCCM run (CSVs + R checkpoints)

figures/             # Generated figures
  pub/               #   Publication-bound figures (main + supplementary/)
  *.svg              #   Tracked vector figures (methods workflow, heatwave example)
  gccm_explainer_*.png # Tracked methodology explainer diagrams

data/
  raw/               #   Input data (shapefiles, boundary) — treat as read-only
  processed/         #   Pipeline outputs (raster stack) — reproducible from raw + code

tests/               # Pytest smoke tests for data loading and model training
```

The methodology exploration notebooks under `notebooks/` (`DEM/`, `Distance_measures/`,
`Hotspots/hotspots_detection.ipynb`, `models.ipynb`, `NDVI_NDBI_BSI/`, etc.) document
earlier exploration and the reasoning behind choices in `src/pipeline.py`. They are
kept in the public repo for reviewers and collaborators who want to see how decisions
were made, but are excluded from the Zenodo publication snapshot. See
[`notebooks/README.md`](notebooks/README.md) for details.

### Loading the data

Once the processed raster exists (either by running the pipeline or downloading from Zenodo), load it in any notebook or script:

```python
from src.data import load_dataset

df, config = load_dataset("config/processing.yaml")
```

This returns a DataFrame with one row per valid pixel and columns for each band (NDVI, NDBI, BSI, DEM, distance_to_water, distance_to_roads, built_density, green_density, LST, hotspot), plus pixel coordinates (row, col, lon, lat).

## Reproducing the paper

Run the steps below in order. Each step depends on the outputs of the previous one.

1. **GEE processing** — computes the aligned raster stack from satellite imagery:
   ```bash
   jupyter notebook notebooks/01_processing_pipeline.ipynb
   ```
   Requires a GEE account. Outputs: `data/processed/ouaga_aligned_stack.tif`

2. **Hotspot detection** — produces the LST map figure:
   ```bash
   jupyter notebook notebooks/02_hotspot_detection.ipynb
   ```
   Reads the processed raster. Generates (to `figures/pub/`, not committed): `lst_hotspot_map.png`.

3. **ML models and SHAP** — trains XGBoost/RF/SVM, generates SHAP and susceptibility figures:
   ```bash
   jupyter notebook notebooks/03_models.ipynb
   ```
   By default, the notebook runs in `MODEL_MODE = "load"` and reads the pre-fit pickled models from `models/Hotspotters_Models.zip` (download from Zenodo — see [Data access](#data-access)). This reproduces the exact published numbers in seconds. To retrain from scratch with the same hyperparameters, set `MODEL_MODE = "manual"` (~2 min).

   Generates (to `figures/pub/`, not committed): `shap_bar_importance.png`, `shap_beeswarm.png`, `susceptibility_maps.png`.

4. **GCCM causal analysis** — runs the Geographical Convergent Cross-Mapping in R:
   ```bash
   Rscript R/gccm_analysis.R --fixed-E=3 --tau=1
   ```
   Requires R packages (see [`R/INSTALL.md`](R/INSTALL.md)). Outputs: `outputs/gccm/main_E3_tau1/`

5. **GCCM figures** — generates convergence and directional asymmetry plots:
   ```bash
   jupyter notebook notebooks/04_causal_analysis.ipynb
   ```
   Outputs: `figures/pub/gccm_convergence_tau1.png`, `figures/pub/gccm_asymmetry_tau1.png`

6. **Supplementary figures and tables** — generates Figures S1–S4 plus the supplementary tables (model hyperparameters, test-set classification metrics):
   ```bash
   python scripts/generate_supplementary_figures.py
   ```
   Outputs to `figures/pub/supplementary/`. Requires `rsvg-convert` for the SVG-derived figures (Homebrew: `brew install librsvg`). The script also runs a sanity check that the regenerated test-set metrics match the values published in Table 4 of the paper, and exits non-zero on drift.

## Tests

A small `pytest` smoke-test suite verifies that data loading and model training behave correctly on synthetic inputs:

```bash
pip install -e ".[dev]"   # if not already installed
pytest tests/ -v
```

Expect 7 tests to pass in under a minute. These are smoke tests covering `src.data` (config loading and raster-to-DataFrame conversion) and basic XGBoost / Random Forest / SVM training paths.

## Data access

The processed raster stack and pre-fit ML models are archived on Zenodo:

| Artifact | Path in repo | Zenodo DOI |
|---|---|---|
| Processed raster stack | `data/processed/ouaga_aligned_stack.tif` | [10.5281/zenodo.19835805](https://doi.org/10.5281/zenodo.19835805) |
| Pre-fit ML models (XGBoost, RF, SVM) | `models/Hotspotters_Models.zip` | [10.5281/zenodo.19835805](https://doi.org/10.5281/zenodo.19835805) |

Download both files. Place the raster at the path shown above; unzip the models bundle in place:

```bash
cd models
unzip Hotspotters_Models.zip
```

This produces `models/xgb_model.pkl`, `models/rf_model.pkl`, and `models/svm_model.pkl` — the paths the notebooks load from when `MODEL_MODE = "load"`.

The raster is also fully regenerable from Step 1 (GEE) — see [`data/README.md`](data/README.md) for full data sources and provenance. All input data sources are open-access.

**Code archive:** This codebase is openly available at <https://github.com/helyne/ouaga-urban-heat-drivers>.

## Research question/objective

- How transferable are the drivers of urban heat islands across diverse climatic and urban contexts?
- Are the factors that drive extreme heat universal, or are they specific to a city's geography, climate, and development pattern?


## Background/Motivation

This comparative study adapts the methodology of Hoang et al. (2025) — originally applied to Da Nang, Vietnam — and applies it to Ouagadougou, Burkina Faso, to investigate urban heat hotspots in a Sahelian urban context. The framework evaluates the effectiveness of machine learning models in identifying hotspots during heatwave events, identifies the most influential environmental and urban factors driving hotspot formation, and contrasts the results with the humid-tropical Da Nang setting to highlight which patterns are climate-dependent.

Hoang, ND., Huynh, TC. & Bui, DT. An interpretable machine learning framework for mapping hotspots and identifying their driving factors in urban environments during heat waves. Environ Monit Assess 197, 1017 (2025). https://doi.org/10.1007/s10661-025-14461-0


## Data

See [`data/README.md`](data/README.md) for full details on data sources, licensing, and setup instructions.

| Source | Resolution | Used for |
|---|---|---|
| Landsat 8/9 (Collection 2, Level 2) | 30 m | Land Surface Temperature |
| Sentinel-2 SR Harmonized | 10-20 m | NDVI, NDBI, BSI |
| Copernicus DEM GLO-30 | 30 m | Elevation |
| JRC Global Surface Water v1.4 | 30 m | Distance to water |
| ESA WorldCover 2021 | 10 m | Built-up and green space density |
| OpenStreetMap | Vector | Distance to roads |


## Methods

### Study area
Ouagadougou, capital of Burkina Faso, is a major urban center in West Africa's Sahel region. Compared to coastal Da Nang (Hoang et al. 2025) — whose methodology this study adapts — Ouagadougou's semi-arid inland conditions provide a contrasting setting for testing the universality of urban heat island drivers.

### Data and processing
Land surface temperature (LST) was derived from Landsat 8/9 Collection 2 Level-2 Surface Temperature products, composited across the March–May hot season from 2022 to 2024. Scenes exceeding 20% cloud cover were excluded, per-pixel cloud and shadow masking was applied, and physically implausible values outside 20–60°C were rejected. A pixel-wise median composite was computed at 30m resolution.

Thermal hotspots were defined as pixels exceeding the study-area mean by more than one standard deviation (LST > μ + 1σ), yielding a binary classification of hotspot (1) versus non-hotspot (0). Of the 613,847 valid pixels covering the Ouagadougou administrative boundary, approximately 10.3% were classified as hotspots.

Eight predictor variables were compiled from spectrally and temporally independent datasets (see [Data](#data) table above): NDVI, NDBI, BSI, DEM, distance to water, distance to roads, built-up density, and green space density. All layers were resampled to a common 30m UTM Zone 30N grid.

### Modelling and feature importance
Three binary classifiers — XGBoost, Random Forest, and a Support Vector Machine (SVM) with RBF kernel — were trained to classify hotspot occurrence using all eight predictors and the full set of 613,847 valid pixels. Data were randomly split 70/30 train/test (following Hoang et al. 2025). Hyperparameters were selected via five-fold cross-validated grid search. Models were evaluated using accuracy, precision, recall, F1, and Cohen's κ.

To identify which predictors most strongly drive hotspot classification, feature importance was quantified using SHapley Additive exPlanations (SHAP) via TreeExplainer on the held-out test set, providing both global importance rankings and directional insights into how each predictor drives hotspot probability.

### Causal inference
To test whether SHAP-identified predictors causally influence LST or merely co-vary with it, we applied Geographical Convergent Cross Mapping (GCCM; Gao et al. 2023) as implemented in the `spEDM` R package. For each predictor–LST pair, bidirectional GCCM was run on the 150m-aggregated raster with embedding dimension E = 3 and spatial lag τ = 1 (block scale), using 2,000 randomly sampled prediction points. Causal direction was determined by three criteria: (1) convergence (Kendall's τ > 0 for cross-map skill ρ vs. library size), (2) significance at the largest library size (p < 0.05), and (3) non-overlapping 95% Fisher-z confidence intervals between forward and reverse directions.


## Literature

Gao, B., Yang, J., Chen, Z. et al. Causal inference from cross-sectional earth system data with geographical convergent cross mapping. Nat Commun 14, 5875 (2023). https://doi.org/10.1038/s41467-023-41619-6

Hoang, ND., Huynh, TC. & Bui, DT. An interpretable machine learning framework for mapping hotspots and identifying their driving factors in urban environments during heat waves. Environ Monit Assess 197, 1017 (2025). https://doi.org/10.1007/s10661-025-14461-0


## Acknowledgements

We would like to express our sincere gratitude to our mentor, Daniel Fiifi Tawia Hagan (Hydro-Climate Extremes Lab, Ghent University), for his invaluable guidance and support throughout this study. His expertise and encouragement were instrumental in shaping the direction of this work. We extend our appreciation to the Climatematch Impact Scholars Program for providing the resources and platform necessary to conduct this research.


## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0-or-later). See [`LICENSE`](LICENSE).
