"""Sprint 6 — Interpretación de segmentos (perfilamiento por cluster).

Objetivo:
- Leer el dataset enriquecido con cluster:
  data/dataset_consolidado_con_cluster_sprint5.csv
- Calcular métricas por cluster (tamaño, %, promedio, mediana).
- Construir una interpretación de negocio por cluster a partir de "drivers":
  variables que más se alejan del promedio global (normalización z-score).

Uso:
  python etl/profile_clusters_sprint6.py

Salida:
- data/cluster_profile_sprint6.csv
- docs/sprint6_cluster_interpretation.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class Sprint6Config:
    input_csv: Path = DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv"
    out_profile_csv: Path = DATA_DIR / "cluster_profile_sprint6.csv"
    out_report_md: Path = DOCS_DIR / "sprint6_cluster_interpretation.md"

    # drivers:
    # - usamos z-score (por feature) y tomamos las top_n con mayor desviación absoluta
    top_n_drivers: int = 5
    cluster_col: str = "cluster"

    # columnas no numéricas / especiales a excluir del perfil numérico
    exclude_cols: Tuple[str, ...] = ("cluster", "user_id")


def _coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def _zscore(series: pd.Series) -> pd.Series:
    # Evitar división por 0
    std = float(series.std(ddof=0))
    if std == 0.0 or np.isnan(std):
        return series * 0.0
    return (series - float(series.mean())) / std


def _compute_cluster_profile(df: pd.DataFrame, feature_cols: List[str], cluster_col: str) -> pd.DataFrame:
    # tamaño
    cluster_size = df.groupby(cluster_col).size().rename("cluster_size")
    cluster_pct = (cluster_size / len(df) * 100.0).rename("cluster_pct")

    # stats mean/median por cluster
    grouped = df.groupby(cluster_col)[feature_cols]
    mean_df = grouped.mean().add_suffix("_mean")
    median_df = grouped.median().add_suffix("_median")

    # combinar
    profile = pd.concat([cluster_size, cluster_pct, mean_df, median_df], axis=1).reset_index()
    return profile


def _compute_drivers(df: pd.DataFrame, feature_cols: List[str], cluster_col: str, top_n: int) -> Dict[int, List[Tuple[str, float]]]:
    # z-score global por feature (sobre la columna original)
    global_z = df[feature_cols].apply(_zscore)

    # para cada cluster, tomamos el mean del z-score (drivers)
    drivers: Dict[int, List[Tuple[str, float]]] = {}
    for cl, sub_idx in df.groupby(cluster_col).groups.items():
        sub = global_z.loc[sub_idx, feature_cols]
        # score por feature: mean(z) absoluto
        score = sub.mean(axis=0)
        score_abs = score.abs().sort_values(ascending=False).head(top_n)

        drivers[int(cl)] = [(feat, float(score[feat])) for feat in score_abs.index]
    return drivers


def _humanize_feature(feature: str) -> str:
    # mapeo mínimo para interpretaciones.
    return feature.replace("_", " ")


def _build_text_interpretation(
    df: pd.DataFrame,
    profile_row: pd.Series,
    drivers: List[Tuple[str, float]],
    feature_mean_cols: List[str],
) -> str:
    # Seleccionamos “drivers” por z-score: si z>0 arriba, z<0 abajo.
    # redactamos 2-4 bullets con interpretaciones genéricas y 1-2 específicas usando mean.
    bullets: List[str] = []
    for feat, z in drivers:
        mean_col = f"{feat}_mean"
        mean_val = profile_row.get(mean_col, np.nan)
        direction = "alto" if z > 0 else "bajo"
        bullets.append(
            f"- Driver: **{_humanize_feature(feat)}** está en un nivel **{direction}** para el cluster (z≈{z:.2f}, media≈{mean_val:.2f})."
        )

    # Heurísticas de “tipo de segmento” (muy simple, pero útil)
    # consumo y valor
    consumption_feats = [f for f in ["horas_consumo_mensual", "gasto_mensual", "cantidad_contenidos_vistos"] if f in df.columns]
    promo_feats = [f for f in ["porcentaje_uso_promociones"] if f in df.columns]
    age_feats = [f for f in ["antiguedad_cliente_meses", "edad"] if f in df.columns]

    # determinar “qué predomina” por media
    # (solo si los drivers incluyen esas columnas)
    drivers_feats = {feat for feat, _ in drivers}
    segment_theme = "segmento"
    if any(f in drivers_feats for f in consumption_feats) and any(f in drivers_feats for f in promo_feats):
        segment_theme = "segmento orientado a consumo vs. sensibilidad a promos"
    elif any(f in drivers_feats for f in consumption_feats):
        segment_theme = "segmento de intensidad de uso"
    elif any(f in drivers_feats for f in promo_feats):
        segment_theme = "segmento con respuesta a promociones"
    elif any(f in drivers_feats for f in age_feats):
        segment_theme = "segmento de perfil maduro/edad"

    return "\n".join(bullets) + f"\n\n**Lectura de negocio (heurística):** cluster principalmente caracterizado como **{segment_theme}**."


def main() -> None:
    cfg = Sprint6Config()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not cfg.input_csv.exists():
        raise FileNotFoundError(f"No existe: {cfg.input_csv}")

    df = pd.read_csv(cfg.input_csv)

    if cfg.cluster_col not in df.columns:
        raise ValueError(f"No existe columna '{cfg.cluster_col}' en: {cfg.input_csv}")

    # features numéricas: todas las que sean numéricas excepto exclude_cols
    candidate_cols = [c for c in df.columns if c not in cfg.exclude_cols]
    # coerce numérico
    df_num = _coerce_numeric(df, candidate_cols)

    # quedarnos con columnas que efectivamente sean numéricas (y no todas NaN)
    feature_cols = [c for c in candidate_cols if df_num[c].notna().any()]
    feature_cols = [c for c in feature_cols if c != cfg.cluster_col]

    # asegurar que no haya NaNs en el perfil
    # (si existieran, imputamos 0 para no romper sprint)
    df_num[feature_cols] = df_num[feature_cols].fillna(0)

    profile = _compute_cluster_profile(df_num, feature_cols=feature_cols, cluster_col=cfg.cluster_col)
    profile.to_csv(cfg.out_profile_csv, index=False)

    drivers = _compute_drivers(df_num, feature_cols=feature_cols, cluster_col=cfg.cluster_col, top_n=cfg.top_n_drivers)

    # Reporte MD
    lines: List[str] = []
    lines.append("# Sprint 6 — Interpretación de segmentos (KMeans)")
    lines.append("")
    lines.append(f"Dataset de entrada: `{cfg.input_csv}`")
    lines.append("")
    lines.append("## Resumen por cluster")
    lines.append("")
    # Mostrar tamaño y %
    # Pandas.to_markdown requiere paquete opcional 'tabulate'. Para que el script sea
    # ejecutable sin dependencias extra, generamos tablas markdown manualmente.
    def _df_to_md_table_simple(df_tbl: pd.DataFrame, float_fmt: str = "{:.4f}") -> str:
        cols_local = list(df_tbl.columns)
        header = "| " + " | ".join(cols_local) + " |"
        sep = "|" + "|".join(["---"] * len(cols_local)) + "|"
        rows_md: List[str] = [header, sep]
        for _, r in df_tbl.iterrows():
            vals: List[str] = []
            for c in cols_local:
                v = r[c]
                if isinstance(v, (float, np.floating)):
                    vals.append(float_fmt.format(float(v)))
                else:
                    vals.append(str(v))
            rows_md.append("| " + " | ".join(vals) + " |")
        return "\n".join(rows_md)

    summary_cols = ["cluster", "cluster_size", "cluster_pct"]
    lines.append(_df_to_md_table_simple(profile[summary_cols], float_fmt="{:.2f}"))
    lines.append("")
    lines.append("## Perfil numérico (promedio y mediana)")
    lines.append("")

    # Elegimos un subconjunto de columnas para no hacer el md enorme: mean de cada feature + top features
    feature_mean_cols = [f"{c}_mean" for c in feature_cols]
    feature_median_cols = [f"{c}_median" for c in feature_cols]

    # limitar cantidad de columnas en la tabla a 12 mean + 12 median (si hay más, recortamos)
    max_features = min(6, len(feature_cols))
    table_features = feature_cols[:max_features]
    table_cols = ["cluster", "cluster_size", "cluster_pct"] + [f"{c}_mean" for c in table_features] + [f"{c}_median" for c in table_features]

    # Tabla manual para evitar dependencia opcional 'tabulate'
    lines.append(_df_to_md_table_simple(profile[table_cols], float_fmt="{:.4f}"))
    lines.append("")


    lines.append("## Drivers y lectura de negocio por cluster")
    lines.append("")
    for cl in sorted(profile[cfg.cluster_col].unique()):
        row = profile.loc[profile[cfg.cluster_col] == cl].iloc[0]
        cl_drivers = drivers.get(int(cl), [])[: cfg.top_n_drivers]

        lines.append(f"### Cluster {int(cl)}")
        # drivers bullets
        lines.append(
            _build_text_interpretation(
                df=df_num,
                profile_row=row,
                drivers=cl_drivers,
                feature_mean_cols=feature_mean_cols,
            )
        )
        lines.append("")

    lines.append("## Nota")
    lines.append(
        "- La interpretación se basa en desviación vs. la media global (z-score) sobre las variables numéricas disponibles.\n"
        "- Ajustes finos (nombres de segmentos, acciones sugeridas) deben alinearse con conocimiento de negocio."
    )

    cfg.out_report_md.write_text("\n".join(lines), encoding="utf-8")
    print("OK - profile_clusters_sprint6")
    print(f"OK - out_profile_csv: {cfg.out_profile_csv}")
    print(f"OK - out_report_md: {cfg.out_report_md}")


if __name__ == "__main__":
    main()
