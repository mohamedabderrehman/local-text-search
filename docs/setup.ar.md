# الإعداد

أنشئ بيئة Python وثبّت requirements.txt ثم صدّر متغيرات .env.example وشغّل bootstrap_demo.py وrun.py. لا يقرأ Python ملف .env تلقائياً. للتسريع ثبّت متطلباته ونفذ build_ext بمترجم C صالح. يتطلب Telegram حزمه وENABLE_TELEGRAM=1 ويظل معطلاً في العرض.

## التفاصيل والأوامر

Create a Python virtual environment, install `pip install -r requirements.txt`, export the variables in `.env.example`, run `python bootstrap_demo.py`, then `python run.py`. Python does not automatically load `.env`; export values in your shell. For acceleration install `requirements.acceleration.txt` and run `python setup.py build_ext --inplace` with a working C compiler. Telegram requires `requirements.telegram.txt` and explicit `ENABLE_TELEGRAM=1`; it remains disabled for demos.

## متغيرات تقرأها الشيفرة

| Variable | Source consumer | Configuration rule |
|---|---|---|
| `ENABLE_TELEGRAM` | `config.py` | Use the local example/source default; adapt to your disposable environment. |
| `FLASK_HOST` | `config.py` | Use the local example/source default; adapt to your disposable environment. |
| `FLASK_PORT` | `config.py` | Use the local example/source default; adapt to your disposable environment. |
| `MAX_RESULTS` | `config.py` | Use the local example/source default; adapt to your disposable environment. |
| `SECRET_KEY` | `config.py` | Supply privately when enabling its integration; no secret default. |
| `TELEGRAM_API_HASH` | `run.py` | Supply privately when enabling its integration; no secret default. |
| `TELEGRAM_API_ID` | `run.py` | Use the local example/source default; adapt to your disposable environment. |
| `TELEGRAM_BOT_TOKEN` | `config.py` | Supply privately when enabling its integration; no secret default. |
| `TELEGRAM_CHANNEL` | `telegram_bot.py` | Use the local example/source default; adapt to your disposable environment. |
| `TELEGRAM_CHANNEL_ID` | `config.py` | Use the local example/source default; adapt to your disposable environment. |
| `TELEGRAM_USER_ID` | `telegram_bot.py` | Use the local example/source default; adapt to your disposable environment. |

لا تُحمَّل ملفات الأمثلة تلقائياً. تستخدم وحدات dotenv الملف حيث تكون مهيأة، ويستخدم PHP بيئة العملية أو الاستضافة. افصل المزودين عن العرض وأنشئ أسراراً جديدة واحفظها خارج المستودع.

## أوامر المكونات
