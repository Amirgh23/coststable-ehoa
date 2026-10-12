from pathlib import Path
import hashlib, json, itertools, sys, zipfile
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon, rankdata
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_experiments import load_data
EXTERNAL={n:{'path':f'data/benchmark_v2/{n}.csv','target':'target'} for n in ['ionosphere','sonar','dermatology','spambase','parkinsons','hill_valley','steel_plates_fault','madelon']}
from proposed.stability import compute_nogueira_stability, compute_jaccard_stability

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'revision_2026_10_12'
OUT.mkdir(exist_ok=True)
for name in ['analysis', 'figures', 'sources', 'qa', 'supplement']:
    (OUT / name).mkdir(exist_ok=True)
METHODS = ['EHOA','Budget-random','Budget-cheapest','Budget-mi','Budget-stable_lcb']
LABELS = ['EHOA','Random/cost','Cheapest','MI/cost','Resampled/cost']
d = pd.read_csv(ROOT/'results/cost_stable_confirmatory/raw/runs.csv')
dataset_rows, frequency_rows, mask_rows, cost_rows = [], [], [], []
ids = dict(ionosphere=59, sonar=40, dermatology=35, spambase=44, parkinsons=1488, hill_valley=1479, steel_plates_fault=1504, madelon=1485)
uci = dict(breast_cancer=17,wine=109,ionosphere=52,sonar=151,dermatology=33,spambase=94,parkinsons=174,hill_valley=147,steel_plates_fault=198,madelon=171)
for ds in d.dataset.drop_duplicates():
    path = ROOT/'data'/f'{ds}.csv' if ds in ['breast_cancer','wine'] else ROOT/'data/benchmark_v2'/f'{ds}.csv'
    raw = pd.read_csv(path)
    X,y = load_data(ds, {'external_datasets':EXTERNAL})
    costs = np.random.default_rng(1000+X.shape[1]).lognormal(0,.7,X.shape[1])
    dataset_rows.append(dict(dataset=ds,N_snapshot=len(raw),D_snapshot=len(raw.columns)-1,N_used=len(X),D_used=X.shape[1],classes=len(np.unique(y)),class_counts_snapshot=json.dumps(raw.target.value_counts().sort_index().to_dict()),class_counts_used=json.dumps(dict(zip(*[a.tolist() for a in np.unique(y,return_counts=True)]))),missing_cells=int(raw.isna().sum().sum()),removed_exact_duplicates=len(raw)-len(X),feature_encoding='No runtime one-hot encoding; numeric snapshot as supplied',snapshot_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),snapshot_source=f'https://www.openml.org/d/{ids[ds]}' if ds in ids else f'https://archive.ics.uci.edu/dataset/{uci[ds]}',original_source=f'https://archive.ics.uci.edu/dataset/{uci[ds]}',total_cost=costs.sum(),absolute_budget=.3*costs.sum(),cost_seed=1000+X.shape[1]))
    for j,name in enumerate(raw.columns.drop('target')):
        cost_rows.append(dict(dataset=ds,feature_index=j,feature=name,cost=costs[j],budget=.3*costs.sum()))
    for method,g in d[d.dataset==ds].groupby('method'):
        masks=[]
        for _,row in g.iterrows():
            p=ROOT/str(row.mask_path).replace('\\','/')
            m=np.load(p)
            masks.append(m)
            sc=float(costs[m.astype(bool)].sum())
            mask_rows.append(dict(dataset=ds,method=method,seed=int(row.seed),fold=row.fold,binary=bool(np.isin(m,[0,1]).all()),D=len(m),selected=int(m.sum()),count_matches=bool(m.sum()==row.selected_features),cost_recomputed=sc,cost_difference=sc-row.selected_cost,budget_violation=sc>.3*costs.sum()+1e-12,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        a=np.vstack(masks)
        phi=compute_nogueira_stability(a)
        jac=compute_jaccard_stability(a)
        for j,name in enumerate(raw.columns.drop('target')):
            frequency_rows.append(dict(dataset=ds,method=method,feature_index=j,feature=name,selected_count=int(a[:,j].sum()),masks=len(a),frequency=float(a[:,j].mean()),synthetic_cost=float(costs[j])))
        d.loc[g.index,'nogueira_recomputed']=phi
        d.loc[g.index,'jaccard_recomputed']=jac
pd.DataFrame(dataset_rows).to_csv(OUT/'analysis/datasets.csv',index=False)
pd.DataFrame(cost_rows).to_csv(OUT/'analysis/feature_costs.csv',index=False)
pd.DataFrame(mask_rows).to_csv(OUT/'analysis/mask_audit.csv',index=False)
freq=pd.DataFrame(frequency_rows)
freq.to_csv(OUT/'analysis/selection_frequencies.csv',index=False)
metrics=['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','jaccard_stability','runtime_seconds']
mean=d.groupby(['dataset','method'])[metrics].mean().reset_index()
mean.to_csv(OUT/'analysis/dataset_method_means.csv',index=False)
overall=mean.groupby('method')[metrics].mean().reindex(METHODS)
overall['budget_violations']=d.assign(violation=d.cost_ratio>d.budget_ratio+1e-12).groupby('method').violation.sum()
overall['n_runs']=d.groupby('method').size()
overall.to_csv(OUT/'analysis/overall.csv')

def holm(ps):
    ps=np.asarray(ps)
    order=np.argsort(ps)
    a=np.empty(len(ps)); running=0
    for k,i in enumerate(order):
        running=max(running,(len(ps)-k)*ps[i]); a[i]=min(1,running)
    return a

friedman, rankrows, pairs = [], [], []
rng=np.random.default_rng(20261012)
for metric in metrics:
    p=mean.pivot(index='dataset',columns='method',values=metric)[METHODS]
    higher=metric in ['balanced_accuracy','nogueira_stability','jaccard_stability']
    ranks=np.array([rankdata(-r if higher else r) for r in p.values])
    fr=friedmanchisquare(*p.values.T)
    friedman.append(dict(metric=metric,n_datasets=len(p),n_methods=5,df=4,statistic=fr.statistic,p_raw=fr.pvalue,analysis='Retrospective reanalysis; asymptotic Friedman p'))
    for j,m in enumerate(METHODS):
        rankrows.append(dict(metric=metric,method=m,average_rank=ranks[:,j].mean(),rank_direction='1 best'))
    for m in METHODS[:-1]:
        delta=(p['Budget-stable_lcb']-p[m]).to_numpy()
        nz=delta[delta!=0]
        ranks_abs=rankdata(abs(nz))
        effect=float((ranks_abs[nz>0].sum()-ranks_abs[nz<0].sum())/ranks_abs.sum()) if len(nz) else 0.
        w=wilcoxon(delta,zero_method='wilcox',alternative='two-sided',method='auto')
        observed=abs(delta.sum())
        signs=np.array(list(itertools.product([-1,1],repeat=len(delta))))
        signp=float(np.mean(abs(signs@delta)>=observed-1e-14))
        boots=delta[rng.integers(0,len(delta),(20000,len(delta)))].mean(axis=1)
        pairs.append(dict(metric=metric,reference=m,method='Budget-stable_lcb',n_datasets=len(p),mean_delta=delta.mean(),median_delta=np.median(delta),wilcoxon_W=w.statistic,p_raw=w.pvalue,signflip_mean_p=signp,rank_biserial=effect,ci95_low=np.quantile(boots,.025),ci95_high=np.quantile(boots,.975),wins=int((delta>0).sum()),ties=int((delta==0).sum()),losses=int((delta<0).sum()),ci_method='Dataset percentile bootstrap 20000 draws; seed 20261012; descriptive, unadjusted'))
fr=pd.DataFrame(friedman); fr['p_holm_six_metrics']=holm(fr.p_raw); fr.to_csv(OUT/'analysis/friedman.csv',index=False)
pd.DataFrame(rankrows).to_csv(OUT/'analysis/average_ranks.csv',index=False)
pr=pd.DataFrame(pairs)
pr['p_holm_within_metric']=pr.groupby('metric').p_raw.transform(lambda x:holm(x.to_numpy()))
pr['p_holm_all_24']=holm(pr.p_raw)
pr.to_csv(OUT/'analysis/paired_comparisons.csv',index=False)
pd.DataFrame([{'metric':x,'status':'Primary metric in supplied config' if x=='balanced_accuracy' else 'Secondary descriptive/exploratory','analysis_date':'2026-10-12'} for x in metrics]).to_csv(OUT/'analysis/analysis_scope.csv',index=False)
audit=dict(rows=len(d),datasets=d.dataset.nunique(),methods=d.method.nunique(),duplicate_keys=int(d.duplicated(['dataset','method','seed','fold']).sum()),missing_cells=int(d.isna().sum().sum()),status_values=d.status.unique().tolist(),mask_count=len(mask_rows),all_binary=all(x['binary'] for x in mask_rows),all_counts_match=all(x['count_matches'] for x in mask_rows),max_cost_error=max(abs(x['cost_difference']) for x in mask_rows),max_stability_error=float(abs(d.nogueira_stability-d.nogueira_recomputed).max()),constrained_budget_violations=sum(x['budget_violation'] for x in mask_rows if x['method']!='EHOA'),unconstrained_budget_exceedances=sum(x['budget_violation'] for x in mask_rows if x['method']=='EHOA'),raw_sha256=hashlib.sha256((ROOT/'results/cost_stable_confirmatory/raw/runs.csv').read_bytes()).hexdigest(),config_current_sha256=hashlib.sha256((ROOT/'configs/cost_stable_confirmatory.yaml').read_bytes()).hexdigest(),run_config_hashes=d.config_hash.unique().tolist(),execution_failure_logs_present=(ROOT/'results/cost_stable_confirmatory/logs').exists(),preregistration_evidence='No dated immutable registration supplied',raw_reanalysis_only=True,python=sys.version)
(OUT/'analysis/audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2,default=int),encoding='utf-8')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
colors=['#4c4c4c','#d08c28','#338a76','#386db7','#a13b60']
fig,axes=plt.subplots(1,2,figsize=(7.1,2.65))
for i,m in enumerate(METHODS):
    axes[0].scatter(overall.loc[m,'cost_ratio'],overall.loc[m,'balanced_accuracy'],color=colors[i],s=42,label=LABELS[i])
axes[0].axvline(.3,color='#888888',ls='--',lw=.8)
axes[0].set(xlabel='Selected / total synthetic cost',ylabel='Mean balanced accuracy',ylim=(.824,.836))
axes[0].legend(fontsize=6,loc='upper right')
axes[1].barh(LABELS,overall.nogueira_stability,color=colors)
axes[1].set(xlabel='Mean Nogueira stability',xlim=(0,.31))
fig.tight_layout()
for ext in ['pdf','svg','png']: fig.savefig(OUT/f'sources/legacy_full10_comparison.{ext}',dpi=400)
plt.close(fig)
bc=freq[freq.dataset=='breast_cancer'].pivot(index='feature',columns='method',values='frequency')[METHODS]
bc=bc.loc[freq[(freq.dataset=='breast_cancer') & (freq.method=='Budget-stable_lcb')].sort_values(['frequency','feature'],ascending=[False,True]).feature]
fig,ax=plt.subplots(figsize=(7.1,6.5)); im=ax.imshow(bc.values,cmap='Blues',vmin=0,vmax=1,aspect='auto')
ax.set_xticks(range(5),LABELS,rotation=20,ha='right'); ax.set_yticks(range(len(bc)),bc.index,fontsize=8)
fig.colorbar(im,ax=ax,label='Selection frequency over six masks')
fig.tight_layout()
for ext in ['pdf','svg','png']: fig.savefig(OUT/f'figures/breast_cancer_frequencies.{ext}',dpi=400)
plt.close(fig)
bcmean=mean[mean.dataset=='breast_cancer'].set_index('method').reindex(METHODS)
bcmean.to_csv(OUT/'analysis/breast_cancer_case.csv')
template_path=Path(r'C:\Users\a.ghafarian\Downloads\قالب_مقاله.docx')
if not template_path.exists():template_path=OUT/'sources/congress_template.docx'
z=zipfile.ZipFile(template_path)
from xml.etree import ElementTree as ET
text=' '.join(ET.fromstring(z.read('word/document.xml')).itertext())
(OUT/'sources/template_text.txt').write_text(text,encoding='utf-8')
for name in z.namelist():
    if name.startswith('word/media/'):
        (OUT/'sources'/Path(name).name).write_bytes(z.read(name))
print(json.dumps(audit,ensure_ascii=False,default=int))
print(fr.to_string(index=False))
print(bcmean[['balanced_accuracy','cost_ratio','selected_features','nogueira_stability']].to_string())
print('Top breast-cancer frequencies:',freq[(freq.dataset=='breast_cancer') & (freq.method=='Budget-stable_lcb')].sort_values('frequency',ascending=False).head(6)[['feature','selected_count']].to_dict('records'))
steel=pd.read_csv(ROOT/'data/benchmark_v2/steel_plates_fault.csv')
leak_pred=(steel[[f'V{i}' for i in range(28,34)]].sum(axis=1)==0).astype(int)
leak=dict(columns=[f'V{i}' for i in range(28,34)],target_recovered_fraction=float((leak_pred==steel.target).mean()),sum_indicators_with_target_unique=sorted((steel[[f'V{i}' for i in range(28,34)]].sum(axis=1)+steel.target).unique().tolist()),source='https://archive.ics.uci.edu/dataset/198/steel+plates+faults',decision='Exclude existing Steel results from primary reanalysis; regenerate 27-feature 7-class experiment before reuse')
(OUT/'analysis/steel_target_leakage.json').write_text(json.dumps(leak,indent=2),encoding='utf-8')
valid=mean[~mean.dataset.isin(['steel_plates_fault','parkinsons'])]
valid.to_csv(OUT/'analysis/eligible_dataset_means.csv',index=False)
valid.groupby('method')[metrics].mean().reindex(METHODS).to_csv(OUT/'analysis/eligible_overall.csv')
fr8,rank8,pair8=[],[],[]
rng=np.random.default_rng(20261012)
for metric in metrics:
    p=valid.pivot(index='dataset',columns='method',values=metric)[METHODS]
    higher=metric in ['balanced_accuracy','nogueira_stability','jaccard_stability']
    ranks=np.array([rankdata(-r if higher else r) for r in p.values])
    fr=friedmanchisquare(*p.values.T)
    fr8.append(dict(metric=metric,n_datasets=8,n_methods=5,df=4,statistic=fr.statistic,p_raw=fr.pvalue,analysis='Exploratory source-audited subset; excludes Steel label leakage and Parkinson subject overlap risk'))
    for j,m in enumerate(METHODS): rank8.append(dict(metric=metric,method=m,average_rank=ranks[:,j].mean()))
    for m in METHODS[:-1]:
        delta=(p['Budget-stable_lcb']-p[m]).to_numpy(); nz=delta[delta!=0]; ranks_abs=rankdata(abs(nz))
        w=wilcoxon(delta,alternative='two-sided',method='auto')
        boots=delta[rng.integers(0,8,(20000,8))].mean(axis=1)
        pair8.append(dict(metric=metric,reference=m,mean_delta=delta.mean(),wilcoxon_W=w.statistic,p_raw=w.pvalue,rank_biserial=float((ranks_abs[nz>0].sum()-ranks_abs[nz<0].sum())/ranks_abs.sum()) if len(nz) else 0.,ci95_low=np.quantile(boots,.025),ci95_high=np.quantile(boots,.975),wins=int((delta>0).sum()),losses=int((delta<0).sum())))
f8=pd.DataFrame(fr8);f8['p_holm_six_metrics']=holm(f8.p_raw); f8.to_csv(OUT/'analysis/eligible_friedman.csv',index=False)
pd.DataFrame(rank8).to_csv(OUT/'analysis/eligible_ranks.csv',index=False)
p8=pd.DataFrame(pair8);p8['p_holm_within_metric']=p8.groupby('metric').p_raw.transform(lambda x:holm(x.to_numpy()));p8['p_holm_all_24']=holm(p8.p_raw);p8.to_csv(OUT/'analysis/eligible_paired.csv',index=False)
print('SOURCE AUDIT:',json.dumps(leak))
print('ELIGIBLE:', valid.groupby('method')[metrics].mean().reindex(METHODS).to_string())
print(f8.to_string(index=False))
print(p8[p8.reference=='EHOA'].to_string(index=False))
