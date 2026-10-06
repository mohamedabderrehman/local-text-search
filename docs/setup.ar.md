# الإعداد الكامل

استخدم Python 3.12 للفحوص المسجلة. صدّر قيم .env.example إلى العملية؛ يحل config.py المسارات النسبية من جذر التطبيق. اضبط SECRET_KEY ثابتاً للجلسات وENABLE_TELEGRAM=0. يطلب bootstrap_demo.py كلمة مدير جديدة بطول 12 ويكتب النص المولد إذا لم يكن موجوداً فقط. Cython اختياري يحتاج مترجماً؛ Python هو المسار الافتراضي المفحوص.

## الأوامر

```sh
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
python bootstrap_demo.py
python app.py
# Separate terminal with the same virtual environment:
python -m unittest discover -s tests
python tools/benchmark.py
# Optional acceleration (requires a compiler):
python -m pip install -r requirements.acceleration.txt
python setup.py build_ext --inplace
python -m unittest discover -s tests
```

## جرد الإعداد

| المتغير | موضع الاستخدام | قاعدة الإعداد |
|---|---|---|
| `ENABLE_TELEGRAM` | `config.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `FLASK_HOST` | `config.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `FLASK_PORT` | `config.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `MAX_RESULTS` | `config.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `SECRET_KEY` | `config.py` | قدم القيمة بصورة خاصة عند تفعيل التكامل، دون سر افتراضي. |
| `TELEGRAM_API_HASH` | `run.py` | قدم القيمة بصورة خاصة عند تفعيل التكامل، دون سر افتراضي. |
| `TELEGRAM_API_ID` | `run.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `TELEGRAM_BOT_TOKEN` | `config.py` | قدم القيمة بصورة خاصة عند تفعيل التكامل، دون سر افتراضي. |
| `TELEGRAM_CHANNEL` | `telegram_bot.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `TELEGRAM_CHANNEL_ID` | `config.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |
| `TELEGRAM_USER_ID` | `telegram_bot.py` | استخدم المثال المحلي أو افتراضي الشيفرة واضبطه للبيئة المؤقتة. |

ليست كل متغيرات الجرد إلزامية. تحدد الفقرة الأولى قيم التشغيل الأساسية، وتلزم قيم المزود للتكامل الحي المفعل فقط. تتجاوز DEMO_API_URL هدف الفحص المحلي عند دعمه. لا توجه أوامر التعبئة والاستعادة والفحص لقاعدة إنتاج. لا تُحمّل أمثلة البيئة نفسها تلقائياً؛ جهز بيئة العملية أو dotenv حيث يستخدمه المكون.

## المكونات

| المكون | المسؤولية |
|---|---|
| `app.py` | مسارات Flask وتنظيم الوظائف وعرض النتائج |
| `search_engine.py` | مسح mmap واختيار العمال |
| `database.py` | بيانات مستخدمي ووظائف ونتائج SQLite |
| `auth.py` | تجزئة bcrypt وأدوات الصلاحيات |
| `search_engine_cython.pyx` | مطابقة اختيارية مسرعة |
| `bootstrap_demo.py` | إنشاء متن اصطناعي وحساب إدارة |
