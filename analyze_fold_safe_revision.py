from pathlib import Path
import json,csv,hashlib
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare,wilcoxon,rankdata
from sklearn.metrics import balanced_accuracy_score,accuracy_score,recall_score
from proposed.stability import compute_nogueira_stability,compute_jaccard_stability

R=Path(__file__).resolve().parent
P=R/'fold_safe_revision_2026_10_12'
A=P/'analysis'
A.mkdir(exist_ok=True)
raw=pd.read_csv(P/'runs.csv')
protocol=json.loads((P/'protocol.json').read_text())
if len(raw)!=protocol['planned_jobs']:raise ValueError('Execution incomplete; final analysis withheld')
M=['EHOA','random','cheapest','mi','stable_lcb']
audits=[]
for row in raw.to_dict('records'):
    path=P/'jobs'/row['job']
    mask=np.load(path/'mask.npy')
    costs=np.random.default_rng(1000+row['D']).lognormal(0,.7,row['D'])
    split=np.load(path/'split_provenance.npz')
    inner=[]
    for k in [1,2,3]:
        tr=split[f'inner_{k}_train']
        va=split[f'inner_{k}_validation']
        inner.append(len(np.intersect1d(tr,va))+len(np.intersect1d(tr,split['outer_test']))+len(np.intersect1d(va,split['outer_test'])))
    candidate=pd.read_csv(path/'candidate_audit.csv')
    predictions=pd.read_csv(path/'predictions.csv')
    audits.append(dict(job=row['job'],mask_count_matches=int(mask.sum())==row['selected_features'],mask_is_binary=bool(np.isin(mask,[0,1]).all()),cost_error=abs(float(costs[mask.astype(bool)].sum())-row['selected_cost']),outer_row_overlap=len(np.intersect1d(split['outer_train'],split['outer_test'])),inner_or_outer_test_row_overlap=max(inner),outer_subject_overlap=row['outer_subject_overlap'],inner_subject_overlap=row['inner_subject_overlap'],smote_dimension_mismatches=int((candidate.selected_features!=candidate.smote_input_features).sum())+int(row['outer_smote_input_features']!=row['selected_features']),inner_budget_violations=0 if row['method']=='EHOA' else int((candidate.selected_cost>row['budget_ratio']*costs.sum()+1e-10).sum()),outer_budget_violation=row['method']!='EHOA' and row['cost_ratio']>row['budget_ratio']+1e-12,ba_error=abs(balanced_accuracy_score(predictions.true,predictions.predicted)-row['balanced_accuracy']),accuracy_error=abs(accuracy_score(predictions.true,predictions.predicted)-row['accuracy'])))
audit=pd.DataFrame(audits)
audit.to_csv(A/'run_audit.csv',index=False)
groupcols=['dataset','method','budget_ratio','evidence_resamples','lambda_penalty','cohort']
for _,g in raw.groupby(groupcols):
    masks=np.vstack([np.load(P/'jobs'/job/'mask.npy') for job in g.job])
    raw.loc[g.index,'nogueira_stability']=compute_nogueira_stability(masks)
    raw.loc[g.index,'jaccard_stability']=compute_jaccard_stability(masks)
