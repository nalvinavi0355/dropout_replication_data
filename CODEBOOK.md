# Codebook: Who Drops Out? analysis data (anonymised)

Derived from two public datasets of the Ministry of Higher Education, Science, and Technology of Indonesia (Kemendiktisaintek), Pusat Data dan Teknologi Informasi, both from PDDikti, academic year 2024 (published 2025):
- Registered students: https://data.kemdiktisaintek.go.id/dataset/data-jumlah-mahasiswa-tahun-2025
- Student dropouts (putus studi, dikeluarkan, mengundurkan diri): https://data.kemdiktisaintek.go.id/dataset/data-jumlah-mahasiswa-drop-out-tahun-2025

All data are aggregated counts with no individual-level information. Institution names, national institution codes (NPSN) and districts are removed; each institution has a random ID (INST-0001 ...), the same in both files and in sheet S21 of the article's supplementary workbook.

## analysis_cells.csv.gz
One row per study program x sex x age band (268,392 rows; 289,670 dropouts; 10,754,154 registered students).

| Column | Description |
|---|---|
| institution_id | Random institution ID |
| institution_type | university, institute, college_sekolah_tinggi, polytechnic, academy, community_academy |
| sector | public_education_ministry, private_education_ministry, public_religious_ministry, private_religious_ministry, civil_service_PTK |
| province | Province of the institution |
| program_code, program_name | Study program code (national program classification) and name |
| level_code | D1, D2, D3, D4, S1, S2, S2 Terapan, S3, S3 Terapan, Profesi, Sp-1, Sp-2 |
| field_group | education, health, natural_sciences_math, humanities, religion, social_sciences, economics_business, agriculture, arts, engineering |
| stem | STEM or non_STEM (classification in the source data) |
| sex | male, female, unknown |
| age_band | 15-19, 20-22, 23-25, 26-30, 31-40, 41-80, invalid (age missing or outside 15-80) |
| dropout | Number of students who dropped out |
| registered | Number of registered students |
| is_universitas_terbuka | True for Universitas Terbuka, analysed separately |

Program attributes are blank for 122 cells (376 dropouts) in programs with no registered students; these are excluded from rate analyses.

## program_level.csv
One row per study program with registered students (31,217 rows), identical to sheet S21 of the supplementary workbook: institution_id, institution_type, sector, province, program_name, level_code, field_group, stem, is_universitas_terbuka, dropout, registered, dropout_rate_pct (dropout / registered x 100).
