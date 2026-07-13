# TODO (Sprints por bloques + nombres) — E3 Segmentación (KMeans) + Supervisado

> Regla clave: README “en tiempo real” → refleja solo lo ya completado en cada commit.

---

## Sprint 1 — ✅ **Base técnica y arquitectura ETL (2 fuentes)**
- [x] Arquitectura y documentación base
  - [x] Definir fuentes y su flujo a dataset consolidado (**2 fuentes**).
  - [x] Crear diagrama de arquitectura ETL → dataset → modelo → dashboard.
  - [x] Estructurar README con secciones acordes a Sprint 1.

  - [x] ETL automatizado end-to-end (**2 fuentes**)
    - [x] Extracción
      - [x] CSV `usuarios_streaming.csv`.
      - [x] CSV `perfil_usuarios.csv`.
      - [x] Eliminación del **3er origen** (API REST placeholder) del pipeline.

    - [x] Transformaciones robustas
      - [x] limpieza (nulos, tipos, reglas de rango)
      - [x] normalización de formatos
      - [x] validación de esquema del dataset final (columnas/tipos/rangos/consistencia)

    - [x] Manejo avanzado de errores
      - [x] logging profesional (formatos, niveles)
      - [x] fallos controlados (reintentos cuando aplique) y trazabilidad

    - [x] Persistencia
      - [x] Persistencia de dataset consolidado en `/data/` (script `etl/pipeline_sprint2.py`).

---

## Sprint 2 — **Exploración, limpieza y preparación del dataset**
- [x] EDA (sobre el dataset consolidado)
  - [x] Analizar nulos, distribuciones, outliers, escalas. (docs `eda_inicial_sprint2.md`)
  - [x] Documentar hallazgos y supuestos que afecten preprocesamiento.

- [x] Limpieza de datos
  - [x] Aplicar reglas deterministas para outliers (capping o eliminación según corresponda). (capping 1%-99% en `etl/prepare_features_sprint2.py` + `docs/cleaning_report_sprint2.md`)
  - [x] Controlar consistencia de unidades y escalas. (validación/consistencia vía coerción + rango aproximado por capping; ver report)
  - [x] Generar métricas “antes/después”. (`docs/cleaning_report_sprint2.md`)

- [x] Transformación e Ingeniería de Características
  - [x] Definir transformaciones necesarias para KMeans. (features numéricas listas)
  - [x] Preparar feature pipeline (imputación si aplica, escalamiento/normalización). (imputación mediana + fallback 0)
  - [ ] Ingeniería de características (agregados/ratios si aplica al contexto). (no hay evidencia de nuevos agregados/ratios; se usan variables existentes)
  - [x] Garantizar que no se usen variables categóricas en el dataset final del modelo. (features sin `user_id`, numéricas)

---

## Sprint 3 — **Implementación progresiva (autorizada) Pre-modelado y quality gates (sin entrenar) (avance)**
- [x] Crear ETL mínimo para consolidar dataset (2 fuentes) en `/data/` (eliminar 3er origen del pipeline).
- [x] Generar dataset consolidado.
- [x] Ejecutar EDA inicial (reporte en `/docs/`).
- [x] Aplicar limpieza determinista + crear dataset de features numéricas para KMeans.
- [x] Documentar esquema de features en `/docs/`.
- [x] Actualizar estado en README (en tiempo real al completar bloques).
- [x] Crear pre-modelado sin entrenar (setup KMeans + range de k).
- [x] Tests automatizados de validación de features (numérico, sin NaNs).
- [x] Reporte de ejecución guardado en `/docs/` o `/tests/`.

---

## Sprint 4 — **Entrenamiento KMeans + métricas (codo y silhouette)**
- [x] Preparar entorno y configuración de entrenamiento (seeds, paths, parámetros base).
- [x] Ejecutar KMeans para un rango de k.
- [x] Generar gráfico del método del codo (Elbow).
- [x] Calcular Silhouette Score para cada k.
- [x] Justificar selección del k óptimo (razonamiento + métricas).
- [x] Generar artefactos/outputs del Sprint 4 en `/docs/` (métricas + Elbow + reporte).

---

## Sprint 5 — **Entrenamiento final y generación de resultados**
- [x] Entrenar KMeans con el k seleccionado.
- [x] Asignar cluster a cada usuario y persistir etiquetas.
- [x] Guardar artefactos del modelo (si aplica) y outputs en `/data/` o `/repo/`.
- [x] Verificar que no existen NaNs en features usadas.

---

