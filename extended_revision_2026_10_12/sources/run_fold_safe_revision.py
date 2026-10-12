import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
import json,hashlib,time,platform,traceback,sys,shutil
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold,StratifiedGroupKFold
from sklearn.neighbors import KNeighborsClassifier
from utils import clean_dataset,preprocess_train_test,calculate_metrics
from proposed.fold_safe_ehoa import FoldSafeEHOA

R=Path(__file__).resolve().parent
P=R/'fold_safe_revision_2026_10_12'
M=['EHOA','random','cheapest','mi','stable_lcb']
D=['breast_cancer','wine','ionosphere','sonar','dermatology','spambase','parkinsons','hill_valley','steel_plates_fault','madelon']
S=[72001,72002,72003]

def load(ds):
    path=R/'revision_2026_10_12/corrected_experiments/steel_27_features_7_classes.csv' if ds=='steel_plates_fault' else R/'data'/('' if ds in ['breast_cancer','wine'] else 'benchmark_v2')/(ds+'.csv')
    frame=pd.read_csv(path)
    X,y=clean_dataset(frame.drop(columns='target').to_numpy(),frame.target.to_numpy())
    groups=pd.read_csv(R/'revision_2026_10_12/corrected_experiments/parkinson_subject_mapping.csv').subject.to_numpy() if ds=='parkinsons' else None
    return X,y,groups

