# cleaning_report_sprint2

Entrada: C:\Users\diego\OneDrive\Escritorio\Programacion Cdd\proyecto_analisis_datos\data\dataset_consolidado_sprint2.csv
Salida features: C:\Users\diego\OneDrive\Escritorio\Programacion Cdd\proyecto_analisis_datos\data\features_kmeans_sprint2.csv

## Resumen
Shape antes: (300, 18)
Shape features: (300, 17)

## Nulos antes (top 15)

|                             |   0 |
|:----------------------------|----:|
| extra_metric_a              |   1 |
| extra_metric_b              |   1 |
| horas_consumo_mensual       |   0 |
| user_id                     |   0 |
| gasto_mensual               |   0 |
| cantidad_contenidos_vistos  |   0 |
| tiempo_promedio_sesion_min  |   0 |
| cantidad_generos_consumidos |   0 |
| sesiones_semana             |   0 |
| porcentaje_finalizacion     |   0 |
| antiguedad_cliente_meses    |   0 |
| porcentaje_uso_promociones  |   0 |
| edad                        |   0 |
| dispositivos_registrados    |   0 |
| cantidad_perfiles_creados   |   0 |

## Nulos después (features)

|                                 |   0 |
|:--------------------------------|----:|
| horas_consumo_mensual           |   0 |
| gasto_mensual                   |   0 |
| cantidad_contenidos_vistos      |   0 |
| sesiones_semana                 |   0 |
| porcentaje_finalizacion         |   0 |
| tiempo_promedio_sesion_min      |   0 |
| cantidad_generos_consumidos     |   0 |
| porcentaje_uso_promociones      |   0 |
| antiguedad_cliente_meses        |   0 |
| edad                            |   0 |
| dispositivos_registrados        |   0 |
| porcentaje_uso_app_movil        |   0 |
| cantidad_perfiles_creados       |   0 |
| interacciones_mensuales_soporte |   0 |
| distancia_promedio_red_km       |   0 |

## Outliers capados (1% - 99%)
- Columnas capadas: 17

| columna | cap_low | cap_high |
|---|---:|---:|
| horas_consumo_mensual | 16.000000 | 62.010000 |
| gasto_mensual | 30.000000 | 580.040000 |
| cantidad_contenidos_vistos | 2.000000 | 78.010000 |
| sesiones_semana | 0.000000 | 24.000000 |
| porcentaje_finalizacion | 12.000000 | 99.000000 |
| tiempo_promedio_sesion_min | 5.000000 | 290.020000 |
| cantidad_generos_consumidos | 1.000000 | 14.000000 |
| porcentaje_uso_promociones | 0.004236 | 0.785535 |
| antiguedad_cliente_meses | 2.000000 | 97.020000 |
| edad | 18.000000 | 69.000000 |

## Imputación (mediana)
- Columnas imputadas: 17

| columna | median |
|---|---:|
| horas_consumo_mensual | 36.000000 |
| gasto_mensual | 182.000000 |
| cantidad_contenidos_vistos | 24.000000 |
| sesiones_semana | 6.000000 |
| porcentaje_finalizacion | 64.000000 |
| tiempo_promedio_sesion_min | 91.000000 |
| cantidad_generos_consumidos | 5.000000 |
| porcentaje_uso_promociones | 0.293452 |
| antiguedad_cliente_meses | 37.500000 |
| edad | 44.000000 |