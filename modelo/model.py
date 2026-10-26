import numpy as np, pandas as pd, sys, json
S=sys.argv[1]; N=int(sys.argv[2]) if len(sys.argv)>2 else 20000
OV=json.loads(sys.argv[5]) if len(sys.argv)>5 else {}
OV0=json.loads(sys.argv[5]) if len(sys.argv)>5 else {}
rng=np.random.default_rng(OV0.get('SEED',29))
b=pd.read_csv(f'{S}/datos/base2023.csv').set_index('const')
# Vox did not stand in S.C. de Tenerife in 2023: use Nov-2019 share (11.54) scaled by national Vox 2023/2019 (12.39/15.09); 80% taken from PP base
_vtf=11.54*12.39/15.09
b.loc['Santa Cruz de Tenerife','VOX']=_vtf; b.loc['Santa Cruz de Tenerife','PP']-=0.8*_vtf
VALID=b.pop('VALID')
SEATS={'Madrid':38,'Barcelona':32,'Valencia':16,'Alicante':12,'Seville':12,'Málaga':11,'Murcia':10,
'A Coruña':8,'Balearic Islands':8,'Biscay':8,'Cádiz':8,'Las Palmas':8,
'Asturias':7,'Granada':7,'Pontevedra':7,'Zaragoza':7,'Santa Cruz de Tenerife':7,
'Almería':6,'Córdoba':6,'Gipuzkoa':6,'Girona':6,'Tarragona':6,'Toledo':6,
'Badajoz':5,'Cantabria':5,'Castellón':5,'Ciudad Real':5,'Huelva':5,'Jaén':5,'Navarre':5,'Valladolid':5,
'Álava':4,'Albacete':4,'Burgos':4,'Cáceres':4,'La Rioja':4,'León':4,'Lleida':4,'Lugo':4,'Ourense':4,'Salamanca':4,
'Ávila':3,'Cuenca':3,'Guadalajara':3,'Huesca':3,'Palencia':3,'Segovia':3,'Teruel':3,'Zamora':3,'Soria':2,'Ceuta':1,'Melilla':1}
assert sum(SEATS.values())==350, sum(SEATS.values())
REG={}
for r,cs in {'GAL':['A Coruña','Lugo','Ourense','Pontevedra'],'CAT':['Barcelona','Girona','Lleida','Tarragona'],
'VAL':['Alicante','Castellón','Valencia'],'ARA':['Huesca','Teruel','Zaragoza'],
'AND':['Almería','Cádiz','Córdoba','Granada','Huelva','Jaén','Málaga','Seville'],'MAD':['Madrid'],
'PV':['Álava','Biscay','Gipuzkoa'],'CAN':['Las Palmas','Santa Cruz de Tenerife'],'BAL':['Balearic Islands'],'NAV':['Navarre'],
'CYL':['Ávila','Burgos','León','Palencia','Salamanca','Segovia','Soria','Valladolid','Zamora'],
'CLM':['Albacete','Ciudad Real','Cuenca','Guadalajara','Toledo'],'EXT':['Badajoz','Cáceres'],'AST':['Asturias'],'CANT':['Cantabria'],
'RIO':['La Rioja'],'MUR':['Murcia'],'CEU':['Ceuta'],'MEL':['Melilla']}.items():
    for c in cs: REG[c]=r
