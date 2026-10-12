import re
from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Pt, Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r'C:\Users\a.ghafarian\Downloads\SUBMIT_TO_PROFESSOR_MOATTAR')
TEMPLATE = Path(r'C:\Users\a.ghafarian\Downloads\قالب_مقاله.docx')
TEX = ROOT / 'paper_sources' / 'cost_stable_ieee_fa.tex'
OUT = ROOT / 'مقاله_آماده_ارسال_کنگره.docx'

tex = TEX.read_text(encoding='utf-8')

def clean(s):
    cites = {'nogueira2018':'[1]', 'hegazy2026':'[2]', 'jagdhuber2020':'[3]', 'demsar2006':'[4]'}
    s = re.sub(r'%.*', '', s)
    s = re.sub(r'\\cite\{([^}]+)\}', lambda m: cites.get(m.group(1), '[?]'), s)
    s = re.sub(r'\\ref\{tab:overall-fa\}', '۱', s)
    s = re.sub(r'\\ref\{[^}]+\}', '', s)
    s = re.sub(r'\\(?:lr|textbf|emph|mathbf)\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\$([^$]+)\$', r'\1', s)
    s = s.replace('\\&', '&').replace('~', ' ').replace('\\%', '٪')
    s = s.replace('\\,', ' ').replace('\\;', ' ').replace('\\:', ' ')
    s = re.sub(r'\\[a-zA-Z]+(?:\[[^\]]*\])?', '', s)
    s = s.replace('{', '').replace('}', '').replace('\\', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

title = clean(re.search(r'\\title\{([^\n]+)\}', tex).group(1))
abstract = clean(re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1))
keywords = clean(re.search(r'\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}', tex, re.S).group(1))

parts = re.split(r'\\section\{([^}]+)\}', tex)
sections = {}
for i in range(1, len(parts), 2):
    name, body = clean(parts[i]), parts[i+1]
    body = re.sub(r'\\begin\{(?:figure|table)\}.*?\\end\{(?:figure|table)\}', '', body, flags=re.S)
    body = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', body, flags=re.S)
    body = re.sub(r'\{?\\linespread\{[^}]+\}\\selectfont', '', body)
    body = re.split(r'\\balance|\\begin\{thebibliography\}', body)[0]
    paras = [clean(p) for p in re.split(r'\n\s*\n', body)]
    sections[name] = [p for p in paras if p and not p.startswith('label')]

doc = Document(TEMPLATE)
body = doc._element.body
for child in list(body):
    body.remove(child)

def bidi(p):
    pPr = p._p.get_or_add_pPr()
    el = pPr.find(qn('w:bidi'))
    if el is None:
        el = OxmlElement('w:bidi'); pPr.append(el)
    el.set(qn('w:val'), '1')

def set_run(run, size=None, bold=None):
    run.font.name = 'B Nazanin'
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:cs'), 'B Nazanin')
    run._element.rPr.rFonts.set(qn('w:ascii'), 'Times New Roman')
    run._element.rPr.rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    if size: run.font.size = Pt(size)
    if bold is not None: run.bold = bold

def para(text='', style='Normal', size=8, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=1):
    p = doc.add_paragraph(style=style)
    p.alignment = align; bidi(p)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text); set_run(r, size)
    return p

p = para(title, 'Title', 12, WD_ALIGN_PARAGRAPH.CENTER, 3)
for r in p.runs: r.bold = True
p = para('امیررضا غفاریان', 'Author', 10, WD_ALIGN_PARAGRAPH.CENTER, 0)
p = para('دانشجوی کارشناسی ارشد، دانشگاه آزاد اسلامی', 'Affiliations', 8, WD_ALIGN_PARAGRAPH.CENTER, 3)
para('چکیده - ' + abstract, 'abstract', 8, WD_ALIGN_PARAGRAPH.JUSTIFY, 1)
para('کلیدواژه‌ها - ' + keywords, 'Index', 8, WD_ALIGN_PARAGRAPH.JUSTIFY, 2)

