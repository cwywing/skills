# -*- coding: utf-8 -*-
"""测试辅助：构建临时软著工作目录与迷你前后端路径。"""

from __future__ import print_function

import json
import os
import shutil
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
FIXTURES = os.path.join(TESTS_DIR, "fixtures")
ASSETS = os.path.join(SKILL_ROOT, "assets")


def backend_root():
    return os.path.join(FIXTURES, "mini_backend")


def frontend_root():
    return os.path.join(FIXTURES, "mini_frontend")


def make_workdir():
    """创建临时 workdir，写入基础资料与 core_business_files.json。"""
    workdir = tempfile.mkdtemp(prefix="ruanzhu_test_")
    material = os.path.join(workdir, "md素材")
    os.makedirs(material)

    basic_src = os.path.join(ASSETS, "基础资料.template.md")
    with open(basic_src, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("后端项目根目录: .", "后端项目根目录: " + backend_root())
    # 仅后端测试时前端仍指向 fixture；模板第二行可能是「前端项目根目录: .」
    content = content.replace("前端项目根目录: .", "前端项目根目录: " + frontend_root(), 1)
    # 兼容旧模板占位
    content = content.replace("/absolute/path/to/backend", backend_root())
    content = content.replace("/absolute/path/to/frontend", frontend_root())
    content = content.replace(
        "（必填）单位或个人全称 — 申请表 + 鉴别材料首页「权利人署名」；说明书其余正文默认不重复",
        "测试权利人",
    )
    # 兼容旧模板文案
    content = content.replace(
        "（必填）单位或个人全称 — 仅申请表使用；说明书正文默认不写",
        "测试权利人",
    )
    content = content.replace("（必填）软件全称，如 XX管理系统软件", "测试商城软件")
    content = content.replace("（必填）简称", "测试商城")
    content = content.replace(
        "（必填）≤50字，一句说清问题与贯通系统",
        "用于自动化测试的迷你商城系统",
    )
    content = content.replace(
        "（必填）用 2～4 句说明本软件要解决什么问题、服务谁",
        "用于自动化测试的迷你商城系统",
    )
    content = content.replace(
        "（必填）≤50字，行业+场景，可含关键系统", "测试领域"
    )
    content = content.replace(
        "（必填）如 工业制造、B2B 电商、供应链管理", "测试领域"
    )
    content = content.replace(
        "（必填）500～1300字，按业务链路分条写全",
        "1. 订单管理：支持下单与列表查询。本段为测试夹具功能描述填充，满足申请表主要功能字段的最低篇幅要求而编写的连续说明文字，涵盖下单、查询、同步等链路，便于回归测试解析基础资料而不触发必填残留检查。",
    )
    content = content.replace(
        "（必填）按业务流程概括能力（先链路后模块），每项 1～3 句",
        "1. 订单管理：支持下单与列表查询",
    )
    content = content.replace(
        "（必填）按 1. 2. 3. … 列出主要功能模块，每项 1～3 句",
        "1. 订单管理：支持下单与列表查询",
    )
    content = content.replace(
        "（必填）标签可选+自填≤100字；写架构/幂等/队列等关键点",
        "Laravel + UniApp 迷你夹具，仅用于 skill 回归测试",
    )
    content = content.replace(
        "（必填）可点选登记系统标签和/或自填，自填≤100字；写架构/幂等/队列等关键点",
        "Laravel + UniApp 迷你夹具，仅用于 skill 回归测试",
    )
    content = content.replace(
        "（必填）架构、技术栈、同步/幂等/队列等关键设计",
        "Laravel + UniApp 迷你夹具，仅用于 skill 回归测试",
    )
    content = content.replace(
        "（必填）架构、前后端技术栈、认证、支付、关键业务设计等",
        "Laravel + UniApp 迷你夹具，仅用于 skill 回归测试",
    )

    basic_path = os.path.join(workdir, "基础资料.md")
    with open(basic_path, "w", encoding="utf-8") as f:
        f.write(content)

    file_list = {
        "说明": "测试清单",
        "生成时间": "2026-07-20",
        "前端文件": [
            {"分类": "前端模块", "路径": "pages/index/index.vue"},
            {"分类": "前端API", "路径": "api/order.js"},
            {"分类": "前端工具", "路径": "utils/request.js"},
        ],
        "后端文件": [
            {"分类": "后端控制器", "路径": "app/Http/Controllers/OrderController.php"},
            {"分类": "后端服务", "路径": "app/Services/OrderServices.php"},
            {"分类": "后端模型", "路径": "app/Models/Order.php"},
            {"分类": "后端路由", "路径": "routes/api/order.php"},
        ],
    }

    with open(
        os.path.join(material, "core_business_files.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(file_list, f, ensure_ascii=False, indent=2)

    for i, body in enumerate(
        [
            "# 文档鉴别材料\n\n## 1. 软件概述\n\n测试商城软件用于回归。\n",
            "## 4. 核心技术说明\n\n采用 Laravel API。\n",
            "## 7. 核心业务流程说明\n\n1. 用户下单\n2. 后端创建订单\n",
        ],
        start=1,
    ):
        with open(
            os.path.join(material, "document_identification-{}.md".format(i)),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(body)

    return workdir


def cleanup(workdir):
    if workdir and os.path.isdir(workdir):
        shutil.rmtree(workdir, ignore_errors=True)
