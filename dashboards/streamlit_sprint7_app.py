from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


@st.cache_data(show_spinner=False)
def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    df = pd.read_csv(path)
    if "cluster" not in df.columns:
        raise ValueError("El dataset debe incluir una columna 'cluster'")
    return df


@st.cache_data(show_spinner=False)
def load_profile(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    return pd.read_csv(path)


def pick_numeric_features(df: pd.DataFrame, exclude: set[str]) -> list[str]:
    cols: list[str] = []
    for c in df.columns:
        if c in exclude:
            continue
        # object/string types are ignored
        if df[c].dtype == "O":
            continue
        # numeric coercion sanity check
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().any():
            cols.append(c)
    return cols


def main() -> None:
    st.set_page_config(page_title="E3 Segmentación — Dashboard (Sprint 7)", layout="wide")

    st.title("E3 Segmentación de usuarios — KMeans (Dashboard)")
    st.markdown(
        "Este dashboard utiliza el dataset enriquecido con `cluster` generado en Sprint 5 y una interpretación por cluster en Sprint 6. "
        "Incluye filtros y comparaciones para análisis orientado a negocio."
    )

    dataset_path = DATA_DIR / "dataset_consolidado_con_cluster_sprint5.csv"
    profile_path = DATA_DIR / "cluster_profile_sprint6.csv"

    df = load_dataset(dataset_path)
    profile = load_profile(profile_path)

    exclude = {"user_id"}

    feature_cols = pick_numeric_features(df, exclude=exclude)
    feature_cols = [c for c in feature_cols if c != "cluster"]

    clusters = sorted(df["cluster"].unique().tolist())

    st.sidebar.header("Filtros")
    selected_clusters = st.sidebar.multiselect(
        "Cluster(s)",
        options=clusters,
        default=clusters,
    )

    df_sel = df[df["cluster"].isin(selected_clusters)].copy()

    # ======================
    # Visualización general
    # ======================
    st.subheader("Visualización general")
    total = len(df)
    counts = df["cluster"].value_counts().reindex(selected_clusters)
    pct = (counts / total * 100.0).round(2)

    general_tbl = pd.DataFrame(
        {
            "cluster": counts.index.astype(int),
            "count": counts.values.astype(int),
            "pct": pct.values,
        }
    )
    st.dataframe(general_tbl, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.bar_chart(general_tbl.set_index("cluster")["count"], use_container_width=True)
    with c2:
        st.bar_chart(general_tbl.set_index("cluster")["pct"], use_container_width=True)

    # ==========================
    # Perfilamiento por segmento
    # ==========================
    st.subheader("Perfilamiento por segmento")
    if selected_clusters:
        st_profile = profile[profile["cluster"].isin(selected_clusters)]
    else:
        st_profile = profile

    st.dataframe(st_profile, use_container_width=True, hide_index=True)

    # ==============================
    # Comparación entre clusters
    # ==============================
    st.subheader("Comparación entre clusters")

    # Heatmap simple con matplotlib (evita plotly)
    mean_feature_cols = [c for c in profile.columns if c.endswith("_mean")]
    if len(mean_feature_cols) > 0:
        top_n = min(12, len(mean_feature_cols))
        mean_feature_cols = mean_feature_cols[:top_n]

        heat_df = profile[profile["cluster"].isin(selected_clusters)][["cluster"] + mean_feature_cols].copy()
        heat_long = heat_df.melt(id_vars=["cluster"], var_name="feature", value_name="mean")
        heat_long["feature"] = heat_long["feature"].str.replace("_mean", "", regex=False)

        import matplotlib.pyplot as plt

        pivot = heat_long.pivot_table(
            index="feature",
            columns="cluster",
            values="mean",
            aggfunc="mean",
        )
        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.imshow(pivot.values, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([str(c) for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index.tolist())
        ax.set_title(f"Heatmap (medias) — Top {top_n} variables")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No se encontró información de medias en `cluster_profile_sprint6.csv`.")

    # Boxplot de una variable
    if feature_cols:
        selected_feature = st.selectbox(
            "Elegir variable para comparar distribución",
            options=feature_cols,
            index=0,
        )

        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.boxplot(data=df_sel, x="cluster", y=selected_feature, ax=ax)
        ax.set_title(f"Distribución de: {selected_feature}")
        st.pyplot(fig, use_container_width=True)

    else:
        st.info("No hay suficientes variables numéricas para boxplot.")

    # ==============================
    # Interacción avanzada (scatter)
    # ==============================
    st.subheader("Exploración avanzada")
    if len(feature_cols) >= 2:
        c_x = st.selectbox("Eje X", options=feature_cols, index=0)
        c_y = st.selectbox("Eje Y", options=feature_cols, index=1)

        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(7, 5))
        sns.scatterplot(data=df_sel, x=c_x, y=c_y, hue="cluster", ax=ax)
        ax.set_title(f"Scatter: {c_x} vs {c_y}")
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No hay suficientes variables numéricas para scatter.")

    # ==============================
    # Lectura de negocio
    # ==============================
    st.subheader("Lectura de negocio (Sprint 6)")
    report_path = DOCS_DIR / "sprint6_cluster_interpretation.md"
    if report_path.exists():
        st.markdown(report_path.read_text(encoding="utf-8"))
    else:
        st.info("No se encontró el reporte de Sprint 6 para mostrar la interpretación.")


if __name__ == "__main__":
    main()

