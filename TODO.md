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

## Sprint 2 — Implementación progresiva (autorizada)
0) Crear ETL mínimo para consolidar dataset (3 fuentes) en `/data/`. ✅
1) Generar dataset consolidado. ✅
2) Ejecutar EDA inicial (reporte en `/docs/`). ✅
3) Aplicar limpieza determinista + crear dataset de features numéricas para KMeans. ✅
4) Documentar esquema de features en `/docs/`. ✅
5) Actualizar estado en README (en tiempo real al completar bloques). ✅

---

## Sprint 3 — **Pre-modelado y quality gates (sin entrenar) (avance)**
1) Crear pre-modelado sin entrenar (setup KMeans + range de k). ✅
2) Tests automatizados de validación de features (numérico, sin NaNs). ✅
3) Reporte de ejecución guardado en `/docs/` o `/tests/`. ✅



