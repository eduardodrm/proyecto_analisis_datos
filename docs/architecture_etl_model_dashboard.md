# Diagrama de arquitectura — ETL → Dataset → Modelo → Dashboard

```mermaid
flowchart LR
  A[usuarios_streaming.csv (CSV)] --> B[ETL: limpieza + validación de esquema]
  C[perfil_usuarios.csv (CSV)] --> B
  D[API REST local (origen 3)] --> B

  B --> E[Dataset consolidado /data/]
  E --> F[KMeans (únicamente KMeans)]
  F --> G[Resultados: labels + métricas]
  G --> H[Dashboard interactivo (Streamlit o Dash)]
  G --> I[API REST de consulta]
```

## Sprint 1 — enfoque técnico
- Validación de esquema del dataset consolidado.
- Manejo de errores con logging profesional y trazabilidad por etapa.
- Reproducibilidad: el origen 3 se ofrece vía API REST **local**.

