# System Capacity & Care Load Analytics for Unaccompanied Children

## Overview

An analytics-only Data Science internship project that transforms the supplied HHS Unaccompanied Alien Children Program CSV into a reproducible validation, metric, EDA, and Streamlit dashboard workflow. It uses aggregate counts only and contains no machine-learning prediction model.

## Problem Statement

Raw daily records do not provide a centralized view of the combined CBP/HHS care load, transfers, discharges, flow pressure, relative high-load periods, or reporting anomalies.

## Objectives

- Inspect and preserve the original CSV.
- Clean dates and comma-formatted numeric values.
- Flag missing, duplicate, invalid, negative, and logically inconsistent records.
- Calculate load, flow-balance, rolling, volatility, and relative high-load indicators.
- Present transparent, interactive operational analytics.

## Dataset

The raw file is stored at `data/raw/uac_dataset.csv`. The supplied CSV has 1,170 rows and six columns. It contains 720 populated observations from 2023-01-12 through 2025-12-21 and 450 fully blank trailing rows. The populated data has no missing fields or duplicate dates. The pipeline retains blank rows in validation outputs and does not alter the raw file.

## Features

- Total System Load = CBP Load + HHS Load.
- Net Intake Pressure = Transfers to HHS - HHS Discharges.
- Cumulative Net Intake as an analytical flow-balance indicator, not an official backlog.
- Safe care-load growth rate, 7/14-observation rolling averages, 14-observation rolling standard deviation, and discharge offset ratio.
- Configurable percentile-based relative high-load flag and sustained positive-pressure duration.
- Streamlit filters, Plotly charts, data-quality reporting, insights, and downloads.

## Methodology

See [docs/methodology.md](docs/methodology.md). Anomalies are flagged rather than silently deleted. No official capacity threshold is inferred because none is present in the dataset.

## KPIs

The dashboard displays current Total System Load, CBP Load, HHS Load, Net Intake Pressure, Cumulative Net Intake, growth rate, high-load observations, and sustained positive-pressure periods. Values are calculated at runtime from the raw CSV.

## Dashboard

Run the Streamlit app to explore daily, weekly, and monthly views, date ranges, rolling averages, threshold settings, pressure duration, anomaly visibility, and downloads.

## Technologies

Python, pandas, NumPy, Plotly, and Streamlit.

## Project Structure

```text
uac-care-load-analytics/
├── app.py
├── requirements.txt
├── README.md
├── data/raw/uac_dataset.csv
├── data/processed/cleaned_uac_data.csv
├── src/{data_loader,preprocessing,metrics,analysis,visualizations}.py
├── notebooks/exploratory_analysis.ipynb
└── docs/{methodology,executive_summary,research_paper_support}.md
```

## Installation

```powershell
cd uac-care-load-analytics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the Application

```powershell
streamlit run app.py
```

## Results

The supplied dataset produced 720 usable dated observations. The maximum observed Total System Load is 11,762 children on 2023-12-20. The pipeline found no negative values and flagged 86 populated rows for logical validation issues; 450 fully blank source rows are also retained and flagged. See [docs/executive_summary.md](docs/executive_summary.md) and [docs/research_paper_support.md](docs/research_paper_support.md) for generated results.

## Limitations

This is an observational aggregate dataset. The analysis does not prove official capacity exceedance, causal relationships, individual outcomes, policy success, or an official backlog. Reporting cadence includes gaps that should be reviewed with the data owner.

## Future Scope

Add validated official capacity and backlog denominators, document reporting cadence, add stakeholder-reviewed definitions, and compare the flow-balance indicator with authoritative operational records.

## Upload to GitHub

Create a repository, then from this project directory run:

```powershell
git init
git add .
git commit -m "Build UAC care load analytics project"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repository>.git
git push -u origin main
```

## Streamlit Deployment

Push the project to GitHub, open Streamlit Community Cloud, choose the repository and `app.py` entrypoint, and deploy. Ensure `data/raw/uac_dataset.csv` is committed because the app reads that project-local file.

## Author

Ankita S Narayankar
