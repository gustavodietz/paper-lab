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
    # Resonancia cardiorrespiratoria, HRV y la crítica a la polivagal

    Cuando respiras a unas **6 respiraciones por minuto (~0,1 Hz)**, la
    variabilidad de tu frecuencia cardiaca (HRV) se dispara: las oscilaciones
    del corazón pueden multiplicarse por varias veces respecto a la respiración
    normal. Este notebook explora **por qué** con un modelo de juguete
    interactivo, y usa esa mecánica para entender algo menos obvio: **por qué
    la HRV no es un termómetro directo del "tono vagal"** — que es el corazón
    de la crítica científica a la teoría polivagal.

    El plan:

    1. El lazo del barorreflejo como sistema de control con retardo.
    2. Un modelo mínimo (oscilador forzado) con sliders: busca tu resonancia.
    3. Por qué respirar en resonancia dispara la HRV.
    4. La demostración incómoda: misma fisiología, distinta respiración,
       "tono vagal" medido completamente distinto.
    5. Qué implica esto para la teoría polivagal (y qué sobrevive de ella).
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 1 · El barorreflejo: un termostato con retardo

    La presión arterial se regula con un lazo de retroalimentación negativa:
    los **barorreceptores** (seno carotídeo y arco aórtico) detectan la
    presión, informan al **núcleo del tracto solitario** (NTS) en el tronco
    encefálico, y este ajusta la frecuencia cardiaca por dos vías: el **vago**
    (rápido, frena) y el **simpático** (lento, acelera). El cambio de
    frecuencia cardiaca altera el gasto cardiaco, que altera la presión…
    y vuelta a empezar.

    La clave: el lazo completo tarda en dar la vuelta (conducción nerviosa,
    respuesta del nodo sinusal, dinámica vascular). **Todo lazo de
    retroalimentación negativa con retardo $\tau$ tiende a oscilar
    espontáneamente con un periodo de aproximadamente $2\tau$.** Con un
    retardo total de ~5 s, eso da oscilaciones de ~10 s: **0,1 Hz**, las
    llamadas ondas de Mayer. Esa es la frecuencia natural del sistema — y por
    eso la respiración "resuena" precisamente ahí.
    """
    )
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
    flowchart LR
        BR[Barorreceptores<br/>seno carotídeo + arco aórtico] -->|nervios de Hering y aórtico| NTS[NTS<br/>tronco encefálico]
        NTS -->|vago: rápido, frena| SA[Nodo sinusal]
        NTS -->|simpático: lento, acelera| SA
        SA --> FC[Frecuencia cardiaca]
        FC --> GC[Gasto cardiaco]
        GC --> PA[Presión arterial]
        PA -->|retardo total del lazo ≈ 5 s| BR
        RESP([Respiración]) -.->|presión intratorácica<br/>+ gating vagal RSA| SA
        RESP -.-> PA
    """
    )
    return


