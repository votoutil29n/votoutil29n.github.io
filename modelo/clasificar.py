"""Calcula, para cada circunscripción, cuánto aporta al bloque de izquierdas cada voto.

Medida: escaños que gana la izquierda (de media) con medio punto más de voto para una lista,
promediando todas las simulaciones y solo las ajustadas. Se publica como «de cada 100 resultados» (chg). Se compara con la mejor opción de
la provincia y se repite en 10 escenarios de control.
Uso: python3 modelo/clasificar.py <raíz del repositorio>
Salida: datos/clasificacion.json y datos/resumen.md
"""
import json, sys, unicodedata
from decimal import Decimal, ROUND_HALF_UP
S = sys.argv[1]
ns = {}; exec(open(f'{S}/modelo/nombres.py', encoding='utf-8').read(), ns)
ES, name = ns['ES'], ns['name']
ALTS = ['seed2', 'ercLow', 'ercHigh', 'blocWide', 'podHigh', 'altLow', 'altHigh', 'aaHigh', 'cis', 'ncFull']
SIM = {t: json.load(open(f'{S}/datos/sim_{t}.json', encoding='utf-8')) for t in ['main'] + ALTS}
COM = {'AND': 'Andalucía', 'ARA': 'Aragón', 'AST': 'Asturias', 'BAL': 'Illes Balears', 'CAN': 'Canarias',
       'CANT': 'Cantabria', 'CAT': 'Cataluña', 'CEU': 'Ceuta', 'CLM': 'Castilla-La Mancha', 'CYL': 'Castilla y León',
       'EXT': 'Extremadura', 'GAL': 'Galicia', 'MAD': 'Madrid', 'MEL': 'Melilla', 'MUR': 'Murcia', 'NAV': 'Navarra',
       'PV': 'País Vasco', 'RIO': 'La Rioja', 'VAL': 'C. Valenciana'}
PSOEN = {'CAT': 'PSC', 'GAL': 'PSdeG-PSOE', 'PV': 'PSE-EE', 'NAV': 'PSN-PSOE'}
OTHERN = {'PP': 'PP', 'VOX': 'Vox', 'SALF': 'SALF', 'JUNTS': 'Junts', 'PNV': 'PNV', 'CC': 'Coalición Canaria',
          'EXISTE': 'Teruel Existe', 'SY': 'Soria ¡Ya!'}
PODIN = {'CAT': 'ERC', 'VAL': 'ALT', 'CAN': 'ALT'}
NO_CONTEST = 0.01   # escaños por medio punto: por debajo, ningún voto de izquierda cambia apenas el reparto

def label(p, R):
    if p == 'PSOE': return PSOEN.get(R, 'PSOE')
    if p in ('FA', 'ALT', 'POD', 'ERC', 'BNG', 'AA', 'BILDU', 'GBAI'): return name(p, R)
    if p == 'PP' and R == 'NAV': return 'UPN-PP'
    return OTHERN.get(p, p)

def metric(v, o):
    x = v['eff'][o]
    return (x['dL'] + x['dL_close']) / 2

def rels(v):
    m = {o: metric(v, o) for o in v['eff']}
    mx = max(m.values())
    return m, mx, {o: (x / mx if mx > 1e-9 else 0.0) for o, x in m.items()}

def level(r):
    return 'max' if r >= 0.9 else 'alto' if r >= 0.6 else 'bajo' if r >= 0.3 else 'nulo'

