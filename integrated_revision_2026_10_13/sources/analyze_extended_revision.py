from pathlib import Path
import json,itertools
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare,wilcoxon,rankdata
from sklearn.metrics import balanced_accuracy_score,accuracy_score,recall_score
from proposed.stability import compute_nogueira_stability,compute_jaccard_stability

ROOT=Path(__file__).resolve().parent
P=ROOT/'extended_revision_2026_10_12'
OLD=ROOT/'fold_safe_revision_2026_10_12'
A=P/'analysis'
A.mkdir(exist_ok=True)
protocol=json.loads((P/'protocol.json').read_text())
new=pd.read_csv(P/'runs.csv')
if len(new)!=protocol['planned_runs']:raise ValueError('Extension incomplete; final analysis withheld')
old=pd.read_csv(OLD/'runs.csv')
old['source_directory']='fold_safe_revision_2026_10_12/jobs/'+old.job
new['source_directory']='extended_revision_2026_10_12/'+new.campaign+'/jobs/'+new.job
primary=pd.concat([old[old.cohort=='primary'],new[new.campaign=='extra_seeds']],ignore_index=True)
primary['cohort']='primary_five_seeds'
M=['EHOA','random','cheapest','mi','stable_lcb']
metrics=['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','jaccard_stability','fit_total_seconds']
for m,g in primary.groupby(['dataset','method']):
    masks=np.vstack([np.load(ROOT/path/'mask.npy') for path in g.source_directory])
    primary.loc[g.index,'nogueira_stability']=compute_nogueira_stability(masks)
    primary.loc[g.index,'jaccard_stability']=compute_jaccard_stability(masks)
primary.to_csv(A/'primary_five_seed_runs.csv',index=False)
means=primary.groupby(['dataset','method'])[metrics+['fitness','evaluations']].mean().reset_index()
means.to_csv(A/'primary_dataset_means.csv',index=False)
means.groupby('method')[metrics].mean().reindex(M).to_csv(A/'primary_overall.csv')

def holm(values):
    order=np.argsort(values)
    adjusted=np.empty(len(values))
    previous=0
    for k,i in enumerate(order):
        previous=max(previous,(len(values)-k)*values[i])
        adjusted[i]=min(1,previous)
    return adjusted

fr=[]
ranks=[]
pairs=[]
rng=np.random.default_rng(20261012)
for metric in metrics:
    pivot=means.pivot(index='dataset',columns='method',values=metric)[M]
    test=friedmanchisquare(*pivot.to_numpy().T)
    fr.append(dict(metric=metric,n_datasets=10,df=4,statistic=test.statistic,p_raw=test.pvalue))
    matrix=np.array([rankdata(row if metric in ['cost_ratio','selected_features','fit_total_seconds'] else -row) for row in pivot.to_numpy()])
    for j,m in enumerate(M):ranks.append(dict(metric=metric,method=m,average_rank=matrix[:,j].mean()))
    for m in M[:-1]:
        delta=(pivot.stable_lcb-pivot[m]).to_numpy()
        test=wilcoxon(delta,alternative='two-sided',method='auto')
        nz=delta[delta!=0]
        rr=rankdata(abs(nz))
        boot=delta[rng.integers(0,10,(20000,10))].mean(1)
        pairs.append(dict(metric=metric,reference=m,mean_delta=delta.mean(),W=test.statistic,p_raw=test.pvalue,rank_biserial=0 if not len(rr) else (rr[nz>0].sum()-rr[nz<0].sum())/rr.sum(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975)))
