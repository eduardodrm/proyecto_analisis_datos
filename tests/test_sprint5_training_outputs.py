from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def _labels_csv() -> Path:
    return DATA_DIR / "user_clusters_sprint5.csv"


def _enriched_dataset_csv() -> Path:
    return DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv"


def test_labels_files_exist() -> None:
    assert _labels_csv().exists(), f"No existe: {_labels_csv()}"
    assert _enriched_dataset_csv().exists(), f"No existe: {_enriched_dataset_csv()}"


def test_labels_shape_and_no_nans() -> None:
    df = pd.read_csv(_labels_csv())
    assert set(df.columns) == {"user_id", "cluster"}
    assert int(df.isna().sum().sum()) == 0
    assert df.shape[0] == 300


def test_enriched_dataset_has_cluster_and_no_nans() -> None:
    df = pd.read_csv(_enriched_dataset_csv())
    assert "cluster" in df.columns
    assert int(df.isna().sum().sum()) == 0
    assert df.shape[0] == 300


def test_cluster_is_int_like() -> None:
    df = pd.read_csv(_labels_csv())
    # cluster debe ser entero o convertíble sin crear NaNs
    converted = pd.to_numeric(df["cluster"], errors="coerce")
    assert int(converted.isna().sum()) == 0

