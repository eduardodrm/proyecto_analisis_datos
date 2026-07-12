# Interpretación de segmentos (KMeans)

Dataset de entrada: `C:\Users\Avywenna\Desktop\Study\EV3\data\dataset_consolidado_con_cluster_sprint5.csv`

## Resumen por cluster

| cluster | cluster_size | cluster_pct |
|---|---|---|
| 0.00 | 77.00 | 25.67 |
| 1.00 | 112.00 | 37.33 |
| 2.00 | 111.00 | 37.00 |

## Perfil numérico (promedio y mediana)

| cluster | cluster_size | cluster_pct | horas_consumo_mensual_mean | gasto_mensual_mean | cantidad_contenidos_vistos_mean | sesiones_semana_mean | porcentaje_finalizacion_mean | tiempo_promedio_sesion_min_mean | horas_consumo_mensual_median | gasto_mensual_median | cantidad_contenidos_vistos_median | sesiones_semana_median | porcentaje_finalizacion_median | tiempo_promedio_sesion_min_median |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.0000 | 77.0000 | 25.6667 | 46.4805 | 428.0909 | 25.4286 | 4.8961 | 84.0130 | 212.1688 | 46.0000 | 410.0000 | 25.0000 | 5.0000 | 84.0000 | 223.0000 |
| 1.0000 | 112.0000 | 37.3333 | 28.8661 | 212.0000 | 49.0179 | 15.0179 | 67.8393 | 114.8839 | 28.0000 | 215.5000 | 49.0000 | 15.0000 | 68.0000 | 113.0000 |
| 2.0000 | 111.0000 | 37.0000 | 35.5045 | 79.6757 | 10.2432 | 3.4685 | 37.8108 | 43.8649 | 37.0000 | 78.0000 | 11.0000 | 4.0000 | 37.0000 | 42.0000 |

## Drivers y lectura de negocio por cluster

### Cluster 0
- Driver: **gasto mensual** está en un nivel **alto** para el cluster (z≈1.39, media≈428.09).
- Driver: **tiempo promedio sesion min** está en un nivel **alto** para el cluster (z≈1.31, media≈212.17).
- Driver: **antiguedad cliente meses** está en un nivel **alto** para el cluster (z≈1.21, media≈70.82).
- Driver: **cantidad generos consumidos** está en un nivel **alto** para el cluster (z≈1.11, media≈9.32).
- Driver: **porcentaje uso promociones** está en un nivel **bajo** para el cluster (z≈-1.11, media≈0.09).

**Lectura de negocio (heurística):** cluster principalmente caracterizado como **segmento orientado a consumo vs. sensibilidad a promos**.

### Cluster 1
- Driver: **sesiones semana** está en un nivel **alto** para el cluster (z≈1.04, media≈15.02).
- Driver: **cantidad contenidos vistos** está en un nivel **alto** para el cluster (z≈0.98, media≈49.02).
- Driver: **horas consumo mensual** está en un nivel **bajo** para el cluster (z≈-0.58, media≈28.87).
- Driver: **porcentaje finalizacion** está en un nivel **alto** para el cluster (z≈0.29, media≈67.84).
- Driver: **distancia promedio red km** está en un nivel **alto** para el cluster (z≈0.22, media≈46.00).

**Lectura de negocio (heurística):** cluster principalmente caracterizado como **segmento de intensidad de uso**.

### Cluster 2
- Driver: **antiguedad cliente meses** está en un nivel **bajo** para el cluster (z≈-0.99, media≈14.64).
- Driver: **porcentaje finalizacion** está en un nivel **bajo** para el cluster (z≈-0.96, media≈37.81).
- Driver: **tiempo promedio sesion min** está en un nivel **bajo** para el cluster (z≈-0.93, media≈43.86).
- Driver: **gasto mensual** está en un nivel **bajo** para el cluster (z≈-0.92, media≈79.68).
- Driver: **cantidad generos consumidos** está en un nivel **bajo** para el cluster (z≈-0.90, media≈2.59).

**Lectura de negocio (heurística):** cluster principalmente caracterizado como **segmento de intensidad de uso**.

## Nota
- La interpretación se basa en desviación vs. la media global (z-score) sobre las variables numéricas disponibles.
- Ajustes finos (nombres de segmentos, acciones sugeridas) deben alinearse con conocimiento de negocio.