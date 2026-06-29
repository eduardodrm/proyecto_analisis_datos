# Sprint 9 — Integración final (ETL + modelo + UI/API)

## Checklist (para completar)
- [ ] Revisar pipeline end-to-end: ingestión → dataset → features → entrenamiento → outputs.
- [ ] Asegurar trazabilidad (logging y trazas por ejecución).
- [x] Ejecutar una corrida completa de extremo a extremo.

- [ ] Actualizar documentación final (README + docs de ejecución).

## Corrida end-to-end (comandos)
> Nota: `api/local_source.py` y `api/results_api.py` usan el mismo puerto 8000.

1) Levantar origen 3 (terminal 1):
- `python api/local_source.py`

2) Ejecutar pipeline completo (terminal 2):
- `python etl/pipeline_sprint2.py`
- `python etl/prepare_features_sprint2.py`
- `python etl/train_kmeans_sprint4.py`
- `python etl/train_kmeans_sprint5.py`
- `python etl/profile_clusters_sprint6.py`

3) Apagar origen 3 (detener terminal 1).

4) Levantar API de resultados (terminal 1/3):
- `python api/results_api.py`

5) Smoke tests:
- `curl http://localhost:8000/v1/clusters`
- `curl http://localhost:8000/v1/clusters/0`
- `curl "http://localhost:8000/v1/metrics?cluster_id=0&stat=mean"`

## Evidencias esperadas (outputs)
- `data/cluster_profile_sprint6.csv`
- `docs/sprint5_kmeans_train_report.md` (si no existe, revisar Sprint 5)
- `docs/sprint6_cluster_interpretation.md`
- API responde JSON en endpoints `/v1/*`

