# DOCUMENTACIÓN CONSOLIDADA — E3 (KMeans + Dashboard + API + Supervisado)

> Archivo único de documentación técnica/operativa. Sustituye la necesidad de navegar múltiples `docs/*.md`.

---

## 1) Resumen ejecutivo
Este proyecto construye un pipeline end-to-end para segmentar usuarios mediante **KMeans** (aprendizaje no supervisado). A partir de datasets CSV, el pipeline:
1. realiza **ETL** y prepara un dataset listo para clustering,
2. entrena **KMeans** (selección de `k` con métricas como Silhouette/Elbow),
3. calcula un **perfil por cluster** (métricas y estadísticos),
4. expone los resultados mediante:
   - **Dashboard** interactivo (Streamlit)
   - **API REST** (resultados clustering)
5. entrena modelos **supervisados** para predecir el cluster (predicción del segmento), generando métricas y artefactos.

Los artefactos principales quedan en `data/` y `repo/`, y la información se consume desde `dashboards/` y `api/`.

---

## 2) Fuentes de datos e inputs
- **`data/usuarios_streaming.csv`**: dataset de consumo.
- **`data/perfil_usuarios.csv`**: dataset de perfil.

> El pipeline consolida estas fuentes y genera datasets listos para modelado.

---

## 3) Arquitectura del sistema (vista técnica)

### Flujo ETL → Dataset → Modelo → Exposición
- ETL (limpieza + validación de esquema) consolida datasets en `data/`.
- KMeans entrena con features numéricas y produce:
  - labels por usuario
  - métricas de selección de `k`
- Perfilamiento agrega/deriva métricas por cluster.
- Exposición:
  - Streamlit consume datasets de `data/`
  - API REST consulta los mismos artefactos.

(La representación visual tipo Mermaid ya existía en `docs/architecture_etl_model_dashboard.md`; este archivo consolida el contenido operativo.)

---

## 4) Componentes del proyecto (qué hace cada carpeta)
- `etl/`
  - Pipelines de ingestión/transformación.
  - Entrenamiento de KMeans y perfilamiento.
  - Dataset y entrenamiento supervisado.
- `data/`
  - datasets consolidados, features, labels, y perfil por cluster.
- `repo/`
  - artefactos serializados (KMeans y modelos supervisados).
- `docs/`
  - reportes/artefactos de evidencia y contratos de API (referenciados dentro de este documento).
- `api/`
  - servicio REST para exponer resultados (clustering y modelos supervisados si aplica).
- `dashboards/`
  - UI interactiva (Streamlit).
- `tests/`
  - quality gates y checks de outputs.

---

## 5) Artefactos de salida (qué deberías ver)
### 5.1 KMeans / segmentación
- Dataset consolidado enriquecido con cluster:
  - `data/dataset_consolidado_con_cluster_sprint5.csv`
- Labels por usuario:
  - `data/user_clusters_sprint5.csv`
- Perfil por cluster:
  - `data/cluster_profile_sprint6.csv`
- Modelo KMeans:
  - `repo/kmeans_model_sprint5.joblib`
- Evidencia `k` óptimo:
  - `docs/sprint4_kmeans_metrics.json`
  - `docs/sprint4_kmeans_metrics.csv`
  - `docs/sprint4_elbow.png` (si se generó)
  - `docs/sprint4_kmeans_report.md`

### 5.2 Supervisado (predicción del cluster)
- Reporte de entrenamiento supervisado:
  - `docs/sprint13_supervised_train_report.json`
- Contrato de API supervisada (si se expone):
  - `docs/api_supervised_results_contract.md`
- Modelos serializados:
  - `repo/logreg_baseline_sprint13.joblib`
  - `repo/logreg_tuned_sprint13.joblib`
  - `repo/rf_baseline_sprint13.joblib`
  - `repo/rf_tuned_sprint13.joblib`
- Evidencia de matrices de confusión:
  - `docs/sprint13_confusion_matrix_*.png`

---

## 6) Manual de ejecución (end-to-end)

> Recomendación: usar entorno virtual (venv) y ejecutar desde la raíz del repo.

