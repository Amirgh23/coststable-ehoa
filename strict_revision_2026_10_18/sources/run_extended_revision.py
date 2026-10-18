import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,hashlib,traceback,itertools,sys
import pandas as pd
import numpy as np
import run_fold_safe_revision as base
from proposed.fold_safe_ehoa import FoldSafeEHOA

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'extended_revision_2026_10_12'

def plan():
    jobs=[]
    for ds,m,s,k in itertools.product(base.D,base.M,[72004,72005],[1,2,3]):jobs.append(dict(campaign='extra_seeds',dataset=ds,method=m,seed=s,fold=k,budget=.3,R=4,lambda_penalty=1.,population=8,iterations=10))
    for ds,k,b,r,lam in itertools.product(base.D,[1,2,3],[.15,.5],[4,8],[0.,2.]):jobs.append(dict(campaign='factorial',dataset=ds,method='stable_lcb',seed=72001,fold=k,budget=b,R=r,lambda_penalty=lam,population=8,iterations=10))
    for ds,m,k in itertools.product(base.D,base.M,[1,2,3]):jobs.append(dict(campaign='larger_search',dataset=ds,method=m,seed=72001,fold=k,budget=.3,R=4,lambda_penalty=1.,population=16,iterations=20))
    return jobs

def execute(job):
    original=base.FoldSafeEHOA
    original_path=base.P
    def configured(*args,**kwargs):
        kwargs['n_hikers']=job['population']
        kwargs['max_iter']=job['iterations']
        return FoldSafeEHOA(*args,**kwargs)
    base.P=OUT/job['campaign']
    base.FoldSafeEHOA=configured
    try:row=base.execute((job['dataset'],job['method'],job['seed'],job['fold'],job['budget'],job['R'],job['lambda_penalty'],job['campaign']))
    finally:
        base.P=original_path
        base.FoldSafeEHOA=original
    row.update(campaign=job['campaign'],n_hikers=job['population'],max_iter=job['iterations'])
    path=OUT/job['campaign']/'jobs'/row['job']/'result.json'
    path.write_text(json.dumps(row,indent=2),encoding='utf-8')
    return row

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    jobs=plan()
    frozen=OUT/'protocol.json'
    if not frozen.exists():
        config=dict(created_utc=datetime.now(timezone.utc).isoformat(),planned_runs=len(jobs),extra_seed_runs=300,factorial_runs=240,larger_search_runs=150,primary_total_seeds=[72001,72002,72003,72004,72005],datasets=base.D,factorial=dict(design='complete 2x2x2 at endpoints; no outer-test tuning',budget_levels=[.15,.5],R_levels=[4,8],lambda_levels=[0,2],seed=72001,outer_folds=3,analysis='dataset-block descriptive factorial contrasts; one stochastic seed; not exhaustive continuous-space interactions'),larger_search=dict(population=16,iterations=20,reference_population=8,reference_iterations=10,seed=72001,methods=base.M,analysis='paired dataset-block descriptive differences; not convergence proof'),registration='Prospective extension after prior outcomes known; publish protocol and code hash commit before execution; not retrospective preregistration',stats=dict(primary_unit='dataset',primary_metric='balanced_accuracy',friedman_df=4,paired='two-sided Wilcoxon; resampled versus four controls',multiplicity='Holm within metric and all 24 contrasts',bootstrap='20000 dataset-block draws; seed 20261012; descriptive unadjusted intervals'),excluded_claims=['real medical prices','external clinical validity','independent clinical identity confirmation','confidence coverage of mean minus SD','false selection error control','guaranteed optimizer convergence'])
        frozen.write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
        hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['run_extended_revision.py','run_fold_safe_revision.py','proposed/fold_safe_ehoa.py','proposed/cost_stable_ehoa.py','ehoa.py','utils.py']}
        hashes['protocol.json']=hashlib.sha256(frozen.read_bytes()).hexdigest()
        (OUT/'frozen_sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
        (OUT/'planned_jobs.json').write_text(json.dumps(jobs,indent=2),encoding='utf-8')
    expected=json.loads((OUT/'frozen_sha256.json').read_text())
    for name,digest in expected.items():
        if hashlib.sha256((OUT/name if name=='protocol.json' else ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen content changed: '+name)
    if '--prepare-only' in sys.argv:
        print('Prepared immutable extension protocol:',len(jobs),'runs')
        sys.exit(0)
    publication=OUT/'publication.json'
    if not publication.exists():raise ValueError('Public protocol commit not recorded before execution')
    rows=[json.loads(file.read_text()) for file in OUT.glob('*/jobs/*/result.json')]
    done={(row['campaign'],row['job']) for row in rows}
    pending=[job for job in jobs if (job['campaign'],f'{job["dataset"]}_{job["method"]}_{job["seed"]}_{job["fold"]}_b{job["budget"]}_r{job["R"]}_l{job["lambda_penalty"]}') not in done]
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(execute,job):job for job in pending}
        for future in as_completed(futures):
            try:
                rows.append(future.result())
                if len(rows)%20==0:
                    pd.DataFrame(rows).to_csv(OUT/'runs.csv',index=False)
                    print(f'Completed {len(rows)}/{len(jobs)}',flush=True)
            except Exception:
                with (OUT/'failure_log.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(job=futures[future],created_utc=datetime.now(timezone.utc).isoformat(),traceback=traceback.format_exc()))+'\n')
                print('FAILED '+str(futures[future]),flush=True)
    pd.DataFrame(rows).to_csv(OUT/'runs.csv',index=False)
    print('Completed',len(rows),'of',len(jobs),flush=True)
