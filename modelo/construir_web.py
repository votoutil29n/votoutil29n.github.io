"""Construye la herramienta a partir de la plantilla y los datos.

Genera:
  index.html          página completa para GitHub Pages
  web/vista_previa.html  fragmento sin cabecera, para previsualizar en otros entornos
Uso: python3 modelo/construir_web.py <raíz del repositorio>
"""
import json, sys, html
S = sys.argv[1] if len(sys.argv) > 1 else '.'
cfg = json.load(open(f'{S}/web/config.json', encoding='utf-8'))
cls = json.load(open(f'{S}/datos/clasificacion.json', encoding='utf-8'))
y23 = {x['id']: x for x in json.load(open(f'{S}/datos/impacto2023.json', encoding='utf-8'))}
for d in cls:
    y = y23[d['id']]
    d['y23'] = {k: y[k] for k in ('seats', 'valid', 'lists', 'left_seats', 'last')}
data = json.dumps(cls, ensure_ascii=False, separators=(',', ':'))
t = open(f'{S}/web/plantilla.html', encoding='utf-8').read().replace('__DATA__', data)
autor = cfg.get('autor', '').strip()
t = t.replace('{{AUTOR_LINEA}}', f'Hecho por {html.escape(autor)}. ' if autor else '')

def fill(s, metodo, repo):
    s = s.replace('{{METODO_URL}}', metodo)
    s = s.replace('{{REPO_LINE}}', f' · <a href="{html.escape(repo)}">código y datos</a>' if repo else '')
    assert '{{' not in s, 'Quedan marcadores sin rellenar'
    return s

# Fragmento para vista previa
open(f'{S}/web/vista_previa.html', 'w', encoding='utf-8').write(fill(t, cfg.get('metodo_vista_previa', 'metodo.html'), ''))

# Página completa
frag = fill(t, 'metodo.html', cfg['repo_url'].rstrip('/'))
i = frag.index('<main>')
head = frag[:i].replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
body = frag[i:]
url = html.escape(cfg['url_publica'])
page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head.rstrip()}
<meta name="description" content="Elige tu provincia y a quién piensas votar: mira cuántos escaños aporta tu voto a la izquierda el 29-N y si otra opción aportaría más. Método y datos abiertos.">
<meta property="og:title" content="¿Dónde aporta más tu voto a la izquierda?">
<meta property="og:description" content="Comprueba el impacto real de tu voto el 29-N, provincia por provincia, y qué pasó con él en 2023.">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}html,body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
</head>
<body>
{body.rstrip()}
</body>
</html>
'''
open(f'{S}/index.html', 'w', encoding='utf-8').write(page)
print('index.html:', len(page), 'bytes · vista previa:', len(t), 'bytes')
