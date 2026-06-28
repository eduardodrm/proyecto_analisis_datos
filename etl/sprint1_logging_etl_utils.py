"""Utilidades de logging y validación para ETL (Sprint 1).

Este módulo agrega:
- logging estructurado por etapas
- validaciones mínimas (no NaNs en columnas clave del consolidado)

Se usa como base para que pipeline_sprint2.py (ETL consolidación) y/o loaders
tengan trazabilidad profesional.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd


@dataclass(frozen=True)
class StageResult:
    stage: str
    ok: bool
    duration_s: float
    extra: Optional[Dict[str, Any]] = None


def setup_logging(level: str = "INFO") -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)

    # Formato simple y legible, compatible con copiar a reportes.
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def _stage_log_payload(run_id: str, stage: str, result: StageResult) -> str:
    payload = {
        "run_id": run_id,
        "stage": result.stage,
        "ok": result.ok,
        "duration_s": result.duration_s,
        "extra": result.extra or {},
    }
    return json.dumps(payload, ensure_ascii=False)


class StageLogger:
    """Logger de etapas con duración y trazabilidad."""

    def __init__(self, run_id: Optional[str] = None) -> None:
        self.run_id = run_id or str(uuid.uuid4())

    def time_stage(self, stage: str):
        return _TimedStageContext(self, stage)


class _TimedStageContext:
    def __init__(self, parent: StageLogger, stage: str) -> None:
        self.parent = parent
        self.stage = stage
        self.t0 = 0.0
        self._extra: Dict[str, Any] = {}

    def __enter__(self):
        self.t0 = time.time()
        return self

    def set_extra(self, **kwargs: Any) -> None:
        self._extra.update(kwargs)

    def __exit__(self, exc_type, exc, tb) -> bool:
        t1 = time.time()
        ok = exc is None
        result = StageResult(
            stage=self.stage,
            ok=ok,
            duration_s=float(t1 - self.t0),
            extra=self._extra,
        )

        msg = _stage_log_payload(self.parent.run_id, self.stage, result)
        if ok:
            logging.info(msg)
        else:
            logging.error(msg)

        # Propagar excepción
        return False


def validate_no_nans(df: pd.DataFrame, required_cols: list[str], context: str) -> None:
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"{context}: faltan columnas requeridas: {missing_cols}")

    nan_total = int(df[required_cols].isna().sum().sum())
    if nan_total != 0:
        nan_by_col = df[required_cols].isna().sum().sort_values(ascending=False).to_dict()
        raise RuntimeError(f"{context}: existen NaNs en columnas clave. nan_total={nan_total}. nan_by_col={nan_by_col}")

