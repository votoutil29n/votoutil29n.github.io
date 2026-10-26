"""Compone METODO.md (cabecera, tabla generada y cuerpo) y lo convierte en metodo.html.

Uso: python3 modelo/construir_metodo.py <raíz del repositorio>
"""
import sys, re, json, html, markdown
from markdown.extensions.toc import slugify
S = sys.argv[1] if len(sys.argv) > 1 else '.'
# METODO.md = cabecera + tabla generada por clasificar.py + cuerpo
md = (open(f'{S}/web/metodo_cabecera.md', encoding='utf-8').read()
      + open(f'{S}/datos/resumen.md', encoding='utf-8').read()
      + open(f'{S}/web/metodo_cuerpo.md', encoding='utf-8').read())
open(f'{S}/METODO.md', 'w', encoding='utf-8').write(md)
body = markdown.markdown(md, extensions=['tables', 'fenced_code', 'toc'])
# Índice con las secciones de segundo nivel, antes de la primera
secs = re.findall(r'^## (.+)$', md, flags=re.M)
toc = '<nav class="toc" aria-label="En esta página"><p class="toc-t">En esta página</p><ol>' + ''.join(
    f'<li><a href="#{slugify(s, "-")}">{html.escape(s)}</a></li>' for s in secs) + '</ol></nav>'
i = body.index('<h2')
body = body[:i] + toc + '\n' + body[i:]
repo = json.load(open(f'{S}/web/config.json', encoding='utf-8'))['repo_url'].rstrip('/')
body = body.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
body = body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')
page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Metodología · Voto útil 29-N</title>
<meta name="description" content="Cómo se calcula el impacto de cada voto en Voto útil 29-N: datos, encuestas, simulaciones, validación y límites.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,500..800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{ --paper:#f6f7f9; --sheet:#ffffff; --ink:#17202b; --muted:#5b6573; --rule:#d9dee5; --link:#1f3a5f;
  --font-display:"Archivo","Arial Narrow",system-ui,sans-serif; --font-body:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --font-data:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
@media (prefers-color-scheme: dark) {{ :root {{ --paper:#12161c; --sheet:#1a2028; --ink:#e8ecf1; --muted:#9aa5b3; --rule:#2c3540; --link:#8fb3e0; color-scheme: dark; }} }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; }}
body {{ background: var(--paper); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.6;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; }}
main {{ max-width: 760px; margin: 0 auto; }}
h1, h2, h3 {{ font-family: var(--font-display); font-stretch: 85%; line-height: 1.15; text-wrap: balance; }}
h1 {{ font-size: clamp(1.8rem, 5vw, 2.4rem); font-weight: 800; margin: 0.4em 0 0.3em; }}
h2 {{ font-size: 1.35rem; margin-top: 2em; padding-top: 0.6em; border-top: 1px solid var(--rule); }}
h3 {{ font-size: 1.1rem; margin-top: 1.4em; }}
p, li {{ max-width: 68ch; }}
a {{ color: var(--link); }}
.tw {{ overflow-x: auto; margin: 1em 0; border: 1px solid var(--rule); border-radius: 6px; background: var(--sheet); }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
th {{ font-weight: 600; background: var(--paper); }}
tr:last-child td {{ border-bottom: 0; }}
pre {{ background: var(--sheet); border: 1px solid var(--rule); border-radius: 6px; padding: 12px; overflow-x: auto; font-family: var(--font-data); font-size: 0.85rem; }}
code {{ font-family: var(--font-data); font-size: 0.9em; }}
.back {{ font-family: var(--font-data); font-size: 0.85rem; }}
.topbar {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 6px 16px; padding-bottom: 10px; border-bottom: 1px solid var(--rule); }}
.topbar .brand {{ font-family: var(--font-data); font-size: 0.8rem; letter-spacing: 0.04em; color: var(--muted); text-decoration: none; }}
.topbar .links {{ display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 0.92rem; font-weight: 600; }}
.topbar a {{ text-decoration: none; }}
.toc {{ margin: 1.2em 0 0.4em; padding: 12px 16px; border: 1px solid var(--rule); border-radius: 6px; background: var(--sheet); }}
.toc-t {{ margin: 0 0 6px; font-family: var(--font-data); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }}
.toc ol {{ margin: 0; padding-left: 1.3em; display: grid; gap: 4px; }}
h2 {{ scroll-margin-top: 12px; }}
</style>
</head>
<body>
<main>
<nav class="topbar" aria-label="Secciones"><a class="brand" href="./">Voto útil 29-N</a><span class="links"><a href="./">← Volver a la herramienta</a><a href="#partidos-incluidos-y-sesgos-conocidos">Sesgos conocidos</a><a target="_blank" rel="noopener" href="{html.escape(repo)}">Código y datos</a></span></nav>
{body}
<p class="back"><a href="./">← Volver a la herramienta</a></p>
</main>
</body>
</html>
'''
open(f'{S}/metodo.html', 'w', encoding='utf-8').write(page)
print('metodo.html generado:', len(page), 'bytes')
