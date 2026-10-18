from pathlib import Path
import json,csv,hashlib,shutil,re
from pypdf import PdfReader
from docx import Document

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scientific_revision_2026_10_18'
AUDIT=ROOT/'scientific_audit_2026_10_18'
OLD=ROOT/'integrated_revision_2026_10_13'
PUBLIC=ROOT/'public_coststable_ehoa' if (ROOT/'public_coststable_ehoa').is_dir() else ROOT
refit=json.loads((AUDIT/'final_classifier_refit_summary.json').read_text())
optimizer=json.loads((AUDIT/'optimizer_replay_summary.json').read_text())
stats=json.loads((AUDIT/'statistical_summary.json').read_text())
secondary=json.loads((AUDIT/'secondary_summary.json').read_text())
robustness=json.loads((AUDIT/'robustness_summary.json').read_text())
visual=json.loads((OUT/'qa_visual_review.json').read_text())
if refit['prediction_disagreements'] or refit['maximum_metric_error']>1e-12 or refit['budget_violations'] or optimizer['historical_mask_mismatches'] or optimizer['maximum_winning_fitness_recalculation_error']>1e-12:
    raise ValueError('Scientific audit failed; publication withheld')
for name,digest in {**visual['pdf_sha256'],**visual['docx_sha256']}.items():
    if hashlib.sha256((OUT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Visual inspection is stale')
if hashlib.sha256((OUT/'sources/manuscript_content.json').read_bytes()).hexdigest()!=visual['content_sha256']:raise ValueError('Reviewed content has changed')
content=json.loads((OUT/'sources/manuscript_content.json').read_text(encoding='utf-8'))
page_counts={n:len(PdfReader(OUT/n).pages) for n in visual['pdf_sha256']}
refs=[b for page in content['pages'] for b in page if b['kind']=='ref']
tables=[b for page in content['pages'] for b in page if b['kind']=='table']
if any(v!=4 for v in page_counts.values()) or len(refs)!=17 or len(tables)!=9:raise ValueError('Manuscript structure failed')
quality={'date':'2026-10-18','page_counts':page_counts,'references':len(refs),'tables':len(tables),'figures':sum(b['kind']=='fig' for page in content['pages'] for b in page),'native_word_equations':{f.name:len(Document(f).element.xpath('.//m:oMath')) for f in OUT.glob('*.docx')},'visual_review':visual,'final_classifier_refit':refit,'optimizer_replay':optimizer,'statistical_audit':stats,'secondary_audit':secondary,'robustness':robustness,'author_approved':False,'submitted':False,'scope':'All saved runs and active scientific analysis audited;75representative optimizer searches replayed, not every historical search. No independent clinical identity or new measured marginal acquisition costs obtained.'}
quality['score_vector_provenance']='The statistical subaudit used saved historical hard labels. The separate parent audit refitted all1464final classifiers, saved fresh score vectors and matched historical scalar AUC/PR-AUC; absent original score vectors are not claimed recovered.'
(OUT/'delivery_quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
with (AUDIT/'external_classifier_refit_audit.csv').open(encoding='utf-8') as f:
    external=list(csv.DictReader(f))
external_summary={'refits':len(external),'prediction_disagreements':sum(int(x['prediction_disagreements']) for x in external),'maximum_probability_error':max(float(x['maximum_probability_error']) for x in external),'target_order_and_labels_match':all(x['target_order_matches']=='True' and x['labels_match']=='True' for x in external)}
(AUDIT/'external_classifier_refit_summary.json').write_text(json.dumps(external_summary,indent=2),encoding='utf-8')
report='''# ممیزی علمی و اصلاح مقاله — 2026-10-18

این مرحله صرفاً بررسی بسته‌بندی نیست. داده‌ها، مسیر فعال آموزش و انتخاب، پیش‌بینی‌ها، معیارها، پایداری، آزمون‌ها، حساسیت، تعامل و ادعاهای مقاله بررسی شدند. نسخه‌های تاریخی تغییر نکرده‌اند. ممیزی محاسباتی جای داوری انسانی یا اعتبارسنجی بالینی نیست.

## اصلاح علمی اصلی

معناداری مرزی پایداری در خانواده24مقایسه، به تعداد دیتاست‌ها حساس است. با حذف هر یک از10دیتاست، جهت اختلاف نسبت به EHOA و Random مثبت می‌ماند ولی هیچ خانواده9دیتاستی معنادار نیست؛ کمینه Holm24=0.09375. حذف Oxford نیز اثر مثبت را حفظ می‌کند. تفکیک آزمون دوطرفه با9تفاضل غیرصفر حداقل2/512است؛ این نتیجه به‌معنی نبود اثر نیست. تحلیل10دیتاستی حذف یا با نتیجه انتخابی جایگزین نشد. چکیده، بخش7، جدول7 و نتیجه‌گیری اکنون این شکنندگی را آشکار می‌کنند.

سه جفت ویژگی یکسان با برچسب مخالف در Spambase شناسایی و در بخش5 افشا شدند. هویت ایمیل اصلی در دسترس نیست؛ برخورد ویژگی، نشت قطعی موجودیت نیست. برچسب‌ها دلخواه عوض یا ردیف‌ها به‌نفع نتیجه حذف نشدند. حساسیت حذف Spambase نیز در پرونده LODO موجود است.

## بازحساب انتها به انتها

هر1464طبقه‌بند نهایی با ماسک و تقسیم تاریخی بازبرازش شد؛ جایگذاری، استانداردسازی و SMOTE فقط روی ستون‌های منتخب آموزش انجام شدند. احتمال‌ها در refit_probabilities ذخیره شدند. اندیس، برچسب و پیش‌بینی با فایل اصلی مقایسه شد؛ AUC،PR-AUC،accuracy،BA،precision،recall،specificity،F1وMCC از نو محاسبه شدند. پیش‌بینی1464اجرا هیچ اختلافی ندارد و بیشینه اختلاف معیار1.11e-16است.25طبقه‌بند انتقال هم بازبرازش شدند و با احتمال‌های ذخیره‌شده قبلی اختلافی نداشتند.

محیط ممیزی فعلی با محیط تاریخی pinned فرق دارد؛ نسخه دقیق در final_classifier_refit_summary.json است. این بازبرازش با ماسک ثابت و محیط جدید است، نه ادعای بازیابی احتمال تاریخیِ ذخیره‌نشده. برابری معیارها، برابری همه احتمال‌های ثبت‌نشده گذشته را ثابت نمی‌کند.

75جست‌وجوی بهینه‌ساز بازاجرا شد:50ترکیب ده‌دیتاست×پنج‌روش در اولین بذر/تقسیم اصلی، به‌اضافه25انتقال. هر75ماسک تاریخی بازتولید شد؛ شمار ارزیابی هر50جست‌وجوی اصلی نیز با رکورد تاریخی برابر است. ماسک خام برنده، ماسک‌های تعمیرشده هر تقسیم، cachehitها،fitnessوaccuracyهمه فراخوانی‌ها اکنون در search_trace.npz ثبت شده‌اند. برازندگی برنده با آموزش جداگانه هر تقسیم مستقلاً بازحساب شد؛ بیشینه خطا5.56e-17است. این75بازاجرای پسینی، لاگ قدیمی همه1464جست‌وجو یا ثبت پیشینی گذشته نیست.

## داده و استنباط

واحد استنباط اصلی دیتاست است؛15ماسک مستقل فرض نشدند. φ با variance(ddof1)،جاکارد،Friedman،رتبه‌ها،WilcoxonوHolmوbootstrapدیتاستی مستقل بازحساب شدند. میانگین‌های اصلی/OFAT،80سلول و280اثر فاکتوریل،28فاصله فاکتوریل و35فاصله مقایسه جست‌وجو با خروجی قبلی در حدود2.85e-14تطابق دارند. فاصله‌های وابسته به دیتاست/فرد توصیفی‌اند؛ از آن‌ها تضمین پوشش یا برتری بالینی استخراج نشد.

هر1464تقسیم از نظر partitionردیف و همپوشانی درونی/بیرونی و گروه‌های نگاشت‌شده بررسی شد. همه قیدهای بودجه فعال رعایت شدند. نبود همپوشانی پیشوند، هویت بالینی31/32فرد را تأیید نمی‌کند. پوشه independent_dataset_structure و پرونده‌های groupchecks وcollisions دامنه شاهد را مشخص می‌کنند.

## بررسی کد و معادلات

مسیر فعال شامل ehoa.py،proposed/fold_safe_ehoa.py،repair_to_budget در proposed/cost_stable_ehoa.py و توابع فعال utils.py است. مقداردهی،عاملSFو به‌روزرسانی سرعت با معادلات6،7و9 منبع اصلی مقایسه شد: https://doi.org/10.1007/s10586-026-05946-9 . clipحدود، RNGبرداری، رفع ماسک تهی وcache جزئیات پیاده‌سازی‌اند و در مقاله توصیف شده‌اند. جداسازی موقعیت پیوسته از ماسک و تعمیر مستقل درونی/بیرونی با مسیر کد و75بازاجرا سازگار است. bestfitness به ماسک خام برنده و تعمیرهای محلی تعلق دارد؛ لزوماً fitnessیک ماسک ثابت نهایی نیست.

کاهش بودجه با حذف ویژگی روی هزینه‌های مثبت تاحدمتناهی تمام می‌شود؛ خروجی ناتهی فقط در صورت وجود ویژگی قابل‌خرید ممکن است. این تضمین قید هزینه است، نه تضمین بهینه‌بودن. λSDکران اطمینان کالیبره نیست. bootstrapسودمندی از ردیف آموزش استفاده می‌کند، نه بازنمونه‌گیری فرد مستقل؛ ازSDآن استنباط بالینی نشده است. SMOTE معمولی می‌تواند برای ستون‌های درجه‌ای/دودویی مقدار کسری بسازد؛ مدل این ورودی‌ها را عددی می‌گیرد و پروفایل حاضر اعتبار زیستی نمونه مصنوعی را اثبات نمی‌کند.

patchسراسری prepare_cv_folds در fit برای API چندرشته‌ای هم‌زمان ایمن نیست؛ اجراهای پژوهش در workerهای ProcessPool جدا و fitسری داخل هرworker هستند. مسیرهای آرشیوی run_experiments/evaluate_classifiers، جایگزین پایپ‌لاین fold-safe مقاله فعلی نیستند. این ممیزی تضمین تمام APIهای آرشیوی یا همه کاربردهای ممکن نیست.

## باقی‌مانده‌های واقعی

اعتبار بالینی کامل همان22ویژگی، هزینه حاشیه‌ای واقعی/زمان/خطر، توضیح معتبر هویت Oxford و سوابق تاریخی مفقود هنوز مدرک ندارند. مطالعه به‌صورت benchmarkمحاسباتی با محدودیت صریح ارائه می‌شود. هزینه واقعی یا هویت تولید نشده است. نویسنده هنوز اظهارنامه را تأیید نکرده و ارسال را منع کرده است؛ ارسال انجام نشده است.
'''
(AUDIT/'SCIENTIFIC_AUDIT_FA.md').write_text(report,encoding='utf-8')
resolutions=[{'finding':'S01','resolution':'Corrected interpretation in new abstract,section7,Table7 and conclusion; primary ten-dataset analysis retained','status':'addressed'},{'finding':'S02','resolution':'Disclosed in section5 and collision files; no unsupported entity-leakage claim or relabeling','status':'disclosed evidence limitation'},{'finding':'S03','resolution':'All mapped groups checked and Oxford-exclusion sensitivity reported; clinical mapping unavailable','status':'external evidence pending'},{'finding':'Missing saved primary score vectors','resolution':'1464fixed-mask final classifiers refitted and fresh probabilities saved; original score vectors not claimed recovered','status':'forward audit gap addressed'},{'finding':'Historical optimizer raw traces missing','resolution':'75current-runtime replay traces and independent fitness checks saved','status':'sampled replay completed; missing original history remains'}]
(AUDIT/'resolution_matrix.json').write_text(json.dumps(resolutions,indent=2),encoding='utf-8')
rows=list(csv.DictReader((OLD/'analysis/reviewer_response.csv').open(encoding='utf-8-sig')))
updates={0:'مسیر علمی فعال و محاسبات ممیزی شدند؛ شکنندگی معناداری پس از حذف دیتاست در چکیده، جدول ۷ و نتیجه‌گیری روشن شد. ادعای برتری عمومی نداریم.',1:'آزمون‌ها، هولم، پایداری و bootstrap مستقل بازحساب شدند. در هر ۱۰ خانواده نه‌دیتاستی LODO، مقدار Holm24 حداقل 0.09375 است؛ جهت اثر مثبت باقی می‌ماند. این حساسیت پسینی است.',2:'هر نسخه فارسی و انگلیسی Word/PDF چهار صفحه، ۱۷ مرجع، ۹ جدول، ۲ شکل و ۵ معادله قابل‌ویرایش دارد. هر ۱۶ صفحه خروجی نهایی بازبینی شد.',5:'ساختار داده، برچسب، partition و گروه‌های هر ۱۴۶۴ اجرا بررسی شد. سه جفت Spambase با X یکسان و y مخالف در بخش ۵ افشا شد؛ نشت قطعی ادعا نشد. هویت بالینی Oxford همچنان نامعلوم است.',6:'۷۵ جست‌وجوی پسینی با trace ماسک خام، تعمیرها و fitness بازاجرا شد. همچنین ۱۴۶۴ طبقه‌بند نهایی و ۲۵ انتقال بازبرازش شدند. محیط جدید ثبت شد؛ لاگ قدیمی یا ثبت پیشینی جعل نشد.',7:'جدول ۸ سرطان پستان، جدول ۹ انتقال، تحلیل گروهی FNA و محدودیت اعتبار بالینی حفظ شدند. هزینه حاشیه‌ای، زمان و خطر واقعی موجود نیست.',12:'در ۱۴۶۴ به‌اضافه ۲۵ بازبرازش، اختلاف پیش‌بینی صفر بود؛ AUC/PR-AUC و سایر معیارها بازحساب شدند. هر ۷۵ ماسک بهینه‌ساز منتخب با نسخه قدیمی مطابق بود؛ این بازاجرای تمام جست‌وجوهای تاریخی نیست.',13:'نویسنده اظهارنامه را تأیید نکرده و ارسال را منع کرده است. اظهارنامه پیش‌نویس باقی مانده و توقف ارسال برقرار است.'}
response='# پاسخ14بند پس از ممیزی علمی\n\nنسخه معتبر: scientific_revision_2026_10_18. ممیزی علمی: scientific_audit_2026_10_18. اعداد اصلی بازمحاسبه شدند و تفسیر شکنندگی اصلاح شد؛ نسخه‌های تاریخی حفظ شدند.\n\n'
for i,row in enumerate(rows):
    row['action']=updates.get(i,row['action']).replace('جدول8','جدول۸').replace('جدول9','جدول۹')
    row['location']='چکیده،بخش5،بخش7/جدول7،جدول8/9،بخش9و10؛ ممیزی علمی'
    row['evidence']='delivery_quality.json؛ scientific_audit_2026_10_18/SCIENTIFIC_AUDIT_FA.md؛ فایل‌های بازحساب/احتمالات/trace'
    response+=f'## {row["reviewer_item"]}\n\nایراد: {row["concern"]}\n\nاقدام: {row["action"]}\n\nمحل و شاهد: {row["location"]}؛ {row["evidence"]}\n\n'
with (OUT/'reviewer_response.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'response_to_reviewers_fa.md').write_text(response,encoding='utf-8')
for name in ['author_declaration_draft_fa.md','AUTHOR_APPROVAL_STATUS.json','SUBMISSION_STATUS_FA.md','evidence_requests_drafts.md']:shutil.copy2(OLD/name,OUT/name)
(OUT/'unresolved_items_fa.md').write_text('''# وضعیت نهایی ممیزی علمی

ممیزی علمی مسیر فعال و ادعاها، بازبرازش1464+25طبقه‌بند، ذخیره احتمال، بازاجرای75جست‌وجوی منتخب، بازحساب مستقل آمار و حساسیت حذف هر دیتاست انجام شد. تفسیر شکنندگی در نسخه مقاله اصلاح شد. نبود بازبینی علمی دیگر به‌عنوان کار انجام‌نشده گزارش نمی‌شود؛ دامنه دقیق و محدودیت ممیزی در SCIENTIFIC_AUDIT_FA.md است.

اعتبار بالینی کامل22ویژگی با داده هم‌تعریف مستقل، هزینه واقعی حاشیه‌ای ویژگی/زمان/خطر، تأیید مالک داده برای هویتOxford و سوابق تاریخی مفقود هنوز مدرک ندارند. این‌ها با تغییر کد یا تولید سند جدید قابل ایجاد معتبر نیستند. داده سه‌ویژگی، تعرفه مشترک و لاگ بازاجرای فعلی جایگزین آن‌ها نشده‌اند.

نویسنده اظهارنامه را تأیید نکرده و ارسال را منع کرده است؛ مقاله ارسال نشده است. همه موارد حل‌نشده در مقاله و پاسخ‌ها محدودیت‌اند، نه وعده تکمیل یا داده ساختگی.
''',encoding='utf-8')
(OUT/'README_FA.md').write_text('''# نسخه علمی ممیزی‌شده

آخرین مقاله: scientific_revision_2026_10_18. Word/PDF/LaTeXهر زبان4صفحه،17مرجع،9جدول،2شکل،5معادله قابل‌ویرایش وپاسخ14بند به‌روز است. همه16صفحه خروجی نهایی بازبینی شد.

نتیجه مهم: معناداری مرزی پایداری با حذف هر دیتاست از بین می‌رود، هرچند جهت اثر مثبت باقی است. اینموضوع اکنون در چکیده و جدول7 روشن است. Spambaseدارای3جفتویژگی یکسان با برچسب مخالف است؛ هویت ایمیل نامعلوم است.

گزارش علمی و فایل‌های مستقل در scientific_audit_2026_10_18 هستند.1464طبقه‌بند نهایی و25انتقال بازبرازش و75بهینه‌ساز منتخب بازاجرا شدند.1464جست‌وجوی کامل دوباره اجرا نشده‌اند. شواهد تاریخی حذف یا بازنویسی نشده‌اند. منع ارسال نویسنده برقرار است.
''',encoding='utf-8')
for script in ['build_scientific_revision_2026_10_18.py','finalize_scientific_revision_2026_10_18.py','audit_final_predictions_2026_10_18.py','audit_optimizer_replay_2026_10_18.py','scientific_statistical_audit_2026_10_18.py','scientific_robustness_audit_2026_10_18.py','scientific_secondary_audit_2026_10_18.py']:
    shutil.copy2(ROOT/script,OUT/'sources'/script)
manifest=[{'path':f.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in OUT.rglob('*') if f.is_file() and f.name!='SHA256_MANIFEST.json' and f.suffix not in ['.aux','.log','.out'] and 'overflow' not in f.name]
(OUT/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
if PUBLIC!=ROOT:
    shutil.copytree(OUT,PUBLIC/OUT.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.aux','*.log','*.out','*overflow*'))
    shutil.copytree(AUDIT,PUBLIC/AUDIT.name,dirs_exist_ok=True)
    for script in ['build_scientific_revision_2026_10_18.py','finalize_scientific_revision_2026_10_18.py','audit_final_predictions_2026_10_18.py','audit_optimizer_replay_2026_10_18.py','scientific_statistical_audit_2026_10_18.py','scientific_robustness_audit_2026_10_18.py','scientific_secondary_audit_2026_10_18.py']:shutil.copy2(ROOT/script,PUBLIC/script)
readme=PUBLIC/'README.md'; s=readme.read_text(encoding='utf-8')
s=s.replace('The latest authoritative manuscript is integrated_revision_2026_10_13; extended_revision_2026_10_12 and earlier results are archival.','The latest authoritative manuscript is scientific_revision_2026_10_18; earlier manuscript versions remain archival.')
s=s.replace('Latest authoritative manuscript: integrated_revision_2026_10_13.','Historical integrated manuscript: integrated_revision_2026_10_13.')
section='\n## Scientific audit and revised manuscript — 2026-10-18\n\nLatest manuscript: scientific_revision_2026_10_18 (both languages4pages,17references,9tables,2figures). See scientific_audit_2026_10_18/SCIENTIFIC_AUDIT_FA.md. All1464fixed-mask final classifiers and25external predictions were refitted; probabilities are saved.75selected searches replayed with matching masks; this is not a replay of every historical optimizer run. Main statistical results reproduce, but all post-hoc nine-dataset leave-one-out families lose Holm24 significance(minimum0.09375); positive stability effects remain. Feature-label collisions are disclosed. Clinical evidence gaps and author submission hold remain.\n'
pattern=r'\n## Scientific audit and revised manuscript — 2026-10-18\n.*?(?=\n## |\Z)'
s=re.sub(pattern,lambda _:section,s,flags=re.S) if re.search(pattern,s,flags=re.S) else s+section
readme.write_text(s,encoding='utf-8')
guide=PUBLIC/'CONTINUE_WORK_FA.md'; s=guide.read_text(encoding='utf-8')
s=s.replace('آخرین مقاله ادغام‌شده: integrated_revision_2026_10_13.','آخرین مقاله علمی ممیزی‌شده: scientific_revision_2026_10_18.')
s=s.replace('آخرین نسخه معتبر: integrated_revision_2026_10_13؛ extended_revision_2026_10_12 نسخه تاریخی است.','آخرین نسخه معتبر: scientific_revision_2026_10_18؛ integrated_revision_2026_10_13 و extended_revision_2026_10_12 نسخه‌های تاریخی‌اند.')
s=s.replace('ساخت سند فعلی با build_integrated_documents.py','ساخت سند فعلی با build_scientific_revision_2026_10_18.py')
paragraph='\nممیزی علمی جدید در scientific_audit_2026_10_18 است. audit_final_predictions_2026_10_18.py همه1464+25طبقه‌بند را بازبرازش می‌کند و audit_optimizer_replay_2026_10_18.py فقط75جست‌وجوی ازپیش‌تعریف‌شده برای ممیزی را بازاجرا می‌کند؛ این اجراها جایگزین1464نتیجه تاریخی نیستند. بازسازی اسناد با سازندهscientificو بسته‌بندی با finalize_scientific_revision_2026_10_18.py است؛ qa_visual_review.json به هش PDFهای دیده‌شده متصل است و پس از تغییرPDF نیازمند بازبینی واقعی دوباره است. محیط ممیزی فعلی با محیط تاریخی pinned فرق دارد و نسخه‌ها ثبت شده‌اند.\n'
if 'ممیزی علمی جدید در scientific_audit_2026_10_18' not in s:s+=paragraph
guide.write_text(s,encoding='utf-8')
print(json.dumps({'pages':page_counts,'references':len(refs),'tables':len(tables),'reviewer_responses':len(rows),'audited_classifier_fits':refit['refitted_runs']+len(external),'optimizer_replays':optimizer['replays'],'scientific_revision':OUT.name},ensure_ascii=False))
