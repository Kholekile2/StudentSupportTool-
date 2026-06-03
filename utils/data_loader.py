"""
data_loader.py
---------------
Single entry point for data validation. Every page imports load_data() from here.
Enforces the data dictionary rules — validation is never accidentally skipped.
"""

import pandas as pd
from pathlib import Path

# The rules from the data dictionary, expressed as Python constants.
# If the dictionary changes, you change these. One source of truth.
VALID_PROVINCES = {
    "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape",
    "Limpopo", "Mpumalanga", "North West", "Free State", "Northern Cape",
}
VALID_AGE_BANDS = {"18-21", "22-25", "26-30", "31+"}
VALID_AREA_TYPES = {"Urban", "Township", "Rural"}
VALID_DEVICE_ACCESS = {"Phone only", "Phone + shared laptop", "Own laptop"}
VALID_INTERNET = {"Stable", "Limited", "Unstable"}
VALID_EMPLOYMENT = {"Unemployed", "Part-time", "Full-time", "Studying"}
VALID_RISK = {"Low", "Medium", "High"}
CONFIDENCE_RANGE = (1, 5)  # inclusive


def confidence_band(score):
    """Turn a 1–5 score into a Low/Medium/High band.
    Matches the rule from the data dictionary exactly: 1-2 Low, 3 Medium, 4-5 High.
    Returns None if score is missing or invalid — we don't guess."""
    if pd.isna(score):
        return None
    try:
        s = int(score)
    except (ValueError, TypeError):
        return None
    if s < CONFIDENCE_RANGE[0] or s > CONFIDENCE_RANGE[1]:
        return None  # out-of-range values (like L008's 7) get filtered, not coerced
    if s <= 2:
        return "Low"
    if s == 3:
        return "Medium"
    return "High"


def load_data(csv_source="data/learners.csv"):
    """Load a CSV and return (dataframe, validation_report).
    
    csv_source can be a file path (string) or file-like object (e.g. from upload).
    Returns tuple: (df with all rows, report dict with validation issues found).
    
    Design: bad rows are flagged, not silently dropped. Users decide what to do.
    """
    # If csv_source is a string, treat it as a file path. Otherwise assume it's
    # a file-like object (e.g. from a Streamlit upload).
    if isinstance(csv_source, str):
        path = Path(csv_source)
        if not path.exists():
            raise FileNotFoundError(f"Could not find {csv_source}. Is the file in the data/ folder?")
        df = pd.read_csv(path)
    else:
        # File-like object from Streamlit uploader
        try:
            df = pd.read_csv(csv_source)
        except Exception as e:
            raise ValueError(f"Could not read uploaded file as a CSV: {e}")

    # Schema check — every required column must be present.
    required_columns = {
        "learner_id", "age_band", "province", "area_type",
        "device_access", "internet_access",
        "digital_confidence", "programming_confidence", "ai_confidence",
        "employment_status", "support_need", "attendance_risk",
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Uploaded data is missing required columns: {sorted(missing)}. "
            f"Please use a CSV that matches the schema in the data dictionary."
        )

    # --- Validation: find issues without modifying the data yet ---
    issues = {
        "duplicate_ids": [],
        "out_of_range_confidence": [],
        "invalid_province": [],
        "missing_value_count": 0,
        "total_rows": len(df),
    }

    # Duplicates — same learner_id appearing more than once
    dup_ids = df[df.duplicated("learner_id", keep=False)]["learner_id"].unique().tolist()
    issues["duplicate_ids"] = dup_ids

    # Out-of-range confidence scores in any of the three confidence columns
    for col in ["digital_confidence", "programming_confidence", "ai_confidence"]:
        # coerce to numeric so strings/blanks become NaN safely
        numeric = pd.to_numeric(df[col], errors="coerce")
        bad_mask = numeric.notna() & ((numeric < CONFIDENCE_RANGE[0]) | (numeric > CONFIDENCE_RANGE[1]))
        for idx in df[bad_mask].index:
            issues["out_of_range_confidence"].append({
                "learner_id": df.loc[idx, "learner_id"],
                "column": col,
                "value": numeric.loc[idx],
            })

    # Province names not in the valid set (e.g. the deliberate "Gautng" typo)
    bad_prov = df[~df["province"].isin(VALID_PROVINCES) & df["province"].notna()]
    for idx in bad_prov.index:
        issues["invalid_province"].append({
            "learner_id": df.loc[idx, "learner_id"],
            "value": df.loc[idx, "province"],
        })

    # Total missing values across the whole frame
    issues["missing_value_count"] = int(df.isna().sum().sum()) + int((df == "").sum().sum())

    # --- Derive band columns fresh from the raw scores ---
    # We DON'T trust the band columns in the CSV (L008's band was deliberately
    # left as "High" even though the raw score was invalid). Always recompute.
    df["digital_confidence_band"] = df["digital_confidence"].apply(confidence_band)
    df["programming_confidence_band"] = df["programming_confidence"].apply(confidence_band)
    df["ai_confidence_band"] = df["ai_confidence"].apply(confidence_band)

    return df, issues
