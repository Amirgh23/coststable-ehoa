from pathlib import Path
import hashlib, itertools, json
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, rankdata, wilcoxon
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, roc_auc_score
from run_fold_safe_revision import load

root=Path(__file__).resolve().parent
out=root/'scientific_audit_2026_10_18'
out.mkdir(exist_ok=True)
old=pd.read_csv(root/'fold_safe_revision_2026_10_12/runs.csv')
new=pd.read_csv(root/'extended_revision_2026_10_12/runs.csv')
old['source_directory']='fold_safe_revision_2026_10_12/jobs/'+old.job
new['source_directory']='extended_revision_2026_10_12/'+new.campaign+'/jobs/'+new.job
raw=pd.concat([old,new],ignore_index=True)
datasets={name:load(name) for name in raw.dataset.unique()}
records=[]
masks={}
for row in raw.to_dict('records'):
    directory=root/row['source_directory']
    mask=np.load(directory/'mask.npy')
    masks[row['source_directory']]=mask
    prediction=pd.read_csv(directory/'predictions.csv')
    split=np.load(directory/'split_provenance.npz')
    x,y,groups=datasets[row['dataset']]
    index=prediction.row.to_numpy(dtype=int)
    costs=np.random.default_rng(1000+row['D']).lognormal(0,.7,row['D'])
    inner_row_overlap=0
    inner_group_overlap=0
    for fold in [1,2,3]:
        train=split[f'inner_{fold}_train'];valid=split[f'inner_{fold}_validation']
        inner_row_overlap=max(inner_row_overlap,len(np.intersect1d(train,valid)),len(np.intersect1d(train,split['outer_test'])),len(np.intersect1d(valid,split['outer_test'])))
        if groups is not None:
            inner_group_overlap=max(inner_group_overlap,len(set(groups[train])&set(groups[valid])),len(set(groups[train])&set(groups[split['outer_test']])),len(set(groups[valid])&set(groups[split['outer_test']])))
    records.append(dict(source_directory=row['source_directory'],dataset=row['dataset'],method=row['method'],seed=row['seed'],fold=row['fold'],true_label_mismatches=int(np.sum(prediction.true.to_numpy()!=y[index])),test_index_mismatches=int(not np.array_equal(index,split['outer_test'])),outer_row_overlap=len(np.intersect1d(split['outer_train'],split['outer_test'])),inner_row_overlap=inner_row_overlap,outer_group_overlap=0 if groups is None else len(set(groups[split['outer_train']])&set(groups[split['outer_test']])),inner_group_overlap=inner_group_overlap,mask_binary=bool(np.isin(mask,[0,1]).all()),mask_count_error=abs(int(mask.sum())-row['selected_features']),mask_cost_error=abs(costs[mask.astype(bool)].sum()-row['selected_cost']),ba_error=abs(balanced_accuracy_score(prediction.true,prediction.predicted)-row['balanced_accuracy']),accuracy_error=abs(accuracy_score(prediction.true,prediction.predicted)-row['accuracy'])))
pd.DataFrame(records).to_csv(out/'all_1464_prediction_and_group_checks.csv',index=False)

def stability(matrix):
    matrix=np.asarray(matrix,dtype=float)
    n,d=matrix.shape
    if n<2:
        return np.nan
    p=matrix.mean()
    phi=1.0 if p in [0,1] else 1-matrix.var(axis=0,ddof=1).mean()/(p*(1-p))
    jaccard=np.mean([np.logical_and(a,b).sum()/np.logical_or(a,b).sum() if np.logical_or(a,b).any() else 1 for a,b in itertools.combinations(matrix.astype(bool),2)])
    return phi,jaccard

primary=pd.concat([old[old.cohort=='primary'],new[new.campaign=='extra_seeds']],ignore_index=True)
metrics=['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','jaccard_stability','fit_total_seconds']
stability_rows=[]
for (dataset,method),group in primary.groupby(['dataset','method']):
    phi,jac=stability([masks[path] for path in group.source_directory])
    primary.loc[group.index,'nogueira_stability']=phi
    primary.loc[group.index,'jaccard_stability']=jac
    stability_rows.append(dict(dataset=dataset,method=method,masks=len(group),seeds=group.seed.nunique(),nogueira_stability=phi,jaccard_stability=jac))
