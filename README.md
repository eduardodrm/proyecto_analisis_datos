# Segmentación de Clientes con Machine Learning

## Descripción del proyecto

Este proyecto implementa una solución completa de segmentación de clientes utilizando técnicas de aprendizaje no supervisado.

El objetivo es identificar grupos de clientes con comportamientos similares a partir de sus características comerciales y de perfil, utilizando el algoritmo **KMeans**.

La solución integra:

- Una fuente de datos en formato CSV.
- Una segunda fuente de datos almacenada en una base de datos PostgreSQL.
- Un pipeline de integración de datos.
- Entrenamiento de un modelo de clustering.
- Exposición del modelo mediante una API REST.
- Dashboard interactivo para análisis de resultados.
- Contenerización completa utilizando Docker.

---

# Arquitectura de la solución


```
                 CSV Clientes
                      |
                      |
                      v

              +----------------+
              |  Integración   |
              |   de datos     |
              +----------------+
                      |
                      |
        +-------------+-------------+
        |                           |
        v                           v

PostgreSQL CRM                Dataset integrado
perfil_cliente                data_clientes.csv


                      |
                      |
                      v

              +----------------+
              |    KMeans      |
              |  Segmentación  |
              +----------------+

                      |
          +-----------+-----------+
          |                       |

          v                       v

      FastAPI                Streamlit
   Servicio ML              Dashboard

```


---

# Tecnologías utilizadas

## Lenguaje

- Python 3.11

## Machine Learning

- Scikit-learn
- KMeans
- StandardScaler
- Silhouette Score
- Método del codo mediante KneeLocator


## Datos

- Pandas
- PostgreSQL
- SQLAlchemy


## Backend

- FastAPI
- Uvicorn


## Visualización

- Streamlit


## Infraestructura

- Docker
- Docker Compose


---

# Estructura del proyecto


```

segmentacion-clientes/

│
├── docker-compose.yml
│
├── database/
│   ├── init.sql
│   └── perfil_cliente.csv
│
├── data/
│   ├── clientes_ecommerce.csv
│   └── data_clientes.csv
│
├── ml-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── train.py
│   ├── app.py
│   ├── modelo_kmeans.pkl
│   └── scaler.pkl
│
└── dashboard/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py


```

---

# Fuentes de datos

## Fuente 1: CSV

Archivo:

```
clientes_ecommerce.csv
```

Contiene información asociada al comportamiento comercial de los clientes.


Ejemplos de variables:

- frecuencia de compra
- gasto promedio
- cantidad de compras
- interacciones digitales


---

## Fuente 2: PostgreSQL

Base de datos:

```
crm_clientes
```

Tabla:

```
perfil_cliente
```

Contiene información complementaria del cliente:

- edad
- características demográficas
- comportamiento registrado en CRM


---

# Pipeline de Machine Learning


El proceso ejecutado por `train.py` realiza:

1. Lectura del archivo CSV.

2. Conexión a PostgreSQL.

3. Extracción de información desde la tabla:

```
perfil_cliente
```

4. Integración mediante:

```
cliente_id
```

5. Generación del dataset analítico:

```
data_clientes.csv
```

6. Normalización de variables utilizando:

```
StandardScaler
```

7. Evaluación de diferentes cantidades de clusters.

8. Selección del número óptimo de segmentos.

9. Entrenamiento del modelo KMeans.

10. Persistencia del modelo:

```
modelo_kmeans.pkl
```

y del escalador:

```
scaler.pkl
```

---

# Ejecución del proyecto

## Requisitos

Tener instalado:

- Docker
- Docker Compose


---

## Levantar la solución

Desde la raíz del proyecto:


```bash
docker compose up --build
```


Esto levantará tres servicios:


| Servicio | Puerto |
|-|-|
| PostgreSQL | 5432 |
| FastAPI | 8000 |
| Streamlit | 8501 |


---

# Acceso a los servicios


## API Machine Learning

Abrir:


```
http://localhost:8000
```


Respuesta esperada:


```json
{
 "mensaje": "Servicio ML funcionando"
}
```


---

## Dashboard

Abrir:


```
http://localhost:8501
```


El dashboard permite:

- métricas del modelo.
- visualizar los clientes segmentados.
- visualizar distribución de segmentos.
- analizar el perfil de cada grupo.


---

# Endpoint de predicción


Servicio:


```
POST /predict
```


Ejemplo de entrada:


```json
{
 "edad":35,
 "ingreso_mensual":5000,
 "frecuencia_compra":10
}
```


Respuesta:


```json
{
 "cluster":2
}
```


---

# Perfilamiento de segmentos


Luego de la predicción se genera un resumen con características promedio:


Ejemplo:


| Segmento | Perfil |
|-|-|
| 0 | Clientes Premium |
| 1 | Clientes sensibles a descuentos |
| 2 | Clientes ocasionales |
| 3 | Clientes exploradores |


El perfil se obtiene analizando:

- promedio de gasto.
- frecuencia de compra.
- edad promedio.
- comportamiento digital.
- características comerciales.


---

# Detener servicios


Para detener los contenedores:


```bash
docker compose down
```


Para eliminar también los volúmenes:


```bash
docker compose down -v
```

---

# Para cambios de código


Para detener los contenedores:


```bash
docker compose down
```


Para eliminar también los volúmenes:


```bash
docker compose build --no-cache
```


Luego, levantamos 


```bash
docker compose up
```

---
Para verificar el contenido de la tabla

```bash
docker exec -it crm_database psql -U admin -d crm_clientes
```

Luego, para ver las tablas, ejecutar

```bash
\dt
```


---

# Objetivo del proyecto

Construir una solución analítica completa que permita transformar datos provenientes de múltiples fuentes en información accionable para la toma de decisiones mediante técnicas de Machine Learning no supervisado.