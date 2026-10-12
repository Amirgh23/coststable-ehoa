from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon, rankdata
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
IN=ROOT/'results/cost_stable_confirmatory/raw/runs.csv'
OUT=ROOT/'results/cost_stable_confirmatory/final_analysis'
METHODS=['EHOA','Budget-random','Budget-cheapest','Budget-mi','Budget-stable_lcb']
METRICS=['balanced_accuracy','f1_score','mcc','roc_auc','pr_auc','selected_features','cost_ratio','nogueira_stability','runtime_seconds']

def holm(ps):
    order=np.argsort(ps); out=np.empty(len(ps)); running=0
    for rank,i in enumerate(order):
        running=max(running,(len(ps)-rank)*ps[i]); out[i]=min(1,running)
    return out

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(IN)
    keys=['dataset','method','seed','fold']
    validation={
      'rows':len(d),'expected_rows':300,'duplicate_keys':int(d.duplicated(keys).sum()),
      'missing_values':int(d.isna().sum().sum()),'datasets':int(d.dataset.nunique()),
      'methods':int(d.method.nunique()),'budget_violations':int(((d.method!='EHOA') & (d.cost_ratio>d.budget_ratio+1e-12)).sum()),
      'status_values':sorted(d.status.unique().tolist()),'mask_files':len(list((IN.parents[1]/'masks').glob('*.npy')))
    }
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    summary=d.groupby(['dataset','method'])[METRICS].agg(['mean','std']).reset_index()
    summary.columns=['_'.join(x).rstrip('_') for x in summary.columns]
    summary.to_csv(OUT/'per_dataset_summary.csv',index=False)
    dsmean=d.groupby(['dataset','method'])[METRICS].mean().reset_index()
    overall=dsmean.groupby('method')[METRICS].agg(['mean','std']).reindex(METHODS)
    overall.columns=['_'.join(x) for x in overall.columns]
    overall.reset_index().to_csv(OUT/'overall_summary.csv',index=False)
    # Across-dataset tests use one independent aggregate per dataset and method.
    stats=[]
    for metric in METRICS:
      p=dsmean.pivot(index='dataset',columns='method',values=metric)[METHODS]
      higher=metric not in ['selected_features','cost_ratio','runtime_seconds']
      vals=[p[m].values for m in METHODS]
      fr=friedmanchisquare(*vals)
      ranks=np.vstack([rankdata(-row if higher else row) for row in p.values])
      for j,m in enumerate(METHODS):
        stats.append({'metric':metric,'comparison':'average_rank','method':m,'estimate':ranks[:,j].mean(),'p_raw':fr.pvalue,'statistic':fr.statistic})
      base=p['Budget-stable_lcb'].values; tmp=[]
      for m in METHODS[:-1]:
        x=base-p[m].values
        try: w=wilcoxon(x,alternative='two-sided',method='auto')
        except ValueError: w=type('W',(),{'statistic':0,'pvalue':1})()
        wins=int((x>1e-12).sum()); ties=int((abs(x)<=1e-12).sum()); losses=int((x<-1e-12).sum())
        tmp.append({'metric':metric,'comparison':f'Budget-stable_lcb vs {m}','method':'Budget-stable_lcb','estimate':x.mean(),'median_delta':np.median(x),'wins':wins,'ties':ties,'losses':losses,'p_raw':w.pvalue,'statistic':w.statistic})
      adj=holm([r['p_raw'] for r in tmp])
      for r,a in zip(tmp,adj): r['p_holm_within_metric']=a; stats.append(r)
    pd.DataFrame(stats).to_csv(OUT/'statistical_tests.csv',index=False)
    # Practical BA deltas and a deterministic dataset bootstrap CI.
    p=dsmean.pivot(index='dataset',columns='method',values='balanced_accuracy')
    rng=np.random.default_rng(20260821); rows=[]
    for m in METHODS[:-1]:
      delta=(p['Budget-stable_lcb']-p[m]).values
      boots=np.array([rng.choice(delta,len(delta),replace=True).mean() for _ in range(20000)])
      rows.append({'comparison':f'Budget-stable_lcb vs {m}','mean_delta':delta.mean(),'median_delta':np.median(delta),'ci95_low':np.quantile(boots,.025),'ci95_high':np.quantile(boots,.975),'wins':int((delta>.005).sum()),'practical_ties':int((abs(delta)<=.005).sum()),'losses':int((delta<-.005).sum())})
    pd.DataFrame(rows).to_csv(OUT/'ba_effects.csv',index=False)
    # Figures derived directly from the final CSV.
    fig,ax=plt.subplots(figsize=(10,5));
    x=np.arange(len(p)); width=.16
    for i,m in enumerate(METHODS): ax.bar(x+(i-2)*width,p[m],width,label=m)
    ax.set_xticks(x,p.index,rotation=35,ha='right'); ax.set_ylabel('Balanced accuracy'); ax.set_ylim(0,1.05); ax.legend(ncol=3,fontsize=8); fig.tight_layout(); fig.savefig(OUT/'balanced_accuracy_by_dataset.png',dpi=220); plt.close(fig)
    q=dsmean.pivot(index='dataset',columns='method',values='cost_ratio')
    fig,ax=plt.subplots(figsize=(8,5));
    for m in METHODS: ax.scatter(q[m],p[m],label=m,s=38,alpha=.85)
    ax.set_xlabel('Selected cost / total cost (lower is better)'); ax.set_ylabel('Balanced accuracy (higher is better)'); ax.legend(fontsize=8); ax.grid(alpha=.25); fig.tight_layout(); fig.savefig(OUT/'accuracy_cost_tradeoff.png',dpi=220); plt.close(fig)
    print(json.dumps(validation)); print(overall[['balanced_accuracy_mean','cost_ratio_mean','nogueira_stability_mean']])

if __name__=='__main__': main()
