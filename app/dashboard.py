import pandas as pd
import plotly.express as px
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
import streamlit as st

from app.stats import category_stats, price_zscores, run_benchmark
from gamescout.database import get_engine
from gamescout.models import Product


def load_data() -> pd.DataFrame:
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Product).options(joinedload(Product.type))
        products = session.exec(statement).all()

        data = []
        for p in products:
            data.append(
                {
                    "product_id": p.product_id,
                    "title": p.title,
                    "price_eur": p.price_eur,
                    "type_id": p.type_id if p.type_id else 0,
                    "type_name": p.type.name if p.type else "Sin tipo",
                }
            )
        return pd.DataFrame(data)


def main() -> None:
    st.set_page_config(page_title="GameScout Prueba Dashboard", layout="wide")
    st.title("GameScout Prueba Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No hay datos cargados en la base de datos.")
        return

    st.sidebar.header("Filtros")

    all_types = sorted(df["type_name"].unique().tolist())
    selected_types = st.sidebar.multiselect(
        "Filtrar por tipo",
        options=all_types,
        default=[],
    )

    min_p = float(df["price_eur"].min())
    max_p = float(df["price_eur"].max())
    price_range = st.sidebar.slider(
        "Rango de precio (€)",
        min_value=min_p,
        max_value=max_p,
        value=(min_p, max_p),
    )

    search_query = st.sidebar.text_input("Buscar por titulo", value="")

    filtered_df = df.copy()

    if selected_types:
        filtered_df = filtered_df[filtered_df["type_name"].isin(selected_types)]

    filtered_df = filtered_df[
        (filtered_df["price_eur"] >= price_range[0])
        & (filtered_df["price_eur"] <= price_range[1])
    ]

    if search_query.strip():
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(search_query, case=False, na=False)
        ]

    st.subheader("Visualizaciones")
    col1, col2 = st.columns(2)

    with col1:
        st.write("Top 10 productos mas caros")
        top10 = filtered_df.nlargest(10, "price_eur").sort_values("price_eur", ascending=True)
        fig_bar = px.bar(
            top10,
            x="price_eur",
            y="title",
            orientation="h",
            labels={"price_eur": "Precio (€)", "title": "Producto"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.write("Distribucion de precios")
        fig_hist = px.histogram(
            filtered_df,
            x="price_eur",
            nbins=15,
            labels={"price_eur": "Precio (€)"},
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.write("Precio promedio por categoria")
    avg_price = (
        filtered_df.groupby("type_name")["price_eur"]
        .mean()
        .reset_index()
        .sort_values("price_eur", ascending=False)
    )
    fig_avg = px.bar(
        avg_price,
        x="type_name",
        y="price_eur",
        labels={"type_name": "Categoria", "price_eur": "Precio Promedio (€)"},
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    st.write("Productos filtrados")
    display_df = filtered_df.copy()
    display_df["precio_formateado"] = display_df["price_eur"].apply(lambda x: f"{x:.2f} €")
    st.dataframe(
        display_df[["product_id", "title", "type_name", "precio_formateado"]],
        use_container_width=True,
    )

    st.divider()
    st.header("Calculos con Numba")

    prices = df["price_eur"].to_numpy(dtype=float)
    type_ids = df["type_id"].to_numpy(dtype=int)

    u_types, counts, mins, maxs, means, stds = category_stats(prices, type_ids)

    id_to_name = dict(zip(df["type_id"], df["type_name"]))
    type_names_res = [id_to_name.get(t, "Sin tipo") for t in u_types]

    stats_df = pd.DataFrame(
        {
            "Categoria": type_names_res,
            "Cantidad": counts,
            "Minimo (€)": mins,
            "Maximo (€)": maxs,
            "Promedio (€)": means,
            "Desviacion Estandar (€)": stds,
        }
    )
    st.write("Resumen estadistico por categoria")
    st.dataframe(stats_df, use_container_width=True)

    st.write("Seccion de Outliers / Ofertas")
    z_threshold = st.slider("Umbral de Z-Score", min_value=1.0, max_value=4.0, value=2.0, step=0.1)

    z_scores_all = price_zscores(prices, type_ids)
    df_outliers = df.copy()
    df_outliers["z_score"] = z_scores_all

    outliers = df_outliers[df_outliers["z_score"].abs() > z_threshold]
    st.write(f"Productos con Z-Score > {z_threshold}:")
    st.dataframe(
        outliers[["product_id", "title", "type_name", "price_eur", "z_score"]],
        use_container_width=True,
    )

    st.write("Benchmark (Python puro vs Numba)")
    st.caption("Primera llamada de compilacion descartada para la medicion.")

    bench_results = run_benchmark(prices, type_ids)

    b_col1, b_col2, b_col3 = st.columns(3)
    b_col1.metric("Tiempo Python Puro", f"{bench_results['python_time_sec'] * 1000:.3f} ms")
    b_col2.metric("Tiempo Numba", f"{bench_results['numba_time_sec'] * 1000:.3f} ms")
    b_col3.metric("Aceleracion", f"{bench_results['speedup']:.2f}x")


if __name__ == "__main__":
    main()