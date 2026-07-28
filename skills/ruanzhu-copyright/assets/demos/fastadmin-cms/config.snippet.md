# Demo：FastAdmin + ThinkPHP + CMS 插件二开（示意）

> 典型：仓库根为 FastAdmin；业务在 `addons/cms/`；PC 模板在插件 view；UniApp 常为插件自带前端。  
> **只读示意**——路径风格可对照，著作权信息与真实相对路径必须按当前仓库改写。

## # config

```
后端项目根目录: .
前端项目根目录: addons/cms/uniapp
后端框架类型: fastadmin
前端框架类型: uniapp
数据库表前缀: fa_
文档输出目录: docs/软著登记申请/md素材
后端模型目录: addons/cms/model
后端控制器目录: addons/cms/controller
后端服务目录: addons/cms/library
后端路由目录: application
```

说明：

- 业务核心在 CMS 插件时，把模型/控制器/服务目录指到 `addons/cms/...`，不要指到空的 `application/admin` 全量 CRUD。
- `前端项目根目录` 可填 UniApp 路径供备注；若 fork 判定认定 UniApp 为上游原生，**2a 的 `前端文件` 仍应为 `[]`**，定制 PC 模板放进 `后端文件`。

## 申请表环境/语言（示意）

```
软件开发环境 / 开发工具: PHP 7.1+、MySQL、ThinkPHP 5、VS Code
该软件的运行平台 / 操作系统: Linux / Windows Server、PHP 运行时
软件运行支撑环境 / 支持软件: PHP、MySQL、Nginx、Redis、ThinkPHP 5
编程语言: HTML,JavaScript,PHP,SQL
```

勿把 FastAdmin / ThinkPHP 填进「编程语言」勾选框。

## 选码注意（本栈高频坑）

| 做 | 不做 |
|----|------|
| 先读 `fork-detection.md` FastAdmin+CMS 行 | 整目录收录 `addons/cms/` |
| 保留：场景/表单邮件分发/权限改造/订单结算/定制 PC 模板/独立 `python/` 工具 | 收录 `thinkphp/`、`vendor/`、`extend/fast/`、`controller/api|wxapp`、未改过的 `uniapp/pages` |
| `分类` 只写功能名 | 标题写「(二开)」「(二开新增)」 |
| 同构 `list_*.html` 少而精（每种业务留 1～2 个代表） | 用几十个雷同栏目模板凑页 |
| 估行约 5000～6500 后 **以 export PDF 实测** 加减文件 | 只信 generate 脚本「约 50 行/页」的页数警告就停手或猛砍 |

## 与 php-mvc-shop demo 的差别

- `php-mvc-shop`：通用单体 PHP MVC + Twig 类模板。
- 本 demo：插件化 `addons/`、FastAdmin 后台 CRUD、CMS 内容模型、常见「UniApp 原生 vs PC 定制模板」分流。
