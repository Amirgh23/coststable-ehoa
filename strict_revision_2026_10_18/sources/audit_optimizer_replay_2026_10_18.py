import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from types import MethodType
import json,io,zipfile,hashlib
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from run_fold_safe_revision import load
from proposed.fold_safe_ehoa import FoldSafeEHOA
from proposed.cost_stable_ehoa import repair_to_budget
from utils import preprocess_train_test

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scientific_audit_2026_10_18'

def replay(job):
    path=ROOT/job['path']; seed=int(job['seed']); external=job['scope']=='external'
    if external:
        p=ROOT/'external_evidence_2026_10_13'; z=zipfile.ZipFile(p/'uci_174.zip')
        frame=pd.read_csv(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('parkinsons.data')))))
        X=frame[['RPDE','DFA','PPE']].to_numpy(); y=frame.status.to_numpy(); groups=frame.name.str.rsplit('_',n=1).str[0].to_numpy()
        costs=np.ones(3); budget=1.; selector_seed=seed
    else:
        allX,ally,allgroups=load(job['dataset']); indices=np.load(path/'split_provenance.npz'); tr=indices['outer_train']
        X=allX[tr]; y=ally[tr]; groups=None if allgroups is None else allgroups[tr]
        costs=np.random.default_rng(1000+X.shape[1]).lognormal(0,.7,X.shape[1]); budget=.3*costs.sum(); selector_seed=seed+100003
    discrete=np.r_[np.ones(33,bool),False] if job['dataset']=='dermatology' else False
    model=FoldSafeEHOA(n_hikers=8,max_iter=10,n_folds=3,alpha=.99,random_state=selector_seed,verbose=False,costs=costs,budget=budget,strategy=job['method'],evidence_resamples=4,lcb_z=1.,groups=groups,discrete_features=discrete)
    original_consider=model._consider_global; original_evaluate=model._evaluate; trace=[]
    def consider(self,position,mask,fitness,accuracy):
        changed=original_consider(position,mask,fitness,accuracy)
        if changed:self.audit_raw_best=np.asarray(mask,dtype=np.uint8).copy()
        return changed
    def evaluate(self,mask):
        count=self.evaluations_; result=original_evaluate(mask)
        trace.append((np.asarray(mask,dtype=np.uint8).copy(),float(result[0]),float(result[1]),self.evaluations_==count))
        return result
    model._consider_global=MethodType(consider,model); model._evaluate=MethodType(evaluate,model)
    mask,_,selected=model.fit(X,y)
    scores=[]; sizes=[]; repaired=[]
    for j,((tr,va),utility) in enumerate(zip(model.inner_indices,model.inner_utilities)):
        selected_inner=np.flatnonzero(model.audit_raw_best if job['method']=='EHOA' else repair_to_budget(model.audit_raw_best,costs,budget,utility))
        xp,yp,xv,_,_=preprocess_train_test(X[tr][:,selected_inner],y[tr],X[va][:,selected_inner],apply_smote=True,random_state=selector_seed+j)
        fitted=KNeighborsClassifier(n_neighbors=min(5,len(yp)),metric='euclidean').fit(xp,yp)
        scores.append(accuracy_score(y[va],fitted.predict(xv))); sizes.append(len(selected_inner))
        repaired.append(np.isin(np.arange(X.shape[1]),selected_inner))
    fitness=.99*(1-np.mean(scores))+.01*np.mean(sizes)/X.shape[1]
    dest=OUT/'optimizer_replay'/job['name']; dest.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(dest/'search_trace.npz',raw_masks=np.vstack([x[0] for x in trace]),fitness=[x[1] for x in trace],accuracy=[x[2] for x in trace],cache_hit=[x[3] for x in trace],winning_raw_mask=model.audit_raw_best,final_mask=mask,winning_inner_masks=np.vstack(repaired),independent_inner_scores=scores)
    oldmask=np.load(path/'mask.npy')
    return {'name':job['name'],'scope':job['scope'],'dataset':job['dataset'],'method':job['method'],'seed':seed,'historical_mask_matches':np.array_equal(mask,oldmask),'historical_fitness_error':None if external else float(abs(model.best_fitness-job['historical_fitness'])),'winning_fitness_recalculation_error':float(abs(model.best_fitness-fitness)),'evaluation_calls_logged':len(trace),'unique_masks_evaluated':model.evaluations_,'cache_hits_logged':sum(x[3] for x in trace),'final_mask_matches_outer_repair':np.array_equal(mask,model.audit_raw_best if job['method']=='EHOA' else repair_to_budget(model.audit_raw_best,costs,budget,model.utility_)),'all_zero_outer_utility':bool(np.all(model.utility_==0)),'inner_subject_overlap':max(x['subject_overlap'] for x in model.split_audit)}

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    old=pd.read_csv(ROOT/'fold_safe_revision_2026_10_12/runs.csv')
    chosen=old[(old.cohort=='primary')&(old.seed==72001)&(old.fold==1)]
    jobs=[{'path':'fold_safe_revision_2026_10_12/jobs/'+row.job,'name':row.job,'scope':'primary','dataset':row.dataset,'method':row.method,'seed':row.seed,'historical_fitness':row.fitness} for row in chosen.itertuples()]
    for path in sorted((ROOT/'external_evidence_2026_10_13/jobs').iterdir()):
        if path.is_dir():
            method,seed=path.name.rsplit('_',1)
            jobs.append({'path':path.relative_to(ROOT).as_posix(),'name':'external_'+path.name,'scope':'external','dataset':'parkinsons_common3','method':method,'seed':int(seed)})
    (OUT/'optimizer_replay_plan.json').write_text(json.dumps({'scope':'Post-hoc current-runtime source-code audit, not new efficacy evidence; all10datasets x5methods firstprimaryseed/fold plus25external fits; historical outputs preserved','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'jobs':jobs},indent=2),encoding='utf-8')
    rows=[]
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures=[pool.submit(replay,job) for job in jobs]
        for future in as_completed(futures):
            rows.append(future.result()); print('Optimizer replay',len(rows),'/',len(jobs),flush=True)
    df=pd.DataFrame(rows).sort_values('name'); df.to_csv(OUT/'optimizer_replay_audit.csv',index=False)
    report={'replays':len(df),'primary_replays':int((df.scope=='primary').sum()),'external_replays':int((df.scope=='external').sum()),'historical_mask_mismatches':int((~df.historical_mask_matches).sum()),'maximum_historical_fitness_error':float(df.historical_fitness_error.max()),'maximum_winning_fitness_recalculation_error':float(df.winning_fitness_recalculation_error.max()),'outer_repair_mismatches':int((~df.final_mask_matches_outer_repair).sum()),'inner_subject_overlap':int(df.inner_subject_overlap.max()),'scope':'Only these75searches replayed on current runtime. Original full optimizer runs not retrospectively instrumented; no historical raw winner trace was saved. Classifier audit covers all1464+25 fixed masks.'}
    (OUT/'optimizer_replay_summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report),flush=True)
