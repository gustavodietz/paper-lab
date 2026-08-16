# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
#     "pandas",
#     "altair",
# ]
# ///

import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # Regresión a la media

    Notebook de ejemplo del flujo de este repo: leer un paper, no terminar de
    creerse (o de entender) un resultado, y comprobarlo con datos sintéticos.

    Aquí simulamos un test y un retest correlacionados y comprobamos el clásico:
    **el peor grupo en el test "mejora" en el retest sin que nadie haya
    intervenido.** Mueve los sliders y observa cómo el efecto depende de la
    correlación: cuanto más ruido (menor $r$), mayor la falsa mejora.
    """
    )
    return


@app.cell
def _(mo):
    r = mo.ui.slider(0.0, 0.95, value=0.4, step=0.05, label="Correlación test–retest (r)")
    n = mo.ui.slider(200, 5000, value=1000, step=100, label="Sujetos (n)")
    mo.vstack([r, n])
    return n, r


@app.cell
def _(n, r):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(42)
    muestras = rng.multivariate_normal(
        mean=[0.0, 0.0],
        cov=[[1.0, r.value], [r.value, 1.0]],
        size=n.value,
    )
    df = pd.DataFrame(muestras, columns=["test", "retest"])
    df["grupo"] = np.where(
        df["test"] <= df["test"].quantile(0.2), "peor 20% en el test", "resto"
    )
    return (df,)


@app.cell
def _(df, mo):
    resumen = (
        df.groupby("grupo")[["test", "retest"]]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"test": "media en test", "retest": "media en retest"})
    )
    mo.vstack(
        [
            mo.md(
                "El peor 20% en el test mejora en el retest sin intervención "
                "alguna — pura regresión a la media:"
            ),
            mo.ui.table(resumen, selection=None),
        ]
    )
    return


@app.cell
def _(df, mo):
    import altair as alt

    grafico = (
        alt.Chart(df)
        .mark_circle(opacity=0.4)
        .encode(
            x=alt.X("test", title="Puntuación en el test"),
            y=alt.Y("retest", title="Puntuación en el retest"),
            color=alt.Color("grupo", title=""),
        )
        .properties(width=520, height=380)
    )
    mo.ui.altair_chart(grafico)
    return


if __name__ == "__main__":
    app.run()
