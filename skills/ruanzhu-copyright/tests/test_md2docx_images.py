# -*- coding: utf-8 -*-
"""md2docx 插图行距、--only 不覆盖另一份。"""

from __future__ import print_function

import os
import sys
import unittest
import runpy
import contextlib
from io import StringIO

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, TESTS_DIR)

from helpers import make_workdir, cleanup, write_tiny_png  # noqa: E402


def _run_md2docx(workdir, extra_args=None):
    path = os.path.join(SCRIPTS_DIR, "md2docx.py")
    old_argv = sys.argv[:]
    if "md2docx" in sys.modules:
        del sys.modules["md2docx"]
    buf = StringIO()
    try:
        sys.argv = [path, "--workdir", workdir]
        if extra_args:
            sys.argv.extend(extra_args)
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            runpy.run_path(path, run_name="__main__")
        return buf.getvalue()
    except SystemExit as e:
        if e.code not in (0, None):
            raise AssertionError(
                "md2docx failed code={} output:\n{}".format(e.code, buf.getvalue())
            )
        return buf.getvalue()
    finally:
        sys.argv = old_argv


class TestMd2DocxImages(unittest.TestCase):
    def setUp(self):
        try:
            import docx  # noqa: F401
        except ImportError:
            self.skipTest("python-docx 未安装")
        self.workdir = make_workdir()
        self.material = os.path.join(self.workdir, "md素材")

    def tearDown(self):
        cleanup(self.workdir)

    def test_image_uses_single_line_spacing_and_real_height(self):
        shots = os.path.join(self.material, "screenshots")
        png = os.path.join(shots, "demo.png")
        write_tiny_png(png, width=80, height=160)

        doc_md = os.path.join(self.material, "document_identification-1.md")
        with open(doc_md, "a", encoding="utf-8") as f:
            f.write("\n![图1-0 测试界面](screenshots/demo.png)\n")

        out = _run_md2docx(self.workdir, ["--only", "document"])
        self.assertIn("[插图]", out)

        from docx import Document
        from docx.enum.text import WD_LINE_SPACING

        docx_path = os.path.join(self.material, "文档鉴别材料.docx")
        self.assertTrue(os.path.isfile(docx_path))
        d = Document(docx_path)
        self.assertGreaterEqual(len(d.inline_shapes), 1)
        height_cm = d.inline_shapes[0].height.cm
        self.assertGreater(
            height_cm,
            5.0,
            "插图高度过小（{}cm），疑似被固定行距压扁".format(height_cm),
        )

        found = False
        for p in d.paragraphs:
            drawings = p._p.findall(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline"
            )
            if not drawings:
                continue
            self.assertEqual(p.paragraph_format.line_spacing, 1.0)
            self.assertEqual(
                p.paragraph_format.line_spacing_rule, WD_LINE_SPACING.SINGLE
            )
            found = True
            break
        self.assertTrue(found, "未找到含图片的段落")

        # --only document 不应生成程序稿
        self.assertFalse(
            os.path.isfile(os.path.join(self.material, "程序鉴别材料.docx"))
        )

    def test_only_document_does_not_overwrite_program(self):
        marker = os.path.join(self.material, "程序鉴别材料.docx")
        with open(marker, "wb") as f:
            f.write(b"PROGRAM-PLACEHOLDER")
        before = open(marker, "rb").read()

        _run_md2docx(self.workdir, ["--only", "document"])

        after = open(marker, "rb").read()
        self.assertEqual(before, after)
        self.assertTrue(
            os.path.isfile(os.path.join(self.material, "文档鉴别材料.docx"))
        )


if __name__ == "__main__":
    unittest.main()
