# Reversal of UHI Drivers in a Sahelian City

Source repository for the Impact Scholars Program 2025–2026 micropublication
*"Reversal of UHI Drivers in a Sahelian City: Low Built-Up Density Increases
Heat in Ouagadougou"* by Lindner, Adamson, Ajadi, Christa, and Hagan.

The rendered paper is built with [MyST Markdown](https://mystmd.org/) and
deployed via the ISP `deploy-paper.yml` GitHub Action.

## Repository contents

| File | Purpose |
|------|---------|
| `index.md` | Manuscript text |
| `myst.yml` | Authors, keywords, bibliography, ISP nexus config |
| `bib.bib` | Bibliography (BibTeX) |
| `figure.png` | Main figure (4 panels: study area, SHAP, susceptibility maps, GCCM) |
| `thumbnails/thumbnail.png` | Gallery thumbnail (Ouagadougou LST map) |
| `environment.yml` | Conda environment for building the paper locally |

## Building locally

```bash
mamba env create -f environment.yml
mamba activate isp-paper
myst start            # live preview at http://localhost:3000
myst build --html     # static build into _build/
```

## Underlying analysis

All notebooks, scripts, and reproducibility documentation for the analysis that
produced the figure live in a separate repository:
<https://github.com/helyne/ouaga-urban-heat-drivers>

That repo contains the data download notebooks, modelling pipeline, R-based
GCCM workflow, and end-to-end instructions.
