"""
Sprint 7 — Dashboard interactivo para la segmentación de usuarios.

Este script implementa un dashboard con Streamlit para visualizar y analizar
los clusters de usuarios generados por el modelo KMeans.

Funcionalidades:
- Visualización general del tamaño de los segmentos.
- Perfilamiento detallado de cada cluster.
- Comparación interactiva entre segmentos.
- Visualización de clusters en 2D mediante PCA.
- Interpretación de negocio de los segmentos.

Para ejecutar:
streamlit run dashboards/streamlit_sprint7_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
from sklearn.decomposition import PCA


# --- Configuración de la página y rutas ---
st.set_page_config(
    page_title="Dashboard de Segmentación de Usuarios",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
REPO_DIR = PROJECT_ROOT / "repo"

# --- Carga de datos (con caché) ---
@st.cache_data
def load_data():
    """Carga todos los datasets necesarios para el dashboard."""
    paths = {
        "clustered_data": DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv",
        "profile": DATA_DIR / "cluster_profile_sprint6.csv",
        "interpretation": DOCS_DIR / "sprint6_cluster_interpretation.md",
    }
    
    data = {}
    for key, path in paths.items():
        if not path.exists():
            st.error(f"Error: No se encontró el archivo {path}. Asegúrese de ejecutar los sprints anteriores.")
            return None
        if path.suffix == ".csv":
            data[key] = pd.read_csv(path)
        else:
            data[key] = path.read_text(encoding="utf-8")
            
    return data

@st.cache_data
def load_pca_data():
    """Carga los datos específicos para la visualización PCA, reutilizando artefactos."""
    features_path = DATA_DIR / "features_kmeans_sprint2.csv"
    clustered_data_path = DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv"
    model_path = REPO_DIR / "kmeans_model_sprint5.joblib"

    if not features_path.exists() or not clustered_data_path.exists() or not model_path.exists():
        return None, None, None, "Faltan archivos necesarios."

    features_df = pd.read_csv(features_path)
    clustered_df = pd.read_csv(clustered_data_path)

    if "user_id" not in features_df.columns or "user_id" not in clustered_df.columns:
        return None, None, None, "Los archivos CSV deben contener 'user_id'."

    merged_df = pd.merge(
        features_df,
        clustered_df[["user_id", "cluster"]],
        on="user_id",
        how="inner",
    )

    bundle = joblib.load(model_path)

    # Recuperar los objetos guardados
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_cols = bundle["feature_cols"]

    # Preparar los datos
    X = merged_df[feature_cols].values
    X = scaler.transform(X)

    y = merged_df["cluster"].values

    # Centroides
    centroids = model.cluster_centers_

    return X, y, centroids, None
    


# --- Funciones de visualización ---

def show_general_visualization(profile_df):
    st.header("1. Visualización General de Segmentos")
    summary_df = profile_df[['cluster', 'cluster_size', 'cluster_pct']].copy()
    summary_df.rename(columns={'cluster': 'Cluster', 'cluster_size': 'Nº Usuarios', 'cluster_pct': '% Usuarios'}, inplace=True)
    
    st.write("Cantidad y porcentaje de usuarios por cluster:")
    st.dataframe(summary_df.set_index('Cluster'))

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.barplot(x='Cluster', y='Nº Usuarios', data=summary_df, ax=ax, palette='viridis')
        ax.set_title('Cantidad de Usuarios por Cluster')
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots()
        ax.pie(summary_df['Nº Usuarios'], labels=[f"Cluster {c}" for c in summary_df['Cluster']], autopct='%1.1f%%', startangle=90, colors=sns.color_palette('viridis', len(summary_df)))
        ax.axis('equal')
        ax.set_title('Distribución Porcentual de Usuarios')
        st.pyplot(fig)

def show_segment_profiling(profile_df):
    st.header("2. Perfilamiento de Segmentos")
    st.write("Tabla con métricas promedio por cluster para entender sus características dominantes.")
    mean_cols = [col for col in profile_df.columns if '_mean' in col]
    display_cols = ['cluster', 'cluster_size'] + mean_cols
    st.dataframe(profile_df[display_cols].set_index('cluster'))

def show_segment_comparison(profile_df, clustered_data_df, selected_clusters):
    st.header("3. Comparación entre Segmentos")
    if not selected_clusters:
        st.warning("Por favor, seleccione al menos un cluster en el panel lateral.")
        return

    filtered_profile = profile_df[profile_df['cluster'].isin(selected_clusters)]
    filtered_data = clustered_data_df[clustered_data_df['cluster'].isin(selected_clusters)]

    st.subheader("Heatmap de Características Promedio")
    heatmap_vars = [col for col in filtered_profile.columns if '_mean' in col]
    if heatmap_vars:
        heatmap_data = filtered_profile.set_index('cluster')[heatmap_vars]
        heatmap_data_normalized = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
        fig, ax = plt.subplots(figsize=(12, max(6, len(selected_clusters))))
        sns.heatmap(heatmap_data_normalized.T, annot=True, cmap='viridis', fmt=".2f", ax=ax)
        ax.set_title('Comparación Normalizada de Métricas Promedio por Cluster')
        st.pyplot(fig)

    st.subheader("Distribución de una Variable por Cluster")
    selectable_vars = [col for col in clustered_data_df.select_dtypes(include=np.number).columns if col not in ['user_id', 'cluster']]
    selected_var = st.selectbox("Seleccione una variable para comparar distribuciones:", options=selectable_vars)
    if selected_var:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='cluster', y=selected_var, data=filtered_data, ax=ax, palette='viridis', order=sorted(selected_clusters))
        ax.set_title(f'Distribución de "{selected_var}" por Cluster')
        st.pyplot(fig)

def show_pca_visualization():
    st.header("4. Visualización de Clusters y Centroides")

    clustered_path = DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv"
    model_path = REPO_DIR / "kmeans_model_sprint5.joblib"

    if not clustered_path.exists() or not model_path.exists():
        st.error("No existen los archivos necesarios.")
        return

    data = pd.read_csv(clustered_path)

    bundle = joblib.load(model_path)

    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_cols = bundle["feature_cols"]

    # Variables a mostrar
    columna_x = "gasto_mensual"
    columna_y = "horas_consumo_mensual"

    X = data[feature_cols]

    # Centroides en escala original
    centroides_original = scaler.inverse_transform(model.cluster_centers_)

    plt.figure(figsize=(10,7))

    plt.scatter(
        data[columna_x],
        data[columna_y],
        c=data["cluster"],
        cmap="viridis",
        s=40,
        alpha=0.7
    )

    plt.scatter(
        centroides_original[:, feature_cols.index(columna_x)],
        centroides_original[:, feature_cols.index(columna_y)],
        marker="X",
        s=250,
        c="red",
        edgecolor="black",
        linewidth=2,
        label="Centroides"
    )

    plt.xlabel(columna_x)
    plt.ylabel(columna_y)
    plt.title("Clusters K-Means (k=3)")
    plt.grid(True)
    plt.legend()

    st.pyplot(plt.gcf())

    st.markdown("""
    **Interpretación**

    - Cada punto representa un usuario.
    - El color indica el cluster asignado por K-Means.
    - Las X rojas representan los centroides de cada cluster.
    """)
    
def show_business_interpretation(interpretation_text):
    st.header("5. Interpretación de Negocio por Segmento")
    st.markdown(interpretation_text, unsafe_allow_html=True)

# --- Layout de la aplicación ---
def main():
    st.title("Dashboard de Segmentación de Usuarios (KMeans)")
    
    data = load_data()
    if data is None:
        return

    clustered_data_df = data["clustered_data"]
    profile_df = data["profile"]
    interpretation_text = data["interpretation"]
    
    all_clusters = sorted(profile_df['cluster'].unique())

    st.sidebar.header("Filtros")
    selected_clusters = st.sidebar.multiselect(
        "Seleccione clusters:",
        options=all_clusters,
        default=all_clusters
    )

    # --- Contenido Principal ---
    show_general_visualization(profile_df)
    st.divider()
    
    show_segment_profiling(profile_df)
    st.divider()
    
    show_segment_comparison(profile_df, clustered_data_df, selected_clusters)
    st.divider()

    # NUEVA SECCIÓN AÑADIDA
    show_pca_visualization()
    st.divider()

    show_business_interpretation(interpretation_text)

if __name__ == "__main__":
    main()