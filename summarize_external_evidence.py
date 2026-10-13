from pathlib import Path
import json,hashlib,shutil,zipfile,platform
import numpy as np
import pandas as pd
import sklearn,imblearn

r=Path(__file__).resolve().parent
p=r/'external_evidence_2026_10_13'
metrics=pd.read_csv(p/'external_subject_metrics.csv')
audit=json.loads((p/'external_audit.json').read_text())
cost=json.loads((p/'cost_model.json').read_text())
recomputed=[]
for _,row in metrics.iterrows():
    d=pd.read_csv(p/f'{row.method}_subject_predictions.csv')
    ba=(np.mean(d.predicted[d.true==0]==0)+np.mean(d.predicted[d.true==1]==1))/2
    recomputed.append(abs(ba-row.balanced_accuracy))
audit['max_subject_ba_recalculation_error']=max(recomputed)
audit['all_target_subjects_three_recordings']=audit['target_recordings_per_subject']==[3]
audit['all_constrained_masks_within_one_feature']=all(int(np.load(f).sum())<=1 for f in (p/'jobs').rglob('mask.npy') if not f.parent.name.startswith('EHOA_'))
(p/'external_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
(p/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'imblearn':imblearn.__version__},indent=2),encoding='utf-8')
text='''# گزارش تکمیلی شواهد عمومی — 2026-10-13

این گزارش مکمل نسخه extended_revision_2026_10_12 است؛ اعداد مقاله چهارصفحه‌ای قبلی را جایگزین نمی‌کند. آن مطالعه 1464 اجرا دارد؛ این مکمل 25 برازش انتقال با پروتکل متفاوت اضافه می‌کند. خواندن نتایج این مکمل همراه مقاله ضروری است.

## داده مستقل و انتقال

دیتاست UCI489 با 240 ضبط از 80 فرد، شامل 40 فرد دارای Parkinson و 40 کنترل، دریافت شد. هر فرد سه ضبط دارد. مجوز CC BY4 و DOI آن 10.24432/C5701F است. منبع: https://archive.ics.uci.edu/dataset/489/parkinson+dataset+with+replicated+acoustic+features

تنها RPDE، DFA و PPE با نام دقیق مشترک استفاده شدند. برابری نام، برابری استخراج یا کالیبراسیون را ثابت نمی‌کند؛ بقیه ویژگی‌ها بدون مدرک معادل‌سازی نشدند. این آزمون، انتقال اکتشافی در فضای سه‌ویژگی مشترک است و اعتبارسنجی کامل مدل اصلی22ویژگی یا مطالعه بالینی آینده‌نگر محسوب نمی‌شود.

پروتکل و کد پیش از اجرا در ثبت 7f716c50ad15fd574850ddf2b1d39250c6bd6060 منتشر شدند. تمام برازش، سودمندی، انتخاب، جایگذاری، استانداردسازی و SMOTE فقط روی Oxford195 انجام شد. انتخاب درونی با جداسازی پیشوند فرد انجام شد. مقصد فقط برای پیش‌بینی و ارزیابی استفاده شد؛ هیچ بازتنظیم یا انتخاب بهترین بذر براساس مقصد انجام نشد. پنج روش × پنج بذر =25 برازش. هزینه سه ستون برابر و مصنوعی است؛ این بخش هزینه واقعی ندارد.

برای هر روش، احتمال پنج مدل میانگین گرفته شد و سپس میانگین سه ضبط هر فرد با آستانه0.5 تصمیم را تعیین کرد. واحد bootstrap فرد بود؛ 10000 بازنمونه طبقه‌بندی‌شده، فاصله توصیفی و شرطی به مدل‌های برازش‌شده است. این فاصله عدم‌قطعیت کل فرایند آموزش را پوشش نمی‌دهد و آزمون چندگانگی یا اثبات برتری نیست.

'''
for _,row in metrics.iterrows():
    text+=f'- {row.method}: BA={row.balanced_accuracy:.3f}، فاصله توصیفی95% [{row.descriptive_ci_low:.3f}, {row.descriptive_ci_high:.3f}]، حساسیت Parkinson={row.sensitivity_pd:.3f}، ویژگی کنترل={row.specificity_control:.3f}، AUC={row.auc:.3f}.\n'
