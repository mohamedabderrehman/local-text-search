# API and execution paths

This index is extracted from the current source. Router-local paths require their mount prefix from the server entry point. PHP endpoint paths map directly to files unless Apache rewrites them. Controllers and auth middleware are authoritative for request bodies and permissions.

See the source entry points below; this project does not declare Express/Flask router paths.

## Source entry points

- [config.py](../config.py)
- [app.py](../app.py)
- [auth.py](../auth.py)
- [search_engine.py](../search_engine.py)
- [database.py](../database.py)
- [search_engine_cython.pyx](../search_engine_cython.pyx)

## الاستخدام

المسارات المذكورة محلية للموجه وتحتاج بادئة الربط في الخادم. ملفات PHP هي مرجع المسارات ما لم تُعَد كتابتها. استخدم بيانات اصطناعية وفحوص الصلاحيات الموجودة في الشيفرة.


## Representative usage

The application is a session-based Flask interface. A job belongs to its initiating user; status, result pages and downloads enforce that ownership. Keywords separated by spaces use AND matching. Results are files plus SQLite metadata rather than a search index.

```sh
python bootstrap_demo.py
python app.py
# Sign in at /login, submit /search, open /job/<id>.
# Status: /api/job/<id>/status. Download: /job/<id>/download.
python -m unittest discover -s tests
```
