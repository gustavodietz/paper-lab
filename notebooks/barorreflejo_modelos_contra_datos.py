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
    # El barorreflejo: modelos contra datos

    El notebook de [resonancia y HRV](../resonancia_hrv_polivagal/) usaba un
    modelo de juguete y terminaba con una nota de honestidad: era lineal,
    estacionario, y la resonancia estaba puesta a mano. Este notebook toma esa
    nota en serio en las dos direcciones: **hacia arriba** (los modelos serios:
    Ottesen y deBoer) y **hacia el suelo** (un registro fisiológico real, con
    su ruido y sus artefactos, analizado desde el ECG crudo).

    La estructura es un partido en tres actos:

    1. **Ottesen** — un lazo con retardo *genera* la oscilación de 0,1 Hz.
    2. **deBoer** — un modelo latido a latido *predice* la forma del espectro.
    3. **Datos reales** — ECG y respiración de una persona de verdad:
       ¿aparece lo que los modelos dicen que debe aparecer?

    Y un acto 4 en el banquillo: el análisis de meditadores (Chi y Kundalini)
    preparado para cuando subamos los datos de PhysioNet al repo.
    """
    )
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
    flowchart LR
        A["🧸 Juguete<br/><i>supone la resonancia</i>"]
        B["🔁 Ottesen<br/><i>la genera</i>"]
        C["🫀 deBoer<br/><i>predice el espectro</i>"]
        D["📈 Datos reales<br/><i>el árbitro</i>"]
        A --> B --> C --> D
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Acto 1 · Ottesen: la resonancia no se supone, se genera

    Modelo mínimo con dos variables — presión media $P$ y frecuencia cardiaca
    $H$ — y tres ingredientes: la **bañera** (windkessel:
    $C\,dP/dt = HV_s/60 - P/R$), la **sigmoide barorrefleja** (los receptores
    saturan: $s(P)$ simpática que baja con la presión, $v(P)$ vagal que sube),
    y los **dos brazos con sus tiempos**: el vago mielinizado lee la presión
    de *ahora*; el simpático llega con retardo $\tau$ y se instala despacio:

    $$\tau_H\,\frac{dH}{dt} = H_0 + G_s\,s\big(P(t-\tau)\big) - G_v\,v\big(P(t)\big) - H$$

    Nada aquí oscila por sí mismo: no hay $f_0$, no hay respiración, no hay
    entrada periódica. Solo un termostato con un cable lento.
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
            tooltip=["t (s)", "valor", "señal"],
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
    **Experimentos** (por defecto: τ=3,5 · Gₛ=80 · Gᵥ=15, oscilación suave):

    1. **Gₛ → 110**: la espiral del plano de fases se vuelve un **ciclo
       límite** — oscilación autosostenida de ~0,1 Hz sin ninguna entrada
       oscilante (bifurcación de Hopf). Son las ondas de Mayer, emergiendo.
    2. **Gᵥ → 60**: mueren. El freno *rápido* (vago mielinizado, sin retardo)
       estabiliza lo que el acelerador *lento* desestabiliza. Ingeniería de
       control, no psicología.
    3. **τ → 1,5**: sin retardo suficiente no hay oscilación posible; y con
       τ=5 el periodo se alarga a ~15 s. La frecuencia que el juguete
       decretaba, aquí emerge de la dinámica. Nota también que la amplitud
       satura (~25 mmHg): la sigmoide pone el techo que un modelo lineal no
       sabe poner.
    """
        ),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Acto 2 · deBoer: el corazón late, y predice un espectro

    deBoer, Karemaker & Strackee (1987): el barorreflejo opera **latido a
    latido**. Cada latido $n$: la presión decae en diástole
    ($D_n = S_{n-1}e^{-I_{n-1}/T_n}$, con $T_n$ controlada por el simpático),
    la nueva sístole suma el pulso (restitución de Starling + respiración +
    ruido fisiológico), y el barorreflejo responde con la presión *efectiva*
    $S' = S_{ref} + 18\arctan\!\big(\tfrac{S-S_{ref}}{18}\big)$ por dos vías:

    $$I_n = I_0 + G_v\,(S'_n - S_{ref}) + G_s\,\big(\overline{S'}_{n-6..n-2} - S_{ref}\big)$$

    La vagal actúa **dentro del mismo latido**; la simpática promedia los
    latidos 2–6 anteriores (el retardo de Ottesen, en unidades de latido).
    Este modelo hace algo que los anteriores no hacían: **predice la forma
    del espectro de la HRV** — un pico LF a ~0,1 Hz (la resonancia del lazo,
    excitada por ruido) y un pico HF en la frecuencia respiratoria.
    """
    )
    return


@app.cell
def _(mo):
    db_rpm = mo.ui.slider(4.0, 20.0, value=15.0, step=0.5, label="🌬️ Frecuencia respiratoria (resp/min)")
    db_aresp = mo.ui.slider(0.0, 6.0, value=3.0, step=0.5, label="💨 Amplitud mecánica de la respiración (mmHg)")
    db_simpatico = mo.ui.switch(value=True, label="🔥 Brazo simpático lento (retardo 2–6 latidos)")
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

    def espectro_welch(x, fs, seg_s=60.0, solape=0.5):
        """PSD de Welch en numpy puro: tramos con ventana Hann, promediados."""
        n = int(seg_s * fs)
        paso = int(n * (1 - solape))
        ventana = np.hanning(n)
        tramos = []
        for ini in range(0, len(x) - n + 1, paso):
            seg = x[ini:ini + n]
            seg = seg - seg.mean()
            tramos.append(np.abs(np.fft.rfft(seg * ventana)) ** 2)
        f = np.fft.rfftfreq(n, 1 / fs)
        return f, np.mean(tramos, axis=0)

    def tacograma_uniforme(t_lat, rr, fs=4.0):
        """Remuestrea la serie RR (irregular por naturaleza) a malla uniforme."""
        tt = np.arange(t_lat[0], t_lat[-1], 1.0 / fs)
        return tt, np.interp(tt, t_lat, rr)

    return db_simula, espectro_welch, tacograma_uniforme


@app.cell
def _(db_aresp, db_rpm, db_simpatico, db_simula):
    db_t, db_S, db_I = db_simula(db_rpm.value, db_aresp.value, db_simpatico.value)
    return db_I, db_t


@app.cell
def _(alt, db_I, db_rpm, db_t, espectro_welch, mo, np, pd, tacograma_uniforme):
    db_tt, db_rru = tacograma_uniforme(db_t[100:], db_I[100:])
    db_f, db_esp = espectro_welch(db_rru, 4.0)
    db_m = (db_f > 0.02) & (db_f < 0.5)
    db_esp_df = pd.DataFrame(
        {"f (Hz)": db_f[db_m], "potencia": db_esp[db_m] / max(db_esp[db_m].max(), 1e-12)}
    )
    db_bandas = pd.DataFrame(
        {"x1": [0.04, 0.15], "x2": [0.15, 0.40], "banda": ["LF", "HF"]}
    )
    db_g = (
        alt.Chart(db_bandas).mark_rect(opacity=0.12).encode(x="x1", x2="x2", color=alt.Color("banda", title=""))
        + alt.Chart(db_esp_df).mark_line().encode(
            x=alt.X("f (Hz)", title="Frecuencia (Hz)"),
            y=alt.Y("potencia", title="Potencia (norm.)"),
            tooltip=["f (Hz)", "potencia"],
        )
    ).properties(width=540, height=230, title="Espectro PREDICHO por deBoer")

    db_lf = (db_f > 0.04) & (db_f < 0.15)
    db_hf = (db_f >= 0.15) & (db_f < 0.4)
    db_sdnn = float(db_I[100:].std() * 1000.0)
    mo.vstack(
        [
            db_g,
            mo.hstack(
                [
                    mo.stat(value=f"{db_sdnn:.1f} ms", label="SDNN simulada"),
                    mo.stat(value=f"{float(db_f[db_lf][np.argmax(db_esp[db_lf])]):.3f} Hz", label="Pico LF"),
                    mo.stat(value=f"{float(db_esp[db_lf].sum() / max(db_esp[db_hf].sum(), 1e-12)):.2f}", label="LF/HF"),
                    mo.stat(value=f"{db_rpm.value / 60:.3f} Hz", label="Respiración"),
                ],
                widths="equal",
            ),
            mo.callout(
                mo.md(
                    "**Experimentos:** apaga el interruptor simpático → el pico "
                    "LF desaparece (no es 'estrés': es la resonancia del lazo "
                    "lento excitada por ruido — Julien 2006). Baja a 6 resp/min "
                    "→ los dos picos se funden y la SDNN se multiplica por ~3. "
                    "Y deja el slider en **9 resp/min**: es lo que respira la "
                    "persona real del acto 3 — esa es la predicción a batir."
                ),
                kind="info",
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Acto 3 · El árbitro: una persona real

    8,4 minutos de **ECG y respiración reales** (100 Hz, reposo con ojos
    cerrados; datos abiertos del proyecto
    [NeuroKit2](https://github.com/neuropsychology/NeuroKit), Makowski et
    al. 2021, incluidos en `notebooks/public/` de este repo). Nada de series
    ya limpias: empezamos donde empieza la ciencia de verdad, en el voltaje
    crudo.

    ### 3.1 · Del voltaje al latido

    Para medir HRV primero hay que *encontrar los latidos*. Usamos un
    detector tipo Pan-Tompkins construido a la vista (nada de cajas negras),
    en tres pasos: quitar la deriva de línea de base (media móvil de 0,6 s),
    realzar las pendientes rápidas del complejo QRS (derivada al cuadrado) e
    integrar su energía en ventanas de 150 ms. Donde esa energía supera un
    umbral, hay un latido. Mueve la ventana y el umbral:
    """
    )
    return


