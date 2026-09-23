from pathlib import Path

import numpy as np
import pandas as pd

from .data_loader import canonical_column_names, load_raw_data

NUMERIC_COLUMNS = [
    "apprehended_cbp",
    "cbp_load",
    "transfers_to_hhs",
    "hhs_load",
    "hhs_discharges",
]


def _numeric_series(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    cleaned = series.astype("string").str.strip().str.replace(",", "", regex=False)
    converted = pd.to_numeric(cleaned, errors="coerce")
    invalid = cleaned.notna() & converted.isna()
    return converted, invalid


def clean_data(raw_data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Clean source values and attach validation flags without hiding anomalies."""
    data = canonical_column_names(raw_data)
    data["source_row_number"] = np.arange(2, len(data) + 2)
    data["is_blank_row"] = data[["date", *NUMERIC_COLUMNS]].isna().all(axis=1)
    data["date"] = pd.to_datetime(data["date"], errors="coerce")

    invalid_numeric = pd.Series(False, index=data.index)
    for column in NUMERIC_COLUMNS:
        data[column], invalid_column = _numeric_series(data[column])
        data[f"invalid_{column}"] = invalid_column
        invalid_numeric |= invalid_column

    data["negative_value"] = data[NUMERIC_COLUMNS].lt(0).any(axis=1)
    data["duplicate_date"] = data["date"].notna() & data["date"].duplicated(keep=False)
    data["transfers_exceed_cbp_load"] = (
        data["transfers_to_hhs"].notna()
        & data["cbp_load"].notna()
        & (data["transfers_to_hhs"] > data["cbp_load"])
    )
    data["discharges_exceed_hhs_load"] = (
        data["hhs_discharges"].notna()
        & data["hhs_load"].notna()
        & (data["hhs_discharges"] > data["hhs_load"])
    )
    data["logical_validation_failure"] = data[
        ["negative_value", "transfers_exceed_cbp_load", "discharges_exceed_hhs_load"]
    ].any(axis=1)
    data["anomaly_flag"] = (
        data["is_blank_row"]
        | data["date"].isna()
        | data["invalid_apprehended_cbp"]
        | data["invalid_cbp_load"]
        | data["invalid_transfers_to_hhs"]
        | data["invalid_hhs_load"]
        | data["invalid_hhs_discharges"]
        | data["logical_validation_failure"]
    )

    data = data.sort_values("date", na_position="last", kind="stable").reset_index(drop=True)
    data["duplicate_row"] = data.duplicated(subset=["date", *NUMERIC_COLUMNS], keep=False)
    data["anomaly_flag"] |= data["duplicate_row"]

    quality = {
        "raw_rows": len(data),
        "raw_columns": len(raw_data.columns),
        "blank_rows": int(data["is_blank_row"].sum()),
        "invalid_dates": int(data["date"].isna().sum()),
        "duplicate_rows": int(raw_data.duplicated().sum()),
        "duplicate_dates": int(raw_data["Date"].duplicated().sum()),
        "duplicate_dates_nonblank": int(data["duplicate_date"].sum()),
        "missing_by_column": data[["date", *NUMERIC_COLUMNS]].isna().sum().to_dict(),
        "negative_value_rows": int(data["negative_value"].sum()),
        "logical_validation_failure_rows": int(data["logical_validation_failure"].sum()),
        "flagged_anomalies": int(data["anomaly_flag"].sum()),
    }
    return data, quality


def load_and_clean(path: str | Path) -> tuple[pd.DataFrame, dict[str, object]]:
    return clean_data(load_raw_data(path))


def analysis_frame(cleaned_data: pd.DataFrame, include_anomalies: bool = False) -> pd.DataFrame:
    """Return dated analytical rows; anomalies stay available unless explicitly hidden."""
    result = cleaned_data[cleaned_data["date"].notna()].copy()
    if not include_anomalies:
        result = result[~result["is_blank_row"]].copy()
    return result.reset_index(drop=True)