f=pd.DataFrame(fr)
f['p_holm_six_metrics']=holm(f.p_raw.to_numpy())
f.to_csv(A/'primary_friedman.csv',index=False)
pd.DataFrame(ranks).to_csv(A/'primary_ranks.csv',index=False)
pair=pd.DataFrame(pairs)
pair['p_holm_within_metric']=pair.groupby('metric').p_raw.transform(lambda x:holm(x.to_numpy()))
pair['p_holm_all_24']=holm(pair.p_raw.to_numpy())
pair.to_csv(A/'primary_paired.csv',index=False)
factorial=new[new.campaign=='factorial'].copy()
keys=['dataset','budget_ratio','evidence_resamples','lambda_penalty']
for _,g in factorial.groupby(keys):
    masks=np.vstack([np.load(ROOT/path/'mask.npy') for path in g.source_directory])
    factorial.loc[g.index,'nogueira_stability']=compute_nogueira_stability(masks)
cells=factorial.groupby(keys)[['balanced_accuracy','cost_ratio','selected_features','nogueira_stability']].mean().reset_index()
cells.to_csv(A/'factorial_cells.csv',index=False)
effects=[]
cols=['budget_ratio','evidence_resamples','lambda_penalty']
for ds,g in cells.groupby('dataset'):
    if len(g)!=8:raise ValueError('Incomplete factorial cells')
    coded=np.column_stack([np.where(g[col]==g[col].max(),1,-1) for col in cols])
    for order in [1,2,3]:
        for indices in itertools.combinations(range(3),order):
            sign=coded[:,indices].prod(1)
            for metric in ['balanced_accuracy','cost_ratio','selected_features','nogueira_stability']:
                effects.append(dict(dataset=ds,term=' x '.join(cols[i] for i in indices),order=order,metric=metric,effect=2*np.mean(sign*g[metric].to_numpy())))
effect=pd.DataFrame(effects)
effect.to_csv(A/'factorial_dataset_effects.csv',index=False)
es=[]
for (term,metric),g in effect.groupby(['term','metric']):
    values=g.effect.to_numpy()
    boot=values[rng.integers(0,10,(20000,10))].mean(1)
    es.append(dict(term=term,metric=metric,mean_effect=values.mean(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975),n_datasets=10,stochastic_seeds=1,interpretation='descriptive endpoint factorial contrast; not all continuous-space interactions'))
pd.DataFrame(es).to_csv(A/'factorial_effects.csv',index=False)
larger=new[new.campaign=='larger_search'].copy()
reference=old[(old.cohort=='primary')&(old.seed==72001)].copy()
search_rows=[]
for population,data in [(8,reference),(16,larger)]:
    for (ds,m),g in data.groupby(['dataset','method']):
        masks=np.vstack([np.load(ROOT/path/'mask.npy') for path in g.source_directory])
        row={metric:float(g[metric].mean()) for metric in ['balanced_accuracy','cost_ratio','selected_features','fitness','evaluations','fit_total_seconds']}
        search_rows.append(dict(dataset=ds,method=m,population=population,iterations=10 if population==8 else 20,nogueira_stability=compute_nogueira_stability(masks),**row))
search=pd.DataFrame(search_rows)
search.to_csv(A/'search_profile_dataset_means.csv',index=False)
sd=[]
for m,g in search.groupby('method'):
    lo=g[g.population==8].set_index('dataset')
    hi=g[g.population==16].set_index('dataset')
    for metric in ['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','fitness','evaluations','fit_total_seconds']:
        delta=(hi[metric]-lo[metric]).to_numpy()
        boot=delta[rng.integers(0,10,(20000,10))].mean(1)
        sd.append(dict(method=m,metric=metric,mean_delta=delta.mean(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975),n_datasets=10,seeds=1,interpretation='descriptive larger-minus-reference search; not convergence proof'))
