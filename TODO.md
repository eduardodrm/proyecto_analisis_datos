# TODO (Sprints por bloques + nombres) — E3 Segmentación no supervisada (KMeans)

> Regla clave: README “en tiempo real” → refleja solo lo ya completado en cada commit.

---

## Sprint 1 — **Base técnica y arquitectura ETL**
1) Arquitectura y documentación base
   - Definir fuentes y su flujo a dataset consolidado (mínimo 3). ✅
   - Crear diagrama de arquitectura ETL → dataset → modelo → dashboard. ✅
   - Estructurar README con secciones acordes a Sprint 1. ✅


2) ETL automatizado end-to-end (mínimo 3 fuentes)
   - Extracción:
     - CSV `usuarios_streaming.csv`. ⏳
     - Carga desde `perfil_usuarios.csv` hacia tabla en Postgres. ⏳
     - 3er origen (API REST u otra tabla/CSV) definido y documentado. ✅ (API REST local)

   - Transformaciones robustas:
     - limpieza (nulos, tipos, reglas de rango),
     - normalización de formatos,
     - validación de esquema del dataset final (columnas/tipos/rangos/consistencia).
   - Manejo avanzado de errores:
     - logging profesional (formatos, niveles),
     - fallos controlados (reintentos cuando aplique) y trazabilidad.
   - Persistencia:
     - dataset final consolidado en `/data/`.

---

## Sprint 2 — **Exploración, limpieza y preparación del dataset**
1) EDA (sobre el dataset consolidado)
   - Analizar nulos, distribuciones, outliers, escalas.
   - Documentar hallazgos y supuestos que afecten preprocesamiento.

2) Limpieza de datos
   - Aplicar reglas deterministas para outliers (capping o eliminación según corresponda).
   - Controlar consistencia de unidades y escalas.
   - Generar métricas “antes/después”.

3) Transformación e Ingeniería de Características
   - Definir transformaciones necesarias para KMeans.
   - Preparar feature pipeline (imputación si aplica, escalamiento/normalización).
   - Ingeniería de características (agregados/ratios si aplica al contexto).
   - Garantizar que no se usen variables categóricas en el dataset final del modelo.

---

## Sprint 3 — **Pre-modelado y quality gates (sin entrenar)**
1) Configuración del Modelo (pre-modelado, solo K-Means)
   - Seleccionar features finales (esquema de columnas).
   - Definir configuración base del modelo (random_state, init, max_iter, rango de k a evaluar).
   - Preparar estructura para ejecutar luego (sin entrenar todavía en este sprint).

2) Testing automatizado (pre-modelado)
   - Tests unitarios para limpieza/transformaciones.
   - Tests de validación de esquema.
   - Tests para asegurar ausencia de categóricas y tipos numéricos.
   - Reporte de ejecución guardado en `/tests/`.

---

## Sprint 4 — **Dataset listo para entrenamiento + KMeans inicial**
1) Preparación final del dataset para entrenamiento
   - Cargar dataset preprocesado.
   - Verificar esquema final (columnas numéricas, sin NaNs según estrategia).

2) Entrenamiento KMeans (KMeans únicamente)
   - Ejecutar KMeans para una grilla de k.
   - Guardar métricas por k.

---

## Sprint 5 — **Selección de k + persistencia de artefactos**
1) Selección de k
   - Método del codo (inercia) y gráfico.
   - Silhouette score y gráfico.
   - Justificación del k final con base en métricas.

2) Artefactos y resultados
   - Guardar: modelo, centroides y labels por usuario.
   - Persistir dataset con columna de cluster en `/data/` o ruta acordada.

3) Testing de entrenamiento
   - Tests de que el pipeline produce labels consistentes (dimensiones, no NaNs).

---

## Sprint 6 — **Interpretación de segmentos (negocio)**
1) Interpretación de clusters (negocio)
   - Calcular métricas por cluster (promedios/medianas) para:
     - horas/mes, gasto/mes, contenidos vistos, antigüedad, promos %, dispositivos, etc.
   - Describir “drivers” y diferenciar segmentos.
   - Redactar interpretación de negocio por cluster.

---

## Sprint 7 — **Dashboard interactivo y evidencia visual**
1) Dashboard interactivo (Streamlit o Plotly Dash)
   - Visualización general:
     - cantidad y % por cluster.
   - Perfilamiento por segmento:
     - métricas principales por cluster.
   - Comparación entre segmentos:
     - heatmap / distribuciones / comparativos.
   - Interacción:
     - filtros por cluster, selección/actualización dinámica.
   - Diferenciar audiencia (texto y layout “para negocio”).

2) Evidencia
   - Capturas del dashboard en `/dashboards/`.

---

## Sprint 8 — **API REST: exposición de resultados**
1) API RESTful en `/api/`
   - Endpoint para clusters y métricas.
   - Endpoint para dataset/artifacts (si aplica).
   - Documentar contratos (ejemplos de request/response).

---

## Sprint 9 — **Containerización y ejecución reproducible**
1) Containerización
   - Dockerfiles (API/ETL/dashboard si aplica).
   - docker-compose con servicios (web/API/db si aplica localmente).
   - Variables de entorno para configuración externa.

2) Logging y ejecución reproducible
   - Configurar logging en cada componente.
   - Scripts de ejecución y comandos documentados.

---

## Sprint 10 — **Despliegue, cierre y documentación final**
1) Manual de despliegue
   - Guía paso a paso en `/docs/`.
   - Sección final en README con cómo desplegar.

2) Cierre
   - Actualizar README completo solo al final (con evidencia de tests/outputs).
   - Revisar estructura de carpetas y que todo esté actualizado.

