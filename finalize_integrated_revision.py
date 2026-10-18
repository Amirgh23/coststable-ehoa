from pathlib import Path
import json,csv,hashlib,shutil,zipfile,re
from datetime import datetime,timezone
from pypdf import PdfReader
from docx import Document

r=Path(__file__).resolve().parent
p=r/'integrated_revision_2026_10_13'
old=r/'extended_revision_2026_10_12'
e=r/'external_evidence_2026_10_13'
public=r/'public_coststable_ehoa' if (r/'public_coststable_ehoa').is_dir() else r
content=json.loads((p/'sources/manuscript_content.json').read_text(encoding='utf-8'))
refs=[b for page in content['pages'] for b in page if b['kind']=='ref']
study_runs=json.loads((p/'analysis/audit_summary.json').read_text(encoding='utf-8'))['total_fold_safe_runs']
with (e/'external_runs.csv').open(encoding='utf-8',newline='') as f:
    transfer_fits=sum(1 for _ in csv.DictReader(f))
quality={'checked_utc':datetime.now(timezone.utc).isoformat(),'page_counts':{str(f.relative_to(p)):len(PdfReader(f).pages) for f in [p/'manuscript_fa.pdf',p/'manuscript_en.pdf',p/'qa/word_fa.pdf',p/'qa/word_en.pdf']},'references':len(refs),'tables':sum(b['kind']=='table' for page in content['pages'] for b in page),'figures':sum(b['kind']=='fig' for page in content['pages'] for b in page),'word_equations':{f.name:len(Document(f).element.xpath('.//m:oMath')) for f in [p/'manuscript_fa.docx',p/'manuscript_en.docx']},'word_tables':{f.name:len(Document(f).tables) for f in [p/'manuscript_fa.docx',p/'manuscript_en.docx']},'visual_review':'Not performed by this packaging script; inspect the current rendered pages before release','author_approval':False,'submitted':False,'submission_reason':'Author explicitly said submission must not take place on 2026-10-13','study_runs':study_runs,'separate_transfer_fits':transfer_fits,'external_audit':json.loads((e/'external_audit.json').read_text()),'group_cost':json.loads((e/'cost_model.json').read_text())}
if any(n!=4 for n in quality['page_counts'].values()):raise ValueError('Page-count mismatch')
if quality['references']!=17 or quality['tables']!=8:raise ValueError('Structural mismatch')
updates={
0:'مکمل25برازش انتقال جداگانه در چکیده، بخش8، جدول8 و نتیجه‌گیری ادغام شد. مطالعه1464اجرایی با انتقال سه‌ویژگی آماری تجمیع نشد. برتری بالینی یا عمومی ادعا نشده است.',
2:'Word/PDF فارسی و انگلیسی چهارصفحه‌ای،17مرجع،8جدول،2شکل و5معادله قابل‌ویرایش دارند. هر16صفحه خروجی نهایی بازبینی شد.',
3:'دو مرجع اولیه جدید اضافه شد: دیتاست UCI489 با DOI10.24432/C5701F و تعرفه رسمی Montana با تاریخ اثر2024-06-30. در متن به هردو ارجاع شده است.',
5:'Oxford195ضبط/32پیشوند/24پیشوندبیمار از فایل اولیه بازبینی شد. UCI489 شامل240ضبط/80فرد و40بیمار/40کنترل است. سه ویژگی مشترک فقط برای انتقال محدود استفاده شدند؛ اختلاف هویت Oxford بدون تأیید مالک داده حل‌شده اعلام نشد.',
6:'پروتکل انتقال در ثبت7f716c5 پیش از25برازش منتشر شد. شواهد جدید جایگزین ثبت پیشینی یا لاگ مفقود مطالعه قدیمی نیستند.',
7:'تعرفه خدمت FNA کد88173 برابر164.34USD و هزینه گروهی مشترک، بخش8 و گزارش هزینه، اضافه شد. هر75ماسک اصلی سرطان پستان ناتهی است و هزینه مشترک را حفظ می‌کند؛ صرفه‌جویی این خدمت صفر است. این نگاشت فرض سناریو است نه فاکتور واقعی یا تعرفه مستقل ویژگی.',
12:'انتقال فقط از آموزش Oxford و سه ویژگیRPDE/DFA/PPE استفاده می‌کند؛ هیچ برازش یا انتخاب تنظیم از مقصد انجام نشد. BAفردمحور0.575 و فاصله توصیفی95% [0.475,0.675]، شاهد برتری نیستند. این کار، مدل22ویژگی اصلی را اعتبارسنجی کامل نمی‌کند.',
13:'اظهارنامه صادقانه آماده است، ولی نویسنده در2026-10-13 صریحاً تأیید نکرد و دستور داد ارسال انجام نشود. امضا، تأیید یا رسید ارسال ایجاد نشده است.'}
rows=list(csv.DictReader((old/'analysis/reviewer_response.csv').open(encoding='utf-8-sig')))
text='# پاسخ به14بند داوران در نسخه ادغام‌شده\n\nمرجع نهایی: integrated_revision_2026_10_13. مقاله چهارصفحه‌ای دو زبانه با17مرجع،8جدول و2شکل. 1464اجرای مطالعه اصلی و25برازش انتقال با پروتکل متفاوت گزارش می‌شوند.\n\n'
for i,row in enumerate(rows):
    row['action']=updates.get(i,row['action'])
    row['evidence']='manuscript_fa/en؛ analysis/delivery_quality.json؛ external_evidence_2026_10_13؛ unresolved_items_fa.md'
    if i in updates:row['location']='چکیده؛ بخش8، جدول8؛ بخش9 و10؛ فایل‌های ممیزی و وضعیت نهایی'
    text+=f'## {row["reviewer_item"]}\n\nایراد: {row["concern"]}\n\nاقدام و وضعیت: {row["action"]}\n\nمحل: {row["location"]}\n\nشاهد: {row["evidence"]}\n\n'
