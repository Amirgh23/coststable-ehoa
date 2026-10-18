from pathlib import Path
import itertools, json
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, rankdata, wilcoxon

root=Path(__file__).resolve().parent
out=root/'scientific_audit_2026_10_18'
means=pd.read_csv(out/'independent_primary_dataset_means.csv')
methods=['EHOA','random','cheapest','mi','stable_lcb']
metrics=['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','jaccard_stability','fit_total_seconds']

def holm(values):
    values=np.asarray(values);order=np.argsort(values)
    adjusted=np.minimum(1,np.maximum.accumulate(values[order]*np.arange(len(values),0,-1)))
    answer=np.empty(len(values));answer[order]=adjusted
    return answer

rng=np.random.default_rng(20261018)
paired=[];friedman=[]
for omitted in sorted(means.dataset.unique()):
    subset=means[means.dataset!=omitted]
    for metric in metrics:
        pivot=subset.pivot(index='dataset',columns='method',values=metric)[methods]
        result=friedmanchisquare(*pivot.to_numpy().T)
        friedman.append(dict(omitted_dataset=omitted,n_datasets=len(pivot),metric=metric,statistic=result.statistic,p_raw=result.pvalue))
        for reference in methods[:-1]:
            delta=(pivot.stable_lcb-pivot[reference]).to_numpy()
            result=wilcoxon(delta,alternative='two-sided',method='auto')
            bootstrap=delta[rng.integers(0,len(delta),(20000,len(delta)))].mean(1)
            paired.append(dict(omitted_dataset=omitted,n_datasets=len(delta),metric=metric,reference=reference,mean_delta=delta.mean(),W=result.statistic,p_raw=result.pvalue,ci95_low=np.quantile(bootstrap,.025),ci95_high=np.quantile(bootstrap,.975),interpretation='post-hoc leave-one-dataset-out robustness; unadjusted descriptive bootstrap intervals'))
paired=pd.DataFrame(paired);friedman=pd.DataFrame(friedman)
paired['p_holm_all_24']=paired.groupby('omitted_dataset').p_raw.transform(holm)
paired['p_holm_within_metric']=paired.groupby(['omitted_dataset','metric']).p_raw.transform(holm)
friedman['p_holm_six_metrics']=friedman.groupby('omitted_dataset').p_raw.transform(holm)
paired.to_csv(out/'leave_one_dataset_out_paired.csv',index=False)
friedman.to_csv(out/'leave_one_dataset_out_friedman.csv',index=False)
paired[paired.omitted_dataset=='parkinsons'].to_csv(out/'exclude_oxford_paired.csv',index=False)
friedman[friedman.omitted_dataset=='parkinsons'].to_csv(out/'exclude_oxford_friedman.csv',index=False)

old=pd.read_csv(root/'fold_safe_revision_2026_10_12/runs.csv')
keys=['dataset','method','budget_ratio','evidence_resamples','lambda_penalty','cohort']
oldmeans=[]
for key,group in old.groupby(keys):
    matrix=np.vstack([np.load(root/'fold_safe_revision_2026_10_12/jobs'/job/'mask.npy') for job in group.job])
    probability=matrix.mean();phi=1-matrix.var(axis=0,ddof=1).mean()/(probability*(1-probability))
    jac=np.mean([np.logical_and(a,b).sum()/np.logical_or(a,b).sum() if np.logical_or(a,b).any() else 1 for a,b in itertools.combinations(matrix,2)])
    oldmeans.append(dict(zip(keys,key),masks=len(group),seeds=group.seed.nunique(),nogueira_stability=phi,jaccard_stability=jac,**{metric:group[metric].mean() for metric in ['balanced_accuracy','cost_ratio','selected_features','fit_total_seconds']}))
oldmeans=pd.DataFrame(oldmeans)
oldmeans.to_csv(out/'independent_original_and_ofat_means.csv',index=False)
published=pd.read_csv(root/'fold_safe_revision_2026_10_12/analysis/all_dataset_means.csv')
merged=published.merge(oldmeans,on=keys,suffixes=('_published','_recomputed'),validate='one_to_one')
comparison=[dict(table='original_and_ofat_means',metric=metric,maximum_absolute_error=float(abs(merged[metric+'_published']-merged[metric+'_recomputed']).max())) for metric in metrics]

source=[]
from run_fold_safe_revision import load
for dataset in sorted(means.dataset.unique()):
    x,y,groups=load(dataset)
    frame=pd.DataFrame(x)
    source.append(dict(dataset=dataset,rows=len(x),features=x.shape[1],classes=len(np.unique(y)),exact_duplicate_feature_rows_including_all_members=int(frame.duplicated(keep=False).sum()),redundant_feature_rows=len(frame)-len(frame.drop_duplicates()),missing_feature_values=int(frame.isna().sum().sum()),subject_prefixes=0 if groups is None else len(np.unique(groups))))
pd.DataFrame(source).to_csv(out/'independent_dataset_structure.csv',index=False)
pd.DataFrame(comparison).to_csv(out/'original_and_ofat_comparisons.csv',index=False)
summary=dict(leave_one_out_families=10,comparisons_per_family=24,minimum_p_holm_all_24=float(paired.p_holm_all_24.min()),significant_all24_rows=int((paired.p_holm_all_24<.05).sum()),analysis_role='Post-hoc sensitivity only; original ten-dataset analysis retained unchanged')
(out/'robustness_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
