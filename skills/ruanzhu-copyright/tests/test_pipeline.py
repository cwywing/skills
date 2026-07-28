# -*- coding: utf-8 -*-
"""端到端：Phase 1 → 2b → 4，以及敏感信息 / Vue style 过滤。"""

from __future__ import print_function

import json
import os
import sys
import unittest
import runpy

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, TESTS_DIR)

from helpers import make_workdir, cleanup  # noqa: E402


def _run_script(script_name, workdir):
    """以独立 argv 执行脚本 main（静默 stdout/stderr）。"""
    import contextlib
    from io import StringIO

    path = os.path.join(SCRIPTS_DIR, script_name)
    old_argv = sys.argv[:]
    for mod in list(sys.modules.keys()):
        if mod in (
            "extract_codebase_data",
            "generate_program_identification",
            "md2docx",
            "redact_materials",
        ):
            del sys.modules[mod]
    buf = StringIO()
    try:
        sys.argv = [path, "--workdir", workdir]
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            runpy.run_path(path, run_name="__main__")
    except SystemExit as e:
        if e.code not in (0, None):
            raise AssertionError(
                "script {} failed code={} output:\n{}".format(
                    script_name, e.code, buf.getvalue()
                )
            )
    finally:
        sys.argv = old_argv


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.workdir = make_workdir()
        self.material = os.path.join(self.workdir, "md素材")

    def tearDown(self):
        cleanup(self.workdir)

    def test_phase1_extract(self):
        _run_script("extract_codebase_data.py", self.workdir)
        out = os.path.join(self.material, "codebase_data.json")
        self.assertTrue(os.path.isfile(out))
        with open(out, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["software_info"]["软件全称"], "测试商城软件")
        self.assertGreaterEqual(len(data.get("models", [])), 1)
        self.assertEqual(data["models"][0]["table"], "mcc_order")
        self.assertGreaterEqual(len(data.get("controllers", [])), 1)
        self.assertGreaterEqual(len(data.get("services", [])), 1)
        self.assertIn("order", data.get("routes", {}))
        self.assertGreaterEqual(len(data.get("frontend", {}).get("pages", [])), 1)

    def test_phase2b_program_md(self):
        _run_script("generate_program_identification.py", self.workdir)
        fe = os.path.join(self.material, "program_identification-1.md")
        be = os.path.join(self.material, "program_identification-2.md")
        self.assertTrue(os.path.isfile(fe))
        self.assertTrue(os.path.isfile(be))

        with open(fe, "r", encoding="utf-8") as f:
            fe_text = f.read()
        with open(be, "r", encoding="utf-8") as f:
            be_text = f.read()

        # Vue <style> 必须剔除
        self.assertNotIn("<style", fe_text.lower())
        self.assertIn("<template>", fe_text)
        self.assertIn("<script>", fe_text)
        self.assertIn("首页", fe_text)

        # 后端代码进文件 2
        self.assertIn("OrderController", be_text)
        self.assertIn("OrderServices", be_text)

        # 敏感信息过滤
        self.assertNotIn("secret-should-be-filtered", be_text)
        self.assertIn("[已移除敏感信息]", be_text)
        # JWT_SECRET 行应被替换
        self.assertNotIn("super-secret-key-abcdefgh", fe_text)

    def test_redact_materials(self):
        doc1 = os.path.join(self.material, "document_identification-1.md")
        with open(doc1, "a", encoding="utf-8") as f:
            f.write("\n由测试权利人开发。路径 C:/Users/demo/proj/app 与 https://example.com/x\n")
            f.write("权利人署名: 测试权利人\n")
        _run_script("redact_materials.py", self.workdir)
        with open(doc1, "r", encoding="utf-8") as f:
            text = f.read()
        self.assertIn("登记权利人", text)
        self.assertIn("权利人署名: 测试权利人", text)
        self.assertIn("[本地路径已省略]", text)
        self.assertIn("[URL已省略]", text)
        # 非署名行不应再残留「由测试权利人开发」
        self.assertNotIn("由测试权利人开发", text)

    def test_phase4_md2docx(self):
        _run_script("generate_program_identification.py", self.workdir)
        try:
            import docx  # noqa: F401
        except ImportError:
            self.skipTest("python-docx 未安装")

        _run_script("redact_materials.py", self.workdir)
        _run_script("md2docx.py", self.workdir)
        prog = os.path.join(self.material, "程序鉴别材料.docx")
        doc = os.path.join(self.material, "文档鉴别材料.docx")
        self.assertTrue(os.path.isfile(prog), "缺少程序鉴别材料.docx")
        self.assertTrue(os.path.isfile(doc), "缺少文档鉴别材料.docx")
        self.assertGreater(os.path.getsize(prog), 1000)
        self.assertGreater(os.path.getsize(doc), 500)

        from docx import Document

        d = Document(prog)
        header_text = "".join(p.text for p in d.sections[0].header.paragraphs)
        self.assertIn("测试商城软件", header_text)
        self.assertIn("V1.0", header_text)

    def test_full_pipeline(self):
        """Phase 1 + 2b + redact + 4 串联。"""
        try:
            import docx  # noqa: F401
        except ImportError:
            self.skipTest("python-docx 未安装")

        _run_script("extract_codebase_data.py", self.workdir)
        _run_script("generate_program_identification.py", self.workdir)
        _run_script("redact_materials.py", self.workdir)
        _run_script("md2docx.py", self.workdir)

        expected = [
            "codebase_data.json",
            "core_business_files.json",
            "program_identification-1.md",
            "program_identification-2.md",
            "程序鉴别材料.docx",
            "文档鉴别材料.docx",
        ]
        for name in expected:
            path = os.path.join(self.material, name)
            self.assertTrue(os.path.isfile(path), "missing {}".format(name))


class TestFiltersUnit(unittest.TestCase):
    def test_filter_sensitive_and_vue(self):
        sys.path.insert(0, SCRIPTS_DIR)
        # 直接导入函数
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "gen", os.path.join(SCRIPTS_DIR, "generate_program_identification.py")
        )
        gen = importlib.util.module_from_spec(spec)
        # 避免执行 main：spec.loader.exec_module 会定义函数但不跑 main（仅 if __name__）
        spec.loader.exec_module(gen)

        line = gen.filter_sensitive("    'password' => 'abc123',\n")
        self.assertIn("[已移除敏感信息]", line)

        path_line = gen.filter_sensitive("    $root = 'C:/Users/demo/proj';\n")
        self.assertIn("[已移除敏感信息]", path_line)

        vue_path = os.path.join(
            TESTS_DIR, "fixtures", "mini_frontend", "pages", "index", "index.vue"
        )
        lines = gen.read_vue_file(vue_path)
        text = "".join(lines)
        self.assertNotIn("<style", text.lower())
        self.assertIn("goOrder", text)


if __name__ == "__main__":
    unittest.main()