@app.cell
def _(mo, pd):
    rd_df = pd.read_csv(
        str(mo.notebook_location() / "public" / "reposo_ecg_rsp_100hz.csv")
    )
    RD_FS = 100.0
    return RD_FS, rd_df


@app.cell
def _(mo):
    rd_inicio = mo.ui.slider(0, 480, value=60, step=5, label="🔎 Ventana: segundo inicial")
    rd_umbral = mo.ui.slider(0.05, 0.60, value=0.25, step=0.05, label="🎚️ Umbral de detección (fracción del percentil 99,5)")
    mo.vstack([rd_inicio, rd_umbral])
    return rd_inicio, rd_umbral


@app.cell
def _(RD_FS, np, rd_df, rd_umbral):
    def rd_media_movil(x, ancho_s):
        n = max(1, int(ancho_s * RD_FS))
        return np.convolve(x, np.ones(n) / n, mode="same")

    rd_ecg = rd_df["ECG"].to_numpy()
    rd_rsp = rd_df["RSP"].to_numpy()

    rd_limpio = rd_ecg - rd_media_movil(rd_ecg, 0.6)
    rd_energia = rd_media_movil(np.gradient(rd_limpio) ** 2, 0.15)
    rd_umb = rd_umbral.value * np.percentile(rd_energia, 99.5)

    rd_cand = np.where(
        (rd_energia[1:-1] > rd_umb)
        & (rd_energia[1:-1] >= rd_energia[:-2])
        & (rd_energia[1:-1] >= rd_energia[2:])
    )[0] + 1
    rd_lista = []
    for rd_c in rd_cand:  # refractario de 300 ms: un QRS no puede repetirse antes
        if rd_lista and (rd_c - rd_lista[-1]) < 0.3 * RD_FS:
            if rd_energia[rd_c] > rd_energia[rd_lista[-1]]:
                rd_lista[-1] = rd_c
        else:
            rd_lista.append(rd_c)
    rd_picos = np.array(
        [
            max(0, p - 5) + int(np.argmax(rd_limpio[max(0, p - 5):p + 5]))
            for p in rd_lista
        ]
    )
    rd_tpicos = rd_picos / RD_FS
    rd_rr = np.diff(rd_tpicos)
    return rd_energia, rd_limpio, rd_picos, rd_rr, rd_rsp, rd_tpicos, rd_umb


