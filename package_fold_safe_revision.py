from pathlib import Path
import json,csv,zipfile,hashlib,shutil,re
from pypdf import PdfReader
from xml.etree import ElementTree as ET

R=Path(__file__).resolve().parent
P=R/'fold_safe_revision_2026_10_12'
OLD=R/'revision_2026_10_12'
audit=json.loads((P/'analysis/audit_summary.json').read_text(encoding='utf-8'))
content=json.loads((P/'sources/manuscript_content.json').read_text(encoding='utf-8'))
pages={str(f.relative_to(P)):len(PdfReader(f).pages) for f in [P/'manuscript_fa.pdf',P/'manuscript_en.pdf',P/'qa/word_fa.pdf',P/'qa/word_en.pdf']}
if any(count>4 for count in pages.values()):raise ValueError('Page limit exceeded')
if audit['completed_runs']!=774 or audit['outer_constrained_budget_violations'] or audit['smote_dimension_mismatches'] or audit['inner_utility_training_overlap_with_inner_validation_or_outer_test']:raise ValueError('Scientific audit not clean')
old=list(csv.DictReader((OLD/'analysis/reviewer_response.csv').open(encoding='utf-8-sig')))
actions=[
('سهم به مقایسه تعمیر در پایپ‌لاین مستقل در سطح تقسیم محدود شد. نتایج 774 اجرای تازه از آرشیو قبلی جدا هستند. عنوان و چکیده اعداد تازه را گزارش می‌کنند.','عنوان، چکیده، بخش‌های 1 و 7','sources/manuscript_content.json؛ analysis/primary_overall.csv'),
('فریدمن روی ده بلوک واقعی دیتاست، آماره، df، p، رتبه‌ها و هولم گزارش شد؛ اثر زوجی و فاصله bootstrap هم موجود است.','بخش‌های 6 و 7؛ جدول 6','analysis/primary_friedman.csv؛ primary_ranks.csv؛ primary_paired.csv'),
('هر 7 جدول و 2 شکل اصلی از داده تازه ساخته شدند؛ فرمت برداری و TIFF چاپی و همه صفحه‌های خروجی بازبینی شدند.','جدول‌های 1 تا 7؛ شکل‌های 1 و 2','figures؛ analysis؛ qa'),
('15 مرجع مرتبط با مرور پزشکی، هزینه، پایداری، MI، SMOTE، اعتبارسنجی و آثار 2021 تا 2026 حفظ و در متن استفاده شدند.','بخش 2 و مراجع','references_for_submission.txt؛ sources/reference_verification.csv'),
('انتساب Jagdhuber به BMC Bioinformatics 21:26 (2020) و DOI صحیح حفظ شد؛ مرجع شماره 1 است.','مراجع، شماره 1','https://doi.org/10.1186/s12859-020-3361-9'),
('جدول ده دیتاست با داده استفاده‌شده واقعی به‌روز شد. Steel اکنون 27 ویژگی و 7 کلاس دارد؛ Parkinson در هر دو سطح گروهی است.','بخش 5؛ جدول 3','data/corrected_steel.csv؛ data/parkinson_subject_mapping.csv'),
('پروتکل، سه بذر، تنظیم‌ها، محیط، زمان کامل و هش کد پیش از اجرا به‌صورت محلی ثبت شدند؛ ثبت عمومی مستقل ادعا نشده است.','بخش 6؛ جدول 4','protocol.json؛ frozen_sha256.json؛ environment.json'),
('مطالعه سرطان پستان با 9 اجرای تازه هر روش، ویژگی‌های منتخب و داده‌های کامل ماسک به‌روز شد؛ هزینه واقعی و اعتبار بالینی هنوز موجود نیستند.','بخش 8؛ جدول 7؛ شکل 2','analysis/breast_cancer_case.csv؛ breast_selection_frequencies.csv'),
('متن دو زبان روشن شد؛ کاندید خام، ماسک تعمیرشده هر تقسیم و ماسک نهایی جدا تعریف شدند.','بخش‌های 1 تا 10','manuscript_fa؛ manuscript_en'),
('ارتباط با محور رسمی سیستم‌های هوشمند تشخیص بیماری حفظ شد؛ ادعای شناختی یا بالینی بیش از شواهد نداریم.','بخش 8','https://baic.um.ac.ir/fa/home/Content/12'),
('کل متن با روش و اعداد تازه هماهنگ شد؛ خروجی قدیمی در این نسخه استفاده نشده و با نتایج تازه تجمیع نشده است.','تمام مقاله','sources/manuscript_content.json؛ scientific_report_fa.md'),
('بودجه سخت، هزینه مصنوعی، پایداری 9 ماسک وابسته، clipping و مکمل جاکارد روشن شدند؛ تحلیل بودجه 15/30/50% اجرا شد.','بخش‌های 4 و 7','analysis/all_dataset_means.csv؛ sensitivity_dataset_means.csv'),
('معادله و جست‌وجوی EHOA حفظ شد؛ سودمندی هر تقسیم فقط از آموزش همان تقسیم است. SMOTE در همه کاندیدها و طبقه‌بند نهایی روی ابعاد منتخب اجرا شد.','بخش‌های 3 و 4؛ معادله برازندگی','proposed/fold_safe_ehoa.py؛ analysis/run_audit.csv؛ jobs/*/split_provenance.npz'),
('متن، کد و نتایج قابل‌ممیزی‌اند و مسئولیت تأیید نهایی با نویسنده است. ادعای استفاده‌نکردن یا اظهارنامه خلاف واقع افزوده نشد؛ سیاست نهایی سامانه باید رعایت شود.','تأیید نویسنده و فرم ارسال','کد، نتایج، گزارش ممیزی و راهنمای رسمی ارسال')]
responses=[]
text='# پاسخ 14 بند داوران؛ نسخه پایپ‌لاین اصلاح‌شده\n\nاین نسخه شامل 774 اجرای واقعاً تازه است. آرشیو قبلی حفظ شده و نتایج آن با این اجراها مخلوط نشده‌اند. موارد نیازمند داده یا تأیید بیرونی همچنان صریح گزارش می‌شوند.\n\n'
for row,(action,loc,evidence) in zip(old,actions):
    responses.append([row['reviewer_item'],row['concern'],action,loc,evidence])
    text+=f'## {row["reviewer_item"]}\n\n**ایراد:** {row["concern"]}\n\n**اقدام انجام‌شده:** {action}\n\n**محل:** {loc}\n\n**شاهد:** {evidence}\n\n'
