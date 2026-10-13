import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ[k]='1'
from pathlib import Path
import hashlib,json,zipfile,io,urllib.request
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import balanced_accuracy_score,roc_auc_score,confusion_matrix
from proposed.fold_safe_ehoa import FoldSafeEHOA
from utils import preprocess_train_test

r=Path(__file__).resolve().parent
p=r/'external_evidence_2026_10_13'
p.mkdir(exist_ok=True)
features=['RPDE','DFA','PPE']
protocol={'created_utc':datetime.now(timezone.utc).isoformat(),'source':'UCI174 Oxford','target':'UCI489 replicated acoustic features','features':features,'feature_mapping':'Exact shared names only; extraction/calibration equivalence not established','seeds':[72001,72002,72003,72004,72005],'methods':['EHOA','random','cheapest','mi','stable_lcb'],'source_fit':'All source observations, inner 3-fold StratifiedGroupKFold, 8 hikers x10 iterations; source-only utility/imputation/scaling/SMOTE','budget':'One of three common columns, equal synthetic costs; EHOA unconstrained comparator','target_use':'Prediction and evaluation only; no target fitting, tuning or feature selection','classifier':'5-neighbor Euclidean KNN','subject_unit':'Mean predicted probability across three target recordings; threshold >=0.5','bootstrap':'10000 stratified subject resamples seed20261013, descriptive 95% intervals for five-seed mean-probability ensemble per method','scope':'Exploratory external public-dataset transfer on a restricted common feature space; not original 22-feature model validation or prospective clinical validation','historical_records':'Cannot create missing past evidence','author_signoff':'Not approved by author'}
if not (p/'protocol.json').exists():
    (p/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    (p/'protocol_code_sha256.json').write_text(json.dumps({'run_external_evidence.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2),encoding='utf-8')
    print('Protocol prepared; run again only after public commit')
    raise SystemExit
if not (p/'publication.json').exists():
    raise RuntimeError('Public protocol commit record required before execution')
z=zipfile.ZipFile(p/'uci_174.zip')
source=pd.read_csv(io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('parkinsons.data')))))
target=pd.read_csv(p/'ReplicatedAcousticFeatures-ParkinsonDatabase.csv')
xs=source[features].to_numpy(); ys=source.status.to_numpy(); gs=source.name.str.rsplit('_',n=1).str[0].to_numpy()
xt=target[features].to_numpy(); yt=target.Status.to_numpy(); gt=target.ID.to_numpy()
if target.groupby('ID').Status.nunique().max()!=1:
    raise ValueError('Inconsistent target subject labels')
rows=[]; probs={m:[] for m in protocol['methods']}
for m in protocol['methods']:
    for seed in protocol['seeds']:
        model=FoldSafeEHOA(n_hikers=8,max_iter=10,n_folds=3,alpha=.99,random_state=seed,verbose=False,costs=np.ones(3),budget=1.,strategy=m,evidence_resamples=4,lcb_z=1.,groups=gs,discrete_features=False)
        mask,_,selected=model.fit(xs,ys)
        xp,yp,xte,_,_=preprocess_train_test(xs[:,selected],ys,xt[:,selected],apply_smote=True,random_state=seed)
        clf=KNeighborsClassifier(n_neighbors=5,metric='euclidean').fit(xp,yp)
        probability=clf.predict_proba(xte)[:,list(clf.classes_).index(1)]
        pred=(probability>=.5).astype(int)
        probs[m].append(probability)
        job=p/'jobs'/f'{m}_{seed}'; job.mkdir(parents=True,exist_ok=True)
        np.save(job/'mask.npy',mask)
        pd.DataFrame({'subject':gt,'true':yt,'probability_pd':probability,'predicted':pred}).to_csv(job/'external_predictions.csv',index=False)
        pd.DataFrame(model.split_audit).to_csv(job/'inner_split_audit.csv',index=False)
        pd.DataFrame(model.candidate_audit).to_csv(job/'candidate_audit.csv',index=False)
        row={'method':m,'seed':seed,'selected_features':','.join(np.asarray(features)[selected]),'selected_count':len(selected),'recording_balanced_accuracy':balanced_accuracy_score(yt,pred),'inner_subject_overlap':max(a['subject_overlap'] for a in model.split_audit),'target_used_for_fit':False}
        rows.append(row)
pd.DataFrame(rows).to_csv(p/'external_runs.csv',index=False)
summary=[]
for m in protocol['methods']:
    df=pd.DataFrame({'subject':gt,'true':yt,'probability_pd':np.mean(probs[m],axis=0)}).groupby('subject').agg(true=('true','first'),probability_pd=('probability_pd','mean'))
    y=df.true.to_numpy(); pr=df.probability_pd.to_numpy(); pred=(pr>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    rng=np.random.default_rng(20261013); blocks=[np.flatnonzero(y==v) for v in [0,1]]
    boot=[]
    for _ in range(10000):
        ix=np.r_[rng.choice(blocks[0],len(blocks[0]),replace=True),rng.choice(blocks[1],len(blocks[1]),replace=True)]
        boot.append((np.mean(pred[ix][y[ix]==0]==0)+np.mean(pred[ix][y[ix]==1]==1))/2)
    df['predicted']=pred; df.to_csv(p/f'{m}_subject_predictions.csv')
    summary.append({'method':m,'subjects':len(df),'balanced_accuracy':balanced_accuracy_score(y,pred),'descriptive_ci_low':np.quantile(boot,.025),'descriptive_ci_high':np.quantile(boot,.975),'sensitivity_pd':tp/(tp+fn),'specificity_control':tn/(tn+fp),'auc':roc_auc_score(y,pr),'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)})
pd.DataFrame(summary).to_csv(p/'external_subject_metrics.csv',index=False)
audit={'source_recordings':len(source),'source_prefixes':len(set(gs)),'source_pd_prefixes':source.assign(group=gs).groupby('group').status.first().sum().item(),'target_recordings':len(target),'target_subjects':target.ID.nunique(),'target_recordings_per_subject':target.groupby('ID').size().unique().tolist(),'target_class_subject_counts':target.groupby('ID').Status.first().value_counts().to_dict(),'common_features':features,'source_inner_subject_overlap':max(row['inner_subject_overlap'] for row in rows),'target_fit_calls':0,'external_runs':len(rows),'clinical_identity_confirmed':False}
(p/'external_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
primary=pd.read_csv(r/'extended_revision_2026_10_12/analysis/primary_five_seed_runs.csv')
bc=primary[primary.dataset=='breast_cancer'].copy()
bc['illustrative_shared_fna_fee_usd']=np.where(bc.selected_features>0,164.34,0.)
bc['clinical_group_cost_ratio']=np.where(bc.selected_features>0,1.,0.)
bc['clinical_fee_saving_usd']=164.34-bc.illustrative_shared_fna_fee_usd
bc.to_csv(p/'breast_shared_service_cost_audit.csv',index=False)
(p/'cost_model.json').write_text(json.dumps({'source_url':'https://dphhs.mt.gov/assets/publichealth/Cancer/MCCP2025FeeSchedule.pdf','document_effective_date':'2024-06-30','page':3,'currency':'USD','code':'88173','global_fna_interpretation_fee':164.34,'technical_fee':98.21,'professional_fee':66.13,'mapping':'Illustrative shared-service grouping of all 30 WDBC image-derived columns; not a validated patient invoice or WDBC feature-extraction tariff','excluded':'Needle collection, imaging, additional visits, feature-computation time and risk; unknown marginal charges','cost_function':'C(S)=164.34 if S is nonempty, else 0','implication':'Nonempty subsets cannot save this shared-service fee; budget30% infeasible under this group-only cost model','primary_masks_audited':len(bc),'nonempty_masks':int((bc.selected_features>0).sum()),'claims':'No Iran/current-2026 tariff claim; no measured per-feature time/risk or clinical saving claim'},indent=2),encoding='utf-8')
print(pd.DataFrame(summary).to_string(index=False))
print(json.dumps(audit))
