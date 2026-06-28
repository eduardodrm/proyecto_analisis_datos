# Loader Postgres — Sprint 1 (Persistencia del dataset)

## Objetivo
Persistir el dataset consolidado de `/data/` en una base **Postgres** para completar el flujo ETL end-to-end (Sprint 1).

## Dataset de entrada
- Archivo: `data/dataset_consolidado_sprint2.csv`
- Tabla objetivo: `streaming_users_consolidado`
- Primary key: `user_id`

## Script
- `etl/db_loader_sprint1.py`

## Configuración (variables de entorno)
Si no se define nada, usa los defaults acordados:
- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `5432`)
- `DB_USER` (default: `admin`)
- `DB_PASSWORD` (default: `admin`)
- `DB_NAME` (default: `db_streaming`)

Ejemplo (Windows):
- `set DB_HOST=localhost`
- `set DB_PORT=5432`
- `set DB_USER=admin`
- `set DB_PASSWORD=admin`
- `set DB_NAME=db_streaming`

## Ejecución
```bash
python etl/db_loader_sprint1.py
```

## Comportamiento
- Crea la tabla si no existe.
- Inserta/actualiza usando `ON CONFLICT (user_id) DO UPDATE`.

## Errores comunes
- No tener Postgres accesible/levantado.
- Credenciales incorrectas.
- Dataset sin columna `user_id`.

