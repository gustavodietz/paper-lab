"""Genera _site/index.html con enlaces a los notebooks exportados a WASM."""

from pathlib import Path

site = Path("_site")
carpetas = sorted(p.name for p in site.iterdir() if p.is_dir())

enlaces = "\n".join(
    f'      <li><a href="{nombre}/">{nombre.replace("_", " ")}</a></li>'
    for nombre in carpetas
)

html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>paper-lab</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 4rem auto; padding: 0 1rem; line-height: 1.6; }}
    h1 {{ font-size: 1.6rem; }}
    li {{ margin: 0.4rem 0; }}
  </style>
</head>
<body>
  <h1>paper-lab</h1>
  <p>Notebooks de investigación primaria: reproducir y entender análisis de
  papers con datos reales o sintéticos. Cada notebook se ejecuta en tu
  navegador (WebAssembly), sin instalar nada.</p>
  <ul>
{enlaces}
  </ul>
</body>
</html>
"""

(site / "index.html").write_text(html, encoding="utf-8")
print(f"Índice generado con {len(carpetas)} notebooks")
