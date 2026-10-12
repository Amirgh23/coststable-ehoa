from pathlib import Path
import zipfile,json,re,hashlib,csv,subprocess
from xml.etree import ElementTree as ET
from pypdf import PdfReader

R=Path(__file__).resolve().parent;P=R/'revision_2026_10_12'
content=json.loads((P/'sources/manuscript_content.json').read_text(encoding='utf-8'))
inspection=[]
for file in [R/'مقاله_آماده_ارسال_کنگره.docx',R/'CostStableEHOA_English_BAIC2026_Native.docx',R/'CostStableEHOA_English_BAIC2026_Compact.docx',P/'manuscript_en.docx',P/'manuscript_fa.docx']:
    z=zipfile.ZipFile(file);root=ET.fromstring(z.read('word/document.xml'));txt=' '.join(t.text or '' for t in root.iter() if t.tag.endswith('}t'))
    inspection.append(dict(file=file.name,paragraphs=len(root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')),native_math_count=len(root.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath')),table_count=len(root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl')),latex_command_fragments=re.findall(r'\\(?:frac|sum|alpha|epsilon|bar|sigma|mathbf)\b',txt),text_length=len(txt)))
(P/'analysis/docx_conversion_audit.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2),encoding='utf-8')
quality=dict(pdf_pages={x.name:len(PdfReader(x).pages) for x in [P/'manuscript_en.pdf',P/'manuscript_fa.pdf',P/'qa/word_en.pdf',P/'qa/word_fa.pdf']},abstract_word_counts={lang:len(content['abstract'][lang].split()) for lang in ['en','fa']},visual_review='Every page of each final manuscript and both native Word renders inspected; see qa PNGs',word_equations='Native editable OMML; multi-line displays; text and tables retained',format='A4, official template header, margins 19/25.4/16/16 mm, two columns with 6 mm gap, no page numbers',font_metric_warning='Bidi multicol emits two missing p warnings per Persian page from invisible depth/phantom probes in multicol-xetex-bidi.def; visible Latin text is rendered with Times New Roman',originals_preserved=True,automated_test_suites_run=False)
(P/'analysis/delivery_quality.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
readme='''# بسته بازنگری CostStableEHOA برای BAIC2026

مقاله‌های فارسی و انگلیسی در manuscript_fa و manuscript_en به سه قالب TEX، PDF و DOCX موجودند. همه PDFها و خروجی چاپ Word حداکثر چهار صفحه دارند. Word متن، جدول و معادله بومی قابل‌ویرایش دارد؛ شکست ستون‌ها ممکن است با PDF متفاوت باشد.

response_to_reviewers_fa.md پاسخ 14 بند دو داور است. supplement/scientific_supplement_fa.md داده‌ها، پارامترها، مطالعات مرتبط، آزمون‌های آماری، تطبیق ادعا و موارد حل‌نشده را دارد. references_for_submission.txt هر منبع را در یک خط بدون شماره برای سامانه نگه می‌دارد.

سه مجموعه نتیجه را مخلوط نکنید:

- آرشیو اولیه ده‌دیتاستی: 300 اجرا؛ دو دیتاست ایراد داده/تقسیم دارند. فقط ممیزی و تاریخچه.
- تحلیل اصلی گذشته‌نگر هشت‌دیتاستی: 240 اجرای آرشیوی واجد شرایط؛ فایل‌های analysis/eligible_*.
- تحلیل حساسیت اصلاح‌شده ده‌دیتاستی: 240 اجرای معتبر قدیمی + 60 اجرای تازه اکتشافی؛ فایل‌های analysis/corrected10_* و corrected_experiments.

60 اجرای تازه، نشت هدف Steel را با حذف شش نشانگر کلاس و هدف هفت‌کلاسه رفع کرد. در Parkinsons، همه ردیف‌ها به فایل اصلی UCI تطبیق یافتند و تقسیم‌های بیرونی و درونی روی پیشوند شناسه فرد، بدون هم‌پوشانی‌اند. متن UCI تعداد 31 فرد را می‌گوید اما فایل 32 پیشوند متفاوت دارد؛ تأیید مستقل هویت گروه‌ها هنوز لازم است. هیچ ادعای بالینی یا هزینه پولی واقعی نمی‌شود.

برتری عمومی دقت یا پایداری بر همه تعمیرها تأیید نشده است. هزینه مصنوعی و شاخص overlap صرفاً خروجی محاسباتی‌اند. مسئولیت تأیید علمی و نگارش نهایی با نویسنده است. در راهنمای عمومی بررسی‌شده الزام نام ابزار نگارش دیده نشد؛ اگر فرم ارسال اظهارنامه می‌خواهد، باید براساس واقعیت تکمیل شود. ادعای عدم استفاده افزوده نشده است.

کد، داده یا فایل‌ها در سرویس عمومی منتشر نشده‌اند. آرشیو محلی شامل داده عمومی برای بازتولید است و انتشار عمومی محسوب نمی‌شود. فایل اصلی دست‌نخورده است.

بازتولید از ریشه پوشه reproducibility بعد از استخراج ZIP: revision_audit.py تحلیل آرشیو؛ revision_corrected_experiments.py اجرای 60 آزمایش اصلاح‌شده؛ revision_corrected_analysis.py تحلیل حساسیت؛ revision_figures.py رسم. محیط اجرا باید وابستگی‌های requirements.txt را داشته باشد. هیچ مجموعه آزمون نرم‌افزاری اجرا نشده است؛ محاسبات علمی، ممیزی ماسک و بازبینی تصویری انجام شده‌اند.

منابع LaTeX با XeLaTeX و فونت‌های Times New Roman و B Nazanin کامپایل می‌شوند؛ تصویر سربرگ و figures را کنار TEX نگه دارید. معادلات Word بومی‌اند و تصاویر چاپی TIFF هستند.
'''
(P/'README_FA.md').write_text(readme,encoding='utf-8')
scripts=['revision_audit.py','revision_corrected_experiments.py','revision_corrected_analysis.py','revision_figures.py','build_revision_documents.py','build_revision_supplement.py','revision_delivery_verification.py','revision_package.py']
for ext in ['pdf','svg','png']:
    old=P/f'figures/repair_comparison.{ext}'
    if old.exists():old.replace(P/f'sources/legacy_full10_comparison.{ext}')
for f in scripts:(P/'sources'/f).write_bytes((R/f).read_bytes())
for stem,pdf in [('final_manuscript_en',P/'manuscript_en.pdf'),('final_manuscript_fa',P/'manuscript_fa.pdf'),('final_word_en',P/'qa/word_en.pdf'),('final_word_fa',P/'qa/word_fa.pdf')]:
    count=len(PdfReader(pdf).pages)
    for file in (P/'qa').glob(stem+'-*.png'):
        index=int(file.stem.rsplit('-',1)[1])
        if index>count and file.resolve().is_relative_to((P/'qa').resolve()):file.unlink()
shutil_source=Path(r'C:\Users\a.ghafarian\Downloads\قالب_مقاله.docx')
(P/'sources/congress_template.docx').write_bytes(shutil_source.read_bytes())
manifest=[]
for f in P.rglob('*'):
    if f.is_file() and f.name!='SHA256SUMS.txt' and f.suffix not in ['.aux','.out','.log'] and 'qa' not in f.parts:manifest.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(P).as_posix()}')
(P/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
archive=R/'CostStableEHOA_BAIC2026_Revised.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in P.rglob('*'):
        if f.is_file() and f.suffix not in ['.aux','.out','.log'] and 'compiler_probe' not in f.parts:
            if 'qa' in f.parts and not (f.name.startswith('final_') or f.name in ['word_en.pdf','word_fa.pdf']):continue
            z.write(f,Path('revision_2026_10_12')/f.relative_to(P))
    for f in scripts+['ehoa.py','utils.py','run_experiments.py','requirements.txt']:
        z.write(R/f,Path('reproducibility')/f)
    for folder in ['data','proposed','configs','results/cost_stable_confirmatory/raw','results/cost_stable_confirmatory/masks']:
        for f in (R/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in f.parts:
                if folder=='data' and f.name in ['arrhythmia.csv','musk_v1.csv']:continue
                z.write(f,Path('reproducibility')/f.relative_to(R))
    for f in P.rglob('*'):
        if f.is_file() and f.suffix in ['.csv','.npy','.json','.zip'] and 'qa' not in f.parts:
            z.write(f,Path('reproducibility/revision_2026_10_12')/f.relative_to(P))
    z.write(P/'sources/congress_template.docx','reproducibility/revision_2026_10_12/sources/congress_template.docx')
print(json.dumps(quality,ensure_ascii=False));print('Archive:',archive,'bytes:',archive.stat().st_size)
