import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
W='output/'
c=pd.read_pickle(W+'cells.pkl')
c=c[c.nm_bp.notna()].copy()   # drop 376 DO in programs without registered students

# harmonized categories
lvl={'D1':'D1-D2','D2':'D1-D2','D3':'D3','D4':'D4 (applied bachelor)','S1':'S1 (bachelor)','S2':'S2 (master)','S2 Terapan':'S2 (master)',
     'S3':'S3 (doctoral)','S3 Terapan':'S3 (doctoral)','Profesi':'Professional','Sp-1':'Specialist','Sp-2':'Specialist'}
c['level']=c.nm_jenj_didik.map(lvl)
c['inst_type']=c.nm_bp.replace({'Akademi Komunitas':'Akademi'})
sec={'Negeri':'Public (Kemdikbud)','Swasta':'Private (Kemdikbud)','PTA Negeri':'Public religious (PTKIN etc.)','PTA Swasta':'Private religious','PTK':'Ministry-run (PTK)'}
c['sector_en']=c.sector.map(sec)
fld={'Pendidikan':'Education','Kesehatan':'Health','MIPA':'Natural sciences & math','Humaniora':'Humanities','Agama':'Religion',
     'Sosial':'Social sciences','Ekonomi':'Economics & business','Pertanian':'Agriculture','Seni':'Arts','Teknik':'Engineering'}
c['field']=c.bidang.map(fld)
c['sex']=c.jk.map({'L':'Male','P':'Female'})
c['stem']=c.stem.str.strip()

out={}
def rate_tab(df,by):
    t=df.groupby(by,observed=True)[['dropout','registered']].sum()
    t['rate_pct']=t.dropout/t.registered*100
    return t
allrate=c.dropout.sum()/c.registered.sum()*100
nout=c[~c.UT]
out['national_all']=dict(dropout=c.dropout.sum(),registered=c.registered.sum(),rate=allrate)
out['national_exUT']=dict(dropout=nout.dropout.sum(),registered=nout.registered.sum(),rate=nout.dropout.sum()/nout.registered.sum()*100)
out['UT']=dict(dropout=c[c.UT].dropout.sum(),registered=c[c.UT].registered.sum())
out['n_programs']=int(c.groupby(['npsn','kode_prodi','nm_jenj_didik']).ngroups); out['n_inst']=int(c.npsn.nunique())
out['n_programs_exUT']=int(nout.groupby(['npsn','kode_prodi','nm_jenj_didik']).ngroups); out['n_inst_exUT']=int(nout.npsn.nunique())

D=nout  # descriptive base: excluding UT
tabs={}
for name,by in [('sex','sex'),('age_band','age_band'),('level','level'),('inst_type','inst_type'),('sector','sector_en'),('field','field'),('stem','stem'),('province','provinsi')]:
    tabs[name]=rate_tab(D[D[by].notna()] if by!='age_band' else D[D.age_band!='invalid'],by).sort_values('rate_pct',ascending=False)
tabs['sex_x_age']=rate_tab(D[(D.age_band!='invalid')&D.sex.notna()],['age_band','sex']).rate_pct.unstack()
tabs['sex_x_field']=rate_tab(D[D.sex.notna()],['field','sex']).rate_pct.unstack().sort_values('Male',ascending=False)
tabs['sex_x_stem']=rate_tab(D[D.sex.notna()],['stem','sex']).rate_pct.unstack()
tabs['level_x_sector']=rate_tab(D,['level','sector_en']).rate_pct.unstack()
# program-level distribution
P=D.groupby(['npsn','kode_prodi','nm_jenj_didik','nama_pt','nm_prodi','level','sector_en','field','provinsi'])[['dropout','registered']].sum().reset_index()
P['rate_pct']=P.dropout/P.registered*100
out['prog_zero_do_share']=float((P.dropout==0).mean()*100)
P100=P[P.registered>=100]
out['prog100_n']=len(P100); out['prog100_median']=float(P100.rate_pct.median()); out['prog100_p90']=float(P100.rate_pct.quantile(.9))
# concentration: share of dropouts in top 10% programs by dropout count
s=P.dropout.sort_values(ascending=False); out['top10pct_prog_share']=float(s.head(int(len(s)*.1)).sum()/s.sum()*100)
I=D.groupby(['npsn','nama_pt','sector_en'])[['dropout','registered']].sum().reset_index(); I['rate_pct']=I.dropout/I.registered*100
si=I.dropout.sort_values(ascending=False); out['top10pct_inst_share']=float(si.head(int(len(si)*.1)).sum()/si.sum()*100)
out['inst_zero_do']=int((I.dropout==0).sum())
tabs['top_inst_by_count']=I.sort_values('dropout',ascending=False).head(20).set_index('nama_pt')

