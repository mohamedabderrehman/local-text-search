# Clean setup

Use Python 3.12 for the recorded checks. Export .env.example values into the process; config.py resolves relative paths from the application root. Set a persistent SECRET_KEY for sessions and ENABLE_TELEGRAM=0. bootstrap_demo.py prompts for a fresh 12-character administrator password and writes generated text only when absent. Cython is optional and requires a compiler; Python remains the default verified path.

## Commands

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

## Complete configuration inventory

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


Variables in the inventory are not all mandatory: the preceding prerequisites identify the required core values. Provider variables are required only for their enabled live integration. Tests may use DEMO_API_URL to override the local target. Never point bootstrap/reset/check scripts at a production database.
