# Sprint 5 — Entrenamiento final KMeans + persistencia

## k seleccionado
- best_k (de Sprint 4): **3**

## Entrenamiento
- Algoritmo: KMeans (únicamente KMeans)
- Standardize antes de entrenar: True
- Parámetros:
  - random_state: 42
  - init: k-means++
  - max_iter: 300
  - n_init: 10

## Distribución de clusters

| cluster | count | % |
|---:|---:|---:|
| 0 | 77 | 25.67 |
| 1 | 112 | 37.33 |
| 2 | 111 | 37.00 |

## Archivos generados
- Labels: `C:\Users\Avywenna\Desktop\Study\EV3\data\user_clusters_sprint5.csv`
- Dataset enriquecido: `C:\Users\Avywenna\Desktop\Study\EV3\data\dataset_consolidado_con_cluster_sprint5.csv`
- Modelo (joblib): `C:\Users\Avywenna\Desktop\Study\EV3\repo\kmeans_model_sprint5.joblib`