# System Capacity & Care Load Analytics for Unaccompanied Children

## Abstract
This study presents an analytics-only workflow for describing observed daily CBP and HHS care-load measures, transfer and discharge flows, relative high-load periods, and data-quality conditions. The supplied aggregate CSV contained 720 usable dated observations from 2023-01-12 through 2025-12-21. The maximum observed combined load was 11,762 on 2023-12-20. No machine-learning model or official capacity claim is made.

## Keywords
Unaccompanied children; healthcare operations analytics; care load; flow balance; CBP; HHS; Streamlit; data quality

## Introduction and Background
The UAC care pipeline includes intake into CBP custody, transfers into HHS care, care delivery, and discharge to placement. Daily aggregate measures can support transparent operational monitoring without inferring individual-level information.

## Problem Statement and Objectives
The objective is to transform raw daily records into reproducible load, flow, rolling-average, volatility, relative high-load, and validation indicators. The project explicitly distinguishes observed counts from interpretation.

## Dataset Description
The source file contains Date plus five aggregate measures: apprehended and placed in CBP custody, children in CBP custody, transfers out of CBP custody, children in HHS care, and HHS discharges. The raw file had 1,170 rows and 6 columns; 450 rows were fully blank.

## Data Preprocessing and Methodology
Column names are canonicalized, dates are parsed with invalid dates retained as flags, numeric strings are trimmed and stripped of commas, and records are chronologically sorted. Duplicate rows, duplicate dates, missing values, negative values, and logical comparisons are flagged rather than silently removed. Valid dated observations feed the metrics and dashboard.

## Derived Metrics
Total System Load equals CBP Load plus HHS Load. Net Intake Pressure equals transfers minus discharges. Cumulative Net Intake is the cumulative sum of that flow difference and is not an official backlog. Growth is period-over-period percentage change with zero denominators treated as missing. Seven- and fourteen-observation rolling means, fourteen-observation rolling standard deviation, discharge offset ratio, a 75th-percentile relative high-load flag, and seven-observation sustained positive-pressure periods are calculated.

## System Architecture
CSV Dataset -> Data Loading -> Data Cleaning -> Data Validation -> Metric Engineering -> EDA -> Statistical Analysis -> Interactive Visualizations -> Streamlit Dashboard -> Insights and Executive Summary.

## Dashboard Design
The Streamlit dashboard provides date, granularity, rolling-average, threshold, pressure-duration, metric, and anomaly controls. It displays KPI cards, trends, flow balance, monthly summaries, data quality, insights, downloadable processed data, and this report.

## Results
- The maximum observed Total System Load was 11,762 on 2023-12-20.
- The average Total System Load during the selected period was 6,232.8.
- There were 238 observations where Net Intake Pressure was positive.
- 8 sustained positive-pressure period(s) met the 7-observation rule; the longest lasted 12 observations.
- CBP load was higher than HHS load on 0.0% of observed dates.

## Discussion, Limitations, and Future Scope
The results describe relative load and observed flow behavior. They do not establish official capacity exceedance, causal effects, individual outcomes, policy success, or an official backlog. Blank trailing rows and reporting cadence should be documented in future source releases. Future work should add validated capacity and backlog denominators, calendar-gap analysis, and stakeholder-reviewed operational definitions.

## Conclusion
A reproducible analytics pipeline makes the supplied UAC aggregate data easier to inspect, validate, and monitor while keeping claims bounded by the available evidence.

## References
- U.S. Department of Health and Human Services, Office of Refugee Resettlement, Unaccompanied Children Program data source supplied for this project.
- pandas, NumPy, Plotly, and Streamlit project documentation.
