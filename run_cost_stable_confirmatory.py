"""Resumable confirmatory benchmark for cost-stable EHOA."""
from __future__ import annotations
import argparse,hashlib,json,traceback,time
from pathlib import Path
import numpy as np,pandas as pd,psutil,yaml
from ehoa import EHOA
from proposed import CostStableEHOA
from proposed.stability import compute_jaccard_stability,compute_nogueira_stability
from run_experiments import load_data,evaluation_splits
from utils import evaluate_classifiers

ROOT=Path(__file__).resolve().parent
EXTERNAL={n:{'path':f'data/benchmark_v2/{n}.csv','target':'target'} for n in ['ionosphere','sonar','dermatology','spambase','parkinsons','hill_valley','steel_plates_fault','madelon']}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--config',type=Path,default=Path('configs/cost_stable_confirmatory.yaml')); ap.add_argument('--output',type=Path,default=Path('results/cost_stable_confirmatory')); args=ap.parse_args()
 cfg=yaml.safe_load(args.config.read_text(encoding='utf-8')); out=args.output; (out/'raw').mkdir(parents=True,exist_ok=True); (out/'logs').mkdir(exist_ok=True); (out/'masks').mkdir(exist_ok=True)
 config_hash=hashlib.sha256(args.config.read_bytes()).hexdigest(); raw_path=out/'raw'/'runs.csv'; fail_path=out/'logs'/'failures.csv'
 rows=pd.read_csv(raw_path).to_dict('records') if cfg['resume'] and raw_path.exists() else []; done={(r['dataset'],r['method'],int(r['seed']),r['fold']) for r in rows}
 split_cfg={'evaluation_protocol':'repeated_nested_cv','seeds':cfg['seeds'],'outer_folds':cfg['outer_folds'],'external_datasets':EXTERNAL}
 failures=[]
 for ds in cfg['datasets']:
  X,y=load_data(ds,split_cfg); rng=np.random.default_rng(cfg['cost_seed_offset']+X.shape[1]); costs=rng.lognormal(0,cfg['cost_lognormal_sigma'],X.shape[1]); budget=cfg['budget_ratio']*costs.sum()
  for seed,fold,selector_seed,tr,te in evaluation_splits(X,y,split_cfg):
   for method in cfg['methods']:
    key=(ds,method,seed,fold)
    if key in done: continue
    started=time.perf_counter(); process=psutil.Process(); rss0=process.memory_info().rss
    try:
     common=dict(n_hikers=cfg['population'],max_iter=cfg['iterations'],n_folds=cfg['inner_folds'],alpha=cfg['alpha'],random_state=selector_seed,verbose=False)
     if method=='EHOA': model=EHOA(**common)
     else: model=CostStableEHOA(**common,costs=costs,budget=budget,strategy=method.removeprefix('Budget-'),evidence_resamples=cfg['evidence_resamples'],lcb_z=cfg['lcb_z'])
     mask,_,features=model.fit(X[tr],y[tr]); metrics,_,_=evaluate_classifiers(X[tr],y[tr],X[te],y[te],features,random_state=seed); knn=metrics[metrics.classifier=='knn'].iloc[0]
     mask_id=f'{ds}_{method}_{seed}_{fold}'.replace('/','_'); np.save(out/'masks'/f'{mask_id}.npy',mask.astype(np.uint8))
     selected_cost=float(costs[mask.astype(bool)].sum())
     mask_path=(out/'masks'/f'{mask_id}.npy').resolve()
     row={'dataset':ds,'method':method,'seed':seed,'selector_seed':selector_seed,'fold':fold,'N':len(X),'D':X.shape[1],'train_size':len(tr),'test_size':len(te),'selected_features':len(features),'selected_ratio':len(features)/X.shape[1],'selected_cost':selected_cost,'total_cost':float(costs.sum()),'cost_ratio':selected_cost/costs.sum(),'budget_ratio':cfg['budget_ratio'],'balanced_accuracy':float(knn.balanced_accuracy),'f1_score':float(knn.f1_score),'mcc':float(knn.mcc),'roc_auc':float(knn.roc_auc),'pr_auc':float(knn.pr_auc),'sensitivity':float(knn.sensitivity),'specificity':float(knn.specificity),'accuracy':float(knn.accuracy),'fitness':model.best_fitness,'evaluations':model.evaluations_,'runtime_seconds':model.runtime_seconds_,'peak_rss_mb':max(rss0,process.memory_info().rss)/1048576,'mask_path':str(mask_path.relative_to(ROOT)),'status':'complete','config_hash':config_hash}
     rows.append(row); pd.DataFrame(rows).to_csv(raw_path,index=False); done.add(key)
    except Exception as e:
     failures.append({'dataset':ds,'method':method,'seed':seed,'fold':fold,'exception':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'elapsed':time.perf_counter()-started,'status':'failed'}); pd.DataFrame(failures).to_csv(fail_path,index=False)
 # External stability is computed only after all independent masks exist.
 raw=pd.DataFrame(rows)
 for (ds,method),g in raw.groupby(['dataset','method']):
  masks=np.vstack([np.load(ROOT/p) for p in g.mask_path]); raw.loc[g.index,'jaccard_stability']=compute_jaccard_stability(masks); raw.loc[g.index,'nogueira_stability']=compute_nogueira_stability(masks)
 raw.to_csv(raw_path,index=False); print(f'complete={len(raw)}/{len(cfg["datasets"])*len(cfg["methods"])*len(cfg["seeds"])*cfg["outer_folds"]} failures={len(failures)}')
if __name__=='__main__': main()
