# TODO (Sprints por bloques + nombres) — E3 Segmentación no supervisada (KMeans)

> Regla clave: README “en tiempo real” → refleja solo lo ya completado en cada commit.

---

## Sprint 1 — ✅ **Base técnica y arquitectura ETL**
- [x] Arquitectura y documentación base
  - [x] Definir fuentes y su flujo a dataset consolidado (mínimo 3).
  - [x] Crear diagrama de arquitectura ETL → dataset → modelo → dashboard.
  - [x] Estructurar README con secciones acordes a Sprint 1.

  - [x] ETL automatizado end-to-end (mínimo 3 fuentes)
    - [x] Extracción
      - [x] CSV `usuarios_streaming.csv`.
      - [x] Carga desde `perfil_usuarios.csv` hacia tabla en Postgres. (se consolida desde `etl/pipeline_sprint2.py` y se persiste dataset consolidado en Postgres con `etl/db_loader_sprint1.py`)
      - [x] 3er origen (API REST u otra tabla/CSV) definido y documentado. (API REST local)

    - [x] Transformaciones robustas
      - [x] limpieza (nulos, tipos, reglas de rango)
      - [x] normalización de formatos
      - [x] validación de esquema del dataset final (columnas/tipos/rangos/consistencia)

    - [x] Manejo avanzado de errores
      - [x] logging profesional (formatos, niveles)
      - [x] fallos controlados (reintentos cuando aplique) y trazabilidad

    - [x] Persistencia
      - [x] Persistencia Postgres del dataset consolidado (script `etl/db_loader_sprint1.py` + docs).

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
- [x] Crear ETL mínimo para consolidar dataset (3 fuentes) en `/data/`.
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
- [ ] Entrenar KMeans con el k seleccionado.
- [ ] Asignar cluster a cada usuario y persistir etiquetas.
- [ ] Guardar artefactos del modelo (si aplica) y outputs en `/data/` o `/repo/`.
- [ ] Verificar que no existen NaNs en features usadas.

---

## Sprint 6 — **Interpretación de segmentos (perfilamiento)**
- [ ] Calcular para cada cluster: promedios/medianas y métricas clave.
- [ ] Identificar características principales que diferencian los segmentos.
- [ ] Redactar interpretación de negocio para cada segmento (texto accionable).
- [ ] Comparar segmentos entre sí (diferencias relevantes y hallazgos).

---

## Sprint 7 — **Dashboard interactivo (visualización y filtros)**
- [ ] Implementar dashboard con: tamaño de clusters y distribución porcentual.
- [ ] Añadir vistas: comparaciones, distribuciones, heatmap/radiales (según aplique).
- [ ] Añadir interacción: filtros/selección de segmentos y actualización dinámica.
- [ ] Validar que el dashboard funciona con datos de salida del modelo.

---

## Sprint 8 — **API REST para servir resultados**
- [ ] Definir contrato de API (endpoints, payloads, ejemplos).
- [ ] Implementar endpoint(s) para consultar clusters y métricas por segmento.
- [ ] Integrar autenticación/validaciones mínimas si aplica (según proyecto).
- [ ] Documentar uso en `/docs/`.

---

## Sprint 9 — **Integración final (ETL + modelo + UI/API)**
- [ ] Revisar pipeline end-to-end: ingestión → dataset → features → entrenamiento → outputs.
- [ ] Asegurar trazabilidad (logging y trazas por ejecución).
- [ ] Ejecutar una corrida completa de extremo a extremo.
- [ ] Actualizar documentación final (README + docs de ejecución).

---

## Sprint 10 — **Entrega, conclusiones y calidad de repositorio**
- [ ] Preparar notebook/guía o script de ejecución para replicabilidad.
- [ ] Evidenciar justificación del k óptimo (codo + silhouette).
- [ ] Conclusiones orientadas al contexto de negocio.
- [ ] Revisar estructura del repositorio, tests, y consistencia de documentación.

