import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[name]='1'
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,hashlib,platform,zipfile,io
import numpy as np
import pandas as pd
import scipy,sklearn,imblearn
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import balanced_accuracy_score,roc_auc_score
from run_fold_safe_revision import load
from utils import preprocess_train_test,calculate_metrics

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scientific_audit_2026_10_18'

def refit(row):
    path=ROOT/row['source_directory']
    X,y,groups=load(row['dataset'])
    indices=np.load(path/'split_provenance.npz')
    tr=indices['outer_train']; te=indices['outer_test']
    selected=np.flatnonzero(np.load(path/'mask.npy'))
    xp,yp,xt,_,_=preprocess_train_test(X[tr][:,selected],y[tr],X[te][:,selected],apply_smote=True,random_state=int(row['seed']))
    model=KNeighborsClassifier(n_neighbors=5,metric='euclidean').fit(xp,yp)
    predicted=model.predict(xt); probability=model.predict_proba(xt)
    recorded=pd.read_csv(path/'predictions.csv')
    calculated=calculate_metrics(y[te],predicted,probability)
    metric_errors={k:float(abs(value-row[k])) for k,value in calculated.items() if not (np.isnan(value) and pd.isna(row[k]))}
    costs=np.random.default_rng(1000+X.shape[1]).lognormal(0,.7,X.shape[1])
    target=OUT/'refit_probabilities'/row['source_directory']
    target.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(target/'predictions.npz',outer_train=tr,outer_test=te,true=y[te],predicted=predicted,probability=probability,classes=model.classes_)
    return {'source_directory':row['source_directory'],'dataset':row['dataset'],'method':row['method'],'seed':int(row['seed']),'outer_record_order_matches':np.array_equal(recorded.row.to_numpy(),te),'outer_true_matches_source':np.array_equal(recorded.true.to_numpy(),y[te]),'prediction_disagreements':int(np.sum(recorded.predicted.to_numpy()!=predicted)),'maximum_metric_error':max(metric_errors.values()),'metric_errors':json.dumps(metric_errors,sort_keys=True),'selected_cost_error':float(abs(costs[selected].sum()-row['selected_cost'])),'constrained_budget_violation':bool(row['method']!='EHOA' and costs[selected].sum()>row['budget_ratio']*costs.sum()+1e-10),'outer_subject_overlap':0 if groups is None else len(set(groups[tr])&set(groups[te])),'train_test_overlap':len(np.intersect1d(tr,te)),'train_test_full_partition':np.array_equal(np.sort(np.r_[tr,te]),np.arange(len(X))),'training_rows_before_smote':len(tr),'training_rows_after_smote':len(yp),'final_classifier_fit_calls':1}

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    old=pd.read_csv(ROOT/'fold_safe_revision_2026_10_12/runs.csv')
    new=pd.read_csv(ROOT/'extended_revision_2026_10_12/runs.csv')
    old['source_directory']='fold_safe_revision_2026_10_12/jobs/'+old.job
    new['source_directory']='extended_revision_2026_10_12/'+new.campaign+'/jobs/'+new.job
    jobs=pd.concat([old,new],ignore_index=True).to_dict('records')
    records=[]
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(refit,row):row['source_directory'] for row in jobs}
        for future in as_completed(futures):
            records.append(future.result())
            if len(records)%100==0:print('Refitted',len(records),'/',len(jobs),flush=True)
    frame=pd.DataFrame(records).sort_values('source_directory')
    frame.to_csv(OUT/'final_classifier_refit_audit.csv',index=False)
    summary={'recorded_runs':len(jobs),'refitted_runs':len(frame),'refit_scope':'Fixed saved feature masks and outer splits; optimizer not rerun','prediction_disagreements':int(frame.prediction_disagreements.sum()),'record_order_mismatches':int((~frame.outer_record_order_matches).sum()),'true_label_mismatches':int((~frame.outer_true_matches_source).sum()),'maximum_metric_error':float(frame.maximum_metric_error.max()),'maximum_cost_error':float(frame.selected_cost_error.max()),'budget_violations':int(frame.constrained_budget_violation.sum()),'outer_subject_overlap':int(frame.outer_subject_overlap.max()),'row_overlap':int(frame.train_test_overlap.max()),'incomplete_outer_partitions':int((~frame.train_test_full_partition).sum()),'refit_classifier_fit_calls':int(frame.final_classifier_fit_calls.sum()),'probabilities_saved':len(list((OUT/'refit_probabilities').rglob('predictions.npz'))),'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'imblearn':imblearn.__version__},'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'final_classifier_refit_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    external=ROOT/'external_evidence_2026_10_13'
    z=zipfile.ZipFile(external/'uci_174.zip')
    source=pd.read_csv(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('parkinsons.data')))))
    target=pd.read_csv(external/'ReplicatedAcousticFeatures-ParkinsonDatabase.csv')
    features=['RPDE','DFA','PPE']; xs=source[features].to_numpy(); ys=source.status.to_numpy(); xt=target[features].to_numpy()
    comparisons=[]
    for job in sorted((external/'jobs').iterdir()):
        if not job.is_dir():continue
        method,seed=job.name.rsplit('_',1); seed=int(seed)
        selected=np.flatnonzero(np.load(job/'mask.npy'))
        xp,yp,xte,_,_=preprocess_train_test(xs[:,selected],ys,xt[:,selected],apply_smote=True,random_state=seed)
        model=KNeighborsClassifier(n_neighbors=5,metric='euclidean').fit(xp,yp)
        probability=model.predict_proba(xte)[:,list(model.classes_).index(1)]
        saved=pd.read_csv(job/'external_predictions.csv')
        comparisons.append({'job':job.name,'target_order_matches':np.array_equal(saved.subject,target.ID),'labels_match':np.array_equal(saved['true'],target.Status),'maximum_probability_error':float(np.max(np.abs(saved.probability_pd-probability))),'prediction_disagreements':int(np.sum(saved.predicted.to_numpy()!=(probability>=.5).astype(int)))})
    pd.DataFrame(comparisons).to_csv(OUT/'external_classifier_refit_audit.csv',index=False)
    print(json.dumps(summary),flush=True)
    print('External25 maximum probability error',max(row['maximum_probability_error'] for row in comparisons),flush=True)
