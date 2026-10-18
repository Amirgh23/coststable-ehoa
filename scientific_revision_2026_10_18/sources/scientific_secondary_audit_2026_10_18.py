from pathlib import Path
import json
import numpy as np
import pandas as pd
from run_fold_safe_revision import load

root=Path(__file__).resolve().parent
out=root/'scientific_audit_2026_10_18'
old=pd.read_csv(root/'fold_safe_revision_2026_10_12/runs.csv')
new=pd.read_csv(root/'extended_revision_2026_10_12/runs.csv')
old['source_directory']='fold_safe_revision_2026_10_12/jobs/'+old.job
new['source_directory']='extended_revision_2026_10_12/'+new.campaign+'/jobs/'+new.job
new['cohort']=new.campaign
raw=pd.concat([old,new],ignore_index=True)
rng=np.random.default_rng(20261012)
for _ in range(24):
    rng.integers(0,10,(20000,10))
effects=pd.read_csv(out/'independent_factorial_effects.csv')
factorial=[]
for (term,metric),group in effects.groupby(['term','metric']):
    values=group.effect.to_numpy()
    boot=values[rng.integers(0,10,(20000,10))].mean(1)
    factorial.append(dict(term=term,metric=metric,mean_effect=values.mean(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975)))
factorial=pd.DataFrame(factorial)
factorial.to_csv(out/'independent_factorial_intervals.csv',index=False)

search=[]
for population,data in [(8,old[(old.cohort=='primary')&(old.seed==72001)]),(16,new[new.campaign=='larger_search'])]:
    for (dataset,method),group in data.groupby(['dataset','method']):
        masks=np.vstack([np.load(root/path/'mask.npy') for path in group.source_directory])
        probability=masks.mean()
        phi=1-masks.var(axis=0,ddof=1).mean()/(probability*(1-probability))
        search.append(dict(dataset=dataset,method=method,population=population,nogueira_stability=phi,**{metric:group[metric].mean() for metric in ['balanced_accuracy','cost_ratio','selected_features','fitness','evaluations','fit_total_seconds']}))
search=pd.DataFrame(search)
search_effects=[]
for method,group in search.groupby('method'):
    low=group[group.population==8].set_index('dataset')
    high=group[group.population==16].set_index('dataset')
    for metric in ['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','fitness','evaluations','fit_total_seconds']:
        delta=(high[metric]-low[metric]).to_numpy()
        boot=delta[rng.integers(0,10,(20000,10))].mean(1)
        search_effects.append(dict(method=method,metric=metric,mean_delta=delta.mean(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975)))
search_effects=pd.DataFrame(search_effects)
search_effects.to_csv(out/'independent_search_effects_and_intervals.csv',index=False)
comparisons=[]
for filename,recomputed,keys in [('factorial_effects',factorial,['term','metric']),('search_profile_effects',search_effects,['method','metric'])]:
    published=pd.read_csv(root/f'extended_revision_2026_10_12/analysis/{filename}.csv')
    merged=published.merge(recomputed,on=keys,suffixes=('_published','_recomputed'),validate='one_to_one')
    for metric in recomputed.select_dtypes('number').columns:
        comparisons.append(dict(table=filename,column=metric,maximum_absolute_error=float(abs(merged[metric+'_published']-merged[metric+'_recomputed']).max())))
pd.DataFrame(comparisons).to_csv(out/'secondary_interval_comparisons.csv',index=False)

x,y,_=load('spambase')
frame=pd.DataFrame(x)
duplicate=frame[frame.duplicated(keep=False)].copy()
duplicate['target']=y[duplicate.index]
duplicate.to_csv(out/'spambase_feature_collisions.csv',index_label='cleaned_row')
groups=duplicate.groupby(list(range(x.shape[1]))).groups
cross=[]
for row in raw[raw.dataset=='spambase'].to_dict('records'):
    split=np.load(root/row['source_directory']/'split_provenance.npz')
    count=sum(bool(set(indices)&set(split['outer_train'])) and bool(set(indices)&set(split['outer_test'])) for indices in groups.values())
    cross.append(dict(source_directory=row['source_directory'],cohort=row['cohort'],method=row['method'],seed=row['seed'],fold=row['fold'],feature_collision_groups_crossing_outer_split=count))
pd.DataFrame(cross).to_csv(out/'spambase_collision_split_audit.csv',index=False)
mapping=pd.read_csv(root/'revision_2026_10_12/corrected_experiments/parkinson_subject_mapping.csv')
_,park_y,park_groups=load('parkinsons')
summary=dict(secondary_maximum_error=float(pd.DataFrame(comparisons).maximum_absolute_error.max()),spambase_collision_rows=len(duplicate),spambase_collision_groups=len(groups),spambase_runs_audited=len(cross),spambase_runs_with_collision_across_outer_split=sum(row['feature_collision_groups_crossing_outer_split']>0 for row in cross),collision_interpretation='Identical feature vectors have discordant labels. This is not sufficient evidence of identical emails or a shared real-world source; do not claim established subject leakage.',parkinson_mapping_label_mismatches=int(np.sum(mapping.target.to_numpy()!=park_y)),parkinson_prefixes=len(np.unique(park_groups)),parkinson_prefix_label_max_nunique=int(mapping.groupby('subject').target.nunique().max()))
(out/'secondary_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
