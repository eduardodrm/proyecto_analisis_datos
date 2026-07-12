"""API REST para servir resultados (Sprint 8).

Endpoints:
- GET /v1/clusters
- GET /v1/clusters/<cluster_id>
- GET /v1/metrics?cluster_id=...&stat=mean|median
- GET /v1/dashboard


Fuente principal de métricas:
- data/cluster_profile_sprint6.csv

Conteos/porcentajes:
- data/user_clusters_sprint5.csv (fallback)
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd
from flask import Flask, jsonify, request



PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

CLUSTER_PROFILE_PATH = DATA_DIR / "cluster_profile_sprint6.csv"
USER_CLUSTERS_PATH = DATA_DIR / "user_clusters_sprint5.csv"

DEFAULT_PORT = 8000

Stat = Literal["mean", "median"]


def _to_int_if_possible(x: Any) -> Any:
    try:
        # handles numpy ints too
        return int(x)
    except Exception:
        return x


@dataclass
class ErrorResponse:
    error: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"error": self.error}
        if self.details:
            out["details"] = self.details
        return out


class ResultsStore:
    def __init__(self) -> None:
        self._cluster_profile_df: pd.DataFrame | None = None
        self._user_clusters_df: pd.DataFrame | None = None

    def load_cluster_profile(self) -> pd.DataFrame:
        if self._cluster_profile_df is None:
            if not CLUSTER_PROFILE_PATH.exists():
                raise FileNotFoundError(f"No existe: {CLUSTER_PROFILE_PATH}")
            self._cluster_profile_df = pd.read_csv(CLUSTER_PROFILE_PATH)
        return self._cluster_profile_df

    def load_user_clusters(self) -> pd.DataFrame:
        if self._user_clusters_df is None:
            if not USER_CLUSTERS_PATH.exists():
                raise FileNotFoundError(f"No existe: {USER_CLUSTERS_PATH}")
            self._user_clusters_df = pd.read_csv(USER_CLUSTERS_PATH)
        return self._user_clusters_df

    def get_clusters_summary(self) -> list[dict[str, Any]]:
        df = self.load_cluster_profile()

        if "cluster" not in df.columns:
            raise ValueError("cluster_profile_sprint6.csv debe incluir columna 'cluster'")

        # cluster_size/cluster_pct pueden existir en cluster_profile
        has_size = "cluster_size" in df.columns
        has_pct = "cluster_pct" in df.columns

        if has_size and has_pct:
            sub = df[["cluster", "cluster_size", "cluster_pct"]].copy()
            sub["cluster"] = sub["cluster"].apply(_to_int_if_possible)
            sub["cluster_size"] = sub["cluster_size"].astype(int)
            # cluster_pct: float
            sub = sub.sort_values("cluster")
            return sub.to_dict(orient="records")

        # fallback: calcular from user_clusters
        users = self.load_user_clusters()
        if "cluster" not in users.columns:
            raise ValueError("user_clusters_sprint5.csv debe incluir columna 'cluster'")
        if "user_id" not in users.columns:
            raise ValueError("user_clusters_sprint5.csv debe incluir columna 'user_id'")

        total = len(users)
        grp = users.groupby("cluster").agg(cluster_size=("user_id", "count")).reset_index()
        grp["cluster_pct"] = (grp["cluster_size"] / total * 100.0).round(6)
        grp["cluster"] = grp["cluster"].apply(_to_int_if_possible)
        grp = grp.sort_values("cluster")
        return grp.to_dict(orient="records")

    def get_cluster_profile(self, cluster_id: int) -> dict[str, Any]:
        df = self.load_cluster_profile()
        if "cluster" not in df.columns:
            raise ValueError("cluster_profile_sprint6.csv debe incluir columna 'cluster'")

        # cluster_id puede venir como int/string
        rows = df[df["cluster"] == cluster_id]
        if rows.empty:
            raise KeyError(f"cluster_id={cluster_id}")

        row = rows.iloc[0].to_dict()
        # normalizar tipos básicos
        if "cluster" in row:
            row["cluster"] = _to_int_if_possible(row["cluster"])
        for k, v in list(row.items()):
            # convert numpy scalar to python
            if hasattr(v, "item"):
                try:
                    row[k] = v.item()
                except Exception:
                    pass
        return row

    def get_metrics_by_stat(self, cluster_id: int, stat: Stat) -> dict[str, Any]:
        profile = self.get_cluster_profile(cluster_id)

        # filtra columnas tipo: <feature>_<stat>
        suffix = f"_{stat}"
        metrics: dict[str, Any] = {}
        for k, v in profile.items():
            if k == "cluster":
                continue
            if k.endswith(suffix):
                base = k[: -len(suffix)]
                metrics[base] = v

        return {
            "cluster": profile.get("cluster", cluster_id),
            "stat": stat,
            "metrics": metrics,
        }


def create_app() -> Flask:
    app = Flask(__name__)
    store = ResultsStore()

    @app.errorhandler(400)
    def bad_request(e: Exception):
        return jsonify(ErrorResponse(error="bad_request").to_dict()), 400

    @app.errorhandler(404)
    def not_found(e: Exception):
        return jsonify(ErrorResponse(error="not_found").to_dict()), 404

    @app.get("/v1/clusters")
    def list_clusters():
        clusters = store.get_clusters_summary()
        return jsonify(clusters)

    @app.get("/v1/clusters/<cluster_id>")
    def cluster_by_id(cluster_id: str):
        try:
            cid = int(cluster_id)
        except ValueError:
            return (
                jsonify(
                    ErrorResponse(
                        error="invalid_cluster_id",
                        details={"cluster_id": cluster_id},
                    ).to_dict()
                ),
                400,
            )

        try:
            profile = store.get_cluster_profile(cid)
            return jsonify(profile)
        except KeyError:
            return (
                jsonify(
                    ErrorResponse(
                        error="cluster_not_found",
                        details={"cluster_id": cid},
                    ).to_dict()
                ),
                404,
            )

    @app.get("/v1/source/extra_user_metrics")
    def extra_user_metrics():
        """Origen 3 (placeholder) para el ETL Sprint 2.

        Contrato esperado por ETL:
        - Retorna una lista JSON de objetos con:
          - user_id (int)
          - extra_metric_a (number)
          - extra_metric_b (number)
        """

        return jsonify(
            [
                {"user_id": 1, "extra_metric_a": 10.0, "extra_metric_b": 0.25},
                {"user_id": 2, "extra_metric_a": 25.0, "extra_metric_b": 0.10},
                {"user_id": 3, "extra_metric_a": 5.0, "extra_metric_b": 0.40},
            ]
        )

    @app.get("/v1/dashboard")
    @app.get("/v1/dashboard/")
    def dashboard():
        """Ruta de UI para explorar los resultados (Streamlit).

        Redirige a la UI Streamlit en http://localhost:8501.
        """
        return ("", 302, {"Location": "http://localhost:8501"})




    @app.get("/v1/metrics")
    def metrics():

        cluster_id = request.args.get("cluster_id", type=str)
        stat = request.args.get("stat", default="mean", type=str)

        if cluster_id is None:
            return (
                jsonify(
                    ErrorResponse(
                        error="missing_parameter",
                        details={"parameter": "cluster_id"},
                    ).to_dict()
                ),
                400,
            )

        try:
            cid = int(cluster_id)
        except ValueError:
            return (
                jsonify(
                    ErrorResponse(
                        error="invalid_cluster_id",
                        details={"cluster_id": cluster_id},
                    ).to_dict()
                ),
                400,
            )

        if stat not in ("mean", "median"):
            return (
                jsonify(
                    ErrorResponse(
                        error="invalid_stat",
                        details={"stat": stat, "allowed": ["mean", "median"]},
                    ).to_dict()
                ),
                400,
            )

        try:
            payload = store.get_metrics_by_stat(cid, stat=stat)  # type: ignore[arg-type]
            return jsonify(payload)
        except KeyError:
            return (
                jsonify(
                    ErrorResponse(
                        error="cluster_not_found",
                        details={"cluster_id": cid},
                    ).to_dict()
                ),
                404,
            )

    return app


def main() -> None:
    app = create_app()
    # Puerto específico para API de resultados (no choca con local_source.py en 8000)
    app.run(host="0.0.0.0", port=DEFAULT_PORT, debug=False)


if __name__ == "__main__":
    main()

