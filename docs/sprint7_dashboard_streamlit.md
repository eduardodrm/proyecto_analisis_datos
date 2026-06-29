# Sprint 7 — Dashboard interactivo (Streamlit)

## Objetivo
Construir un dashboard interactivo para explorar los segmentos (clusters) generados con KMeans.

## Dataset y artefactos usados
- Dataset con cluster: `data/dataset_consolidado_con_cluster_sprint5.csv`
- Perfil por cluster: `data/cluster_profile_sprint6.csv`
- Interpretación (texto): `docs/sprint6_cluster_interpretation.md`

## Implementación
Archivo principal:
- `dashboards/streamlit_sprint7_app.py`

## Funcionalidades (mínimos del enunciado)
1) **Visualización general**
- Cantidad y % de usuarios por cluster.
- Gráfico de barras (tamaño por cluster).
- Gráfico de torta (distribución porcentual).

2) **Perfilamiento de segmentos**
- Tabla con métricas (promedio/mediana) por cluster desde `cluster_profile_sprint6.csv`.

3) **Comparación entre segmentos**
- Heatmap de medias por cluster (top variables con sufijo `_mean`).
- Boxplot para comparar distribución de una variable seleccionada.

4) **Interacción**
- Multiselect de clusters en el sidebar.
- Selectbox para variable del boxplot.
- Selectores para scatter (si hay al menos 2 variables numéricas).

5) **Lectura orientada a negocio**
- Render del reporte `docs/sprint6_cluster_interpretation.md` dentro del dashboard.

## Cómo ejecutar (local)
> Requiere `streamlit` instalado.

```bash
streamlit run dashboards/streamlit_sprint7_app.py
```

## Nota
La demo se espera funcionar en el entorno del repo sin dependencias extra además de las ya definidas.