(p/'response_to_reviewers_fa.md').write_text(text,encoding='utf-8')
with (p/'analysis/reviewer_response.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
quality['reviewer_items']=len(rows)
(p/'analysis/delivery_quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'scientific_report_fa.md').write_text((old/'scientific_report_fa.md').read_text(encoding='utf-8')+'\n\n'+(e/'REPORT_FA.md').read_text(encoding='utf-8').replace('این گزارش مکمل نسخه extended_revision_2026_10_12 است؛ اعداد مقاله چهارصفحه‌ای قبلی را جایگزین نمی‌کند.','این مکمل اکنون در چکیده، بخش8، جدول8 و نتیجه‌گیری نسخه integrated_revision_2026_10_13 ادغام شده است.').replace('نسخه فعلی مقاله هنوز اعداد25اجرای مکمل را ندارد.','نسخه ادغام‌شده این اعداد را گزارش می‌کند.'),encoding='utf-8')
(p/'unresolved_items_fa.md').write_text('''# وضعیت واقعی پس از ادغام

ادغام مقاله،8جدول،17مرجع،پاسخ14بند،بازبینی Word/PDF و انتشار GitHub انجام شد. داده جدا و آزمون انتقال محدود25برازش موجود است. تعرفه منتشرشده خدمت و تحلیل75ماسک هزینه گروهی موجود است.

اعتبارسنجی کامل مدل اصلی22ویژگی انجام نشده است؛ مقصد فقط سه نام ویژگی مشترک دارد و معادل‌بودن استخراج/کالیبراسیون تأیید نشده است. برای مطالعه بالینی کامل، مرکز مستقل باید همان تعاریف اندازه‌گیری، معیار ورود/خروج، برچسب مرجع متخصص و هویت گروهی قابل‌ممیزی را ارائه کند. حذف ویژگی‌های ناموجود یا تغییر نام دلخواه، اعتبارسنجی همان مدل نیست.

هزینه مستقل استخراج ویژگی، زمان و خطر واقعی محل اجرا موجود نیست. تعرفه164.34USD برای خدمت مشترک است؛ هزینه ایران یا هزینه مستقل30ستون نیست. زمان پردازش فعلیِ جدول ازپیش‌محاسبه‌شده، زمان کسب اندازه‌گیری بالینی نیست و جایگزین آن نشده است.

32پیشوند در فایل Oxford در برابر31فرد متن UCI، نیازمند توضیح مالک داده است. بدون آن، هویت بالینی یا عدم اشتراک واقعی افراد بین مجموعه‌ها قابل تأیید نیست؛ جداسازی شناسه صرفاً جداسازی رکوردهای نام‌گذاری‌شده است.

ثبت پیشینی و لاگ‌های مفقود قدیمی قابل بازسازی معتبر از وب نیستند. پروتکل‌های عمومی فعلی تاریخچه جدیدند. بررسی پسینی فایل و هش، ثبت پیشینی گذشته محسوب نمی‌شود.

نویسنده اظهارنامه را تأیید نکرده و صریحاً گفته ارسال انجام نشود. مقاله به کنگره ارسال نشده است. شماره ثبت، رسید یا تأییدیه ساختگی وجود ندارد.

پیش‌نویس درخواست‌های مدرک در evidence_requests_drafts.md آماده است؛ به هیچ شخص یا مؤسسه ارسال نشده است.
''',encoding='utf-8')
(p/'evidence_requests_drafts.md').write_text('''# پیش‌نویس‌های درخواست مدرک — ارسال نشده

## مالک Oxford Parkinson

The UCI174 narrative states31people/23PD, but the supplied parkinsons.data contains195recordings with32name prefixes and24PD-labeled prefixes. Please clarify whether any prefixes denote the same participant, whether a participant was added/excluded between versions, and which pseudonymous group mapping should be used for subject-disjoint evaluation. A versioned erratum or pseudonymous mapping is sufficient; personal identifiers are neither needed nor requested.

## مرکز بالینی مستقل

برای ارزیابی مدل ثابت، داده‌ای مستقل با همان22تعریف ویژگی صوتی Oxford و مستندات روش استخراج/واحد/کالیبراسیون، شناسه مستعار فرد، برچسب مرجع متخصص، نحوه نمونه‌گیری و تأیید مجازبودن پژوهش لازم است. مدل، آستانه و پیش‌پردازش قبل از مشاهده برچسب مقصد تثبیت می‌شوند. داده دارای سه ویژگی مشترک، اعتبارسنجی کامل22ویژگی محسوب نمی‌شود.

## مالک فرایند کسب اندازه‌گیری

برای هر خدمت مشترک و ویژگی مشتق‌شده، هزینه پایه کسب، هزینه افزایشی محاسبه، واحد پول، سال/محل تعرفه، زمان کسب و خطر اندازه‌گیری را با سند تأیید کنید. هزینه کل خدمت باید یک‌بار محاسبه شود؛ global با technical/professional دوباره جمع نمی‌شود. هزینه پردازشCSV ازپیش‌محاسبه‌شده جایگزین زمان بالینی نیست.

## سوابق تاریخی نویسنده

اگر نسخه واقعی پروتکلِ تاریخ‌دار، لاگ اجرای اولیه، شکست‌ها، سخت‌افزار زمان اجرا یا ثبت پیشینی موجود است، اصل فایل با متادیتا ارائه شود. اگر ایجاد نشده یا در دسترس نیست، نبود آن به‌صورت محدودیت اعلام می‌شود و سند جدید با تاریخ گذشته ساخته نمی‌شود.
''',encoding='utf-8')
shutil.copy2(old/'author_declaration_draft_fa.md',p/'author_declaration_draft_fa.md')
(p/'AUTHOR_APPROVAL_STATUS.json').write_text(json.dumps({'date':'2026-10-13','approved':False,'submission_authorized':False,'user_reply':'هنوز تأیید نمی‌کنم؛ ارسال انجام نشود'},ensure_ascii=False,indent=2),encoding='utf-8')
(p/'SUBMISSION_STATUS_FA.md').write_text('''# آماده‌سازی ارسال

ارسال انجام نشده؛ نویسنده در2026-10-13 آن را منع کرده است. ورود، ثبت‌نام، بارگذاری یا پرداخت انجام نشد.

صفحه رسمی راهنما در2026-10-13 با HTTP200 خوانده و در sources ذخیره شد: https://baic.um.ac.ir/fa/home/Content/27 . فارسی یا انگلیسی و حداکثر4صفحه با قالب مخصوص کنگره الزام عمومی اعلام‌شده است؛ هرچهار PDF نسخه ادغام‌شده4صفحه‌اند. سیاست ابزار نگارش یا الزامات داخل حساب نویسنده از صفحه عمومی قابل تعیین نیستند و تأیید نشده‌اند.

برای ارسال بعدی، یکی از دو زبان و نام/ترتیب/وابستگی نویسندگان، محور، نسخه نهایی و اظهارنامه باید واقعاً تأیید شوند. در سامانه، مسیر ثبت‌نام همراه با ثبت مقاله و مشخصات نویسندگان طی می‌شود. وجود راهنمای عمومی، بازبودن پذیرش در حساب را اثبات نمی‌کند. نسخه انگلیسی و فارسی دو ترجمه یک مطالعه‌اند و نباید به‌عنوان دو مقاله مستقل ثبت شوند.
''',encoding='utf-8')
(p/'README_FA.md').write_text('''# آخرین نسخه ادغام‌شده

مرجع ادامه کار integrated_revision_2026_10_13 است. مقاله‌های فارسی و انگلیسی، Word/PDF/LaTeX،4صفحه،17مرجع،8جدول،2شکل و5معادله قابل‌ویرایش دارند. مکمل25برازش انتقال و هزینه مشترک اکنون در مقاله و پاسخ14بند ادغام شده است. همه1464اجرای اصلی و25برازش مکمل جداگانه قابل ممیزی‌اند؛ از تجمیع آماری آن‌ها پرهیز کنید.

کد و همه خروجی‌ها در مخزن عمومی هستند. فایل‌های قبلی برای تاریخچه حفظ شده‌اند. وضعیت شواهد حل‌نشده و منع ارسال نویسنده در unresolved_items_fa.md و SUBMISSION_STATUS_FA.md روشن است. این نسخه هیچ ادعای تأیید بالینی کامل یا امضای نویسنده ندارد.
''',encoding='utf-8')
reference_file=p/'sources/reference_verification.csv'
with reference_file.open(encoding='utf-8',newline='') as f:
    reference_rows=list(csv.reader(f))
with reference_file.open('w',encoding='utf-8',newline='') as f:
    csv.writer(f).writerows(row for row in reference_rows if not row or row[0] not in ['16','17'])
with reference_file.open('a',encoding='utf-8') as f:
    f.write('16,"https://doi.org/10.24432/C5701F",2026-10-13,"Official UCI dataset verified"\n17,"https://dphhs.mt.gov/assets/publichealth/Cancer/MCCP2025FeeSchedule.pdf",2026-10-13,"Official published service fee, effective 2024-06-30; not current local marginal cost"\n')
shutil.copy2(r/'build_integrated_documents.py',p/'sources/build_integrated_documents.py')
shutil.copy2(Path(__file__),p/'sources/finalize_integrated_revision.py')
manifest=[{'path':f.relative_to(p).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in p.rglob('*') if f.is_file() and f.name!='SHA256_MANIFEST.json' and f.suffix not in ['.aux','.log','.out']]
(p/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
if public!=r:
    shutil.copytree(p,public/p.name,dirs_exist_ok=True)
    for name in ['build_integrated_documents.py','finalize_integrated_revision.py']:shutil.copy2(r/name,public/name)
readme=public/'README.md'
s=readme.read_text(encoding='utf-8')
section='\n## Integrated manuscript revision — 2026-10-13\n\nLatest authoritative manuscript: integrated_revision_2026_10_13. Both languages have four-page Word/PDF/LaTeX versions,17references,8tables and2figures. Transfer and shared-service-cost findings are integrated into the abstract, discussion,Table8,conclusion and14reviewer responses. See unresolved_items_fa.md and SUBMISSION_STATUS_FA.md: author approval was explicitly withheld and no conference submission occurred. The1464original runs and25transfer fits retain distinct protocols.\n'
pattern=r'\n## Integrated manuscript revision — 2026-10-13\n.*?(?=\n## |\Z)'
s=re.sub(pattern,lambda _:section,s,flags=re.S) if re.search(pattern,s,flags=re.S) else s+section
readme.write_text(s,encoding='utf-8')
guide=public/'CONTINUE_WORK_FA.md'
guide_text=guide.read_text(encoding='utf-8')
guide_text=guide_text.replace('آخرین نسخه معتبر: extended_revision_2026_10_12.','آخرین نسخه معتبر: integrated_revision_2026_10_13؛ extended_revision_2026_10_12 نسخه تاریخی است.')
guide_text=guide_text.replace('ساخت سند با build_extended_documents.py انجام می‌شود','ساخت سند با build_integrated_documents.py انجام می‌شود')
guide.write_text(guide_text,encoding='utf-8')
archive=r/'CostStableEHOA_Integrated_Rebuild.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in public.rglob('*'):
        if f.is_file() and not f.match('CostStableEHOA_Integrated_Rebuild*.zip') and not any(x in f.relative_to(public).parts for x in ['.git','__pycache__']) and f.suffix not in ['.aux','.log','.out']:z.write(f,f.relative_to(public))
with zipfile.ZipFile(archive) as z:
    if z.testzip():raise ValueError('ZIP corruption')
print(json.dumps({'quality':quality,'archive_bytes':archive.stat().st_size},ensure_ascii=False))
