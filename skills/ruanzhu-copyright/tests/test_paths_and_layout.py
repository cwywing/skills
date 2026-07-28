# -*- coding: utf-8 -*-
"""_paths.py 与 skill 目录结构测试。"""

from __future__ import print_function

import os
import sys
import tempfile
import unittest
import shutil

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from _paths import parse_workdir_arg, load_basic_info  # noqa: E402
from helpers import make_workdir, cleanup, ASSETS  # noqa: E402


class TestPaths(unittest.TestCase):
    def test_parse_workdir_arg(self):
        workdir = make_workdir()
        try:
            meta = parse_workdir_arg(["--workdir", workdir])
            self.assertEqual(meta["workdir"], os.path.abspath(workdir))
            self.assertTrue(os.path.isfile(meta["basic_info"]))
            self.assertTrue(os.path.isdir(meta["material_dir"]))
        finally:
            cleanup(workdir)

    def test_parse_workdir_missing_exits(self):
        import contextlib
        from io import StringIO

        missing = os.path.join(tempfile.gettempdir(), "ruanzhu_no_such_dir_xyz")
        buf = StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                parse_workdir_arg(["--workdir", missing])

    def test_load_basic_info(self):
        workdir = make_workdir()
        try:
            config, info = load_basic_info(os.path.join(workdir, "基础资料.md"))
            self.assertIn("后端项目根目录", config)
            self.assertTrue(os.path.isdir(config["后端项目根目录"]))
            self.assertEqual(info.get("软件全称"), "测试商城软件")
            self.assertEqual(info.get("版本号"), "V1.0")
        finally:
            cleanup(workdir)


class TestSkillLayout(unittest.TestCase):
    REQUIRED = [
        "SKILL.md",
        "README.md",
        "scripts/_paths.py",
        "scripts/extract_codebase_data.py",
        "scripts/generate_program_identification.py",
        "scripts/md2docx.py",
        "scripts/redact_materials.py",
        "scripts/export_identification_pdf.py",
        "scripts/requirements.txt",
        "assets/基础资料.template.md",
        "assets/core_business_files.template.json",
        "assets/document_prompt.md",
        "references/workflow-phases.md",
        "references/application-form-fields.md",
        "references/content-redaction.md",
        "references/core-file-selection.md",
        "references/document-generation.md",
        "references/framework-adapters.md",
        "references/quality-checklist.md",
        "references/submission-rules.md",
    ]

    def test_required_files_exist(self):
        for rel in self.REQUIRED:
            path = os.path.join(SKILL_ROOT, rel.replace("/", os.sep))
            self.assertTrue(os.path.isfile(path), "missing: {}".format(rel))

    def test_skill_frontmatter(self):
        with open(os.path.join(SKILL_ROOT, "SKILL.md"), "r", encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.startswith("---"))
        self.assertIn("name: ruanzhu-copyright", text)
        self.assertIn("description:", text)
        self.assertIn("软著", text)
        self.assertIn("--workdir", text)

    def test_assets_template_has_config_keys(self):
        path = os.path.join(ASSETS, "基础资料.template.md")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        for key in ("后端项目根目录", "前端项目根目录", "软件全称", "版本号", "著作权人"):
            self.assertIn(key, text)
        self.assertIn("后端项目根目录: .", text)
        self.assertIn("权利人署名", text)
        self.assertIn("500～1300", text)
        self.assertIn("≤50字", text)

    def test_document_prompt_flow_first(self):
        path = os.path.join(ASSETS, "document_prompt.md")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        self.assertIn("项目背景", text)
        self.assertIn("总体业务蓝图", text)
        self.assertIn("按流程详解", text)
        self.assertIn("禁止模块优先", text)

    def test_skill_hard_constraints(self):
        with open(os.path.join(SKILL_ROOT, "SKILL.md"), "r", encoding="utf-8") as f:
            text = f.read()
        self.assertIn("redact_materials.py", text)
        self.assertIn("export_identification_pdf.py", text)
        self.assertIn("application-form-fields.md", text)
        self.assertIn("背景→蓝图→流程→模块", text)
        self.assertIn("content-redaction.md", text)
        self.assertIn("1.2.0", text)


if __name__ == "__main__":
    unittest.main()
