# Deployment and troubleshooting

## Historical status

Local corpus-processing and administration application. Public demos use generated text only.

تطبيق معالجة مجموعات نصوص محلية وإدارتها. يستخدم العرض نصوصاً مولدة فقط.

## Local release environment

Use fresh configuration, a disposable database/corpus and independently installed dependencies. This release never needs retired production services. Keep credentials, uploaded files, sessions, caches and signing material outside the public source. Credential removal does not revoke a provider key.

## Troubleshooting

### No files found

Put generated .txt files in configured CORPUS_DIR; paths resolve relative to the app.

### Session lost at restart

Provide a persistent SECRET_KEY environment value.

### Cython unavailable

Python fallback is supported; install a C compiler and acceleration requirements to compare.

### Telegram package missing

Leave ENABLE_TELEGRAM=0 unless you installed its optional requirements.

## Current limits

No unsupported speedup or terabyte-scale claim. Native acceleration needs a compiler. Interrupted-job recovery and non-Windows behavior require their own checks.

لا ندعي تسريعاً غير مقاس أو معالجة تيرابايت. يتطلب التسريع مترجماً. يحتاج التعافي من وظائف منقطعة والأنظمة الأخرى إلى فحوص مستقلة.
