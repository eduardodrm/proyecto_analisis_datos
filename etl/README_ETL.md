# ETL — Sprint 1 (esqueleto)

Este documento describe el objetivo y la intención del pipeline ETL para E3 (segmentación no supervisada con KMeans).

## Fuentes (mínimo 3)
1. `data/usuarios_streaming.csv` (CSV)
2. `data/perfil_usuarios.csv` (CSV; carga a Postgres en sprints siguientes)
3. **API REST local** (3er origen para cumplir el requisito del enunciado)

## Objetivo del dataset consolidado
- Construir un dataset final persistido en `/data/`.
- Asegurar que el dataset final sea apto para KMeans: solo variables numéricas, sin NaNs según estrategia y con esquema validado.

## Estructura sugerida de módulos
- `etl/pipeline.py`: orquestación, ejecución y manejo de errores.
- `etl/extractors.py`: extractores por fuente.
- `etl/transform.py`: limpieza + normalización.
- `etl/schemas.py`: validación de esquema.
- `etl/loader.py`: persistencia.
- `etl/config.py`: configuración via variables de entorno.

> En Sprint 1 se deja la base documentada; la implementación completa del ETL end-to-end se completará en sprints posteriores.

