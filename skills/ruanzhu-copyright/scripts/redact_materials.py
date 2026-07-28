# -*- coding: utf-8 -*-
"""
Phase 4 前置：对 md素材 中的程序/文档鉴别 MD 做脱敏。

- 去除/替换基础资料中的著作权人（说明书默认不出现单位全称）
- 替换本机绝对路径
- 替换常见生产 URL / 邮箱形态
- 可选：替换 --names 指定的人名（导出材料内，不改业务仓库）

用法:
    python redact_materials.py --workdir docs/软著登记申请
    python redact_materials.py --workdir docs/软著登记申请 --keep-org
    python redact_materials.py --workdir docs/软著登记申请 --names 张三,李四
"""
from __future__ import print_function

import os
import re
import sys

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _paths import parse_workdir_arg, load_basic_info  # noqa: E402


PATH_PATTERNS = [
    # Windows 盘符路径（排除 https:// 这类「字母://」）
    (re.compile(r"[A-Za-z]:\\[^\s\"'<>|]+"), "[本地路径已省略]"),
    (re.compile(r"[A-Za-z]:/(?!/)[^\s\"'<>|]+"), "[本地路径已省略]"),
    (re.compile(r"/Users/[^\s\"'<>|]+"), "[本地路径已省略]"),
    (re.compile(r"/home/[^\s\"'<>|]+"), "[本地路径已省略]"),
]

OTHER_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[邮箱已省略]"),
    (re.compile(r"https?://[^\s\)\"'<>]+"), "[URL已省略]"),
]


def _org_name_variants(org):
    """单位名常见全角/半角括号与空白变体，避免源码落款漏脱。"""
    org = (org or "").strip()
    if not org:
        return []
    variants = [org]
    # 全角括号 ↔ 半角括号
    variants.append(org.replace("（", "(").replace("）", ")"))
    variants.append(org.replace("(", "（").replace(")", "）"))
    # 去空白后再还原一对括号形态
    compact = re.sub(r"\s+", "", org)
    if compact and compact not in variants:
        variants.append(compact)
        variants.append(compact.replace("（", "(").replace("）", ")"))
        variants.append(compact.replace("(", "（").replace(")", "）"))
    # 长到短替换，避免短串误伤
    uniq = []
    for v in variants:
        if v and v not in uniq:
            uniq.append(v)
    uniq.sort(key=len, reverse=True)
    return uniq


def redact_text(text, org_name, names, keep_org):
    """脱敏正文；保留首页「权利人署名:」行中的著作权人全称。"""
    if org_name and not keep_org and org_name.strip():
        variants = _org_name_variants(org_name)
        out_lines = []
        for line in text.splitlines(True):
            # 首页登记署名行必须与申请表一致，不做替换
            if re.match(r"^\s*权利人署名\s*[:：]", line):
                out_lines.append(line)
            else:
                for org in variants:
                    line = line.replace(org, "登记权利人")
                out_lines.append(line)
        text = "".join(out_lines)
    # 先处理 URL/邮箱，避免 https:// 被盘符路径规则误伤
    for pat, repl in OTHER_PATTERNS:
        text = pat.sub(repl, text)
    for pat, repl in PATH_PATTERNS:
        text = pat.sub(repl, text)
    for name in names:
        name = name.strip()
        if len(name) >= 2:
            text = text.replace(name, "[人员已省略]")
    return text


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    keep_org = "--keep-org" in argv
    names = []
    if "--names" in argv:
        i = argv.index("--names")
        if i + 1 < len(argv):
            names = [x for x in argv[i + 1].split(",") if x.strip()]

    paths = parse_workdir_arg(argv)
    _, info = load_basic_info(paths["basic_info"])
    org = info.get("著作权人", "") or ""

    material = paths["material_dir"]
    targets = []
    for fn in os.listdir(material):
        if not fn.endswith(".md"):
            continue
        if fn.startswith("document_identification") or fn.startswith(
            "program_identification"
        ):
            targets.append(os.path.join(material, fn))
        if fn == "功能模块梳理.md":
            targets.append(os.path.join(material, fn))

    if not targets:
        print("警告: 未找到 document_/program_identification MD")
        return 0

    print("著作权人脱敏:", "保留" if keep_org else "替换为「登记权利人」", "({0})".format(org or "空"))
    print("额外人名:", names or "无")
    for fp in sorted(targets):
        with open(fp, "r", encoding="utf-8") as f:
            raw = f.read()
        new = redact_text(raw, org, names, keep_org)
        if new != raw:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new)
            print("  已脱敏:", os.path.basename(fp))
        else:
            print("  无变更:", os.path.basename(fp))

    # codebase_data.json: drop 著作权人 from software_info to avoid re-injection
    json_path = os.path.join(material, "codebase_data.json")
    if os.path.isfile(json_path) and not keep_org:
        try:
            import json

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            si = data.get("software_info") or {}
            if "著作权人" in si:
                del si["著作权人"]
                data["software_info"] = si
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("  已从 codebase_data.json 移除 software_info.著作权人")
        except Exception as e:
            print("  跳过 JSON 处理:", e)

    print("完成。请接着运行 md2docx.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
