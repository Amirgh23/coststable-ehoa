# CostStableEHOA reproducibility

Auditable feature selection with hard synthetic budgets, fold-local mutual-information repair, and selected-column imputation/scaling/SMOTE. Author: Amirreza Ghaffarian.

The completed fold-safe study contains 1,464 runs: 750 primary runs with five seeds, 324 biomedical sensitivity runs, 240 factorial runs, and 150 larger-search runs. `fold_safe_revision_2026_10_12/analysis/audit_summary.json` records recomputed mask costs, budgets, split separation and prediction checks. No universal predictive superiority or external clinical validity is claimed.

## Prospective extension

`extended_revision_2026_10_12/protocol.json` froze 690 further runs before execution; all 690 are completed: 300 runs add two seeds to the primary comparison, 240 runs form a complete endpoint 2×2×2 budget/R/lambda factorial design across ten datasets, and 150 runs evaluate 16 hikers × 20 iterations. Factorial and larger-search experiments use one stochastic seed with three outer folds; they cannot establish all continuous-space interactions or convergence. Prior study results were known when this extension was designed. This public versioned protocol is not an independent formal preregistration of the earlier research.

## Reproduce

Use Python 3.13 and the package versions in `requirements.txt`. Exact dataset input hashes are listed in `DATA_SOURCES.json`. Original and snapshot URLs, dimensions and class counts are in `fold_safe_revision_2026_10_12/analysis/fresh_dataset_specifications.csv`.

Run `run_fold_safe_revision.py` and `analyze_fold_safe_revision.py` for the completed study; run `run_extended_revision.py` and `analyze_extended_revision.py` for the extension. Its pre-execution public protocol commit is recorded in `extended_revision_2026_10_12/publication.json`. Result records are saved per job and can be resumed. Protocol/code hashes are verified before execution.

## Data and limitations

Clinical tariffs and independent external clinical observations are not present. Feature costs are synthetic. Parkinson recording groups are pseudonymous prefixes; the source narrative and file differ in reported group count. Code availability does not resolve that identity discrepancy. MI mean-minus-SD is a heuristic, without confidence coverage or false-selection error guarantees. Dataset blocks, rather than overlapping folds, are statistical units.

Data attribution and redistribution permissions are documented separately. Publication does not invent a code license or a historical registration record. The author's writing disclosure must follow the actual conference submission policy.

## Source erratum

The Hill-Valley UCI identifier was corrected to 166; id 147 is Statlog Image Segmentation. The exact OpenML 1479 numeric snapshot and numerical results were unchanged. Public dataset snapshots and attribution are now included.

All 1,464 public benchmark job outputs include masks, predictions, split provenance and candidate audits. Extension audit and dataset-block statistical results are in `extended_revision_2026_10_12/analysis`. Recorded timings compare batches with different worker counts (three versus six) and are not a controlled speed benchmark. At the author’s explicit request, the complete research workspace now includes manuscripts, reviewer responses, author declaration drafts and prior versions. The latest authoritative version is extended_revision_2026_10_12; earlier results are archival.

## Complete workspace transfer

See CONTINUE_WORK_FA.md for continuation instructions. The complete ZIP in Releases also includes prior delivery ZIPs. COMPLETE_WORKSPACE_MANIFEST.json records every archived research file. Generated caches and internal Git files are excluded.

## Public evidence supplement — 2026-10-13

See external_evidence_2026_10_13/REPORT_FA.md. This adds 25 exploratory source-only fits evaluated on a separate public cohort in a restricted three-feature space, plus an official published FNA fee and shared-service cost scenario. Subject-level balanced accuracy was 0.575 with a descriptive 95% interval [0.475,0.675]; no clinical superiority is established. The original 1,464-run paper remains separate. Clinical identities, historical missing evidence and author signoff remain unresolved.

## Integrated manuscript revision — 2026-10-13

Latest authoritative manuscript: integrated_revision_2026_10_13. Both languages have four-page Word/PDF/LaTeX versions,17references,8tables and2figures. Transfer and shared-service-cost findings are integrated into the abstract, discussion,Table8,conclusion and14reviewer responses. See unresolved_items_fa.md and SUBMISSION_STATUS_FA.md: author approval was explicitly withheld and no conference submission occurred. The1464original runs and25transfer fits retain distinct protocols.
