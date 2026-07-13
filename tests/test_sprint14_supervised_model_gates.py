import json
from pathlib import Path


def test_sprint13_report_exists_and_quality_gates() -> None:
    report_path = Path(__file__).resolve().parents[1] / "docs" / "sprint13_supervised_train_report.json"
    assert report_path.exists(), f"No existe: {report_path}"

    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data.get("sprint") == 13

    models = data.get("models", {})
    assert "logistic_regression" in models
    assert "random_forest" in models

    # Gate mínimo razonable: f1_macro > 0.2 (ajustable si deseas)
    for model_key in ["logistic_regression", "random_forest"]:
        for split_key in ["baseline", "tuned"]:
            metrics = models[model_key][split_key]["metrics"]
            f1_macro = metrics["f1_macro"]
            assert isinstance(f1_macro, (int, float))
            assert f1_macro > 0.2, (
                f"f1_macro demasiado bajo: model={model_key} split={split_key} f1_macro={f1_macro}"
            )

    # Validar matriz de confusión serializable
    # Estructura esperada (por el reporte de Sprint 13):
    # - en baseline/tuned puede venir como dict{labels, confusion_matrix} o como list[list[int]]
    for model_key in ["logistic_regression", "random_forest"]:
        for split_key in ["baseline", "tuned"]:
            cm_obj = models[model_key][split_key]["confusion_matrix"]

            if isinstance(cm_obj, dict):
                cm = cm_obj.get("confusion_matrix")
            else:
                cm = cm_obj

            assert isinstance(cm, list)
            assert all(isinstance(row, list) for row in cm)


