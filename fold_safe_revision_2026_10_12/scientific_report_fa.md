# اجرای تازه با پایپ‌لاین اصلاح‌شده

{
  "planned_runs": 774,
  "completed_runs": 774,
  "primary_runs": 450,
  "sensitivity_runs": 324,
  "duplicate_jobs": 0,
  "failed_attempts": 0,
  "all_masks_binary": true,
  "all_mask_counts_match": true,
  "maximum_cost_error": 5.684341886080802e-14,
  "inner_utility_training_overlap_with_inner_validation_or_outer_test": 0,
  "outer_row_overlap": 0,
  "outer_subject_overlap": 0,
  "inner_subject_overlap": 0,
  "smote_dimension_mismatches": 0,
  "inner_candidate_budget_violations": 0,
  "outer_constrained_budget_violations": 0,
  "maximum_ba_recalculation_error": 1.1102230246251565e-16,
  "maximum_accuracy_recalculation_error": 1.1102230246251565e-16,
  "analysis": "Fresh redesigned protocol; locally frozen, exploratory, not independent public preregistration",
  "stability": "Nine overlapping final masks per dataset/configuration, not nine independent samples",
  "sensitivity": "Descriptive OFAT on three biomedical datasets; not exhaustive interactions or clinical validation"
}

## تغییر واقعی روش

برای هر ماسک کاندید، تعمیر و محاسبه سودمندی در هر تقسیم درونی به‌صورت مستقل و فقط با داده آموزش آن تقسیم انجام می‌شود. برازندگی، میانگین دقت معمولی و میانگین اندازه ماسک‌های تعمیرشده در سه تقسیم است. ماسک نهایی از کاندید برنده با سودمندی آموزش بیرونی ساخته می‌شود. ماسک درونی و نهایی می‌توانند متفاوت باشند؛ این طراحی تازه است و نتایج آن جایگزین محاسبات قبلی به‌صورت بی‌اعلان نمی‌شوند. پیش‌پردازش و SMOTE در همه ارزیابی‌ها روی ابعاد منتخب اجرا شده‌اند. امتیاز درونی همچنان امتیاز انتخاب بهینه‌شده است؛ تخمین عملکرد از آزمون بیرونی می‌آید.