pd.DataFrame(sd).to_csv(A/'search_profile_effects.csv',index=False)
audit_rows=[]
for row in new.to_dict('records'):
    path=ROOT/row['source_directory']
    mask=np.load(path/'mask.npy')
    costs=np.random.default_rng(1000+row['D']).lognormal(0,.7,row['D'])
    provenance=np.load(path/'split_provenance.npz')
    overlaps=[]
    for j in [1,2,3]:
        tr=provenance[f'inner_{j}_train']
        va=provenance[f'inner_{j}_validation']
        overlaps.append(len(np.intersect1d(tr,va))+len(np.intersect1d(tr,provenance['outer_test']))+len(np.intersect1d(va,provenance['outer_test'])))
    candidates=pd.read_csv(path/'candidate_audit.csv')
    pred=pd.read_csv(path/'predictions.csv')
    audit_rows.append(dict(campaign=row['campaign'],job=row['job'],mask_count_matches=int(mask.sum())==row['selected_features'],mask_binary=bool(np.isin(mask,[0,1]).all()),cost_error=abs(costs[mask.astype(bool)].sum()-row['selected_cost']),inner_train_validation_test_overlap=max(overlaps),outer_overlap=len(np.intersect1d(provenance['outer_train'],provenance['outer_test'])),inner_subject_overlap=row['inner_subject_overlap'],outer_subject_overlap=row['outer_subject_overlap'],smote_dimension_mismatches=int((candidates.selected_features!=candidates.smote_input_features).sum()),candidate_budget_violations=0 if row['method']=='EHOA' else int((candidates.selected_cost>row['budget_ratio']*costs.sum()+1e-10).sum()),final_budget_violation=row['method']!='EHOA' and row['cost_ratio']>row['budget_ratio']+1e-12,ba_error=abs(balanced_accuracy_score(pred.true,pred.predicted)-row['balanced_accuracy']),accuracy_error=abs(accuracy_score(pred.true,pred.predicted)-row['accuracy'])))