@app.cell
def _(RD_FS, alt, mo, np, pd, rd_inicio, rd_limpio, rd_picos, rd_umb, rd_energia):
    rd_a = int(rd_inicio.value * RD_FS)
    rd_b = min(rd_a + int(10 * RD_FS), len(rd_limpio))
    rd_tv = np.arange(rd_a, rd_b) / RD_FS
    rd_v_df = pd.DataFrame({"t (s)": rd_tv, "ECG (mV)": rd_limpio[rd_a:rd_b]})
    rd_en_df = pd.DataFrame(
        {"t (s)": rd_tv, "energía": rd_energia[rd_a:rd_b] / rd_umb}
    )
    rd_pv = rd_picos[(rd_picos >= rd_a) & (rd_picos < rd_b)]
    rd_p_df = pd.DataFrame(
        {"t (s)": rd_pv / RD_FS, "ECG (mV)": rd_limpio[rd_pv]}
    )
    rd_g1 = (
        alt.Chart(rd_v_df).mark_line(strokeWidth=1).encode(
            x=alt.X("t (s)", scale=alt.Scale(zero=False)), y="ECG (mV)"
        )
        + alt.Chart(rd_p_df).mark_point(color="#d62728", size=70, shape="triangle-down").encode(
            x="t (s)", y="ECG (mV)", tooltip=["t (s)"]
        )
    ).properties(width=540, height=180, title="ECG real con latidos detectados")
    rd_g2 = (
        alt.Chart(rd_en_df).mark_line(color="#7f7f7f").encode(
            x=alt.X("t (s)", scale=alt.Scale(zero=False)),
            y=alt.Y("energía", title="energía / umbral"),
        )
        + alt.Chart(pd.DataFrame({"y": [1.0]})).mark_rule(strokeDash=[4, 3]).encode(y="y")
    ).properties(width=540, height=100, title="Energía QRS frente al umbral")
    mo.vstack([rd_g1, rd_g2])
    return


