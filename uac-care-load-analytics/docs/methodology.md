# Methodology

The project keeps the supplied CSV unchanged in `data/raw/` and loads it with explicit validation. Known source headers are mapped to stable internal names. Numeric fields are trimmed, commas are removed, and invalid conversions become missing values plus flags. Dates are parsed with `errors="coerce"` and records are sorted chronologically.

Fully blank rows remain visible in the cleaned validation output and are counted as anomalies. Metrics use valid dated observations; the dashboard can show or hide flagged records. No record is automatically deleted because an anomaly may reflect a source-reporting issue.

## Metric definitions

- **Total System Load:** CBP Load + HHS Load.
- **Net Intake Pressure:** Transfers to HHS - HHS Discharges.
- **Cumulative Net Intake:** Cumulative sum of Net Intake Pressure; this is not an official backlog.
- **Growth rate:** Percentage change in Total System Load from the previous observation; zero denominators produce missing values.
- **Rolling averages:** Seven- and fourteen-observation rolling means for the requested load and flow measures.
- **Volatility:** Fourteen-observation rolling standard deviation of Total System Load.
- **Discharge Offset Ratio:** HHS Discharges / Transfers to HHS; zero transfer denominators are missing.
- **High-load:** Total System Load at or above the selected percentile, default 75th percentile. This is relative, not an official capacity threshold.
- **Sustained pressure:** Positive Net Intake Pressure for at least the selected number of consecutive observations, default seven.

Correlation is descriptive only: these are time-series operational measures with shared time trends and are not evidence of causation.
