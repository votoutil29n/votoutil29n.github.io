import io, pandas as pd, re, sys, json
S=sys.argv[1]
names=open(f'{S}/datos/names.txt').read().split('\n')
rows=[]
for n in names:
    html=open(f'{S}/datos/wp/{n}_(Congress_of_Deputies_constituency).html',encoding='utf-8').read()
    ts=pd.read_html(io.StringIO(html), match='23 July 2023')
    t=ts[0].iloc[:, [1,2,3,5]]; t.columns=['party','votes','pct','seats']
    valid=None
    for _,r in t.iterrows():
        p=r.party
        if not isinstance(p,str): continue
        if p.startswith('Valid votes'): valid=int(str(r.votes).replace(',',''))
        if p.startswith(('Valid','Invalid','Votes cast','Abstentions','Registered','Total','Sources')) : continue
        try: v=int(str(r.votes).replace(',','')); pc=float(r.pct)
        except: continue
        rows.append(dict(const=n,party=p,votes=v,pct=pc,seats=r.seats))
    rows.append(dict(const=n,party='__VALID__',votes=valid,pct=100.0,seats=None))
df=pd.DataFrame(rows)
df.to_csv(f'{S}/datos/res2023_long.csv',index=False)
# list distinct party labels with total votes
g=df[df.party!='__VALID__'].groupby('party').votes.sum().sort_values(ascending=False)
print(g.head(60).to_string())
print('valid total', df[df.party=='__VALID__'].votes.sum())
