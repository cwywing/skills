# -*- coding: utf-8 -*-
"""运行 skill 全部测试。

用法（在任意目录）:
    python .cursor/skills/ruanzhu-copyright/tests/run_tests.py
"""

from __future__ import print_function

import os
import sys
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    sys.path.insert(0, TESTS_DIR)
    suite = unittest.defaultTestLoader.discover(TESTS_DIR, pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
