# Sprint 3 — Pre-modelado (KMeans, sin entrenamiento)

Features CSV: `C:\Users\eduar\Desktop\proyectoEvaluacion3\proyecto_analisis_datos\data\features_kmeans_sprint2.csv`

## Shape
- Filas: 300
- Columnas: 17

## Quality gates
- Total NaNs: 0
- Dtypes (string):
  - horas_consumo_mensual: float64
  - gasto_mensual: float64
  - cantidad_contenidos_vistos: float64
  - sesiones_semana: float64
  - porcentaje_finalizacion: float64
  - tiempo_promedio_sesion_min: float64
  - cantidad_generos_consumidos: float64
  - porcentaje_uso_promociones: float64
  - antiguedad_cliente_meses: float64
  - edad: float64
  - dispositivos_registrados: float64
  - porcentaje_uso_app_movil: float64
  - cantidad_perfiles_creados: float64
  - interacciones_mensuales_soporte: float64
  - distancia_promedio_red_km: float64
  - extra_metric_a: float64
  - extra_metric_b: float64

## Configuración base de KMeans (para Sprint 4)
- random_state: 42
- init: k-means++
- max_iter: 300
- n_init: 10
- k_range: 2..10 (step 1)

> Nota: no se ejecuta KMeans.fit en este sprint.