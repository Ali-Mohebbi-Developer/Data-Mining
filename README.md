# پروژه کامل داده‌کاوی محصولات فروشگاهی

این مخزن یک پروژه کامل و ماژولار برای درس داده‌کاوی است. داده از صفحات عمومی وب جمع‌آوری می‌شود و سپس مراحل پاک‌سازی، مهندسی ویژگی، تحلیل اکتشافی، قواعد انجمنی، دسته‌بندی و خوشه‌بندی روی آن اجرا می‌شود.

## موضوع و منبع داده

موضوع انتخاب‌شده «محصولات فروشگاهی» و نوع محصول «کتاب» است. منبع اصلی سایت عمومی `Books to Scrape` است که برای تمرین وب‌اسکرپینگ طراحی شده و حدود ۱۰۰۰ محصول دارد.

فایل `data/raw/books_seed.csv` یک نسخه خام ذخیره‌شده با ۹۹۳ رکورد است تا اجرای پروژه بدون اسکرپ مجدد نیز ممکن باشد. اسکرپر کامل در `src/web_scraper.py` قرار دارد و با گزینه `--scrape` قابل اجرا است.

## ساختار پروژه

```text
books_data_mining_project/
├── data/
│   ├── raw/
│   │   ├── books_seed.csv
│   │   └── sample_catalogue_page.html
│   ├── interim/
│   └── processed/
├── models/
├── notebooks/
│   └── complete_analysis.ipynb
├── reports/
│   ├── figures/
│   └── tables/
├── src/
│   ├── apriori_library.py
│   ├── apriori_manual.py
│   ├── association_rules_analysis.py
│   ├── classification.py
│   ├── clustering.py
│   ├── config.py
│   ├── data_loader.py
│   ├── exploratory_analysis.py
│   ├── feature_engineering.py
│   ├── pipeline.py
│   ├── preprocessing.py
│   ├── report_builder.py
│   ├── transaction_builder.py
│   ├── utils.py
│   ├── visualization.py
│   └── web_scraper.py
├── for_student.md
├── main.py
├── overview.md
├── questions.md
├── README.md
├── reports.md
└── requirements.txt
```

## نصب و اجرا در Linux و macOS

1. وارد پوشه پروژه شوید:

```bash
cd books_data_mining_project
```

2. محیط مجازی بسازید:

```bash
python3 -m venv venv
```

3. محیط مجازی را فعال کنید:

```bash
source venv/bin/activate
```

4. وابستگی‌ها را نصب کنید:

```bash
python3 -m pip install -r requirements.txt
```

5. پروژه کامل را اجرا کنید:

```bash
python3 main.py
```

## نصب و اجرا در Windows PowerShell

```powershell
cd books_data_mining_project
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## اجرای اسکرپ مجدد

برای جمع‌آوری مستقیم داده از وب و سپس اجرای همه تحلیل‌ها:

```bash
python3 main.py --scrape
```

برای تست سریع اسکرپر روی دو صفحه فهرست:

```bash
python3 main.py --scrape --max-pages 2
```

اسکرپر بین درخواست‌ها مکث دارد. مقدار مکث با گزینه زیر قابل تغییر است:

```bash
python3 main.py --scrape --delay 0.8
```

## اجرای Apriori با کتابخانه mlxtend

حالت پیش‌فرض از پیاده‌سازی دستی Apriori استفاده می‌کند. برای اجرای نسخه کتابخانه‌ای:

```bash
python3 main.py --association-engine mlxtend
```

## اجرای پروژه با فایل خام دیگر

```bash
python3 main.py --input path/to/input.csv
```

فایل ورودی حداقل باید ستون‌های `title` و `price` را داشته باشد. ستون‌های دیگر در مرحله پاک‌سازی با مقدار پیش‌فرض مدیریت می‌شوند.

## خروجی‌ها

پس از اجرای موفق، فایل‌های زیر ساخته یا به‌روزرسانی می‌شوند:

- `data/interim/books_cleaned.csv`
- `data/processed/books_features.csv`
- `reports/figures/price_distribution.png`
- `reports/figures/rating_counts.png`
- `reports/figures/price_by_rating.png`
- `reports/tables/association_rules.csv`
- `reports/tables/classification_metrics.csv`
- `reports/tables/confusion_matrix_logistic_regression.csv`
- `reports/tables/confusion_matrix_random_forest.csv`
- `reports/tables/k_selection_scores.csv`
- `reports/tables/clustering_metrics.csv`
- `reports/tables/cluster_profiles_kmeans.csv`
- `reports/tables/cluster_profiles_agglomerative.csv`
- `models/logistic_regression.joblib`
- `models/random_forest.joblib`
- `models/kmeans.joblib`
- `reports.md`

## روش‌های داده‌کاوی

### قواعد انجمنی

برای هر کتاب یک Basket از ویژگی‌های دسته‌ای ساخته می‌شود. ویژگی‌هایی مانند گروه قیمت، امتیاز، گروه امتیاز، طول عنوان، موضوع متن، وجود شماره سری و گروه حرف اول در Basket قرار می‌گیرند. Apriori با معیارهای Support، Confidence و Lift اجرا می‌شود.

### دسته‌بندی

برچسب هدف `price_band` است و سه کلاس Low، Medium و High دارد. داده با روش Stratified Train/Test Split تقسیم می‌شود. مدل‌های زیر اجرا می‌شوند:

- Logistic Regression
- Random Forest

معیارهای Accuracy، Precision، Recall و F1 به‌صورت Macro گزارش می‌شوند.

### خوشه‌بندی

TF-IDF متن با ویژگی‌های عددی استانداردشده ترکیب می‌شود. سپس کاهش بعد با Truncated SVD انجام می‌گیرد. تعداد خوشه با Silhouette Score برای k بین ۲ تا ۶ انتخاب می‌شود. الگوریتم‌های زیر اجرا می‌شوند:

- KMeans
- Agglomerative Clustering

## نکات بازتولیدپذیری

- مقدار Random State برابر ۴۲ است.
- همه مسیرها در `src/config.py` تعریف شده‌اند.
- اجرای پیش‌فرض به اینترنت نیاز ندارد.
- اجرای `--scrape` به اینترنت نیاز دارد.
- داده خام همراه پروژه برای اجرای فوری قرار داده شده است.

## فایل آموزشی شخصی

فایل `for_student.md` شرح مرحله‌به‌مرحله کد، منطق مدل‌ها و پرسش‌های احتمالی استاد را توضیح می‌دهد. این فایل بخشی از اجرای پروژه نیست و می‌توان پیش از تحویل حذفش کرد.
