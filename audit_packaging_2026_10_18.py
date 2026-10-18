from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys, tempfile, zipfile

root=Path(__file__).resolve().parent
public_source=root/'public_coststable_ehoa' if (root/'public_coststable_ehoa').is_dir() else root
out=root/'supervision_2026_10_18'
out.mkdir(exist_ok=True)
records=[]
for layout in ['clone','staging']:
    with tempfile.TemporaryDirectory(prefix='coststable_packaging_') as directory:
        work=Path(directory)
        shutil.copytree(root/'integrated_revision_2026_10_13',work/'integrated_revision_2026_10_13')
        for relative in ['extended_revision_2026_10_12/scientific_report_fa.md','extended_revision_2026_10_12/author_declaration_draft_fa.md','extended_revision_2026_10_12/analysis/reviewer_response.csv','external_evidence_2026_10_13/external_runs.csv','external_evidence_2026_10_13/external_audit.json','external_evidence_2026_10_13/cost_model.json','external_evidence_2026_10_13/REPORT_FA.md','build_integrated_documents.py','finalize_integrated_revision.py']:
            destination=work/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(root/relative,destination)
        public=work if layout=='clone' else work/'public_coststable_ehoa'
        public.mkdir(exist_ok=True)
        for name in ['README.md','CONTINUE_WORK_FA.md']:
            shutil.copy2(public_source/name,public/name)
        with (public/'README.md').open('a',encoding='utf-8') as stream:
            stream.write('\n## Packaging audit sentinel\n\nPreserve this later section.\n')
        (public/'CostStableEHOA_Integrated_Rebuild_older.zip').write_bytes(b'prior rebuild sentinel')
        rounds=[]
        for number in [1,2]:
            process=subprocess.run([sys.executable,str(work/'finalize_integrated_revision.py')],cwd=work,capture_output=True,text=True,encoding='utf-8')
            if process.returncode:
                raise RuntimeError(process.stderr)
            with (work/'integrated_revision_2026_10_13/sources/reference_verification.csv').open(encoding='utf-8',newline='') as stream:
                references=list(csv.DictReader(stream))
            archive=work/'CostStableEHOA_Integrated_Rebuild.zip'
            with zipfile.ZipFile(archive) as package:
                corrupt=package.testzip()
                contains_self=archive.name in package.namelist()
                nested_rebuilds=[name for name in package.namelist() if Path(name).match('CostStableEHOA_Integrated_Rebuild*.zip')]
            quality=json.loads((work/'integrated_revision_2026_10_13/analysis/delivery_quality.json').read_text(encoding='utf-8'))
            rounds.append({'round':number,'exit_code':process.returncode,'reference_rows':len(references),'reference_16_rows':sum(x['reference_id']=='16' for x in references),'reference_17_rows':sum(x['reference_id']=='17' for x in references),'readme_integrated_sections':(public/'README.md').read_text(encoding='utf-8').count('## Integrated manuscript revision — 2026-10-13'),'readme_later_section_preserved':'Preserve this later section.' in (public/'README.md').read_text(encoding='utf-8'),'guide_old_authoritative_statement':'آخرین نسخه معتبر: extended_revision_2026_10_12.' in (public/'CONTINUE_WORK_FA.md').read_text(encoding='utf-8'),'archive_corruption':corrupt,'archive_contains_itself':contains_self,'archive_nested_rebuilds':nested_rebuilds,'page_counts':quality['page_counts'],'visual_review':quality['visual_review'],'study_runs':quality['study_runs'],'transfer_fits':quality['separate_transfer_fits']})
        records.append({'layout':layout,'rounds':rounds})
        if layout=='clone':
            shutil.copytree(work,out/'packaging_clone_snapshot',dirs_exist_ok=True)
(out/'packaging_smoke.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
