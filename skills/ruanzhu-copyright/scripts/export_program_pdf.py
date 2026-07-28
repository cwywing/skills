# -*- coding: utf-8 -*-
"""兼容入口：转调 export_identification_pdf.py（程序+文档）。"""
from __future__ import print_function

import sys

from export_identification_pdf import main

if __name__ == "__main__":
    # 旧脚本默认只做程序；若未指定 --only 则导出全部
    argv = sys.argv[1:]
    if "--only" not in argv:
        argv = list(argv) + ["--only", "all"]
    main(argv)
