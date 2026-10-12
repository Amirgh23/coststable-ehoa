from pathlib import Path
import json,itertools
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare,wilcoxon,rankdata
from proposed.stability import compute_nogueira_stability,compute_jaccard_stability

R=Path(__file__).resolve().parent;P=R/'revision_2026_10_12';A=P/'analysis'
M=['EHOA','Budget-random','Budget-cheapest','Budget-mi','Budget-stable_lcb']
metrics=['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','jaccard_stability']
new=pd.read_csv(P/'corrected_experiments/runs.csv')
old=pd.read_csv(R/'results/cost_stable_confirmatory/raw/runs.csv')
checks=[]
for (ds,m),g in new.groupby(['dataset','method']):
    masks=np.vstack([np.load(R/p) for p in g.mask_path])
    costs=np.random.default_rng(1000+int(g.D.iloc[0])).lognormal(0,.7,int(g.D.iloc[0]))
    checks.append(dict(dataset=ds,method=m,rows=len(g),counts_match=bool(np.array_equal(masks.sum(1),g.selected_features.values)),max_cost_error=float(abs(masks@costs-g.selected_cost.values).max()),phi_error=float(abs(compute_nogueira_stability(masks)-g.nogueira_stability.iloc[0])),budget_violations=int((g.cost_ratio>.3+1e-12).sum())))
pd.DataFrame(checks).to_csv(A/'corrected_mask_audit.csv',index=False)
new.groupby(['dataset','method'])[metrics].mean().reset_index().to_csv(A/'corrected_dataset_means.csv',index=False)
combined=pd.concat([old[~old.dataset.isin(['steel_plates_fault','parkinsons'])],new],ignore_index=True)
combined['evidence_origin']=['archived eligible' if ds not in ['steel_plates_fault','parkinsons'] else 'new exploratory correction' for ds in combined.dataset]
combined.to_csv(A/'corrected10_runs.csv',index=False)
means=combined.groupby(['dataset','method'])[metrics].mean().reset_index()
means.to_csv(A/'corrected10_dataset_means.csv',index=False)
means.groupby('method')[metrics].mean().reindex(M).to_csv(A/'corrected10_overall.csv')
def holm(ps):
    order=np.argsort(ps);a=np.empty(len(ps));v=0
    for k,i in enumerate(order):v=max(v,(len(ps)-k)*ps[i]);a[i]=min(1,v)
    return a
frows,rrows,pairs=[],[],[]
rng=np.random.default_rng(20261012)
for metric in metrics:
    p=means.pivot(index='dataset',columns='method',values=metric)[M]
    fr=friedmanchisquare(*p.values.T)
    frows.append(dict(metric=metric,n_datasets=10,df=4,statistic=fr.statistic,p_raw=fr.pvalue,status='Exploratory corrected-ten sensitivity; combines eight archived and two new datasets'))
    ranks=np.array([rankdata(r if metric in ['cost_ratio','selected_features'] else -r) for r in p.values])
    for j,m in enumerate(M):rrows.append(dict(metric=metric,method=m,average_rank=ranks[:,j].mean()))
    for m in M[:-1]:
        delta=(p['Budget-stable_lcb']-p[m]).to_numpy();w=wilcoxon(delta,alternative='two-sided',method='auto');nz=delta[delta!=0];rr=rankdata(abs(nz))
        boots=delta[rng.integers(0,10,(20000,10))].mean(1)
        pairs.append(dict(metric=metric,reference=m,mean_delta=delta.mean(),wilcoxon_W=w.statistic,p_raw=w.pvalue,rank_biserial=float((rr[nz>0].sum()-rr[nz<0].sum())/rr.sum()) if len(rr) else 0,ci95_low=np.quantile(boots,.025),ci95_high=np.quantile(boots,.975)))
ff=pd.DataFrame(frows);ff['p_holm_five_metrics']=holm(ff.p_raw.values);ff.to_csv(A/'corrected10_friedman.csv',index=False)
pd.DataFrame(rrows).to_csv(A/'corrected10_ranks.csv',index=False)
pp=pd.DataFrame(pairs);pp['p_holm_within_metric']=pp.groupby('metric').p_raw.transform(lambda x:holm(x.to_numpy()));pp['p_holm_all_20']=holm(pp.p_raw.values);pp.to_csv(A/'corrected10_paired.csv',index=False)
split=pd.read_csv(P/'corrected_experiments/subject_split_audit.csv')
audit=dict(new_runs=len(new),new_masks=len(list((P/'corrected_experiments/masks').glob('*.npy'))),old_eligible_runs=240,corrected10_runs=len(combined),duplicates=int(combined.duplicated(['dataset','method','seed','fold']).sum()),constrained_budget_violations=int(((new.method!='EHOA')&(new.cost_ratio>.3+1e-12)).sum()),outer_subject_overlap=int(split.outer_subject_overlap.max()),inner_subject_overlap=int(split.inner_subject_overlap.max()),unique_subject_prefixes=32,steel_predictors=27,steel_classes=7,new_experiment_status='exploratory; not preregistered',combined_status='secondary sensitivity; heterogeneous recording/group protocols explicitly reported')
(A/'corrected_experiment_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
spec=[]
for ds in ['steel_plates_fault','parkinsons']:
    frame=pd.read_csv(P/'corrected_experiments/steel_27_features_7_classes.csv') if ds=='steel_plates_fault' else pd.read_csv(R/'data/benchmark_v2/parkinsons.csv')
    spec.append(dict(dataset=ds,N=len(frame),D=len(frame.columns)-1,classes=frame.target.nunique(),class_counts=json.dumps(frame.target.value_counts().sort_index().to_dict()),split_unit='row' if ds=='steel_plates_fault' else 'subject-prefix',subject_groups='' if ds=='steel_plates_fault' else 32))
pd.DataFrame(spec).to_csv(A/'corrected_datasets.csv',index=False)
print(json.dumps(audit));print(ff.to_string(index=False));print(pp[pp.reference=='EHOA'].to_string(index=False))