(P/'response_to_reviewers_fa.md').write_text(text,encoding='utf-8')
with (P/'analysis/reviewer_response.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(['reviewer_item','concern','action','location','evidence']);w.writerows(responses)
(P/'unresolved_items_fa.md').write_text('''# وضعیت مشکلات پس از اجرای تازه

رفع‌شده در این نسخه:

- محاسبه سودمندی با برچسب اعتبارسنجی درونی: سودمندی هر تقسیم از آموزش همان تقسیم محاسبه شد.
- SMOTE بر اساس همه ابعاد: اکنون همه کاندیدها و مدل نهایی فقط ابعاد منتخب را استفاده می‌کنند.
- تایمر ناقص: زمان برازش شامل سودمندی و زمان سرتاسری شامل طبقه‌بند نهایی ثبت شد.
- MI پیوسته روی ویژگی‌های درجه‌ای Dermatology: 33 ویژگی گسسته و سن پیوسته تعریف شدند.
- حساسیت بررسی‌نشده: بودجه 15/30/50 درصد، R=4/8/16 و lambda=0/1/2 روی سه دیتاست پزشکی اجرا شد.
- نشت هدف Steel: 27 پیش‌بین و 7 کلاس استفاده شد.
- هم‌پوشانی ضبط Parkinson: تقسیم بیرونی و درونی بر اساس پیشوند فرد، بدون هم‌پوشانی است.

هنوز نیازمند داده یا شواهد بیشتر:

- قیمت/زمان/خطر واقعی و مدل گروهی اندازه‌گیری از مالک داده؛ هزینه مصنوعی، قیمت پزشکی نیست.
- داده بالینی مستقل و همکاری متخصص برای اعتبارسنجی بیرونی یا آینده‌نگر.
- تأیید مستقل هویت 32 پیشوند Parkinson در برابر 31 فرد اعلام‌شده UCI؛ تقسیم گروهی، هویت بالینی را تأیید نمی‌کند.
- مخزن عمومی واقعی و مجوز انتشار؛ بسته محلی منتشرشدن عمومی محسوب نمی‌شود.
- اطلاعات تاریخی ثبت پیشینی، سخت‌افزار و لاگ شکست‌های قبلی؛ این موارد را نمی‌توان برای گذشته ایجاد کرد.
- تأیید نویسنده برای اظهارنامه نهایی مطابق سیاست کنگره.

محدودیت‌های پژوهشی باقی‌مانده:

- تحلیل حساسیت یک عامل در هر مرحله و روی سه دیتاست است؛ تمام تعامل‌ها را پوشش نمی‌دهد.
- سه بذر و جست‌وجوی 8×10، آزمایش همه تنظیم‌ها یا تضمین همگرایی نیست.
- MI حاشیه‌ای و امتیاز میانگین منهای SD، تضمین پوشش اطمینان یا کنترل انتخاب کاذب ندارد.
- ماسک‌های تکرارشده وابسته‌اند؛ دیتاست واحد تحلیل آماری است.
- نتیجه معنادار یا غیرمعنادار باید با اصلاح چندگانگی گزارش شود؛ اصلاح روش، تضمین برتری یا پذیرش مقاله نیست.
''',encoding='utf-8')
(P/'data').mkdir(exist_ok=True)
shutil.copy2(OLD/'corrected_experiments/steel_27_features_7_classes.csv',P/'data/corrected_steel.csv')
shutil.copy2(OLD/'corrected_experiments/parkinson_subject_mapping.csv',P/'data/parkinson_subject_mapping.csv')
shutil.copy2(OLD/'analysis/datasets.csv',P/'data/source_metadata_archived.csv')
shutil.copy2(OLD/'sources/parkinsons_uci.zip',P/'data/parkinsons_uci.zip')
refs=[b for page in content['pages'] for b in page if b['kind']=='ref']
allbody=[b for page in content['pages'] for b in page if b['kind']!='ref']
cited=set()
for b in allbody:
    for group in re.findall(r'\[([0-9]+(?:,[0-9]+)*)\]',b.get('en','')+' '+str(b.get('rows',[]))):cited.update(map(int,group.split(',')))
quality=dict(page_counts=pages,references=len(refs),uncited_references=sorted(set(range(1,len(refs)+1))-cited),tables=sum(b['kind']=='table' for b in allbody),figures=sum(b['kind']=='fig' for b in allbody),reviewer_items=len(responses),visual_review='All final manuscript and Word-render pages inspected',scientific_audit=audit)
for lang in ['en','fa']:
    with zipfile.ZipFile(P/f'manuscript_{lang}.docx') as z:root=ET.fromstring(z.read('word/document.xml'))
    quality['native_equations_'+lang]=len(root.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath'))
(P/'analysis/delivery_quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
scripts=['run_fold_safe_revision.py','analyze_fold_safe_revision.py','build_fold_safe_documents.py','draw_fold_safe_figures.py','package_fold_safe_revision.py','build_revision_documents.py','ehoa.py','utils.py']
for name in scripts:shutil.copy2(R/name,P/'sources'/name)
shutil.copy2(T:=OLD/'sources/congress_template.docx',P/'sources/congress_template.docx')
(P/'README_FA.md').write_text('''# بسته تازه اصلاح پایپ‌لاین

نسخه اصلی مقاله، این پوشه است: manuscript_fa و manuscript_en در قالب Word/PDF/LaTeX. همه خروجی‌های چاپی حداکثر چهار صفحه دارند. نتایج این مقاله از 774 اجرای تازه هستند: 450 اصلی و 324 حساسیت. آنها را با نتایج آرشیو قبلی به‌عنوان یک پروتکل یکسان ترکیب نکنید.

scientific_report_fa.md تحلیل کامل؛ response_to_reviewers_fa.md پاسخ 14 بند؛ unresolved_items_fa.md وضعیت محدودیت‌ها؛ analysis/audit_summary.json ممیزی واقعی و jobs شامل خروجی هر اجراست. کد اصلی آرشیوی تغییر نکرده است. اصلاحات در proposed/fold_safe_ehoa.py جدا هستند.

protocol.json و frozen_sha256.json پیش از اجرای تازه ثبت شدند. ثبت محلی با اطلاع از نتایج قبلی، ثبت پیشینی مستقل عمومی نیست. نسخه محیط و زمان کامل ثبت شده‌اند. هزینه پزشکی واقعی و داده بالینی بیرونی در اختیار نیستند.

بازتولید از ریشه reproducibility: ابتدا run_fold_safe_revision.py، سپس analyze_fold_safe_revision.py. بازتولید مقاله به فونت‌های Times New Roman/B Nazanin، XeLaTeX و python-docx نیاز دارد. خروجی آماده برای استفاده موجود است؛ کامپایل مجدد ضروری نیست. هیچ آزمون واحد نرم‌افزاری اجرا نشده؛ اجرای پژوهش، بازمحاسبه و ممیزی خروجی واقعی انجام شدند.
''',encoding='utf-8')
manifest=[f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.relative_to(P).as_posix()}' for file in P.rglob('*') if file.is_file() and file.name!='SHA256SUMS.txt' and file.suffix not in ['.aux','.out','.log']]
(P/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
dest=R/'CostStableEHOA_BAIC2026_FoldSafe_Revised.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in P.rglob('*'):
        if file.is_file() and file.suffix not in ['.aux','.out','.log']:z.write(file,Path(P.name)/file.relative_to(P))
    for name in scripts+['requirements.txt']:z.write(R/name,Path('reproducibility')/name)
    for folder in ['proposed','data']:
        for file in (R/folder).rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts and file.name not in ['arrhythmia.csv','musk_v1.csv']:z.write(file,Path('reproducibility')/file.relative_to(R))
    for name in ['corrected_experiments/steel_27_features_7_classes.csv','corrected_experiments/parkinson_subject_mapping.csv','analysis/datasets.csv','sources/congress_template.docx','sources/manuscript_content.json','references_for_submission.txt','sources/reference_verification.csv','baic2026_header.png']:
        z.write(OLD/name,Path('reproducibility/revision_2026_10_12')/name)
    for name in ['protocol.json','frozen_sha256.json','runs.csv']:
        z.write(P/name,Path('reproducibility')/P.name/name)
print(json.dumps(quality,ensure_ascii=False))
print('Archive:',dest,'bytes:',dest.stat().st_size)
