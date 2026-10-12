# گزارش تکمیل تحلیل تعامل و جست‌وجو

690 اجرای تکمیلی واقعاً انجام شد: 300 اجرای دو بذر اضافه، 240 اجرای طرح کامل 2×2×2 و 150 اجرای جست‌وجوی 16×20. با 774 اجرای قبلی پایپ‌لاین مستقل، 1464 اجرا موجود است. تحلیل اصلی پنج‌بذری 750 اجرا دارد؛ سه دسته را به‌عنوان یک پروتکل عددی یکسان مخلوط نکردیم.

## ممیزی

```json
{
  "planned_extension_runs": 690,
  "completed_extension_runs": 690,
  "total_fold_safe_runs": 1464,
  "primary_five_seed_runs": 750,
  "primary_masks_per_dataset_method": 15,
  "factorial_runs": 240,
  "larger_search_runs": 150,
  "duplicate_jobs": 0,
  "failed_attempts": 0,
  "all_masks_binary": true,
  "all_mask_counts_match": true,
  "maximum_cost_error": 2.842170943040401e-14,
  "inner_train_validation_outer_test_overlap": 0,
  "outer_row_overlap": 0,
  "inner_subject_overlap": 0,
  "outer_subject_overlap": 0,
  "smote_dimension_mismatches": 0,
  "candidate_budget_violations": 0,
  "final_constrained_budget_violations": 0,
  "maximum_ba_error": 1.1102230246251565e-16,
  "maximum_accuracy_error": 1.1102230246251565e-16,
  "publication": {
    "repository": "https://github.com/Amirgh23/coststable-ehoa",
    "protocol_commit": "72c87b6a44fb236225eef18e6cfca196b14fbdee",
    "verified_public": true,
    "recorded_before_execution_utc": "2026-10-12T12:12:32.783322+00:00",
    "protocol_url": "https://github.com/Amirgh23/coststable-ehoa/blob/72c87b6a44fb236225eef18e6cfca196b14fbdee/extended_revision_2026_10_12/protocol.json"
  },
  "scope": "Prior 774 fold-safe runs plus 690 prospective extension runs; original leaked archival results excluded"
}
```

## تحلیل اصلی پنج بذر

| method | balanced_accuracy | cost_ratio | selected_features | nogueira_stability | jaccard_stability | fit_total_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| EHOA | 0.794638 | 0.494728 | 42.84 | 0.103649 | 0.383943 | 6.071454 |
| random | 0.78139 | 0.272366 | 31.593333 | 0.121657 | 0.279197 | 5.276545 |
| cheapest | 0.794432 | 0.276463 | 35.046667 | 0.247562 | 0.378036 | 5.356846 |
| mi | 0.794857 | 0.278735 | 27.306667 | 0.220334 | 0.330894 | 7.275047 |
| stable_lcb | 0.793225 | 0.277406 | 31.24 | 0.224095 | 0.349894 | 13.071954 |

| metric | n_datasets | df | statistic | p_raw | p_holm_six_metrics |
| --- | --- | --- | --- | --- | --- |
| balanced_accuracy | 10 | 4 | 6.88 | 0.1423672 | 0.1423672 |
| cost_ratio | 10 | 4 | 21.2 | 0.00028903 | 0.00057805 |
| selected_features | 10 | 4 | 29.13131313 | 7.35e-06 | 2.843e-05 |
| nogueira_stability | 10 | 4 | 29.68 | 5.69e-06 | 2.843e-05 |
| jaccard_stability | 10 | 4 | 29.44 | 6.36e-06 | 2.843e-05 |
| fit_total_seconds | 10 | 4 | 31.76 | 2.14e-06 | 1.285e-05 |

