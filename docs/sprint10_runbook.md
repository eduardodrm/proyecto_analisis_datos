# Sprint 10 — Runbook de ejecución (replicabilidad)

Este runbook documenta cómo reproducir el pipeline end-to-end de segmentación no supervisada con **KMeans**.

> Supuestos: se trabaja desde la raíz del repo `proyecto_analisis_datos/`.


## 0) Prerrequisitos
- Python 3.x
- Dependencias: `pip install -r requirements.txt`

> Recomendado: usar entorno virtual para reproducibilidad.


## 1) Origen 3 (API REST local)
Levantar el servicio que provee datos para el ETL.

En una terminal:
```bash
python api/local_source.py
```

- El servicio usa el puerto **8000**.
</new_str

## 2) Pipeline ETL + modelo + artefactos
En otra terminal (ejecutar en este orden):
```bash
python etl/pipeline_sprint2.py
python etl/prepare_features_sprint2.py
python etl/train_kmeans_sprint4.py
python etl/train_kmeans_sprint5.py
python etl/profile_clusters_sprint6.py
```


## 3) Detener origen 3
Cuando termine el pipeline, apagar el proceso de la terminal 1.

## 4) API REST de resultados (segmentos y métricas)
En una terminal:
```bash
python api/results_api.py
```

> La API expone resultados desde `data/cluster_profile_sprint6.csv`.

## 5) Smoke tests (validación rápida)
```bash
curl http://localhost:8000/v1/clusters
curl http://localhost:8000/v1/clusters/0
curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"
```

## 6) Evidencia de k óptimo (Elbow + Silhouette)
El script `etl/train_kmeans_sprint4.py` genera:
- `docs/sprint4_kmeans_metrics.csv`
- `docs/sprint4_kmeans_metrics.json`
- `docs/sprint4_elbow.png` (si `matplotlib` está disponible)
- `docs/sprint4_kmeans_report.md`

En este repo, el reporte selecciona:
- **best_k = 3**
- Criterio: **mayor `silhouette_score`** dentro del rango evaluado.

## 7) Rutas esperadas de outputs principales
- Dataset consolidado + enriquecimientos:
  - `data/dataset_consolidado_sprint2.csv`
  - `data/dataset_consolidado_con_cluster_sprint5.csv`
- Features para KMeans:
  - `data/features_kmeans_sprint2.csv`
- Labels del clustering:
  - `data/user_clusters_sprint5.csv`
- Perfil por cluster:
  - `data/cluster_profile_sprint6.csv`
- Modelo serializado:
  - `repo/kmeans_model_sprint5.joblib`
- Artefactos de Sprint 4 (métricas/k):
  - `docs/sprint4_kmeans_metrics.csv`
  - `docs/sprint4_kmeans_metrics.json`
  - `docs/sprint4_elbow.png`
  - `docs/sprint4_kmeans_report.md`

