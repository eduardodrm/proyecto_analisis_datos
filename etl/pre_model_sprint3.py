"""Pre-modelado (Sprint 3): quality gates + configuración base de KMeans (sin entrenar).

Objetivo (Sprint 3):
- Definir features finales (ya están en data/features_kmeans_sprint2.csv)
- Aplicar quality gates (sin fit/entrenamiento)
- Guardar reporte de esquema y configuración base del modelo

Uso:
  py etl/pre_model_sprint3.py

Salida:
  docs/sprint3_pre_model_report.md
  docs/sprint3_kmeans_base_config.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class PreModelConfig:
    features_csv: Path = DATA_DIR / "features_kmeans_sprint2.csv"

    report_md: Path = DOCS_DIR / "sprint3_pre_model_report.md"
    base_config_json: Path = DOCS_DIR / "sprint3_kmeans_base_config.json"

    # Config base (no se entrena en este sprint)
    k_min: int = 2
    k_max: int = 10
    k_step: int = 1

    random_state: int = 42
    init: str = "k-means++"
    max_iter: int = 300
    n_init: int = 10


def _ensure_numeric_no_nan(df: pd.DataFrame, feature_cols: List[str]) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}

    # Coerción numérica defensiva
    df_num = df[feature_cols].copy()
    for c in feature_cols:
        df_num[c] = pd.to_numeric(df_num[c], errors="coerce")

    nan_total = int(df_num.isna().sum().sum())
    nan_by_col = df_num.isna().sum().sort_values(ascending=False)

    stats["nan_total"] = nan_total
    stats["nan_by_col_top"] = nan_by_col.head(10).to_dict()

    if nan_total != 0:
        raise RuntimeError("Quality gate falló: existen NaNs en features.")

    dtypes = df_num.dtypes.astype(str).to_dict()
    stats["dtypes"] = dtypes

    return stats


def main() -> None:
    cfg = PreModelConfig()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if not cfg.features_csv.exists():
        raise FileNotFoundError(f"No existe features_csv: {cfg.features_csv}")

    df = pd.read_csv(cfg.features_csv)

    if "user_id" in df.columns:
        raise ValueError("El dataset de features no debe incluir user_id (ya excluido en Sprint 2).")

    feature_cols = list(df.columns)

    shape = df.shape

    # Quality gates: numéricas y sin NaNs
    qg_stats = _ensure_numeric_no_nan(df, feature_cols)

    ks = list(range(cfg.k_min, cfg.k_max + 1, cfg.k_step))

    base_config = {
        "model": "KMeans",
        "constraint": "Sin entrenamiento en Sprint 3",
        "features": feature_cols,
        "shape": {"rows": int(shape[0]), "cols": int(shape[1])},
        "random_state": cfg.random_state,
        "init": cfg.init,
        "max_iter": cfg.max_iter,
        "n_init": cfg.n_init,
        "k_range": {"k_min": cfg.k_min, "k_max": cfg.k_max, "k_step": cfg.k_step, "ks": ks},
        "quality_gates": {
            "nan_total": qg_stats["nan_total"],
            "nan_by_col_top": qg_stats["nan_by_col_top"],
            "dtypes": qg_stats["dtypes"],
        },
    }

    cfg.base_config_json.write_text(json.dumps(base_config, ensure_ascii=False, indent=2), encoding="utf-8")

    # Report MD
    lines: List[str] = []
    lines.append("# Sprint 3 — Pre-modelado (KMeans, sin entrenamiento)")
    lines.append("")
    lines.append(f"Features CSV: `{cfg.features_csv}`")
    lines.append("")
    lines.append("## Shape")
    lines.append(f"- Filas: {shape[0]}")
    lines.append(f"- Columnas: {shape[1]}")
    lines.append("")

    lines.append("## Quality gates")
    lines.append(f"- Total NaNs: {qg_stats['nan_total']}")
    lines.append("- Dtypes (string):")
    for c, dt in qg_stats["dtypes"].items():
        lines.append(f"  - {c}: {dt}")
    lines.append("")

    lines.append("## Configuración base de KMeans (para Sprint 4)")
    lines.append(f"- random_state: {cfg.random_state}")
    lines.append(f"- init: {cfg.init}")
    lines.append(f"- max_iter: {cfg.max_iter}")
    lines.append(f"- n_init: {cfg.n_init}")
    lines.append(f"- k_range: {cfg.k_min}..{cfg.k_max} (step {cfg.k_step})")

    lines.append("")
    lines.append("> Nota: no se ejecuta KMeans.fit en este sprint.")

    cfg.report_md.write_text("\n".join(lines), encoding="utf-8")

    print("OK - pre_model_sprint3")
    print(f"OK - report: {cfg.report_md}")
    print(f"OK - base config: {cfg.base_config_json}")


if __name__ == "__main__":
    main()

