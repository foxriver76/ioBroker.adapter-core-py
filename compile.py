# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# compile with python3 compile.py build_ext --inplace
ext_modules = [
    Extension('iobcore',  ['iobcore/adapter.py', 'iobcore/objects.py', 
                           'iobcore/objects_utils.py', 'iobcore/states.py'])    
    ]

setup(
    name = 'iobroker.adapter-core-py',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)