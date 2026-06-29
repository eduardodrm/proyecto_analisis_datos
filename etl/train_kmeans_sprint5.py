"""Entrenamiento final KMeans (Sprint 5)

Objetivo:
- Entrenar KMeans utilizando el k óptimo (obtenido en Sprint 4).
- Asignar cluster a cada usuario.
- Persistir artefactos:
  - etiquetas (user_id -> cluster) y dataset enriquecido con cluster en /data/
  - modelo serializado en /repo/
  - reporte MD en /docs/

Uso:
  python etl/train_kmeans_sprint5.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
REPO_DIR = PROJECT_ROOT / "repo"


@dataclass(frozen=True)
class Sprint5Config:
    # Inputs from Sprint 2/4
    features_csv: Path = DATA_DIR / "features_kmeans_sprint2.csv"
    consolidated_csv: Path = DATA_DIR / "dataset_consolidado_sprint2.csv"
    sprint4_metrics_json: Path = DOCS_DIR / "sprint4_kmeans_metrics.json"

    # Outputs
    out_labels_csv: Path = DATA_DIR / "user_clusters_sprint5.csv"
    out_dataset_with_cluster_csv: Path = DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv"
    out_model_path: Path = REPO_DIR / "kmeans_model_sprint5.joblib"

    out_report_md: Path = DOCS_DIR / "sprint5_kmeans_train_report.md"

    # Model params
    random_state_default: int = 42
    init_default: str = "k-means++"
    max_iter_default: int = 300
    n_init_default: int = 10


def _load_sprint4_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_X_and_feature_cols(features_df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
    feature_cols = list(features_df.columns)
    X_df = features_df[feature_cols].copy()
    X = X_df.to_numpy(dtype=float)
    return X, feature_cols


def main() -> None:
    cfg = Sprint5Config()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPO_DIR.mkdir(parents=True, exist_ok=True)

    if not cfg.features_csv.exists():
        raise FileNotFoundError(f"No existe features_csv: {cfg.features_csv}")
    if not cfg.consolidated_csv.exists():
        raise FileNotFoundError(f"No existe consolidated_csv: {cfg.consolidated_csv}")

    base = _load_sprint4_metrics(cfg.sprint4_metrics_json)
    best_k = int(base["best_k"])
    model_params = base.get("model_params", {})

    random_state = int(model_params.get("random_state", cfg.random_state_default))
    init = str(model_params.get("init", cfg.init_default))
    max_iter = int(model_params.get("max_iter", cfg.max_iter_default))
    n_init = int(model_params.get("n_init", cfg.n_init_default))
    standardize = bool(model_params.get("standardize", True))

    # Load datasets
    features_df = pd.read_csv(cfg.features_csv)
    consolidated_df = pd.read_csv(cfg.consolidated_csv)

    if "user_id" not in consolidated_df.columns:
        raise ValueError("dataset_consolidado_sprint2.csv debe incluir user_id")

    # Sprint 2 garantiza que features no tiene user_id
    X, feature_cols = _extract_X_and_feature_cols(features_df)

    scaler = StandardScaler() if standardize else None
    if scaler is not None:
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X

    # Train
    model = KMeans(
        n_clusters=best_k,
        random_state=random_state,
        init=init,
        max_iter=max_iter,
        n_init=n_init,
    )

    labels = model.fit_predict(X_scaled)

    # Persist labels + enriched dataset
    out_df_labels = pd.DataFrame({"user_id": consolidated_df["user_id"].astype(int).values, "cluster": labels.astype(int)})
    out_df_labels.to_csv(cfg.out_labels_csv, index=False)

    enriched = consolidated_df.copy()
    enriched["cluster"] = labels.astype(int)
    enriched.to_csv(cfg.out_dataset_with_cluster_csv, index=False)

    # Persist model + scaler (if any)
    payload = {
        "model": model,
        "scaler": scaler,
        "feature_cols": feature_cols,
        "k": best_k,
        "model_params": {
            "random_state": random_state,
            "init": init,
            "max_iter": max_iter,
            "n_init": n_init,
            "standardize": standardize,
        },
    }
    joblib.dump(payload, cfg.out_model_path)

    # Report
    cluster_counts = out_df_labels["cluster"].value_counts().sort_index()
    total = len(out_df_labels)

    lines: List[str] = []
    lines.append("# Sprint 5 — Entrenamiento final KMeans + persistencia")
    lines.append("")
    lines.append("## k seleccionado")
    lines.append(f"- best_k (de Sprint 4): **{best_k}**")
    lines.append("")
    lines.append("## Entrenamiento")
    lines.append("- Algoritmo: KMeans (únicamente KMeans)")
    lines.append("- Standardize antes de entrenar: " + str(standardize))
    lines.append("- Parámetros:")
    lines.append(f"  - random_state: {random_state}")
    lines.append(f"  - init: {init}")
    lines.append(f"  - max_iter: {max_iter}")
    lines.append(f"  - n_init: {n_init}")
    lines.append("")
    lines.append("## Distribución de clusters")
    lines.append("")
    lines.append("| cluster | count | % |")
    lines.append("|---:|---:|---:|")
    for cl, cnt in cluster_counts.items():
        pct = float(cnt) / float(total) * 100.0
        lines.append(f"| {int(cl)} | {int(cnt)} | {pct:.2f} |")

    lines.append("")
    lines.append("## Archivos generados")
    lines.append(f"- Labels: `{cfg.out_labels_csv}`")
    lines.append(f"- Dataset enriquecido: `{cfg.out_dataset_with_cluster_csv}`")
    lines.append(f"- Modelo (joblib): `{cfg.out_model_path}`")

    cfg.out_report_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"OK - train_kmeans_sprint5")
    print(f"OK - k={best_k}")
    print(f"OK - out_labels_csv={cfg.out_labels_csv}")
    print(f"OK - out_dataset_with_cluster_csv={cfg.out_dataset_with_cluster_csv}")
    print(f"OK - out_model_path={cfg.out_model_path}")
    print(f"OK - report={cfg.out_report_md}")


if __name__ == "__main__":
    main()

