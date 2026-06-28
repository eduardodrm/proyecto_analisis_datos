# EDA inicial (Sprint 2)

> Dataset consolidado: `data/dataset_consolidado_sprint2.csv`

## 1) Tamaño
- Filas: 300
- Columnas: 18

## 2) Nulos (rápido)
- `extra_metric_a`: 100% nulos (señal: el payload de API local es placeholder y puede no estar completo para todos los `user_id`)
- `extra_metric_b`: 100% nulos
- El resto de variables numéricas presenta 0% nulos.

## 3) Variables incluidas
Del dataset consolidado se identifican variables típicas para segmentación KMeans como:
- consumo: `horas_consumo_mensual`, `gasto_mensual`, `cantidad_contenidos_vistos`, `sesiones_semana`, `porcentaje_finalizacion`, `tiempo_promedio_sesion_min`
- diversidad: `cantidad_generos_consumidos`, `cantidad_generos_consumidos`
- promociones: `porcentaje_uso_promociones`
- perfil: `edad`, `dispositivos_registrados`, `porcentaje_uso_app_movil`, `cantidad_perfiles_creados`
- soporte/red: `interacciones_mensuales_soporte`, `distancia_promedio_red_km`

## 4) Observación para preprocesamiento
Como las variables del origen 3 (`extra_metric_*`) vienen completamente nulas, se trata en el pipeline de features con imputación (y fallback a 0) para que el dataset final de KMeans no tenga NaNs.

---

> Siguiente paso en Sprint 2: limpieza determinista + construcción de `data/features_kmeans_sprint2.csv` (ya ejecutado en el repo).

