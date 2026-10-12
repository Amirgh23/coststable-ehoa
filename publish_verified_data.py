from pathlib import Path
import json,shutil,urllib.request
import pandas as pd

ROOT=Path(__file__).resolve().parent
P=ROOT/'public_coststable_ehoa'
E=ROOT/'extended_revision_2026_10_12'
licenses=json.loads((E/'dataset_license_verification.json').read_text())
if len(licenses)!=10 or not all(row['CC_BY_4_0_link'] and row['page_mentions_CC_BY'] for row in licenses):raise ValueError('Dataset redistribution license not verified')
metadata=json.loads((E/'uci_metadata.json').read_text())
hill=json.load(urllib.request.urlopen('https://archive.ics.uci.edu/api/dataset?id=166',timeout=30))
metadata.pop('147')
metadata['166']=hill
ids=dict(breast_cancer=17,wine=109,ionosphere=52,sonar=151,dermatology=33,spambase=94,parkinsons=174,hill_valley=166,steel_plates_fault=198,madelon=171)
notice='# Dataset attribution and redistribution\n\nThe ten public source datasets are published by UCI under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Primary-page license links were verified on 2026-10-12; see dataset_license_verification.json. Numeric snapshots are retained exactly, with hashes in DATA_SOURCES.json. OpenML snapshot transformations and the corrected Steel target are explicitly documented. These data are public benchmark observations, not an independent external clinical validation cohort.\n\n'
for ds,uid in ids.items():
    source=ROOT/'data'/('' if ds in ['breast_cancer','wine'] else 'benchmark_v2')/(ds+'.csv')
    target=P/source.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    d=metadata[str(uid)]['data']
    notice+=f'## {d["name"]}\n\nCreators: '+', '.join(d['creators'])+f'. DOI: https://doi.org/{d["dataset_doi"]}. Source: https://archive.ics.uci.edu/dataset/{uid}. License: CC BY 4.0.\n\n'
notice+='## Changes and source correction\n\nBreast Cancer and Wine are sklearn snapshots; eight other snapshots were obtained through OpenML. Exact duplicate (X,y) rows are removed only by the experiment loader. Missing values and selected-column scaling/SMOTE are fitted on training data only. Steel has a separately retained corrected snapshot with 27 predictors and seven classes; the original 33-input binary snapshot is preserved for audit, not used for fresh model evaluation. Parkinson recording prefixes are public pseudonymous group keys, not independently verified clinical identities. Hill-Valley is the no-noise training/test combination from OpenML 1479; its correct UCI id is 166, not 147. The wrong UCI link in the first publication commit was a metadata error; numerical data and completed experiment outputs did not change.\n'
(P/'data/DATA_LICENSE.md').write_text(notice,encoding='utf-8')
shutil.copy2(E/'dataset_license_verification.json',P/'data/dataset_license_verification.json')
for name in ['steel_27_features_7_classes.csv','parkinson_subject_mapping.csv']:
    target=P/'revision_2026_10_12/corrected_experiments'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'revision_2026_10_12/corrected_experiments'/name,target)
for relative in ['revision_2026_10_12/analysis/datasets.csv','fold_safe_revision_2026_10_12/analysis/fresh_dataset_specifications.csv']:
    frame=pd.read_csv(P/relative)
    frame.loc[frame.dataset=='hill_valley','original_source']='https://archive.ics.uci.edu/dataset/166/hill+valley'
    frame.to_csv(P/relative,index=False)
text=(P/'README.md').read_text(encoding='utf-8')
text+='\n## Source erratum\n\nThe Hill-Valley UCI identifier was corrected to 166; id 147 is Statlog Image Segmentation. The exact OpenML 1479 numeric snapshot and numerical results were unchanged. Public dataset snapshots and attribution are now included.\n'
(P/'README.md').write_text(text,encoding='utf-8')
print('Ten verified public datasets, attribution and corrected source links prepared')
