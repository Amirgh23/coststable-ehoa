# CostStableEHOA reproducibility

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
