"""ETL mínimo para habilitar Sprint 2.

Objetivo:
- Consolidar 3 fuentes en un dataset único apto para EDA/cleaning/features.

Fuentes:
- data/usuarios_streaming.csv
- data/perfil_usuarios.csv
- API REST local: GET /v1/source/extra_user_metrics (ver api/local_source.py)

Notas:
- Este script está diseñado para ejecutarse localmente y ser reproducible.
- No entrena modelos: solo prepara un dataset consolidado.

Uso:
  python etl/pipeline_sprint2.py

Salida:
- data/dataset_consolidado_sprint2.csv
- data/dataset_consolidado_sprint2.schema.json (solo metadatos)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class ETLConfig:
    usuarios_streaming_path: Path = DATA_DIR / "usuarios_streaming.csv"
    perfil_usuarios_path: Path = DATA_DIR / "perfil_usuarios.csv"

    api_base_url: str = "http://localhost:8000"
    api_endpoint: str = "/v1/source/extra_user_metrics"

    output_csv: Path = DATA_DIR / "dataset_consolidado_sprint2.csv"
    output_schema_json: Path = DATA_DIR / "dataset_consolidado_sprint2.schema.json"

    http_timeout_seconds: int = 10
    http_retries: int = 3
    http_retry_backoff_seconds: float = 0.8


def _http_get_json_with_retries(url: str, timeout_seconds: int, retries: int, backoff_seconds: float) -> Any:
    last_exc: Optional[Exception] = None
    for i in range(retries):
        try:
            resp = requests.get(url, timeout=timeout_seconds)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if i < retries - 1:
                time.sleep(backoff_seconds * (2**i))
    assert last_exc is not None
    raise last_exc


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo requerido: {path}")
    return pd.read_csv(path)


def fetch_extra_metrics(cfg: ETLConfig) -> pd.DataFrame:
    url = f"{cfg.api_base_url}{cfg.api_endpoint}"
    payload = _http_get_json_with_retries(
        url,
        timeout_seconds=cfg.http_timeout_seconds,
        retries=cfg.http_retries,
        backoff_seconds=cfg.http_retry_backoff_seconds,
    )

    if not isinstance(payload, list):
        raise ValueError("El payload del endpoint debe ser una lista de objetos")
    return pd.DataFrame(payload)


def standardize_user_id(df: pd.DataFrame, user_id_col_candidates: List[str]) -> pd.DataFrame:
    for col in user_id_col_candidates:
        if col in df.columns:
            if col != "user_id":
                df = df.rename(columns={col: "user_id"})
            break
    if "user_id" not in df.columns:
        raise ValueError(f"No se encontró una columna de identificador de usuario en: {df.columns.tolist()}")
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    return df


def build_schema_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    def col_meta(s: pd.Series) -> Dict[str, Any]:
        return {
            "dtype": str(s.dtype),
            "non_null": int(s.notna().sum()),
            "null": int(s.isna().sum()),
            "min": None if s.dropna().empty else float(s.min()),
            "max": None if s.dropna().empty else float(s.max()),
        }

    return {
        "row_count": int(len(df)),
        "columns": {c: col_meta(df[c]) for c in df.columns},
    }


def main() -> None:
    cfg = ETLConfig()

    usuarios_df = load_csv(cfg.usuarios_streaming_path)
    perfil_df = load_csv(cfg.perfil_usuarios_path)
    extra_df = fetch_extra_metrics(cfg)

    # Estandarizar user_id (posibles nombres según dataset)
    usuarios_df = standardize_user_id(usuarios_df, ["user_id", "id", "usuario_id", "id_cliente"])
    perfil_df = standardize_user_id(perfil_df, ["user_id", "id", "usuario_id", "id_cliente"])
    extra_df = standardize_user_id(extra_df, ["user_id", "id", "usuario_id", "id_cliente"])


    # Consolidación: join por user_id
    # - left join desde usuarios_streaming para conservar comportamiento de consumo.
    df = usuarios_df.merge(perfil_df, on="user_id", how="left", suffixes=("_consumo", "_perfil"))
    df = df.merge(extra_df, on="user_id", how="left")

    # Guardar
    cfg.output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cfg.output_csv, index=False)

    schema_meta = build_schema_metadata(df)
    with open(cfg.output_schema_json, "w", encoding="utf-8") as f:
        json.dump(schema_meta, f, ensure_ascii=False, indent=2)

    print(f"OK - Dataset consolidado guardado en: {cfg.output_csv}")
    print(f"OK - Schema metadata guardada en: {cfg.output_schema_json}")


if __name__ == "__main__":
    main()

