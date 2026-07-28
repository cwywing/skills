# 二开 vs 开源原生区分（Fork Detection）

> Phase 2a 前置判定。当项目基于开源框架 / 开源插件 / 公开模板二开时，必须先区分「二开代码」与「开源原生代码」，否则会把大量已公开代码当自有源码提交，软著审查可能因「代码已公开来源」而不予认可。

---

## 何时启用本判定

满足任一即启用：

- 项目根有 `composer.json` / `package.json` 且依赖中含知名开源框架（ThinkPHP / Laravel / FastAdmin / CRMEB / WordPress / Discuz / Django / Spring Boot …）。
- 存在 `vendor/`、`node_modules/`、`thinkphp/`、`extend/`、`addons/`（FastAdmin 插件）、`wp-content/plugins/`、`wp-content/themes/` 等上游/插件目录。
- 代码注释里出现 `@author FastAdmin`、`@package ThinkPHP`、`@license MIT/GPL/Apache`、`@link github.com/...` 等开源标记。
- 用户明确说「基于 XX 二开」「在 XX 上改的」「XX 插件自带的」。

---

## 判定流程（Phase 2a 前先做）

### 1. 识别开源上游

读 `composer.json` / `package.json` / `.env` / 入口文件，列出：

| 上游类型 | 常见路径 | 处置 |
|----------|----------|------|
| 框架核心 | `thinkphp/`、`vendor/laravel`、`vendor/topthink` | **一律排除**，不进清单 |
| 框架扩展库 | `extend/fast/`、`vendor/...` | **一律排除** |
| 开源插件/模块 | `addons/cms/`、`addons/nkeditor/`、`wp-content/plugins/*` | **逐文件判定**（见下） |
| 开源主题/模板 | `addons/cms/view/default/*`、`wp-content/themes/*` | **逐文件判定** |
| 开源前端工程 | `addons/cms/uniapp/`、`wp-content/.../js` | **逐文件判定** |
| 第三方 SDK | `extend/aliyunVod.php`、`vendor/alipay` | **一律排除** |

### 2. 对插件/模板/前端目录逐文件判定「原生 vs 二开」

不能整目录一刀切。对插件目录下的每个文件，按以下信号判定：

#### 二开信号（保留）

- 文件内有**本项目特有业务逻辑**：定制权限校验、邮件分发规则、场景/方案模块、定制表单字段、本项目专有模型字段。
- 文件名/类名含**本项目特有命名**：`Scene`、`SceneProduct`、`SearchLog`、`list_prd_cczz`、`page_factory`、`diyform_pxbm` 等非插件默认命名。
- 文件内有**对原生类的重写/扩展**：覆盖了插件的 `getChannelList`、`getDiyformList`、`_initialize` 等方法并加入定制逻辑。
- **本项目新增的控制器/模型**（插件原生不存在该文件）。
- **本项目定制的 PC 模板**（文件名带产品/栏目/表单特有 slug，且内容含本项目业务变量）。
- **本项目独立的工具脚本**（如 `python/` 下的采集、SQL 生成脚本，与框架无关）。

#### 原生信号（排除）

- 文件是插件**默认 CRUD**：标准 `index/add/edit/del/multi` 五件套且无业务定制。
- 文件是插件**自带的 API/小程序控制器**：`addons/cms/controller/api/*`、`addons/cms/controller/wxapp/*` 通常是插件原生对外接口，除非有本项目定制逻辑。
- 文件是插件**自带的前端页面**：`addons/cms/uniapp/pages/*` 默认页面，除非有本项目定制。
- 文件是插件**自带的通用库**：`addons/cms/library/Auth.php`、`Token.php`、`Upload.php`、`Sms.php` 等基础服务（除非本项目改过）。
- 文件是插件**自带的基础模型**：仅含表名声明、字段映射，无业务方法。
- 文件**纯样式/纯装饰**：`*.css`、`*.min.js`、图标资源。
- 文件内有 `@author FastAdmin` / `@package think-cms` 且无本项目改动痕迹。

### 3. 灰区处理

