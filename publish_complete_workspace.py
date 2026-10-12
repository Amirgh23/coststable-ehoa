from pathlib import Path
import hashlib
import json
import shutil
import zipfile

r = Path(__file__).resolve().parent
p = r / 'public_coststable_ehoa'
archive = r / 'CostStableEHOA_Complete_Workspace.zip'
skip = {'public_coststable_ehoa', '.git', '__pycache__', '.docx_work'}
files = sorted(f for f in r.rglob('*') if f.is_file() and not any(s in f.relative_to(r).parts for s in skip) and f != archive)
entries = []
for f in files:
    rel = f.relative_to(r)
    entries.append({'path': rel.as_posix(), 'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
    if f.suffix.lower() != '.zip':
        target = p / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
(p / 'COMPLETE_WORKSPACE_MANIFEST.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
(p / 'CONTINUE_WORK_FA.md').write_text('''# ادامه کار روی سیستم دیگر

نسخه کامل شامل مقاله‌ها، منابع، فایل‌های Word/PDF/LaTeX، پاسخ داوران، گزارش ممیزی، داده‌ها، کد، خروجی آزمایش‌ها و نسخه‌های قبلی است. فایل‌های ZIP قبلی نیز داخل فایل Complete Workspace در بخش Releases موجودند. کش Python، پوشه موقت Word و تاریخچه داخلی Git دوباره بایگانی نشده‌اند.

آخرین نسخه معتبر: extended_revision_2026_10_12. نتایج اصلی پنج‌بذری 750 اجرا، تعامل‌ها 240 اجرا و جست‌وجوی بزرگ‌تر 150 اجرا هستند؛ با حساسیت قبلی، مجموع 1464 اجرا. نتایج قدیمی در results و previous_delivery صرفاً آرشیوی‌اند و نباید با نتایج تازه ادغام شوند.

برای ادامه، مخزن را clone کنید یا فایل CostStableEHOA_Complete_Workspace.zip را از Releases دانلود و استخراج کنید. مسیرهای مطلق ثبت‌شده در لاگ‌های قدیمی متعلق به سیستم اولیه‌اند. اسکریپت‌های اصلی اجرا، ریشه را از محل خود فایل پیدا می‌کنند. Python 3.13 و نسخه‌های requirements.txt را استفاده کنید. run_fold_safe_revision.py و سپس run_extended_revision.py اجراها را بازتولید می‌کنند؛ analyze_fold_safe_revision.py و analyze_extended_revision.py گزارش‌های آماری را تولید می‌کنند. اجرای مجدد می‌تواند زمان‌بر باشد؛ خروجی کامل آماده موجود است.

ساخت سند با build_extended_documents.py انجام می‌شود و به سازنده‌های قبلی موجود در ریشه وابسته است. رندر Word به Microsoft Word در Windows نیاز دارد؛ PDF فارسی به XeLaTeX و فونت‌های تعریف‌شده در TeX نیاز دارد. مسیر Python همراه Codex در برخی ابزارهای تولید سند وابسته به سیستم اولیه است؛ در سیستم جدید آن را به Python محلی دارای وابستگی‌های سند تغییر دهید.

پیش‌نویس اظهارنامه، تأیید یا امضای نهایی نویسنده نیست. هزینه واقعی، داده بالینی مستقل، هویت بالینی گروه‌های Parkinson و سوابق تاریخی مفقود همچنان حل‌نشده‌اند؛ unresolved_items_fa.md را بخوانید. ثبت عمومی پروتکل تکمیلی پیش از 690 اجرای جدید انجام شد، نه پیش از مطالعه قدیمی.

COMPLETE_WORKSPACE_MANIFEST.json مسیر، اندازه و SHA256 تمام فایل‌های بایگانی‌شده را ثبت می‌کند. آرشیو کامل و مخزن هر دو برای انتقال کار قابل استفاده‌اند.
''', encoding='utf-8')
readme = p / 'README.md'
s = readme.read_text(encoding='utf-8').replace('Manuscripts, reviewer correspondence and author declaration drafts are excluded from this repository.', 'At the author’s explicit request, the complete research workspace now includes manuscripts, reviewer responses, author declaration drafts and prior versions. The latest authoritative version is extended_revision_2026_10_12; earlier results are archival.')
s += '\n## Complete workspace transfer\n\nSee CONTINUE_WORK_FA.md for continuation instructions. The complete ZIP in Releases also includes prior delivery ZIPs. COMPLETE_WORKSPACE_MANIFEST.json records every archived research file. Generated caches and internal Git files are excluded.\n'
readme.write_text(s, encoding='utf-8')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for f in files:
        z.write(f, f.relative_to(r))
    for name in ['COMPLETE_WORKSPACE_MANIFEST.json', 'CONTINUE_WORK_FA.md']:
        z.write(p / name, name)
with zipfile.ZipFile(archive) as z:
    failure = z.testzip()
    if failure:
        raise ValueError(failure)
print(json.dumps({'files': len(files), 'archive': str(archive), 'bytes': archive.stat().st_size, 'zip_crc': 'clean'}))
