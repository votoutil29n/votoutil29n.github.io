"""Impacto real del voto en las generales de 2023, por circunscripción.

Para cada provincia: votos y escaños de cada lista, quién ganó el último escaño y por cuántos
votos, y cuántos votos le faltaron a cada lista para un escaño más.
Uso: python3 modelo/impacto2023.py <raíz del repositorio>
"""
import json, sys
import pandas as pd
S = sys.argv[1]
ns = {}; exec(open(f'{S}/modelo/nombres.py', encoding='utf-8').read(), ns); ES = ns['ES']
src = open(f'{S}/modelo/base.py', encoding='utf-8').read(); bns = {}
exec(src[src.index('def code(p):'):src.index("df['code']")], {'pd': pd}, bns); code = bns['code']
lg = pd.read_csv(f'{S}/datos/res2023_long.csv'); lg['code'] = lg.party.map(code)
sim = json.load(open(f'{S}/datos/sim_main.json', encoding='utf-8'))
REG = {c: v['region'] for c, v in sim.items()}
SEATS23 = {c: v['M'] for c, v in sim.items()}; SEATS23['Madrid'] = 37; SEATS23['Cádiz'] = 9
LEFT = {'PSOE', 'SUMAR', 'ERC', 'BILDU', 'BNG', 'CUP', 'NC', 'GBAI', 'AA'}
PSOEN = {'CAT': 'PSC', 'GAL': 'PSdeG-PSOE', 'PV': 'PSE-EE', 'NAV': 'PSN-PSOE'}
SUML = {'CAT': 'Sumar-En Comú Podem', 'VAL': 'Sumar-Compromís', 'GAL': 'Sumar Galicia', 'BAL': 'Sumar-Més',
        'ARA': 'Sumar Aragón', 'AND': 'Sumar Andalucía', 'CAN': 'Sumar Canarias'}
NAMES = {'PP': 'PP', 'VOX': 'Vox', 'ERC': 'ERC', 'JUNTS': 'Junts', 'BILDU': 'EH Bildu', 'PNV': 'PNV', 'BNG': 'BNG',
         'CC': 'Coalición Canaria', 'UPN': 'UPN', 'NC': 'Nueva Canarias', 'CUP': 'CUP', 'GBAI': 'Geroa Bai',
         'SY': 'Soria ¡Ya!', 'UPL': 'UPL', 'XAV': 'Por Ávila', 'JM': 'Jaén Merece Más', 'AA': 'Adelante Andalucía'}
def label(k, R, c):
    if k == 'PSOE': return PSOEN.get(R, 'PSOE')
    if k == 'SUMAR': return SUML.get(R, 'Sumar')
    if k == 'EXISTE': return 'Teruel Existe' if c == 'Teruel' else 'Aragón Existe'
    return NAMES.get(k, k)
out = []
for c in sim:
    R = REG[c]; M = SEATS23[c]; d = lg[lg.const == c]
    valid = int(d[d.code == 'VALID'].votes.sum())
    v = d[~d.code.isin(['VALID', 'BLANK', 'OTH'])].groupby('code').votes.sum().to_dict()
    thr = 0.03 * valid
    q = sorted([(vv / k, p, k) for p, vv in v.items() if vv >= thr for k in range(1, M + 1)], reverse=True)
    won = q[:M]; seats = {}
    for _, p, _ in won: seats[p] = seats.get(p, 0) + 1
    qlast = won[-1][0]; last_party = won[-1][1]
    runner = q[M] if len(q) > M else None
    def short(p):
        vv = v[p]; k = seats.get(p, 0)
        need = (k + 1) * qlast - vv
        if vv < thr: need = max(need, thr - vv)
        return int(need) + 1
    lists = []
    for p, vv in sorted(v.items(), key=lambda t: -t[1]):
        if vv / valid < 0.01 and seats.get(p, 0) == 0: continue
        lists.append(dict(id=p, name=label(p, R, c), votes=int(vv), pct=round(vv / valid * 100, 1),
                          seats=seats.get(p, 0), left=p in LEFT, short=short(p)))
    left_seats = sum(seats.get(p, 0) for p in LEFT)
    out.append(dict(id=c, name=ES[c], seats=M, valid=valid, lists=lists, left_seats=left_seats,
                    last=dict(party=label(last_party, R, c), nth=seats[last_party],
                              runner=label(runner[1], R, c) if runner else None,
                              runner_nth=runner[2] if runner else None,
                              margin=short(runner[1]) if runner else None)))
json.dump(out, open(f'{S}/datos/impacto2023.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
real = lg[~lg.code.isin(['VALID'])].copy(); real['s'] = pd.to_numeric(real.seats, errors='coerce').fillna(0)
mism = 0
for x in out:
    rs = real[real.const == x['id']].groupby('code').s.sum()
    for l in x['lists']:
        if int(rs.get(l['id'], 0)) != l['seats']: mism += 1
print('impacto2023:', len(out), 'circunscripciones; discrepancias con escaños reales:', mism)