| metric | reference | mean_delta | W | p_raw | rank_biserial | ci95_low | ci95_high | p_holm_within_metric | p_holm_all_24 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| balanced_accuracy | EHOA | -0.00141247 | 22.0 | 0.625 | -0.2 | -0.01024181 | 0.00798541 | 1.0 | 1.0 |
| cost_ratio | EHOA | -0.21732137 | 0.0 | 0.00195312 | -1.0 | -0.24862484 | -0.18592024 | 0.0078125 | 0.046875 |
| selected_features | EHOA | -11.6 | 0.0 | 0.00195312 | -1.0 | -24.78016667 | -3.89333333 | 0.0078125 | 0.046875 |
| nogueira_stability | EHOA | 0.12044575 | 0.0 | 0.00195312 | 1.0 | 0.08909049 | 0.15814658 | 0.0078125 | 0.046875 |
| jaccard_stability | EHOA | -0.03404921 | 3.0 | 0.00976562 | -0.89090909 | -0.04856269 | -0.01887088 | 0.02929688 | 0.14648438 |
| fit_total_seconds | EHOA | 7.00050001 | 0.0 | 0.00195312 | 1.0 | 2.20865664 | 15.02537728 | 0.0078125 | 0.046875 |

## تعامل پارامترها

طرح کامل 2×2×2 شامل بودجه 0.15/0.50، R=4/8 و lambda=0/2 روی ده دیتاست است. اثرهای اصلی، تعامل‌های دوتایی و تعامل سه‌تایی به‌صورت کنتراست متعامد محاسبه شدند. واحد بازنمونه‌گیری، دیتاست است. تنها یک بذر تصادفی و سه تقسیم بیرونی برای هر خانه داریم؛ اثرها توصیفی‌اند و همه سطوح پیوسته یا عدم‌قطعیت بذر را پوشش نمی‌دهند. پایداری خانه‌ها از سه ماسک محاسبه شد و فقط با خانه‌های هم‌پروتکل مقایسه می‌شود.

| term | metric | mean_effect | ci95_low | ci95_high | n_datasets | stochastic_seeds | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| budget_ratio | balanced_accuracy | 0.013818 | -0.005824 | 0.037761 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio | cost_ratio | 0.307603 | 0.289141 | 0.325971 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio | nogueira_stability | -0.21049 | -0.263202 | -0.149462 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio | selected_features | 21.55 | 6.991667 | 46.0 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples | balanced_accuracy | 0.003777 | -0.000947 | 0.009209 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples | cost_ratio | 0.003886 | -0.001558 | 0.008657 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples | nogueira_stability | -0.020923 | -0.059425 | 0.01427 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples | selected_features | 0.0 | -0.3 | 0.308333 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples x lambda_penalty | balanced_accuracy | -0.000839 | -0.004064 | 0.002455 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples x lambda_penalty | cost_ratio | -0.000924 | -0.007076 | 0.004843 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples x lambda_penalty | nogueira_stability | 0.013225 | -0.004624 | 0.03121 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x evidence_resamples x lambda_penalty | selected_features | 0.433333 | -0.041667 | 0.983333 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x lambda_penalty | balanced_accuracy | -0.002358 | -0.007152 | 0.002782 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x lambda_penalty | cost_ratio | 0.000754 | -0.005991 | 0.007764 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x lambda_penalty | nogueira_stability | 0.00155 | -0.043248 | 0.049688 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| budget_ratio x lambda_penalty | selected_features | 1.15 | 0.1 | 2.791667 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples | balanced_accuracy | 0.007859 | 0.001535 | 0.015267 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples | cost_ratio | 0.005401 | -0.000279 | 0.010728 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples | nogueira_stability | 0.007514 | -0.025067 | 0.041201 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples | selected_features | 0.416667 | -0.041667 | 0.9 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples x lambda_penalty | balanced_accuracy | 0.00124 | -0.002533 | 0.005511 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples x lambda_penalty | cost_ratio | -0.002764 | -0.009529 | 0.003663 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples x lambda_penalty | nogueira_stability | -0.006284 | -0.043703 | 0.026598 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| evidence_resamples x lambda_penalty | selected_features | -0.283333 | -0.983542 | 0.241667 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| lambda_penalty | balanced_accuracy | 0.00684 | 8.3e-05 | 0.01553 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| lambda_penalty | cost_ratio | -0.000269 | -0.009069 | 0.00804 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| lambda_penalty | nogueira_stability | -0.006616 | -0.053415 | 0.043656 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |
| lambda_penalty | selected_features | -1.533333 | -3.891667 | 0.033333 | 10 | 1 | descriptive endpoint factorial contrast; not all continuous-space interactions |

