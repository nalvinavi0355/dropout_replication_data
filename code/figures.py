import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
W='output/'
R=pd.read_pickle(W+'results.pkl'); T=R['tabs']
BLUE,ORANGE,INK,INK2,GRID='#2a78d6','#eb6834','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':INK2,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,
    'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.6,'axes.axisbelow':True,
    'figure.facecolor':'white','axes.facecolor':'white','savefig.dpi':300,'savefig.bbox':'tight'})

# Fig 1: dropout rate by age band and sex
t=T['sex_x_age'].loc[['15-19','20-22','23-25','26-30','31-40','41-80']]
fig,ax=plt.subplots(figsize=(6.2,3.4)); x=np.arange(len(t)); w=0.38
for i,(s,col) in enumerate([('Male',BLUE),('Female',ORANGE)]):
    b=ax.bar(x+(i-0.5)*w,t[s],w-0.03,color=col,label=s)
    for xi,v in zip(x+(i-0.5)*w,t[s]): ax.text(xi,v+0.2,f'{v:.1f}',ha='center',va='bottom',fontsize=7,color=INK2)
ax.set_xticks(x,[a+' yrs' for a in t.index]); ax.set_ylabel('Dropout rate (% of registered)'); ax.grid(axis='x',visible=False)
ax.legend(frameon=False,loc='upper left'); ax.set_title('Figure 1. Dropout rate by age group and sex',loc='left',color=INK,fontsize=10)
fig.savefig(W+'fig1_age_sex.png'); plt.close()

# Fig 2: dot plot field x sex
t=T['sex_x_field'].sort_values('Male')
fig,ax=plt.subplots(figsize=(6.2,3.8)); y=np.arange(len(t))
ax.hlines(y,t.Female,t.Male,color=GRID,lw=2,zorder=1)
ax.scatter(t.Male,y,s=42,color=BLUE,label='Male',zorder=3,edgecolor='white',lw=1)
ax.scatter(t.Female,y,s=42,color=ORANGE,label='Female',zorder=3,edgecolor='white',lw=1)
ax.set_yticks(y,t.index); ax.set_xlabel('Dropout rate (% of registered)'); ax.grid(axis='y',visible=False); ax.set_xlim(0,6)
ax.legend(frameon=False,loc='lower right'); ax.set_title('Figure 2. Dropout rate by field of study and sex',loc='left',color=INK,fontsize=10)
fig.savefig(W+'fig2_field_sex.png'); plt.close()

# Fig 3: forest plot of adjusted IRRs (Model 1, excluding provinces)
m=R['m1']; m=m[~m.term.str.startswith(('provinsi','Intercept'))].copy()
groups=[('sex','Sex (ref. female)'),('age_band','Age (ref. 20-22)'),('level','Level (ref. bachelor, S1)'),('inst_type','Institution type (ref. university)'),
        ('sector_en','Sector (ref. public, education ministry)'),('field','Field (ref. education)')]
EN={'D1-D2':'Diploma 1-2 (D1-D2)','D3':'Diploma 3 (D3)','D4 (applied bachelor)':'Applied bachelor (D4)','Professional':'Professional programme',
    'S2 (master)':'Master (S2)','S3 (doctoral)':'Doctorate (S3)','Specialist':'Medical specialist (Sp)','Akademi':'Academy','Institut':'Institute',
    'Politeknik':'Polytechnic','Sekolah Tinggi':'College (Sekolah Tinggi)','Ministry-run (PTK)':'Civil-service institutions (PTK)',
    'Private (Kemdikbud)':'Private, education ministry','Private religious':'Private, religious affairs ministry','Public religious (PTKIN etc.)':'Public, religious affairs ministry'}
rows=[]
for g,lab in groups:
    rows.append((lab,None));
    for _,r in m[m.term.str.startswith(g+':')].iterrows(): rows.append(('   '+EN.get(r.term.split(': ',1)[1],r.term.split(': ',1)[1]),r))
fig,ax=plt.subplots(figsize=(6.4,8.2)); n=len(rows)
for i,(lab,r) in enumerate(rows):
    yy=n-i
    if r is None:
        ax.text(-0.02,yy,lab.strip(),fontweight='bold',fontsize=8.2,color=INK,va='center',ha='right',transform=ax.get_yaxis_transform()); continue
    sig=r.IRR_lo>1 or r.IRR_hi<1; col=BLUE if sig else '#9a9993'
    ax.hlines(yy,r.IRR_lo,r.IRR_hi,color=col,lw=1.6); ax.plot(r.IRR,yy,'o',color=col,ms=5,mec='white',mew=0.8)
    ax.text(-0.02,yy,lab.strip(),fontsize=8,color=INK2,va='center',ha='right',transform=ax.get_yaxis_transform())
    ax.text(1.02,yy,f'{r.IRR:.2f} ({r.IRR_lo:.2f}-{r.IRR_hi:.2f})',fontsize=7.4,color=INK2,va='center',transform=ax.get_yaxis_transform())
ax.axvline(1,color=INK2,lw=0.8,ls='--'); ax.set_xscale('log'); ax.set_xlim(0.05,10)
ax.set_xticks([0.1,0.25,0.5,1,2,4,8],['0.1','0.25','0.5','1','2','4','8']); ax.set_yticks([]); ax.grid(axis='y',visible=False)
ax.set_xlabel('Adjusted incidence rate ratio (log scale), 95% CI'); ax.spines['left'].set_visible(False)
ax.set_title('Figure 3. Adjusted dropout rate ratios (Poisson model, cluster-robust CIs)',loc='right',color=INK,fontsize=10)
ax.text(0,-0.6,'Also adjusted for province (33 fixed effects). Blue = CI excludes 1.',fontsize=7,color=INK2,transform=ax.get_yaxis_transform())
ax.set_ylim(-1.2,n+1); fig.savefig(W+'fig3_forest.png'); plt.close()

# Fig 4: concentration curve across programs
cells=pd.read_pickle(W+'cells.pkl'); cells=cells[cells.nm_bp.notna()&~cells.UT]
p=cells.groupby(['npsn','kode_prodi','nm_jenj_didik'])[['dropout','registered']].sum()
fig,ax=plt.subplots(figsize=(5.2,4.2))
for key,col,lab in [('dropout',BLUE,'Dropouts'),('registered',ORANGE,'Registered students')]:
    s=np.sort(p[key].values)[::-1]; cx=np.arange(1,len(s)+1)/len(s)*100; cy=np.cumsum(s)/s.sum()*100
    ax.plot(cx,cy,color=col,lw=2,label=lab)
ax.plot([0,100],[0,100],color=INK2,lw=0.8,ls='--')
s=np.sort(p.dropout.values)[::-1]; v=s[:int(len(s)*.1)].sum()/s.sum()*100
ax.plot([10,10],[0,v],color=INK2,lw=0.8,ls=':'); ax.plot([0,10],[v,v],color=INK2,lw=0.8,ls=':'); ax.plot(10,v,'o',color=BLUE,ms=5,mec='white')
ax.text(1,v+1.5,f'{v:.0f}%',fontsize=8,color=INK,va='bottom'); ax.text(11,2,'10%',fontsize=8,color=INK,va='bottom')
ax.set_xlabel('Cumulative % of study programs (each ranked by its own count)'); ax.set_ylabel('Cumulative % of total'); ax.set_xlim(0,100); ax.set_ylim(0,101)
ax.legend(frameon=False,loc='lower right'); ax.set_title('Figure 4. Concentration of dropouts across study programs',loc='left',color=INK,fontsize=10)
fig.savefig(W+'fig4_concentration.png'); plt.close()
print('ok')
