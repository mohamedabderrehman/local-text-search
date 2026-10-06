# Setup and configuration

Create a Python virtual environment, install `pip install -r requirements.txt`, export the variables in `.env.example`, run `python bootstrap_demo.py`, then `python run.py`. Python does not automatically load `.env`; export values in your shell. For acceleration install `requirements.acceleration.txt` and run `python setup.py build_ext --inplace` with a working C compiler. Telegram requires `requirements.telegram.txt` and explicit `ENABLE_TELEGRAM=1`; it remains disabled for demos.

## Environment variables read by source

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

Environment examples do not load themselves. Node dotenv modules read local `.env` where configured; PHP uses its process/hosting environment. Keep provider integrations disconnected for demos. Generate a new secret with `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"` or equivalent, then store it privately.

## Declared component commands



## Source boundaries

| Component | Responsibility |
|---|---|
| `app.py` | Flask routes, job orchestration and result views |
| `search_engine.py` | mmap scanning and worker selection |
| `database.py` | SQLite users/jobs/results metadata |
| `auth.py` | bcrypt and role helpers |
| `search_engine_cython.pyx` | Optional accelerated matching |
| `bootstrap_demo.py` | Synthetic corpus/admin bootstrap |
