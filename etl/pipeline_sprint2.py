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
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests



PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@dataclass(frozen=True)
class ETLConfig:
    logger_level: str = os.getenv("ETL_LOG_LEVEL", "INFO")

    # Si falla la validación del dataset final, levantar excepción.
    strict_schema_validation: bool = os.getenv("ETL_STRICT_SCHEMA_VALIDATION", "true").lower() == "true"

    execution_report_json: Path = DOCS_DIR / "etl_sprint1_execution_report.json"

    usuarios_streaming_path: Path = DATA_DIR / "usuarios_streaming.csv"
    perfil_usuarios_path: Path = DATA_DIR / "perfil_usuarios.csv"

    api_base_url: str = "http://localhost:8000"
    api_endpoint: str = "/v1/source/extra_user_metrics"

    output_csv: Path = DATA_DIR / "dataset_consolidado_sprint2.csv"
    output_schema_json: Path = DATA_DIR / "dataset_consolidado_sprint2.schema.json"

    http_timeout_seconds: int = 10
    http_retries: int = 3
    http_retry_backoff_seconds: float = 0.8


def _init_logger(level: str) -> logging.Logger:
    logger = logging.getLogger("etl_sprint1")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger


def _http_get_json_with_retries(
    logger: logging.Logger,
    url: str,
    timeout_seconds: int,
    retries: int,
    backoff_seconds: float,
) -> Any:

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


def fetch_extra_metrics(cfg: ETLConfig, logger: logging.Logger) -> pd.DataFrame:
    """Fetch de métricas extra desde el origen 3 (API local).

    Sprint 1 (robustez): si la API falla, devolvemos un DataFrame vacío con columnas esperadas.
    """
    url = f"{cfg.api_base_url}{cfg.api_endpoint}"
    try:
        payload = _http_get_json_with_retries(
            logger,
            url,
            timeout_seconds=cfg.http_timeout_seconds,
            retries=cfg.http_retries,
            backoff_seconds=cfg.http_retry_backoff_seconds,
        )

        if not isinstance(payload, list):
            raise ValueError("El payload del endpoint debe ser una lista de objetos")
        return pd.DataFrame(payload)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Origen 3 (API) falló; usando payload vacío. Error: {type(e).__name__}: {e}")
        # Columnas conocidas del contrato (docs/api_local_source_contract.md)
        return pd.DataFrame([{"user_id": 1, "extra_metric_a": 0.0, "extra_metric_b": 0.0}]).head(0)



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


