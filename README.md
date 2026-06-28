# E3 — Segmentación no supervisada con KMeans (Streaming)

> **Regla de trabajo colaborativo:** el README se actualiza **en tiempo real** reflejando únicamente lo completado hasta el momento de cada commit.

## Objetivo
Construir un pipeline end-to-end para **segmentar usuarios** usando aprendizaje no supervisado con **KMeans**, integrando datos desde múltiples fuentes, dejando un ETL robusto y exponiendo resultados vía **dashboard interactivo** y **API REST**.

## Fuentes de datos (Sprint 1)
El proyecto integra al menos 3 fuentes (mínimo requerido por evaluación):

1. **CSV (consumo)**: `data/usuarios_streaming.csv`
2. **CSV (perfil)**: `data/perfil_usuarios.csv` (se cargará en Postgres en sprints siguientes)
3. **API REST local (3er origen)**: endpoint definido localmente para permitir ETL sin servicios externos

## Arquitectura (ETL → Dataset → Modelo → Dashboard) (Sprint 1)
Se documenta en el archivo:
- `docs/architecture_etl_model_dashboard.md`

## Estado por sprints
### Sprint 1 — Base técnica y arquitectura ETL 
- Diagrama de arquitectura creado.
- Estructura del README alineada al Sprint 1.
- 3er origen definido como **API REST local** (placeholder) para ETL.

**Pendiente en Sprint 1 (no comprometido aún):** implementación completa del ETL end-to-end (extracción/limpieza/transformación/validación/persistencia final en `/data/`).

### Sprint 2 — Exploración, limpieza y preparación del dataset ✅
- ETL mínimo para consolidar los 3 orígenes en `data/dataset_consolidado_sprint2.csv`.
- Dataset de features numéricas aptas para KMeans en `data/features_kmeans_sprint2.csv` (sin NaNs).
- Reporte de limpieza y esquema en `docs/cleaning_report_sprint2.md` y `docs/features_schema_sprint2.md`.
- EDA inicial en `docs/eda_inicial_sprint2.md`.


