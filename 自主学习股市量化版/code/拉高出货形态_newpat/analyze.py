import pandas as pd,numpy as np
from scipy.stats import mannwhitneyu
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
ev=pd.read_csv('events_all.csv'); ev['y']=ev.group.isin(['crash','crash2']).astype(int)
d=ev[ev.group!='pending']
F=['volB_vs_P','volP_vs_A','volH_vs_50','volmaxH5_vs_50','ushadow_days_H5','hivol_stall_H5','gapsB','obv_div','ad_div','cmf_H','cmf_P','atrp_pct_P','bbw_pct_P','rsi_H','dist_ma50','dist_ma200','slopeB_A','max_upstreak_B','A_gain','B_gain','B_days','P_days','P_break_flag','H_ath']
T0=None
rows=[]
for f in F:
    a=d[d.y==1][f].dropna();b=d[d.y==0][f].dropna()
    if len(a)<3 or len(b)<3: continue
    U,p=mannwhitneyu(a,b); rbc=2*U/(len(a)*len(b))-1
    rows.append(dict(ind=f,crash_med=a.median(),ctrl_med=b.median(),crash_mean=a.mean(),ctrl_mean=b.mean(),p=p,rank_biserial=rbc,n1=len(a),n0=len(b)))
T=pd.DataFrame(rows).sort_values('p'); T['p_bonf']=np.minimum(T.p*len(T),1); T.to_csv('indicator_compare.csv',index=False)
print(d.groupby(['type','group']).size()); print('base',d.y.mean(), 'strict crash',(d.group=='crash').mean())
print(T.round(3).to_string())
tr=d[d.year<=2015];te=d[d.year>2015]
for name,m in [('logit',make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(C=.3,max_iter=1000))),('tree',make_pipeline(SimpleImputer(strategy='median'),DecisionTreeClassifier(max_depth=3,min_samples_leaf=15)))]:
    m.fit(tr[F],tr.y); pr=m.predict_proba(te[F])[:,1]; print(name,'train',len(tr),'test',len(te),'AUC_test',round(roc_auc_score(te.y,pr),3),'AUC_train',round(roc_auc_score(tr.y,m.predict_proba(tr[F])[:,1]),3))
    if name=='logit': print(dict(zip(F,np.round(m[-1].coef_[0],2))))
    else:
        from sklearn.tree import export_text; print(export_text(m[-1],feature_names=F))
