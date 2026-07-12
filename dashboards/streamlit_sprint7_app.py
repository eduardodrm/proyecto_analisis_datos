from pathlib import Path

import json

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



@st.cache_data(show_spinner=False)
def load_metrics_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_elbow_png(path: Path) -> bytes | None:
    # Streamlit puede mostrar bytes con st.image
    if not path.exists():
        return None
    return path.read_bytes()





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
    st.set_page_config(page_title="E3 Segmentación — Dashboard (Sprint 11)", layout="wide")

    st.title("E3 Segmentación de usuarios — KMeans (Dashboard Sprint 11)")

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
    # ==============================
    # Sprint 11: PCA / Elbow-Silhouette / Radar
    # ==============================
    st.subheader("Sprint 11 — PCA, Elbow/Silhouette y radar")

    # -----------
    # PCA (2D)
    # -----------
    st.markdown("### PCA por cluster (2 componentes)")
    from sklearn.decomposition import PCA
    import numpy as np

    pca_cols = [c for c in feature_cols if c in df.columns]
    pca_cols = pca_cols[: min(len(pca_cols), 10)]  # evita gráficos pesados

    if len(pca_cols) >= 2:
        X = df_sel[pca_cols].copy()
        X = X.apply(pd.to_numeric, errors="coerce")
        X = X.fillna(X.median(numeric_only=True))

        pca = PCA(n_components=2, random_state=42)
        comps = pca.fit_transform(X.values)

        pca_df = pd.DataFrame(comps, columns=["PC1", "PC2"])
        pca_df["cluster"] = df_sel["cluster"].values

        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=pca_df, x="PC1", y="PC2", hue="cluster", ax=ax)
        ax.set_title(
            f"PCA (2D) — PC1: {pca.explained_variance_ratio_[0]:.2%}, PC2: {pca.explained_variance_ratio_[1]:.2%}"
        )
        st.pyplot(fig, use_container_width=True)

        with st.expander("Ver variables usadas en PCA"):
            st.write(pca_cols)
    else:
        st.info("No hay suficientes variables numéricas para PCA (mínimo 2).")

    # -----------------
    # Elbow y Silhouette
    # -----------------
    st.markdown("### Elbow y Silhouette")
    metrics_json_path = DOCS_DIR / "sprint4_kmeans_metrics.json"
    elbow_png_path = DOCS_DIR / "sprint4_elbow.png"

    if metrics_json_path.exists():
        metrics_obj = load_metrics_json(metrics_json_path)
        metrics_list = metrics_obj.get("metrics", [])

        if metrics_list:
            mdf = pd.DataFrame(metrics_list)
            best_k = metrics_obj.get("best_k")

            c1, c2 = st.columns(2)
            with c1:
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(mdf["k"], mdf["inertia"], marker="o")
                if best_k is not None:
                    ax.axvline(best_k, color="red", linestyle="--", alpha=0.7)
                ax.set_title("Elbow (Inertia)")
                ax.set_xlabel("k")
                ax.set_ylabel("inertia")
                st.pyplot(fig, use_container_width=True)

            with c2:
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(mdf["k"], mdf["silhouette_score"], marker="o")
                if best_k is not None:
                    ax.axvline(best_k, color="red", linestyle="--", alpha=0.7)
                ax.set_title("Silhouette")
                ax.set_xlabel("k")
                ax.set_ylabel("silhouette_score")
                st.pyplot(fig, use_container_width=True)

            if elbow_png_path.exists():
                with st.expander("Ver Elbow PNG generado (si existe)"):
                    st.image(str(elbow_png_path), use_container_width=True)
        else:
            st.info("No se encontró lista 'metrics' en sprint4_kmeans_metrics.json")
    else:
        st.info("No se encontró docs/sprint4_kmeans_metrics.json")

    # -----------
    # Radar chart
    # -----------
    st.markdown("### Radar chart (perfil comparado)")
    mode = st.radio("Medida", options=["mean", "median"], index=0, horizontal=True)
    top_n = st.slider("Top N variables", min_value=3, max_value=20, value=8, step=1)

    stat_suffix = f"_{mode}"
    base_feature_cols = [c for c in profile.columns if c.endswith(stat_suffix)]
    base_feature_cols = [c[: -len(stat_suffix)] for c in base_feature_cols]
    # dedupe y orden estable
    seen = set()
    base_feature_cols_unique: list[str] = []
    for b in base_feature_cols:
        if b not in seen:
            seen.add(b)
            base_feature_cols_unique.append(b)

    if base_feature_cols_unique:
        # tomar top_n por varianza entre clusters (mejor para radar)
        radar_df = profile[profile["cluster"].isin(selected_clusters)].copy()
        # construir matriz de valores por cluster para cada variable
        radar_vars = []
        for v in base_feature_cols_unique:
            col = f"{v}{stat_suffix}"
            if col in radar_df.columns:
                radar_vars.append((v, col))

        if radar_vars:
            var_scores = []
            for v, col in radar_vars:
                s = pd.to_numeric(radar_df[col], errors="coerce")
                if s.notna().any():
                    var_scores.append((v, float(s.var(skipna=True))))
            var_scores = sorted(var_scores, key=lambda x: x[1], reverse=True)
            chosen = [v for v, _ in var_scores[:top_n]]

            # normalizar 0..1 para radar
            vals = {}
            for v in chosen:
                col = f"{v}{stat_suffix}"
                x = pd.to_numeric(radar_df[col], errors="coerce")
                minv = float(x.min(skipna=True))
                maxv = float(x.max(skipna=True))
                denom = max(maxv - minv, 1e-12)
                vals[v] = ((x - minv) / denom).fillna(0.0).values

            import matplotlib.pyplot as plt
            import numpy as np

            clusters_for_radar = radar_df["cluster"].tolist()
            angles = np.linspace(0, 2 * np.pi, len(chosen), endpoint=False).tolist()
            angles += angles[:1]

            fig = plt.figure(figsize=(8, 6))
            ax = plt.subplot(111, polar=True)
            for i, cid in enumerate(clusters_for_radar):
                data = [vals[v][i] for v in chosen]
                data += data[:1]
                ax.plot(angles, data, linewidth=2, label=str(cid))
                ax.fill(angles, data, alpha=0.1)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(chosen, fontsize=9)
            ax.set_title(f"Radar — {mode} (normalizado) | Top {len(chosen)} variables")
            ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.10))
            st.pyplot(fig, use_container_width=True)

        else:
            st.info("No hay columnas para construir radar con el sufijo seleccionado.")
    else:
        st.info("No se encontraron variables para radar (mean/median) en cluster_profile_sprint6.csv")

    # ==============================
    # Lectura de negocio (Sprint 6)
    # ==============================
    st.subheader("Lectura de negocio (Sprint 6)")
    report_path = DOCS_DIR / "sprint6_cluster_interpretation.md"
    if report_path.exists():
        st.markdown(report_path.read_text(encoding="utf-8"))
    else:
        st.info("No se encontró el reporte de Sprint 6 para mostrar la interpretación.")


if __name__ == "__main__":
    main()