out = []
for c, v in SIM['main'].items():
    R = v['region']; M = v['M']
    m, mx, rel = rels(v)
    best = max(rel, key=rel.get)
    misses = 0
    ranges = {o: [rel[o], rel[o]] for o in rel}
    for t in ALTS:
        _, mx_t, rel_t = rels(SIM[t][c])
        if rel_t.get(best, 0) < 0.9: misses += 1
        for o in rel:
            ranges[o][0] = min(ranges[o][0], rel_t.get(o, 0)); ranges[o][1] = max(ranges[o][1], rel_t.get(o, 0))
    conf = 'alta' if misses == 0 else 'media' if misses <= 3 else 'baja'
    # votos que faltan para el siguiente escaño (escenario central, participación de 2023)
    sh = {p: x for p, x in v['mean_share'].items() if p not in ('OTH', 'BLANK')}
    q = sorted([(x / k, p, k) for p, x in sh.items() if x >= 3 for k in range(1, M + 1)], reverse=True)
    qlast = q[M - 1][0]; seats = {}
    for _, p, _ in q[:M]: seats[p] = seats.get(p, 0) + 1
    opts = []
    for o in v['eff']:
        share = v['mean_share'][o]; k = seats.get(o, 0)
        need = max((k + 1) * qlast - share, (3 - share) if share < 3 else 0)
        opts.append(dict(id=o, name=label(o, R), share=round(share, 1), pseat=round(v['p_seat'][o], 2),
                         seats_now=k, need_pts=round(need, 2),
                         chg=float(Decimal(repr(m[o] * 100)).quantize(Decimal('0.1'), ROUND_HALF_UP)),  # de cada 100 resultados: escaño más para la izquierda
                         rel=round(rel[o], 2), lo=round(ranges[o][0], 2), hi=round(ranges[o][1], 2),
                         level=level(rel[o]), stable=level(ranges[o][0]) == level(ranges[o][1])))
    opts.sort(key=lambda o: (-o['rel'], -o['share']))
    def nth(p, k):
        art = 'del ' if label(p, R) in ('PP', 'PSOE', 'PSC', 'PSN-PSOE', 'PSE-EE', 'PSdeG-PSOE', 'PNV', 'BNG') else 'de '
        return f'el {k}.º {art}{label(p, R)}'
    contest = [nth(p, k) for _, p, k in q[M - 1:M + 2]]
    others = [dict(name=label(p, R), share=round(x, 1)) for p, x in sorted(sh.items(), key=lambda t: -t[1])
              if p not in v['eff'] and x >= 3]
    out.append(dict(id=c, name=ES[c], com=COM[R], seats=M, psoe=label('PSOE', R), conf=conf,
                    nocontest=mx < NO_CONTEST, contest=contest, others=others, options=opts,
                    podIn=PODIN.get(R)))
def skey(s): return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()
out.sort(key=lambda d: skey(d['name']))
json.dump(out, open(f'{S}/datos/clasificacion.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# Resumen en Markdown para METODO.md
def f(x): return f'{x:.1f}'.replace('.', ',')
rows = []
for d in out:
    best = d['options'][0]
    alt = [o for o in d['options'] if o['id'] != 'PSOE']
    top_alt = alt[0] if alt else None
    if d['nocontest']: verdict = 'Sin disputa'
    elif top_alt and top_alt['rel'] >= 0.9: verdict = 'Sí'
    elif top_alt and top_alt['rel'] >= 0.3: verdict = 'En parte'
    else: verdict = 'No'
    d['verdict'] = verdict
    rows.append((d, best, top_alt))
order = {'Sí': 0, 'En parte': 1, 'Sin disputa': 2, 'No': 3}
def seat100(ps): return '<1' if ps < 0.005 else str(round(ps * 100))
def chg100(x): return '<0,1' if x < 0.05 else f(x)
md = ['| Circunscripción (escaños) | Voto que más aporta a la izquierda | Mejor voto fuera del PSOE | Saca escaño | Escaño más para la izquierda | Escaño más con el PSOE | Confianza |',
      '|---|---|---|---|---|---|---|']
for d, best, ta in sorted(rows, key=lambda r: (order[r[0]['verdict']], skey(r[0]['name']))):
    if d['verdict'] == 'No': continue
    bests = ' o '.join(o['name'] for o in d['options'] if o['rel'] >= 0.9)
    ps = next((o for o in d['options'] if o['id'] == 'PSOE'), None)
    first = 'Sin disputa' if d['nocontest'] else bests
    tan = ta['name'] if ta else '—'
    sea = f"{seat100(ta['pseat'])} de 100" if ta else '—'
    tch = f"{chg100(ta['chg'])} de 100" if ta else '—'
    pch = f"{chg100(ps['chg'])} de 100" if ps else '—'
    md.append(f"| {d['name']} ({d['seats']}) | {first} | {tan} | {sea} | {tch} | {pch} | {d['conf']} |")
no = sorted((d['name'] for d, _, _ in rows if d['verdict'] == 'No'), key=skey)
md.append('')
md.append(f"**Solo el PSOE aporta escaños a la izquierda ({len(no)}):** " + ', '.join(no[:-1]) + ' y ' + no[-1] + '.')
open(f'{S}/datos/resumen.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
from collections import Counter
print('clasificacion:', len(out), Counter(d['verdict'] for d in out), 'escaños con Sí:', sum(d['seats'] for d in out if d['verdict'] == 'Sí'))
