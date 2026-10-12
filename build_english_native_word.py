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
TEX = ROOT / 'paper_sources' / 'cost_stable_ieee_en.tex'
OUT = ROOT / 'CostStableEHOA_English_BAIC2026_Native.docx'
tex = TEX.read_text(encoding='utf-8')

def clean(s):
    cite = {'hegazy2026':'[1]','nogueira2018':'[2]','jagdhuber2020':'[3]','demsar2006':'[4]'}
    s = re.sub(r'%.*', '', s)
    s = re.sub(r'\\cite\{([^}]+)\}', lambda m: cite.get(m.group(1), '[?]'), s)
    s = re.sub(r'\\ref\{tab:overall\}', 'Table I', s)
    s = re.sub(r'\\ref\{tab:detail-en\}', 'Table II', s)
    s = re.sub(r'\\(?:textbf|emph|mathbf)\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\$([^$]+)\$', r'\1', s)
    s = s.replace('\\%', '%').replace('~', ' ')
    s = re.sub(r'\\[a-zA-Z]+(?:\[[^\]]*\])?', '', s)
    s = s.replace('{','').replace('}','').replace('\\',' ')
    return re.sub(r'\s+', ' ', s).strip()

title = 'CostStableEHOA: Budget-Feasible and Stability-Aware Feature Selection Using Resampled Lower-Confidence Utility'
abstract = clean(re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1))
keywords = clean(re.search(r'\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}', tex, re.S).group(1))
parts = re.split(r'\\section\{([^}]+)\}', tex)
sections = {}
for i in range(1, len(parts), 2):
    name, body = parts[i], parts[i+1]
    body = re.sub(r'\\begin\{(?:figure|table|equation)\}.*?\\end\{(?:figure|table|equation)\}', '', body, flags=re.S)
    body = re.split(r'\\balance|\\begin\{thebibliography\}', body)[0]
    sections[name] = [clean(x) for x in re.split(r'\n\s*\n', body) if clean(x)]

doc = Document(TEMPLATE)
body = doc._element.body
for child in list(body): body.remove(child)

def set_font(run, size, bold=False, italic=False):
    run.font.name='Times New Roman'; run.font.size=Pt(size); run.bold=bold; run.italic=italic
    rfonts=run._element.get_or_add_rPr().get_or_add_rFonts()
    for k in ('ascii','hAnsi','eastAsia','cs'): rfonts.set(qn('w:'+k),'Times New Roman')

def addp(text='', style='Normal', size=8, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=1, bold=False):
    p=doc.add_paragraph(style=style if style in [s.name for s in doc.styles] else 'Normal')
    p.alignment=align; p.paragraph_format.space_after=Pt(after); p.paragraph_format.line_spacing=0.95
    r=p.add_run(text); set_font(r,size,bold)
    return p

p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(4)
p.add_run().add_picture(str(ROOT/'paper_sources'/'baic2026_header.png'), width=Cm(17.8))
addp(title,'Title(English)',12,WD_ALIGN_PARAGRAPH.CENTER,2,True)
addp('Amirreza Ghaffarian','Authors( English)',9,WD_ALIGN_PARAGRAPH.CENTER,0)
addp('Graduate Student, Islamic Azad University','Affiliations(English)',8,WD_ALIGN_PARAGRAPH.CENTER,2)
addp('Abstract—'+abstract,'Abstract(English)',8,WD_ALIGN_PARAGRAPH.JUSTIFY,1)
addp('Index Terms—'+keywords,'Index',8,WD_ALIGN_PARAGRAPH.JUSTIFY,2)

sec=doc.add_section(WD_SECTION.CONTINUOUS)
for s in (doc.sections[0],sec):
    s.page_width,s.page_height=Cm(21),Cm(29.7); s.top_margin,s.bottom_margin=Cm(1.9),Cm(2.54); s.left_margin=s.right_margin=Cm(1.6)
for s,n in ((doc.sections[0],'1'),(sec,'2')):
    old=s._sectPr.find(qn('w:cols'))
    if old is not None: s._sectPr.remove(old)
    cols=OxmlElement('w:cols'); cols.set(qn('w:num'),n); cols.set(qn('w:space'),'340'); s._sectPr.append(cols)

