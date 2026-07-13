# Contrato — Métricas de modelos supervisados (Sprint 14)

Base: `http://localhost:8000`

Este contrato documenta la exposición de métricas del modelo supervisado entrenado en **Sprint 13**.

## Fuente
- `docs/sprint13_supervised_train_report.json`

## Endpoints propuestos

### 1) GET /v1/supervised/models

Devuelve las métricas por modelo y por split (baseline/tuned) para la clasificación de `cluster`.

#### Respuesta (200)
`application/json`

Ejemplo (estructura):
```json
{
  "logistic_regression": {
    "baseline": {
      "metrics": {
        "accuracy": 0.98,
        "f1_macro": 0.98
      }
    },
    "tuned": {
      "metrics": {
        "accuracy": 0.99,
        "f1_macro": 0.99
      }
    }
  },
  "random_forest": {
    "baseline": {"metrics": {"accuracy": 0.95, "f1_macro": 0.95}},
    "tuned": {"metrics": {"accuracy": 0.96, "f1_macro": 0.96}}
  }
}
```

### Errores
- 500 si el reporte no existe o es inválido.

> Nota: si luego se decide exponer también endpoints por modelo específicos, se extenderá el contrato.

