# Manual de usuario — Segmentación KMeans (Streaming)

## 1) ¿Qué es este proyecto?
El proyecto segmenta usuarios con **KMeans** (aprendizaje no supervisado). Consta de un pipeline (ETL + entrenamiento) que genera artefactos en `data/` y expone los resultados mediante:
- **Dashboard interactivo** (Streamlit).
- **API REST** para consultar clusters y métricas.

Los segmentos resultan de entrenar KMeans con un dataset de **features numéricas** derivadas de:
- `data/usuarios_streaming.csv`
- `data/perfil_usuarios.csv`

## 2) Qué artefactos ver
Una vez ejecutado el pipeline, consulta estos archivos principales:
- `data/user_clusters_sprint5.csv`: asignación usuario → cluster.
- `data/cluster_profile_sprint6.csv`: perfil por cluster (métricas y estadísticos).
- `data/dataset_consolidado_con_cluster_sprint5.csv`: dataset consolidado enriquecido con `cluster`.
- `repo/kmeans_model_sprint5.joblib`: modelo entrenado.

## 3) Cómo usar el Dashboard (Streamlit)

### 3.1 Requisitos
- Python 3.x
- Dependencias instaladas (`pip install -r requirements.txt`)
- Archivo de artefactos generado por el pipeline (sección 8).

### 3.2 Ejecución
```bash
streamlit run dashboards/streamlit_sprint7_app.py --server.port 8501
```
Abre: http://localhost:8501

### 3.3 Secciones del dashboard
1. **Resumen de clusters**
   - Cantidad de usuarios por cluster.
   - Distribución porcentual.

2. **Perfilamiento por cluster**
   - Tabla con métricas (promedio/mediana) para cada cluster desde `data/cluster_profile_sprint6.csv`.

3. **Comparación entre segmentos**
   - Heatmap de variables (por defecto, variables con sufijo `_mean`).
   - Boxplot para comparar distribución de una variable seleccionada.

4. **Reporte narrativo**
   - Render de `docs/sprint6_cluster_interpretation.md` dentro del dashboard.

### 3.4 Lectura orientada a negocio
- Usa el **tamaño y porcentaje** del cluster para estimar alcance.
- Usa las **variables del perfil** para inferir drivers (qué características distinguen a cada segmento).
- Interpreta las métricas junto con el reporte del sprint 6.

## 4) Cómo usar la API REST

### 4.1 Base URL
- `http://localhost:8000`

### 4.2 Endpoints

#### a) Listar clusters
- `GET /v1/clusters`

Devuelve una lista con:
- `cluster`
- `cluster_size`
- `cluster_pct`

#### b) Obtener el perfil completo de un cluster
- `GET /v1/clusters/<cluster_id>`

Devuelve un objeto con:
- tamaño/porcentaje del cluster
- métricas/estadísticos por variable (según el contenido de `cluster_profile_sprint6.csv`)

#### c) Consultar métricas agregadas por cluster
- `GET /v1/metrics?cluster_id=<id>&stat=mean|median`

- `stat` controla si el endpoint usa el promedio (`mean`) o mediana (`median`).

### 4.3 Ejemplos rápidos (curl)
```bash
curl http://localhost:8000/v1/clusters
curl http://localhost:8000/v1/clusters/0
curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"
```

## 5) Manejo de errores (usuario)
- Si el `cluster_id` no existe, el endpoint responde **404**.
- Si el `cluster_id` o `stat` es inválido, responde **400**.

## 6) Supuestos y limitaciones
- El modelo KMeans está entrenado una vez; el dashboard y la API consultan los **artefactos generados**.
- Las salidas están limitadas a las columnas presentes en `data/cluster_profile_sprint6.csv`.
- Si el dashboard no puede generar visualizaciones para ciertas variables, se debe a falta de columnas numéricas disponibles.

## 7) Evidencia de calidad
Revisa en `docs/`:
- `docs/sprint4_kmeans_report.md`
- `docs/sprint4_kmeans_metrics.json`
- `docs/sprint4_elbow.png` (si se generó)

## 8) Flujo recomendado del usuario (resumen)
1. Ejecutar pipeline (ETL → entrenamiento → perfiles).
2. Levantar API REST.
3. Levantar dashboard.
4. Explorar clusters y consultar perfiles vía UI o API.

