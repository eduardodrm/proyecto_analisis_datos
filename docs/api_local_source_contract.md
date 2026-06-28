# Contrato — API REST local (3er origen) para ETL (Sprint 1)

## Endpoint
- `GET /v1/source/extra_user_metrics`

## Respuesta (200)
`application/json`

```json
[
  {
    "user_id": 1,
    "extra_metric_a": 10.0,
    "extra_metric_b": 0.25
  }
]
```

## Campos
- `user_id` (int): identificador del usuario
- `extra_metric_a` (number): métrica adicional A (placeholder)
- `extra_metric_b` (number): métrica adicional B (placeholder)

## Notas
- En sprints posteriores se reemplazará el placeholder por la extracción real.
- El ETL deberá validar esquema del payload y manejar errores de red.

