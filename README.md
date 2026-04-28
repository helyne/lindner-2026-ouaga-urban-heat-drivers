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
   git clone <repo-url>
   cd ouaga-urban-heat-drivers
   ```

2. Create a virtual environment and install the package + dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -e .
   ```
   This installs the project in editable mode (registers `src/` as an importable package) and pulls all dependencies pinned in `requirements.txt`.

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

src/                 # Reusable Python modules
  data.py            #   Configuration loading, raster-to-DataFrame conversion
  pipeline.py        #   GEE feature engineering, stacking, and download

R/                   # GCCM causal analysis (R scripts)
  gccm_config.R      #   Shared config (predictors, parameters, paths)
  gccm_analysis.R    #   Main GCCM analysis script
  INSTALL.md         #   R dependency installation instructions

notebooks/           # Analysis notebooks (run in order)
  01_processing_pipeline  # GEE → aligned raster stack
  02_hotspot_detection    # LST map figure
  03_models               # ML models, SHAP, susceptibility maps
  04_causal_analysis      # GCCM convergence + asymmetry figures

data/
  raw/               #   Input data (shapefiles, boundary) — treat as read-only
  processed/         #   Pipeline outputs (raster stack) — reproducible from raw + code
```

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
   Requires a GEE account. Outputs: `figures/pub/lst_hotspot_map.png`

3. **ML models and SHAP** — trains XGBoost/RF/SVM, generates SHAP and susceptibility figures:
   ```bash
   jupyter notebook notebooks/03_models.ipynb
   ```
   By default, the notebook runs in `MODEL_MODE = "load"` and reads the pre-fit pickled models from `models/Hotspotters_Models.zip` (download from Zenodo — see [Data access](#data-access)). This reproduces the exact published numbers in seconds. To retrain from scratch with the same hyperparameters, set `MODEL_MODE = "manual"` (~2 min).

   Outputs: `figures/pub/shap_*.png`, `figures/pub/susceptibility_maps.png`

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

**Code archive:** This codebase is archived on Zenodo at _DOI pending_. Cite this DOI when referencing the analysis code.

## Research question/objective

- How transferable are the drivers of urban heat islands across diverse climatic and urban contexts?
- Are the factors that drive extreme heat universal, or are they specific to a city's geography, climate, and development pattern?


## Background/Motivation

This comparative study replicates the methodology of the Da Nang study in Vietnam and applies it to Ouagadougou, Burkina Faso, to investigate urban heat hotspots in a Sahelian urban context. Specifically, it aims to evaluate the effectiveness of machine learning models in identifying hotspots during heatwave events, determine the most influential environmental and urban factors driving hotspot formation, and directly compare these results with those from Da Nang to evaluate which patterns are consistent and which differ due to Ouagadougou's specific climate and urban structure.

The study is modeled after and builds upon the work by Hoang et al. (2025).

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


## Methods/Approach

### The study area
We selected the capital city of Ouagadougou, Burkina Faso, a major urban center in West Africa's Sahel region, as our comparative study area. Crucially, Ouagadougou shares key characteristics with Da Nang (e.g. similar latitude, population size, and a significant March-May 2024 heatwave), while representing a starkly different environment. Unlike coastal Da Nang's humid climate, Ouagadougou's semi-arid inland conditions create a climatic contrast, allowing us to investigate which urban heat drivers are universal or context-specific. This comparison can reveal how local climate modulates urban heat island effects.

### Research material
To characterize heatwave dynamics and intra-urban variations in temperature, we collect and preprocess a combination of remote sensing and vector-based spatial datasets (summarised in Table 1). We primarily use satellite imagery from Landsat 8 and Sentinel-2, digital elevation data from Copernicus, and road network data extracted from OpenStreetMap.

Table 1 - Research material and data sources

Surface reflectance and surface temperature products (30 m) from Landsat-8 and Sentinel-2 provide fine-scale spatial information of both land surface temperature (LST) and land use land cover (LULC) indices, including urban, vegetation, water, and soil indices (e.g. NDBI, NDVI, MNDWI, and Bare Soil Index). Topographical features are derived from the Copernicus global digital elevation model (DEM) at a resolution of 30m. OpenStreetMap (OSM) vector data is used for urban infrastructure features, such as proximity to roads and water bodies. Global Human Settlement Layer (GHSL) datasets are used for population metrics.

### The analysis methods
We will apply a machine learning approach to examine the precise spatial drivers of intra-urban heat patterns during extreme events and then test whether these drivers are consistent across two different urban environments. The study will replicate the XGBoost and SHAP analysis framework from Hoang et al. (2025) for Da Nang, Vietnam in 2024, and adapt it for the novel context of Ouagadougou, Burkina Faso, a rapidly urbanizing Sahelian city that also experienced severe heatwave events in 2024. We will test the generalizability of urban heat drivers by comparing the results from Ouagadougou with the published results from Da Nang, Vietnam. To build upon the work by Hoang, a causal model with pre-hoc weight assignment will be implemented before the training as in Yeboah et al. (2025), providing greater explanatory power to the study.

General method details:
- Heatwave events defined via ETCCDI indices (TX90p, WSDI).
- Anomalies computed vs. rural reference areas.
- Predictors: NDVI, NDBI, MNDWI, slope/elevation, green density, built-up share, distance to roads/water, population.
- Models: XGBoost + RF (stratified cross-validation, SHAP interpretability); pre-hoc causal model with weight assignment.

### Heat risk map
To test mitigation policies, we will digitally alter Ouagadougou's input maps - for example, artificially increasing the 'green space density' value by 10% in the city center - and then feed this modified map into our already-trained model to generate a new heat risk forecast. Comparing this new forecast to the original map will show us exactly how much and where the heat risk would be modified by an intervention.


## Literature

Gao, B., Yang, J., Chen, Z. et al. Causal inference from cross-sectional earth system data with geographical convergent cross mapping. Nat Commun 14, 5875 (2023). https://doi.org/10.1038/s41467-023-41619-6

Hoang, ND., Huynh, TC. & Bui, DT. An interpretable machine learning framework for mapping hotspots and identifying their driving factors in urban environments during heat waves. Environ Monit Assess 197, 1017 (2025). https://doi.org/10.1007/s10661-025-14461-0

Yeboah, E., Wang, G., Hagan, D.F.T. et al. A causal investigation of land use and land cover change on emerging urban heat island footprints in a mid-latitude region. Environ Dev Sustain (2025). https://doi.org/10.1007/s10668-025-06328-8


## Acknowledgements

We would like to express our sincere gratitude to our mentor, Daniel Fiifi Tawia Hagan (Hydro-Climate Extremes Lab, Ghent University), for his invaluable guidance and support throughout this study. His expertise and encouragement were instrumental in shaping the direction of this work. We extend our appreciation to the Climatematch Impact Scholars Program for providing the resources and platform necessary to conduct this research.


## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0-or-later). See [`LICENSE`](LICENSE).