order=['Introduction','Related Work','Method','Experimental Protocol','Results','Discussion','Threats to Validity','Detailed Results and Reproducibility','Conclusion']
for idx,name in enumerate(order,1):
    if name not in sections: continue
    addp(f'{idx}. {name.upper()}','Normal',8.5,WD_ALIGN_PARAGRAPH.CENTER,1,True)
    for t in sections[name]:
        if t.startswith(('includegraphics','caption','label')): continue
        addp(t,'Normal',7.8,WD_ALIGN_PARAGRAPH.JUSTIFY,1)
    if name=='Method':
        addp('[[EQ1]]','Equation',8,WD_ALIGN_PARAGRAPH.CENTER,1)
        addp('For bootstrap resamples, stable utility and the utility-to-cost ratio are defined as:','Normal',7.8,WD_ALIGN_PARAGRAPH.JUSTIFY,1)
        addp('[[EQ2]]','Equation',8,WD_ALIGN_PARAGRAPH.CENTER,1)
    if name=='Results':
        addp('TABLE I. MEAN RESULTS ACROSS TEN DATA SETS','Table Title',7,WD_ALIGN_PARAGRAPH.CENTER,1)
        data=[['Method','Accuracy','Cost ratio','Features','Stability'],['EHOA','0.8301','0.4782','42.07','0.1229'],['Budget-random','0.8288','0.2724','31.87','0.1403'],['Budget-cheapest','0.8324','0.2728','35.18','0.2552'],['Budget-MI','0.8331','0.2735','27.95','0.2335'],['Stable-LCB','0.8280','0.2775','30.98','0.2554']]
        table=doc.add_table(rows=len(data),cols=5); table.autofit=True
        for ri,row in enumerate(data):
            for ci,val in enumerate(row):
                cell=table.cell(ri,ci); cell.text=val; cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for pp in cell.paragraphs:
                    pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
                    for rr in pp.runs: set_font(rr,6.2,ri==0)
        img=ROOT/'results'/'cost_stable_confirmatory'/'final_analysis'/'accuracy_cost_tradeoff.png'
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(img),width=Cm(7.8))
        addp('Fig. 1. Accuracy-cost outcomes. The preferred direction is upper left.','Caption',6.8,WD_ALIGN_PARAGRAPH.CENTER,1)
    if name=='Detailed Results and Reproducibility':
        img=ROOT/'results'/'cost_stable_confirmatory'/'final_analysis'/'balanced_accuracy_by_dataset.png'
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(img),width=Cm(7.8))
        addp('Fig. 2. Balanced accuracy of the five methods on each data set.','Caption',6.8,WD_ALIGN_PARAGRAPH.CENTER,1)

addp('REFERENCES','Normal',8.5,WD_ALIGN_PARAGRAPH.CENTER,1,True)
refs=[
'[1] A. E. Hegazy, M. A. Makhlouf, O. A. M. Salem, and B. Hafiz, “An enhanced Hiking optimization algorithm for accurate and interpretable feature selection in medical data classification,” Cluster Computing, vol. 29, p. 244, 2026.',
'[2] S. Nogueira, K. Sechidis, and G. Brown, “On the stability of feature selection algorithms,” JMLR, vol. 18, no. 174, pp. 1-54, 2018.',
'[3] R. Jagdhuber et al., “Cost-constrained feature selection in binary classification,” Computational Statistics, vol. 35, pp. 1419-1440, 2020.',
'[4] J. Demsar, “Statistical comparisons of classifiers over multiple data sets,” JMLR, vol. 7, pp. 1-30, 2006.'
]
for x in refs: addp(x,'Normal',6.5,WD_ALIGN_PARAGRAPH.LEFT,0)
end_sec=doc.add_section(WD_SECTION.CONTINUOUS)
end_sec.page_width,end_sec.page_height=Cm(21),Cm(29.7)
end_sec.top_margin,end_sec.bottom_margin=Cm(1.9),Cm(2.54)
end_sec.left_margin=end_sec.right_margin=Cm(1.6)
old=end_sec._sectPr.find(qn('w:cols'))
if old is not None: end_sec._sectPr.remove(old)
cols=OxmlElement('w:cols'); cols.set(qn('w:num'),'1'); end_sec._sectPr.append(cols)
doc.core_properties.title=title; doc.core_properties.author='Amirreza Ghaffarian'
doc.save(OUT); print(OUT)
