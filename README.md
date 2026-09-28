# System Capacity & Care Load Analytics for Unaccompanied Children

A data analytics and visualization project designed to analyze care-load patterns, intake and discharge flows, capacity pressure, and trends in the Unaccompanied Children (UAC) care system.

## 📌 Project Overview

The **System Capacity & Care Load Analytics for Unaccompanied Children** project uses historical time-series data to understand how children move through different stages of the care system.

The project analyzes:

- Children entering CBP custody
- Children currently in CBP custody
- Children transferred from CBP
- Children receiving HHS care
- Children discharged from HHS care
- Total system care load
- Net intake pressure
- High-load periods
- Sustained periods of positive care pressure

The project focuses on **data analytics and visualization rather than machine learning**.

---

## 🎯 Objectives

The main objectives of this project are:

1. Analyze daily care-load data.
2. Compare CBP custody and HHS care loads.
3. Analyze transfers and discharges.
4. Calculate total system load.
5. Measure net intake pressure.
6. Identify high-load periods.
7. Analyze short-term and long-term trends.
8. Detect sustained positive intake pressure.
9. Provide an interactive dashboard for data exploration.
10. Present data-driven insights through visualizations.

---

## 📊 Dataset

The dataset contains the following fields:

| Column | Description |
|---|---|
| `Date` | Date of observation |
| `Children apprehended and placed in CBP custody` | Daily intake into CBP custody |
| `Children in CBP custody` | Children currently in CBP custody |
| `Children transferred out of CBP custody` | Children transferred from CBP |
| `Children in HHS Care` | Children currently receiving HHS care |
| `Children discharged from HHS Care` | Children discharged from HHS care |

The dataset was cleaned and validated before performing the analysis.

---

## 🧹 Data Preprocessing

The preprocessing stage includes:

- Date format conversion
- Numeric data conversion
- Removal of comma separators from numeric values
- Missing-value identification
- Duplicate-record detection
- Date sorting
- Data-quality validation
- Logical consistency checks

Missing dates are not automatically treated as zero because a missing observation does not necessarily represent zero activity.

---

## 📐 Key Metrics

### 1. Total System Load

```text
Total System Load =
Children in CBP Custody + Children in HHS Care
