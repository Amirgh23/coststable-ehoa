from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

src = Path(r'C:\Users\a.ghafarian\Downloads\cost_stable_ieee_en_compact.docx')
out = Path(r'C:\Users\a.ghafarian\Downloads\cost_stable_ieee_en_compact_fixed.docx')
doc = Document(src)

def force_font(run, name):
    run.font.name = name
    rfonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        rfonts.set(qn('w:' + key), name)

# Repair the malformed summation glyph introduced during PDF-to-Word conversion.
equation = doc.paragraphs[28]
for run in equation.runs:
    if 'Σ' in run.text:
        run.text = run.text.replace('Σ', '∑')
    force_font(run, 'Cambria Math')
    run.font.size = Pt(10)
for run in doc.paragraphs[29].runs:
    force_font(run, 'Cambria Math')

# Normalize the second equation's math glyph fonts without changing its positioning.
for index in range(49, 54):
    for run in doc.paragraphs[index].runs:
        force_font(run, 'Cambria Math')

# Prevent converted table rows from splitting across columns/pages.
for table in doc.tables:
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        if tr_pr.find(qn('w:cantSplit')) is None:
            tr_pr.append(OxmlElement('w:cantSplit'))

# The converted second table had two adjacent values touching visually.
for row in doc.tables[1].rows:
    for cell in row.cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(6.5)
                force_font(run, 'Times New Roman')

# Keep table labels and figure captions attached to the following object/text.
for paragraph in doc.paragraphs:
    text = paragraph.text.strip()
    if text in ('TABLE I', 'TABLE II'):
        paragraph.paragraph_format.keep_with_next = True
    if text.startswith('Fig.'):
        paragraph.paragraph_format.keep_together = True

doc.core_properties.title = 'CostStableEHOA Budget Feasible and Stability Aware Feature Selection'
doc.save(out)
print(out)
