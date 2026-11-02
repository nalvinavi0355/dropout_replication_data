# Who Drops Out? Replication data and code

Data and code for the article **"Who Drops Out? A National Analysis of Dropout Rates in Indonesian Higher Education"** (Alvin Armein, Universitas Sumatera Utara; under review).

The study links two public PDDikti datasets for academic year 2024 (registered students and student dropouts) for 31,170 study programs at 3,811 institutions, and estimates adjusted dropout rate ratios with Poisson models.

## Contents
| Path | Description |
|---|---|
| `analysis_cells.csv.gz` | Linked analysis dataset: one row per study program x sex x age band (268,392 rows), institutions anonymised |
| `program_level.csv` | The same data summed to one row per study program, with dropout rates |
| `CODEBOOK.md` | Column definitions and data sources |
| `Supplementary_Who_Drops_Out.xlsx` | Supplementary tables S1–S21: rates, all models, anonymised program-level data |
| `code/` | Python scripts that build the dataset, fit the models and draw the figures (see `code/README.md`) |

## Anonymisation
Institution names, national institution codes (NPSN) and districts are not included. Each institution has a random ID (INST-0001 ...), the same in all files.

## Source data
Kementerian Pendidikan Tinggi, Sains, dan Teknologi, Pusat Data dan Teknologi Informasi (2025):
- Registered students: https://data.kemdiktisaintek.go.id/dataset/data-jumlah-mahasiswa-tahun-2025
- Student dropouts: https://data.kemdiktisaintek.go.id/dataset/data-jumlah-mahasiswa-drop-out-tahun-2025

The original ministry files are not redistributed here; download them from the links above to rerun `code/`.

## Licence
Data files: CC BY 4.0. Code: MIT. See `LICENSE`.

## Citation
Please cite the article and this repository (see `CITATION.cff`).
