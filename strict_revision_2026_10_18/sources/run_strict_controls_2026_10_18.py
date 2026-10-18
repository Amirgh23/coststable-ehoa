import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib,json,itertools,platform
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.neighbors import KNeighborsClassifier
from run_fold_safe_revision import load
from proposed.cost_stable_ehoa import repair_to_budget
from utils import preprocess_train_test,calculate_metrics

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'strict_review_2026_10_18'

def execute(row):
    X,y,groups=load(row['dataset'])
    source=ROOT/row['source_directory']
    split=np.load(source/'split_provenance.npz')
    tr,te=split['outer_train'],split['outer_test']
    utility=split['outer_utility']
    costs=np.random.default_rng(1000+X.shape[1]).lognormal(0,.7,X.shape[1])
    method=row['control']
    mask=np.ones(X.shape[1],bool) if method=='AllFeatures' else repair_to_budget(np.ones(X.shape[1],bool),costs,.3*costs.sum(),utility)
    selected=np.flatnonzero(mask)
    xp,yp,xt,_,_=preprocess_train_test(X[tr][:,selected],y[tr],X[te][:,selected],apply_smote=True,random_state=int(row['seed']))
    model=KNeighborsClassifier(n_neighbors=5,metric='euclidean').fit(xp,yp)
    predicted=model.predict(xt)
    probability=model.predict_proba(xt)
    dest=OUT/'jobs'/f"{row['dataset']}_{method}_{row['seed']}_{row['fold']}"
    dest.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dest/'evidence.npz',mask=mask,costs=costs,utility=utility,outer_train=tr,outer_test=te,true=y[te],predicted=predicted,probability=probability,classes=model.classes_)
    result=dict(dataset=row['dataset'],method=method,seed=int(row['seed']),fold=int(row['fold']),source_directory=row['source_directory'],selected_features=len(selected),cost_ratio=float(costs[mask].sum()/costs.sum()),outer_overlap=len(np.intersect1d(tr,te)),outer_group_overlap=0 if groups is None else len(set(groups[tr])&set(groups[te])),**calculate_metrics(y[te],predicted,probability))
    (dest/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

def holm(p):
    p=np.asarray(p);order=np.argsort(p);result=np.empty(len(p));result[order]=np.minimum(1,np.maximum.accumulate(p[order]*np.arange(len(p),0,-1)));return result

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    old=pd.read_csv(ROOT/'fold_safe_revision_2026_10_12/runs.csv')
    new=pd.read_csv(ROOT/'extended_revision_2026_10_12/runs.csv')
    old['source_directory']='fold_safe_revision_2026_10_12/jobs/'+old.job
    new['source_directory']='extended_revision_2026_10_12/'+new.campaign+'/jobs/'+new.job
    primary=pd.concat([old[old.cohort=='primary'],new[new.campaign=='extra_seeds']],ignore_index=True)
    jobs=[]
    for control,source in [('GreedyMI','mi'),('GreedyResampled','stable_lcb'),('AllFeatures','EHOA')]:
        jobs.extend(dict(row,control=control) for row in primary[primary.method==source].to_dict('records'))
    plan=dict(created_utc=datetime.now(timezone.utc).isoformat(),status='Post-hoc controls; original outcomes already known; not preregistered',jobs=len(jobs),design='Same ten datasets, five seeds, three saved outer folds; fixed KNN5 and selected-column preprocessing/SMOTE. No search or test-label tuning. Greedy starts with all features and applies the exact existing utility/cost deletion repair once. Saved outer-training utility is reused, not fitted on test labels.',costs='Same single synthetic cost draw per dimension as primary; no generalization over cost assignments',analysis='Ten dataset means; Resampled EHOA minus three controls for BA, cost ratio and descriptive Nogueira stability. Exact conditional signed-rank; one Holm family of nine tests. Bootstrap 20000 dataset resamples, descriptive unadjusted intervals. AllFeatures stability is degenerate (one by convention), not evidence of useful biomarkers.',timing='Utility is reused; no standalone runtime or speedup claim.',code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),environment=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__))
    protocol=OUT/'protocol.json'
    if not protocol.exists():protocol.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    if json.loads(protocol.read_text())['code_sha256']!=plan['code_sha256']:raise ValueError('Code differs from recorded plan')
    records=[]
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures=[pool.submit(execute,row) for row in jobs]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records)%50==0:print('Controls',len(records),'/',len(jobs),flush=True)
    runs=pd.DataFrame(records).sort_values(['dataset','method','seed','fold'])
    runs.to_csv(OUT/'runs.csv',index=False)
    means=[]
    for (ds,method),group in runs.groupby(['dataset','method']):
        masks=[np.load(OUT/'jobs'/f'{ds}_{method}_{r.seed}_{r.fold}'/'evidence.npz')['mask'] for r in group.itertuples()]
        a=np.asarray(masks,float);p=a.mean();phi=1. if p in [0,1] else 1-a.var(0,ddof=1).mean()/(p*(1-p))
        means.append(dict(dataset=ds,method=method,nogueira_stability=phi,**{key:float(group[key].mean()) for key in ['balanced_accuracy','cost_ratio','selected_features']}))
    means=pd.DataFrame(means)
    published=pd.read_csv(ROOT/'scientific_audit_2026_10_18/independent_primary_dataset_means.csv')
    allmeans=pd.concat([means,published],ignore_index=True)
    allmeans.to_csv(OUT/'dataset_means.csv',index=False)
    rng=np.random.default_rng(20261018);comparisons=[]
    for metric in ['balanced_accuracy','cost_ratio','nogueira_stability']:
        pivot=allmeans.pivot(index='dataset',columns='method',values=metric)
        for reference in ['GreedyMI','GreedyResampled','AllFeatures']:
            delta=(pivot.stable_lcb-pivot[reference]).to_numpy();nz=delta[delta!=0];ranks=rankdata(abs(nz));positive=ranks[nz>0].sum();tail=min(positive,ranks.sum()-positive)
            sums=np.array([np.dot(signs,ranks) for signs in itertools.product([0,1],repeat=len(nz))])
            exact=min(1.,2*np.mean(sums<=tail+1e-12))
            boots=delta[rng.integers(0,len(delta),(20000,len(delta)))].mean(1)
            comparisons.append(dict(metric=metric,reference=reference,mean_delta=float(delta.mean()),p_exact=float(exact),ci95_low=float(np.quantile(boots,.025)),ci95_high=float(np.quantile(boots,.975)),datasets=len(delta)))
    comparisons=pd.DataFrame(comparisons);comparisons['p_holm_9']=holm(comparisons.p_exact)
    comparisons.to_csv(OUT/'paired_controls.csv',index=False)
    summary=dict(completed=len(runs),expected=len(jobs),budget_violations=int(((runs.method!='AllFeatures')&(runs.cost_ratio>.3+1e-10)).sum()),row_overlap=int(runs.outer_overlap.max()),group_overlap=int(runs.outer_group_overlap.max()),macro_means=allmeans.groupby('method')[['balanced_accuracy','cost_ratio','nogueira_stability']].mean().to_dict('index'),comparisons=comparisons.to_dict('records'))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary),flush=True)
