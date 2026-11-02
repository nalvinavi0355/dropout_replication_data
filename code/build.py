import pandas as pd, numpy as np
S='data/'
d=pd.read_csv(S+'do.csv',low_memory=False,dtype={'npsn':str,'kode_prodi':str})
r=pd.read_csv(S+'reg.csv',low_memory=False,dtype={'npsn':str,'kode_prodi':str})
d=d.rename(columns={'jumlah_mhs_Do':'n'}); r=r.rename(columns={'jumlah_mhs':'n'})
d=d[d.n.notna()].copy(); r=r[r.n.notna()].copy()
for x in (d,r):
    x['npsn']=x.npsn.str.strip().str.zfill(6); x['kode_prodi']=x.kode_prodi.astype(str).str.strip()
    x['usia']=pd.to_numeric(x.usia,errors='coerce')
    x['age_band']=pd.cut(x.usia,[14,19,22,25,30,40,80],labels=['15-19','20-22','23-25','26-30','31-40','41-80']).astype(object).fillna('invalid').astype(str)
    x['jk']=x.jk.replace('*','unknown')
d['sector']=d.kelompok_lemb; r['sector']=r.kelompok_lemb2
key=['npsn','kode_prodi','nm_jenj_didik']
# program attributes from registered file (complete)
attr=r.groupby(key).agg(nama_pt=('nama_pt','first'),nm_prodi=('nm_prodi','first'),nm_bp=('nm_bp','first'),sector=('sector','first'),
    provinsi=('provinsi_pt','first'),kabupaten=('Kabupaten_pt','first'),bidang=('nm_kel_bidang','first'),stem=('a_stem','first')).reset_index()
ck=key+['jk','age_band']
cd=d.groupby(ck).n.sum().rename('dropout'); cr=r.groupby(ck).n.sum().rename('registered')
cells=pd.concat([cd,cr],axis=1).fillna(0).reset_index().merge(attr,on=key,how='left')
cells['provinsi']=cells.provinsi.str.replace('Prov. ','',regex=False)
cells['UT']=cells.npsn.eq('001031')
print('cells',len(cells),'DO',cells.dropout.sum(),'REG',cells.registered.sum())
print('DO in cells with reg=0',cells.loc[cells.registered==0,'dropout'].sum(), (cells.registered==0).sum())
print('attr missing',cells.nm_bp.isna().sum())
# check sector consistency DO vs REG
chk=d.groupby(key).sector.first().reset_index().merge(attr[key+['sector']],on=key,suffixes=('_do','_reg'))
print('sector mismatch',(chk.sector_do!=chk.sector_reg).sum())
chk=d.groupby(key).nm_kel_bidang.first().reset_index().merge(attr[key+['bidang']],on=key)
print('bidang mismatch',(chk.nm_kel_bidang!=chk.bidang).sum())
import os; os.makedirs('output',exist_ok=True); cells.to_pickle('output/cells.pkl')
prog=cells.groupby(key+['nama_pt','nm_prodi','nm_bp','sector','provinsi','kabupaten','bidang','stem','UT'])[['dropout','registered']].sum().reset_index()
prog.to_pickle('output/prog.pkl'); print('programs',len(prog), 'programs with 0 reg',(prog.registered==0).sum(),'DO there',prog.loc[prog.registered==0,'dropout'].sum())
print('institutions',prog.npsn.nunique())
