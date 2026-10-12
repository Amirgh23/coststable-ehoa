from pathlib import Path
import io, urllib.request, json, time
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import ehoa
from ehoa import EHOA
from proposed.cost_stable_ehoa import CostStableEHOA
from utils import PreparedFold, _resample_training, preprocess_train_test, calculate_metrics
from proposed.stability import compute_nogueira_stability, compute_jaccard_stability

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'revision_2026_10_12'
(OUT/'corrected_experiments/masks').mkdir(parents=True,exist_ok=True)
url='https://archive.ics.uci.edu/static/public/174/parkinsons.zip'
import zipfile
payload=urllib.request.urlopen(url,timeout=45).read()
(OUT/'sources/parkinsons_uci.zip').write_bytes(payload)
z=zipfile.ZipFile(io.BytesIO(payload))
member=next(x for x in z.namelist() if x.endswith('parkinsons.data'))
orig=pd.read_csv(z.open(member))
par=pd.read_csv(ROOT/'data/benchmark_v2/parkinsons.csv')
features=orig.drop(columns=['name','status'])
mapping=[]
for row in par.drop(columns='target').to_numpy():
    hits=np.flatnonzero(np.isclose(features.to_numpy(),row,rtol=1e-10,atol=1e-12).all(axis=1))
    if len(hits)!=1:raise ValueError('Parkinson row cannot be uniquely matched to UCI recording')
    mapping.append(int(hits[0]))