raw.to_csv(A/'all_runs_with_stability.csv',index=False)
metrics=['balanced_accuracy','cost_ratio','selected_features','nogueira_stability','jaccard_stability','fit_total_seconds']
means=raw.groupby(groupcols)[metrics].mean().reset_index()
means.to_csv(A/'all_dataset_means.csv',index=False)
primary=means[means.cohort=='primary']
primary.to_csv(A/'primary_dataset_means.csv',index=False)
source_metadata=pd.read_csv(R/'revision_2026_10_12/analysis/datasets.csv').set_index('dataset')
dataset_specs=[]
from run_fold_safe_revision import load
for ds in protocol['primary_datasets']:
    X,y,groups=load(ds)
    labels,counts=np.unique(y,return_counts=True)
    source=R/'revision_2026_10_12/corrected_experiments/steel_27_features_7_classes.csv' if ds=='steel_plates_fault' else R/'data'/('' if ds in ['breast_cancer','wine'] else 'benchmark_v2')/(ds+'.csv')
    dataset_specs.append(dict(dataset=ds,N=len(X),D=X.shape[1],classes=len(labels),class_counts=json.dumps({int(label):int(count) for label,count in zip(labels,counts)}),subject_groups='' if groups is None else len(np.unique(groups)),original_source=source_metadata.loc[ds,'original_source'],snapshot_source=source_metadata.loc[ds,'snapshot_source'],input_file_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
pd.DataFrame(dataset_specs).to_csv(A/'fresh_dataset_specifications.csv',index=False)
primary.groupby('method')[metrics].mean().reindex(M).to_csv(A/'primary_overall.csv')
means[means.cohort!='primary'].to_csv(A/'sensitivity_dataset_means.csv',index=False)

def holm(values):
    order=np.argsort(values)
    out=np.empty(len(values))
    previous=0
    for k,i in enumerate(order):
        previous=max(previous,(len(values)-k)*values[i])
        out[i]=min(1,previous)
    return out

franks=[]
frows=[]
pairs=[]
rng=np.random.default_rng(20261012)
for metric in metrics:
    values=primary.pivot(index='dataset',columns='method',values=metric)[M]
    stat=friedmanchisquare(*values.to_numpy().T)
    frows.append(dict(metric=metric,n_datasets=len(values),df=4,statistic=stat.statistic,p_raw=stat.pvalue))
    ranks=np.array([rankdata(r if metric in ['cost_ratio','selected_features','fit_total_seconds'] else -r) for r in values.to_numpy()])
    for j,m in enumerate(M):franks.append(dict(metric=metric,method=m,average_rank=ranks[:,j].mean()))
    for m in M[:-1]:
        delta=(values.stable_lcb-values[m]).to_numpy()
        w=wilcoxon(delta,alternative='two-sided',method='auto')
        nz=delta[delta!=0]
        r=rankdata(abs(nz))
        boot=delta[rng.integers(0,len(delta),(20000,len(delta)))].mean(1)
        pairs.append(dict(metric=metric,reference=m,mean_delta=delta.mean(),W=w.statistic,p_raw=w.pvalue,rank_biserial=0 if not len(r) else (r[nz>0].sum()-r[nz<0].sum())/r.sum(),ci95_low=np.quantile(boot,.025),ci95_high=np.quantile(boot,.975)))
f=pd.DataFrame(frows)
f['p_holm_six_metrics']=holm(f.p_raw.to_numpy())
f.to_csv(A/'primary_friedman.csv',index=False)
pd.DataFrame(franks).to_csv(A/'primary_ranks.csv',index=False)
pair=pd.DataFrame(pairs)
pair['p_holm_within_metric']=pair.groupby('metric').p_raw.transform(lambda x:holm(x.to_numpy()))
pair['p_holm_all_24']=holm(pair.p_raw.to_numpy())
pair.to_csv(A/'primary_paired.csv',index=False)
bc=primary[primary.dataset=='breast_cancer']
bc.to_csv(A/'breast_cancer_case.csv',index=False)
clinical=[]
for m in M:
    g=raw[(raw.dataset=='breast_cancer')&(raw.method==m)&(raw.cohort=='primary')]
    malignant=[]
    benign=[]
    for job in g.job:
        prediction=pd.read_csv(P/'jobs'/job/'predictions.csv')
        malignant.append(recall_score(prediction.true,prediction.predicted,pos_label=0))
        benign.append(recall_score(prediction.true,prediction.predicted,pos_label=1))
    clinical.append(dict(method=m,malignant_sensitivity=np.mean(malignant),benign_specificity=np.mean(benign),malignant_label=0,benign_label=1,folds=len(g)))
pd.DataFrame(clinical).to_csv(A/'breast_class_specific_metrics.csv',index=False)
columns=pd.read_csv(R/'data/breast_cancer.csv',nrows=1).drop(columns='target').columns
freq=[]
for m in M:
    g=raw[(raw.dataset=='breast_cancer')&(raw.method==m)&(raw.cohort=='primary')]
    masks=np.vstack([np.load(P/'jobs'/j/'mask.npy') for j in g.job])
    freq.extend(dict(method=m,feature=name,selected_count=int(masks[:,i].sum()),n_masks=len(masks)) for i,name in enumerate(columns))
pd.DataFrame(freq).to_csv(A/'breast_selection_frequencies.csv',index=False)
failure=P/'failure_log.jsonl'
summary=dict(planned_runs=protocol['planned_jobs'],completed_runs=len(raw),primary_runs=int((raw.cohort=='primary').sum()),sensitivity_runs=int((raw.cohort!='primary').sum()),duplicate_jobs=int(raw.job.duplicated().sum()),failed_attempts=0 if not failure.exists() else len(failure.read_text().splitlines()),all_masks_binary=bool(audit.mask_is_binary.all()),all_mask_counts_match=bool(audit.mask_count_matches.all()),maximum_cost_error=float(audit.cost_error.max()),inner_utility_training_overlap_with_inner_validation_or_outer_test=int(audit.inner_or_outer_test_row_overlap.max()),outer_row_overlap=int(audit.outer_row_overlap.max()),outer_subject_overlap=int(audit.outer_subject_overlap.max()),inner_subject_overlap=int(audit.inner_subject_overlap.max()),smote_dimension_mismatches=int(audit.smote_dimension_mismatches.sum()),inner_candidate_budget_violations=int(audit.inner_budget_violations.sum()),outer_constrained_budget_violations=int(audit.outer_budget_violation.sum()),maximum_ba_recalculation_error=float(audit.ba_error.max()),maximum_accuracy_recalculation_error=float(audit.accuracy_error.max()),analysis='Fresh redesigned protocol; locally frozen, exploratory, not independent public preregistration',stability='Nine overlapping final masks per dataset/configuration, not nine independent samples',sensitivity='Descriptive OFAT on three biomedical datasets; not exhaustive interactions or clinical validation')
(A/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
def table(frame):
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))+'\n'
report='# اجرای تازه با پایپ‌لاین اصلاح‌شده\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n\n'
report+='## تغییر واقعی روش\n\nبرای هر ماسک کاندید، تعمیر و محاسبه سودمندی در هر تقسیم درونی به‌صورت مستقل و فقط با داده آموزش آن تقسیم انجام می‌شود. برازندگی، میانگین دقت معمولی و میانگین اندازه ماسک‌های تعمیرشده در سه تقسیم است. ماسک نهایی از کاندید برنده با سودمندی آموزش بیرونی ساخته می‌شود. ماسک درونی و نهایی می‌توانند متفاوت باشند؛ این طراحی تازه است و نتایج آن جایگزین محاسبات قبلی به‌صورت بی‌اعلان نمی‌شوند. پیش‌پردازش و SMOTE در همه ارزیابی‌ها روی ابعاد منتخب اجرا شده‌اند. امتیاز درونی همچنان امتیاز انتخاب بهینه‌شده است؛ تخمین عملکرد از آزمون بیرونی می‌آید.\n\nDermatology مطابق [تعریف ناشر](https://archive.ics.uci.edu/dataset/33/dermatology)، 33 ویژگی درجه‌ای/گسسته و سن پیوسته دارد؛ MI نوع‌آگاه استفاده شد. Steel با 27 پیش‌بین و 7 کلاس اجرا شد. Parkinsons در بیرونی و درونی به‌صورت گروهی تقسیم شد؛ اختلاف 31 فرد اعلام‌شده و 32 پیشوند فایل همچنان نیازمند تأیید مستقل است.\n\n'
spec=pd.DataFrame(dataset_specs)[['dataset','N','D','classes','class_counts','subject_groups','original_source','snapshot_source']]
spec['original_source']=spec.original_source.map(lambda url:f'[منبع اصلی]({url})')
spec['snapshot_source']=spec.snapshot_source.map(lambda url:f'[منبع snapshot]({url})')
report+='## مشخصات واقعی اجرای تازه و لینک مستقیم داده\n\n'+table(spec)+'\nSteel از snapshot اصلاح‌شده بازسازی شد و Parkinson با فایل اصلی UCI تطبیق یافت. هش فایل استفاده‌شده در fresh_dataset_specifications.csv است. این جدول با مشخصات آرشیو قدیمی که Steel در آن 33 ورودی دارد، متفاوت است.\n\n'
report+='## نتیجه اصلی ده دیتاست\n\n'+table(pd.read_csv(A/'primary_overall.csv').round(6))+'\n'+table(f.round(8))+'\n'+table(pair[pair.reference=='EHOA'].round(8))
report+='\nاصلاح هولم هم درون هر معیار و هم روی همه 24 مقایسه گزارش شد. فاصله‌های bootstrap دیتاستی، توصیفی و بدون اصلاح چندگانگی‌اند. نتیجه آزمون با اثر توصیفی یکسان نیست؛ عدم معناداری، هم‌ارزی را ثابت نمی‌کند. زمان کامل ثبت شده، ولی اجرای هم‌زمان سه پردازش و یک رایانه، مبنای ادعای سرعت عمومی نیست.\n\n'
report+='## شاخص پزشکی سرطان پستان\n\nدر کدگذاری sklearn این فایل، 0 بدخیم و 1 خوش‌خیم است. sensitivity عمومی CSV، بازخوانی کلاس 1 است و نباید حساسیت سرطان خوانده شود. شاخص حساسیت بدخیم و ویژگی خوش‌خیم از پیش‌بینی ذخیره‌شده، جداگانه و با برچسب صریح محاسبه شدند؛ میانگین نه تقسیم هم‌پوشان، اعتبار بالینی بیرونی نیست.\n\n'+table(pd.DataFrame(clinical).round(6))+'\n'
report+='## حساسیت\n\nبودجه‌های 0.15، 0.30 و 0.50 برای چهار تعمیر؛ R برابر 4، 8 و 16 و lambda برابر 0، 1 و 2 برای روش بازنمونه‌گیری‌شده روی سرطان پستان، Dermatology و Parkinsons بررسی شدند. تنظیم‌ها پیش از این اجراها تثبیت شدند؛ از آزمون بیرونی برای انتخاب تنظیم برنده استفاده نکردیم. این تحلیل یک‌عامل‌درهرمرحله است و همه تعامل‌ها را پوشش نمی‌دهد.\n\n'+table(means[means.cohort!='primary'].round(6))
report+='\n## باقی‌مانده\n\nهزینه واقعی/گروهی پزشکی، داده بالینی بیرونی، تأیید مستقل هویت افراد، انتشار عمومی و تأیید اظهارنامه نویسنده همچنان موجود نیستند. ثبت محلی پیش از اجرای جدید، ثبت پیشینی مستقل عمومی محسوب نمی‌شود و لاگ تاریخی مفقود را بازسازی نمی‌کند. محدودیت سه بذر، جست‌وجوی کوتاه و وابستگی حاشیه‌ای MI باقی است.\n'
(P/'scientific_report_fa.md').write_text(report,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
print(f.to_string(index=False))
print(pair[pair.reference=='EHOA'].to_string(index=False))
