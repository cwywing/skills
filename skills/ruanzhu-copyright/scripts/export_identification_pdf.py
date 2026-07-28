# -*- coding: utf-8 -*-
"""
将程序/文档鉴别材料.docx 转为提交用 PDF（整本输出，不另存全文 PDF）。

页数目标（本项目约定）：
  - 程序鉴别材料.pdf：80～100 页（至少 80，不超过 100）
  - 文档鉴别材料.pdf：至少 60 页（可按材料完整性适当超出）

依赖：本机 Microsoft Word（win32com）、PyMuPDF（fitz）

用法:
    python export_identification_pdf.py --workdir docs/软著登记申请
    python export_identification_pdf.py --workdir docs/软著登记申请 --only program
    python export_identification_pdf.py --workdir docs/软著登记申请 --only document
"""

from __future__ import print_function

import argparse
import os
import sys
import time

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _paths import parse_workdir_arg  # noqa: E402

TARGETS = [
    {
        "key": "program",
        "docx": "程序鉴别材料.docx",
        "submit_pdf": "程序鉴别材料.pdf",
        "min_pages": 80,
        "max_pages": 100,
        "label": "程序鉴别材料",
    },
    {
        "key": "document",
        "docx": "文档鉴别材料.docx",
        "submit_pdf": "文档鉴别材料.pdf",
        "min_pages": 60,
        "max_pages": None,  # 可按完整性适当超出
        "label": "文档鉴别材料",
    },
]


def docx_to_pdf(docx_path, pdf_path):
    """用 Word COM 将 docx 另存为 PDF。"""
    import win32com.client  # type: ignore

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)
        if os.path.exists(abs_pdf):
            os.remove(abs_pdf)
        doc = word.Documents.Open(abs_docx, ReadOnly=True)
        # 17 = wdFormatPDF
        doc.SaveAs(abs_pdf, FileFormat=17)
        print("  已导出 PDF: {}".format(abs_pdf))
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()
        time.sleep(1)


def pdf_page_count(pdf_path):
    import fitz  # PyMuPDF

    src = fitz.open(pdf_path)
    total = src.page_count
    src.close()
    return total


def cleanup_legacy_full_pdf(material, item):
    """清理历史遗留的「*-全文.pdf」。"""
    legacy = os.path.join(
        material, item["submit_pdf"].replace(".pdf", "-全文.pdf")
    )
    if os.path.isfile(legacy):
        os.remove(legacy)
        print("  已清理遗留全文 PDF: {}".format(os.path.basename(legacy)))


def export_one(material, item):
    docx = os.path.join(material, item["docx"])
    submit_pdf = os.path.join(material, item["submit_pdf"])

    if not os.path.isfile(docx):
        print("跳过（未找到）: {}".format(docx))
        return False

    cleanup_legacy_full_pdf(material, item)

    print("[{}] Word -> PDF（整本）…".format(item["docx"]))
    docx_to_pdf(docx, submit_pdf)
    if not os.path.isfile(submit_pdf):
        print("  PDF 导出失败")
        return False

    total = pdf_page_count(submit_pdf)
    min_p = item.get("min_pages")
    max_p = item.get("max_pages")
    print("  页数: {}".format(total))

    if min_p is not None and total < min_p:
        print(
            "  警告: {} 当前 {} 页，低于目标下限 {} 页，请扩充素材后重导".format(
                item["label"], total, min_p
            )
        )
    elif max_p is not None and total > max_p:
        print(
            "  警告: {} 当前 {} 页，超过目标上限 {} 页，请精简素材后重导".format(
                item["label"], total, max_p
            )
        )
    else:
        if max_p is not None:
            print(
                "  达标: {} 页（目标 {}～{} 页）".format(total, min_p, max_p)
            )
        else:
            print("  达标: {} 页（目标 ≥{} 页）".format(total, min_p))

    print("  上传: {}".format(os.path.abspath(submit_pdf)))
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="导出程序/文档鉴别材料提交用 PDF")
    parser.add_argument("--workdir", required=True, help="软著工作目录")
    parser.add_argument(
        "--only",
        choices=("program", "document", "all"),
        default="all",
        help="只导出程序 / 只导出文档 / 全部（默认）",
    )
    # 保留旧参数以免外部调用报错，但不再做前/后截取
    parser.add_argument("--front", type=int, default=30, help=argparse.SUPPRESS)
    parser.add_argument("--back", type=int, default=30, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    paths = parse_workdir_arg(["--workdir", args.workdir])
    material = paths["material_dir"]

    ok = True
    for item in TARGETS:
        if args.only != "all" and item["key"] != args.only:
            continue
        if not export_one(material, item):
            ok = False

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
