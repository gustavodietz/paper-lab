# paper-lab

Notebooks [marimo](https://marimo.io) de investigación primaria: cuando un
paper no se entiende (o no se cree), se reproduce el análisis con datos
reales o sintéticos.

**Notebooks publicados:** https://gustavodietz.github.io/paper-lab/
(interactivos, se ejecutan en el navegador vía WebAssembly, sin instalar nada)

## Cómo trabajar en local

Solo hace falta [uv](https://docs.astral.sh/uv/). Cada notebook lleva sus
dependencias declaradas en la cabecera (PEP 723), así que:

```bash
uvx marimo edit --sandbox notebooks/regresion_a_la_media.py
```

crea un entorno aislado con las dependencias justas de ese notebook y abre el
editor en el navegador. Para un notebook nuevo:

```bash
uvx marimo edit --sandbox notebooks/mi_nuevo_analisis.py
```

(al añadir imports desde el editor, marimo actualiza la cabecera de
dependencias solo).

## Cómo se publica

Cada push a `main` dispara `.github/workflows/publicar.yml`, que exporta cada
`notebooks/*.py` a HTML+WASM (`marimo export html-wasm`), genera un índice y
lo despliega en GitHub Pages. No hay servidor: el código Python corre en el
navegador de quien abre la página (Pyodide).

Implicación práctica: los notebooks deben apañárselas con dependencias puras
de Python o con wheel para Pyodide (numpy, pandas, polars, scipy, altair,
matplotlib, plotly… todo eso funciona) y con datos incluidos en el repo o
sintéticos. Nada de conexiones a bases de datos ni secretos: **todo lo que se
sube aquí es público**.

## Convenciones

- Un notebook = una pregunta o un paper. Nombre descriptivo en snake_case.
- Datos pequeños en `notebooks/public/`: esa carpeta se copia al export WASM,
  y los notebooks la leen con `mo.notebook_location() / "public" / fichero`
  (funciona igual en local y en la web publicada).
- Los notebooks son `.py` planos: se revisan y diffean como código normal.

## Datos incluidos

- `notebooks/public/reposo_ecg_rsp_100hz.csv`: 8,4 min de ECG + respiración
  reales en reposo, 100 Hz. Recorte del fichero `bio_resting_8min_100hz.csv`
  del proyecto [NeuroKit2](https://github.com/neuropsychology/NeuroKit)
  (Makowski et al. 2021, licencia MIT).
- `notebooks/public/meditacion/` (pendiente): series RR del dataset
  [meditation 1.0.0 de PhysioNet](https://physionet.org/content/meditation/1.0.0/)
  (Peng et al. 1999) — instrucciones de subida dentro del notebook
  `barorreflejo_modelos_contra_datos.py`.
