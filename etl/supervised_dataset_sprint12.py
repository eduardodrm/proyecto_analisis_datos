"""Sprint 12 — Aprendizaje supervisado (predicción de cluster)

Objetivo:
- Construir dataset supervisado para predecir `cluster` (KMeans) usando
  features numéricas.

Fuentes:
- X: data/features_kmeans_sprint2.csv
- y: data/user_clusters_sprint5.csv (columna: cluster)

Salida (data/):
- supervised_X_train_sprint12.csv
- supervised_X_val_sprint12.csv
- supervised_y_train_sprint12.csv
- supervised_y_val_sprint12.csv
- docs/sprint12_supervised_dataset_report.json

Uso:
python etl/supervised_dataset_sprint12.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class Config:
    features_path: Path = DATA_DIR / "features_kmeans_sprint2.csv"
    clusters_path: Path = DATA_DIR / "user_clusters_sprint5.csv"

    out_x_train: Path = DATA_DIR / "supervised_X_train_sprint12.csv"
    out_x_val: Path = DATA_DIR / "supervised_X_val_sprint12.csv"
    out_y_train: Path = DATA_DIR / "supervised_y_train_sprint12.csv"
    out_y_val: Path = DATA_DIR / "supervised_y_val_sprint12.csv"

    report_path: Path = DOCS_DIR / "sprint12_supervised_dataset_report.json"

    test_size: float = 0.2
    random_state: int = 42


def _coerce_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def build_supervised_dataset(config: Config) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    if not config.features_path.exists():
        raise FileNotFoundError(f"No existe: {config.features_path}")
    if not config.clusters_path.exists():
        raise FileNotFoundError(f"No existe: {config.clusters_path}")

    df_x = pd.read_csv(config.features_path)
    df_y = pd.read_csv(config.clusters_path)

    if "cluster" not in df_y.columns:
        raise ValueError(
            f"En {config.clusters_path} no existe columna 'cluster'. "
            f"Columnas disponibles: {list(df_y.columns)}"
        )

    # X: features numéricas (sin user_id / cluster)
    x_cols = [c for c in df_x.columns if c != "cluster"]
    df_x = df_x[x_cols].copy()

    # Preferimos merge por user_id si existe en ambos
    if "user_id" in df_x.columns and "user_id" in df_y.columns:
        df = df_x.merge(df_y[["user_id", "cluster"]], on="user_id", how="inner")
        if df.empty:
            raise ValueError("El merge X/y produjo un dataset vacío.")
        y = df["cluster"]
        X = df.drop(columns=["cluster", "user_id"], errors="ignore")
    else:
        # caso típico del repo: X no trae user_id => alineación por índice/orden
        if len(df_x) != len(df_y):
            raise ValueError(
                "No se puede alinear X e y por ausencia de user_id. "
                f"len(X)={len(df_x)} len(y)={len(df_y)}"
            )
        X = df_x
        y = df_y["cluster"]

    X = _coerce_numeric_features(X)

    if X.isna().any().any():
        na_cols = X.columns[X.isna().any()].tolist()
        raise ValueError(f"Existen NaNs en features luego de coerción numérica. Columnas: {na_cols[:20]}")
    if y.isna().any():
        raise ValueError("Existen NaNs en y (cluster).")

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=y,
    )

    return X_train, X_val, y_train, y_val


def main() -> None:
    cfg = Config()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    X_train, X_val, y_train, y_val = build_supervised_dataset(cfg)

    X_train.to_csv(cfg.out_x_train, index=False)
    X_val.to_csv(cfg.out_x_val, index=False)
    y_train.to_frame(name="cluster").to_csv(cfg.out_y_train, index=False)
    y_val.to_frame(name="cluster").to_csv(cfg.out_y_val, index=False)

    report = {
        "features_path": str(cfg.features_path),
        "clusters_path": str(cfg.clusters_path),
        "n_samples_total": int(len(X_train) + len(X_val)),
        "n_features": int(X_train.shape[1]),
        "test_size": cfg.test_size,
        "random_state": cfg.random_state,
        "train": {
            "n": int(X_train.shape[0]),
            "y_distribution": y_train.value_counts(normalize=True).sort_index().to_dict(),
        },
        "val": {
            "n": int(X_val.shape[0]),
            "y_distribution": y_val.value_counts(normalize=True).sort_index().to_dict(),
        },
        "saved_files": {
            "X_train": str(cfg.out_x_train),
            "X_val": str(cfg.out_x_val),
            "y_train": str(cfg.out_y_train),
            "y_val": str(cfg.out_y_val),
        },
    }

    cfg.report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[Sprint12] Dataset supervisado generado correctamente.")
    print(f"- X_train: {cfg.out_x_train}")
    print(f"- X_val:   {cfg.out_x_val}")
    print(f"- y_train: {cfg.out_y_train}")
    print(f"- y_val:   {cfg.out_y_val}")
    print(f"- Report:  {cfg.report_path}")


if __name__ == "__main__":
    main()