assert set(REG)==set(b.index)
AA26={'Almería':3.1,'Cádiz':14.3,'Córdoba':8.3,'Granada':6.8,'Huelva':8.0,'Jaén':4.4,'Málaga':9.3,'Seville':12.9}
# --- 2026 lists per constituency ---
# party codes 2026: PP VOX SALF PSOE FA POD ALT(single alt list: Compromis-FV / UPC) ERC JUNTS BILDU PNV BNG CC GBAI EXISTE SY AA OTH BLANK
LEFT={'PSOE','FA','POD','ALT','ERC','BILDU','BNG','AA','GBAI'}
RIGHT={'PP','VOX','SALF'}
# national ratios (pre-calibration) and regional blends
nat={'PP':0.97,'PSOE':0.838,'VOX':1.53,'ALTSP':0.79}
regadj={ # multiplicative adjustments relative to national ratio for region
 'GAL':{'PP':0.947/0.97,'PSOE':0.867/0.838,'VOX':1.63/1.53,'ALTSP':0.69/0.79},
 'VAL':{'PP':0.99/0.97,'PSOE':0.82/0.838,'VOX':1.48/1.53,'ALTSP':0.77/0.79},
 'ARA':{'PP':0.96/0.97,'PSOE':0.90/0.838,'VOX':1.36/1.53,'ALTSP':0.88/0.79},
 'CAT':{'PP':0.975/0.97,'PSOE':0.85/0.838,'VOX':1.55/1.53,'ALTSP':0.43/0.79},
 'AND':{'ALTSP':0.75},
}
def mean_shares(c, r):
    s=b.loc[c]; R=REG[c]; adj=regadj.get(R,{})
    g=lambda p: nat[p]*adj.get(p,1.0)
    out={}
    pp=s.PP+(s.UPN if R=='NAV' else 0)
    out['PP']=pp*g('PP')*r['PP']; out['PSOE']=s.PSOE*g('PSOE')*r['PSOE']; out['VOX']=s.VOX*g('VOX')*r['VOX']
    alt=s.SUMAR*g('ALTSP')*r['ALTSP']
    fpod=r['FPOD']
    if R=='CAT':
        out['FA']=alt   # Comuns-Front Ampli; Podem inside ERC
        out['ERC']=s.ERC*OV.get('ERC_RATIO',1.25)*r['ERC']; out['JUNTS']=s.JUNTS*0.95*r['JUNTS']
    elif R=='VAL':
        out['ALT']=alt  # Compromis-Front Valencia (incl. Podemos, EUPV)
    elif R=='CAN':
        ncs=OV.get('NC_UPC',0.5)
        out['ALT']=alt+s.NC*ncs*r['NC']  # Unidad del Pueblo Canario (NC minus Primero Canarias split)
        out['CC']=(s.CC+s.NC*(1-ncs))*0.85*r['CC']  # CC with Municipalistas Primero Canarias
    elif R=='BAL':
        if OV.get('MERGE'): out['FA']=alt
        else: out['FA']=alt*(1-fpod); out['POD']=alt*fpod   # Ara Mes-Front Ampli + Podemos
    elif c=='Teruel':
        if OV.get('MERGE'): out['FA']=alt*(1-fpod)*0.5+alt*fpod
        else: out['FA']=alt*(1-fpod)*0.5; out['POD']=alt*fpod
    else:
        if OV.get('MERGE'): out['FA']=alt
        else: out['FA']=alt*(1-fpod); out['POD']=alt*fpod
    if R=='PV': out['BILDU']=s.BILDU*1.03*r['BILDU']; out['PNV']=s.PNV*0.80*r['PNV']
    if R=='NAV': out['BILDU']=s.BILDU*1.03*r['BILDU']; out['GBAI']=s.GBAI*1.0*r['GBAI']
    if R=='GAL': out['BNG']=s.BNG*1.45*r['BNG']
    if R=='AND': out['AA']=OV.get('AA_TOTAL',4.5)*AA26[c]/9.6*r['AA']
    if R=='ARA': out['EXISTE']=s.EXISTE*1.0*r['EXISTE']
    if c=='Soria': out['SY']=s.SY*1.0*r['SY']
    out['SALF']=1.6*r['SALF']
    out['OTH']=max(s.OTH,0)+ (s.PACMA if 'PACMA' in s else 0)
    out['BLANK']=s.BLANK
    return out