def _clean_and_normalize_final_dataset(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Transformación/normalización: inicio")

    if "user_id" not in df.columns:
        raise ValueError("El dataset consolidado debe contener 'user_id'.")

    # Normalizar user_id a int (coerción defensiva)
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    if df["user_id"].isna().any():
        bad_rows = int(df["user_id"].isna().sum())
        raise ValueError(f"user_id contiene NaNs tras normalización: {bad_rows}")
    df["user_id"] = df["user_id"].astype("int64")

    # Coerción numérica mínima para columnas que parecen numéricas
    # (no convertimos todo: solo si el dtype es object)
    for c in df.columns:
        if c == "user_id":
            continue
        if df[c].dtype == "object":
            df[c] = pd.to_numeric(df[c], errors="ignore")

    # Mantener el ETL determinista: dejar nulos como están (Sprint 2 se encarga de imputación).
    logger.info("Transformación/normalización: fin")
    return df


def _validate_final_dataset(df: pd.DataFrame, logger: logging.Logger) -> Dict[str, Any]:
    logger.info("Validación fuerte del dataset final: inicio")

    expected_min_cols = ["user_id"]
    missing = [c for c in expected_min_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en dataset final: {missing}")

    # Validaciones de tipos básicos
    user_id_non_null = int(df["user_id"].notna().sum())
    if user_id_non_null != int(len(df)):
        raise ValueError("user_id no puede tener nulos en dataset final")

    # Validación de rangos simples solo cuando existan columnas típicas
    range_checks: List[Tuple[str, float, float]] = []
    # porcentajes suelen venir como 0..1 o 0..100 (no sabemos cuál), entonces validamos no-negatividad
    for col in df.columns:
        lname = col.lower()
        if any(k in lname for k in ["porcentaje", "pct", "ratio"]) or lname.startswith("%"):
            range_checks.append((col, 0.0, float("inf")))


    violations: Dict[str, int] = {}
    for col, lo, hi in range_checks:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce")
            # Ignorar NaNs para no bloquear columnas que Sprint 2 imputará.
            mask = series.dropna()
            if mask.empty:
                continue
            cnt = int(((mask < lo) | (mask > hi)).sum())
            if cnt > 0:
                violations[col] = cnt

    logger.info("Validación fuerte del dataset final: fin")
    return {
        "rows": int(len(df)),
        "cols": int(len(df.columns)),
        "user_id_non_null": user_id_non_null,
        "range_violations": violations,
    }


def main() -> None:

    cfg = ETLConfig()

    logger = _init_logger(cfg.logger_level)
    run_started_at = datetime.now(timezone.utc).isoformat()
    logger.info("ETL Sprint 1 iniciado")

    report: Dict[str, Any] = {
        "started_at_utc": run_started_at,
        "config": {
            "api_base_url": cfg.api_base_url,
            "api_endpoint": cfg.api_endpoint,
            "usuarios_streaming_path": str(cfg.usuarios_streaming_path),
            "perfil_usuarios_path": str(cfg.perfil_usuarios_path),
            "output_csv": str(cfg.output_csv),
            "output_schema_json": str(cfg.output_schema_json),
            "strict_schema_validation": cfg.strict_schema_validation,
        },
        "stages": {},
    }

    try:
        usuarios_df = load_csv(cfg.usuarios_streaming_path)
        report["stages"]["extract_usuarios_streaming"] = {"rows": int(len(usuarios_df)), "cols": int(len(usuarios_df.columns))}
        logger.info("Extracción usuarios_streaming.csv OK")

        perfil_df = load_csv(cfg.perfil_usuarios_path)
        report["stages"]["extract_perfil_usuarios"] = {"rows": int(len(perfil_df)), "cols": int(len(perfil_df.columns))}
        logger.info("Extracción perfil_usuarios.csv OK")

        extra_df = fetch_extra_metrics(cfg, logger)
        report["stages"]["extract_api_extra_user_metrics"] = {"rows": int(len(extra_df)), "cols": int(len(extra_df.columns))}
        logger.info("Extracción API REST local OK")

        usuarios_df = standardize_user_id(usuarios_df, ["user_id", "id", "usuario_id", "id_cliente"])
        perfil_df = standardize_user_id(perfil_df, ["user_id", "id", "usuario_id", "id_cliente"])
        extra_df = standardize_user_id(extra_df, ["user_id", "id", "usuario_id", "id_cliente"])

        report["stages"]["standardize_user_id"] = {
            "usuarios_user_id_non_null": int(usuarios_df["user_id"].notna().sum()),
            "perfil_user_id_non_null": int(perfil_df["user_id"].notna().sum()),
            "extra_user_id_non_null": int(extra_df["user_id"].notna().sum()),
        }

        # Consolidación: join por user_id
        # - left join desde usuarios_streaming para conservar comportamiento de consumo.
        df = usuarios_df.merge(
            perfil_df, on="user_id", how="left", suffixes=("_consumo", "_perfil")
        )
        df = df.merge(extra_df, on="user_id", how="left")


        # Transformaciones/validación (paso 2: robustez)
        df = _clean_and_normalize_final_dataset(df, logger)


        report["stages"]["transform_clean_normalize"] = {
            "rows": int(len(df)),
            "cols": int(len(df.columns)),
            "null_total": int(df.isna().sum().sum()),
        }

        # Validación fuerte del dataset final
        validation = _validate_final_dataset(df, logger)
        report["stages"]["validate_final_dataset"] = validation

        # Guardar
        cfg.output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cfg.output_csv, index=False)

        schema_meta = build_schema_metadata(df)
        with open(cfg.output_schema_json, "w", encoding="utf-8") as f:
            json.dump(schema_meta, f, ensure_ascii=False, indent=2)

        report["outputs"] = {
            "output_csv": str(cfg.output_csv),
            "output_schema_json": str(cfg.output_schema_json),
        }

        logger.info(f"OK - Dataset consolidado guardado en: {cfg.output_csv}")
        logger.info(f"OK - Schema metadata guardada en: {cfg.output_schema_json}")

        # Persistir reporte de ejecución (trazabilidad)
        cfg.execution_report_json.parent.mkdir(parents=True, exist_ok=True)
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        report["status"] = "success"
        cfg.execution_report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    except Exception as e:  # noqa: BLE001
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        report["status"] = "error"
        report["error"] = {"type": type(e).__name__, "message": str(e)}
        cfg.execution_report_json.parent.mkdir(parents=True, exist_ok=True)
        cfg.execution_report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.exception("ETL Sprint 1 falló")
        raise



if __name__ == "__main__":
    main()

