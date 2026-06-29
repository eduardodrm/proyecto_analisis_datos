# Sprint 4 — Entrenamiento KMeans + métricas (Elbow y Silhouette)

## Configuración
- k_range: 2..10 (step 1)
- features: 17 columnas
- standardize: True

## Métricas por k

| k | inertia | silhouette_score |
|---:|---:|---:|
| 2 | 3339.6211 | 0.230509 |
| 3 | 2728.7524 | 0.231283 |
| 4 | 2613.6964 | 0.180013 |
| 5 | 2503.1984 | 0.126441 |
| 6 | 2428.8959 | 0.094077 |
| 7 | 2371.5981 | 0.092953 |
| 8 | 2302.0420 | 0.094345 |
| 9 | 2234.1169 | 0.091716 |
| 10 | 2186.2108 | 0.091985 |

## Selección del k óptimo
- k propuesto (best_k): **3**
- Justificación: se elige el k con **mayor silhouette_score** (distancia/estructura de clusters).

## Elbow
- Gráfico: `C:\Users\eduar\Desktop\proyectoEvaluacion3\proyecto_analisis_datos\docs\sprint4_elbow.png`

## Archivos generados
- Métricas CSV: `C:\Users\eduar\Desktop\proyectoEvaluacion3\proyecto_analisis_datos\docs\sprint4_kmeans_metrics.csv`
- Métricas JSON: `C:\Users\eduar\Desktop\proyectoEvaluacion3\proyecto_analisis_datos\docs\sprint4_kmeans_metrics.json`
- Reporte MD: `C:\Users\eduar\Desktop\proyectoEvaluacion3\proyecto_analisis_datos\docs\sprint4_kmeans_report.md`