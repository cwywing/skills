# -*- coding: utf-8 -*-
"""
软著工作目录路径解析（供本目录下各脚本共用）。

约定工作目录结构:
    <workdir>/
      基础资料.md
      md素材/
        codebase_data.json
        core_business_files.json
        program_identification-*.md
        document_identification-*.md
        *.docx

用法:
    python <script>.py --workdir docs/软著登记申请
"""

from __future__ import print_function

import argparse
import os
import re
import sys


def parse_workdir_arg(argv=None):
    """解析 --workdir，返回绝对路径；未提供时尝试从 cwd 推断。"""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--workdir",
        default=None,
        help="软著工作目录（含 基础资料.md 与 md素材/）",
    )
    args, _ = parser.parse_known_args(argv if argv is not None else sys.argv[1:])

    if args.workdir:
        workdir = os.path.abspath(args.workdir)
    else:
        cwd = os.getcwd()
        if os.path.isfile(os.path.join(cwd, "基础资料.md")):
            workdir = cwd
        elif os.path.isfile(os.path.join(cwd, os.pardir, "基础资料.md")):
            workdir = os.path.abspath(os.path.join(cwd, os.pardir))
        else:
            print("错误: 请通过 --workdir 指定软著工作目录，或在工作目录下运行。")
            print("  示例: python extract_codebase_data.py --workdir docs/软著登记申请")
            print("  工作目录须包含 基础资料.md，脚本会读写其中的 md素材/。")
            sys.exit(1)

    if not os.path.isdir(workdir):
        print("错误: 工作目录不存在: {}".format(workdir))
        sys.exit(1)

    basic = os.path.join(workdir, "基础资料.md")
    if not os.path.isfile(basic):
        print("错误: 找不到基础资料文件: {}".format(basic))
        sys.exit(1)

    material = os.path.join(workdir, "md素材")
    if not os.path.isdir(material):
        os.makedirs(material)

    return {
        "workdir": workdir,
        "basic_info": basic,
        "material_dir": material,
    }


def read_text(filepath):
    """按常见编码读取文本。"""
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
        except FileNotFoundError:
            return ""
    return ""


def load_basic_info(basic_info_path):
    """
    解析基础资料.md，返回 (config_dict, info_dict)。
    # config 段写入 config；# pageN 及其他键值写入 info。
    """
    content = read_text(basic_info_path)
    if not content:
        return {}, {}

    config = {}
    info = {}
    in_config = False

    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("# 基础资料") or line.startswith(">"):
            continue
        if line == "# config":
            in_config = True
            continue
        if line.startswith("# page"):
            in_config = False
            continue
        if line.startswith("---") or line.startswith("##"):
            continue
        m = re.match(r"^(.+?)\s*:\s*(.+)$", line)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            if in_config:
                config[key] = value
            else:
                info[key] = value

    return config, info


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path
