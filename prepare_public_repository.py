from pathlib import Path
import shutil,json,hashlib,re

R=Path(__file__).resolve().parent
P=R/'public_coststable_ehoa'
P.mkdir(exist_ok=True)
files=['ehoa.py','utils.py','requirements.txt','run_fold_safe_revision.py','analyze_fold_safe_revision.py','run_extended_revision.py','proposed/fold_safe_ehoa.py','proposed/cost_stable_ehoa.py','proposed/stability.py']
for name in files:
    target=P/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(R/name,target)
for folder,names in [('fold_safe_revision_2026_10_12',['protocol.json','frozen_sha256.json','environment.json','runs.csv','analysis/audit_summary.json','analysis/primary_overall.csv','analysis/primary_friedman.csv','analysis/primary_paired.csv','analysis/fresh_dataset_specifications.csv']),('extended_revision_2026_10_12',['protocol.json','frozen_sha256.json','planned_jobs.json'])]:
    for name in names:
        target=P/folder/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(R/folder/name,target)
for name in ['analysis/datasets.csv','corrected_experiments/steel_27_features_7_classes.csv','corrected_experiments/parkinson_subject_mapping.csv']:
    target=P/'revision_2026_10_12'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if name.startswith('analysis/'):shutil.copy2(R/'revision_2026_10_12'/name,target)
manifest=[]
for file in (R/'data').rglob('*.csv'):
    if file.name in ['breast_cancer.csv','wine.csv','ionosphere.csv','sonar.csv','dermatology.csv','spambase.csv','parkinsons.csv','hill_valley.csv','steel_plates_fault.csv','madelon.csv']:manifest.append(dict(path=str(file.relative_to(R)).replace('\\','/'),sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
(P/'DATA_SOURCES.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(P/'.gitignore').write_text('__pycache__/\n*.pyc\n*.log\n*.aux\n*.out\n',encoding='utf-8')
(P/'README.md').write_text('''# CostStableEHOA reproducibility

Auditable feature selection with hard synthetic budgets, fold-local mutual-information repair, and selected-column imputation/scaling/SMOTE. Author: Amirreza Ghaffarian.

The completed fold-safe study contains 774 runs: 450 primary and 324 biomedical sensitivity runs. `fold_safe_revision_2026_10_12/analysis/audit_summary.json` records recomputed mask costs, budgets, split separation and prediction checks. No universal predictive superiority or external clinical validity is claimed.

## Prospective extension

`extended_revision_2026_10_12/protocol.json` freezes 690 further runs before execution: 300 runs add two seeds to the primary comparison, 240 runs form a complete endpoint 2×2×2 budget/R/lambda factorial design across ten datasets, and 150 runs evaluate 16 hikers × 20 iterations. Factorial and larger-search experiments use one stochastic seed with three outer folds; they cannot establish all continuous-space interactions or convergence. Prior study results were known when this extension was designed. This public versioned protocol is not an independent formal preregistration of the earlier research.

## Reproduce

Use Python 3.13 and the package versions in `requirements.txt`. Exact dataset input hashes are listed in `DATA_SOURCES.json`. Original and snapshot URLs, dimensions and class counts are in `fold_safe_revision_2026_10_12/analysis/fresh_dataset_specifications.csv`.

Run `run_fold_safe_revision.py` and `analyze_fold_safe_revision.py` for the completed study; run `run_extended_revision.py` for the extension once its public protocol commit has been recorded in `extended_revision_2026_10_12/publication.json`. Result records are saved per job and can be resumed. Protocol/code hashes are verified before execution.

## Data and limitations

Clinical tariffs and independent external clinical observations are not present. Feature costs are synthetic. Parkinson recording groups are pseudonymous prefixes; the source narrative and file differ in reported group count. Code availability does not resolve that identity discrepancy. MI mean-minus-SD is a heuristic, without confidence coverage or false-selection error guarantees. Dataset blocks, rather than overlapping folds, are statistical units.

Data attribution and redistribution permissions are documented separately. Publication does not invent a code license or a historical registration record. The author's writing disclosure must follow the actual conference submission policy.
''',encoding='utf-8')
print('Curated publication prepared:',P)
