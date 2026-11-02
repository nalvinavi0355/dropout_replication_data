# Who Drops Out? Replication code

Replication code for "Who Drops Out? A National Analysis of Dropout Rates in Indonesian Higher Education".

## Data (public, not included)
Download both files from the Kemendiktisaintek open data portal and save them in `data/`:
- Mahasiswa Terdaftar.xlsx: https://data.kemdiktisaintek.go.id/dataset/data-jumlah-mahasiswa-tahun-2025
- Mahasiswa DO.xlsx: https://data.kemdiktisaintek.go.id/dataset/data-jumlah-mahasiswa-drop-out-tahun-2025

Both cover academic year 2024 (published 2025).

## Steps (Python 3.11+, pandas, numpy, scipy, matplotlib, openpyxl)
1. `python convert_xlsx_to_csv.py "data/Mahasiswa DO.xlsx" data/do.csv`
2. `python convert_xlsx_to_csv.py "data/Mahasiswa Terdaftar.xlsx" data/reg.csv`
3. `python build.py`: cleans, links and aggregates to program x sex x age-band cells (output/cells.pkl)
4. `python analysis.py`: rate tables and Poisson models with cluster-robust SEs (output/dropout_analysis_tables.xlsx)
5. `python figures.py`: Figures 1-4 (output/*.png)

The Poisson estimator and sandwich standard errors are implemented directly in numpy/scipy (analysis.py, function `poisson`).
