# بسته نهایی پروژه درس کلان‌داده

دانشجو: امیررضا غفاریان  
استاد: دکتر محمدحسین معطر  
مقطع: کارشناسی ارشد - دانشگاه آزاد اسلامی

## اقلام اصلی

- `reports/code_documentation.pdf`: مستندات فنی و توضیح قطعه‌کدها.
- `reports/results_discussion.pdf`: نتایج واقعی، نمودارها، آزمون آماری و بحث.
- `src/`: کد الگوریتم، اجرا و تحلیل.
- `config/cost_stable_confirmatory.yaml`: پیکربندی دقیق ۳۰۰ اجرا.
- `results/raw/runs.csv`: تمام ردیف‌های خام اجرای تأییدی.
- `results/final_analysis/`: جداول آماری و نمودارهای مشتق‌شده از داده خام.
- `results/masks/`: ۳۰۰ ماسک انتخاب ویژگی برای ممیزی.
- `data/`: ده دیتاست استفاده‌شده و فایل‌های راهنما.
- `tests/`: آزمون‌های خودکار؛ نتیجه نهایی ۲۸ آزمون موفق.
- `latex/`: منبع LaTeX دو گزارش.

## اجرای مجدد

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python run_cost_stable_confirmatory.py --config configs/cost_stable_confirmatory.yaml --output results/cost_stable_confirmatory
python analyze_cost_stable_confirmatory.py
```

## خلاصه صحت

۳۰۰/۳۰۰ اجرا کامل، ۱۰ دیتاست، ۵ روش، بدون داده گم‌شده، کلید تکراری یا نقض بودجه. کاهش هزینه و افزایش پایداری نسبت به EHOA معنادار است؛ برتری دقت ادعا نمی‌شود.