def execute(job):
    ds,method,seed,k,b,Rn,lam,cohort=job
    name=f'{ds}_{method}_{seed}_{k}_b{b}_r{Rn}_l{lam}'
    dest=P/'jobs'/name
    dest.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    X,y,groups=load(ds)
    cv=StratifiedKFold(3,shuffle=True,random_state=seed) if groups is None else StratifiedGroupKFold(3,shuffle=True,random_state=seed)
    splits=list(cv.split(X,y) if groups is None else cv.split(X,y,groups))
    tr,te=splits[k-1]
    outer_overlap=0 if groups is None else len(set(groups[tr])&set(groups[te]))
    if outer_overlap:raise ValueError('Outer subject overlap')
    costs=np.random.default_rng(1000+X.shape[1]).lognormal(0,.7,X.shape[1])
    discrete=np.r_[np.ones(33,bool),False] if ds=='dermatology' else False
    model=FoldSafeEHOA(n_hikers=8,max_iter=10,n_folds=3,alpha=.99,random_state=seed+k*100003,verbose=False,costs=costs,budget=b*costs.sum(),strategy=method,evidence_resamples=Rn,lcb_z=lam,groups=None if groups is None else groups[tr],discrete_features=discrete)
    mask,_,selected=model.fit(X[tr],y[tr])
    xp,yp,xt,_,_=preprocess_train_test(X[tr][:,selected],y[tr],X[te][:,selected],apply_smote=True,random_state=seed)
    clf=KNeighborsClassifier(n_neighbors=5,metric='euclidean')
    clf.fit(xp,yp)
    pred=clf.predict(xt)
    probability=clf.predict_proba(xt)
    metrics=calculate_metrics(y[te],pred,probability)
    np.save(dest/'mask.npy',mask)
    np.savez_compressed(dest/'split_provenance.npz',outer_train=tr,outer_test=te,outer_utility=model.utility_,**{f'inner_{j+1}_{kind}':arr for j,(itr,iva) in enumerate(model.inner_indices) for kind,arr in [('train',tr[itr]),('validation',tr[iva]),('utility',model.inner_utilities[j])]} )
    pd.DataFrame(model.split_audit).to_csv(dest/'inner_split_audit.csv',index=False)
    pd.DataFrame(model.candidate_audit).to_csv(dest/'candidate_audit.csv',index=False)
    pd.DataFrame(dict(row=te,true=y[te],predicted=pred)).to_csv(dest/'predictions.csv',index=False)
    row=dict(job=name,dataset=ds,method=method,seed=seed,fold=k,budget_ratio=b,evidence_resamples=Rn,lambda_penalty=lam,cohort=cohort,N=len(X),D=X.shape[1],classes=len(np.unique(y)),selected_features=len(selected),selected_cost=float(costs[selected].sum()),total_cost=float(costs.sum()),cost_ratio=float(costs[selected].sum()/costs.sum()),fitness=model.best_fitness,evaluations=model.evaluations_,fit_total_seconds=model.fit_total_seconds_,end_to_end_seconds=time.perf_counter()-started,outer_subject_overlap=outer_overlap,inner_subject_overlap=max(a['subject_overlap'] for a in model.split_audit),utility_validation_overlap=max(a['utility_validation_row_overlap'] for a in model.split_audit),smote_dimensions_match=all(a['selected_features']==a['smote_input_features'] for a in model.candidate_audit),outer_smote_input_features=xp.shape[1],status='complete',**metrics)
    (dest/'result.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
    return row

if __name__=='__main__':
    P.mkdir(exist_ok=True)
    (P/'jobs').mkdir(exist_ok=True)
    jobs=[(ds,m,s,k,.3,4,1.,'primary') for ds in D for m in M for s in S for k in [1,2,3]]
    for ds in ['breast_cancer','dermatology','parkinsons']:
        for s in S:
            for k in [1,2,3]:
                for b in [.15,.5]:
                    for m in M[1:]:jobs.append((ds,m,s,k,b,4,1.,'budget_sensitivity'))
                for Rn,lam in [(8,1.),(16,1.),(4,0.),(4,2.)]:jobs.append((ds,'stable_lcb',s,k,.3,Rn,lam,'utility_sensitivity'))
    config=dict(created_utc=datetime.now(timezone.utc).isoformat(),registration='Locally frozen before this execution; not independent public preregistration; prior data results already known',primary_datasets=D,methods=M,seeds=S,outer_folds=3,inner_folds=3,n_hikers=8,max_iter=10,alpha=.99,primary_budget=.3,primary_R=4,primary_lambda=1,planned_jobs=len(jobs),primary_jobs=450,sensitivity_datasets=['breast_cancer','dermatology','parkinsons'],changes=['inner utility fitted only on inner training rows','each candidate repaired separately in each inner fold; objective averages fold accuracies and subset sizes','final deployment mask repaired using outer-training-only utility','imputation/scaling/SMOTE fit on selected dimensions per candidate and final mask','Dermatology first 33 inputs discrete for MI, age continuous','complete timing includes utility and final classification'],scope='All fresh runs; never combine with archived metrics as one identical protocol',remaining=['synthetic costs','unverified clinical identity of Parkinson subject prefixes','no external clinical validation','only three search seeds and short search','MI remains marginal; resampling score has no confidence coverage'])
    protocol=P/'protocol.json'
    if not protocol.exists():
        protocol.write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
        hashes={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['ehoa.py','utils.py','proposed/fold_safe_ehoa.py','run_fold_safe_revision.py']}
        hashes['protocol.json']=hashlib.sha256(protocol.read_bytes()).hexdigest()
        (P/'frozen_sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
        (P/'environment.json').write_text(json.dumps(dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),logical_cpus=os.cpu_count(),numpy=np.__version__,pandas=pd.__version__,sklearn=__import__('sklearn').__version__,imblearn=__import__('imblearn').__version__,scipy=__import__('scipy').__version__),indent=2),encoding='utf-8')
    expected=json.loads((P/'frozen_sha256.json').read_text())
    for f,digest in expected.items():
        actual=(P/f if f=='protocol.json' else R/f).read_bytes()
        if hashlib.sha256(actual).hexdigest()!=digest:raise ValueError('Frozen protocol/code changed: '+f)
    rows=[json.loads(f.read_text()) for f in (P/'jobs').glob('*/result.json')]
    done={row['job'] for row in rows}
    pending=[job for job in jobs if f'{job[0]}_{job[1]}_{job[2]}_{job[3]}_b{job[4]}_r{job[5]}_l{job[6]}' not in done]
    print(f'Protocol frozen: {len(jobs)} jobs; existing {len(rows)}; pending {len(pending)}',flush=True)
    with ProcessPoolExecutor(max_workers=3) as pool:
        submitted={pool.submit(execute,job):job for job in pending}
        for future in as_completed(submitted):
            try:
                row=future.result()
                rows.append(row)
                pd.DataFrame(rows).to_csv(P/'runs.csv',index=False)
                print(f'{len(rows)}/{len(jobs)} {row["job"]} BA={row["balanced_accuracy"]:.4f} seconds={row["end_to_end_seconds"]:.1f}',flush=True)
            except Exception:
                with (P/'failure_log.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(job=submitted[future],time_utc=datetime.now(timezone.utc).isoformat(),traceback=traceback.format_exc()))+'\n')
                print('FAILED '+str(submitted[future]),flush=True)
    print('Completed',len(rows),'of',len(jobs),flush=True)
