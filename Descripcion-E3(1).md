# Evaluación: Segmentación de usuarios mediante técnicas de aprendizaje no supervisado

## Contexto de negocio

Una empresa dedicada al servicio de streaming digital desea mejorar la experiencia de sus usuarios mediante estrategias personalizadas de contenido y fidelización.

Actualmente, la plataforma recomienda contenido utilizando reglas generales para todos sus usuarios. Sin embargo, la organización busca identificar grupos de usuarios con comportamientos similares para diseñar acciones diferenciadas, tales como:

* recomendaciones personalizadas de contenido,
* campañas de retención,
* beneficios para usuarios frecuentes,
* estrategias para aumentar el consumo dentro de la plataforma.

El área de analítica ha identificado que la información necesaria para comprender el comportamiento de los usuarios se encuentra distribuida en diferentes sistemas internos.

Por esta razón, antes de construir un modelo de segmentación será necesario integrar y preparar los datos provenientes de distintas fuentes.

El objetivo del proyecto es construir un modelo de segmentación utilizando técnicas de aprendizaje no supervisado que permita identificar perfiles de usuarios con características similares.

---

# Fuentes de datos disponibles

## Fuente 1: Información de consumo dentro de la plataforma

Archivo:

`usuarios_streaming.csv`

Esta fuente contiene información relacionada con los hábitos de consumo de los usuarios dentro de la plataforma.

Incluye variables como:

* horas de consumo mensual
* gasto mensual asociado al servicio
* cantidad de contenidos vistos
* cantidad de sesiones semanales
* porcentaje de contenidos finalizados
* duración promedio de sesión
* cantidad de géneros consumidos
* porcentaje de uso de promociones
* antigüedad del usuario

---

## Fuente 2: Información complementaria del usuario

Archivo:

`perfil_usuarios.csv`

Esta fuente contiene información obtenida desde el sistema de perfiles y atención al usuario.

Incluye variables como:

* edad del usuario
* cantidad de dispositivos registrados
* porcentaje de uso desde aplicación móvil
* cantidad de perfiles creados
* cantidad de interacciones con soporte
* distancia promedio asociada a la red de conexión

El contenido de este archivo debe ser cargado en una tabla en una base de datos en postgres.

---

# Objetivo general

Integrar ambas fuentes de datos, construir un conjunto analítico consolidado y desarrollar un modelo de segmentación utilizando el algoritmo KMeans que permita identificar perfiles diferenciados de usuarios.

---

# Actividades a desarrollar



## 1. Construcción del modelo

Implementar:

**Algoritmo obligatorio:**

* KMeans

Consideraciones:

* Aplicar escalamiento antes del entrenamiento.
* Evaluar diferentes cantidades de clusters.
* Justificar la selección del número óptimo de grupos.

Debe incluir:

* Método del codo.
* Coeficiente Silhouette.

---

## 2. Interpretación de segmentos

Analizar los grupos obtenidos considerando:

* características principales,
* diferencias entre segmentos,
* comportamiento de usuarios.

Cada segmento debe tener una interpretación de negocio.

Ejemplo:

"Usuarios intensivos con alto consumo mensual y baja sensibilidad a promociones".

## 3. Construcción de dashboard de análisis de segmentos

Una vez construido el modelo de segmentación e identificados los grupos de usuarios, deberá desarrollar un dashboard interactivo que permita visualizar y comunicar los resultados obtenidos.

El dashboard debe estar orientado a usuarios de negocio, permitiendo comprender las características principales de cada segmento identificado.

La solución debe incluir como mínimo:

### Visualización general de segmentos

* Cantidad de usuarios pertenecientes a cada cluster.
* Distribución porcentual de usuarios por segmento.
* Visualización gráfica que permita comparar el tamaño de los grupos.

### Perfilamiento de segmentos

Para cada segmento deberá mostrar indicadores que permitan interpretar su comportamiento, tales como:

* promedio de horas de consumo mensual,
* gasto mensual promedio,
* cantidad promedio de contenidos vistos,
* antigüedad promedio,
* porcentaje de uso de promociones,
* promedio de dispositivos utilizados.

### Comparación entre segmentos

El dashboard debe permitir identificar diferencias entre clusters mediante visualizaciones como:

* gráficos comparativos,
* gráficos de distribución,
* mapas de calor,
* gráficos radiales u otras visualizaciones apropiadas.

### Interacción

El dashboard debe permitir explorar los resultados mediante elementos interactivos, por ejemplo:

* filtros por segmento,
* selección de clusters,
* actualización dinámica de métricas.

La herramienta utilizada para la construcción del dashboard debe permitir la exploración de los resultados obtenidos por el modelo.


---

# Entregables


El grupo deberá dejar evidencia en el repositorio considerando ramas que evidencien la participación de cada integrante:

1. Código utilizado para:
   * carga de datos,
   * integración de fuentes,
   * limpieza,
   * transformación,
   * entrenamiento del modelo,
   * generación de resultados para visualización.

2. Dashboard interactivo implementado utilizando una herramienta de visualización.

   * El dashboard debe permitir analizar los segmentos encontrados y presentar información relevante para la toma de decisiones.

3. Presentación final:

* Justificación del número de clusters seleccionado.
* Metodología aplicada.
* Análisis e interpretación de los segmentos.
* Evidencia del funcionamiento del dashboard.
* Conclusiones orientadas al contexto de negocio.


---

# Restricciones

* Utilizar únicamente KMeans.
* No utilizar variables categóricas en el modelo final.
* Las conclusiones deben estar fundamentadas en los resultados obtenidos.



_Última actualización: 2026-06-17_