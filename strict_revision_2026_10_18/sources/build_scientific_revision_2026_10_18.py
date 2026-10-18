from pathlib import Path
import json,re,shutil
import pandas as pd
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scientific_revision_2026_10_18'
OLD=ROOT/'integrated_revision_2026_10_13'
TEMPLATE=ROOT/'revision_2026_10_12/sources/congress_template.docx'
for folder in ['figures','sources']:
    shutil.copytree(OLD/folder,OUT/folder,dirs_exist_ok=True)
(OUT/'qa').mkdir(exist_ok=True)
shutil.copy2(OLD/'baic2026_header.png',OUT/'baic2026_header.png')
c=json.loads((OLD/'sources/manuscript_content.json').read_text(encoding='utf-8'))
title=c['title']; abstract=c['abstract']; keywords=c['keywords']; pages=c['pages']
abstract['en']=abstract['en'].replace('Corrected comparisons do not establish predictive superiority.','Corrected comparisons do not establish predictive superiority; stability significance is lost in every post-hoc nine-dataset leave-one-out analysis.')
abstract['fa']=abstract['fa'].replace('مقایسه اصلاح‌شده برتری پیش‌بینی را ثابت نمی‌کند.','مقایسه اصلاح‌شده برتری پیش‌بینی را ثابت نمی‌کند؛ معناداری پایداری در هر تحلیل پسینی حذف یک دیتاست از بین می‌رود.')
for page in pages:
    for b in page:
        if b['kind']=='table' and b['en'].startswith('Table 7.'):
            b['en']=b['en'].replace('Table 7.','Table 8.')
            b['fa']=b['fa'].replace('جدول ۷.','جدول ۸.')
        elif b['kind']=='table' and b['en'].startswith('Table 8.'):
            b['en']=b['en'].replace('Table 8.','Table 9.')
            b['fa']=b['fa'].replace('جدول۸.','جدول۹.').replace('جدول ۸.','جدول ۹.')
        if b['kind']=='p' and b['en'].startswith('Breast Cancer Wisconsin'):
            b['en']=b['en'].replace('Table 7','Table 8')
            b['fa']=b['fa'].replace('جدول ۷','جدول ۸')
        if b['kind']=='p' and b['en'].startswith('Exact (X,y) duplicates'):
            b['en']+=' Six Spambase rows form three identical-feature, opposite-label pairs; 94/114 runs split a pair across outer folds. Email identities are unknown; feature collision does not establish entity leakage.'
            b['fa']+=' شش ردیف Spambase سه جفت ویژگی یکسان با برچسب مخالف دارند؛ در ۹۴ اجرا از ۱۱۴ اجرا، یک جفت بین آموزش/آزمون بیرونی پخش می‌شود. هویت ایمیل نامعلوم است؛ برخورد ویژگی، نشت موجودیت را ثابت نمی‌کند.'
        if b['kind']=='p' and b['en'].startswith('github.com/'):
            b['en']='github.com/Amirgh23/coststable-ehoa provides code, data, masks, predictions and audits. An independent audit recomputed all 1464 final classifiers, including AUC/PR-AUC, and 25 external predictions with zero prediction disagreements; probabilities are now saved. All 75 selected optimizer replays matched historical masks on the newer runtime, and winning fitness was independently checked. This is not a replay of every historical search. Protocols and cohorts remain separate; Hill-Valley uses UCI166/OpenML1479.'
            b['fa']='مخزن github.com/Amirgh23/coststable-ehoa کد، داده، ماسک، پیش‌بینی و ممیزی را دارد. ممیزی مستقل، طبقه‌بند نهایی هر ۱۴۶۴ اجرا شامل AUC/PR-AUC و ۲۵ پیش‌بینی بیرونی را بدون اختلاف پیش‌بینی بازحساب کرد؛ احتمال‌ها اکنون ذخیره شده‌اند. هر ۷۵ بازاجرای منتخب بهینه‌ساز روی محیط جدید، ماسک تاریخی را بازتولید کرد و برازندگی برنده مستقل بررسی شد؛ این بازاجرای تمام جست‌وجوهای تاریخی نیست. پروتکل‌ها و دسته‌ها جدا هستند؛ Hill-Valley از UCI166/OpenML1479 است.'
        if b['kind']=='p' and b['en'].startswith('Fold-local repair enforces'):
            b['en']='Fold-local repair enforces synthetic budgets. Positive stability differences are threshold-fragile under dataset omission; predictive superiority is unestablished. Public-cohort transfer is weak and column deletion does not reduce shared-service fees. Clinical identity, measured marginal costs and full clinical validation remain necessary for deployment.'
            b['fa']='تعمیر محلی، بودجه مصنوعی را رعایت می‌کند. اختلاف مثبت پایداری از نظر آستانه معناداری به حذف دیتاست حساس است؛ برتری پیش‌بینی ثابت نشده است. انتقال به مجموعه عمومی ضعیف است و حذف ستون تعرفه مشترک را کم نمی‌کند. استقرار به هویت بالینی تأییدشده، هزینه حاشیه‌ای اندازه‌گیری‌شده و اعتبارسنجی کامل بالینی نیاز دارد.'
