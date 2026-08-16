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
    # El barorreflejo en serio: de juguete a deBoer

    El notebook de [resonancia y HRV](../resonancia_hrv_polivagal/) terminaba
    con una nota de honestidad: *"el modelo es deliberadamente de juguete
    (lineal, estacionario) — no sustituye a los modelos fisiológicos serios
    del barorreflejo (deBoer, Ottesen)"*. Este notebook es esa nota
    desplegada: **qué mentiras cuenta el modelo de juguete, y qué se ve
    cuando las quitas.**

    Subiremos una escalera de tres peldaños. En cada uno, el modelo se
    complica un poco y a cambio **explica algo que el anterior solo podía
    suponer**:
    """
    )
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
    flowchart LR
        A["🧸 Juguete<br/>oscilador lineal forzado<br/><i>supone la resonancia</i>"]
        B["🔁 Ottesen (1997)<br/>retroalimentación con retardo<br/><i>la resonancia <b>emerge</b></i>"]
        C["🫀 deBoer (1987)<br/>latido a latido<br/><i>el espectro LF/HF <b>emerge</b></i>"]
        D["🏥 Modelos completos<br/>Ursino, pulsátiles, 3D…"]
        A --> B --> C -.-> D
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 0 · Las tres mentiras del modelo de juguete

    El oscilador forzado del notebook anterior era útil, pero hacía trampas:

    1. **La resonancia estaba puesta a mano.** Escribimos $f_0 = 1/(2\tau)$
       en el modelo. No demostramos que un lazo con retardo oscile a esa
       frecuencia: lo *decretamos*.
    2. **Era lineal.** Duplicar la ganancia duplicaba la amplitud, hasta el
       infinito. La fisiología real satura: los barorreceptores tienen una
       curva sigmoidea, no una recta.
    3. **Era continuo y estacionario.** Pero el corazón *late*: la presión
       solo puede ajustar el ritmo una vez por latido. El sistema se muestrea
       a sí mismo a frecuencia variable — y eso deja huellas en el espectro.

    Cada peldaño de la escalera elimina una mentira.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 1 · Peldaño Ottesen: la resonancia emerge

    Ottesen (1997) modeló el barorreflejo como **ecuaciones diferenciales con
    retardo** (DDE). Nuestra versión mínima tiene dos variables — presión
    arterial media $P$ y frecuencia cardiaca $H$ — y tres ingredientes:

    **① La bañera (windkessel).** Las arterias son un depósito elástico: el
    corazón mete sangre ($H \cdot V_s$, latidos por minuto × volumen por
    latido) y la periferia la deja escapar ($P/R$):

    $$C\,\frac{dP}{dt} = \frac{H}{60}\,V_s - \frac{P}{R}$$

    **② La sigmoide barorrefleja.** Los barorreceptores no responden en línea
    recta: por debajo de su rango no disparan, por encima saturan. La
    actividad simpática **baja** con la presión y la vagal **sube**:

    $$s(P) = \frac{1}{1+(P/P_{50})^{k}} \qquad v(P) = \frac{1}{1+(P_{50}/P)^{k}}$$

    La pendiente en el centro es la **ganancia barorrefleja** — exactamente
    lo que el biofeedback de HRV parece entrenar.

    **③ Los dos brazos, con sus tiempos reales.** El vago (mielinizado,
    sináptico rápido) lee la presión *de ahora mismo*: $v(P(t))$. El
    simpático es lento: conducción + norepinefrina + segundos mensajeros
    suman un **retardo** $\tau$, y además su efecto se instala con una
    constante $\tau_H$:

    $$\tau_H\,\frac{dH}{dt} = \underbrace{H_0 + G_s\, s\big(P(t-\tau)\big)}_{\text{acelerador lento y retrasado}} - \underbrace{G_v\, v\big(P(t)\big)}_{\text{freno rápido}} - H$$

    Nada en estas ecuaciones oscila por sí mismo. No hay resonancia escrita,
    no hay $f_0$, no hay respiración. Solo un termostato con un cable lento.
    **Juega:**
    """
    )
    return


