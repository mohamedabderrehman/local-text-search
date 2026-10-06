# الواجهات ومسارات التنفيذ

ينشئ المستخدم بحثاً بعد الدخول ← يمسح العامل المجموعة الاصطناعية ← تُحدَّث الوظيفة والنتائج ← يتصفح المالك أو ينزل النتائج ← تراجع الإدارة الاستخدام.

تحتاج المسارات المحلية للموجه إلى بادئة الخادم. تستخدم مسارات PHP الملفات الفعلية ما لم توجد إعادة كتابة. المتحكمات والوسطاء في الشيفرة مرجع الحقول والصلاحيات. فحوص tools/check-demo تمثل طلبات حقيقية ببيانات اصطناعية وليست مزوداً وهمياً.

## مراجع التنفيذ

- [config.py](../config.py)
- [app.py](../app.py)
- [auth.py](../auth.py)
- [search_engine.py](../search_engine.py)
- [database.py](../database.py)
- [search_engine_cython.pyx](../search_engine_cython.pyx)

## حدود التكامل

لم يُفحص تطابق Cython وعمال Linux والتعافي من وظيفة منقطعة. القياس المرفق خاص بـPython على جهاز Windows الموثق وليس مقارنة تسريع. إدخال Telegram الاختياري معطل في العرض.


## جرد المسارات



## مثال الاستخدام

التطبيق واجهة Flask بجلسات. تنتمي الوظيفة للمستخدم الذي بدأها وتفرض الحالة وصفحات النتائج والتنزيل الملكية. تستخدم الكلمات المفصولة بمسافات مطابقة AND. تُحفظ النتائج بملفات وبيانات SQLite وليس فهرس بحث.

```sh
python bootstrap_demo.py
python app.py
# Sign in at /login, submit /search, open /job/<id>.
# Status: /api/job/<id>/status. Download: /job/<id>/download.
python -m unittest discover -s tests
```
