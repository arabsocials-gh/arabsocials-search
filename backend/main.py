from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import pandas as pd
import numpy as np
import math
import os

app = FastAPI(title="ArabSocials Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load & clean data once at startup ──────────────────────────────────────────
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "users.xlsx")

df = pd.read_excel(EXCEL_PATH, engine="openpyxl")

# Keep only relevant columns + display columns
FILTER_COLS = [
    "Country", "State", "City", "Location", "Nationality",
    "Date of Birth", "Age", "Gender", "Marital Status",
    "Profession", "Education", "Height", "Religion",
    "About Me", "Interests", "Language Spoken",
]
DISPLAY_COLS = ["ID", "Name", "Username", "Image"] + FILTER_COLS

df = df[[c for c in DISPLAY_COLS if c in df.columns]].copy()

# Clean Age — keep only sane values
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df.loc[~df["Age"].between(10, 100), "Age"] = np.nan

# Remove null/placeholder countries
df = df[~df["Country"].isin(["null", None]) & df["Country"].notna()]

def safe_list(series: pd.Series) -> list:
    return sorted(series.dropna().astype(str).unique().tolist())

def split_multi(series: pd.Series, sep=";") -> List[str]:
    """Collect all unique tokens from a semicolon-separated column."""
    vals = set()
    for cell in series.dropna():
        for part in str(cell).split(sep):
            v = part.strip()
            if v:
                vals.add(v)
    return sorted(vals, key=str.lower)

# ── Options endpoint ────────────────────────────────────────────────────────────
@app.get("/options")
def get_options():
    return {
        "countries":      safe_list(df["Country"]),
        "nationalities":  safe_list(df["Nationality"]),
        "genders":        safe_list(df["Gender"]),
        "marital_statuses": safe_list(df["Marital Status"]),
        "educations":     safe_list(df["Education"]),
        "religions":      safe_list(df["Religion"]),
        "professions":    safe_list(df["Profession"]),
        "languages":      split_multi(df["Language Spoken"]),
        "interests":      split_multi(df["Interests"]),
        "age_min":        int(df["Age"].min(skipna=True)),
        "age_max":        int(df["Age"].max(skipna=True)),
    }

# ── Search endpoint ─────────────────────────────────────────────────────────────
@app.get("/search")
def search(
    country:        Optional[str] = None,
    state:          Optional[str] = None,
    city:           Optional[str] = None,
    nationality:    Optional[str] = None,
    gender:         Optional[str] = None,
    marital_status: Optional[str] = None,
    education:      Optional[str] = None,
    religion:       Optional[str] = None,
    profession:     Optional[str] = None,
    language:       Optional[str] = None,   # comma-separated → match ANY
    interest:       Optional[str] = None,   # comma-separated → match ANY
    age_min:        Optional[int] = None,
    age_max:        Optional[int] = None,
    about_keyword:  Optional[str] = None,   # free-text search in About Me
    page:           int = Query(1, ge=1),
    page_size:      int = Query(20, ge=1, le=100),
):
    result = df.copy()

    # Exact-match filters
    exact = {
        "Country":        country,
        "State":          state,
        "City":           city,
        "Nationality":    nationality,
        "Gender":         gender,
        "Marital Status": marital_status,
        "Education":      education,
        "Religion":       religion,
        "Profession":     profession,
    }
    for col, val in exact.items():
        if val and col in result.columns:
            result = result[result[col].astype(str).str.lower() == val.lower()]

    # Age range
    if age_min is not None:
        result = result[result["Age"] >= age_min]
    if age_max is not None:
        result = result[result["Age"] <= age_max]

    # Language — match ANY of the requested languages
    if language:
        langs = [l.strip().lower() for l in language.split(",") if l.strip()]
        if langs:
            def has_lang(cell):
                if pd.isna(cell):
                    return False
                cell_langs = [x.strip().lower() for x in str(cell).split(";")]
                return any(l in cell_langs for l in langs)
            result = result[result["Language Spoken"].apply(has_lang)]

    # Interest — match ANY of the requested interests
    if interest:
        ints = [i.strip().lower() for i in interest.split(",") if i.strip()]
        if ints:
            def has_interest(cell):
                if pd.isna(cell):
                    return False
                cell_ints = [x.strip().lower() for x in str(cell).split(";")]
                return any(i in cell_ints for i in ints)
            result = result[result["Interests"].apply(has_interest)]

    # Free-text search in About Me
    if about_keyword:
        result = result[
            result["About Me"].astype(str).str.contains(about_keyword, case=False, na=False)
        ]

    total = len(result)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    page_df = result.iloc[start:end]

    # Serialize safely
    records = []
    for _, row in page_df.iterrows():
        rec = {}
        for col in page_df.columns:
            val = row[col]
            if pd.isna(val) if not isinstance(val, str) else False:
                rec[col] = None
            elif isinstance(val, float) and val == int(val):
                rec[col] = int(val)
            else:
                rec[col] = val
        records.append(rec)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "results": records,
    }