@app.cell
def _(mo):
    ot_tau = mo.ui.slider(1.0, 6.0, value=3.5, step=0.25, label="⏱️ Retardo simpático τ (s)")
    ot_gsimp = mo.ui.slider(20.0, 120.0, value=80.0, step=5.0, label="🔥 Ganancia simpática Gₛ")
    ot_gvagal = mo.ui.slider(0.0, 90.0, value=15.0, step=5.0, label="🧊 Ganancia vagal rápida Gᵥ")
    mo.vstack([ot_tau, ot_gsimp, ot_gvagal])
    return ot_gsimp, ot_gvagal, ot_tau


@app.cell
def _(ot_gsimp, ot_gvagal, ot_tau):
    import numpy as np

    OT_DT, OT_DUR = 0.02, 240.0
    OT_C, OT_VS = 1.5, 70.0
    OT_P50, OT_K = 100.0, 7.0
    OT_TAUH = 2.0
    OT_HEQ, OT_PEQ = 70.0, 100.0
    # R y H0 elegidos para que el equilibrio sea exactamente (P=100, H=70)
    # sea cual sea la ganancia: mismo punto fijo, distinta ESTABILIDAD.
    ot_R = OT_PEQ * 60.0 / (OT_HEQ * OT_VS)
    ot_H0 = OT_HEQ - (ot_gsimp.value - ot_gvagal.value) * 0.5

    ot_n = int(OT_DUR / OT_DT)
    ot_d = max(1, int(round(ot_tau.value / OT_DT)))
    ot_P = np.full(ot_n, OT_PEQ + 3.0)  # empezamos 3 mmHg fuera del equilibrio
    ot_H = np.full(ot_n, OT_HEQ)
    for ot_i in range(ot_n - 1):
        ot_pret = ot_P[ot_i - ot_d] if ot_i >= ot_d else ot_P[0]
        ot_s = 1.0 / (1.0 + (ot_pret / OT_P50) ** OT_K)
        ot_v = 1.0 / (1.0 + (OT_P50 / ot_P[ot_i]) ** OT_K)
        ot_hobj = ot_H0 + ot_gsimp.value * ot_s - ot_gvagal.value * ot_v
        ot_H[ot_i + 1] = ot_H[ot_i] + OT_DT * (ot_hobj - ot_H[ot_i]) / OT_TAUH
        ot_P[ot_i + 1] = ot_P[ot_i] + OT_DT * (
            ot_H[ot_i] / 60.0 * OT_VS - ot_P[ot_i] / ot_R
        ) / OT_C
    ot_t = np.arange(ot_n) * OT_DT
    return np, ot_H, ot_P, ot_t


