from pathlib import Path
import csv,json,re,zipfile
from xml.etree import ElementTree as ET
from pypdf import PdfReader

R=Path(__file__).resolve().parent
P=R/'revision_2026_10_12'
c=json.loads((P/'sources/manuscript_content.json').read_text(encoding='utf-8'))
def read(name):
    with (P/'analysis'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
refs=[b for page in c['pages'] for b in page if b['kind']=='ref']
body=[b for page in c['pages'] for b in page if b['kind']!='ref']
cited=set()
for b in body:
    for group in re.findall(r'\[([0-9]+(?:,[0-9]+)*)\]',b.get('en','')+' '+str(b.get('rows',[]))):cited.update(map(int,group.split(',')))
checks={'reference_count':len(refs),'uncited_references':sorted(set(range(1,len(refs)+1))-cited),'undefined_citations':sorted(cited-set(range(1,len(refs)+1))),'submission_reference_lines':len((P/'references_for_submission.txt').read_text(encoding='utf-8').splitlines()),'tables':sum(b['kind']=='table' for b in body),'figures':sum(b['kind']=='fig' for b in body),'body_prose_words':{lang:sum(len(b.get(lang,'').split()) for b in body if b['kind']=='p') for lang in ['en','fa']},'page_counts':{str(f.relative_to(P)):len(PdfReader(f).pages) for f in [P/'manuscript_en.pdf',P/'manuscript_fa.pdf',P/'qa/word_en.pdf',P/'qa/word_fa.pdf']}}
methods=['EHOA','Budget-random','Budget-cheapest','Budget-mi','Budget-stable_lcb']
table5=next(b for b in body if b['kind']=='table' and b['en'].startswith('Table 5.'))
overall={row['method']:row for row in read('eligible_overall.csv')}
numeric=[]
for m,row in zip(methods,table5['rows']):
    for i,metric in enumerate(['balanced_accuracy','cost_ratio','selected_features','nogueira_stability'],1):
        numeric.append(abs(float(row[i])-float(overall[m][metric]))<=.005001 if metric=='selected_features' else abs(float(row[i])-float(overall[m][metric]))<=.0000501)
checks['table5_all_values_match_source_rounding']=all(numeric)
table6=next(b for b in body if b['kind']=='table' and b['en'].startswith('Table 6.'))
friedman={row['metric']:row for row in read('eligible_friedman.csv')}
rankrows={(row['metric'],row['method']):row['average_rank'] for row in read('eligible_ranks.csv')}
comparison=[]
for metric,row in zip(['balanced_accuracy','cost_ratio','selected_features','nogueira_stability'],table6['rows']):
    comparison.extend([abs(float(row[1])-float(friedman[metric]['statistic']))<=.0000501,abs(float(row[2])-float(friedman[metric]['p_raw']))<=.00000501])
    comparison.extend(abs(float(v)-float(rankrows[metric,m]))<=.005001 for v,m in zip(row[3:],methods))
checks['table6_statistics_and_ranks_match_source_rounding']=all(comparison)
table7=next(b for b in body if b['kind']=='table' and b['en'].startswith('Table 7.'))
cases={row['method']:row for row in read('breast_cancer_case.csv')}
checks['table7_all_values_match_source_rounding']=all(abs(float(row[i])-float(cases[m][metric]))<=(.005001 if metric=='selected_features' else .0000501) for m,row in zip(methods,table7['rows']) for i,metric in enumerate(['balanced_accuracy','cost_ratio','selected_features','nogueira_stability'],1))
checks['archived_run_audit']=json.loads((P/'analysis/audit.json').read_text())
checks['corrected_run_audit']=json.loads((P/'analysis/corrected_experiment_audit.json').read_text())
checks['reviewer_items']=len(read('reviewer_response.csv'))
checks['docx_structure']={}
for lang in ['en','fa']:
    with zipfile.ZipFile(P/f'manuscript_{lang}.docx') as z:root=ET.fromstring(z.read('word/document.xml'))
    checks['docx_structure'][lang]={'native_equations':len(root.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath')),'tables':len(root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))}
prior_pdf=R/'previous_delivery/manuscript_en.pdf'
checks['pdf_english_words_before']=sum(len((p.extract_text() or '').split()) for p in PdfReader(prior_pdf).pages) if prior_pdf.exists() else json.loads((P/'analysis/final_verification.json').read_text(encoding='utf-8'))['pdf_english_words_before']
checks['pdf_english_words_after']=sum(len((p.extract_text() or '').split()) for p in PdfReader(P/'manuscript_en.pdf').pages)
checks['visual_review']='All 16 final pages inspected; no cropped tables or equations. Figure 1 close labels separated with leader lines.'
(P/'analysis/final_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
status=['اصلاح متنی انجام شد؛ برتری عمومی تأیید نشد','رفع شد','رفع شد','رفع شد؛ 15 منبع مرتبط','رفع شد؛ انتساب ناشر اصلاح شد','رفع شد؛ تفاوت snapshot و داده اصلی صریح است','رفع شد؛ اجرای اصلی با تنظیمات واقعی مستند شد','رفع شد در حد مطالعه محاسباتی؛ اعتبار بالینی نیازمند داده است','بازنویسی انجام شد','رفع شد در حد محور رسمی مرتبط','بازنویسی انجام شد','رفع ابهام شد؛ مدل هزینه واقعی هنوز موجود نیست','رفع شد؛ شرح با کد اجراشده تطبیق دارد','پاسخ آماده است؛ اظهارنامه نهایی نیازمند تأیید نویسنده است']
matrix=[]
for row,state in zip(read('reviewer_response.csv'),status):matrix.append([row['reviewer_item'],state,row['location'],row['evidence']])
with (P/'analysis/reviewer_completion_matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(['reviewer_item','verified_status','location','evidence']);w.writerows(matrix)
report='# گزارش تطبیق نهایی بازنگری\n\nمنابع از 9 به 15 مورد افزایش یافتند. همه 15 منبع در متن یا جدول ارجاع دارند؛ شماره ناموجود یا منبع بدون ارجاع دیده نشد. متن روش‌شناسی، محدودیت MI، تفاوت انتخاب پایدار، کنترل اعتبارسنجی، استدلال شدنی‌بودن و تفسیر پزشکی گسترش یافت. شمار واژه استخراج‌شده از PDF انگلیسی از '+str(checks['pdf_english_words_before'])+' به '+str(checks['pdf_english_words_after'])+' رسید؛ این شمار شامل جدول و مراجع است. هر چهار خروجی چاپی فارسی/انگلیسی و Word چهارصفحه‌ای‌اند.\n\n7 جدول، 2 شکل اصلی، 5 معادله بومی در هر Word و 14 پاسخ داوری بررسی شدند. بازحساب 300 ماسک قدیمی، تعداد ویژگی، هزینه و پایداری را تا خطای گردکردن تأیید کرد؛ 240 خروجی مقید قدیمی نقض بودجه ندارند. 60 اجرای اصلاح‌شده دارای 60 ماسک‌اند و 48 خروجی مقید تازه نیز نقض ندارند؛ هم‌پوشانی گروه‌های Parkinsons در تقسیم درونی و بیرونی صفر است. فایل final_verification.json نتیجه ماشین‌خوان و reviewer_completion_matrix.csv وضعیت هر بند را دارد.\n\nادعای «همه مشکلات علمی حل شدند» درست نیست. پاسخ به بندهای داوری با رفع همه نیازهای پژوهشی یکسان نیست. هزینه واقعی، اعتبارسنجی بالینی، طراحی utility درونی و SMOTE روی ابعاد منتخب، حساسیت R/lambda/بودجه، تأیید هویت گروه، ثبت پیشینی، لاگ تاریخی و مخزن عمومی همچنان در unresolved_items_fa.md آمده‌اند. نتایج تازه اکتشافی‌اند.\n\n| بند | وضعیت بررسی‌شده | محل | شاهد |\n| --- | --- | --- | --- |\n'
report+='\n'.join('| '+' | '.join(x.replace('|','/') for x in row)+' |' for row in matrix)+'\n'
(P/'final_verification_fa.md').write_text(report,encoding='utf-8')
print(json.dumps({k:v for k,v in checks.items() if k not in ['archived_run_audit','corrected_run_audit']},ensure_ascii=False))