PARTIES=['PP','VOX','SALF','PSOE','FA','POD','ALT','ERC','JUNTS','BILDU','PNV','BNG','CC','GBAI','EXISTE','SY','AA','OTH','BLANK']
consts=list(b.index)
# ---------- calibration (central scenario, r=1) ----------
ones={k:1.0 for k in ['PP','PSOE','VOX','ALTSP','ERC','JUNTS','BILDU','PNV','BNG','CC','NC','GBAI','EXISTE','SY','AA','SALF']}; ones['FPOD']=OV.get('FPOD',0.33)
def national(r):
    tot={p:0.0 for p in PARTIES}; W=0
    for c in consts:
        m=mean_shares(c,r); z=sum(m.values())
        for p,v in m.items(): tot[p]+=v/z*100*VALID[c]
        W+=VALID[c]
    return {p:v/W for p,v in tot.items()}
target={'PP':OV.get('PP',32.0),'PSOE':OV.get('PSOE',26.5),'VOX':OV.get('VOX',18.9)}
for it in range(30):
    n=national(ones)
    for p,t in target.items(): ones[p]*= t/n[p]
    altn=n['FA']+n['POD']+n['ALT']; ones['ALTSP']*=OV.get('ALT_TARGET',10.0)/altn
n=national(ones)
print('calibrated national:',{k:round(v,2) for k,v in n.items() if v>0.3}, 'alt', round(n['FA']+n['POD']+n['ALT'],2))
cal=dict(ones)
json.dump(cal,open(f'{S}/datos/cal.json','w'))
# ---------- Monte Carlo ----------
sd_nat={'PP':0.06,'PSOE':0.07,'VOX':0.09,'ALTSP':0.15,'ERC':0.13,'JUNTS':0.12,'BILDU':0.10,'PNV':0.12,'BNG':0.15,'CC':0.20,'NC':0.25,'GBAI':0.30,'EXISTE':0.30,'SY':0.20,'AA':0.35,'SALF':0.30}
SD_REG=0.08; SD_PROV=0.10; SD_BLOC=float(sys.argv[3]) if len(sys.argv)>3 else 0.05
regions=sorted(set(REG.values()))
z=rng.normal(0,1,N)
blocR=np.exp(z*SD_BLOC); blocL=np.exp(-z*SD_BLOC)
natdraw={p:np.exp(rng.normal(0,sd,N)-sd**2/2) for p,sd in sd_nat.items()}
for p in ['PP','VOX','SALF']: natdraw[p]=natdraw[p]*blocR
for p in ['PSOE','ALTSP','ERC','BILDU','BNG','AA','NC','GBAI']: natdraw[p]=natdraw[p]*blocL
fpod=np.clip(rng.normal(OV.get('FPOD',0.33),0.07,N),0.1,0.7)
regdraw={(R,p):np.exp(rng.normal(0,SD_REG,N)-SD_REG**2/2) for R in regions for p in sd_nat}
def dhondt(M, X, cand, thr=3.0):
    if X.shape[0]>40000:
        return np.vstack([dhondt(M, X[i:i+40000], cand, thr) for i in range(0, X.shape[0], 40000)])
    # cand: boolean mask of columns that can win seats (OTH/BLANK cannot); threshold on share of valid votes
    Xt=np.where((X>=thr)&cand[None,:], X, 0.0)
    q=(Xt[:,:,None]/np.arange(1,M+1)[None,None,:]).reshape(X.shape[0],-1)
    idx=np.argpartition(-q, M-1, axis=1)[:,:M]
    party=idx//M
    seats=np.zeros(X.shape, dtype=np.int16)
    np.add.at(seats,(np.repeat(np.arange(X.shape[0]),M),party.ravel()),1)
    return seats