@app.cell
def _(mo, np, ot_H, ot_P, ot_t):
    import altair as alt
    import pandas as pd

    ot_sel = (ot_t >= 60.0)[::4]
    ot_td, ot_Pd, ot_Hd = ot_t[::4][ot_sel], ot_P[::4][ot_sel], ot_H[::4][ot_sel]

    ot_series_df = pd.concat(
        [
            pd.DataFrame({"t (s)": ot_td, "valor": ot_Pd, "señal": "presión (mmHg)"}),
            pd.DataFrame({"t (s)": ot_td, "valor": ot_Hd, "señal": "frec. cardiaca (lpm)"}),
        ],
        ignore_index=True,
    )
    ot_g_series = (
        alt.Chart(ot_series_df)
        .mark_line()
        .encode(
            x=alt.X("t (s)", title="Tiempo (s)"),
            y=alt.Y("valor", title="", scale=alt.Scale(zero=False)),
            color=alt.Color("señal", title=""),
        )
        .properties(width=540, height=220)
    )

    ot_fase_df = pd.DataFrame({"P (mmHg)": ot_Pd, "H (lpm)": ot_Hd, "t": ot_td})
    ot_g_fase = (
        alt.Chart(ot_fase_df)
        .mark_line(opacity=0.75)
        .encode(
            x=alt.X("P (mmHg)", scale=alt.Scale(zero=False)),
            y=alt.Y("H (lpm)", scale=alt.Scale(zero=False)),
            order="t",
            color=alt.Color("t", scale=alt.Scale(scheme="viridis"), legend=None),
        )
        .properties(width=260, height=220, title="Plano de fases (P, H)")
    )

    ot_amp = float((ot_P[ot_t > 150].max() - ot_P[ot_t > 150].min()) / 2.0)
    mo.vstack(
        [
            mo.md(
                f"**Amplitud sostenida de la oscilación de presión: "
                f"{ot_amp:.1f} mmHg** — si es ≈0, el termostato amortigua; "
                "si no, has creado ondas de Mayer:"
            ),
            ot_g_series,
            ot_g_fase,
        ]
    )
    return alt, pd


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            r"""
    **Tres experimentos guiados** (parte de los valores por defecto:
    τ=3,5 · Gₛ=80 · Gᵥ=15, una oscilación suave de ~12 s):

    1. **Crea ondas de Mayer.** Sube Gₛ a 110: la espiral del plano de fases
       se convierte en un **ciclo límite** — oscilación autosostenida de ~0,1
       Hz *sin ninguna entrada oscilante*. Es una bifurcación de Hopf: el
       mismo equilibrio (100 mmHg, 70 lpm) pierde estabilidad.
    2. **El vago como amortiguador.** Con las ondas en marcha, sube Gᵥ a 60:
       mueren. El freno **rápido** (vago mielinizado, sin retardo) estabiliza
       el lazo que el acelerador **lento** desestabiliza. La "ventaja" del
       vago rápido es ingeniería de control, no un estado psicológico.
    3. **Sin retardo no hay música.** Baja τ a 1,5 s: por mucha ganancia que
       pongas, no hay oscilación. Y observa que el *periodo* de las ondas
       sigue al retardo (τ=5 s → ~15 s): la frecuencia de resonancia que el
       juguete decretaba como $1/(2\tau)$, aquí **emerge** de la dinámica.

    Fíjate también en la mentira nº 2 corregida: con Gₛ=110 la amplitud no
    crece hasta el infinito — la **sigmoide satura** y el ciclo límite se
    queda en ~25 mmHg. Los sistemas lineales no saben hacer eso.
    """
        ),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 2 · Peldaño deBoer: el corazón late (y eso importa)

    El modelo de deBoer, Karemaker & Strackee (1987) fue el primero en tomar
    en serio que el barorreflejo opera **latido a latido**: no hay "presión
    en tiempo continuo", hay una sístole $S_n$, un intervalo $I_n$, y vuelta
    a empezar. Cada latido $n$ es un pequeño ciclo causal:

    1. **Decaimiento diastólico (windkessel):** la presión cae
       exponencialmente durante el intervalo previo:
       $D_n = S_{n-1}\, e^{-I_{n-1}/T_n}$, con $T_n$ = constante de tiempo
       arterial **controlada por el simpático** (más vasoconstricción → decae
       más despacio).
    2. **Nueva sístole:** $S_n = D_n + PP_n$, donde el pulso $PP_n$ incluye
       la **restitución** (un intervalo previo largo → más llenado → latido
       más fuerte, ley de Starling), la **respiración** como perturbación
       mecánica directa de amplitud $A$, y un poco de **ruido** fisiológico.
    3. **El barorreflejo responde:** el intervalo siguiente se alarga con la
       presión *efectiva* $S' = S_{ref} + 18\arctan\!\big(\tfrac{S-S_{ref}}{18}\big)$
       (ahí está la sigmoide) por dos vías: la **vagal, dentro del mismo
       latido**, y la **simpática, promediando los latidos 2 a 6 anteriores**:

    $$I_n = I_0 + G_v\,(S'_n - S_{ref}) + G_s\,\big(\overline{S'}_{n-6..n-2} - S_{ref}\big)$$

    Ese promedio retrasado de 2–6 latidos es el retardo simpático de Ottesen,
    ahora en unidades de *latidos*. **Juega** — y prueba sobre todo el
    interruptor:
    """
    )
    return


@app.cell
def _(mo):
    db_rpm = mo.ui.slider(4.0, 20.0, value=15.0, step=0.5, label="🌬️ Frecuencia respiratoria (resp/min)")
    db_aresp = mo.ui.slider(0.0, 6.0, value=3.0, step=0.5, label="💨 Amplitud mecánica de la respiración (mmHg)")
    db_simpatico = mo.ui.switch(value=True, label="🔥 Brazo simpático lento (retardo de 2–6 latidos)")
    mo.vstack([db_rpm, db_aresp, db_simpatico])
    return db_aresp, db_rpm, db_simpatico


@app.cell
def _(np):
    def db_simula(rpm, a_resp, con_simpatico, n_lat=700, semilla=7):
        """Mini-deBoer: devuelve (tiempos, sistólicas, intervalos RR)."""
        S_REF, I0, T0 = 120.0, 0.8, 1.8
        G_V, G_S = 0.005, 0.010      # s/mmHg (vagal, simpático)
        G_T = 0.02                   # control simpático del windkessel
        RHO = 30.0                   # restitución (mmHg por s de intervalo)
        RUIDO = 1.0                  # mmHg
        PP0 = S_REF * (1.0 - np.exp(-I0 / T0))
        rng = np.random.default_rng(semilla)
        f_r = rpm / 60.0

        S = np.full(n_lat, S_REF)
        I = np.full(n_lat, I0)
        t = np.zeros(n_lat)

        def efectiva(x):
            return S_REF + 18.0 * np.arctan((x - S_REF) / 18.0)

        for n in range(1, n_lat):
            t[n] = t[n - 1] + I[n - 1]
            if con_simpatico and n >= 7:
                s_lento = np.mean(efectiva(S[n - 6:n - 1])) - S_REF
            else:
                s_lento = 0.0
            T_n = T0 - G_T * s_lento
            D = S[n - 1] * np.exp(-I[n - 1] / T_n)
            PP = (
                PP0
                + RHO * (I[n - 1] - I0)
                + a_resp * np.sin(2.0 * np.pi * f_r * t[n])
                + RUIDO * rng.standard_normal()
            )
            S[n] = D + PP
            I[n] = I0 + G_V * (efectiva(S[n]) - S_REF) + G_S * s_lento
            I[n] = max(I[n], 0.3)
        return t, S, I

    def db_espectro(t, I, descartar=100):
        """PSD del tacograma, remuestreado a 4 Hz."""
        t2, I2 = t[descartar:], I[descartar:]
        fs = 4.0
        tt = np.arange(t2[0], t2[-1], 1.0 / fs)
        rr = np.interp(tt, t2, I2)
        rr = rr - rr.mean()
        esp = np.abs(np.fft.rfft(rr * np.hanning(len(rr)))) ** 2
        f = np.fft.rfftfreq(len(rr), 1.0 / fs)
        return f, esp

    return db_espectro, db_simula


@app.cell
def _(db_aresp, db_rpm, db_simpatico, db_simula):
    db_t, db_S, db_I = db_simula(
        db_rpm.value, db_aresp.value, db_simpatico.value
    )
    return db_I, db_S, db_t


@app.cell
def _(alt, db_I, db_t, mo, pd):
    db_taco_df = pd.DataFrame(
        {"t (s)": db_t[100:400], "RR (ms)": db_I[100:400] * 1000.0}
    )
    db_g_taco = (
        alt.Chart(db_taco_df)
        .mark_line(point=alt.OverlayMarkDef(size=6))
        .encode(
            x=alt.X("t (s)", title="Tiempo (s)", scale=alt.Scale(zero=False)),
            y=alt.Y("RR (ms)", scale=alt.Scale(zero=False)),
        )
        .properties(width=540, height=200, title="Tacograma: cada punto es un latido")
    )
    mo.vstack([db_g_taco])
    return


@app.cell
def _(alt, db_I, db_espectro, db_rpm, db_t, mo, np, pd):
    db_f, db_esp = db_espectro(db_t, db_I)
    db_m = (db_f > 0.02) & (db_f < 0.5)
    db_esp_df = pd.DataFrame(
        {"f (Hz)": db_f[db_m], "potencia": db_esp[db_m] / max(db_esp[db_m].max(), 1e-12)}
    )
    db_bandas = pd.DataFrame(
        {
            "x1": [0.04, 0.15],
            "x2": [0.15, 0.40],
            "banda": ["LF (0,04–0,15 Hz)", "HF (0,15–0,40 Hz)"],
        }
    )
    db_g_bandas = (
        alt.Chart(db_bandas)
        .mark_rect(opacity=0.12)
        .encode(x="x1", x2="x2", color=alt.Color("banda", title=""))
    )
    db_g_esp = (
        alt.Chart(db_esp_df)
        .mark_line()
        .encode(
            x=alt.X("f (Hz)", title="Frecuencia (Hz)"),
            y=alt.Y("potencia", title="Potencia (norm.)"),
        )
    )
    db_lf = (db_f > 0.04) & (db_f < 0.15)
    db_hf = (db_f >= 0.15) & (db_f < 0.4)
    db_pico_lf = float(db_f[db_lf][np.argmax(db_esp[db_lf])])
    db_lfhf = float(db_esp[db_lf].sum() / max(db_esp[db_hf].sum(), 1e-12))
    db_sdnn = float(db_I[100:].std() * 1000.0)

    mo.vstack(
        [
            (db_g_bandas + db_g_esp).properties(
                width=540, height=240, title="Espectro del tacograma"
            ),
            mo.hstack(
                [
                    mo.stat(value=f"{db_sdnn:.1f} ms", label="SDNN"),
                    mo.stat(value=f"{db_pico_lf:.3f} Hz", label="Pico LF"),
                    mo.stat(value=f"{db_lfhf:.2f}", label="LF/HF"),
                    mo.stat(
                        value=f"{db_rpm.value / 60:.3f} Hz",
                        label="Tu respiración",
                    ),
                ],
                widths="equal",
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            r"""
    **Tres experimentos guiados con deBoer:**

    1. **¿De dónde sale el pico LF?** Con respiración a 15 resp/min, apaga el
       interruptor simpático: el pico de ~0,1 Hz del espectro **desaparece**.
       El famoso pico LF de tu pulsera no es una "onda del estrés": es la
       resonancia del lazo simpático lento, excitada por el ruido
       fisiológico. deBoer lo demostró en 1987 y sigue siendo la explicación
       más sobria (Julien, 2006).
    2. **Resonancia, ahora en serio.** Baja la respiración a 6 resp/min: el
       pico respiratorio (HF) *entra* en la banda LF, se funde con la
       resonancia del lazo y la SDNN se multiplica por ~3 — misma fisiología,
       mismos parámetros. Es la versión latido-a-latido de lo que el notebook
       anterior mostraba con el oscilador de juguete.
    3. **La huella del muestreo.** Mira el tacograma a 18 resp/min: la RSA
       casi desaparece, y no solo por el filtro vagal — con ~4 latidos por
       ciclo respiratorio el corazón apenas puede *muestrear* la onda. Un
       sistema que late no es un sistema continuo (mentira nº 3).
    """
        ),
        kind="info",
    )
    return


@app.cell
def _(db_aresp, db_simpatico, db_simula, np):
    # Barrido: SDNN frente a frecuencia respiratoria. La curva de resonancia
    # ya no se dibuja a mano — emerge del modelo latido a latido.
    db_rejilla = np.arange(4.0, 20.5, 1.0)
    db_sdnn_barrido = [
        float(db_simula(r, db_aresp.value, db_simpatico.value)[2][100:].std() * 1000.0)
        for r in db_rejilla
    ]
    return db_rejilla, db_sdnn_barrido


@app.cell
def _(alt, db_rejilla, db_rpm, db_sdnn_barrido, mo, pd):
    db_barrido_df = pd.DataFrame(
        {"resp/min": db_rejilla, "SDNN (ms)": db_sdnn_barrido}
    )
    db_g_barrido = (
        alt.Chart(db_barrido_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("resp/min", title="Frecuencia respiratoria (resp/min)"),
            y=alt.Y("SDNN (ms)"),
        )
    )
    db_g_marca = (
        alt.Chart(pd.DataFrame({"x": [db_rpm.value]}))
        .mark_rule(color="#888", strokeDash=[2, 2])
        .encode(x="x")
    )
    mo.vstack(
        [
            mo.md(
                "**La curva de resonancia, emergida.** En el notebook anterior "
                "esta curva era la *definición* del modelo; aquí nadie la "
                "escribió — sale sola de las reglas latido a latido:"
            ),
            (db_g_barrido + db_g_marca).properties(width=540, height=240),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## 3 · Peldaño pendiente: lo que TAMBIÉN estos modelos callan

    La honestidad intelectual no se agota en el peldaño 2. Ottesen y deBoer
    también mienten, solo que con mentiras más caras de corregir:

    | | Juguete | Ottesen | deBoer | Fisiología real |
    |---|---|---|---|---|
    | Resonancia | decretada | emerge | emerge | emerge |
    | No linealidad (sigmoide) | ✗ | ✓ | ✓ | ✓ |
    | Latido a latido | ✗ | ✗ | ✓ | ✓ |
    | Parámetros que cambian con el estado (postura, sueño, emoción) | ✗ | ✗ | ✗ | ✓ |
    | Ruido 1/f, fractalidad de largo plazo | ✗ | ✗ | ✗ | ✓ |
    | Química lenta (hormonas, renina-angiotensina, temperatura) | ✗ | ✗ | ✗ | ✓ |
    | Respiración real (no sinusoidal, acoplada al estado) | ✗ | ✗ | ✗ | ✓ |

    Los tres supuestos de la última mitad de la tabla son la razón de que la
    HRV *sí* lleve información sobre el estado del organismo — pero mezclada,
    no estacionaria y confundida con la mecánica que acabas de ver. La
    lección metodológica del recorrido completo:

    - **Un modelo no es verdadero o falso: responde una pregunta.** El
      juguete responde *"¿por qué hay una frecuencia privilegiada?"*; Ottesen
      responde *"¿de dónde salen las ondas de Mayer?"*; deBoer responde
      *"¿por qué el espectro de la HRV tiene esa forma?"*.
    - **Antes de leer psicología en una métrica, agota la mecánica.** Todo lo
      que este notebook reproduce (pico LF, ratio LF/HF, SDNN que se triplica
      al respirar lento) sale de bañeras, retardos y sigmoides — sin
      emociones, sin "estados ventral-vagales", sin teoría polivagal. Lo que
      quede *después* de descontar la mecánica, eso es lo interesante.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ---
    ### Referencias

    - deBoer, R. W., Karemaker, J. M., & Strackee, J. (1987). Hemodynamic
      fluctuations and baroreflex sensitivity in humans: a beat-to-beat
      model. *American Journal of Physiology*, 253(3), H680–H689.
    - Ottesen, J. T. (1997). Modelling of the baroreflex-feedback mechanism
      with time-delay. *Journal of Mathematical Biology*, 36(1), 41–63.
    - Julien, C. (2006). The enigma of Mayer waves: facts and models.
      *Cardiovascular Research*, 70(1), 12–21.
    - Ursino, M. (1998). Interaction between carotid baroregulation and the
      pulsating heart: a mathematical model. *American Journal of
      Physiology*, 275(5), H1733–H1747.
    - Vaschillo, E., Lehrer, P., Rishe, N., & Konstantinov, M. (2002). Heart
      rate variability biofeedback as a method for assessing baroreflex
      function. *Applied Psychophysiology and Biofeedback*, 27(1), 1–27.

    *Ambos modelos están simplificados respecto a los papers originales
    (parámetros redondeados, respiración sinusoidal, sin control de
    resistencia periférica en Ottesen); las ecuaciones conservan la
    estructura causal, que es lo que este notebook quiere enseñar.*
    """
    )
    return


if __name__ == "__main__":
    app.run()
