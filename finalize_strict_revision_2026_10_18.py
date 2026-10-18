from pathlib import Path
import json,csv,hashlib,shutil,re,os,zipfile
import numpy as np
import pandas as pd
from pypdf import PdfReader
from docx import Document

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'strict_revision_2026_10_18'
AUDIT=ROOT/'strict_review_2026_10_18'
OLD=ROOT/'scientific_revision_2026_10_18'
PUBLIC=ROOT/'public_coststable_ehoa' if (ROOT/'public_coststable_ehoa').is_dir() else ROOT
summary=json.loads((AUDIT/'summary.json').read_text())
independent=json.loads((AUDIT/'independent_control_check.json').read_text())
if summary['completed']!=450 or summary['budget_violations'] or summary['row_overlap'] or summary['group_overlap'] or any(independent['maxima'].values()) or independent['stability_maximum_error']>1e-12:
    raise ValueError('Control audit failed')
old=pd.read_csv(ROOT/'scientific_audit_2026_10_18/independent_paired_and_exact_sensitivity.csv')
new=pd.read_csv(AUDIT/'paired_controls.csv')
p=np.r_[old.p_exact_conditional_ties,new.p_exact];order=np.argsort(p);adjusted=np.empty(len(p));adjusted[order]=np.minimum(1,np.maximum.accumulate(p[order]*np.arange(len(p),0,-1)))
new['p_holm_combined_33']=adjusted[len(old):]
new.to_csv(AUDIT/'paired_controls_global_sensitivity.csv',index=False)
content=json.loads((OUT/'sources/manuscript_content.json').read_text(encoding='utf-8'))
page_counts={name:len(PdfReader(OUT/name).pages) for name in ['manuscript_en.pdf','manuscript_fa.pdf','qa/word_en.pdf','qa/word_fa.pdf']}
if set(page_counts.values())!={4}:raise ValueError('Four-page template requirement failed')
visual=json.loads((OUT/'qa_visual_review.json').read_text())
for name,digest in {**visual['pdf_sha256'],**visual['docx_sha256'],'sources/manuscript_content.json':visual['content_sha256']}.items():
    if hashlib.sha256((OUT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Visual review is stale')
counts={kind:sum(b['kind']==kind for page in content['pages'] for b in page) for kind in ['ref','table','fig']}
if counts!={'ref':18,'table':9,'fig':2}:raise ValueError('Content counts differ')
for name in ['author_declaration_draft_fa.md','AUTHOR_APPROVAL_STATUS.json','SUBMISSION_STATUS_FA.md','evidence_requests_drafts.md','unresolved_items_fa.md']:
    shutil.copy2(OLD/name,OUT/name)
with (OUT/'unresolved_items_fa.md').open('a',encoding='utf-8') as f:
    f.write('\n\nممیزی سخت‌گیرانه: کنترل‌های بدون جست‌وجو ضرورت EHOA را ثابت نکردند؛ این ایراد با آزمایش و محدودکردن ادعا پاسخ گرفت، نه با اثبات برتری. تعمیم به تخصیص‌های هزینه تازه، اثر مستقل SD در تمام تنظیم اصلی، bootstrap سودمندی فردمحور و طبقه‌بندهای دیگر هنوز مطالعه نشده‌اند. نتیجه به همین پروتکل محدود است.\n')
report='''# داوری سخت‌گیرانه و اقدامات اصلاحی

نتیجه اصلی: مقایسه اولیه بدون کنترل فیلتر ساده، ضرورت EHOA را بررسی نمی‌کرد. ۴۵۰ کنترل تازه روی همان تقسیم‌ها اجرا شد. شواهد فعلی ضرورت جست‌وجو یا برتری پیش‌بینی روش را اثبات نمی‌کنند؛ پایداری توصیفی فیلترها بسیار بیشتر است. مقاله اکنون نتیجه منفی و دامنه محدود خود را در چکیده، جدول۵، بخش۷ و نتیجه‌گیری نشان می‌دهد.

## ۱ فقدان کنترل بدون جست‌وجو

رفع آزمایشی: GreedyMI و GreedyResampled از ماسک کامل شروع و همان حذف کمینه سودمندی/هزینه را یک بار اعمال می‌کنند؛ حل دقیق کوله‌پشتی یا پیاده‌سازی الگوریتم مقاله دیگری نیستند. AllFeatures کنترل نامقید است. هر روش ده دیتاست×پنج بذر×سه تقسیم دارد. سودمندی، تقسیم و هزینه از فایل آموزش بیرونی همان روش اولیه گرفته شدند؛ ماسک با برچسب آزمون انتخاب نشد. همان پیش‌پردازش منتخب، SMOTE فقط آموزش و KNN5 استفاده شد. ۴۵۰ فایل evidence.npz ماسک، هزینه، سودمندی، تقسیم، برچسب و احتمال را نگه می‌دارند. بررسی مستقل هر۴۵۰ فایل، اختلاف ماسک/سودمندی/تقسیم/برچسب صفر و اختلاف پایداری≤۱٫۱۱e−16 داشت.

میانگین دقت متوازن/پایداری: EHOA بازنمونه‌گیری‌شده0.7932/0.2241، فیلترMI برابر0.7869/0.6709، فیلتر بازنمونه‌گیری0.7840/0.7999 و همه‌ویژگی‌ها0.7873/1 است. پایداری۱ ماسک کامل قرارداد تباهیده است، نه زیست‌نشانگر معتبر. این روش به بودجه۳۰٪ مقید نیست؛ هزینه۱ آن نتیجه مکانیکی است.

## ۲ آزمون‌های پسینی و چندگانگی

طرح کنترل پیش از محاسبه محلی ثبت شد، ولی نتایج قبلی معلوم بودند؛ ثبت پیشینی مستقل یا عمومی ادعا نمی‌شود. واحد آماری ده میانگین دیتاست است، نه۴۵۰ برازش مستقل. خانواده۹آزمونی سه معیار×سه کنترل، آزمون علامت‌رتبه دقیق شرطی و هولم دارد. دقت متوازن نسبت به دو فیلتر p=0.7734375 و0.966796875 دارد. اختلاف پایداری با فیلترMI برابر−0.4467799635 و با فیلتر بازنمونه‌گیری−0.5758034652 است؛ Holm9 p=0.0234375 و0.017578125.

برای حساسیت محافظه‌کارانه، پس از نتایج، ۲۴ مقایسه اصلی و۹کنترل در یک خانواده۳۳تایی با p دقیق شرطی ترکیب شدند. برای دو اختلاف پایداری p=0.08203125 و0.064453125 است و هیچ مقایسه جدید در سطح0.05 معنادار نمی‌ماند. این خانواده جایگزین پنهان تحلیل اولیه نیست؛ هر دو نمایش داده شده‌اند. فاصله‌های۲۰۰۰۰bootstrap دیتاست، تعدیل‌نشده و توصیفی‌اند و تضمین پوشش یا تعمیم به جامعه دلخواه دیتاست‌ها ندارند. عدم معناداری، هم‌ارزی/عدم‌کمتری نیست.

## ۳ سهم علمی و نوآوری

ادعای روش برتر، ضرورت wrapper یا خانواده بهینه‌سازی تازه حذف/رد شد. سهم قابل‌دفاع، ارزیابی کنترل‌شده و بازتولیدپذیر تعمیر بودجه و نشان‌دادن محدودیت‌های آن است. افزودن فیلترها، محدودیت ناشی از نبود مقایسه ساده را رفع می‌کند؛ برتری بر همه روش‌های روز یا پذیرش کنگره را ثابت نمی‌کند. نتایج هیچ بازنویسی به سود روش دریافت نکردند.

## ۴ هزینه مصنوعی و نسبت سودمندی به هزینه

فقط یک بردار lognormal برای هر بُعد با بذر1000+D وجود دارد؛ دیتاست‌های هم‌بُعد همان بردار را دارند. نتیجه شرطی به این تخصیص است و حساسیت بودجه، حساسیت به تخصیص هزینه نیست. این قید در بخش۴ و نتیجه‌گیری افزوده شد. مرجع۱۸ از متن اصلی نویسندگان درباره ترجیح نویز ارزان توسط نسبت سود/هزینه بررسی و افزوده شد: https://arxiv.org/abs/2008.05163v2 . هزینه واقعی هر ویژگی، زمان و خطر یا صرفه‌جویی بالینی فراهم نشده و ادعا نمی‌شود. تعرفهFNA فقط سناریوی مشترک قبلی است.

## ۵ اثر مستقل SD و واحد بازنمونه‌گیری

مقایسه MI با میانگین منهایSD هم میانگین‌گیری و هم جریمه را تغییر می‌دهد. کنترل mean-only در همه تنظیم‌های اصلی موجود نیست؛ اثر مستقل SD ادعا نمی‌شود. حساسیت‌های قبلی فقط دامنه خود را پوشش می‌دهند. بازنمونه‌گیری سودمندی Parkinson در سطح ضبط است؛ جداسازی گروهیCV آن را به bootstrap فردی تبدیل نمی‌کند. این SD عدم‌قطعیت فردمحور نیست و با bootstrap فردی مقصد تفاوت دارد. متن صریح شد؛ پروتکل گذشته پنهانی تغییر نکرد.

## ۶ دامنه تعمیم و شواهد باقی‌مانده

خروجی به همین KNN/SMOTE، دیتاست‌ها، هزینه و بودجه محدود است. بازبرازش و کنترل عددی، اعتبار بالینی نیست. آزمون انتقال سه‌ویژگی مدل۲۲ویژگی را اعتبارسنجی نمی‌کند. هویت بالینیOxford، هزینه حاشیه‌ای واقعی، داده بالینی کامل مستقل و سوابق تاریخی مفقود هنوز شواهد تازه ندارند. اینها با واژه‌پردازی حل‌شده اعلام نشدند. تأیید اظهارنامه نویسنده وجود ندارد و ارسال به کنگره طبق دستور نویسنده انجام نشده است.

## مدارک

پروتکل: protocol.json؛ خروجی‌ها: runs.csv و jobs؛ آمار: dataset_means.csv و paired_controls.csv؛ حساسیت۳۳تایی: paired_controls_global_sensitivity.csv؛ بررسی مستقل: independent_control_check.json و INDEPENDENT_REVIEW_FA.md. مقاله معتبر: strict_revision_2026_10_18. نسخه‌های قبلی تاریخی‌اند.
'''
(AUDIT/'STRICT_REVIEW_AND_RESOLUTIONS_FA.md').write_text(report,encoding='utf-8')
rows=list(csv.DictReader((OLD/'reviewer_response.csv').open(encoding='utf-8-sig')))
updates={0:'کنترل گمشده بدون جست‌وجو با۴۵۰ برازش اضافه شد؛ ضرورت EHOA و برتری پیش‌بینی ثابت نیست. سهم به مقایسه کنترل‌شده محدود شد.',1:'خانواده۹آزمونی کنترل‌ها و حساسیت محافظه‌کارانه۳۳تایی با۲۴مقایسه اصلی افزوده شد؛ هیچ مقایسه جدید در Holm33 معنادار نیست. عدم معناداری هم‌ارزی نیست.',2:'نسخه فارسی و انگلیسی Word/PDF هرکدام چهار صفحه،۱۸مرجع،۹جدول،۲شکل و۵معادله بومی Word دارند؛۱۶صفحه نهایی بازبینی شد.',3:'آزمایش فیلترهای مستقیم، سهم جست‌وجو را از سودمندی جدا کرد؛ کنترل اثر مستقلSD در همه تنظیم اصلی موجود نیست و آن اثر ادعا نمی‌شود.',7:'سناریویFNA و انتقال سه‌ویژگی حفظ شدند؛ تعمیم به مدل۲۲ویژگی، هزینه حاشیه‌ای واقعی یا کاربرد بالینی اثبات نشده است.',12:'۴۵۰کنترل تازه با مدارک ماسک/احتمال/تقسیم منتشر شد و مستقلاً بررسی شد؛ اعداد تاریخی۱۴۶۴اجرایی تغییر نکردند.'}
response='# پاسخ۱۴بند پس از داوری سخت‌گیرانه\n\nنسخه معتبر strict_revision_2026_10_18؛ کنترل‌ها مستقل از۱۴۶۴اجرای اصلی و۲۵انتقال‌اند.\n\n'
for i,row in enumerate(rows):
    row['action']=updates.get(i,row['action']).replace('۱۷ مرجع','۱۸ مرجع')
    row['location']='چکیده؛ بخش۴،۷/جدول۵،۹ و۱۰؛ پیوست داوری سخت‌گیرانه'
    row['evidence']='strict_review_2026_10_18/STRICT_REVIEW_AND_RESOLUTIONS_FA.md؛ paired_controls_global_sensitivity.csv؛ independent_control_check.json؛ delivery_quality.json'
    response+=f'## {row["reviewer_item"]}\n\nایراد: {row["concern"]}\n\nاقدام: {row["action"]}\n\nمحل و شاهد: {row["location"]}؛ {row["evidence"]}\n\n'
with (OUT/'reviewer_response.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
(OUT/'response_to_reviewers_fa.md').write_text(response,encoding='utf-8')
readme='''# مقاله پس از داوری سخت‌گیرانه

آخرین مقاله: strict_revision_2026_10_18؛ شواهد تازه: strict_review_2026_10_18.

ایراد اصلی نبود کنترل بدون EHOA بود.۴۵۰برازش تازه این کنترل را افزودند. فیلترهای ساده پایداری توصیفی بسیار بیشتری دارند؛ برتری دقت یا ضرورت EHOA ثابت نشد. نتایج منفی در چکیده، جدول۵، بحث و نتیجه‌گیری‌اند. Holm9 و حساسیت محافظه‌کارانهHolm33 هر دو گزارش شدند؛ در خانواده۳۳تایی هیچ مقایسه جدید معنادار نیست. نتیجه شرطی به یک تخصیص هزینه مصنوعی برای هر بُعد و همین پایپ‌لاین است.

هر مقاله فارسی و انگلیسی Word/PDF چهار صفحه،۱۸مرجع،۹جدول،۲شکل و۵معادله بومی دارد. پاسخ۱۴بند و گزارش نقد/اصلاح پیوست‌اند. نسخه‌های پیشین حفظ شدند. مطالعه اولیه۱۴۶۴اجرا، انتقال۲۵برازش و کنترل تازه۴۵۰برازش جدا هستند؛ بازبرازش و بازاجرای ممیزی تکرار مستقل آماری نیستند.

برای بازتولید کنترل‌ها run_strict_controls_2026_10_18.py را در یک کپی اجرا کنید؛ utility آموزش ذخیره‌شده استفاده می‌شود و ادعای زمان مستقل وجود ندارد. ساخت سند با build_strict_revision_2026_10_18.py و آماده‌سازی با finalize_strict_revision_2026_10_18.py است. بعد از ساخت، XeLaTeX و Word باید دوباره رندر و همه صفحات واقعاً بازبینی شوند؛ هش قدیمی تأیید نسخه جدید نیست. نسخه محیط فعلی در پروتکل است و با محیط تاریخی تفاوت دارد.

هویت بالینیOxford، هزینه واقعی ویژگی، اعتبارسنجی کامل بالینی و سوابق تاریخی هنوز شواهد کافی ندارند. اظهارنامه نویسنده تأیید نشده؛ ارسال به کنگره انجام نشد. ممیزی تضمین پذیرش نیست.
'''
(OUT/'README_FA.md').write_text(readme,encoding='utf-8')
verification=pd.read_csv(OUT/'sources/reference_verification.csv')
verification=verification[verification.reference_id!=18]
verification=pd.concat([verification,pd.DataFrame([dict(reference_id=18,verified_source='https://arxiv.org/abs/2008.05163v2',verification_date='2026-10-18',doi_status='Author primary source checked; preprint explicitly labeled')])],ignore_index=True)
verification.to_csv(OUT/'sources/reference_verification.csv',index=False)
for script in ['run_strict_controls_2026_10_18.py','build_strict_revision_2026_10_18.py','finalize_strict_revision_2026_10_18.py']:
    shutil.copy2(ROOT/script,OUT/'sources'/script)
quality=dict(date='2026-10-18',page_counts=page_counts,references=18,tables=9,figures=2,reviewer_responses=len(rows),native_word_equations={f'manuscript_{lang}.docx':len(Document(OUT/f'manuscript_{lang}.docx').element.xpath('.//m:oMath')) for lang in ['en','fa']},visual_review=visual,controls=summary,independent_audit=independent,combined_33_sensitivity=new.to_dict('records'),original_study_runs=1464,separate_transfer_fits=25,new_posthoc_controls=450,submission='Not authorized; not submitted')
(OUT/'delivery_quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=[dict(path=f.relative_to(OUT).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in OUT.rglob('*') if f.is_file() and f.name!='SHA256_MANIFEST.json' and f.suffix not in ['.aux','.log','.out']]
(OUT/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
if PUBLIC!=ROOT:
    for folder in [OUT,AUDIT]:shutil.copytree(folder,PUBLIC/folder.name,dirs_exist_ok=True)
    for script in ['run_strict_controls_2026_10_18.py','build_strict_revision_2026_10_18.py','finalize_strict_revision_2026_10_18.py']:shutil.copy2(ROOT/script,PUBLIC/script)
    for name in ['README.md','CONTINUE_WORK_FA.md']:
        path=PUBLIC/name;text=path.read_text(encoding='utf-8')
        text=text.replace('The latest authoritative manuscript is scientific_revision_2026_10_18','The latest authoritative manuscript is strict_revision_2026_10_18').replace('آخرین نسخه معتبر: scientific_revision_2026_10_18','آخرین نسخه معتبر: strict_revision_2026_10_18')
        marker='## Strict reviewer controls 2026-10-18'
        if marker in text:text=text.split(marker)[0].rstrip()+'\n'
        text+='\n'+marker+'\n\nLatest manuscript: `strict_revision_2026_10_18`; new evidence: `strict_review_2026_10_18`. 450 post-hoc no-search controls use the same 150 outer splits per method. EHOA predictive superiority and necessity are unestablished; no-search filters have higher descriptive subset stability. Both Holm9 and conservative combined Holm33 sensitivity are reported. All four manuscript PDFs have four pages, 18 references, nine tables and two figures. Run `run_strict_controls_2026_10_18.py`, then rebuild/render/review manuscripts; original historical inputs remain frozen. Author approval is absent and conference submission remains prohibited.\n'
        path.write_text(text,encoding='utf-8')
print(json.dumps(dict(pages=page_counts,references=18,responses=len(rows),controls=450)),flush=True)