Dermatology مطابق [تعریف ناشر](https://archive.ics.uci.edu/dataset/33/dermatology)، 33 ویژگی درجه‌ای/گسسته و سن پیوسته دارد؛ MI نوع‌آگاه استفاده شد. Steel با 27 پیش‌بین و 7 کلاس اجرا شد. Parkinsons در بیرونی و درونی به‌صورت گروهی تقسیم شد؛ اختلاف 31 فرد اعلام‌شده و 32 پیشوند فایل همچنان نیازمند تأیید مستقل است.

## مشخصات واقعی اجرای تازه و لینک مستقیم داده

| dataset | N | D | classes | class_counts | subject_groups | original_source | snapshot_source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| breast_cancer | 569 | 30 | 2 | {"0": 212, "1": 357} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/17) | [منبع snapshot](https://archive.ics.uci.edu/dataset/17) |
| wine | 178 | 13 | 3 | {"0": 59, "1": 71, "2": 48} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/109) | [منبع snapshot](https://archive.ics.uci.edu/dataset/109) |
| ionosphere | 350 | 34 | 2 | {"0": 125, "1": 225} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/52) | [منبع snapshot](https://www.openml.org/d/59) |
| sonar | 208 | 60 | 2 | {"0": 111, "1": 97} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/151) | [منبع snapshot](https://www.openml.org/d/40) |
| dermatology | 366 | 34 | 6 | {"0": 112, "1": 61, "2": 72, "3": 49, "4": 52, "5": 20} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/33) | [منبع snapshot](https://www.openml.org/d/35) |
| spambase | 4210 | 57 | 2 | {"0": 2531, "1": 1679} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/94) | [منبع snapshot](https://www.openml.org/d/44) |
| parkinsons | 195 | 22 | 2 | {"0": 48, "1": 147} | 32 | [منبع اصلی](https://archive.ics.uci.edu/dataset/174) | [منبع snapshot](https://www.openml.org/d/1488) |
| hill_valley | 1212 | 100 | 2 | {"0": 606, "1": 606} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/147) | [منبع snapshot](https://www.openml.org/d/1479) |
| steel_plates_fault | 1941 | 27 | 7 | {"0": 158, "1": 190, "2": 391, "3": 72, "4": 55, "5": 402, "6": 673} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/198) | [منبع snapshot](https://www.openml.org/d/1504) |
| madelon | 2600 | 500 | 2 | {"0": 1300, "1": 1300} |  | [منبع اصلی](https://archive.ics.uci.edu/dataset/171) | [منبع snapshot](https://www.openml.org/d/1485) |

Steel از snapshot اصلاح‌شده بازسازی شد و Parkinson با فایل اصلی UCI تطبیق یافت. هش فایل استفاده‌شده در fresh_dataset_specifications.csv است. این جدول با مشخصات آرشیو قدیمی که Steel در آن 33 ورودی دارد، متفاوت است.

## نتیجه اصلی ده دیتاست

| method | balanced_accuracy | cost_ratio | selected_features | nogueira_stability | jaccard_stability | fit_total_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| EHOA | 0.79315 | 0.492255 | 42.7 | 0.118267 | 0.387755 | 4.707368 |
| random | 0.779413 | 0.271725 | 31.433333 | 0.11596 | 0.272913 | 4.131871 |
| cheapest | 0.796082 | 0.275836 | 34.9 | 0.286135 | 0.401692 | 4.109929 |
| mi | 0.796094 | 0.277288 | 27.277778 | 0.225024 | 0.332832 | 5.973626 |
| stable_lcb | 0.794314 | 0.27685 | 31.311111 | 0.221619 | 0.349847 | 10.982437 |

| metric | n_datasets | df | statistic | p_raw | p_holm_six_metrics |
| --- | --- | --- | --- | --- | --- |
| balanced_accuracy | 10 | 4 | 7.92 | 0.09455305 | 0.09455305 |
| cost_ratio | 10 | 4 | 20.72 | 0.00035982 | 0.00071964 |
| selected_features | 10 | 4 | 31.03589744 | 3.01e-06 | 1.806e-05 |
| nogueira_stability | 10 | 4 | 23.84 | 8.599e-05 | 0.00025798 |
| jaccard_stability | 10 | 4 | 26.64 | 2.35e-05 | 9.402e-05 |
| fit_total_seconds | 10 | 4 | 30.48 | 3.91e-06 | 1.954e-05 |

| metric | reference | mean_delta | W | p_raw | rank_biserial | ci95_low | ci95_high | p_holm_within_metric | p_holm_all_24 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| balanced_accuracy | EHOA | 0.00116411 | 27.0 | 1.0 | 0.01818182 | -0.01279994 | 0.01569886 | 1.0 | 1.0 |
| cost_ratio | EHOA | -0.21540567 | 0.0 | 0.00195312 | -1.0 | -0.24256593 | -0.18954738 | 0.0078125 | 0.046875 |
| selected_features | EHOA | -11.38888889 | 0.0 | 0.00195312 | -1.0 | -24.55583333 | -3.68888889 | 0.0078125 | 0.046875 |
| nogueira_stability | EHOA | 0.10335157 | 2.0 | 0.00585938 | 0.92727273 | 0.0463828 | 0.16774335 | 0.01757812 | 0.09375 |
| jaccard_stability | EHOA | -0.03790895 | 9.0 | 0.06445312 | -0.67272727 | -0.06995789 | -0.00305676 | 0.12890625 | 0.64453125 |
| fit_total_seconds | EHOA | 6.27506818 | 0.0 | 0.00195312 | 1.0 | 1.81507492 | 13.6074934 | 0.0078125 | 0.046875 |

اصلاح هولم هم درون هر معیار و هم روی همه 24 مقایسه گزارش شد. فاصله‌های bootstrap دیتاستی، توصیفی و بدون اصلاح چندگانگی‌اند. نتیجه آزمون با اثر توصیفی یکسان نیست؛ عدم معناداری، هم‌ارزی را ثابت نمی‌کند. زمان کامل ثبت شده، ولی اجرای هم‌زمان سه پردازش و یک رایانه، مبنای ادعای سرعت عمومی نیست.

## شاخص پزشکی سرطان پستان

در کدگذاری sklearn این فایل، 0 بدخیم و 1 خوش‌خیم است. sensitivity عمومی CSV، بازخوانی کلاس 1 است و نباید حساسیت سرطان خوانده شود. شاخص حساسیت بدخیم و ویژگی خوش‌خیم از پیش‌بینی ذخیره‌شده، جداگانه و با برچسب صریح محاسبه شدند؛ میانگین نه تقسیم هم‌پوشان، اعتبار بالینی بیرونی نیست.

| method | malignant_sensitivity | benign_specificity | malignant_label | benign_label | folds |
| --- | --- | --- | --- | --- | --- |
| EHOA | 0.946524 | 0.958917 | 0 | 1 | 9 |
| random | 0.924503 | 0.950514 | 0 | 1 | 9 |
| cheapest | 0.944936 | 0.964519 | 0 | 1 | 9 |
| mi | 0.943327 | 0.966387 | 0 | 1 | 9 |
| stable_lcb | 0.93235 | 0.968254 | 0 | 1 | 9 |

## حساسیت

بودجه‌های 0.15، 0.30 و 0.50 برای چهار تعمیر؛ R برابر 4، 8 و 16 و lambda برابر 0، 1 و 2 برای روش بازنمونه‌گیری‌شده روی سرطان پستان، Dermatology و Parkinsons بررسی شدند. تنظیم‌ها پیش از این اجراها تثبیت شدند؛ از آزمون بیرونی برای انتخاب تنظیم برنده استفاده نکردیم. این تحلیل یک‌عامل‌درهرمرحله است و همه تعامل‌ها را پوشش نمی‌دهد.

| dataset | method | budget_ratio | evidence_resamples | lambda_penalty | cohort | balanced_accuracy | cost_ratio | selected_features | nogueira_stability | jaccard_stability | fit_total_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breast_cancer | cheapest | 0.15 | 4 | 1.0 | budget_sensitivity | 0.944275 | 0.134901 | 7.555556 | 0.208831 | 0.266068 | 2.10171 |
| breast_cancer | cheapest | 0.5 | 4 | 1.0 | budget_sensitivity | 0.948819 | 0.439149 | 14.777778 | 0.103507 | 0.379163 | 2.297403 |
| breast_cancer | mi | 0.15 | 4 | 1.0 | budget_sensitivity | 0.931857 | 0.125456 | 6.111111 | 0.337844 | 0.315627 | 2.427486 |
| breast_cancer | mi | 0.5 | 4 | 1.0 | budget_sensitivity | 0.947665 | 0.419392 | 12.555556 | 0.113494 | 0.331497 | 2.269953 |
| breast_cancer | random | 0.15 | 4 | 1.0 | budget_sensitivity | 0.923334 | 0.132394 | 6.555556 | 0.089083 | 0.178869 | 1.958311 |
| breast_cancer | random | 0.5 | 4 | 1.0 | budget_sensitivity | 0.951144 | 0.451568 | 13.666667 | 0.118965 | 0.358067 | 2.147535 |
| breast_cancer | stable_lcb | 0.15 | 4 | 1.0 | budget_sensitivity | 0.930923 | 0.138769 | 7.0 | 0.353002 | 0.350437 | 3.383116 |
| breast_cancer | stable_lcb | 0.3 | 4 | 0.0 | utility_sensitivity | 0.954552 | 0.267811 | 10.444444 | 0.241115 | 0.350629 | 3.449281 |
| breast_cancer | stable_lcb | 0.3 | 4 | 2.0 | utility_sensitivity | 0.94987 | 0.265142 | 10.555556 | 0.175789 | 0.308894 | 3.543301 |
| breast_cancer | stable_lcb | 0.3 | 8 | 1.0 | utility_sensitivity | 0.952987 | 0.265786 | 10.555556 | 0.19609 | 0.344261 | 4.680115 |
| breast_cancer | stable_lcb | 0.3 | 16 | 1.0 | utility_sensitivity | 0.952205 | 0.271531 | 10.333333 | 0.200383 | 0.336585 | 7.584166 |
| breast_cancer | stable_lcb | 0.5 | 4 | 1.0 | budget_sensitivity | 0.954588 | 0.429473 | 13.555556 | 0.057931 | 0.323478 | 3.530505 |
| dermatology | cheapest | 0.15 | 4 | 1.0 | budget_sensitivity | 0.84167 | 0.141592 | 10.222222 | 0.393844 | 0.410051 | 3.232301 |
| dermatology | cheapest | 0.5 | 4 | 1.0 | budget_sensitivity | 0.947635 | 0.467538 | 18.666667 | 0.198175 | 0.474262 | 2.383572 |
| dermatology | mi | 0.15 | 4 | 1.0 | budget_sensitivity | 0.882481 | 0.136549 | 9.111111 | 0.437745 | 0.427407 | 3.210382 |
| dermatology | mi | 0.5 | 4 | 1.0 | budget_sensitivity | 0.951477 | 0.473017 | 16.666667 | 0.280769 | 0.470902 | 3.140453 |
| dermatology | random | 0.15 | 4 | 1.0 | budget_sensitivity | 0.780391 | 0.135442 | 9.111111 | 0.162865 | 0.244884 | 2.971487 |
| dermatology | random | 0.5 | 4 | 1.0 | budget_sensitivity | 0.936945 | 0.467737 | 17.666667 | 0.116288 | 0.409183 | 2.601041 |
| dermatology | stable_lcb | 0.15 | 4 | 1.0 | budget_sensitivity | 0.866372 | 0.143081 | 8.666667 | 0.341852 | 0.3543 | 4.116096 |
| dermatology | stable_lcb | 0.3 | 4 | 0.0 | utility_sensitivity | 0.933053 | 0.273474 | 12.555556 | 0.200238 | 0.336131 | 3.657423 |
| dermatology | stable_lcb | 0.3 | 4 | 2.0 | utility_sensitivity | 0.917026 | 0.279143 | 12.333333 | 0.225988 | 0.345624 | 3.497221 |
| dermatology | stable_lcb | 0.3 | 8 | 1.0 | utility_sensitivity | 0.927753 | 0.27413 | 11.777778 | 0.198915 | 0.326464 | 4.859976 |
| dermatology | stable_lcb | 0.3 | 16 | 1.0 | utility_sensitivity | 0.935701 | 0.277924 | 12.333333 | 0.261331 | 0.368326 | 6.874122 |
| dermatology | stable_lcb | 0.5 | 4 | 1.0 | budget_sensitivity | 0.95223 | 0.481485 | 17.333333 | 0.274231 | 0.481538 | 3.566206 |
| parkinsons | cheapest | 0.15 | 4 | 1.0 | budget_sensitivity | 0.681217 | 0.134084 | 4.444444 | 0.342089 | 0.329376 | 1.269709 |
| parkinsons | cheapest | 0.5 | 4 | 1.0 | budget_sensitivity | 0.702822 | 0.416551 | 9.111111 | 0.146552 | 0.345905 | 1.645237 |
| parkinsons | mi | 0.15 | 4 | 1.0 | budget_sensitivity | 0.704523 | 0.128027 | 3.666667 | 0.136364 | 0.173578 | 1.765576 |
| parkinsons | mi | 0.5 | 4 | 1.0 | budget_sensitivity | 0.719892 | 0.430517 | 9.111111 | 0.084104 | 0.312072 | 2.015397 |
| parkinsons | random | 0.15 | 4 | 1.0 | budget_sensitivity | 0.664809 | 0.123102 | 3.888889 | 0.071604 | 0.145437 | 1.757022 |
| parkinsons | random | 0.5 | 4 | 1.0 | budget_sensitivity | 0.715262 | 0.392747 | 8.777778 | 0.078555 | 0.292863 | 1.486136 |
| parkinsons | stable_lcb | 0.15 | 4 | 1.0 | budget_sensitivity | 0.68802 | 0.140344 | 4.111111 | 0.218902 | 0.234854 | 2.759405 |
| parkinsons | stable_lcb | 0.3 | 4 | 0.0 | utility_sensitivity | 0.718758 | 0.275341 | 7.111111 | 0.295826 | 0.367092 | 2.689218 |
| parkinsons | stable_lcb | 0.3 | 4 | 2.0 | utility_sensitivity | 0.724836 | 0.273089 | 6.0 | 0.096065 | 0.216094 | 2.595335 |
| parkinsons | stable_lcb | 0.3 | 8 | 1.0 | utility_sensitivity | 0.694791 | 0.261536 | 6.888889 | 0.266188 | 0.345071 | 3.614806 |
| parkinsons | stable_lcb | 0.3 | 16 | 1.0 | utility_sensitivity | 0.733907 | 0.277949 | 6.444444 | 0.39649 | 0.419054 | 5.523071 |
| parkinsons | stable_lcb | 0.5 | 4 | 1.0 | budget_sensitivity | 0.728836 | 0.44284 | 9.888889 | 0.152974 | 0.3753 | 2.728322 |

## باقی‌مانده

هزینه واقعی/گروهی پزشکی، داده بالینی بیرونی، تأیید مستقل هویت افراد، انتشار عمومی و تأیید اظهارنامه نویسنده همچنان موجود نیستند. ثبت محلی پیش از اجرای جدید، ثبت پیشینی مستقل عمومی محسوب نمی‌شود و لاگ تاریخی مفقود را بازسازی نمی‌کند. محدودیت سه بذر، جست‌وجوی کوتاه و وابستگی حاشیه‌ای MI باقی است.