@app.cell
def _(mo, np, rd_rr):
    rd_malos = int(np.sum((rd_rr < 0.4) | (rd_rr > 1.6)))
    mo.hstack(
        [
            mo.stat(value=f"{len(rd_rr) + 1}", label="Latidos detectados"),
            mo.stat(value=f"{60.0 / rd_rr.mean():.1f} lpm", label="FC media"),
            mo.stat(value=f"{rd_rr.std() * 1000:.1f} ms", label="SDNN"),
            mo.stat(
                value=f"{rd_malos}",
                label="RR imposibles (<400 o >1600 ms)",
                caption="si sube de 0, el umbral está mal puesto — pruébalo",
            ),
        ],
        widths="equal",
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    Con el umbral por defecto: **cero intervalos imposibles**. Bájalo a 0,05 o
    súbelo a 0,6 y mira cómo aparecen falsos positivos o latidos perdidos —
    cada uno mete un artefacto enorme en la HRV. Esta sensibilidad al
    preprocesado es la primera lección que ningún modelo enseña: *la métrica
    depende de decisiones de ingeniería tomadas antes de calcularla*.

    ### 3.2 · La RSA, a simple vista

    El tacograma real contra la respiración real, sin espectros de por medio:
    """
    )
    return


@app.cell
def _(RD_FS, alt, mo, np, pd, rd_inicio, rd_rr, rd_rsp, rd_tpicos):
    rd_w0 = float(rd_inicio.value)
    rd_w1 = rd_w0 + 60.0
    rd_msk = (rd_tpicos[1:] >= rd_w0) & (rd_tpicos[1:] <= rd_w1)
    rd_fc_inst = 60.0 / rd_rr[rd_msk]
    rd_taco_df = pd.DataFrame(
        {"t (s)": rd_tpicos[1:][rd_msk], "valor": rd_fc_inst, "señal": "FC instantánea (lpm)"}
    )
    rd_ir = np.arange(int(rd_w0 * RD_FS), min(int(rd_w1 * RD_FS), len(rd_rsp)), 25)
    rd_r_z = rd_rsp[rd_ir]
    rd_r_z = (rd_r_z - rd_r_z.mean()) / (rd_r_z.std() + 1e-9)
    rd_resp_df = pd.DataFrame(
        {
            "t (s)": rd_ir / RD_FS,
            "valor": rd_fc_inst.mean() + rd_r_z * rd_fc_inst.std(),
            "señal": "respiración (reescalada)",
        }
    )
    rd_g_rsa = (
        alt.Chart(pd.concat([rd_taco_df, rd_resp_df], ignore_index=True))
        .mark_line()
        .encode(
            x=alt.X("t (s)", scale=alt.Scale(zero=False)),
            y=alt.Y("valor", title="lpm", scale=alt.Scale(zero=False)),
            color=alt.Color("señal", title=""),
            tooltip=["t (s)", "valor"],
        )
        .properties(width=540, height=230, title="Arritmia sinusal respiratoria, en crudo (60 s)")
    )
    mo.vstack(
        [
            rd_g_rsa,
            mo.md(
                "Inspiración → el corazón acelera; espiración → frena. Esta "
                "persona respira espontáneamente a **~9 resp/min (0,15 Hz)**, "
                "cerca de la zona de resonancia — y su RSA es enorme a simple "
                "vista. Usa el slider de ventana de arriba para recorrer los "
                "8 minutos."
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### 3.3 · El veredicto espectral

    Espectro del tacograma real (mismo método de Welch que usamos con el
    modelo) y **coherencia** respiración↔RR — el estadístico que mide, banda a
    banda, cuánta de la variabilidad cardiaca está *enganchada* a la
    respiración:
    """
    )
    return


