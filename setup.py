"""
Setup script لبناء Cython extension
"""
from setuptools import setup, Extension
from Cython.Build import cythonize
import sys

# إعدادات التجميع حسب النظام
if sys.platform == 'win32':
    compile_args = ['/O2', '/GL']  # Windows optimization
    link_args = ['/LTCG']
else:
    compile_args = ['-O3', '-march=native', '-ffast-math']  # Linux/Mac optimization
    link_args = []

extensions = [
    Extension(
        "search_engine_cython",
        ["search_engine_cython.pyx"],
        extra_compile_args=compile_args,
        extra_link_args=link_args,
    )
]

setup(
    name='Search Engine Cython',
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'cdivision': True,
        'initializedcheck': False,
    }),
    zip_safe=False,
)
