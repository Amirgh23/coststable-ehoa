from docx import Document
p=r'C:\Users\a.ghafarian\Downloads\قالب_مقاله.docx'
d=Document(p)
for s in d.styles:
    if s.type == 1:
        print(s.name, '|', s.style_id, '|', s.font.name, s.font.size.pt if s.font.size else None)
for i,p in enumerate(d.paragraphs[:20]):
    print(i, repr(p.text[:80]), p.style.name, p.alignment)
