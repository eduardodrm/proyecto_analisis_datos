# Sprint 10 — Conclusiones orientadas al negocio

## Qué aportan los clusters
Con KMeans (segmentación no supervisada) se agrupan usuarios según patrones de comportamiento/consumo representados por las variables numéricas definidas en el pipeline de features.

Esto habilita:
- **Personalización**: campañas o recomendaciones adaptadas por segmento.
- **Priorización operativa**: identificar segmentos con mayor gasto/actividad para estrategias de retención o crecimiento.
- **Lectura accionable**: el perfil por cluster resume tendencias centrales (media/mediana) para facilitar decisiones.

## Evidencia del k óptimo (Elbow + Silhouette)
El script `etl/train_kmeans_sprint4.py` evalúa k en el rango definido por `docs/sprint3_kmeans_base_config.json`, calculando:
- **Elbow (inertia)**: compactación de clusters.
- **Silhouette score**: separación y cohesión.

En el reporte `docs/sprint4_kmeans_report.md` el modelo selecciona:
- **best_k = 3**, por ser el **k con mayor `silhouette_score`** dentro del rango evaluado.

## Cómo usar los resultados
- Consultar **por cluster** la información servida por la API:
  - `data/cluster_profile_sprint6.csv` (fuente de perfiles)
- Usar el dashboard (Sprint 7) para validar patrones visualmente y explorar diferencias por variable.

## Limitaciones y próximos pasos
- Al ser no supervisado, los clusters deben interpretarse con cautela: validar consistencia temporal y estabilidad del clustering.
- Próximo paso sugerido: **monitorizar drift** y re-entrenar cuando cambien los patrones de comportamiento.
- Extensión futura: incorporar más variables (o ingeniería de features agregados/ratios) si el contexto de negocio lo justifica.

