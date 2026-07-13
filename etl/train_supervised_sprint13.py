"""Sprint 13 — Modelos supervisados + tuning y métricas

Objetivo:
- Entrenar al menos 2 algoritmos supervisados para predecir `cluster`.
- Baseline + tuning con GridSearchCV.
- Métricas: accuracy, F1-macro, matriz de confusión.
- Guardar reportes en /docs/ y modelos en /repo/.

Uso:
python etl/train_supervised_sprint13.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
REPO_DIR = ROOT / "repo"


@dataclass(frozen=True)
class Config:
    X_train_path: Path = DATA_DIR / "supervised_X_train_sprint12.csv"
    X_val_path: Path = DATA_DIR / "supervised_X_val_sprint12.csv"
    y_train_path: Path = DATA_DIR / "supervised_y_train_sprint12.csv"
    y_val_path: Path = DATA_DIR / "supervised_y_val_sprint12.csv"

    report_path: Path = DOCS_DIR / "sprint13_supervised_train_report.json"

    conf_matrix_png_prefix: Path = DOCS_DIR / "sprint13_confusion_matrix"

    random_state: int = 42


def _load_xy(config: Config) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    for p in [config.X_train_path, config.X_val_path, config.y_train_path, config.y_val_path]:
        if not p.exists():
            raise FileNotFoundError(f"No existe: {p}")

    X_train = pd.read_csv(config.X_train_path)
    X_val = pd.read_csv(config.X_val_path)

    y_train_df = pd.read_csv(config.y_train_path)
    y_val_df = pd.read_csv(config.y_val_path)

    if "cluster" not in y_train_df.columns or "cluster" not in y_val_df.columns:
        raise ValueError("Los CSV de y deben incluir columna 'cluster'.")

    y_train = y_train_df["cluster"]
    y_val = y_val_df["cluster"]

    # Robustez: convertir a numérico si aplica
    X_train = X_train.apply(pd.to_numeric, errors="coerce")
    X_val = X_val.apply(pd.to_numeric, errors="coerce")

    if X_train.isna().any().any() or X_val.isna().any().any():
        na_cols_train = X_train.columns[X_train.isna().any()].tolist()
        na_cols_val = X_val.columns[X_val.isna().any()].tolist()
        raise ValueError(
            "NaNs detectados en X. "
            f"train_na_cols={na_cols_train[:20]} val_na_cols={na_cols_val[:20]}"
        )

    return X_train, X_val, y_train, y_val


def _plot_and_save_confusion_matrix(
    y_true: pd.Series,
    y_pred: np.ndarray,
    labels: List[Any],
    title: str,
    png_path: Path,
) -> Dict[str, Any]:
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    plt.figure(figsize=(10, 8))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=90)
    plt.yticks(tick_marks, labels)
    plt.ylabel("True label")
    plt.xlabel("Predicted label")

    # Texto en cada celda
    thresh = cm.max() / 2.0 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j,
                i,
                format(cm[i, j], "d"),
                horizontalalignment="center",
                color="white" if cm[i, j] > thresh else "black",
            )

    plt.tight_layout()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(png_path, dpi=160)
    plt.close()

    # Asegurar tipos nativos
    labels_out = [int(x) if isinstance(x, (np.integer,)) else x for x in labels]
    cm_out = cm.tolist()

    return {
        "labels": labels_out,
        "confusion_matrix": cm_out,
    }


def _evaluate_model(model: Any, X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
    y_pred = model.predict(X_val)
    labels_sorted = sorted(list(pd.unique(y_val)))

    acc = float(accuracy_score(y_val, y_pred))
    f1_macro = float(f1_score(y_val, y_pred, average="macro"))

    cm = confusion_matrix(y_val, y_pred, labels=labels_sorted)

    labels_out = [int(x) if isinstance(x, (np.integer,)) else x for x in labels_sorted]
    cm_out = cm.tolist()

    return {
        "accuracy": acc,
        "f1_macro": f1_macro,
        "labels": labels_out,
        "confusion_matrix": cm_out,
    }


def _baseline_and_tuning(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    config: Config,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}

    numeric_features = list(X_train.columns)
    preprocessor = ColumnTransformer(
        transformers=[("num", StandardScaler(), numeric_features)],
        remainder="drop",
    )

    # -------------------- Logistic Regression --------------------
    logreg_pipe = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", LogisticRegression(random_state=config.random_state)),
        ]
    )

    logreg_baseline = logreg_pipe.set_params(
        model__solver="lbfgs",
        model__penalty="l2",
        model__C=1.0,
        model__max_iter=2000,
    )
    logreg_baseline.fit(X_train, y_train)

    logreg_baseline_metrics = _evaluate_model(logreg_baseline, X_val, y_val)

    conf_png = config.conf_matrix_png_prefix.parent / (
        config.conf_matrix_png_prefix.name + "_logreg_baseline.png"
    )
    conf_info = _plot_and_save_confusion_matrix(
        y_true=y_val,
        y_pred=logreg_baseline.predict(X_val),
        labels=logreg_baseline_metrics["labels"],
        title="LogisticRegression - baseline - confusion matrix",
        png_path=conf_png,
    )

    logreg_param_grid = {
        "model__solver": ["lbfgs"],
        "model__penalty": ["l2"],
        "model__C": [0.1, 0.3, 1.0, 3.0, 10.0],
    }

    logreg_search = GridSearchCV(
        estimator=logreg_pipe,
        param_grid=logreg_param_grid,
        scoring="f1_macro",
        cv=3,
        n_jobs=-1,
        verbose=0,
    )
    logreg_search.fit(X_train, y_train)

    logreg_tuned = logreg_search.best_estimator_
    logreg_tuned_metrics = _evaluate_model(logreg_tuned, X_val, y_val)

    tuned_conf_png = config.conf_matrix_png_prefix.parent / (
        config.conf_matrix_png_prefix.name + "_logreg_tuned.png"
    )
    tuned_conf_info = _plot_and_save_confusion_matrix(
        y_true=y_val,
        y_pred=logreg_tuned.predict(X_val),
        labels=logreg_tuned_metrics["labels"],
        title="LogisticRegression - tuned - confusion matrix",
        png_path=tuned_conf_png,
    )

    results["logistic_regression"] = {
        "baseline": {
            "best_params": None,
            "trainable_model": "LogisticRegression",
            "metrics": logreg_baseline_metrics,
            "confusion_matrix_png": str(conf_png),
            "confusion_matrix": conf_info,
        },
        "tuned": {
            "best_params": {k: (int(v) if isinstance(v, (np.integer,)) else float(v) if isinstance(v, (np.floating,)) else v) for k, v in logreg_search.best_params_.items()},
            "cv_best_score_f1_macro": float(logreg_search.best_score_),
            "metrics": logreg_tuned_metrics,
            "confusion_matrix_png": str(tuned_conf_png),
            "confusion_matrix": tuned_conf_info,
        },
    }

    joblib.dump(logreg_baseline, REPO_DIR / "logreg_baseline_sprint13.joblib")
    joblib.dump(logreg_tuned, REPO_DIR / "logreg_tuned_sprint13.joblib")

    # -------------------- RandomForest --------------------
    rf_baseline = RandomForestClassifier(
        n_estimators=300,
        random_state=config.random_state,
        n_jobs=-1,
    )
    rf_baseline.fit(X_train, y_train)

    rf_baseline_metrics = _evaluate_model(rf_baseline, X_val, y_val)

    rf_conf_png = config.conf_matrix_png_prefix.parent / (
        config.conf_matrix_png_prefix.name + "_randomforest_baseline.png"
    )
    rf_conf_info = _plot_and_save_confusion_matrix(
        y_true=y_val,
        y_pred=rf_baseline.predict(X_val),
        labels=rf_baseline_metrics["labels"],
        title="RandomForestClassifier - baseline - confusion matrix",
        png_path=rf_conf_png,
    )

    rf_pipe = Pipeline(steps=[("model", rf_baseline)])

    rf_param_grid = {
        "model__n_estimators": [400, 600],
        "model__max_depth": [None, 10, 20],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 4],
    }

    rf_search = GridSearchCV(
        estimator=rf_pipe,
        param_grid=rf_param_grid,
        scoring="f1_macro",
        cv=3,
        n_jobs=-1,
        verbose=0,
    )
    rf_search.fit(X_train, y_train)

    rf_tuned = rf_search.best_estimator_
    rf_tuned_metrics = _evaluate_model(rf_tuned, X_val, y_val)

    rf_tuned_conf_png = config.conf_matrix_png_prefix.parent / (
        config.conf_matrix_png_prefix.name + "_randomforest_tuned.png"
    )
    rf_tuned_conf_info = _plot_and_save_confusion_matrix(
        y_true=y_val,
        y_pred=rf_tuned.predict(X_val),
        labels=rf_tuned_metrics["labels"],
        title="RandomForestClassifier - tuned - confusion matrix",
        png_path=rf_tuned_conf_png,
    )

    results["random_forest"] = {
        "baseline": {
            "metrics": rf_baseline_metrics,
            "confusion_matrix_png": str(rf_conf_png),
            "confusion_matrix": rf_conf_info,
        },
        "tuned": {
            "best_params": {k: (int(v) if isinstance(v, (np.integer,)) else v) for k, v in rf_search.best_params_.items()},
            "cv_best_score_f1_macro": float(rf_search.best_score_),
            "metrics": rf_tuned_metrics,
            "confusion_matrix_png": str(rf_tuned_conf_png),
            "confusion_matrix": rf_tuned_conf_info,
        },
    }

    joblib.dump(rf_baseline, REPO_DIR / "rf_baseline_sprint13.joblib")
    joblib.dump(rf_tuned, REPO_DIR / "rf_tuned_sprint13.joblib")

    return results


def _jsonify(obj: Any) -> Any:
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonify(v) for v in obj]
    return obj


def main() -> None:
    config = Config()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPO_DIR.mkdir(parents=True, exist_ok=True)

    X_train, X_val, y_train, y_val = _load_xy(config)

    if len(pd.unique(y_train)) < 2:
        raise ValueError("y_train tiene menos de 2 clases; no se puede evaluar clasificación.")

    report_payload: Dict[str, Any] = {
        "sprint": 13,
        "task": "supervised_model_training",
        "input": {
            "X_train": str(config.X_train_path),
            "X_val": str(config.X_val_path),
            "y_train": str(config.y_train_path),
            "y_val": str(config.y_val_path),
            "n_train": int(len(X_train)),
            "n_val": int(len(X_val)),
            "n_features": int(X_train.shape[1]),
            "y_train_distribution": _jsonify(
                y_train.value_counts(normalize=True).sort_index().to_dict()
            ),
            "y_val_distribution": _jsonify(
                y_val.value_counts(normalize=True).sort_index().to_dict()
            ),
        },
        "models": {},
    }

    models_results = _baseline_and_tuning(X_train, y_train, X_val, y_val, config)
    report_payload["models"] = _jsonify(models_results)

    config.report_path.write_text(
        json.dumps(report_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("[Sprint13] Entrenamiento supervisado completado.")
    print(f"- Report: {config.report_path}")
    print(f"- Repo model outputs in: {REPO_DIR}")


if __name__ == "__main__":
    main()

