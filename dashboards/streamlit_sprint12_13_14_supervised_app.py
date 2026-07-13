from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
REPO_DIR = PROJECT_ROOT / "repo"


@st.cache_data(show_spinner=False)
def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    return pd.read_csv(path)


def _extract_confusion_matrix(cm_obj: Any) -> list[list[int]]:
    """Normaliza la matriz de confusión desde el reporte.

    Puede venir como:
    - list[list[int]]
    - dict {"labels": [...], "confusion_matrix": [[...], ...]}
    """

    if isinstance(cm_obj, dict):
        cm = cm_obj.get("confusion_matrix")
    else:
        cm = cm_obj

    if not isinstance(cm, list) or not all(isinstance(r, list) for r in cm):
        raise ValueError("Matriz de confusión con formato inesperado")
    return cm


def _format_labels(labels: list[Any]) -> list[str]:
    return [str(x) for x in labels]


def _get_doc_report_path_for_sprint(sprint: int) -> Path:
    if sprint == 12:
        return DOCS_DIR / "sprint12_supervised_dataset_report.json"
    if sprint == 13:
        return DOCS_DIR / "sprint13_supervised_train_report.json"
    # Sprint 14 no tiene report JSON en el repo; se usa el contrato/artefactos existentes.
    raise FileNotFoundError("Sprint 14 no tiene reporte JSON dedicado en docs/.")


def show_dataset_overview() -> None:
    st.subheader("Sprint 12 — Dataset supervisado (overview)")

    report_path = _get_doc_report_path_for_sprint(12)
    report = load_json(report_path)

    # métricas de dataset
    cols = ["n_samples_total", "n_features", "test_size", "random_state"]
    metric_tbl = {c: report.get(c) for c in cols}

    df_metrics = pd.DataFrame(
        [{"propiedad": k, "valor": v} for k, v in metric_tbl.items()],
    )
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

    # Distribuciones
    def _dist_to_df(dist: dict[str, float], split_name: str) -> pd.DataFrame:
        return pd.DataFrame(
            {"split": split_name, "clase": list(dist.keys()), "proporcion": list(dist.values())}
        )

    train_dist = report.get("train", {}).get("y_distribution", {})
    val_dist = report.get("val", {}).get("y_distribution", {})

    if train_dist and val_dist:
        st.markdown("**Distribución de clases (y) — train/val**")
        c1, c2 = st.columns(2)
        with c1:
            st.dataframe(_dist_to_df(train_dist, "train"), use_container_width=True)
        with c2:
            st.dataframe(_dist_to_df(val_dist, "val"), use_container_width=True)
    else:
        st.info("No se encontró distribución de clases en el reporte de Sprint 12.")

    # Visual: proporciones en barras
    if train_dist:
        classes = sorted(train_dist.keys(), key=lambda x: int(x))
        proportions = [train_dist[c] for c in classes]
        st.bar_chart(pd.DataFrame({"proporcion": proportions}, index=classes))


def show_supervised_training_models() -> None:
    st.subheader("Sprint 13 — Modelos supervisados y resultados")

    report_path = DOCS_DIR / "sprint13_supervised_train_report.json"
    report = load_json(report_path)

    models = report.get("models", {})
    if not models:
        st.info("El reporte no incluye sección 'models'.")
        return

    model_keys = list(models.keys())
    selected_model = st.sidebar.radio("Modelo", options=model_keys, index=0, horizontal=True)

    split = st.sidebar.radio("Split", options=["baseline", "tuned"], index=1, horizontal=True)

    model_obj = models[selected_model][split]
    metrics = model_obj.get("metrics", {})

    st.markdown("### Métricas")
    metric_items = []
    for k in ["accuracy", "f1_macro"]:
        if k in metrics:
            metric_items.append({"métrica": k, "valor": metrics[k]})

    if metric_items:
        st.dataframe(pd.DataFrame(metric_items), use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron métricas en el reporte.")

    # Confusion matrix (PNG si existe)
    png_key = "confusion_matrix_png"
    cm_png = model_obj.get(png_key)
    if cm_png:
        cm_png_path = Path(cm_png)
        if cm_png_path.exists():
            st.markdown("### Matriz de confusión (PNG)")
            st.image(str(cm_png_path), use_container_width=True)
        else:
            st.info("El PNG de matriz de confusión no existe en el path del reporte.")

    # Confusion matrix (tabla)
    cm_obj = model_obj.get("confusion_matrix")
    labels = None
    if isinstance(cm_obj, dict):
        labels = cm_obj.get("labels")
    try:
        cm = _extract_confusion_matrix(cm_obj)
    except Exception:
        cm = None

    if cm is not None:
        if labels is None:
            labels = list(range(len(cm)))
        st.markdown("### Matriz de confusión (tabla)")
        cm_df = pd.DataFrame(cm, index=_format_labels(labels), columns=_format_labels(labels))
        st.dataframe(cm_df, use_container_width=True)


def show_recommendations_from_metrics() -> None:
    st.subheader("Lectura para negocio (insights rápidos)")

    report_path = DOCS_DIR / "sprint13_supervised_train_report.json"
    report = load_json(report_path)

    models = report.get("models", {})

    rows = []
    for model_key, splits in models.items():
        for split_key in ["baseline", "tuned"]:
            m = splits.get(split_key, {}).get("metrics", {})
            rows.append(
                {
                    "modelo": model_key,
                    "split": split_key,
                    "accuracy": m.get("accuracy"),
                    "f1_macro": m.get("f1_macro"),
                }
            )

    df = pd.DataFrame(rows)

    if df.empty:
        st.info("Sin datos para insights.")
        return

    # Mejor por f1_macro
    best = df.sort_values("f1_macro", ascending=False).iloc[0]
    st.success(
        f"Mejor configuración por F1 macro: {best['modelo']} ({best['split']}) = {best['f1_macro']:.3f}"
    )

    # Comparación baseline vs tuned
    pivot = df.pivot(index="modelo", columns="split", values="f1_macro")
    st.markdown("**F1 macro (baseline vs tuned)**")
    st.dataframe(pivot, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Dashboard - Supervisado (Sprint 12/13/14)", layout="wide")

    st.title("E3 — Modelos supervisados (Sprint 12/13/14)")

    st.markdown(
        "Este dashboard integra los artefactos generados en **Sprint 12** (dataset supervisado) y **Sprint 13** (entrenamiento y evaluación). "
        "En Sprint 14 se toma el contrato de exposición de métricas; si existieran artefactos adicionales, se incluirían aquí."
    )

    section = st.sidebar.selectbox(
        "Sección",
        options=["Dataset (Sprint 12)", "Entrenamiento (Sprint 13)", "Insights (negocio)"] ,
        index=1,
    )

    if section == "Dataset (Sprint 12)":
        show_dataset_overview()
    elif section == "Entrenamiento (Sprint 13)":
        show_supervised_training_models()
    else:
        show_recommendations_from_metrics()


if __name__ == "__main__":
    main()

