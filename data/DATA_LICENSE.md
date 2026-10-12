# Dataset attribution and redistribution

The ten public source datasets are published by UCI under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Primary-page license links were verified on 2026-10-12; see dataset_license_verification.json. Numeric snapshots are retained exactly, with hashes in DATA_SOURCES.json. OpenML snapshot transformations and the corrected Steel target are explicitly documented. These data are public benchmark observations, not an independent external clinical validation cohort.

## Breast Cancer Wisconsin (Diagnostic)

Creators: William Wolberg, Olvi Mangasarian, Nick Street, W. Street. DOI: https://doi.org/10.24432/C5DW2B. Source: https://archive.ics.uci.edu/dataset/17. License: CC BY 4.0.

## Wine

Creators: Stefan Aeberhard, M. Forina. DOI: https://doi.org/10.24432/C5PC7J. Source: https://archive.ics.uci.edu/dataset/109. License: CC BY 4.0.

## Ionosphere

Creators: V. Sigillito, S. Wing, L. Hutton, K. Baker. DOI: https://doi.org/10.24432/C5W01B. Source: https://archive.ics.uci.edu/dataset/52. License: CC BY 4.0.

## Connectionist Bench (Sonar, Mines vs. Rocks)

Creators: Terry Sejnowski, R. Gorman. DOI: https://doi.org/10.24432/C5T01Q. Source: https://archive.ics.uci.edu/dataset/151. License: CC BY 4.0.

## Dermatology

Creators: Nilsel Ilter, H. Guvenir. DOI: https://doi.org/10.24432/C5FK5P. Source: https://archive.ics.uci.edu/dataset/33. License: CC BY 4.0.

## Spambase

Creators: Mark Hopkins, Erik Reeber, George Forman, Jaap Suermondt. DOI: https://doi.org/10.24432/C53G6X. Source: https://archive.ics.uci.edu/dataset/94. License: CC BY 4.0.

## Parkinsons

Creators: Max Little. DOI: https://doi.org/10.24432/C59C74. Source: https://archive.ics.uci.edu/dataset/174. License: CC BY 4.0.

## Hill-Valley

Creators: Lee Graham, Franz Oppacher. DOI: https://doi.org/10.24432/C5JC8P. Source: https://archive.ics.uci.edu/dataset/166. License: CC BY 4.0.

## Steel Plates Faults

Creators: M Buscema, S Terzi, W Tastle. DOI: https://doi.org/10.24432/C5J88N. Source: https://archive.ics.uci.edu/dataset/198. License: CC BY 4.0.

## Madelon

Creators: Isabelle Guyon. DOI: https://doi.org/10.24432/C5602H. Source: https://archive.ics.uci.edu/dataset/171. License: CC BY 4.0.

## Changes and source correction

Breast Cancer and Wine are sklearn snapshots; eight other snapshots were obtained through OpenML. Exact duplicate (X,y) rows are removed only by the experiment loader. Missing values and selected-column scaling/SMOTE are fitted on training data only. Steel has a separately retained corrected snapshot with 27 predictors and seven classes; the original 33-input binary snapshot is preserved for audit, not used for fresh model evaluation. Parkinson recording prefixes are public pseudonymous group keys, not independently verified clinical identities. Hill-Valley is the no-noise training/test combination from OpenML 1479; its correct UCI id is 166, not 147. The wrong UCI link in the first publication commit was a metadata error; numerical data and completed experiment outputs did not change.
