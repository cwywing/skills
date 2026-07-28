# -*- coding: utf-8 -*-
"""
程序鉴别材料生成脚本（v2）
从 core_business_files.json 读取核心业务文件清单，生成软著程序鉴别材料。

与 v1 的区别：
  - 不再全量扫描目录，改为读取 LLM 筛选后的文件清单
  - Vue 文件自动剔除 <style> 块，只保留 <template> + <script>
  - 后端文件保持全量读取

用法:
    python generate_program_identification.py --workdir docs/软著登记申请
"""

from __future__ import print_function

import os
import re
import json
import sys

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _paths import parse_workdir_arg, load_basic_info  # noqa: E402

BASIC_INFO_FILE = ""
FILE_LIST_JSON = ""
OUTPUT_DIR = ""


def load_paths():
    """从基础资料.md读取路径配置"""
    config, info = load_basic_info(BASIC_INFO_FILE)
    backend_root = config.get("后端项目根目录", "")
    frontend_root = config.get("前端项目根目录", "")
    if not backend_root:
        print("错误: 基础资料.md 中缺少 '后端项目根目录' 配置")
        return None, None, info
    return backend_root, frontend_root, info


SENSITIVE_PATTERNS = [
    r"'password'\s*=>\s*'[^']*'",
    r'"password"\s*:\s*"[^"]*"',
    r"DB_PASSWORD\s*=\s*.+",
    r"APP_KEY\s*=\s*.+",
    r"JWT_SECRET\s*=\s*.+",
    r"WECHAT_PAYMENT_MERCHANT_KEY\s*=\s*.+",
    r"appsecret\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    r"appkey_ios\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    r"appkey_android\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    r"secret\s*[=:]\s*['\"][a-z0-9]{16,}['\"]",
    r"key\s*[=:]\s*['\"][A-Z0-9\-]{20,}['\"]",
    # 本机绝对路径（导出程序材料时屏蔽；排除 https://）
    r"[A-Za-z]:\\[^\s\"']+",
    r"[A-Za-z]:/(?!/)[^\s\"']+",
    r"/Users/[^\s\"']+",
    r"/home/[^\s\"']+",
]


def filter_sensitive(line):
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            indent = len(line) - len(line.lstrip())
            return " " * indent + "/* [已移除敏感信息] */\n"
    return line


def read_file_raw(filepath):
    if not os.path.exists(filepath):
        return None
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    return None


def read_file(filepath):
    content = read_file_raw(filepath)
    if content is None:
        return []
    lines = content.splitlines(True)
    return [filter_sensitive(line) for line in lines]


def read_vue_file(filepath):
    content = read_file_raw(filepath)
    if content is None:
        return []
    content = re.sub(
        r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL | re.IGNORECASE
    )
    lines = content.splitlines(True)
    lines = [filter_sensitive(line) for line in lines]
    result = []
    empty_count = 0
    for line in lines:
        if line.strip() == "":
            empty_count += 1
            if empty_count <= 2:
                result.append(line)
        else:
            empty_count = 0
            result.append(line)
    return result


def load_file_list():
    if not os.path.exists(FILE_LIST_JSON):
        print("错误: 找不到文件清单 {}".format(FILE_LIST_JSON))
        print("请先让 LLM 分析生成 core_business_files.json")
        return None
    with open(FILE_LIST_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def section_header(title):
    return [
        "\n",
        "/* ======= {} ======= */\n".format(title),
        "\n",
    ]


def _lang_for_ext(ext):
    ext = ext.lower()
    mapping = {
        ".vue": "vue",
        ".js": "javascript",
        ".ts": "typescript",
        ".json": "json",
        ".php": "php",
        ".py": "python",
        ".java": "java",
        ".go": "go",
        ".cs": "csharp",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
        ".dart": "dart",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sql": "sql",
    }
    return mapping.get(ext, "text")


def collect_all_lines(frontend_root, backend_root, file_list_data, info):
    all_lines = []
    sw_name = info.get("软件全称", "软件")
    sw_ver = info.get("版本号", "V1.0")

    frontend_files = file_list_data.get("前端文件", [])
    has_frontend = bool(frontend_root and frontend_files)
    composition = (
        "由前端代码与后端代码组成"
        if has_frontend
        else "由后端程序源代码组成"
    )
    owner = info.get("著作权人", "") or ""
    all_lines += [
        "# 程序鉴别材料（程序源代码）\n",
        "\n",
        "## 说明\n",
        "以下内容为本软件的程序源代码材料，{}，代码结构清晰、可运行，不包含敏感信息。\n".format(
            composition
        ),
        "\n",
        "权利人署名: {}\n".format(owner),
        "软件名称: {}\n".format(sw_name),
        "软件版本号: {}\n".format(sw_ver),
        "\n",
        "---\n",
        "\n",
        "## 源代码正文\n",
        "\n",
    ]

    if has_frontend:
        all_lines += ["### 一、前端代码\n", "\n"]

    frontend_total = 0
    frontend_count = 0
    for item in frontend_files:
        category = item["分类"]
        rel_path = item["路径"]
        full_path = (
            os.path.join(frontend_root, rel_path.replace("/", os.sep))
            if frontend_root
            else ""
        )
        if not full_path or not os.path.exists(full_path):
            print("  [跳过] 前端文件不存在: {}".format(rel_path))
            continue

        ext = os.path.splitext(rel_path)[1].lower()
        short_name = os.path.splitext(os.path.basename(rel_path))[0]
        label = "{}：{}".format(category, rel_path.replace("/", os.sep))

        if ext == ".vue":
            lines = read_vue_file(full_path)
        else:
            lines = read_file(full_path)
        if not lines:
            continue

        lang = _lang_for_ext(ext)
        all_lines += section_header(label)
        all_lines += ["```{}\n".format(lang)]
        all_lines += lines
        if not lines[-1].endswith("\n"):
            all_lines += ["\n"]
        all_lines += ["```\n", "\n"]
        frontend_total += len(lines)
        frontend_count += 1
        print("  [前端] {}: {} 行".format(label, len(lines)))

    backend_files = file_list_data.get("后端文件", [])
    backend_heading = "### 二、后端代码\n" if has_frontend else "### 后端代码\n"
    all_lines += [backend_heading, "\n"]

    backend_total = 0
    backend_count = 0
    for item in backend_files:
        category = item["分类"]
        rel_path = item["路径"]
        full_path = os.path.join(backend_root, rel_path.replace("/", os.sep))
        if not os.path.exists(full_path):
            print("  [跳过] 后端文件不存在: {}".format(rel_path))
            continue

        lines = read_file(full_path)
        if not lines:
            continue

        ext = os.path.splitext(rel_path)[1].lower()
        short_name = os.path.splitext(os.path.basename(rel_path))[0]
        label = "{}：{}".format(category, rel_path.replace("/", os.sep))

        all_lines += section_header(label)
        all_lines += ["```{}\n".format(_lang_for_ext(ext))]
        all_lines += lines
        if not lines[-1].endswith("\n"):
            all_lines += ["\n"]
        all_lines += ["```\n", "\n"]
        backend_total += len(lines)
        backend_count += 1
        print("  [后端] {}: {} 行".format(label, len(lines)))

    total = frontend_total + backend_total
    pages = total // 50 if total else 0
    all_lines += [
        "\n",
        "---\n",
        "\n",
        "## 代码统计\n",
        "\n",
        "| 项目       | 文件数 | 行数     | 估算页数（50行/页） |\n",
        "|------------|--------|----------|---------------------|\n",
        "| 前端代码   | {} 个 | {} 行 | 约 {} 页 |\n".format(
            frontend_count, frontend_total, frontend_total // 50
        ),
        "| 后端代码   | {} 个 | {} 行 | 约 {} 页 |\n".format(
            backend_count, backend_total, backend_total // 50
        ),
        "| **合计**   | **{} 个** | **{} 行** | **约 {} 页** |\n".format(
            frontend_count + backend_count, total, pages
        ),
        "\n",
    ]

    be_ratio = (backend_total / total * 100) if total else 0
    print(
        "\n统计: 前端 {} 个文件 {} 行 | 后端 {} 个文件 {} 行 | 合计 {} 行，估算 {} 页，后端占比 {:.1f}%".format(
            frontend_count,
            frontend_total,
            backend_count,
            backend_total,
            total,
            pages,
            be_ratio,
        )
    )
    if total and be_ratio < 40:
        print("警告: 后端代码占比低于 40%，建议调整 core_business_files.json")
    if total and (pages < 80 or pages > 100):
        print(
            "提示: 程序 PDF 目标 80～100 页。脚本按约 50 行/页估算为 {} 页（{} 行）；"
            "实际 Word 常约 55～70 行/页，请以 export_identification_pdf 实测为准再加减文件。".format(
                pages, total
            )
        )
    return all_lines


def write_split_files(all_lines):
    backend_start = None
    for i, line in enumerate(all_lines):
        if "### 二、后端代码" in line or line.strip() == "### 后端代码":
            backend_start = i
            break

    written_files = []
    fe_chunk = all_lines[:backend_start] if backend_start else all_lines
    fname = os.path.join(OUTPUT_DIR, "program_identification-1.md")
    with open(fname, "w", encoding="utf-8") as f:
        f.writelines(fe_chunk)
    print("  => 写入 program_identification-1.md ({} 行) [前端]".format(len(fe_chunk)))
    written_files.append(fname)

    if backend_start:
        be_chunk = all_lines[backend_start:]
        fname = os.path.join(OUTPUT_DIR, "program_identification-2.md")
        with open(fname, "w", encoding="utf-8") as f:
            f.writelines(be_chunk)
        print(
            "  => 写入 program_identification-2.md ({} 行) [后端]".format(len(be_chunk))
        )
        written_files.append(fname)

    for idx in range(3, 7):
        old = os.path.join(OUTPUT_DIR, "program_identification-{}.md".format(idx))
        if os.path.exists(old):
            os.remove(old)
            print("  => 清理旧文件: program_identification-{}.md".format(idx))

    return written_files


def main():
    global BASIC_INFO_FILE, FILE_LIST_JSON, OUTPUT_DIR

    paths_meta = parse_workdir_arg()
    BASIC_INFO_FILE = paths_meta["basic_info"]
    OUTPUT_DIR = paths_meta["material_dir"]
    FILE_LIST_JSON = os.path.join(OUTPUT_DIR, "core_business_files.json")

    backend_root, frontend_root, info = load_paths()
    if not backend_root:
        sys.exit(1)

    sw_name = info.get("软件全称", "软件")
    sw_ver = info.get("版本号", "V1.0")

    print("=" * 60)
    print("程序鉴别材料生成脚本 v2")
    print("工作目录: {}".format(paths_meta["workdir"]))
    print("项目: {} {}".format(sw_name, sw_ver))
    print("后端: {}".format(backend_root))
    if frontend_root:
        print("前端: {}".format(frontend_root))
    print("=" * 60)

    print("\n[1/3] 加载核心业务文件清单...")
    file_list_data = load_file_list()
    if not file_list_data:
        sys.exit(1)
    print("  前端: {} 个文件".format(len(file_list_data.get("前端文件", []))))
    print("  后端: {} 个文件".format(len(file_list_data.get("后端文件", []))))

    print("\n[2/3] 收集源代码（.vue 自动剔除 <style>；其他扩展名整文件读入）...")
    all_lines = collect_all_lines(frontend_root, backend_root, file_list_data, info)
    print("\n共收集 {} 行内容".format(len(all_lines)))

    print("\n[3/3] 写入分段文件...")
    files = write_split_files(all_lines)

    print("\n" + "=" * 60)
    print("生成完成！共 {} 个文件：".format(len(files)))
    for f in files:
        print("  {}".format(os.path.basename(f)))
    print("=" * 60)


if __name__ == "__main__":
    main()
