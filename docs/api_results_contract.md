# API REST — Resultados de Segmentación (Sprint 8)

Base URL:
- `http://localhost:8001`

Esta API expone los resultados del clustering KMeans (Sprint 5) y su interpretación por segmento (Sprint 6), sirviendo información principalmente desde:
- `data/cluster_profile_sprint6.csv`

---

## 1) Listar clusters

### Endpoint
`GET /v1/clusters`

### Respuesta (200)
`application/json`

Ejemplo:
```json
[
  {
    "cluster": 0,
    "cluster_size": 77,
    "cluster_pct": 25.6666666667
  },
  {
    "cluster": 1,
    "cluster_size": 112,
    "cluster_pct": 37.3333333333
  }
]
```

Campos:
- `cluster` (int): id del segmento
- `cluster_size` (int): cantidad de usuarios en el cluster
- `cluster_pct` (number): porcentaje sobre el total (%).

---

## 2) Obtener perfil completo de un cluster

### Endpoint
`GET /v1/clusters/<cluster_id>`

- `cluster_id` (int): id del segmento

### Respuesta (200)
`application/json`

Ejemplo (estructura):
```json
{
  "cluster": 0,
  "cluster_size": 77,
  "cluster_pct": 25.6666666667,

  "horas_consumo_mensual_mean": 46.48,
  "horas_consumo_mensual_median": 46.0,

  "gasto_mensual_mean": 428.09,
  "gasto_mensual_median": 410.0,

  "...": "..."
}
```

---

### Errores
- **400**: `cluster_id` inválido (no convertible a int)
- **404**: cluster no existe

Formato de error:
```json
{
  "error": "cluster_not_found",
  "details": {"cluster_id": 999}
}
```

---

## 3) Consultar métricas por segmento (mean o median)

### Endpoint
`GET /v1/metrics?cluster_id=<id>&stat=mean|median`

Query params:
- `cluster_id` (int, requerido)
- `stat` (string, opcional; default `mean`)
  - valores permitidos: `mean`, `median`

### Respuesta (200)
`application/json`

Ejemplo:
```json
{
  "cluster": 0,
  "stat": "mean",
  "metrics": {
    "horas_consumo_mensual": 46.48,
    "gasto_mensual": 428.09,
    "sesiones_semana": 4.90
  }
}
```

---

### Errores
- **400**: `cluster_id` ausente o `stat` inválido
- **404**: cluster no existe


