from pathlib import Path
import json,csv,zipfile,hashlib,shutil
from pypdf import PdfReader

R=Path(__file__).resolve().parent
P=R/'extended_revision_2026_10_12'
OLD=R/'fold_safe_revision_2026_10_12'
PUBLIC=R/'public_coststable_ehoa'
audit=json.loads((P/'analysis/audit_summary.json').read_text(encoding='utf-8'))
if audit['completed_extension_runs']!=690 or audit['final_constrained_budget_violations'] or audit['inner_train_validation_outer_test_overlap'] or audit['smote_dimension_mismatches']:raise ValueError('Extension audit is not complete and clean')
pages={str(f.relative_to(P)):len(PdfReader(f).pages) for f in [P/'manuscript_fa.pdf',P/'manuscript_en.pdf',P/'qa/word_fa.pdf',P/'qa/word_en.pdf']}
if any(n>4 for n in pages.values()):raise ValueError('Article page limit exceeded')
old=list(csv.DictReader((OLD/'analysis/reviewer_response.csv').open(encoding='utf-8-sig')))
updates={0:'نسخه نهایی از تحلیل اصلی پنج‌بذری 750 اجرا، طرح کامل تعامل روی ده دیتاست و مقایسه جست‌وجوی بزرگ‌تر استفاده می‌کند. ادعای برتری فقط براساس آزمون اصلاح‌شده قابل طرح است.',1:'آماره فریدمن، df=4، رتبه و p روی ده بلوک دیتاست و مقایسه‌های زوجی هولم از تحلیل پنج‌بذری به‌روز شدند. پانزده ماسک وابسته، پانزده مشاهده مستقل نیستند.',2:'7 جدول، 2 شکل و 5 معادله Word با اعداد تازه هماهنگ شدند؛ تمام PDF و چاپ Word حداکثر چهار صفحه‌اند و همه صفحه‌ها بازبینی شدند.',3:'15 مرجع مرتبط حفظ شدند؛ DOI و منبع درست Hill-Valley (UCI166 و OpenML1479) تصحیح شدند.',5:'جدول داده‌ها شامل Steel اصلاح‌شده 27 ویژگی/7 کلاس و Parkinson گروهی است. لینک Hill-Valley تصحیح شد؛ داده عددی آن تغییر نکرد.',6:'پروتکل تکمیلی، هش کد و طرح 690 اجرای جدید پیش از اجرا در مخزن عمومی ثبت شدند. نسخه محیط و سخت‌افزار جاری موجود است؛ ثبت تاریخی مفقود جعل نشد.',7:'مطالعه سرطان پستان با 15 ماسک، حساسیت بدخیم و ویژگی خوش‌خیم صریح، به‌روز شد. قیمت واقعی و اعتبار بالینی بیرونی ادعا نشده‌اند.',11:'بودجه، پایداری وابسته و واحد دیتاست روشن‌اند. تعامل بودجه/R/lambda با طرح کامل2×2×2 روی ده دیتاست بررسی شد؛ نه تمام فضای پیوسته.',12:'پایپ‌لاین در سطح تقسیم مستقل است. جست‌وجوی16×20 در برابر8×10 روی تقسیم و بذر مشترک اجرا شد؛ تضمین همگرایی ادعا نشد.',13:'اظهارنامه صادقانه بدون نام تجاری به‌صورت پیش‌نویس آماده شد؛ عدم استفاده یا امضای نویسنده جعل نشد. الزام فرم نهایی ارسال باید رعایت شود.'}
response='# پاسخ نهایی 14 بند داوران\n\nمخزن عمومی: https://github.com/Amirgh23/coststable-ehoa. 690 اجرای تکمیلی و 774 اجرای پیشین پایپ‌لاین مستقل، جمعاً1464 اجرا هستند. دسته اصلی پنج‌بذری750 اجرا دارد. پروتکل گسترش پیش از اجرای آن در ثبت72c87b6 منتشر شد؛ ثبت پیشینی آزمایش گذشته ادعا نمی‌شود.\n\n'
records=[]
for i,row in enumerate(old):
    action=updates.get(i,row['action'])
    evidence='analysis؛ scientific_report_fa.md؛ manuscript_fa/en؛ public_repository_manifest.json'
    response+=f'## {row["reviewer_item"]}\n\n**ایراد:** {row["concern"]}\n\n**اقدام:** {action}\n\n**محل:** {row["location"]}\n\n**شاهد:** {evidence}\n\n'
    records.append([row['reviewer_item'],row['concern'],action,row['location'],evidence])