## Sprint 6 — **Interpretación de segmentos (perfilamiento)**

- [x] Calcular para cada cluster: promedios/medianas y métricas clave.
- [x] Identificar características principales que diferencian los segmentos.
- [x] Redactar interpretación de negocio para cada segmento (texto accionable).
- [x] Comparar segmentos entre sí (diferencias relevantes y hallazgos).

---

## Sprint 7 — **Dashboard interactivo (visualización y filtros)**

- [x] Implementar dashboard con: tamaño de clusters y distribución porcentual.
- [x] Añadir vistas: comparaciones, distribuciones, heatmap (matplotlib) y scatter (si hay suficientes features).
- [x] Añadir interacción: filtros/selección de segmentos y selección dinámica de variables.
- [x] Validar que el dashboard funciona con datos de salida del modelo (dataset + profile Sprint 6).

---

## Sprint 8 — **API REST para servir resultados**
- [x] Definir contrato de API (endpoints, payloads, ejemplos).
- [x] Implementar endpoint(s) para consultar clusters y métricas por segmento.
- [x] Integrar autenticación/validaciones mínimas si aplica (según proyecto).
- [x] Documentar uso en `/docs/`.

---

## Sprint 9 — **Integración final (ETL + modelo + UI/API)**
- [x] Revisar pipeline end-to-end: ingestión → dataset → features → entrenamiento → outputs. (scripts identificados)
- [x] Asegurar trazabilidad (logging y trazas por ejecución). (ETL genera `docs/etl_sprint1_execution_report.json`; se usaron reports de Sprint 5/6)
- [x] Ejecutar una corrida completa de extremo a extremo.
- [x] Actualizar documentación final (README + docs de ejecución).

---

## Sprint 10 — **Entrega, conclusiones y calidad de repositorio**
- [x] Preparar notebook/guía o script de ejecución para replicabilidad. (`docs/sprint10_runbook.md`)
- [x] Evidenciar justificación del k óptimo (codo + silhouette). (`docs/sprint4_kmeans_report.md`)
- [x] Conclusiones orientadas al contexto de negocio. (`docs/sprint10_conclusiones.md`)
- [x] Revisar estructura del repositorio, tests, y consistencia de documentación. (tests: `pytest`)

---

## Sprint 11 — Dashboard ampliado (PCA, Elbow/Silhouette, radar) + endpoint de UI
- [x] Actualizar `dashboards/streamlit_sprint7_app.py`:

  - [x] Agregar PCA (2 componentes) y gráfico interactivo por cluster.

  - [x] Agregar sección “Elbow y Silhouette” usando `docs/sprint4_kmeans_metrics.json` (y `docs/sprint4_elbow.png` si existe).

  - [x] Agregar gráfico radial (radar chart) para comparar perfiles.

  - [x] Agregar toggles: `mean/median` y selector “Top N variables”.

- [x] Actualizar `api/results_api.py`:
  - [x] Implementar `GET /v1/dashboard` (redirigir a la UI del dashboard).

- [x] Smoke tests:
  - [x] `curl http://localhost:8000/v1/clusters`
  - [x] `curl -L http://localhost:8000/v1/dashboard`

---

## Sprint 12 — **Aprendizaje supervisado (predicción de cluster)**
- [x] Definir target supervisado (recomendado: predecir `cluster` generado por KMeans en `data/user_clusters_sprint5.csv`).
- [x] Construir dataset supervisado: `X` = features numéricas (del archivo `data/features_kmeans_sprint2.csv`) y `y` = `cluster`. (script `etl/supervised_dataset_sprint12.py`)
- [x] Split train/val (estratificado por cluster). (script `etl/supervised_dataset_sprint12.py`)


---

## Sprint 13 — **Modelos supervisados + tuning y métricas**
- [x] Entrenar al menos 2 algoritmos supervisados (ej.: RandomForestClassifier + LogisticRegression) con baseline.
- [x] Tuning con GridSearchCV/RandomizedSearchCV (en train).
- [x] Métricas de clasificación por negocio (ej.: accuracy, F1-macro, matriz de confusión).
- [x] Guardar reportes en `/docs/` y modelos en `/repo/`.


---

## Sprint 14 — **Integración de resultados supervisados (API/UI) + CI hooks**
- [x] Actualizar contrato/documentación de API para exponer métricas del modelo supervisado.
- [x] Smoke tests y/o tests unitarios para asegurar que el dataset supervisado no tiene NaNs y que el modelo supera un mínimo razonable de F1-macro.

