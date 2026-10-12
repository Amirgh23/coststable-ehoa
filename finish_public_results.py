from pathlib import Path
import shutil

r = Path(__file__).resolve().parent
p = r / 'public_coststable_ehoa'
names = {'mask.npy', 'predictions.csv', 'split_provenance.npz', 'candidate_audit.csv', 'inner_split_audit.csv', 'result.json'}
count = 0
for base in ['fold_safe_revision_2026_10_12', 'extended_revision_2026_10_12']:
    for f in (r / base).rglob('*'):
        if f.is_file() and 'jobs' in f.parts and f.name in names:
            target = p / f.relative_to(r)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            count += 1
q = p / 'README.md'
s = q.read_text(encoding='utf-8')
s = s.replace('The completed fold-safe study contains 774 runs: 450 primary and 324 biomedical sensitivity runs.', 'The completed fold-safe study contains 1,464 runs: 750 primary runs with five seeds, 324 biomedical sensitivity runs, 240 factorial runs, and 150 larger-search runs.')
s = s.replace('freezes 690 further runs before execution:', 'froze 690 further runs before execution; all 690 are completed:')
s = s.replace('run `run_extended_revision.py` for the extension once its public protocol commit has been recorded in `extended_revision_2026_10_12/publication.json`.', 'run `run_extended_revision.py` and `analyze_extended_revision.py` for the extension. Its pre-execution public protocol commit is recorded in `extended_revision_2026_10_12/publication.json`.')
s += '\nAll 1,464 public benchmark job outputs include masks, predictions, split provenance and candidate audits. Extension audit and dataset-block statistical results are in `extended_revision_2026_10_12/analysis`. Recorded timings compare batches with different worker counts (three versus six) and are not a controlled speed benchmark. Manuscripts, reviewer correspondence and author declaration drafts are excluded from this repository.\n'
q.write_text(s, encoding='utf-8')
print('Public job files:', count)
