"""Entrenamiento KMeans (Sprint 4): Elbow + Silhouette.

Objetivo:
- Ejecutar KMeans para k en rango (k_min..k_max) usando configuración base generada en Sprint 3.
- Calcular:
  - inertia (para Elbow)
  - silhouette_score
- Guardar:
  - CSV de métricas
  - JSON de métricas
  - gráfico Elbow (PNG)
  - reporte Markdown con justificación del k óptimo

Uso:
  python etl/train_kmeans_sprint4.py

"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler



PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class Sprint4Config:
    base_config_json: Path = DOCS_DIR / "sprint3_kmeans_base_config.json"

    features_csv: Path = DATA_DIR / "features_kmeans_sprint2.csv"

    out_metrics_csv: Path = DOCS_DIR / "sprint4_kmeans_metrics.csv"
    out_metrics_json: Path = DOCS_DIR / "sprint4_kmeans_metrics.json"

    out_elbow_png: Path = DOCS_DIR / "sprint4_elbow.png"
    out_report_md: Path = DOCS_DIR / "sprint4_kmeans_report.md"

    # Standarización recomendada para métricas de distancia (silhouette).
    standardize: bool = True


def _load_base_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No existe base_config_json: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _maybe_import_matplotlib_pyplot():
    # Import diferido para no fallar si el entorno no tiene display.
    # Si matplotlib no está instalado, devolvemos None y continuamos sin gráfico.
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        return plt
    except ModuleNotFoundError:
        return None



def _compute_silhouette_for_k(
    X: np.ndarray,
    k: int,
    random_state: int,
    init: str,
    max_iter: int,
    n_init: int,
) -> Tuple[float, float]:
    # fit
    model = KMeans(
        n_clusters=k,
        random_state=random_state,
        init=init,
        max_iter=max_iter,
        n_init=n_init,
    )
    labels = model.fit_predict(X)

    # inertia (Elbow)
    inertia = float(model.inertia_)

    # silhouette: requiere k >= 2
    # Si algún cluster colapsa y genera solo 1 etiqueta efectiva, silhouette falla.
    unique_labels = np.unique(labels)
    if unique_labels.size <= 1:
        return inertia, float("nan")

    sil = float(silhouette_score(X, labels))
    return inertia, sil


def _choose_best_k(k_to_sil: Dict[int, float], k_to_inertia: Dict[int, float]) -> int:
    # Estrategia simple/robusta:
    # - elegir k con mayor silhouette
    # - si hay nan, ignorar
    # - si tie, elegir el menor k (más simple)
    best_k: int | None = None
    best_sil = -math.inf

    for k, sil in k_to_sil.items():
        if sil is None or (isinstance(sil, float) and np.isnan(sil)):
            continue
        if sil > best_sil:
            best_sil = sil
            best_k = k
        elif sil == best_sil and best_k is not None and k < best_k:
            best_k = k

    if best_k is None:
        # Fallback: menor inercia
        best_k = min(k_to_inertia.keys(), key=lambda kk: k_to_inertia[kk])

    return int(best_k)


def main() -> None:
    cfg = Sprint4Config()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    base_cfg = _load_base_config(cfg.base_config_json)

    k_min = int(base_cfg["k_range"]["k_min"])
    k_max = int(base_cfg["k_range"]["k_max"])
    k_step = int(base_cfg["k_range"]["k_step"])
    ks = list(range(k_min, k_max + 1, k_step))

    random_state = int(base_cfg["random_state"])
    init = str(base_cfg["init"])
    max_iter = int(base_cfg["max_iter"])
    n_init = int(base_cfg["n_init"])

    features_cols = list(base_cfg["features"])

    if not cfg.features_csv.exists():
        raise FileNotFoundError(f"No existe features_csv: {cfg.features_csv}")

    df = pd.read_csv(cfg.features_csv)
    missing = [c for c in features_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en features_csv respecto a base_config: {missing}")

    X_df = df[features_cols].copy()
    X = X_df.to_numpy(dtype=float)

    if cfg.standardize:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    metrics: List[Dict[str, Any]] = []
    k_to_inertia: Dict[int, float] = {}
    k_to_sil: Dict[int, float] = {}

    for k in ks:
        inertia, sil = _compute_silhouette_for_k(
            X=X,
            k=k,
            random_state=random_state,
            init=init,
            max_iter=max_iter,
            n_init=n_init,
        )
        k_to_inertia[int(k)] = inertia
        k_to_sil[int(k)] = sil
        metrics.append(
            {
                "k": int(k),
                "inertia": inertia,
                "silhouette_score": sil,
            }
        )
        print(f"OK - k={k}: inertia={inertia:.4f} silhouette={sil}")

    best_k = _choose_best_k(k_to_sil, k_to_inertia)

    # Guardar métricas
    metrics_df = pd.DataFrame(metrics).sort_values("k")
    metrics_df.to_csv(cfg.out_metrics_csv, index=False)

    payload = {
        "k_range": {"k_min": k_min, "k_max": k_max, "k_step": k_step, "ks": ks},
        "model_params": {
            "random_state": random_state,
            "init": init,
            "max_iter": max_iter,
            "n_init": n_init,
            "standardize": cfg.standardize,
        },
        "best_k": best_k,
        "metrics": metrics,
    }
    cfg.out_metrics_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Gráfico Elbow (opcional si matplotlib no está instalado)
    plt = _maybe_import_matplotlib_pyplot()
    if plt is not None:
        fig = plt.figure(figsize=(8, 5))
        plt.plot(metrics_df["k"], metrics_df["inertia"], marker="o")
        plt.title("Sprint 4 — Elbow (Inertia vs k)")
        plt.xlabel("k")
        plt.ylabel("inertia")
        plt.grid(True, alpha=0.3)

        # Mark best k
        if best_k in metrics_df["k"].values:
            best_inertia = float(metrics_df.loc[metrics_df["k"] == best_k, "inertia"].iloc[0])
            plt.scatter([best_k], [best_inertia], color="red", zorder=5, label=f"best_k={best_k}")
            plt.legend()

        plt.tight_layout()
        fig.savefig(cfg.out_elbow_png, dpi=150)
        plt.close(fig)
    else:
        print("WARN - matplotlib no está instalado; se omite el gráfico Elbow PNG")


    # Report MD
    best_sil = payload["metrics"][int(best_k) - k_min]["silhouette_score"] if len(payload["metrics"]) == (k_max - k_min + 1) else k_to_sil[best_k]

    lines: List[str] = []
    lines.append("# Sprint 4 — Entrenamiento KMeans + métricas (Elbow y Silhouette)")
    lines.append("")
    lines.append("## Configuración")
    lines.append(f"- k_range: {k_min}..{k_max} (step {k_step})")
    lines.append(f"- features: {len(features_cols)} columnas")
    lines.append(f"- standardize: {cfg.standardize}")
    lines.append("")
    lines.append("## Métricas por k")
    lines.append("")

    # Tabla simple en markdown
    lines.append("| k | inertia | silhouette_score |")
    lines.append("|---:|---:|---:|")
    for row in metrics_df.itertuples(index=False):
        k = int(row.k)
        inertia = float(row.inertia)
        sil = row.silhouette_score
        sil_str = "NaN" if (isinstance(sil, float) and np.isnan(sil)) else f"{float(sil):.6f}"
        lines.append(f"| {k} | {inertia:.4f} | {sil_str} |")

    lines.append("")
    lines.append("## Selección del k óptimo")
    lines.append(f"- k propuesto (best_k): **{best_k}**")
    lines.append(f"- Justificación: se elige el k con **mayor silhouette_score** (distancia/estructura de clusters).")
    lines.append("")
    lines.append("## Elbow")
    lines.append(f"- Gráfico: `{cfg.out_elbow_png}`")

    lines.append("")
    lines.append("## Archivos generados")
    lines.append(f"- Métricas CSV: `{cfg.out_metrics_csv}`")
    lines.append(f"- Métricas JSON: `{cfg.out_metrics_json}`")
    lines.append(f"- Reporte MD: `{cfg.out_report_md}`")

    cfg.out_report_md.write_text("\n".join(lines), encoding="utf-8")

    print("OK - sprint4_kmeans_report")
    print(f"OK - metrics csv: {cfg.out_metrics_csv}")
    print(f"OK - metrics json: {cfg.out_metrics_json}")
    print(f"OK - elbow png: {cfg.out_elbow_png}")
    print(f"OK - report md: {cfg.out_report_md}")


if __name__ == "__main__":
    main()