loo=pd.read_csv(ROOT/'scientific_audit_2026_10_18/leave_one_dataset_out_paired.csv')
phi=loo[(loo.metric=='nogueira_stability')&(loo.reference=='EHOA')]
ox=phi[phi.omitted_dataset=='parkinsons'].iloc[0]
primary=pd.read_csv(ROOT/'extended_revision_2026_10_12/analysis/primary_paired.csv')
full=primary[(primary.metric=='nogueira_stability')&(primary.reference=='EHOA')].iloc[0]
new=[{'kind':'p','en':'Post-hoc dataset omission retains positive stability differences versus EHOA and Random, but none of the ten nine-dataset families retains Holm24 significance (Table 7). With nine nonzero blocks, the minimum two-sided signed-rank p is 2/512; observed minimum Holm24 is 0.09375. This threshold fragility does not prove no effect. The original ten-dataset analysis is retained; no omission is used to choose a winner.','fa':'حذف پسینی دیتاست، اختلاف مثبت پایداری نسبت به EHOA و Random را حفظ می‌کند، اما هیچ خانواده نه‌دیتاستی معناداری Holm24 ندارد (جدول ۷). در نه بلوک غیرصفر، کمینه p دوطرفه signed-rank برابر 2/512 است؛ کمینه هولم مشاهده‌شده 0.09375 است. این شکنندگی آستانه، نبود اثر را ثابت نمی‌کند. تحلیل اصلی ده‌دیتاستی حفظ شد و حذف دیتاست برای انتخاب برنده استفاده نشد.'},
{'kind':'table','en':'Table 7. Post-hoc stability robustness, Resampled minus EHOA; intervals across omissions are ranges, not confidence intervals.','fa':'جدول ۷. استحکام پسینی پایداری، روش بازنمونه‌گیری منهای EHOA؛ بازه حذف‌ها دامنه است، نه فاصله اطمینان.','headers':['Analysis','N','Stability delta','Holm24 p'],'rows':[['Original',10,f'{full.mean_delta:+.5f}',f'{full.p_holm_all_24:.5f}'],['No Oxford',9,f'{ox.mean_delta:+.5f}',f'{ox.p_holm_all_24:.5f}'],['Each omission',9,f'[{phi.mean_delta.min():+.5f},{phi.mean_delta.max():+.5f}]','>=0.09375']],'widths':[1.0,.25,1.4,.8]}]
page=pages[2]
idx=next(i for i,b in enumerate(page) if b['kind']=='p' and b['en'].startswith('Resampled minus EHOA'))
page[idx+1:idx+1]=new
(OUT/'sources/manuscript_content.json').write_text(json.dumps(dict(title=title,abstract=abstract,keywords=keywords,pages=pages),ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'references_for_submission.txt').write_text('\n'.join(b['en']+' '+b['url'] for pg in pages for b in pg if b['kind']=='ref')+'\n',encoding='utf-8')
renderer=(ROOT/'build_revision_documents.py').read_text(encoding='utf-8')
renderer=renderer.replace('section_settings(doc.add_section(WD_SECTION.CONTINUOUS),1,fa)','')
exec(compile(renderer[renderer.index('def esc(s):'):],'scientifically_audited_document_renderer','exec'))