audit=pd.DataFrame(audit_rows)
audit.to_csv(A/'extended_run_audit.csv',index=False)
failure=P/'failure_log.jsonl'
summary=dict(planned_extension_runs=690,completed_extension_runs=len(new),total_fold_safe_runs=len(old)+len(new),primary_five_seed_runs=len(primary),primary_masks_per_dataset_method=15,factorial_runs=len(factorial),larger_search_runs=len(larger),duplicate_jobs=int(new.duplicated(['campaign','job']).sum()),failed_attempts=0 if not failure.exists() else len(failure.read_text().splitlines()),all_masks_binary=bool(audit.mask_binary.all()),all_mask_counts_match=bool(audit.mask_count_matches.all()),maximum_cost_error=float(audit.cost_error.max()),inner_train_validation_outer_test_overlap=int(audit.inner_train_validation_test_overlap.max()),outer_row_overlap=int(audit.outer_overlap.max()),inner_subject_overlap=int(audit.inner_subject_overlap.max()),outer_subject_overlap=int(audit.outer_subject_overlap.max()),smote_dimension_mismatches=int(audit.smote_dimension_mismatches.sum()),candidate_budget_violations=int(audit.candidate_budget_violations.sum()),final_constrained_budget_violations=int(audit.final_budget_violation.sum()),maximum_ba_error=float(audit.ba_error.max()),maximum_accuracy_error=float(audit.accuracy_error.max()),publication=json.loads((P/'publication.json').read_text()),scope='Prior 774 fold-safe runs plus 690 prospective extension runs; original leaked archival results excluded')
(A/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
case=means[means.dataset=='breast_cancer']
case.to_csv(A/'breast_cancer_case.csv',index=False)
clinical=[]
frequencies=[]
names=pd.read_csv(ROOT/'data/breast_cancer.csv',nrows=1).drop(columns='target').columns
for m in M:
    g=primary[(primary.dataset=='breast_cancer')&(primary.method==m)]
    mal=[]
    ben=[]
    masks=[]
    for path in g.source_directory:
        pred=pd.read_csv(ROOT/path/'predictions.csv')
        mal.append(recall_score(pred.true,pred.predicted,pos_label=0))
        ben.append(recall_score(pred.true,pred.predicted,pos_label=1))
        masks.append(np.load(ROOT/path/'mask.npy'))
    clinical.append(dict(method=m,malignant_sensitivity=np.mean(mal),benign_specificity=np.mean(ben),malignant_label=0,benign_label=1,folds=15))
    masks=np.vstack(masks)
    frequencies.extend(dict(method=m,feature=name,selected_count=int(masks[:,j].sum()),n_masks=15) for j,name in enumerate(names))
pd.DataFrame(clinical).to_csv(A/'breast_class_specific_metrics.csv',index=False)
pd.DataFrame(frequencies).to_csv(A/'breast_selection_frequencies.csv',index=False)
sources=pd.read_csv(OLD/'analysis/fresh_dataset_specifications.csv')
sources.loc[sources.dataset=='hill_valley','original_source']='https://archive.ics.uci.edu/dataset/166/hill+valley'
sources.to_csv(A/'fresh_dataset_specifications.csv',index=False)
def table(frame):
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))+'\n'
report='# گزارش تکمیل تحلیل تعامل و جست‌وجو\n\n690 اجرای تکمیلی واقعاً انجام شد: 300 اجرای دو بذر اضافه، 240 اجرای طرح کامل 2×2×2 و 150 اجرای جست‌وجوی 16×20. با 774 اجرای قبلی پایپ‌لاین مستقل، 1464 اجرا موجود است. تحلیل اصلی پنج‌بذری 750 اجرا دارد؛ سه دسته را به‌عنوان یک پروتکل عددی یکسان مخلوط نکردیم.\n\n'
report+='## ممیزی\n\n```json\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n```\n\n'
report+='## تحلیل اصلی پنج بذر\n\n'+table(pd.read_csv(A/'primary_overall.csv').round(6))+'\n'+table(f.round(8))+'\n'+table(pair[pair.reference=='EHOA'].round(8))
report+='\n## تعامل پارامترها\n\nطرح کامل 2×2×2 شامل بودجه 0.15/0.50، R=4/8 و lambda=0/2 روی ده دیتاست است. اثرهای اصلی، تعامل‌های دوتایی و تعامل سه‌تایی به‌صورت کنتراست متعامد محاسبه شدند. واحد بازنمونه‌گیری، دیتاست است. تنها یک بذر تصادفی و سه تقسیم بیرونی برای هر خانه داریم؛ اثرها توصیفی‌اند و همه سطوح پیوسته یا عدم‌قطعیت بذر را پوشش نمی‌دهند. پایداری خانه‌ها از سه ماسک محاسبه شد و فقط با خانه‌های هم‌پروتکل مقایسه می‌شود.\n\n'+table(pd.DataFrame(es).round(6))
report+='\n## جست‌وجوی بزرگ‌تر\n\n16 کوه‌پیما و 20 تکرار با 8 کوه‌پیما و 10 تکرار روی همان بذر 72001 و تقسیم‌های مشترک، برای هر پنج روش و ده دیتاست مقایسه شدند. اثرهای زیر از ده اختلاف دیتاستی‌اند؛ تضمین بهینه سراسری یا همگرایی نیستند. هیچ تنظیم برنده‌ای با آزمون بیرونی انتخاب نشد.\n\n'+table(pd.DataFrame(sd).round(6))
report+='\n## منابع و باقی‌مانده\n\nشناسه UCI صحیح Hill-Valley برابر 166 است؛ 147 مربوط به Statlog Image Segmentation است. snapshot عددی OpenML 1479 تغییر نکرد و خطا فقط ارجاع منبع بود. هزینه‌ها همچنان lognormal مصنوعی‌اند؛ تعرفه واقعی و داده بالینی مستقل در پوشه معرفی‌شده پیدا نشدند. شناسه بالینی Parkinson از پیشوند ضبط قابل اثبات نیست. ثبت عمومی پروتکل تکمیلی پیش از اجرا، ثبت پیشینی آزمایش‌های گذشته یا ثبت رسمی مستقل محسوب نمی‌شود. MI منهای SD همچنان ابتکاری است؛ پوشش اطمینان، کنترل انتخاب کاذب و تضمین پذیرش ادعا نمی‌شود.\n'
(P/'scientific_report_fa.md').write_text(report,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
print(f.to_string(index=False))