@app.cell
def _(mo):
    mo.accordion(
        {
            "🫀 Anatomía: ver láminas (OpenStax, CC BY — se cargan de Wikimedia)": mo.vstack(
                [
                    mo.image(
                        src="https://commons.wikimedia.org/wiki/Special:FilePath/2032_Automatic_Innervation.jpg?width=640",
                        width=560,
                    ),
                    mo.md(
                        "*Inervación autónoma del corazón: vías simpática y "
                        "parasimpática (vago) hasta el nodo sinusal. Fuente: "
                        "OpenStax Anatomy & Physiology, CC BY, via Wikimedia "
                        "Commons.*"
                    ),
                    mo.image(
                        src="https://commons.wikimedia.org/wiki/Special:FilePath/1503_Connections_of_the_Parasympathetic_Nervous_System.jpg?width=640",
                        width=560,
                    ),
                    mo.md(
                        "*Conexiones del sistema parasimpático: el vago (X par) "
                        "y su territorio torácico-abdominal. Fuente: OpenStax "
                        "Anatomy & Physiology, CC BY, via Wikimedia Commons.*"
                    ),
                ]
            )
        }
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 2 · Un modelo mínimo: oscilador forzado

    Tratemos el lazo barorreflejo como un **oscilador amortiguado** con
    frecuencia natural $f_0 = 1/(2\tau)$ y amortiguación $\zeta$, forzado por
    la respiración a frecuencia $f$. La amplitud de la oscilación cardiaca que
    provoca la respiración es la clásica curva de resonancia:

    $$A_{baro}(f) = \frac{G_{baro}}{\sqrt{\left(1 - (f/f_0)^2\right)^2 + \left(2\zeta f/f_0\right)^2}}$$

    A esto se suma la **arritmia sinusal respiratoria (RSA)**: el gating
    directo de la salida vagal por el ciclo respiratorio. El nodo sinusal
    responde al vago como un **filtro paso-bajo**: cuanto más lenta la
    respiración, más completa la respuesta del corazón:

    $$A_{rsa}(f) = \frac{G_{rsa}}{\sqrt{1 + (f/f_c)^2}}$$

    En torno a 0,1 Hz ambos mecanismos, además, se alinean en fase (Lehrer &
    Gevirtz, 2014) — aquí los sumamos directamente como aproximación.

    **Es un modelo de juguete**: lineal, estacionario, sin ruido. Pero captura
    lo esencial: por qué existe una frecuencia privilegiada y de qué depende.

    ### Juega con el sistema
    """
    )
    return


@app.cell
def _(mo):
    rpm = mo.ui.slider(3.0, 20.0, value=6.0, step=0.5, label="🌬️ Frecuencia respiratoria (resp/min)")
    tau = mo.ui.slider(2.5, 8.0, value=5.0, step=0.25, label="⏱️ Retardo del lazo barorreflejo τ (s)")
    zeta = mo.ui.slider(0.10, 1.0, value=0.35, step=0.05, label="🌊 Amortiguación ζ")
    g_baro = mo.ui.slider(2.0, 15.0, value=8.0, step=0.5, label="⚙️ Ganancia barorrefleja (lpm)")
    g_rsa = mo.ui.slider(0.0, 10.0, value=4.0, step=0.5, label="🧠 Ganancia vagal RSA (lpm)")
    mo.vstack([rpm, tau, zeta, g_baro, g_rsa])
    return g_baro, g_rsa, rpm, tau, zeta


@app.cell
def _(g_baro, g_rsa, tau, zeta):
    import numpy as np

    F_CORTE_RSA = 0.1  # Hz, paso-bajo del efector vagal en el nodo sinusal

    def amplitudes(f_hz):
        """Amplitud (lpm) de la oscilación cardiaca a frecuencia respiratoria f_hz."""
        f0 = 1.0 / (2.0 * tau.value)
        razon = f_hz / f0
        a_baro = g_baro.value / np.sqrt(
            (1.0 - razon**2) ** 2 + (2.0 * zeta.value * razon) ** 2
        )
        a_rsa = g_rsa.value / np.sqrt(1.0 + (f_hz / F_CORTE_RSA) ** 2)
        return a_baro, a_rsa

    return amplitudes, np


@app.cell
def _(amplitudes, np, rpm, tau):
    import pandas as pd

    f_actual_hz = rpm.value / 60.0
    f0_hz = 1.0 / (2.0 * tau.value)

    rejilla_rpm = np.linspace(2.0, 20.0, 250)
    a_baro_g, a_rsa_g = amplitudes(rejilla_rpm / 60.0)
    curva_df = pd.concat(
        [
            pd.DataFrame({"resp/min": rejilla_rpm, "amplitud (lpm)": a_baro_g, "componente": "barorreflejo (resonancia)"}),
            pd.DataFrame({"resp/min": rejilla_rpm, "amplitud (lpm)": a_rsa_g, "componente": "RSA (paso-bajo vagal)"}),
            pd.DataFrame({"resp/min": rejilla_rpm, "amplitud (lpm)": a_baro_g + a_rsa_g, "componente": "total"}),
        ],
        ignore_index=True,
    )

    a_baro_act, a_rsa_act = amplitudes(f_actual_hz)
    amplitud_actual = float(a_baro_act + a_rsa_act)
    return amplitud_actual, curva_df, f0_hz, f_actual_hz, pd


@app.cell
def _(curva_df, mo, pd, rpm):
    import altair as alt

    base = (
        alt.Chart(curva_df)
        .mark_line()
        .encode(
            x=alt.X("resp/min", title="Frecuencia respiratoria (resp/min)"),
            y=alt.Y("amplitud (lpm)", title="Amplitud de la oscilación cardiaca (lpm)"),
            color=alt.Color("componente", title=""),
            strokeDash=alt.condition(
                alt.datum.componente == "total", alt.value([0]), alt.value([6, 4])
            ),
        )
    )
    marcador = (
        alt.Chart(pd.DataFrame({"x": [rpm.value]}))
        .mark_rule(color="#888", strokeDash=[2, 2])
        .encode(x="x")
    )
    mo.vstack(
        [
            mo.md("**Curva de resonancia** — la línea vertical es tu frecuencia respiratoria actual:"),
            (base + marcador).properties(width=560, height=340),
        ]
    )
    return (alt,)


@app.cell
def _(alt, amplitudes, f_actual_hz, mo, np, pd, rpm):
    t = np.linspace(0.0, 60.0, 1200)
    a_b, a_r = amplitudes(f_actual_hz)
    respiracion = np.sin(2.0 * np.pi * f_actual_hz * t)
    fc = 65.0 + float(a_b + a_r) * np.sin(2.0 * np.pi * f_actual_hz * t)

    serie_df = pd.concat(
        [
            pd.DataFrame({"t (s)": t, "valor": 65.0 + 10.0 * respiracion, "señal": "respiración (escalada)"}),
            pd.DataFrame({"t (s)": t, "valor": fc, "señal": "frecuencia cardiaca (lpm)"}),
        ],
        ignore_index=True,
    )
    grafico_serie = (
        alt.Chart(serie_df)
        .mark_line()
        .encode(
            x=alt.X("t (s)", title="Tiempo (s)"),
            y=alt.Y("valor", title="lpm", scale=alt.Scale(zero=False)),
            color=alt.Color("señal", title=""),
        )
        .properties(width=560, height=260)
    )
    mo.vstack(
        [
            mo.md(f"**Tacograma simulado** a {rpm.value:g} resp/min:"),
            grafico_serie,
        ]
    )
    return


@app.cell
def _(amplitud_actual, f0_hz, mo, rpm):
    en_resonancia = abs(rpm.value - f0_hz * 60.0) < 0.75
    mo.hstack(
        [
            mo.stat(
                value=f"{f0_hz * 60.0:.1f} resp/min",
                label="Tu frecuencia de resonancia (según τ)",
                caption="f₀ = 1/(2τ) — varía entre personas: por eso el biofeedback la busca individualmente",
            ),
            mo.stat(
                value=f"{amplitud_actual:.1f} lpm",
                label="Amplitud de oscilación cardiaca",
                caption="pico de la onda del tacograma",
            ),
            mo.stat(
                value=f"{amplitud_actual / (2**0.5):.1f} lpm",
                label="≈ SDNN del tacograma",
                caption="desviación típica de una sinusoide = A/√2",
                bordered=en_resonancia,
            ),
        ],
        widths="equal",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 3 · Por qué respirar en resonancia dispara la HRV

    Tres cosas que puedes comprobar con los sliders de arriba:

    - **El pico está donde está el retardo.** Mueve $\tau$: la frecuencia de
      resonancia se desplaza. Con τ ≈ 5 s cae en ~6 resp/min. Personas con
      lazos más lentos o rápidos resuenan a otra frecuencia — por eso los
      protocolos de biofeedback de HRV (Lehrer, Vaschillo) **buscan** la
      frecuencia de cada persona entre ~4,5 y 7 resp/min en vez de asumirla.

    - **Dos mecanismos suman.** A ~0,1 Hz coinciden (a) la resonancia del lazo
      barorreflejo y (b) la zona donde el filtro paso-bajo vagal aún deja
      pasar casi toda la RSA. Además llegan **en fase**: el pico de cada uno
      empuja en el mismo sentido. A 15 resp/min, en cambio, la RSA está
      atenuada y el barorreflejo ni se entera.

    - **Menos amortiguación, más pico.** Baja $\zeta$ y la resonancia se
      afila. En fisiología real, un barorreflejo con buena ganancia se
      comporta como un sistema poco amortiguado — y la práctica repetida de
      respiración en resonancia parece **entrenar** esa ganancia
      barorrefleja, que es uno de los mecanismos propuestos de sus efectos
      clínicos (hipertensión, ansiedad, depresión).

    La consecuencia: la HRV enorme de la respiración lenta **no indica un
    estado vagal extraordinario**. Indica que estás empujando un columpio
    exactamente a su frecuencia natural. El columpio (el lazo) es el mismo;
    lo que cambia es cuándo empujas.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 4 · La demostración incómoda: mismo vago, distinta medida

    Fija los sliders de ganancia (tu "fisiología") y compara la HRV medida
    respirando a 6 y a 15 resp/min. **Nada del sistema nervioso ha cambiado
    entre las dos columnas** — solo el ritmo respiratorio:
    """
    )
    return