无法一眼判定时：

- **优先读文件头部 + 1～2 个方法**，看有无本项目业务字段/逻辑。
- **仍判不准**：默认**排除**（宁可少交，不可交开源原生）。
- **边界情况**：插件原生文件被本项目**实质性修改**（改了业务逻辑而非仅改注释）→ 算二开，**保留**；`分类` 只写功能名，勿写「(二开)」。

---

## 输出：`core_business_files.json`（对外标题不含二开标签）

筛选时必须排除上游原生；写入 JSON 时：

- `分类`：功能名（如「报价列表页」「订单模型」）
- `路径`：相对项目根
- 程序段标题由脚本生成：`/* ======= {分类}：{相对路径} ======= */`

```json
{
  "后端文件": [
    {"分类": "CMS文章模型", "路径": "addons/cms/model/Archives.php"},
    {"分类": "自定义表单控制器", "路径": "addons/cms/controller/Diyform.php"},
    {"分类": "场景管理控制器", "路径": "application/admin/controller/cms/Scene.php"},
    {"分类": "PC首页模板", "路径": "addons/cms/view/default/index.html"},
    {"分类": "文章采集工具", "路径": "python/article.py"}
  ]
}
```

**Incorrect：** `"分类": "CMS模型-文章(二开权限/邮件)"` —— 二开标签不要进程序正文标题。  
如需内部备注，可写在 JSON 顶层 `说明` 字段，不写入 `分类`。

---

## 常见框架速查

| 框架/插件 | 原生目录（默认排除） | 二开常见位置 |
|-----------|---------------------|--------------|
| FastAdmin + CMS | `thinkphp/`、`vendor/`、`extend/fast/`、`addons/cms/controller/api/*`、`addons/cms/controller/wxapp/*`、`addons/cms/uniapp/*`、`addons/cms/library/Auth/Token/Upload/Sms` | `addons/cms/model/*`(改造)、`addons/cms/controller/*`(前台非api)、`application/admin/controller/cms/*`、`application/index/controller/*`、`addons/cms/view/default/*`(定制模板)、`python/*` |
| ThinkPHP 裸框架 | `thinkphp/`、`vendor/topthink`、`extend/` | `application/<module>/controller/*`、`application/<module>/model/*` |
| 电商类 PHP 开源商城 + 定制 | `system/`、`vendor/`、上游原生 extension/插件目录 | 本项目改造的 controller/model/view 与自研后台模块 |
| Laravel + 开源包 | `vendor/laravel`、`vendor/<package>` | `app/Http/Controllers/*`、`app/Services/*`、`app/Models/*`(非包内模型) |
| WordPress | `wp-admin/`、`wp-includes/`、`wp-content/plugins/<第三方插件>/` | `wp-content/themes/<自有主题>/*`、`wp-content/mu-plugins/*`(自写)、`wp-content/plugins/<自有插件>/*` |
| CRMEB | `crmeb/`、`vendor/`、`template/admin/`(默认模板) | `app/`(定制控制器/服务)、`template/admin/`(定制模板)、`crmeb/services/*`(改造) |
| Django | `venv/`、第三方 `site-packages` | `<app>/views.py`、`<app>/models.py`、`<app>/services/` |

---

## 对比：正确 vs 错误

- **Correct**：先列上游清单 → 逐文件判定 → **仅保留本项目定制代码** → `分类` 写功能名、路径写相对路径
- **Incorrect**：整目录收录开源原生；或在程序标题中写「(二开新增)」
- **Rationale**：开源原生代码已公开来源，审查可能不认可；程序正文只需相对路径定位，无需二开标签。

---

## 与其他参考的关系

- 本判定在 **Phase 2a 之前**进行，结果直接驱动 `core_business_files.json` 的选入文件。
- 判定后仍需遵守 `core-file-selection.md` 的页数体量约束（程序 PDF 80～100 页、后端 ≥40%）。
- 若定制代码总量不足，**优先补本项目定制模板、工具脚本、前台控制器**，不要回退收录开源原生代码。