(P/'response_to_reviewers_fa.md').write_text(response,encoding='utf-8')
with (P/'analysis/reviewer_response.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(['reviewer_item','concern','action','location','evidence']);w.writerows(records)
(P/'unresolved_items_fa.md').write_text('''# وضعیت نهایی مشکلات

رفع‌شده یا تکمیل‌شده با شواهد:

- سودمندی آموزش همان تقسیم، SMOTE روی ابعاد منتخب، MI گسسته Dermatology، زمان کامل و ممیزی ماسک‌ها.
- Steel اصلاح‌شده و تقسیم درونی/بیرونی گروهی Parkinson بدون هم‌پوشانی پیشوندها.
- سه بذر به پنج بذر اصلی افزایش یافت؛ 750 اجرای اصلی موجود است.
- طرح کامل2×2×2 تعامل بودجه/R/lambda روی هر ده دیتاست اجرا شد؛ اثر اصلی، دوتایی و سه‌تایی گزارش شد.
- جست‌وجوی16×20 با8×10 برای پنج روش و ده دیتاست مقایسه شد.
- مخزن عمومی واقعی با مجوز داده‌های CC BY4، انتساب، کد و خروجی‌ها ایجاد شد.
- پروتکل گسترش و هش کد پیش از اجرای690 آزمایش تکمیلی به‌صورت عمومی ثبت شد.
- ارجاع نادرست Hill-Valley اصلاح شد: UCI166، نه147؛ snapshot عددی تغییر نکرد.
- پیش‌نویس اظهارنامه صادقانه نویسنده آماده شد.

نیازمند داده یا تأیید بیرونی:

- فایل قیمت/زمان/خطر واقعی و گروه‌های کسب اندازه‌گیری در پوشه معرفی‌شده پیدا نشد؛ هزینه مصنوعی جایگزین قیمت پزشکی نیست.
- داده بالینی بیرونی مستقل و همکاری متخصص موجود نیست؛ داده عمومی استفاده‌شده دوباره «بیرونی مستقل» نام‌گذاری نشد.
- هویت بالینی32 پیشوند Parkinson در برابر31 فرد متن UCI قابل اثبات از این فایل‌ها نیست؛ مالک داده باید تأیید کند.
- ثبت پیشینی، سخت‌افزار و لاگ شکست آزمایش‌های قدیمی را نمی‌توان برای گذشته ایجاد کرد؛ شواهد جاری جدا ثبت شدند.
- اظهارنامه نهایی و امضای واقعی نویسنده در سامانه ارسال، مسئولیت نویسنده است.

محدودیت‌های ذاتی یا دامنه مطالعه:

- فاکتوریل دو سطح انتهایی و یک بذر دارد؛ همه سطوح پیوسته یا تغییرپذیری تصادفی تعامل‌ها را پوشش نمی‌دهد.
- مقایسه جست‌وجوی بزرگ‌تر یک بذر دارد؛ افزایش بودجه محاسباتی، اثبات بهینه سراسری یا همگرایی نیست.
- MI منهای SD ابتکاری است و تضمین پوشش اطمینان یا کنترل انتخاب کاذب ندارد؛ چنین تضمینی در مقاله ادعا نمی‌شود.
- ماسک‌ها به‌دلیل اشتراک داده وابسته‌اند؛ دیتاست واحد استنباط است.
- زمان‌های دسته‌های سه/شش‌پردازشی، بنچمارک کنترل‌شده سرعت نیستند.
- اصلاح روش و شفافیت، نتیجه معنادار یا پذیرش مقاله را تضمین نمی‌کند.
''',encoding='utf-8')
scripts=['run_extended_revision.py','analyze_extended_revision.py','build_extended_documents.py','draw_extended_figures.py','package_extended_revision.py','run_fold_safe_revision.py','analyze_fold_safe_revision.py','build_fold_safe_documents.py','draw_fold_safe_figures.py','build_revision_documents.py','ehoa.py','utils.py']
for name in scripts:shutil.copy2(R/name,P/'sources'/name)
shutil.copy2(R/'revision_2026_10_12/sources/congress_template.docx',P/'sources/congress_template.docx')
quality=dict(page_counts=pages,reviewer_items=14,references=15,tables=7,figures=2,visual_review='All final pages of both articles and both Word renders inspected',scientific_audit=audit,public_repo='https://github.com/Amirgh23/coststable-ehoa',remaining='Real tariffs, independent clinical validation, clinical group identity, missing old historical records and human final signoff')
(P/'analysis/delivery_quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'README_FA.md').write_text('''# نسخه تکمیل‌شده با مخزن عمومی

مقاله فارسی و انگلیسی در سه قالب PDF/Word/LaTeX، حداکثر چهار صفحه، در این پوشه‌اند. پاسخ14 بند، گزارش علمی و وضعیت باقی‌مانده‌ها جدا هستند. نتایج پنج‌بذری750 اجرا، فاکتوریل240 اجرا و جست‌وجوی بزرگ‌تر150 اجرا را جدا تفسیر کنید. با حساسیت قبلی، کل پایپ‌لاین مستقل1464 اجرا دارد.

مخزن عمومی: https://github.com/Amirgh23/coststable-ehoa. پروتکل تکمیلی در ثبت72c87b6 پیش از اجرا منتشر شد. اطلاعات خصوصی، متن داوران و پیش‌نویس اظهارنامه به مخزن عمومی ارسال نشده‌اند. هزینه واقعی یا اعتبار بالینی بیرونی موجود نیست.

برای بازتولید، از ریشه reproducibility ابتدا run_fold_safe_revision.py، سپس run_extended_revision.py و تحلیل‌های متناظر را اجرا کنید. ورودی‌ها، نسخه محیط و هش‌ها مشخص‌اند. مصارف سرعت به‌دلیل هم‌زمانی متفاوت فقط زمان ثبت‌شده‌اند. هیچ آزمون واحد نرم‌افزاری اجرا نشد؛ آزمایش واقعی، بازحساب و ممیزی علمی انجام شدند.
''',encoding='utf-8')
for folder,names in [('extended_revision_2026_10_12',['protocol.json','frozen_sha256.json','publication.json','runs.csv','analysis/primary_five_seed_runs.csv','analysis/primary_dataset_means.csv','analysis/primary_overall.csv','analysis/primary_friedman.csv','analysis/primary_ranks.csv','analysis/primary_paired.csv','analysis/factorial_cells.csv','analysis/factorial_dataset_effects.csv','analysis/factorial_effects.csv','analysis/search_profile_dataset_means.csv','analysis/search_profile_effects.csv','analysis/audit_summary.json','analysis/fresh_dataset_specifications.csv','current_hardware.json'])]:
    for name in names:
        target=PUBLIC/folder/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(R/folder/name,target)
for name in ['analyze_extended_revision.py']:shutil.copy2(R/name,PUBLIC/name)
for base in [OLD,P]:
    for file in base.rglob('mask.npy'):
        target=PUBLIC/file.relative_to(R)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(file,target)
for filename in ['primary_dataset_means.csv','primary_ranks.csv','breast_cancer_case.csv','breast_class_specific_metrics.csv','breast_selection_frequencies.csv']:
    target=PUBLIC/'fold_safe_revision_2026_10_12/analysis'/filename
    shutil.copy2(OLD/'analysis'/filename,target)
manifest=[dict(path=str(file.relative_to(PUBLIC)).replace('\\','/'),sha256=hashlib.sha256(file.read_bytes()).hexdigest()) for file in PUBLIC.rglob('*') if file.is_file() and '.git' not in file.parts]
(P/'public_repository_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
lines=[f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.relative_to(P).as_posix()}' for file in P.rglob('*') if file.is_file() and file.name!='SHA256SUMS.txt' and file.suffix not in ['.aux','.log','.out']]
(P/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
dest=R/'CostStableEHOA_BAIC2026_Extended_Public.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in P.rglob('*'):
        if file.is_file() and file.suffix not in ['.aux','.log','.out']:z.write(file,Path(P.name)/file.relative_to(P))
    for base in [OLD]:
        for file in base.rglob('*'):
            if file.is_file() and 'jobs' in file.parts:z.write(file,file.relative_to(R))
    for file in PUBLIC.rglob('*'):
        if file.is_file() and '.git' not in file.parts:z.write(file,Path('reproducibility')/file.relative_to(PUBLIC))
print(json.dumps(quality,ensure_ascii=False))
print('Local delivery:',dest,'bytes:',dest.stat().st_size)
