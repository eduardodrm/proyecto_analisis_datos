"""API REST local (3er origen) para el pipeline ETL.

E3 requiere al menos 3 fuentes de datos y una de ellas debe ser vía API REST.
Para no depender de servicios externos (reproducibilidad), se define un origen
vía endpoint local.

Este endpoint retorna un payload placeholder (será reemplazado por datos reales
alineados al dataset en sprints siguientes).
"""

from __future__ import annotations

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/v1/source/extra_user_metrics")
def extra_user_metrics():
    """Retorna métricas adicionales por usuario (placeholder)."""
    return jsonify(
        [
            {"user_id": 1, "extra_metric_a": 10.0, "extra_metric_b": 0.25},
            {"user_id": 2, "extra_metric_a": 25.0, "extra_metric_b": 0.10},
            {"user_id": 3, "extra_metric_a": 5.0, "extra_metric_b": 0.40},
        ]
    )


def main() -> None:
    # Puerto fijo en Sprint 1; más adelante se parametriza con variables de entorno.
    app.run(host="0.0.0.0", port=8000, debug=False)


if __name__ == "__main__":
    main()

