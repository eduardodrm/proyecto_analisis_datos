"""Preparación de datos para Sprint 2 (EDA/limpieza/features sin entrenar KMeans).

Tareas incluidas:
1) Cargar dataset consolidado: data/dataset_consolidado_sprint2.csv
2) Reportar resumen antes/después (nulos, outliers capados).
3) Limpieza determinista:
   - imputación numérica: mediana por columna
   - outliers: capping por percentiles (1% - 99%)
   - convertir columnas a numéricas
4) Construir dataset final de features SOLO NUMÉRICAS:
   - sin user_id
   - sin NaNs
5) Persistir:
   - data/features_kmeans_sprint2.csv
   - docs/cleaning_report_sprint2.md
   - docs/features_schema_sprint2.md

Uso:
  python etl/prepare_features_sprint2.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class FeatureConfig:
    consolidated_csv: Path = DATA_DIR / "dataset_consolidado_sprint2.csv"
    output_features_csv: Path = DATA_DIR / "features_kmeans_sprint2.csv"

    report_md: Path = DOCS_DIR / "cleaning_report_sprint2.md"
    schema_md: Path = DOCS_DIR / "features_schema_sprint2.md"

    outlier_lower_q: float = 0.01
    outlier_upper_q: float = 0.99


def _numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    # Convertir todas las columnas a numéricas donde aplique.
    out = df.copy()
    for c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def _cap_outliers(df: pd.DataFrame, cols: List[str], q_low: float, q_high: float) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    capped = df.copy()
    meta: Dict[str, Dict[str, float]] = {}

    for c in cols:
        s = capped[c]
        lo = float(s.quantile(q_low))
        hi = float(s.quantile(q_high))
        meta[c] = {"q_low": q_low, "q_high": q_high, "cap_low": lo, "cap_high": hi}
        capped[c] = np.where(s < lo, lo, np.where(s > hi, hi, s))

    return capped, meta


def _impute_median(df: pd.DataFrame, cols: List[str]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    out = df.copy()
    impute_values: Dict[str, float] = {}
    for c in cols:
        med = float(out[c].median())
        impute_values[c] = med
        out[c] = out[c].fillna(med)
    return out, impute_values


def _build_schema_md(features: pd.DataFrame, schema_path: Path) -> None:
    lines: List[str] = []
    lines.append("# features_kmeans_sprint2.csv - Esquema")
    lines.append("")
    lines.append(f"Columnas: {len(features.columns)}")
    lines.append("")
    lines.append("| columna | dtype | min | max | missing |")
    lines.append("|---|---|---:|---:|---:|")
    for c in features.columns:
        s = features[c]
        lines.append(
            f"| {c} | {str(s.dtype)} | {float(s.min()):.6f} | {float(s.max()):.6f} | {int(s.isna().sum())} |"
        )

    schema_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cfg = FeatureConfig()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(cfg.consolidated_csv)

    # Reporte antes
    before_shape = df.shape
    before_missing = df.isna().mean().sort_values(ascending=False)

    # Construir base numérica
    df_num = _numeric_df(df)

    # Features: SOLO numéricas, excluyendo user_id
    if "user_id" not in df_num.columns:
        raise ValueError("No existe 'user_id' en el dataset consolidado.")
    feature_cols = [c for c in df_num.columns if c != "user_id"]

    # Capado de outliers
    capped, cap_meta = _cap_outliers(
        df_num,
        cols=feature_cols,
        q_low=cfg.outlier_lower_q,
        q_high=cfg.outlier_upper_q,
    )

    # Imputación
    imputed, imputes = _impute_median(capped, cols=feature_cols)

    # Garantías para KMeans
    features = imputed[feature_cols].copy()

    # Si una columna está 100% en NaN (p.ej. extra_metric_b por ausencia en el payload),
    # la imputación por mediana produce NaN. En ese caso usamos 0 como fallback.
    cols_all_nan = [c for c in feature_cols if features[c].isna().all()]
    if cols_all_nan:
        for c in cols_all_nan:
            features[c] = 0.0

    if features.isna().any().any():
        # Si todavía hay NaNs, fallamos para no producir un dataset inválido para KMeans.
        raise RuntimeError("Aún existen NaNs luego de imputación/fallback. Revisa el pipeline.")


    features.to_csv(cfg.output_features_csv, index=False)

    after_missing = features.isna().mean().sort_values(ascending=False)

    # Reporte MD
    report_lines: List[str] = []
    report_lines.append("# cleaning_report_sprint2")
    report_lines.append("")
    report_lines.append(f"Entrada: {cfg.consolidated_csv}")
    report_lines.append(f"Salida features: {cfg.output_features_csv}")
    report_lines.append("")

    report_lines.append("## Resumen")
    report_lines.append(f"Shape antes: {before_shape}")
    report_lines.append(f"Shape features: {features.shape}")
    report_lines.append("")

    report_lines.append("## Nulos antes (top 15)")
    report_lines.append("\n" + before_missing.head(15).to_markdown())
    report_lines.append("")

    report_lines.append("## Nulos después (features)")
    report_lines.append("\n" + after_missing.head(15).to_markdown())
    report_lines.append("")

    report_lines.append("## Outliers capados (1% - 99%)")
    # mostrar solo algunas columnas para no hacer el md enorme
    report_lines.append("- Columnas capadas: " + str(len(feature_cols)))
    sample_cols = feature_cols[: min(10, len(feature_cols))]
    report_lines.append("")
    report_lines.append("| columna | cap_low | cap_high |")
    report_lines.append("|---|---:|---:|")
    for c in sample_cols:
        meta = cap_meta[c]
        report_lines.append(f"| {c} | {meta['cap_low']:.6f} | {meta['cap_high']:.6f} |")

    report_lines.append("")
    report_lines.append("## Imputación (mediana)")
    report_lines.append(f"- Columnas imputadas: {len(feature_cols)}")
    report_lines.append("")
    report_lines.append("| columna | median |")
    report_lines.append("|---|---:|")
    for c in sample_cols:
        report_lines.append(f"| {c} | {imputes[c]:.6f} |")

    cfg.report_md.write_text("\n".join(report_lines), encoding="utf-8")

    _build_schema_md(features, cfg.schema_md)

    print("OK - features generadas")
    print(f"OK - cleaning_report_sprint2: {cfg.report_md}")
    print(f"OK - features_schema_sprint2: {cfg.schema_md}")


if __name__ == "__main__":
    main()

