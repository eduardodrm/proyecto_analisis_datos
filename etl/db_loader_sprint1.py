"""Loader Sprint 1 (ETL): persistir el dataset consolidado en Postgres.

Objetivo (Sprint 1): completar la parte de persistencia (loader) hacia una base SQL.

Este script:
- Lee el dataset consolidado desde `data/dataset_consolidado_sprint2.csv`.
- Crea una tabla `streaming_users_consolidado` si no existe.
- Inserta los datos (modo UPSERT opcional según estrategia simple).

Requisitos:
- Postgres accesible desde la máquina donde se ejecuta.

Variables de entorno (opcional, si no se definen se usan defaults del enunciado):
- DB_HOST (default: localhost)
- DB_PORT (default: 5432)
- DB_USER (default: admin)
- DB_PASSWORD (default: admin)
- DB_NAME (default: db_streaming)

Ejecución:
  python etl/db_loader_sprint1.py

"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError as e:  # pragma: no cover
    raise RuntimeError(
        "Falta dependencia psycopg2. Agrega 'psycopg2-binary' a requirements.txt"
    ) from e


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class DBConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    user: str = os.getenv("DB_USER", "admin")
    password: str = os.getenv("DB_PASSWORD", "admin")
    name: str = os.getenv("DB_NAME", "db_streaming")


TABLE_NAME = "streaming_users_consolidado"


def _infer_sql_type(dtype: str) -> str:
    # Dtype proviene de pandas (string como 'int64', 'float64', etc.)
    if dtype.startswith("int"):
        return "BIGINT"
    if dtype.startswith("float"):
        return "DOUBLE PRECISION"
    # Fallback
    return "DOUBLE PRECISION"


def _build_create_table_sql(df: pd.DataFrame) -> Tuple[str, Dict[str, str]]:
    # Primera columna esperada: user_id
    # Generamos columnas según tipos inferidos.
    col_types: Dict[str, str] = {c: _infer_sql_type(str(df[c].dtype)) for c in df.columns}

    cols_sql = ",\n  ".join([f"{c} {t}" for c, t in col_types.items()])
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      {cols_sql},
      PRIMARY KEY (user_id)
    );
    """
    return create_sql, col_types


def _insert_rows(conn, df: pd.DataFrame) -> None:
    cols = df.columns.tolist()
    values = df.to_records(index=False)

    # UPSERT simple (Postgres 15+): ON CONFLICT con PK user_id
    # Si PK existe, actualiza el resto de columnas.
    update_cols = [c for c in cols if c != "user_id"]
    set_sql = ", ".join([f"{c}=EXCLUDED.{c}" for c in update_cols])

    insert_sql = f"""
    INSERT INTO {TABLE_NAME} ({', '.join(cols)})
    VALUES %s
    ON CONFLICT (user_id) DO UPDATE SET {set_sql};
    """ 

    data_list = [tuple(getattr(r, c) for c in cols) for r in values]
    with conn.cursor() as cur:
        execute_values(cur, insert_sql, data_list, page_size=500)


def main() -> None:
    cfg = DBConfig()

    consolidated_csv = DATA_DIR / "dataset_consolidado_sprint2.csv"
    if not consolidated_csv.exists():
        raise FileNotFoundError(f"No existe: {consolidated_csv}")

    df = pd.read_csv(consolidated_csv)

    if "user_id" not in df.columns:
        raise ValueError("El dataset consolidado debe contener la columna 'user_id'.")

    # Convertir user_id a int
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    if df["user_id"].isna().any():
        raise ValueError("user_id contiene valores no convertibles (NaN).")
    df["user_id"] = df["user_id"].astype("int64")

    create_sql, _ = _build_create_table_sql(df)

    conn = psycopg2.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        dbname=cfg.name,
    )

    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(create_sql)
            conn.commit()

        _insert_rows(conn, df)
        conn.commit()

        print(f"OK - Loader persistió {len(df)} filas en Postgres: {cfg.name}.{TABLE_NAME}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

