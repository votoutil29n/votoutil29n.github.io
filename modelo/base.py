import pandas as pd, re, sys
S=sys.argv[1]
df=pd.read_csv(f'{S}/datos/res2023_long.csv')
def code(p):
    if p=='__VALID__': return 'VALID'
    if p.startswith('Blank ballots'): return 'BLANK'
    if p.startswith("People's Party"): return 'PP'
    if 'PSOE' in p: return 'PSOE'
    if p.startswith('Vox'): return 'VOX'
    if 'Sumar' in p: return 'SUMAR'
    if 'ERC' in p: return 'ERC'
    if 'Junts' in p: return 'JUNTS'
    if 'EH Bildu' in p: return 'BILDU'
    if 'PNV' in p: return 'PNV'
    if '(BNG)' in p: return 'BNG'
    if '(CCa)' in p: return 'CC'
    if '(UPN)' in p: return 'UPN'
    if 'NC–BC' in p: return 'NC'
    if 'CUP' in p: return 'CUP'
    if 'GBai' in p: return 'GBAI'
    if 'Exist' in p: return 'EXISTE'
    if '(SY)' in p: return 'SY'
    if 'Adelante' in p: return 'AA'
    if '(UPL)' in p: return 'UPL'
    if '(XAV)' in p: return 'XAV'
    if '(JM+)' in p: return 'JM'
    return 'OTH'
df['code']=df.party.map(code)
w=df.pivot_table(index='const',columns='code',values='votes',aggfunc='sum',fill_value=0)
sh=w.drop(columns='VALID').div(w.VALID,axis=0)*100
sh['VALID']=w.VALID
sh.to_csv(f'{S}/datos/base2023.csv')
nat=w.drop(columns='VALID').sum()/w.VALID.sum()*100
print(nat.round(2).sort_values(ascending=False).to_string())
reg={'Galicia':['A Coruña','Lugo','Ourense','Pontevedra'],'Catalonia':['Barcelona','Girona','Lleida','Tarragona'],
'Valencia':['Alicante','Castellón','Valencia'],'Aragon':['Huesca','Teruel','Zaragoza'],
'Andalusia':['Almería','Cádiz','Córdoba','Granada','Huelva','Jaén','Málaga','Seville'],'Madrid':['Madrid'],'Basque':['Álava','Biscay','Gipuzkoa'],'Canarias':['Las Palmas','Santa Cruz de Tenerife'],'Baleares':['Balearic Islands']}
for r,cs in reg.items():
    ww=w.loc[cs]; s=(ww.drop(columns='VALID').sum()/ww.VALID.sum()*100)
    print(r, {k:round(v,1) for k,v in s.items() if v>1.5}, 'natshare%', round(ww.VALID.sum()/w.VALID.sum()*100,1))
