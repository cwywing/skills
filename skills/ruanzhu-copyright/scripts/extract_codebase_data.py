# -*- coding: utf-8 -*-
"""
Phase 1: 从代码库提取结构化数据（辅助清单，非硬门槛）

读取配置的模型/控制器/服务/路由目录与基础资料，输出 codebase_data.json。
默认回退目录可覆盖；解析偏空时仍应进入 Phase 2a 手选源码（栈无关）。

用法:
    python extract_codebase_data.py --workdir docs/软著登记申请
"""

import os
import re
import json
import sys

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _paths import parse_workdir_arg, load_basic_info  # noqa: E402

# 由 main() 初始化
BASIC_INFO_FILE = ""
OUTPUT_FILE = ""
MATERIAL_DIR = ""


def load_config():
    """从基础资料.md读取路径配置和软件信息"""
    return load_basic_info(BASIC_INFO_FILE)


def _join_under(root, rel_or_abs):
    """相对路径拼到 root；已是绝对路径则直接用。"""
    if not rel_or_abs:
        return ""
    if os.path.isabs(rel_or_abs):
        return rel_or_abs
    return os.path.join(root, rel_or_abs.replace("/", os.sep))


def resolve_paths(config):
    """根据配置解析所有路径；支持可选覆盖目录键。"""
    backend_root = config.get("后端项目根目录", "")
    frontend_root = config.get("前端项目根目录", "")

    if not backend_root or not os.path.exists(backend_root):
        print("错误: 后端项目根目录无效: {}".format(backend_root))
        print("  请检查基础资料.md 中的 '后端项目根目录' 配置")
        return None

    # 回退目录仅为常见约定；必须用基础资料 # config 覆盖为当前仓库路径（栈无关）
    model_rel = config.get("后端模型目录", "app/Models")
    ctrl_rel = config.get("后端控制器目录", "app/Http/Controllers")
    service_rel = config.get("后端服务目录", "app/Services")
    route_rel = config.get("后端路由目录", "routes/api")

    return {
        "backend_root": backend_root,
        "frontend_root": frontend_root,
        "model_dir": _join_under(backend_root, model_rel),
        "ctrl_dir": _join_under(backend_root, ctrl_rel),
        "service_dir": _join_under(backend_root, service_rel),
        "route_dir": _join_under(backend_root, route_rel),
    }

# ========================================================================
# 工具函数
# ========================================================================

def read_file(filepath):
    """读取文件内容，自动处理编码"""
    if not os.path.exists(filepath):
        return ""
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    return ""


def find_php_files(directory, recursive=True):
    """查找目录下所有 PHP 文件"""
    results = []
    if not os.path.exists(directory):
        return results
    if recursive:
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".php"):
                    results.append(os.path.join(root, f))
    else:
        for f in os.listdir(directory):
            if f.endswith(".php"):
                results.append(os.path.join(directory, f))
    return sorted(results)


def class_name_from_path(filepath):
    """从文件路径提取类名 (如 Product.php -> Product)"""
    return os.path.splitext(os.path.basename(filepath))[0]


# ========================================================================
# 提取器: Model
# ========================================================================

# 扫描配置的模型目录；下列基类名跳过（可按项目扩展，不表示绑定某框架）
SKIP_MODEL_CLASSES = {"MccModel", "Model", "BaseModel"}