DELTA=0.5
natseats={p:np.zeros(N) for p in PARTIES}
acc={}
for c in consts:
    R=REG[c]; M=SEATS[c]
    r={p:cal[p]*natdraw[p]*regdraw[(R,p)] for p in sd_nat}; r['FPOD']=fpod
    m=mean_shares(c,r)
    plist=[p for p in PARTIES if p in m]
    cand=np.array([p not in ('OTH','BLANK') for p in plist])
    X=np.column_stack([np.asarray(m[p])*np.ones(N) for p in plist])
    for j,p in enumerate(plist):
        if p not in ('OTH','BLANK'): X[:,j]*=np.exp(rng.normal(0,SD_PROV,N)-SD_PROV**2/2)
    X=X/X.sum(1,keepdims=True)*100
    base=dhondt(M,X,cand)
    for j,p in enumerate(plist): natseats[p]+=base[:,j]
    Lc=[j for j,p in enumerate(plist) if p in LEFT]; Rc=[j for j,p in enumerate(plist) if p in RIGHT]
    L0=base[:,Lc].sum(1); R0=base[:,Rc].sum(1)
    effs={}
    for o in [p for p in plist if p in LEFT]:
        Xb=X.copy(); j=plist.index(o); Xb[:,j]+=DELTA
        nb=dhondt(M,Xb,cand)
        effs[o]=((nb[:,Lc].sum(1)-L0).astype(np.int8),(nb[:,Rc].sum(1)-R0).astype(np.int8),(nb[:,j]-base[:,j]).astype(np.int8))
    acc[c]=dict(M=M,R=R,plist=plist,
        mean_share={p:float(X[:,j].mean()) for j,p in enumerate(plist)},
        p10={p:float(np.percentile(X[:,j],10)) for j,p in enumerate(plist)},
        p90={p:float(np.percentile(X[:,j],90)) for j,p in enumerate(plist)},
        exp_seats={p:float(base[:,j].mean()) for j,p in enumerate(plist)},
        p_seat={p:float((base[:,j]>=1).mean()) for j,p in enumerate(plist)},
        seats_arr={p:base[:,j].astype(np.int8) for j,p in enumerate(plist)}, effs=effs)
    del X, base
RB=natseats['PP']+natseats['VOX']+natseats['SALF']
close=(RB>=168)&(RB<=184)
print('bloc sd',SD_BLOC,' P(PP+Vox+SALF>=176)=',round(float((RB>=176).mean()),3),' P(>=177)',round(float((RB>=177).mean()),3),' n close',int(close.sum()), ' mean right', round(float(RB.mean()),1))
res={}
for c,v in acc.items():
    eff={}
    for o,(dL,dR,dO) in v['effs'].items():
        eff[o]={'dL':float(dL.mean()),'dR':float(dR.mean()),'dOwn':float(dO.mean()),
                'dR_close':float(dR[close].mean()),'dL_close':float(dL[close].mean()),
                'se_close':float(dR[close].std()/np.sqrt(close.sum()))}
    res[c]={'M':v['M'],'region':v['R'],'mean_share':v['mean_share'],'p10':v['p10'],'p90':v['p90'],
            'exp_seats':v['exp_seats'],'p_seat':v['p_seat'],
            'exp_seats_close':{p:float(a[close].mean()) for p,a in v['seats_arr'].items()},'eff':eff}
tag=sys.argv[4] if len(sys.argv)>4 else 'main'
json.dump(res,open(f'{S}/datos/sim_{tag}.json','w'),ensure_ascii=False,indent=1)
tot={p:float(v.mean()) for p,v in natseats.items() if v.mean()>0.05}
print('national seats:',{k:round(v,1) for k,v in sorted(tot.items(),key=lambda x:-x[1])})
L=sum(natseats[p] for p in LEFT)
print('mean left',round(float(L.mean()),1),' P(left>=176)',round(float((L>=176).mean()),4), ' P(left+PNV+Junts+CC>=176)', round(float(((L+natseats['PNV']+natseats['JUNTS']+natseats['CC'])>=176).mean()),4))
