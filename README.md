# E3 — Segmentación no supervisada con KMeans (Streaming)

> **Regla de trabajo colaborativo:** el README se actualiza **en tiempo real** reflejando únicamente lo completado hasta el momento de cada commit.

## Objetivo
Construir un pipeline end-to-end para **segmentar usuarios** usando aprendizaje no supervisado con **KMeans**, integrando datos desde múltiples fuentes, dejando un ETL robusto y exponiendo resultados vía **dashboard interactivo** y **API REST**.

## Documentación técnica (guías del repo)
- **Arquitectura (ETL → Dataset → Modelo → Dashboard):** `docs/architecture_etl_model_model_dashboard.md`
- **Contrato de API (resultados):** `docs/api_results_contract.md`
- **Manual de usuario (UI + API):** `docs/manual_usuario.md`
- **Guía de despliegue (local + Docker Compose):** `docs/guia_despliegue.md`
- **Runbook de ejecución / replicabilidad:** `docs/sprint10_runbook.md`

## Fuentes de datos (Sprint 1)
El proyecto integra **solo 2 fuentes**:
1. **CSV (consumo):** `data/usuarios_streaming.csv`
2. **CSV (perfil):** `data/perfil_usuarios.csv`

## Quickstart (local)

### 1) Ejecutar pipeline (ETL → modelo → perfiles)
```bash
python etl/pipeline_sprint2.py
python etl/prepare_features_sprint2.py
python etl/train_kmeans_sprint4.py
python etl/train_kmeans_sprint5.py
python etl/profile_clusters_sprint6.py
```

### 2) Levantar API REST (resultados)
```bash
python api/results_api.py
```
- Puerto: **8000**

### 3) Smoke tests (API)
```bash
curl http://localhost:8000/v1/clusters
curl http://localhost:8000/v1/clusters/0
curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"
```

### 4) Levantar dashboard (Streamlit)
```bash
streamlit run dashboards/streamlit_sprint7_app.py --server.port 8501
```
- Abre: http://localhost:8501

## Evidencia técnica (qué revisar)
- **K óptimo (Sprint 4):**
  - `docs/sprint4_kmeans_metrics.json` (contiene `silhouette_score` por k y `best_k`)
  - `docs/sprint4_elbow.png` (puede no generarse si `matplotlib` no está disponible)
  - `docs/sprint4_kmeans_report.md`
- **Perfiles y segmentos (Sprint 6):**
  - `data/cluster_profile_sprint6.csv`

## Despliegue
Ver `docs/guia_despliegue.md`.

## Estado por sprints

### Sprint 1 — Base técnica y arquitectura ETL
- Diagrama de arquitectura creado.
- Estructura del README alineada al Sprint 1.

**Estado Sprint 1 (parcial):** se implementa el ETL mínimo para consolidar **2 fuentes** en `/data/` (`etl/pipeline_sprint2.py`) y se genera metadata de esquema (`data/dataset_consolidado_sprint2.schema.json`).

### Sprint 2 — Exploración, limpieza y preparación del dataset ✅
- ETL mínimo para consolidar los 3 orígenes en `data/dataset_consolidado_sprint2.csv`.
- Dataset de features numéricas aptas para KMeans en `data/features_kmeans_sprint2.csv` (sin NaNs).
- Reporte de limpieza y esquema en `docs/cleaning_report_sprint2.md` y `docs/features_schema_sprint2.md`.
- EDA inicial en `docs/eda_inicial_sprint2.md`.

### Sprint 3 — Pre-modelado (quality gates + configuración base) ✅
- Quality gates sin entrenamiento: features numéricas y sin NaNs.
- Configuración base KMeans para Sprint 4 en `docs/sprint3_kmeans_base_config.json`.

### Sprint 4 — Entrenamiento KMeans + métricas (Elbow y Silhouette) ✅
- Ejecución KMeans para k en rango 2..10.
- Métricas guardadas en `docs/sprint4_kmeans_metrics.csv` y `docs/sprint4_kmeans_metrics.json`.
- Reporte de resultados en `docs/sprint4_kmeans_report.md`.
- Gráfico Elbow: `docs/sprint4_elbow.png` (puede no generarse si `matplotlib` no está disponible en el entorno).

### Sprint 5 — Entrenamiento final y generación de resultados ✅
- Entrenamiento KMeans con el k seleccionado.
- Persistencia de labels en `data/user_clusters_sprint5.csv`.
- Persistencia de dataset enriquecido con `cluster` en `data/dataset_consolidado_con_cluster_sprint5.csv`.
- Modelo serializado en `repo/kmeans_model_sprint5.joblib`.

### Sprint 6 — Interpretación de segmentos (perfilamiento) ✅
- Perfil numérico por cluster y cálculo de drivers.
- Salida principal: `data/cluster_profile_sprint6.csv`.
- Reporte: `docs/sprint6_cluster_interpretation.md`.

### Sprint 8 — API REST para servir resultados ✅
- Contrato documentado en `docs/api_results_contract.md`.
- API implementada en `api/results_api.py`.

### Sprint 9 — Integración final (ETL + modelo + UI/API) ✅
#### Corrida end-to-end (local)

1) Terminal 1 (pipeline completo):
- `python etl/pipeline_sprint2.py`
- `python etl/prepare_features_sprint2.py`
- `python etl/train_kmeans_sprint4.py`
- `python etl/train_kmeans_sprint5.py`
- `python etl/profile_clusters_sprint6.py`

2) Terminal 2 (API de resultados):
- `python api/results_api.py`

3) Validación (smoke tests):
- `curl http://localhost:8000/v1/clusters`
- `curl http://localhost:8000/v1/clusters/0`
- `curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"`

### Sprint 10 — Entrega, conclusiones y calidad de repositorio ✅
- [x] Preparar notebook/guía o script de ejecución para replicabilidad. (`docs/sprint10_runbook.md`)
- [x] Evidenciar justificación del k óptimo (codo + silhouette). (ver `docs/sprint4_kmeans_report.md` y `docs/sprint4_kmeans_metrics.json`)
- [x] Conclusiones orientadas al contexto de negocio. (`docs/sprint10_conclusiones.md`)
- [x] Revisar estructura del repositorio, tests, y consistencia de documentación. (tests: `pytest`)

