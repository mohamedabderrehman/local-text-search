# Current release verification

Recorded on 2026-10-06 using disposable local data. Historical deployment is a separate owner-provided fact.

## Passed locally

All six Python regression/access tests passed: long lines and AND matching, zero/mixed-byte cases, a shared result budget across files, job ownership, unauthenticated search, and a 1,000-line matching regression. A measured Windows Python-only benchmark found exactly 800 matches in 800,000 generated lines (36,353,960 bytes); three runs took 10.2452, 10.9746 and 10.5983 seconds. OS caches were not flushed.

## Checks and commands

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

## CI status

The configured GitHub Actions workflows are registered, but the initial runs ended with startup_failure before any jobs or check annotations were created. Local results above are independent of CI. No passing CI badge is shown; the service supplied no further diagnostic message through the available API.

## Remaining platform and coverage limits

Cython equivalence, Linux worker behavior and interrupted-job recovery remain unverified. Included benchmark is Python-only on the documented Windows machine, not a speedup comparison. Optional Telegram ingestion is disabled for demos.

PHP checks used PHP 8.4.26; Node builds used Node 24.19; Python checks used Python 3.12.10 where applicable. This record does not claim production hardening, paid provider verification or tests on every platform.
