# Reproducibilidad (E3 Segmentación KMeans)

Guía para que cualquier persona pueda ejecutar el pipeline y levantar el dashboard/UI con los mismos artefactos.

> Directorio de trabajo esperado: la raíz del repo `proyecto_analisis_datos/`.

---

## 1) Prerrequisitos
- Python 3.x
- Acceso a red local (solo si se ejecutan servicios locales; en este proyecto el origen 3 es local)

---

## 2) Crear entorno y dependencias
### Recomendado (venv)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3) Correr el pipeline end-to-end (ETL → modelo → perfiles)
El proyecto genera artefactos en:
- `data/`
- `docs/`
- `repo/`

### 3.1) Levantar Origen 3 (API REST local)
En una terminal:
```bash
python api/local_source.py
```
- Puerto: **8000**

### 3.2) Ejecutar pipeline
En otra terminal (sin detener la anterior):
```bash
python etl/pipeline_sprint2.py
python etl/prepare_features_sprint2.py
python etl/train_kmeans_sprint4.py
python etl/train_kmeans_sprint5.py
python etl/profile_clusters_sprint6.py
```

### 3.3) Apagar origen 3
Cuando termine el pipeline, detén `python api/local_source.py`.

---

## 4) Levantar API de resultados (clusters + métricas)
En una terminal:
```bash
python api/results_api.py
```
- Puerto: **8000**

---

## 5) Smoke tests (API)
Ejecuta:
```bash
python -c "import requests; print(requests.get('http://localhost:8000/v1/clusters').status_code)"
python -c "import requests; print(requests.get('http://localhost:8000/v1/clusters/0').status_code)"
python -c "import requests; print(requests.get('http://localhost:8000/v1/metrics?cluster_id=0&stat=mean').status_code)"
```

> Nota: el endpoint `GET /v1/dashboard` puede depender de cómo se despliegue el frontend Streamlit.

---

## 6) Levantar dashboard Streamlit (interactivo)
En otra terminal:
```bash
streamlit run dashboards/streamlit_sprint7_app.py --server.port 8501
```

- Abre: http://localhost:8501

---

## 7) Qué verificar / evidencia
### K óptimo (Sprint 4)
Revisa:
- `docs/sprint4_kmeans_metrics.json` (contiene `silhouette_score` por k y `best_k`)
- `docs/sprint4_elbow.png` (si matplotlib está disponible en el entorno)
- `docs/sprint4_kmeans_report.md`

### Perfiles y segmentos (Sprint 6)
- `data/cluster_profile_sprint6.csv`

---

## 8) Notas de compatibilidad
- Este proyecto usa `matplotlib` en varios reportes; si el entorno no genera PNG, se mantiene el JSON/CSV como evidencia.
- El dashboard intenta trabajar con `dataset_consolidado_con_cluster_sprint5.csv` y `cluster_profile_sprint6.csv`.

