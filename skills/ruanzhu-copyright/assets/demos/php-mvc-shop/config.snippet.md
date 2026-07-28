# Demo：开源 PHP MVC 商城二开 + 服务端模板（示意）

> 典型：单体仓库内 controller/model/view，无独立前端工程。仅作风格参考。

## # config

```
后端项目根目录: .
前端项目根目录: .
后端框架类型: php-mvc
前端框架类型: twig
数据库表前缀: （按实，如有）
文档输出目录: docs/软著登记申请/md素材
后端模型目录: catalog/model
后端控制器目录: catalog/controller
后端服务目录: admin/model
后端路由目录: 
```

说明：前端根可与后端同为 `.`；2a 时把模板文件放进 `前端文件`，PHP 业务放进 `后端文件`。

## 申请表环境/语言（示意）

```
软件开发环境 / 开发工具: PHP、MySQL、VS Code
该软件的运行平台 / 操作系统: Linux、PHP 运行时
软件运行支撑环境 / 支持软件: PHP、MySQL、Nginx
编程语言: HTML,JavaScript,PHP,SQL
```

## 选码注意

- 先做 fork 判定：排除 `system/`、`vendor/`、上游原生 extension
- `分类` 只写功能名，不要写「(二开)」
- 优先库存/计价/支付回调/报价转单等定制 Model；少选同构后台列表与空壳 Controller
- 前端模板少而精，避免连续多个雷同 list 页
