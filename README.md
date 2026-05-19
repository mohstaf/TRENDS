# TRENDS: Temporal Recent Epidemiology of Notifiable Diseases in Southeast Asia

**TRENDS** stands for **T**emporal **R**ecent **E**pidemiology of
**N**otifiable **D**iseases in **S**outheast Asia. It is an open,
harmonised, province-level weekly surveillance resource designed to
support comparative time-series and spatial epidemiology of priority
notifiable infections across Southeast Asia.

This repository hosts the construction script and analysis pipeline that
accompany the Thailand release of TRENDS, a decade-long (2016 to 2025)
province-level weekly dataset of dengue, chikungunya, and hand, foot,
and mouth disease (HFMD) across all 77 Thai provinces.

Researchers in other Southeast Asian countries are warmly invited to
reuse the dataset for cross-country comparative work and to contribute
their own national notifiable-disease records as additional country
releases of TRENDS. The Country column in both data sheets is intended
to make such extensions straightforward.

**Contents**

> TRENDS/\
> README.docx this file\
> LICENSE CC BY 4.0 (data) + MIT (code)\
> requirements.txt Python dependencies\
> build_dataset.py builds TRENDS.xlsx from the raw MOPH 506\
> line-list files (provenance / reproducibility)\
> analysis_pipeline.py loads the deposited dataset and writes the\
> four summary CSVs

build_dataset.py is the construction script that produced the deposited
TRENDS.xlsx. It is included for transparency and reproducibility: it
documents exactly how the 30 raw MOPH yearly disease files (one per
disease, per year, 2016 to 2025) were normalised, joined to the RTSD
ADM-1 province reference and the DOPA year-specific province
populations, and aggregated to the released province-week panel. The raw
MOPH 506 line-list files are not redistributed (individual-level
surveillance data under Thai data-sharing terms), so build_dataset.py
cannot be run end-to-end from this repo; download the deposit from
Zenodo instead and use analysis_pipeline.py to reproduce the analytic
summaries.

The **dataset itself** (TRENDS.xlsx) is archived on Zenodo, not in this
repository. Download it from the Zenodo record at
https://doi.org/10.5281/zenodo.20269896 and place it next to
analysis_pipeline.py before running the quick start below.

**The dataset**

TRENDS.xlsx (Thailand release) is a single Excel workbook with three
sheets. The weekly data sheet contains 40,579 rows by 18 columns and
provides weekly case counts and pre-computed incidence rates per 100,000
population for each (country, province, epidemiological week). The
province data sheet contains 77 rows by 16 columns and provides province
attributes (country, P-code, English name, centroid latitude and
longitude in WGS84, area in square kilometres) together with the
year-specific civil-registration population for each year from 2016 to
2025. The data dictionary sheet contains 22 rows by 5 columns and lists
every variable, the sheet on which it is stored, its data type, its unit
where applicable, and a concise definition.

Both data sheets share Country, P-code, and Province as join keys. To
recover the year-specific population denominator for any (P-code, Year)
row in weekly data, join the two sheets on P-code and select the
matching Population \<year\> column in province data.

Coverage of the Thailand release:

- 77 Thai provinces by 527 epidemiological weeks (1 January 2016 to 31
  December 2025).

- Three diseases: dengue (with severity strata dengue fever, dengue
  haemorrhagic fever, and dengue shock syndrome, plus a combined dengue
  total), chikungunya, and hand, foot, and mouth disease.

- 790,263 dengue, 32,265 chikungunya, and 713,822 HFMD cases over the
  ten-year window. 100 percent completeness across the grid.

- Country is Thailand for every row in this release.

**Data sources**

- **Disease counts:** Thailand Ministry of Public Health 506 notifiable
  disease surveillance system, Department of Disease Control
  (https://ddc.moph.go.th/).

- **Population denominators:** Bureau of Registration Administration,
  Department of Provincial Administration
  (https://stat.bora.dopa.go.th/).

- **Province polygons:** Royal Thai Survey Department, distributed via
  the OCHA Common Operational Dataset
  (https://data.humdata.org/dataset/cod-ab-tha), version v01, valid from
  22 January 2022.

**Quick start**

> git clone https://github.com/mohstaf/TRENDS.git\
> cd TRENDS\
> pip install -r requirements.txt\
> python analysis_pipeline.py \--xlsx \"TRENDS.xlsx\" \--outdir output

The pipeline writes four CSV summaries into the output folder:

- **validation_summary.csv:** row count, province count, week count,
  year range, total cases per disease.

- **annual_summary.csv:** yearly case counts per disease plus national
  civil-registration population.

- **phase_summary.csv:** mean annual incidence rate per 100,000 by
  pandemic phase (Pre-COVID 2016 to 2019, Pandemic 2020 to 2022,
  Post-acute 2023 to 2025), with percent change versus Pre-COVID.

- **top_provinces.csv:** top 10 provinces per disease by mean annual
  incidence rate.

Pandemic phase rate calculation: cases are aggregated to annual totals,
divided by the national population for that year (sum of provincial
populations), then averaged within each phase.

**Rebuilding the dataset from the raw MOPH files (provenance only)**

build_dataset.py is the script that constructed TRENDS.xlsx from the 30
raw MOPH 506 yearly disease files. The raw files are not redistributed
in this repository (they are individual-level surveillance records under
Thai data-sharing terms); the script is included as a transparent record
of how the deposited dataset was produced. With access to the raw
inputs, the build can be reproduced end to end:

> python build_dataset.py \\\
> \--src \<path to MOPH yearly disease files folder\> \\\
> \--master \<path to Disease Data (2016 - 2025) master workbook\> \\\
> \--out \"TRENDS.xlsx\" \\\
> \--country \"Thailand\"

The \<src\> folder must contain three subfolders (Dengue, Chikungunya,
Hand Foot and Mouth) each holding ten yearly Excel files (2016 to 2025).
The \<master\> workbook carries the RTSD ADM-1 province reference and
the year-specific DOPA province populations. The script runs an
exploratory pass, normalises the 2016 to 2024 and 2025 column layouts,
reconciles province names against the RTSD reference, assigns each case
to a Sunday-to-Saturday epidemiological week, aggregates to a complete
(country, province, year, week) grid, attaches the population
denominators, and writes the three-sheet output workbook with Country
populated as Thailand.

**Extending TRENDS to other Southeast Asian countries**

The dataset is designed for regional expansion. National surveillance
teams (or research groups working with national surveillance data) in
other Southeast Asian countries are encouraged to contribute their own
country releases. The recommended path is:

- Prepare a province-week panel for your country covering the same
  notifiable conditions (or any subset), following the column layout of
  the Thailand release.

- Fill the Country column with your country name.

- Open an issue or pull request on this repository, or contact the
  maintainers, to discuss harmonisation and joint release.

**Licence**

- **Dataset:** Creative Commons Attribution 4.0 International (CC BY
  4.0).

- **Code:** MIT License.

**Contact**

For questions about reuse, joint analyses, or contributing a new country
release of TRENDS, please contact us at mohstaf@outlook.com (Mohamed
Mustaf Ahmed) or doctorkrit@gmail.com (Krit Pongpirul), or open an issue
on the GitHub repository.