group_names=orig.name.iloc[mapping].str.rsplit('_',n=1).str[0].to_numpy()
(OUT/'corrected_experiments/subject_count_note.json').write_text(json.dumps({'distinct_recording_subject_prefixes':len(np.unique(group_names)),'UCI_narrative_subject_count':31,'grouping_rule':'recording name with final recording index removed','all_rows_uniquely_matched':True},indent=2),encoding='utf-8')
if not np.array_equal(orig.status.iloc[mapping].to_numpy(),par.target.to_numpy()):raise ValueError('Parkinson label mapping mismatch')
pd.DataFrame(dict(snapshot_row=range(len(par)),uci_row=mapping,subject=group_names,target=par.target)).to_csv(OUT/'corrected_experiments/parkinson_subject_mapping.csv',index=False)
steel=pd.read_csv(ROOT/'data/benchmark_v2/steel_plates_fault.csv')
indicators=steel[[f'V{i}' for i in range(28,34)]+['target']].to_numpy()
if not np.isin(indicators,[0,1]).all() or not np.all(indicators.sum(axis=1)==1):raise ValueError('Invalid fault indicators')
steel_corrected=steel[[f'V{i}' for i in range(1,28)]].copy()
steel_corrected['target']=indicators.argmax(axis=1)
steel_corrected.to_csv(OUT/'corrected_experiments/steel_27_features_7_classes.csv',index=False)
M=['EHOA','Budget-random','Budget-cheapest','Budget-mi','Budget-stable_lcb']
target=OUT/'corrected_experiments/runs.csv'
rows=pd.read_csv(target).to_dict('records') if target.exists() else []
done={(r['dataset'],r['method'],int(r['seed']),r['fold']) for r in rows}
proof=[]
base_prepare=ehoa.prepare_cv_folds
for ds,frame,groups in [('steel_plates_fault',steel_corrected,None),('parkinsons',par,group_names)]:
    X=frame.drop(columns='target').to_numpy(float);y=frame.target.to_numpy(int)
    costs=np.random.default_rng(1000+X.shape[1]).lognormal(0,.7,X.shape[1]);budget=.3*costs.sum()
    for seed in [71001,71002]:
        outer=StratifiedKFold(3,shuffle=True,random_state=seed) if groups is None else StratifiedGroupKFold(3,shuffle=True,random_state=seed)
        splits=outer.split(X,y) if groups is None else outer.split(X,y,groups)
        for k,(tr,te) in enumerate(splits,1):
            fold=f'outer_{k}';ss=seed+k*100003
            if groups is not None:
                outer_overlap=sorted(set(groups[tr])&set(groups[te]))
                if outer_overlap:raise ValueError('Outer subject overlap')
                training_groups=groups[tr]
                def grouped_prepare(X_train,y_train,n_folds,random_state,apply_smote):
                    cv=StratifiedGroupKFold(n_folds,shuffle=True,random_state=random_state);result=[]
                    for j,(itr,iva) in enumerate(cv.split(X_train,y_train,training_groups)):
                        overlap=sorted(set(training_groups[itr])&set(training_groups[iva]))
                        if overlap:raise ValueError('Inner subject overlap')
                        proof.append(dict(dataset=ds,seed=seed,outer_fold=k,inner_fold=j+1,outer_subject_overlap=0,inner_subject_overlap=0,train_subjects=len(np.unique(training_groups[itr])),validation_subjects=len(np.unique(training_groups[iva]))))
                        imp=SimpleImputer(strategy='mean');sc=StandardScaler()
                        xt=sc.fit_transform(imp.fit_transform(X_train[itr]));xv=sc.transform(imp.transform(X_train[iva]));yt=y_train[itr]
                        if apply_smote:xt,yt=_resample_training(xt,yt,random_state+j)
                        result.append(PreparedFold(xt,yt,xv,y_train[iva]))
                    return result
                ehoa.prepare_cv_folds=grouped_prepare
            else:ehoa.prepare_cv_folds=base_prepare
            for method in M:
                if (ds,method,seed,fold) in done:continue
                common=dict(n_hikers=8,max_iter=10,n_folds=3,alpha=.99,random_state=ss,verbose=False)
                model=EHOA(**common) if method=='EHOA' else CostStableEHOA(**common,costs=costs,budget=budget,strategy=method.removeprefix('Budget-'),evidence_resamples=4,lcb_z=1)
                started=time.perf_counter();mask,_,idx=model.fit(X[tr],y[tr]);elapsed=time.perf_counter()-started
                xp,yp,xte,_,_=preprocess_train_test(X[tr],y[tr],X[te],apply_smote=True,random_state=seed)
                knn=KNeighborsClassifier(n_neighbors=5,metric='euclidean');knn.fit(xp[:,idx],yp)
                metrics=calculate_metrics(y[te],knn.predict(xte[:,idx]),knn.predict_proba(xte[:,idx]))
                mp=OUT/'corrected_experiments/masks'/f'{ds}_{method}_{seed}_{fold}.npy';np.save(mp,mask.astype(np.uint8))
                scost=float(costs[mask.astype(bool)].sum())
                rows.append(dict(dataset=ds,method=method,seed=seed,selector_seed=ss,fold=fold,N=len(X),D=X.shape[1],train_size=len(tr),test_size=len(te),selected_features=len(idx),selected_ratio=len(idx)/X.shape[1],selected_cost=scost,total_cost=costs.sum(),cost_ratio=scost/costs.sum(),budget_ratio=.3,fitness=model.best_fitness,evaluations=model.evaluations_,runtime_seconds=model.runtime_seconds_,fit_total_seconds=elapsed,mask_path=str(mp.relative_to(ROOT)),status='complete',analysis_status='new exploratory correction',split_unit='subject' if groups is not None else 'row',**metrics))
                pd.DataFrame(rows).to_csv(target,index=False)
                print(f'{ds} {method} {seed} {fold} BA={metrics["balanced_accuracy"]:.4f}',flush=True)
ehoa.prepare_cv_folds=base_prepare
raw=pd.DataFrame(rows)
for (ds,m),g in raw.groupby(['dataset','method']):
    masks=np.vstack([np.load(ROOT/p) for p in g.mask_path])
    raw.loc[g.index,'nogueira_stability']=compute_nogueira_stability(masks);raw.loc[g.index,'jaccard_stability']=compute_jaccard_stability(masks)
raw.to_csv(target,index=False)
pd.DataFrame(proof).drop_duplicates().to_csv(OUT/'corrected_experiments/subject_split_audit.csv',index=False)
print('Completed',len(raw),'new exploratory runs')