### 6.1 Prerrequisitos
- Python 3.x
- `pip`

### 6.2 Instalación de dependencias
```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3 Generar artefactos del pipeline (ETL + KMeans + perfilamiento)
```bash
python etl/pipeline_sprint2.py
python etl/prepare_features_sprint2.py
python etl/train_kmeans_sprint4.py
python etl/train_kmeans_sprint5.py
python etl/profile_clusters_sprint6.py
```

### 6.4 Levantar API REST (clustering)
```bash
python api/results_api.py
```
- Puerto: **8000**
- Base URL: `http://localhost:8000`

### 6.5 Smoke tests (clustering)
```bash
curl http://localhost:8000/v1/clusters
curl http://localhost:8000/v1/clusters/0
curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"
```

### 6.6 Levantar dashboard (Streamlit)
```bash
streamlit run dashboards/streamlit_sprint7_app.py --server.port 8501
```
- Abre: http://localhost:8501

---

## 7) API REST — documentación consolidada

### 7.1 Base URL
- Clustering (resultados KMeans): `http://localhost:8000`

### 7.2 Endpoints (clusters y métricas)

#### a) Listar clusters
- `GET /v1/clusters`

**Respuesta (ejemplo):**
```json
[
  {"cluster": 0, "cluster_size": 77, "cluster_pct": 25.66},
  {"cluster": 1, "cluster_size": 112, "cluster_pct": 37.33}
]
```

#### b) Perfil completo por cluster
- `GET /v1/clusters/<cluster_id>`

Devuelve un JSON con:
- `cluster`, `cluster_size`, `cluster_pct`
- variables del perfil (promedios/medianas según `cluster_profile_sprint6.csv`)

#### c) Métricas por cluster
- `GET /v1/metrics?cluster_id=<id>&stat=mean|median`

- `stat`:
  - `mean` (por defecto)
  - `median`

**Errores típicos:**
- 400: `cluster_id` inválido / parámetros inválidos
- 404: cluster no existe

---

## 8) Dashboard (Streamlit) — guía de uso

El dashboard usa como fuentes:
- `data/dataset_consolidado_con_cluster_sprint5.csv`
- `data/cluster_profile_sprint6.csv`

Funcionalidades principales:
- resumen de clusters (tamaño y %)
- tablas con perfil por cluster
- comparaciones (heatmap/boxplot/scatter si aplica)
- render del texto narrativo desde `docs/sprint6_cluster_interpretation.md`

---

## 9) Despliegue local (solo local)

### 9.1 Sin Docker
1) Ejecuta el pipeline (sección 6.3)
2) API:
   - `python api/results_api.py` (8000)
3) Dashboard:
   - `streamlit run ... --server.port 8501`

### 9.2 Con Docker Compose (solo API REST)
El repo incluye Docker para la API REST.

Ejecuta desde la raíz:
```bash
docker-compose -f docker/docker-compose.yml up --build
```

Validación:
```bash
curl http://localhost:8000/v1/clusters
```

> Nota: el dashboard no está desplegado dentro del compose actual; se ejecuta como proceso local de Streamlit.

---

## 10) Calidad y tests
- `tests/test_sprint3_quality_gates.py`
- `tests/test_sprint5_training_outputs.py`
- `tests/test_sprint14_supervised_model_gates.py`

Ejecuta:
```bash
pytest -q
```

---

## 11) Referencias internas (para no perder contexto)
Este documento consolida la información. Si en algún punto necesitas más detalle histórico o evidencia adicional, consulta:
- arquitectura: `docs/architecture_etl_model_dashboard.md`
- contratos: `docs/api_results_contract.md`, `docs/api_supervised_results_contract.md`
- runbook adicional: `docs/sprint10_runbook.md`

---

## 12) Checklist final
- [ ] Ejecutaste pipeline completo (sección 6.3)
- [ ] API responde (sección 6.5)
- [ ] Dashboard carga y muestra clusters/perfiles
- [ ] Artefactos esperados existen en `data/` y `repo/`
- [ ] (Opcional) `pytest -q`