@app.cell
def _(RD_FS, espectro_welch, np, rd_rr, rd_rsp, rd_tpicos, tacograma_uniforme):
    rd_tt, rd_rru = tacograma_uniforme(rd_tpicos[1:], rd_rr)
    rd_rspu = np.interp(rd_tt, np.arange(len(rd_rsp)) / RD_FS, rd_rsp)

    rd_f, rd_prr = espectro_welch(rd_rru, 4.0)
    rd_f2, rd_prsp = espectro_welch(rd_rspu, 4.0)

    def rd_coherencia(x, y, fs=4.0, seg_s=60.0, solape=0.5):
        n = int(seg_s * fs)
        paso = int(n * (1 - solape))
        ventana = np.hanning(n)
        pxx = pyy = 0.0
        pxy = 0.0 + 0.0j
        for ini in range(0, len(x) - n + 1, paso):
            sx = (x[ini:ini + n] - x[ini:ini + n].mean()) * ventana
            sy = (y[ini:ini + n] - y[ini:ini + n].mean()) * ventana
            fx, fy = np.fft.rfft(sx), np.fft.rfft(sy)
            pxx = pxx + np.abs(fx) ** 2
            pyy = pyy + np.abs(fy) ** 2
            pxy = pxy + fx * np.conj(fy)
        f = np.fft.rfftfreq(n, 1 / fs)
        return f, np.abs(pxy) ** 2 / (pxx * pyy + 1e-20)

    rd_fc_, rd_coh = rd_coherencia(rd_rru, rd_rspu)
    rd_frespir = float(
        rd_f2[(rd_f2 > 0.05) & (rd_f2 < 0.5)][
            np.argmax(rd_prsp[(rd_f2 > 0.05) & (rd_f2 < 0.5)])
        ]
    )
    return rd_coh, rd_f, rd_fc_, rd_frespir, rd_prr