text+='''
نتیجه انتقال ضعیف است؛ فاصله BA شامل0.5 می‌شود و برتری روش پیشنهادی نشان داده نشد. پنج بذر یا25 برازش،25 فرد مستقل نیستند. انتخاب بهترین نتیجه یا تغییر روش پس از دیدن مقصد انجام نشد. ناهمگنی ثبت و استخراج ویژگی و فضای کوچک سه‌ستونی، تفسیر را محدود می‌کنند.

## هزینه واقعیِ خدمت و مدل گروهی

یک تعرفه رسمی عمومی، نه فاکتور بیمار، پیدا شد: Montana Cancer Control Programs، فایل MCCP2025FeeSchedule، صفحه3، تاریخ اثر مندرج2024-06-30. کد88173 برای تفسیر FNA: global164.34USD، technical98.21USD و professional66.13USD. global را با دو جزء آن جمع نکردیم. این جدول تعرفه ایران یا تأیید نرخ جاری2026 نیست.

منبع: https://dphhs.mt.gov/assets/publichealth/Cancer/MCCP2025FeeSchedule.pdf

UCI17 تصریح می‌کند ویژگی‌ها از تصویر دیجیتال FNA استخراج شده‌اند: https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic

به‌عنوان تحلیل سناریوی مشترک، همه30ستون WDBC به یک خدمت تعلق گرفتند و C(S)=164.34 برای هر زیرمجموعه غیرخالی تعریف شد. این نگاشت فرض تحلیلی است؛ صورت‌حساب واقعی یا تعرفه استخراج هر ستون تأیید نشده است. هزینه جمع‌آوری نمونه، تصویربرداری، مراجعات، زمان محاسبه و خطر مشخص نیست. بنابراین آن را جایگزین هزینه مصنوعی مقاله نکردیم.

'''
text+=f'روی {cost["primary_masks_audited"]} ماسک اصلی سرطان پستان، {cost["nonempty_masks"]} ماسک غیرخالی‌اند. در این سناریو همه100% هزینه خدمت را دارند و صرفه‌جویی خدمت صفر است؛ بودجه30% برای هر زیرمجموعه غیرخالی ناممکن می‌شود. در نتیجه کاهش ستون، کاهش تعرفه خدمت را اثبات نمی‌کند. breast_shared_service_cost_audit.csv شاهد محاسبات است.\n'
text+='''
## هویت Parkinson، تاریخچه و اظهارنامه

بازبینی فایل اصلی UCI174:195ضبط،32پیشوند،24پیشوند با برچسب Parkinson. متن رسمی UCI همچنان31فرد و23بیمار ذکر می‌کند؛ خلاصه صفحه حتی197نمونه نشان می‌دهد. اختلاف فایل و شرح ثبت شد، نه با حذف دلخواه فرد رفع شد. منبع: https://archive.ics.uci.edu/dataset/174/parkinsons

جداسازی پیشوندها و دریافت یک دیتاست دیگر، تأیید هویت بالینی افراد Oxford نیست. بدون تأیید مالک داده، این مورد باز می‌ماند. پیامی به مالک داده ارسال نشده است.

ثبت عمومی قبلی و فعلی، شواهد اجرای جدیدند و جایگزین ثبت پیشینی یا لاگ مفقود مطالعه قدیمی نیستند. داده عمومی نمی‌تواند تاریخچه خصوصی آزمایش‌های نویسنده را بازسازی کند. این ایراد با محدودسازی ادعا گزارش می‌شود، نه جعل ثبت یا لاگ.

نویسنده صریحاً گفته اظهارنامه را هنوز بررسی و تأیید نکرده است؛ پیش‌نویس تأییدنشده باقی می‌ماند. امضا یا تأیید نویسنده ایجاد نشده است.

## وضعیت پنج مورد

- هزینه: تعرفه واقعیِ منتشرشده برای خدمت و تحلیل گروهی تهیه شد؛ هزینه واقعی هر ویژگی، زمان و خطرِ محل اجرا همچنان نامعلوم است.
- داده بیرونی: داده عمومی جدا دریافت و انتقال محدود واقعاً اجرا شد؛ عملکرد ضعیف است و اعتبار بالینی کامل ادعا نمی‌شود.
- هویت: اختلاف با فایل اولیه بازتأیید شد؛ تأیید مالک داده موجود نیست.
- تاریخچه: ثبت‌های جاری موجودند؛ گذشته مفقود قابل ساختن نیست.
- اظهارنامه: آماده ولی تأییدنشده است.

برای ادامه روی سیستم دیگر، این مکمل و run_external_evidence.py را کنار ریشه مخزن قرار دهید. هیچ فایل از نسخه پیشین حذف نشده است. نتیجه تازه را در قسمت محدودیت/بحث نسخه بعدی و پاسخ داور وارد کنید؛ نسخه فعلی مقاله هنوز اعداد25اجرای مکمل را ندارد.
'''
(p/'REPORT_FA.md').write_text(text,encoding='utf-8')
(p/'DATA_LICENSE.md').write_text('UCI174 and UCI489 are CC BY 4.0 datasets. Attribution: Little, M. et al., Parkinsons, UCI, DOI10.24432/C59C74; Prez, C., Parkinson Dataset with replicated acoustic features, UCI, DOI10.24432/C5701F. Original CSV/ZIP files are preserved without numeric modification. Source links appear in REPORT_FA.md. The public Montana fee table is referenced; no local PDF download succeeded. The report records the directly verified official page and its effective date.\n',encoding='utf-8')
manifest=[{'path':f.relative_to(p).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in p.rglob('*') if f.is_file() and f.name!='SHA256_MANIFEST.json']
(p/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
d=r/'public_coststable_ehoa'
shutil.copytree(p,d/p.name,dirs_exist_ok=True)
shutil.copy2(Path(__file__),d/Path(__file__).name)
readme=d/'README.md'
s=readme.read_text(encoding='utf-8')
if 'external_evidence_2026_10_13/REPORT_FA.md' not in s:
    s+='\n## Public evidence supplement — 2026-10-13\n\nSee external_evidence_2026_10_13/REPORT_FA.md. This adds 25 exploratory source-only fits evaluated on a separate public cohort in a restricted three-feature space, plus an official published FNA fee and shared-service cost scenario. Subject-level balanced accuracy was 0.575 with a descriptive 95% interval [0.475,0.675]; no clinical superiority is established. The original 1,464-run paper remains separate. Clinical identities, historical missing evidence and author signoff remain unresolved.\n'
readme.write_text(s,encoding='utf-8')
with zipfile.ZipFile(r/'CostStableEHOA_Public_Evidence_2026_10_13.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in p.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(r))
    for name in ['run_external_evidence.py','summarize_external_evidence.py']:z.write(r/name,name)
print(json.dumps(audit))