def extract_model_data(filepath, project_root):
    """从单个 Model 文件提取结构化信息"""
    content = read_file(filepath)
    if not content:
        return None

    data = {
        "file": os.path.relpath(filepath, _project_root).replace("\\", "/"),
        "class": class_name_from_path(filepath),
        "table": "",
        "primary_key": "",
        "fillable": [],
        "casts": {},
        "hidden": [],
        "relationships": [],
        "constants": {},
        "key_methods": [],
        "timestamps": True,
    }

    # table 名
    m = re.search(r"protected\s+\$table\s*=\s*['\"](\w+)['\"]", content)
    if m:
        data["table"] = m.group(1)

    # primary key
    m = re.search(r"protected\s+\$primaryKey\s*=\s*['\"](\w+)['\"]", content)
    if m:
        data["primary_key"] = m.group(1)

    # fillable
    m = re.search(r"protected\s+\$fillable\s*=\s*\[([^\]]*)\]", content, re.DOTALL)
    if m:
        raw = m.group(1)
        data["fillable"] = re.findall(r"['\"](\w+)['\"]", raw)

    # casts
    m = re.search(r"protected\s+\$casts\s*=\s*\[([^\]]*)\]", content, re.DOTALL)
    if m:
        raw = m.group(1)
        pairs = re.findall(r"['\"](\w+)['\"]\s*=>\s*['\"]?(\w+)['\"]?", raw)
        data["casts"] = dict(pairs)

    # hidden
    m = re.search(r"protected\s+\$hidden\s*=\s*\[([^\]]*)\]", content, re.DOTALL)
    if m:
        raw = m.group(1)
        data["hidden"] = re.findall(r"['\"](\w+)['\"]", raw)

    # timestamps
    if re.search(r"public\s+\$timestamps\s*=\s*false", content):
        data["timestamps"] = False

    # incrementing
    m_inc = re.search(r"public\s+\$incrementing\s*=\s*(false|true)", content)

    # 关联关系
    rel_types = [
        "hasOne", "hasMany", "belongsTo", "belongsToMany",
        "morphMany", "morphOne", "morphTo"
    ]
    for rel in rel_types:
        pattern = r"function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*?return\s+\$this->" + rel + r"\s*\("
        for match in re.finditer(pattern, content, re.DOTALL):
            method_name = match.group(1)
            # 跳过 _ 开头的方法
            if method_name.startswith("_"):
                continue
            # 获取关联参数
            rest = content[match.end():]
            args_match = re.match(r"([^)]+)\)", rest)
            args_str = args_match.group(1) if args_match else ""
            data["relationships"].append({
                "method": method_name,
                "type": rel,
                "args": args_str.strip()
            })

    # 常量定义 (const ... = ...)
    for match in re.finditer(r"(?:const|public\s+const)\s+(\w+)\s*=\s*([^;]+);", content):
        name = match.group(1)
        value = match.group(2).strip()
        data["constants"][name] = value

    # 关键 public 方法（不含 __construct, 关联关系）
    rel_methods = {r["method"] for r in data["relationships"]}
    for match in re.finditer(
        r"public\s+function\s+(\w+)\s*\(", content
    ):
        method_name = match.group(1)
        if method_name.startswith("__"):
            continue
        if method_name in rel_methods:
            continue
        # 提取方法体前几行作为简要描述
        start = match.end()
        snippet = content[start:start + 300]
        # 取注释
        doc_comment = ""
        # 向前找 /** */ 注释
        before = content[max(0, match.start() - 500):match.start()]
        doc_match = re.findall(r"\*\s+([^*]+)", before)
        if doc_match:
            last_comments = doc_match[-3:]  # 取最后3行注释
            doc_comment = " ".join(l.strip() for l in last_comments if l.strip())
        data["key_methods"].append({
            "name": method_name,
            "comment": doc_comment[:200] if doc_comment else ""
        })

    return data


def extract_all_models(model_dir):
    """自动扫描 Models 目录，提取所有模型数据"""
    global _project_root
    models = []
    for filepath in find_php_files(model_dir, recursive=True):
        class_name = class_name_from_path(filepath)
        if class_name in SKIP_MODEL_CLASSES:
            continue
        data = extract_model_data(filepath, _project_root)
        if data:
            rel = os.path.relpath(filepath, model_dir)
            data["rel_path"] = os.path.splitext(rel)[0].replace("\\", "/")
            models.append(data)
    return models


