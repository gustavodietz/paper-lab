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
- Datos pequeños (CSV) en `data/`; los notebooks los leen con rutas relativas.
- Los notebooks son `.py` planos: se revisan y diffean como código normal.
