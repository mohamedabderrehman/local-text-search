#!/bin/bash

echo "========================================"
echo "بناء Cython Module للبحث السريع"
echo "========================================"
echo ""

echo "تثبيت المتطلبات..."
pip install cython numpy

echo ""
echo "بناء Cython extension..."
python setup.py build_ext --inplace

echo ""
echo "========================================"
echo "تم البناء بنجاح!"
echo "========================================"
echo ""
echo "الآن يمكنك تشغيل: python app.py"
echo ""