# ========================================================================
# 提取器: Controller
# ========================================================================

def extract_controller_data(filepath):
    """从 Controller 文件提取方法列表"""
    content = read_file(filepath)
    if not content:
        return None

    class_name = class_name_from_path(filepath)
    if class_name in ("Controller", "BaseAuthenticatedController", "BaseOptionalAuthController"):
        return None

    methods = []
    for match in re.finditer(r"public\s+function\s+(\w+)\s*\(", content):
        method_name = match.group(1)
        if method_name.startswith("__"):
            continue
        # 提取方法上方的注释
        before = content[max(0, match.start() - 600):match.start()]
        doc_lines = re.findall(r"\*\s+([^\*]+)", before)
        doc_comment = ""
        if doc_lines:
            last_lines = doc_lines[-3:]
            doc_comment = " ".join(l.strip() for l in last_lines if l.strip())

        # 判断方法是否有 Route 注解或参数类型
        start = match.end()
        snippet = content[start:start + 200]
        has_request = "Request" in snippet
        returns_json = "json" in snippet.lower() or "response" in snippet.lower() or "return" in snippet

        methods.append({
            "name": method_name,
            "comment": doc_comment[:200] if doc_comment else "",
            "has_request_param": has_request,
        })

    return {
        "class": class_name,
        "file": os.path.relpath(filepath, _project_root).replace("\\", "/"),
        "methods": methods,
    }


def extract_all_controllers(ctrl_dir):
    """提取所有 Controller 数据"""
    controllers = []
    for filepath in find_php_files(ctrl_dir, recursive=False):
        data = extract_controller_data(filepath)
        if data:
            controllers.append(data)
    # 也检查子目录（如 User/）
    for entry in os.listdir(ctrl_dir):
        subdir = os.path.join(ctrl_dir, entry)
        if os.path.isdir(subdir):
            for filepath in find_php_files(subdir, recursive=False):
                data = extract_controller_data(filepath)
                if data:
                    data["file"] = entry + "/" + data["file"].split("/")[-1]
                    controllers.append(data)
    return controllers


# ========================================================================
# 提取器: Route
# ========================================================================

