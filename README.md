# E3 — Segmentación no supervisada con KMeans (Streaming)

> **Objetivo del proyecto:** construir un pipeline end-to-end para segmentar usuarios mediante **KMeans**, integrando datos desde fuentes definidas, generando artefactos reproducibles y sirviendo resultados vía **dashboard (Streamlit)** y **API REST**.

Toda la documentación consolidada de este proyecto se encuentra en: `docs/DOCUMENTACION.md`.

---

## 1) Resumen técnico
- **Entrada (datasets):**
  - `data/usuarios_streaming.csv`
  - `data/perfil_usuarios.csv`
- **Modelo:** clustering **KMeans** sobre features numéricas.
- **Artefactos principales (outputs):**
  - `data/user_clusters_sprint5.csv` (usuario → cluster)
  - `data/dataset_consolidado_con_cluster_sprint5.csv` (dataset enriquecido)
  - `data/cluster_profile_sprint6.csv` (perfil estadístico por cluster)
  - `repo/kmeans_model_sprint5.joblib` (modelo serializado)
- **Servicios para consumir resultados:**
  - **Dashboard:** `dashboards/streamlit_sprint7_app.py`
  - **API REST:** `api/results_api.py`

---

## 2) Documentación técnica del repositorio
- **Arquitectura (ETL → Dataset → Modelo → Dashboard):** `docs/architecture_etl_model_dashboard.md`
- **Contratos de API:**
  - Resultados (clusters/métricas): `docs/api_results_contract.md`

  - Supervisado (si aplica): `docs/api_supervised_results_contract.md`
- **Manual de usuario (UI + API):** `docs/manual_usuario.md`
- **Guía de despliegue (local + Docker Compose):** `docs/guia_despliegue.md`
- **Runbook / reproducibilidad:** `docs/sprint10_runbook.md`

---

## 3) Quickstart (local)

### 3.1 Prerrequisitos
- Python 3.x
- Dependencias: `pip install -r requirements.txt`

### 3.2 Ejecutar pipeline completo (ETL → modelo → perfiles)
```bash
python etl/pipeline_sprint2.py
python etl/prepare_features_sprint2.py
python etl/train_kmeans_sprint4.py
python etl/train_kmeans_sprint5.py
python etl/profile_clusters_sprint6.py
```

> Si ya existen los artefactos en `data/` y `repo/`, puedes omitir pasos y avanzar a la sección 3.3.

### 3.3 Levantar API REST
```bash
python api/results_api.py
```
- Base URL: `http://localhost:8000`

### 3.4 Validación rápida (smoke tests)
```bash
curl http://localhost:8000/v1/clusters
curl http://localhost:8000/v1/clusters/0
curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"
```

> Nota: el dashboard consume `data/dataset_consolidado_con_cluster_sprint5.csv` y `data/cluster_profile_sprint6.csv`.


### 3.5 Levantar dashboard Streamlit
```bash
streamlit run dashboards/streamlit_sprint7_app.py --server.port 8501
```
- Abre: http://localhost:8501

---

## 4) Evidencia del entrenamiento (KMeans + supervisado)

### 4.1 K óptimo (KMeans)
- `docs/sprint4_kmeans_metrics.json` / `docs/sprint4_kmeans_metrics.csv`
- `docs/sprint4_kmeans_report.md`
- `docs/sprint4_elbow.png` (si se generó)

### 4.2 Interpretación de segmentos
- `docs/sprint6_cluster_interpretation.md`
- `data/cluster_profile_sprint6.csv`

### 4.3 Supervisado (predicción del cluster) — Sprint 12/13
- Dataset supervisado: `etl/supervised_dataset_sprint12.py` y reportes en `docs/`
- Artefactos de modelos en `repo/`:
  - `repo/logreg_baseline_sprint13.joblib`
  - `repo/logreg_tuned_sprint13.joblib`
  - `repo/rf_baseline_sprint13.joblib`
  - `repo/rf_tuned_sprint13.joblib`

---

## 5) Despliegue
Ver: **`docs/guia_despliegue.md`**

Incluye:
- Ejecución local (sin Docker)
- Ejecución con **Docker Compose** (API REST)

---

## 6) Estructura del repositorio (alto nivel)
- `etl/`: pipelines de preparación, entrenamiento y perfiles.
- `data/`: datasets consolidados y outputs listos para consumo.
- `repo/`: artefactos de modelos serializados.
- `docs/`: arquitectura, reportes, contratos y runbook.
- `api/`: servicios REST.
- `dashboards/`: UI interactiva.
- `tests/`: quality gates y checks de outputs.

---

## 7) Estado / cobertura por fases
Este proyecto se encuentra documentado por fases; el detalle está en `docs/` y el runbook en `docs/sprint10_runbook.md`.