pd.DataFrame(stability_rows).to_csv(out/'independent_primary_mask_stability.csv',index=False)
means=primary.groupby(['dataset','method'])[metrics].mean().reset_index()
means.to_csv(out/'independent_primary_dataset_means.csv',index=False)
methods=['EHOA','random','cheapest','mi','stable_lcb']

def holm(values):
    values=np.asarray(values)
    order=np.argsort(values)
    sorted_adjusted=np.minimum(1,np.maximum.accumulate(values[order]*np.arange(len(values),0,-1)))
    result=np.empty(len(values));result[order]=sorted_adjusted
    return result

rng=np.random.default_rng(20261012)
friedman=[];ranks=[];paired=[]
for metric in metrics:
    pivot=means.pivot(index='dataset',columns='method',values=metric)[methods]
    result=friedmanchisquare(*pivot.to_numpy().T)
    friedman.append(dict(metric=metric,statistic=result.statistic,p_raw=result.pvalue))
    rank=np.array([rankdata(row if metric in ['cost_ratio','selected_features','fit_total_seconds'] else -row) for row in pivot.to_numpy()])
    for column,method in enumerate(methods):
        ranks.append(dict(metric=metric,method=method,average_rank=rank[:,column].mean()))
    for reference in methods[:-1]:
        delta=(pivot.stable_lcb-pivot[reference]).to_numpy()
        result=wilcoxon(delta,alternative='two-sided',method='auto')
        nonzero=delta[delta!=0];absolute_ranks=rankdata(abs(nonzero))
        positive_rank=absolute_ranks[nonzero>0].sum()
        all_rank_sums=np.array([np.dot(signs,absolute_ranks) for signs in itertools.product([0,1],repeat=len(nonzero))])
        tail=min(positive_rank,absolute_ranks.sum()-positive_rank)
        exact=min(1.,2*np.mean(all_rank_sums<=tail+1e-12))
        bootstrap=delta[rng.integers(0,len(delta),(20000,len(delta)))].mean(1)
        paired.append(dict(metric=metric,reference=reference,mean_delta=delta.mean(),W=result.statistic,p_raw=result.pvalue,p_exact_conditional_ties=exact,rank_biserial=(2*positive_rank-absolute_ranks.sum())/absolute_ranks.sum(),ci95_low=np.quantile(bootstrap,.025),ci95_high=np.quantile(bootstrap,.975),nonzero_datasets=len(nonzero)))
friedman=pd.DataFrame(friedman);friedman['p_holm_six_metrics']=holm(friedman.p_raw)
paired=pd.DataFrame(paired)
paired['p_holm_within_metric']=paired.groupby('metric').p_raw.transform(lambda values:holm(values))
paired['p_holm_all_24']=holm(paired.p_raw)
paired['p_exact_holm_all_24']=holm(paired.p_exact_conditional_ties)
friedman.to_csv(out/'independent_friedman.csv',index=False)
pd.DataFrame(ranks).to_csv(out/'independent_ranks.csv',index=False)
paired.to_csv(out/'independent_paired_and_exact_sensitivity.csv',index=False)
comparisons=[]
for name,recomputed,keys in [('primary_dataset_means',means,['dataset','method']),('primary_friedman',friedman,['metric']),('primary_ranks',pd.DataFrame(ranks),['metric','method']),('primary_paired',paired,['metric','reference'])]:
    published=pd.read_csv(root/f'extended_revision_2026_10_12/analysis/{name}.csv')
    merged=published.merge(recomputed,on=keys,suffixes=('_published','_recomputed'),validate='one_to_one')
    for column in recomputed.select_dtypes('number').columns:
        if column in published:
            comparisons.append(dict(table=name,column=column,rows=len(merged),maximum_absolute_error=float(abs(merged[column+'_published']-merged[column+'_recomputed']).max())))
