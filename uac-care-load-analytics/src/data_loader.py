from pathlib import Path
from typing import Any

import pandas as pd

EXPECTED_COLUMNS = [
    "Date",
    "Children apprehended and placed in CBP custody*",
    "Children in CBP custody",
    "Children transferred out of CBP custody",
    "Children in HHS Care",
    "Children discharged from HHS Care",
]

COLUMN_RENAMES = {
    "Date": "date",
    "Children apprehended and placed in CBP custody*": "apprehended_cbp",
    "Children in CBP custody": "cbp_load",
    "Children transferred out of CBP custody": "transfers_to_hhs",
    "Children in HHS Care": "hhs_load",
    "Children discharged from HHS Care": "hhs_discharges",
}


def load_raw_data(path: str | Path) -> pd.DataFrame:
    """Load the raw CSV exactly as supplied, including blank rows."""
    return pd.read_csv(path, dtype=object, keep_default_na=True)


def inspect_raw_data(data: pd.DataFrame) -> dict[str, Any]:
    """Return reproducible structural and quality facts about the raw dataframe."""
    date_values = pd.to_datetime(data.get("Date"), errors="coerce")
    return {
        "shape": data.shape,
        "columns": list(data.columns),
        "dtypes": data.dtypes.astype(str).to_dict(),
        "missing_by_column": data.isna().sum().to_dict(),
        "duplicate_rows": int(data.duplicated().sum()),
        "duplicate_dates": int(data["Date"].duplicated().sum()),
        "invalid_dates": int(date_values.isna().sum()),
        "date_min": date_values.min(),
        "date_max": date_values.max(),
        "expected_columns_present": list(data.columns) == EXPECTED_COLUMNS,
    }


def canonical_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """Rename known source columns to stable names used by the analysis code."""
    missing = set(EXPECTED_COLUMNS) - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {sorted(missing)}")
    return data.rename(columns=COLUMN_RENAMES).copy()
