import os
import sys

import mold

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'test':
    try:
        __import__('py')
    except ImportError:
        # If pytest is not available, just run the tests natively
        test_bin = 'python'
    else:
        # Use pytest if available
        test_bin = 'py.test'
    errors = os.system('{test_bin} test.py'.format(test_bin=test_bin))
    sys.exit(bool(errors))
