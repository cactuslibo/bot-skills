import pandas as pd,numpy as np
R=pd.read_csv('stage12.csv'); S=pd.read_csv('stage3_text.csv'); R=R.merge(S,on='ticker',how='left')
s2=R.s2=='通过'
R['sig_cl']=np.where(R.cl_rev.isna(),'缺数据',np.where(R.cl_rev>=0.10,'是','否'))
R['sig_bb']=np.where(R.book_to_bill.isna(),'缺数据',np.where((R.book_to_bill>=1.05)&(R.rpo_yoy>0),'是','否'))
R['sig_cap']=np.where(R.cap_terms.fillna('')!='','是','否')
R['sig_ss']='缺数据'  # 全文检索只能判断同一份10-K共现，无法确认是客户把该公司列为单一来源，噪声过大，不计分
for c in ['sig_cl','sig_bb','sig_cap','sig_ss']: R.loc[~s2,c]=''
R['n_sig']=(R[['sig_cl','sig_bb','sig_cap','sig_ss']]=='是').sum(axis=1)
R['n_missing']=(R[['sig_cl','sig_bb']]=='缺数据').sum(axis=1)
R['s3']=np.where(~s2,'—',np.where(R.n_sig>=2,'通过',np.where(R.n_missing>0,'数据不足','未通过')))
R['final']=np.where(R.s3=='通过','三段全过',np.where(R.s3=='数据不足','观察名单(第三段数据不足)',np.where(R.s3=='未通过','前两段过/第三段未过','')))
R['score']=R.gm_trough_pct.fillna(0)+R.n_sig*0.25+(R.up_dom_mean-R.up_dgm_mean).clip(upper=0.1).fillna(0)*2
R=R.sort_values(['final','n_sig','gm_trough_pct'],ascending=[True,False,False])
R.to_csv('results.csv',index=False,encoding='utf-8-sig')
print(R.s3.value_counts())