# ---------------- model: Poisson with log(registered) offset, cluster-robust SE by institution
M=D[(D.age_band!='invalid')&D.sex.notna()&(D.registered>0)].copy()
out['model_cells']=len(M); out['model_dropout']=M.dropout.sum(); out['model_dropped_DO_reg0']=D[(D.registered==0)].dropout.sum()
refs={'sex':'Female','age_band':'20-22','level':'S1 (bachelor)','inst_type':'Universitas','sector_en':'Public (Kemdikbud)','field':'Education','provinsi':'Jawa Timur'}
def design(df,terms,inter=None):
    cols=[np.ones(len(df))]; names=['Intercept']
    for t in terms:
        for lv in sorted(df[t].dropna().unique()):
            if lv==refs.get(t): continue
            cols.append((df[t]==lv).values.astype(float)); names.append(f'{t}: {lv}')
    if inter:
        a,av,b=inter
        for lv in sorted(df[b].unique()):
            if lv==refs.get(b): continue
            cols.append(((df[a]==av)&(df[b]==lv)).values.astype(float)); names.append(f'{a}={av} x {b}: {lv}')
    return np.column_stack(cols),names
def poisson(X,y,off,groups,maxit=50):
    b=np.zeros(X.shape[1]); b[0]=np.log(y.sum()/np.exp(off).sum())
    for _ in range(maxit):
        eta=X@b+off; mu=np.exp(eta); z=eta-off+(y-mu)/mu
        XtW=X.T*mu; bn=np.linalg.solve(XtW@X,XtW@z)
        if np.max(np.abs(bn-b))<1e-9: b=bn; break
        b=bn
    mu=np.exp(X@b+off); A=np.linalg.inv((X.T*mu)@X)
    sc=X*(y-mu)[:,None]
    G=pd.DataFrame(sc).groupby(groups).sum().values; g=G.shape[0]
    V=A@(G.T@G)@A*g/(g-1)
    pearson=((y-mu)**2/mu).sum()/(len(y)-X.shape[1])
    ll=(y*np.log(np.where(mu>0,mu,1))-mu).sum()
    return b,np.sqrt(np.diag(V)),pearson,mu
def fit(df,terms,inter=None,label=''):
    X,names=design(df,terms,inter); y=df.dropout.values; off=np.log(df.registered.values)
    b,se,disp,mu=poisson(X,y,off,df.npsn.values)
    z=b/se; p=2*stats.norm.sf(np.abs(z))
    res=pd.DataFrame({'term':names,'coef':b,'se_robust':se,'IRR':np.exp(b),'IRR_lo':np.exp(b-1.96*se),'IRR_hi':np.exp(b+1.96*se),'p':p})
    print(label,'cells',len(df),'pearson dispersion',round(disp,2),'clusters',df.npsn.nunique())
    return res,disp
base=['sex','age_band','level','inst_type','sector_en','field','provinsi']
m1,d1=fit(M,base,label='M1 main')
refs['stem']='NON STEM'
m2,d2=fit(M,[t for t in base if t!='field']+['stem'],inter=('sex','Male','stem'),label='M2 STEM x sex')
m2b,d2b=fit(M,base,inter=('sex','Male','stem'),label='M2b stem x sex within fields')
m3,d3=fit(M,base,inter=('sex','Male','field'),label='M3 field x sex')
MU=D[(D.age_band!='invalid')&D.sex.notna()&(D.registered>0)].copy()
MALL=c[(c.age_band!='invalid')&c.sex.notna()&(c.registered>0)].copy()
m4,d4=fit(MALL,base,label='S1 incl UT')
# sensitivity: only programs with >=50 registered
big=M.groupby(['npsn','kode_prodi','nm_jenj_didik']).registered.transform('sum')>=50
m5,d5=fit(M[big],base,label='S2 programs>=50')
out['dispersion']=dict(M1=d1,M2=d2,M3=d3,S_inclUT=d4,S_big=d5)

# ---------------- save
with pd.ExcelWriter(W+'dropout_analysis_tables.xlsx') as xw:
    pd.DataFrame([out['national_all'],out['national_exUT'],out['UT']],index=['All institutions','Excluding Universitas Terbuka','Universitas Terbuka']).to_excel(xw,sheet_name='National')
    for k,v in tabs.items(): v.round(3).to_excel(xw,sheet_name=k[:31])
    for k,v in [('M1_main',m1),('M2_stem_x_sex',m2),('M2b_stem_x_sex_fieldFE',m2b),('M3_field_x_sex',m3),('S1_incl_UT',m4),('S2_programs_ge50',m5)]: v.round(4).to_excel(xw,sheet_name=k,index=False)
    P.sort_values('dropout',ascending=False).to_excel(xw,sheet_name='program_level_data',index=False)
pd.to_pickle(dict(out=out,tabs=tabs,m1=m1,m2=m2,m2b=m2b,m3=m3,m4=m4,m5=m5),W+'results.pkl')
json.dump(out,open(W+'summary.json','w'),indent=1,default=float)
print(json.dumps(out,indent=1,default=float))