## جست‌وجوی بزرگ‌تر

16 کوه‌پیما و 20 تکرار با 8 کوه‌پیما و 10 تکرار روی همان بذر 72001 و تقسیم‌های مشترک، برای هر پنج روش و ده دیتاست مقایسه شدند. اثرهای زیر از ده اختلاف دیتاستی‌اند؛ تضمین بهینه سراسری یا همگرایی نیستند. هیچ تنظیم برنده‌ای با آزمون بیرونی انتخاب نشد.

| method | metric | mean_delta | ci95_low | ci95_high | n_datasets | seeds | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EHOA | balanced_accuracy | -0.007327 | -0.014107 | -0.002184 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| EHOA | cost_ratio | -0.006731 | -0.057497 | 0.042179 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| EHOA | selected_features | 1.133333 | 0.166667 | 2.133333 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| EHOA | nogueira_stability | -0.059052 | -0.146418 | 0.025057 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| EHOA | fitness | -0.009061 | -0.014333 | -0.00499 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| EHOA | evaluations | 127.9 | 84.998333 | 172.5675 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| EHOA | fit_total_seconds | 13.817505 | 3.922592 | 31.255265 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | balanced_accuracy | -0.003157 | -0.014628 | 0.00917 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | cost_ratio | 0.00122 | -0.005519 | 0.008289 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | selected_features | -1.133333 | -1.833333 | -0.466667 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | nogueira_stability | -0.068295 | -0.232611 | 0.069429 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | fitness | -0.017087 | -0.023007 | -0.011007 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | evaluations | 131.8 | 94.433333 | 172.5 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| cheapest | fit_total_seconds | 12.783761 | 4.991069 | 25.837949 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | balanced_accuracy | 0.017991 | -0.001057 | 0.039521 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | cost_ratio | -0.007128 | -0.018511 | 0.00257 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | selected_features | -0.466667 | -1.233333 | 0.266667 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | nogueira_stability | 0.048453 | -0.032643 | 0.129813 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | fitness | -0.015246 | -0.020446 | -0.010447 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | evaluations | 121.3 | 73.899167 | 169.834167 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| mi | fit_total_seconds | 12.48709 | 4.096909 | 26.259651 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | balanced_accuracy | 0.004952 | -0.008019 | 0.017412 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | cost_ratio | -0.007948 | -0.020127 | 0.00163 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | selected_features | 0.2 | -0.533333 | 0.833333 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | nogueira_stability | 0.07735 | -0.015045 | 0.173606 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | fitness | -0.009748 | -0.015934 | -0.003443 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | evaluations | 164.933333 | 119.0 | 206.6 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| random | fit_total_seconds | 15.102033 | 6.014376 | 30.204653 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | balanced_accuracy | -0.004245 | -0.028692 | 0.019402 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | cost_ratio | 4.3e-05 | -0.003687 | 0.004276 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | selected_features | -0.0 | -0.933333 | 1.3 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | nogueira_stability | 0.008103 | -0.056443 | 0.082037 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | fitness | -0.015541 | -0.023381 | -0.009111 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | evaluations | 137.5 | 89.466667 | 186.300833 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |
| stable_lcb | fit_total_seconds | 10.397638 | 4.565321 | 18.246029 | 10 | 1 | descriptive larger-minus-reference search; not convergence proof |

## منابع و باقی‌مانده

شناسه UCI صحیح Hill-Valley برابر 166 است؛ 147 مربوط به Statlog Image Segmentation است. snapshot عددی OpenML 1479 تغییر نکرد و خطا فقط ارجاع منبع بود. هزینه‌ها همچنان lognormal مصنوعی‌اند؛ تعرفه واقعی و داده بالینی مستقل در پوشه معرفی‌شده پیدا نشدند. شناسه بالینی Parkinson از پیشوند ضبط قابل اثبات نیست. ثبت عمومی پروتکل تکمیلی پیش از اجرا، ثبت پیشینی آزمایش‌های گذشته یا ثبت رسمی مستقل محسوب نمی‌شود. MI منهای SD همچنان ابتکاری است؛ پوشش اطمینان، کنترل انتخاب کاذب و تضمین پذیرش ادعا نمی‌شود.