@app.cell
def _(amplitudes, mo):
    a_b6, a_r6 = amplitudes(6.0 / 60.0)
    a_b15, a_r15 = amplitudes(15.0 / 60.0)
    sdnn_6 = float(a_b6 + a_r6) / (2**0.5)
    sdnn_15 = float(a_b15 + a_r15) / (2**0.5)
    mo.hstack(
        [
            mo.stat(
                value=f"{sdnn_6:.1f} lpm",
                label="HRV (≈SDNN) a 6 resp/min",
                caption="misma fisiología",
            ),
            mo.stat(
                value=f"{sdnn_15:.1f} lpm",
                label="HRV (≈SDNN) a 15 resp/min",
                caption="misma fisiología",
            ),
            mo.stat(
                value=f"×{sdnn_6 / max(sdnn_15, 1e-9):.1f}",
                label="Ratio",
                caption="'tono vagal' aparente multiplicado solo con cambiar el ritmo",
            ),
        ],
        widths="equal",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 5 · Qué implica esto para la teoría polivagal

    La teoría polivagal (Porges) descansa, entre otras, sobre dos premisas
    que este modelo ayuda a examinar:

    **Premisa A: la RSA/HRV como índice del "vago ventral".** La teoría trata
    la amplitud de la RSA como lectura del estado del complejo vagal ventral
    (y por extensión, del "estado de seguridad" social del organismo). Pero
    acabas de ver que la medida depende masivamente de la **mecánica
    respiratoria y de la resonancia del lazo barorreflejo**: puedes
    multiplicar tu RSA sin que cambie la actividad vagal tónica, solo
    cambiando frecuencia (y profundidad) de respiración. Grossman & Taylor
    (2007) documentaron esto empíricamente mucho antes de que fuera cómodo
    decirlo: **RSA y tono vagal cardiaco no son la misma cosa**, y comparar
    RSA entre personas o estados sin controlar la respiración es
    ininterpretable.

    **Premisa B: la filogenia.** El argumento evolutivo central — el vago
    mielinizado "inteligente" como innovación exclusiva de mamíferos, ligada
    al sistema de compromiso social — resultó ser empíricamente falso:
    peces pulmonados (Monteiro et al., 2018, *Science Advances*) presentan
    fibras vagales cardiacas **mielinizadas** y un acoplamiento
    cardiorrespiratorio funcionalmente análogo a la RSA. La revisión de
    Grossman (2023) recorre las cinco premisas fundacionales y argumenta que
    ninguna se sostiene en la evidencia actual.

    **Qué sobrevive.** La crítica no dice que el vago no importe, ni que la
    respiración lenta no funcione — funciona, y este notebook muestra el
    mecanismo (resonancia + barorreflejo) que **basta** para explicarlo sin
    necesidad de la superestructura polivagal. Lo que cae es la lectura
    inversa: *"HRV alta ⇒ estado ventral-vagal de seguridad"*. El sensor de
    HRV mide la mecánica de un lazo de control; inferir de ahí un estado
    socioemocional concreto es saltarse varios pasos que la evidencia no
    cubre.
    """
    )
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
    flowchart TD
        subgraph medido["Lo que el sensor mide"]
            RESP2([ritmo y profundidad<br/>respiratoria]) --> HRV[amplitud HRV / RSA]
            BARO[resonancia del lazo<br/>barorreflejo] --> HRV
            VAGO[actividad vagal<br/>tónica] --> HRV
        end
        subgraph inferido["Lo que la polivagal infiere"]
            HRV -.->|salto no justificado| ESTADO[estado ventral-vagal<br/>de 'seguridad social']
        end
        style ESTADO stroke-dasharray: 5 5
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ---
    ### Referencias

    - Lehrer, P. M., & Gevirtz, R. (2014). Heart rate variability biofeedback:
      how and why does it work? *Frontiers in Psychology*, 5, 756.
    - Vaschillo, E., Lehrer, P., Rishe, N., & Konstantinov, M. (2002). Heart
      rate variability biofeedback as a method for assessing baroreflex
      function. *Applied Psychophysiology and Biofeedback*, 27(1), 1–27.
    - Grossman, P., & Taylor, E. W. (2007). Toward understanding respiratory
      sinus arrhythmia: relations to cardiac vagal tone, evolution and
      biobehavioral functions. *Biological Psychology*, 74(2), 263–285.
    - Monteiro, D. A., et al. (2018). Cardiorespiratory interactions
      previously identified as mammalian are present in the primitive
      lungfish. *Science Advances*, 4(2), eaaq0800.
    - Grossman, P. (2023). Fundamental challenges and likely refutations of
      the five basic premises of the polyvagal theory. *Biological
      Psychology*, 180, 108589.

    *Modelo y texto: notebook de exploración personal; el modelo es
    deliberadamente mínimo y no sustituye a los modelos fisiológicos serios
    (deBoer, Ottesen) del lazo barorreflejo.*
    """
    )
    return


if __name__ == "__main__":
    app.run()
