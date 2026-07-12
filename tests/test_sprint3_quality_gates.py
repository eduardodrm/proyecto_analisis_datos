from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
FEATURES_CSV = DATA_DIR / "features_kmeans_sprint2.csv"


def test_features_file_exists() -> None:
    assert FEATURES_CSV.exists(), f"No existe: {FEATURES_CSV}"


def test_features_shape_and_no_nans() -> None:
    df = pd.read_csv(FEATURES_CSV)
    # Según Sprint 2 (estado actual del repo)
    assert df.shape[0] == 300
    assert df.shape[1] == 15

    # NaNs
    assert int(df.isna().sum().sum()) == 0


def test_features_all_numeric() -> None:
    df = pd.read_csv(FEATURES_CSV)
    # Si hay objetos (strings), esto fallará (coerción a NaN se reflejaría en test NaNs).
    for c in df.columns:
        converted = pd.to_numeric(df[c], errors="coerce")
        assert int(converted.isna().sum()) == 0

