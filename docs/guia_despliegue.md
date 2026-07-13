# Guía de despliegue (local) — Dashboard + API REST

## 1) Alcance
Despliegue **solo local**, pensado para ejecutar con artefactos ya generados por el pipeline del proyecto.
Incluye:
- Ejecución local (sin Docker)
- Ejecución con Docker Compose

## 2) Requisitos previos
- Python 3.x y `pip` (para ejecución sin Docker)
- Docker Desktop (para opción con Docker)

## 3) Paso 0 — Generar artefactos (ETL → modelo → perfiles)
Antes de desplegar UI/API, ejecuta el pipeline end-to-end.

En una terminal (Windows):
```bash
python etl/pipeline_sprint2.py
python etl/prepare_features_sprint2.py
python etl/train_kmeans_sprint4.py
python etl/train_kmeans_sprint5.py
python etl/profile_clusters_sprint6.py
```

Esto genera artefactos en:
- `data/` (datasets + perfil por cluster)
- `docs/` (evidencia del entrenamiento)
- `repo/` (modelo)

## 4) Despliegue local (sin Docker)

### 4.1 Levantar API REST
```bash
python api/results_api.py
```
- Puerto: **8000**

Valida con:
```bash
curl http://localhost:8000/v1/clusters
```

### 4.2 Levantar dashboard Streamlit
```bash
streamlit run dashboards/streamlit_sprint7_app.py --server.port 8501
```
Abre: http://localhost:8501

## 5) Despliegue con Docker Compose

### 5.1 Construir y levantar servicios
Desde la carpeta `docker/compose` no aplica; usa la ruta del archivo existente en el repo.

Ejecuta desde la raíz del repo:
```bash
docker-compose -f docker/docker-compose.yml up --build
```

### 5.2 Qué se levanta
Por `docker/docker-compose.yml` se levanta:
- `results_api` en `container_name: e3-results-api`
- Puerto: **8000** mapeado como `8000:8000`

### 5.3 Validación (smoke tests)
Con el contenedor arriba:
```bash
curl http://localhost:8000/v1/clusters
curl http://localhost:8000/v1/clusters/0
curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"
```

## 6) Nota sobre el dashboard con Docker
El repo actual incluye Docker para la **API REST**. Para correr el dashboard con Docker sería necesario agregar un segundo servicio (Streamlit) al `docker-compose.yml`.

## 7) Troubleshooting rápido
- **La API responde 500**: verifica que exista `data/cluster_profile_sprint6.csv`.
- **Endpoints no encontrados**: verifica que la API esté escuchando en el puerto **8000**.
- **El dashboard no carga**: valida que existan `data/dataset_consolidado_con_cluster_sprint5.csv` y `data/cluster_profile_sprint6.csv`.

