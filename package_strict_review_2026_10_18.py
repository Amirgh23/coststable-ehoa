from pathlib import Path
import hashlib,json,os,zipfile

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public_coststable_ehoa'
records=[]
for folder in ['fold_safe_revision_2026_10_12','extended_revision_2026_10_12']:
    for name,expected in json.loads((ROOT/folder/'frozen_sha256.json').read_text()).items():
        path=ROOT/folder/name if name=='protocol.json' else ROOT/name
        records.append(dict(protocol=folder,file=name,matches=hashlib.sha256(path.read_bytes()).hexdigest()==expected))
if not all(row['matches'] for row in records):raise ValueError('Frozen historical inputs changed')
(ROOT/'strict_review_2026_10_18/frozen_integrity_check.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(PUBLIC/'strict_review_2026_10_18/frozen_integrity_check.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
plan=json.loads((ROOT/'strict_review_2026_10_18/protocol.json').read_text())
if hashlib.sha256((ROOT/'run_strict_controls_2026_10_18.py').read_bytes()).hexdigest()!=plan['code_sha256']:raise ValueError('Post-hoc control plan/code differ')
manifest_name='STRICT_RELEASE_MANIFEST_2026_10_18.json'
files=[]
for current,dirs,names in os.walk(PUBLIC):
    dirs[:]=[d for d in dirs if d not in ['.git','__pycache__','.pytest_cache','packaging_clone','node_modules']]
    for name in names:
        path=Path(current)/name
        if name==manifest_name or path.suffix in ['.aux','.log','.out'] or 'overflow' in name:continue
        files.append(dict(path=path.relative_to(PUBLIC).as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
files.sort(key=lambda row:row['path'])
(PUBLIC/manifest_name).write_text(json.dumps(files,indent=2),encoding='utf-8')
archive=ROOT/'CostStableEHOA_Strict_Review_2026_10_18.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as package:
    for row in files:package.write(PUBLIC/row['path'],row['path'])
    package.write(PUBLIC/manifest_name,manifest_name)
with zipfile.ZipFile(archive) as package:
    if package.testzip() is not None:raise ValueError('Archive CRC failure')
    entries=len(package.namelist())
print(json.dumps(dict(archive=str(archive),entries=entries,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),frozen_matches=len(records))),flush=True)
