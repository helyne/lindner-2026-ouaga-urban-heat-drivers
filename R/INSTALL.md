# R Dependencies

## Requirements

- R >= 4.3

## Install packages

```r
install.packages(c("spEDM", "terra", "SpatialPack", "ggplot2", "yaml"))
```

Tested with: spEDM 1.7, terra 1.8.54, SpatialPack 0.4.1, ggplot2 3.5.2, yaml 2.3.7

## Usage

Run all R scripts from the repository root:

```bash
cd ouaga-urban-heat-drivers
Rscript R/gccm_analysis.R --fixed-E=3 --tau=1
```
