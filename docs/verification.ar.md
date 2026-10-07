# التحقق من الإصدار الحالي

سجل 2026-10-06 ببيانات محلية مؤقتة. يوثق هذا الملف فحوص التطوير منفصلة عن النشر السابق.

## الفحوص المحلية الناجحة

نجحت اختبارات Python الستة: الأسطر الطويلة ومطابقة AND وعدم وجود نتائج والبايتات المختلطة وحد نتائج مشترك بين الملفات وملكية الوظيفة ورفض البحث دون دخول وفحص تراجع على ألف سطر. وجد قياس Windows دون Cython 800 نتيجة في 800 ألف سطر مولد بحجم 36,353,960 بايت؛ الأوقات 10.2452 و10.9746 و10.5983 ثانية دون تفريغ مخبأ النظام.

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

## حالة CI

سُجلت مسارات GitHub Actions لكن المحاولات الأولى انتهت بـstartup_failure قبل إنشاء أي وظيفة أو ملاحظة فحص. النتائج المحلية أعلاه مستقلة عن CI. لا نعرض شارة نجاح ولم توفر الواجهة المتاحة سبباً تفصيلياً.

## حدود المنصة والتغطية

لم يُفحص تطابق Cython وعمال Linux والتعافي من وظيفة منقطعة. القياس المرفق خاص بـPython على جهاز Windows الموثق وليس مقارنة تسريع. إدخال Telegram الاختياري معطل في العرض.

استُخدم PHP 8.4.26 وNode 24.19 وPython 3.12.10 حيث ينطبق. لا يثبت السجل جاهزية إنتاج شاملة أو فحص مزود مدفوع أو جميع المنصات.