sec = doc.add_section(WD_SECTION.CONTINUOUS)
first = doc.sections[0]
first.page_width, first.page_height = Cm(21), Cm(29.7)
first.top_margin, first.bottom_margin = Cm(1.9), Cm(2.54)
first.left_margin = first.right_margin = Cm(1.6)
first_cols = OxmlElement('w:cols'); first_cols.set(qn('w:num'), '1')
old_first_cols = first._sectPr.find(qn('w:cols'))
if old_first_cols is not None: first._sectPr.remove(old_first_cols)
first._sectPr.append(first_cols)
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(1.9), Cm(2.54)
sec.left_margin = sec.right_margin = Cm(1.6)
cols = OxmlElement('w:cols'); cols.set(qn('w:num'), '2'); cols.set(qn('w:space'), '340')
old = sec._sectPr.find(qn('w:cols'))
if old is not None: sec._sectPr.remove(old)
sec._sectPr.append(cols)

order = ['مقدمه','کارهای مرتبط','روش پیشنهادی','پروتکل آزمایش','نتایج','بحث','تهدیدهای اعتبار','نتیجه‌گیری']
for name in order:
    if name not in sections: continue
    p = para(name, 'Heading 1', 9, WD_ALIGN_PARAGRAPH.CENTER, 1)
    for r in p.runs: r.bold = True
    for text in sections[name]:
        if len(text) < 3 or text.startswith('includegraphics') or text.startswith('caption'): continue
        para(text, 'Normal', 8, WD_ALIGN_PARAGRAPH.JUSTIFY, 1)
    if name == 'روش پیشنهادی':
        para('روابط اصلی:  Σ(zⱼcⱼ) ≤ B ،  uⱼ = max(0, Īⱼ − zαsⱼ) ،  qⱼ = uⱼ / max(cⱼ, ε). در صورت نقض بودجه، ویژگی فعال با کمترین qⱼ حذف می‌شود.', 'Equation', 8, WD_ALIGN_PARAGRAPH.CENTER, 2)
    if name == 'نتایج':
        para('جدول ۱ - میانگین نتایج روی ده دیتاست', 'Table Title', 8, WD_ALIGN_PARAGRAPH.CENTER, 1)
        data = [
            ['روش','دقت','هزینه','ویژگی','پایداری'],
            ['EHOA','0.8301','0.4782','42.07','0.1229'],
            ['Budget-random','0.8288','0.2724','31.87','0.1403'],
            ['Budget-cheapest','0.8324','0.2728','35.18','0.2552'],
            ['Budget-MI','0.8331','0.2735','27.95','0.2335'],
            ['Stable-LCB','0.8280','0.2775','30.98','0.2554'],
        ]
        table = doc.add_table(rows=len(data), cols=5)
        table.autofit = True
        for ri,row in enumerate(data):
            for ci,val in enumerate(row):
                cell=table.cell(ri,ci); cell.text=val; cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for pp in cell.paragraphs:
                    pp.alignment=WD_ALIGN_PARAGRAPH.CENTER; bidi(pp)
                    for rr in pp.runs: set_run(rr, 6.5, ri==0)
        img = ROOT/'results'/'cost_stable_confirmatory'/'final_analysis'/'accuracy_cost_tradeoff.png'
        if not img.exists(): img = ROOT/'results'/'final_analysis'/'accuracy_cost_tradeoff.png'
        if img.exists():
            p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(img), width=Cm(7.8))
            para('شکل ۱ - مبادله دقت و هزینه؛ جهت مطلوب، بالا و چپ است.', 'Caption', 7, WD_ALIGN_PARAGRAPH.CENTER, 1)

p = para('مراجع', 'Heading', 9, WD_ALIGN_PARAGRAPH.CENTER, 1)
for r in p.runs: r.bold=True
refs = [
    '[1] S. Nogueira, K. Sechidis, and G. Brown, “On the stability of feature selection algorithms,” JMLR, vol. 18, no. 174, pp. 1-54, 2018.',
    '[2] A. E. Hegazy et al., “An enhanced Hiking optimization algorithm for accurate and interpretable feature selection in medical data classification,” Cluster Computing, vol. 29, p. 244, 2026.',
    '[3] R. Jagdhuber et al., “Cost-constrained feature selection in binary classification,” Computational Statistics, vol. 35, pp. 1419-1440, 2020.',
    '[4] J. Demsar, “Statistical comparisons of classifiers over multiple data sets,” JMLR, vol. 7, pp. 1-30, 2006.',
]
for ref in refs: para(ref, 'Normal', 6.5, WD_ALIGN_PARAGRAPH.LEFT, 0)

core = doc.core_properties
core.title = title; core.author = 'امیررضا غفاریان'; core.subject = 'مقاله کنگره'
doc.save(OUT)
print(OUT)