def extract_route_data(filepath):
    """从路由文件提取路由定义"""
    content = read_file(filepath)
    if not content:
        return []

    routes = []
    file_name = class_name_from_path(filepath)

    # 匹配 Route::get/post/put/delete/any/patch
    pattern = r"Route::(\w+)\(\s*['\"]([^'\"]+)['\"]"
    for match in re.finditer(pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        rest = content[match.end():match.end() + 200]
        handler = ""
        # 格式1: ControllerClass@method (字符串语法)
        ctrl_match = re.search(r"(\w+)Controller@(\w+)", rest)
        if ctrl_match:
            handler = f"{ctrl_match.group(1)}Controller@{ctrl_match.group(2)}"
        else:
            # 格式2: [ControllerClass::class, 'method'] (数组语法)
            arr_match = re.search(r"(\w+)Controller::class\s*,\s*'(\w+)'", rest)
            if arr_match:
                handler = f"{arr_match.group(1)}Controller@{arr_match.group(2)}"
        routes.append({
            "http_method": method,
            "path": path,
            "handler": handler,
        })

    # 匹配 Route::group + 内部路由
    # 简化处理：也匹配闭包中的路由定义
    group_pattern = r"\$router->(\w+)\(\s*['\"]([^'\"]+)['\"]"
    for match in re.finditer(group_pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        rest = content[match.end():match.end() + 200]
        handler = ""
        ctrl_match = re.search(r"(\w+)Controller@(\w+)", rest)
        if ctrl_match:
            handler = f"{ctrl_match.group(1)}Controller@{ctrl_match.group(2)}"
        else:
            arr_match = re.search(r"(\w+)Controller::class\s*,\s*'(\w+)'", rest)
            if arr_match:
                handler = f"{arr_match.group(1)}Controller@{arr_match.group(2)}"
        # 避免重复
        if not any(r["path"] == path and r["http_method"] == method for r in routes):
            routes.append({
                "http_method": method,
                "path": path,
                "handler": handler,
            })

    return {file_name: routes}


def extract_all_routes(route_dir):
    """提取所有路由"""
    all_routes = {}
    for filepath in find_php_files(route_dir, recursive=False):
        route_data = extract_route_data(filepath)
        all_routes.update(route_data)
    return all_routes


# ========================================================================
# 提取器: Service
# ========================================================================

def extract_service_data(filepath):
    """从 Service 文件提取方法列表"""
    content = read_file(filepath)
    if not content:
        return None

    class_name = class_name_from_path(filepath)
    methods = []
    for match in re.finditer(r"public\s+function\s+(\w+)\s*\(", content):
        method_name = match.group(1)
        if method_name.startswith("__"):
            continue
        before = content[max(0, match.start() - 600):match.start()]
        doc_lines = re.findall(r"\*\s+([^\*]+)", before)
        doc_comment = ""
        if doc_lines:
            last_lines = doc_lines[-3:]
            doc_comment = " ".join(l.strip() for l in last_lines if l.strip())
        methods.append({
            "name": method_name,
            "comment": doc_comment[:200] if doc_comment else "",
        })

    return {
        "class": class_name,
        "file": os.path.relpath(filepath, _project_root).replace("\\", "/"),
        "methods": methods,
    }


def extract_all_services(service_dir):
    """提取所有 Service 数据"""
    services = []
    for filepath in find_php_files(service_dir, recursive=True):
        data = extract_service_data(filepath)
        if data:
            services.append(data)
    return services


# ========================================================================
# 提取器: 基础资料
# ========================================================================

def extract_basic_info():
    """从 基础资料.md 提取键值对（不含 config 段）"""
    config, info = load_config()
    return info


# ========================================================================
# 提取器: 前端页面列表
# ========================================================================

def extract_frontend_pages(frontend_root):
    """扫描 UniApp 前端 pages 目录结构"""
    pages_dir = os.path.join(frontend_root, "pages")
    if not os.path.exists(pages_dir):
        return {"error": f"目录不存在: {pages_dir}"}

    page_list = []
    for root, dirs, files in os.walk(pages_dir):
        for f in files:
            if f.endswith(".vue"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, frontend_root).replace("\\", "/")
                page_list.append(rel)

    # 也扫描 components
    comp_dir = os.path.join(frontend_root, "components")
    comp_list = []
    if os.path.exists(comp_dir):
        for root, dirs, files in os.walk(comp_dir):
            for f in files:
                if f.endswith(".vue"):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, frontend_root).replace("\\", "/")
                    comp_list.append(rel)

    # api 目录
    api_dir = os.path.join(frontend_root, "api")
    api_list = []
    if os.path.exists(api_dir):
        for f in os.listdir(api_dir):
            if f.endswith(".js"):
                api_list.append(f)

    # store 目录
    store_dir = os.path.join(frontend_root, "store")
    store_list = []
    if os.path.exists(store_dir):
        for root, dirs, files in os.walk(store_dir):
            for f in files:
                if f.endswith(".js"):
                    store_list.append(f)

    # utils 目录
    utils_dir = os.path.join(frontend_root, "utils")
    utils_list = []
    if os.path.exists(utils_dir):
        for f in os.listdir(utils_dir):
            if f.endswith(".js"):
                utils_list.append(f)

    return {
        "pages": sorted(page_list),
        "components": sorted(comp_list),
        "api_files": sorted(api_list),
        "store_files": sorted(store_list),
        "utils_files": sorted(utils_list),
    }


# ========================================================================
# 全局变量（由 main 初始化）
# ========================================================================
_project_root = ""

def main():
    global _project_root, BASIC_INFO_FILE, OUTPUT_FILE, MATERIAL_DIR

    paths_meta = parse_workdir_arg()
    BASIC_INFO_FILE = paths_meta["basic_info"]
    MATERIAL_DIR = paths_meta["material_dir"]
    OUTPUT_FILE = os.path.join(MATERIAL_DIR, "codebase_data.json")

    # 读取配置
    config, software_info = load_config()
    paths = resolve_paths(config)
    if paths is None:
        return

    _project_root = paths["backend_root"]
    sw_name = software_info.get("软件全称", "未命名软件")
    sw_ver = software_info.get("版本号", "V1.0")

    print("=" * 60)
    print("Phase 1: 从代码库提取结构化数据")
    print("工作目录: {}".format(paths_meta["workdir"]))
    print("项目: {} {}".format(sw_name, sw_ver))
    print("后端: {}".format(paths["backend_root"]))
    if paths["frontend_root"]:
        print("前端: {}".format(paths["frontend_root"]))
    print("=" * 60)

    result = {}

    # 1. 基础资料
    print("\n[1/6] 提取基础资料...")
    result["software_info"] = software_info
    print(f"  -> 提取到 {len(result['software_info'])} 个字段")

    # 2. 模型（自动扫描）
    print("\n[2/6] 提取模型数据（自动扫描 Models 目录）...")
    result["models"] = extract_all_models(paths["model_dir"])
    total_methods = sum(len(m["key_methods"]) for m in result["models"])
    total_rels = sum(len(m["relationships"]) for m in result["models"])
    print(f"  -> {len(result['models'])} 个模型")
    print(f"     {total_rels} 个关联关系, {total_methods} 个方法")

    # 3. 控制器
    print("\n[3/6] 提取控制器数据...")
    result["controllers"] = extract_all_controllers(paths["ctrl_dir"])
    total_ctrl_methods = sum(len(c["methods"]) for c in result["controllers"])
    print(f"  -> {len(result['controllers'])} 个控制器, {total_ctrl_methods} 个方法")

    # 4. 路由
    print("\n[4/6] 提取路由数据...")
    result["routes"] = extract_all_routes(paths["route_dir"])
    total_routes = sum(len(v) for v in result["routes"].values())
    print(f"  -> {len(result['routes'])} 个路由文件, {total_routes} 条路由")

    # 5. 服务层
    print("\n[5/6] 提取服务层数据...")
    result["services"] = extract_all_services(paths["service_dir"])
    total_svc_methods = sum(len(s["methods"]) for s in result["services"])
    print(f"  -> {len(result['services'])} 个服务类, {total_svc_methods} 个方法")

    # 6. 前端页面
    print("\n[6/6] 扫描前端页面结构...")
    if paths["frontend_root"] and os.path.exists(paths["frontend_root"]):
        result["frontend"] = extract_frontend_pages(paths["frontend_root"])
        print(f"  -> {len(result['frontend'].get('pages', []))} 个页面")
        print(f"     {len(result['frontend'].get('components', []))} 个组件")
        print(f"     {len(result['frontend'].get('api_files', []))} 个 API 文件")
    else:
        result["frontend"] = {}
        print("  -> 前端目录未配置或不存在，跳过")

    # 统计摘要
    result["_summary"] = {
        "models_count": len(result["models"]),
        "controllers_count": len(result["controllers"]),
        "services_count": len(result["services"]),
        "route_files_count": len(result["routes"]),
        "total_routes": total_routes,
        "frontend_pages_count": len(result["frontend"].get("pages", [])),
        "frontend_components_count": len(result["frontend"].get("components", [])),
    }

    # 输出 JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n{'=' * 60}")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"文件大小: {file_size:,} bytes ({file_size // 1024} KB)")
    print(f"{'=' * 60}")
    print(f"\n下一步: 将此 JSON 提供给大模型，结合文档模板生成《文档鉴别材料》")


if __name__ == "__main__":
    main()