pd.DataFrame(comparisons).to_csv(out/'published_primary_comparisons.csv',index=False)

cells=[]
for key,group in new[new.campaign=='factorial'].groupby(['dataset','budget_ratio','evidence_resamples','lambda_penalty']):
    phi,_=stability([masks[path] for path in group.source_directory])
    cells.append(dict(zip(['dataset','budget_ratio','evidence_resamples','lambda_penalty'],key),balanced_accuracy=group.balanced_accuracy.mean(),cost_ratio=group.cost_ratio.mean(),selected_features=group.selected_features.mean(),nogueira_stability=phi))
cells=pd.DataFrame(cells);effect=[]
for dataset,group in cells.groupby('dataset'):
    design=np.column_stack([np.where(group[column]==group[column].max(),1.,-1.) for column in ['budget_ratio','evidence_resamples','lambda_penalty']])
    for size in [1,2,3]:
        for selection in itertools.combinations(range(3),size):
            weights=design[:,selection].prod(1)
            for metric in ['balanced_accuracy','cost_ratio','selected_features','nogueira_stability']:
                effect.append(dict(dataset=dataset,term=' x '.join(['budget_ratio','evidence_resamples','lambda_penalty'][i] for i in selection),metric=metric,effect=group.loc[weights==1,metric].mean()-group.loc[weights==-1,metric].mean()))
effect=pd.DataFrame(effect)
effect.to_csv(out/'independent_factorial_effects.csv',index=False)
original=pd.read_csv(root/'extended_revision_2026_10_12/analysis/factorial_dataset_effects.csv')
joined=original.merge(effect,on=['dataset','term','metric'],suffixes=('_published','_recomputed'),validate='one_to_one')

external=root/'external_evidence_2026_10_13'
target=pd.read_csv(external/'ReplicatedAcousticFeatures-ParkinsonDatabase.csv')
transfer=[]
for method in methods:
    predictions=[]
    for seed in range(72001,72006):
        prediction=pd.read_csv(external/'jobs'/f'{method}_{seed}'/'external_predictions.csv')
        transfer.append(dict(method=method,seed=seed,subject_mismatches=int((prediction.subject!=target.ID).sum()),label_mismatches=int((prediction.true!=target.Status).sum()),recording_ba=balanced_accuracy_score(prediction.true,prediction.predicted)))
        predictions.append(prediction.probability_pd.to_numpy())
    subjects=pd.DataFrame(dict(subject=target.ID,true=target.Status,probability=np.mean(predictions,axis=0))).groupby('subject').agg(true=('true','first'),probability=('probability','mean'))
    predicted=(subjects.probability>=.5).astype(int)
    matrix=confusion_matrix(subjects.true,predicted,labels=[0,1])
    transfer.append(dict(method=method,seed='ensemble',subjects=len(subjects),subject_ba=balanced_accuracy_score(subjects.true,predicted),auc=roc_auc_score(subjects.true,subjects.probability),tn=matrix[0,0],fp=matrix[0,1],fn=matrix[1,0],tp=matrix[1,1]))
pd.DataFrame(transfer).to_csv(out/'independent_external_predictions.csv',index=False)
summary=dict(runs=len(raw),primary_runs=len(primary),datasets=len(datasets),factorial_runs=int((new.campaign=='factorial').sum()),factorial_max_effect_error=float(abs(joined.effect_published-joined.effect_recomputed).max()),primary_max_comparison_error=float(pd.DataFrame(comparisons).maximum_absolute_error.max()),metric_recomputation_scope='Saved hard-label predictions; score-based AUC/PR-AUC of the 1464 primary-study runs cannot be independently recalculated because saved files contain no probabilities',group_identity_scope='Checks pseudonymous mapping, not clinical identity',files_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['analyze_extended_revision.py','analyze_fold_safe_revision.py','proposed/stability.py']})
(out/'statistical_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