@app.cell
def _(alt, mo, np, pd, rd_coh, rd_f, rd_fc_, rd_frespir, rd_prr):
    rd_m = (rd_f > 0.02) & (rd_f < 0.5)
    rd_esp_df = pd.DataFrame(
        {"f (Hz)": rd_f[rd_m], "potencia": rd_prr[rd_m] / rd_prr[rd_m].max()}
    )
    rd_bandas2 = pd.DataFrame(
        {"x1": [0.04, 0.15], "x2": [0.15, 0.40], "banda": ["LF", "HF"]}
    )
    rd_g_esp = (
        alt.Chart(rd_bandas2).mark_rect(opacity=0.12).encode(x="x1", x2="x2", color=alt.Color("banda", title=""))
        + alt.Chart(rd_esp_df).mark_line().encode(
            x=alt.X("f (Hz)", title="Frecuencia (Hz)"),
            y=alt.Y("potencia", title="Potencia (norm.)"),
            tooltip=["f (Hz)", "potencia"],
        )
        + alt.Chart(pd.DataFrame({"x": [rd_frespir]})).mark_rule(
            color="#d62728", strokeDash=[4, 3]
        ).encode(x="x")
    ).properties(width=540, height=220, title="Espectro MEDIDO (línea roja: frecuencia respiratoria)")

    rd_mc = (rd_fc_ > 0.02) & (rd_fc_ < 0.5)
    rd_coh_df = pd.DataFrame({"f (Hz)": rd_fc_[rd_mc], "coherencia": rd_coh[rd_mc]})
    rd_g_coh = (
        alt.Chart(rd_coh_df).mark_area(opacity=0.55).encode(
            x=alt.X("f (Hz)", title="Frecuencia (Hz)"),
            y=alt.Y("coherencia", scale=alt.Scale(domain=[0, 1])),
            tooltip=["f (Hz)", "coherencia"],
        )
        + alt.Chart(pd.DataFrame({"x": [rd_frespir]})).mark_rule(
            color="#d62728", strokeDash=[4, 3]
        ).encode(x="x")
    ).properties(width=540, height=160, title="Coherencia respiración ↔ RR")

    rd_coh_resp = float(rd_coh[np.argmin(np.abs(rd_fc_ - rd_frespir))])
    mo.vstack(
        [
            rd_g_esp,
            rd_g_coh,
            mo.hstack(
                [
                    mo.stat(value=f"{rd_frespir * 60:.1f} resp/min", label="Respiración medida"),
                    mo.stat(
                        value=f"{rd_coh_resp:.2f}",
                        label="Coherencia en esa frecuencia",
                        caption="1,0 = acoplamiento perfecto",
                    ),
                ],
                widths="equal",
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### 3.4 · El contraste

    | Predicción de los modelos | ¿Y en la persona real? |
    |---|---|
    | Pico HF clavado en la frecuencia respiratoria (deBoer) | ✅ Pico dominante exactamente en ~0,15 Hz, donde respira |
    | Coherencia alta resp↔RR solo alrededor de esa frecuencia | ✅ Coherencia ~0,95 en la banda respiratoria, y baja fuera |
    | Potencia LF apreciable sin necesidad de "estrés" (resonancia + ruido) | ✅ Hay potencia LF en reposo profundo con ojos cerrados |
    | HRV grande si respiras lento (resonancia) | ✅ Respirador lento espontáneo (~9/min): SDNN ~83 ms, enorme |

    El mismo mensaje del notebook anterior, ahora con datos: la estructura de
    la HRV la explica la **mecánica del lazo** (respiración + barorreflejo +
    retardo). Cualquier lectura psicológica —"esta persona tiene un LF/HF de
    1,4, luego su balance simpático-vagal..."— tiene que descontar primero
    todo esto. Con un solo sujeto no demostramos nada estadísticamente, pero
    tampoco hace falta: basta para ver que **la métrica sigue a la mecánica**.

    ## Acto 4 · Meditadores (esperando datos) 🧘

    Aquí va el análisis del dataset clásico de Peng, Benson & Goldberger:
    series RR de meditadores de **Chi** y **Kundalini** antes y durante la
    meditación. La predicción de todo lo anterior es concreta: si esas
    técnicas ralentizan la respiración hacia la zona de resonancia, deben
    aparecer oscilaciones cardiacas *gigantes* a 0,05–0,1 Hz — sin necesidad
    de invocar estados vagales especiales.
    """
    )
    return


@app.cell
def _(mo, np, pd):
    def med_carga(nombre):
        """Lector tolerante de las series RR de PhysioNet (meditation 1.0.0).

        Acepta ficheros de 1 columna (intervalos RR, en s o ms) o de 2
        columnas (tiempo, FC instantánea en lpm o intervalo RR).
        Devuelve (tiempos_latido_s, rr_s) o None si el fichero no está.
        """
        try:
            ruta = mo.notebook_location() / "public" / "meditacion" / nombre
            tabla = pd.read_csv(str(ruta), sep=r"\s+", header=None, comment="#")
        except Exception:
            return None
        vals = tabla.to_numpy(dtype=float)
        if vals.shape[1] == 1:
            rr = vals[:, 0]
            rr = rr / 1000.0 if np.nanmedian(rr) > 10 else rr
            t = np.cumsum(rr)
        else:
            t, col2 = vals[:, 0], vals[:, 1]
            if np.nanmedian(col2) > 20:      # FC en lpm
                rr = 60.0 / col2
            else:                             # RR en s
                rr = col2
        ok = (rr > 0.3) & (rr < 2.5)
        return t[ok], rr[ok]

    MED_REGISTROS = [f"C{i}" for i in range(1, 9)] + [f"Y{i}" for i in range(1, 5)]
    med_datos = {}
    for med_r in MED_REGISTROS:
        med_pre = med_carga(f"{med_r}_pre.txt")
        med_med = med_carga(f"{med_r}_med.txt")
        if med_pre is not None and med_med is not None:
            med_datos[med_r] = {"pre": med_pre, "med": med_med}
    return (med_datos,)


@app.cell
def _(med_datos, mo):
    if not med_datos:
        med_aviso = mo.callout(
            mo.md(
                r"""
    **Para activar este acto** (2 minutos):

    1. Descarga el dataset (acceso abierto):
       [physionet.org/content/meditation/1.0.0](https://physionet.org/content/meditation/1.0.0/)
    2. De la carpeta `data/`, coge las series de los grupos Chi (C1…C8) y
       Kundalini (Y1…Y4), en sus versiones **pre** y **med**.
    3. Renómbralas `C1_pre.txt`, `C1_med.txt`, … `Y4_med.txt` y súbelas a
       `notebooks/public/meditacion/` del repo (arrastrar y soltar en
       github.com → Add file → Upload files).

    En el siguiente push, esta sección se llena sola: tacogramas pre→med,
    espectrogramas donde se ve *aparecer* la oscilación al empezar a meditar,
    y comparación de amplitudes entre grupos. El lector de ficheros es
    tolerante con el formato (1 o 2 columnas, s o ms), pero si algo no
    cuadra, lo ajustamos.
    """
            ),
            kind="warn",
        )
    else:
        med_aviso = mo.md(
            f"**Registros cargados:** {', '.join(sorted(med_datos))} — elige uno:"
        )
    med_aviso
    return


@app.cell
def _(med_datos, mo):
    med_sel = (
        mo.ui.dropdown(options=sorted(med_datos), value=sorted(med_datos)[0])
        if med_datos
        else None
    )
    med_sel
    return (med_sel,)


@app.cell
def _(alt, med_datos, med_sel, mo, np, pd, espectro_welch, tacograma_uniforme):
    def med_espectrograma(t, rr, vent_s=120.0, paso_s=20.0):
        """STFT sencilla del tacograma: potencia 0–0,2 Hz frente al tiempo."""
        tt, rru = tacograma_uniforme(t, rr, fs=4.0)
        filas = []
        n = int(vent_s * 4)
        for ini in range(0, len(rru) - n, int(paso_s * 4)):
            seg = rru[ini:ini + n] - rru[ini:ini + n].mean()
            esp = np.abs(np.fft.rfft(seg * np.hanning(n))) ** 2
            f = np.fft.rfftfreq(n, 0.25)
            m = (f > 0.02) & (f < 0.2)
            for fi, pi in zip(f[m], esp[m]):
                filas.append({"t (min)": tt[ini + n // 2] / 60.0, "f (Hz)": round(float(fi), 4), "potencia": float(pi)})
        return pd.DataFrame(filas)

    if med_datos and med_sel is not None:
        med_t_pre, med_rr_pre = med_datos[med_sel.value]["pre"]
        med_t_med, med_rr_med = med_datos[med_sel.value]["med"]

        med_df_taco = pd.concat(
            [
                pd.DataFrame({"t (min)": med_t_pre / 60.0, "FC (lpm)": 60.0 / med_rr_pre, "fase": "pre"}),
                pd.DataFrame({"t (min)": med_t_med / 60.0, "FC (lpm)": 60.0 / med_rr_med, "fase": "meditación"}),
            ],
            ignore_index=True,
        ).iloc[::3]
        med_g_taco = (
            alt.Chart(med_df_taco)
            .mark_line(strokeWidth=1)
            .encode(
                x="t (min)",
                y=alt.Y("FC (lpm)", scale=alt.Scale(zero=False)),
                color=alt.Color("fase", title=""),
                tooltip=["t (min)", "FC (lpm)"],
            )
            .properties(width=540, height=200, title=f"{med_sel.value}: tacograma pre vs meditación")
        )

        med_eg = med_espectrograma(med_t_med, med_rr_med)
        med_g_spec = (
            alt.Chart(med_eg)
            .mark_rect()
            .encode(
                x=alt.X("t (min):O", title="Tiempo (min)", axis=alt.Axis(labelOverlap=True, format=".0f")),
                y=alt.Y("f (Hz):O", sort="descending"),
                color=alt.Color("potencia", scale=alt.Scale(scheme="magma"), legend=None),
                tooltip=["t (min)", "f (Hz)", "potencia"],
            )
            .properties(width=540, height=220, title="Espectrograma durante la meditación")
        )

        def med_amp(t, rr):
            _, esp = espectro_welch(tacograma_uniforme(t, rr, fs=4.0)[1], 4.0, seg_s=120.0)
            f = np.fft.rfftfreq(int(120 * 4), 0.25)
            m = (f > 0.025) & (f < 0.15)
            return float(esp[m].sum())

        med_ratio = med_amp(med_t_med, med_rr_med) / max(med_amp(med_t_pre, med_rr_pre), 1e-12)
        med_salida = mo.vstack(
            [
                med_g_taco,
                med_g_spec,
                mo.stat(
                    value=f"×{med_ratio:.1f}",
                    label="Potencia 0,025–0,15 Hz: meditación / pre",
                    caption="la oscilación 'exagerada' de Peng et al., cuantificada",
                ),
            ]
        )
    else:
        med_salida = mo.md("*Sección a la espera de los datos (instrucciones arriba).*")
    med_salida
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
    - Peng, C.-K., Mietus, J. E., Liu, Y., Khalsa, G., Douglas, P. S.,
      Benson, H., & Goldberger, A. L. (1999). Exaggerated heart rate
      oscillations during two meditation techniques. *International Journal
      of Cardiology*, 70(2), 101–107.
    - Makowski, D., et al. (2021). NeuroKit2: A Python toolbox for
      neurophysiological signal processing. *Behavior Research Methods*,
      53(4), 1689–1696. (Origen de los datos de reposo, licencia MIT.)
    - Grossman, P., & Taylor, E. W. (2007). Toward understanding respiratory
      sinus arrhythmia. *Biological Psychology*, 74(2), 263–285.

    *Los modelos están simplificados respecto a los papers originales; las
    ecuaciones conservan la estructura causal. El detector de picos R es
    deliberadamente transparente y no sustituye a un detector clínico.*
    """
    )
    return


if __name__ == "__main__":
    app.run()
