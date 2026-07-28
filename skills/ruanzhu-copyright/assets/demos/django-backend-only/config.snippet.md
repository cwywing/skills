# Demo：Django 仅后端（示意）

> 无独立前端或前端不纳入本次材料时使用。`前端文件` 可为 `[]`。

## # config

```
后端项目根目录: .
前端项目根目录: 
后端框架类型: django
前端框架类型: none
数据库表前缀: 
文档输出目录: docs/软著登记申请/md素材
后端模型目录: apps/orders/models.py
后端控制器目录: apps/orders/views.py
后端服务目录: apps/orders/services
后端路由目录: config/urls.py
```

说明：单文件 `models.py` / `views.py` 时，目录键可填到文件路径所在包；Phase 1 可能摘要不完整，以 2a 手选 `.py` 文件为准。

## 申请表环境/语言（示意）

```
软件开发环境 / 开发工具: Python、Django、PyCharm
该软件的运行平台 / 操作系统: Linux、Python 运行时
软件运行支撑环境 / 支持软件: Python、PostgreSQL、Nginx、Gunicorn
编程语言: Python,SQL
```

## 选码注意

- 排除 `venv/`、`migrations` 流水账、第三方 site-packages
- 优先 `services/` 与含业务规则的 `models` 方法；views 只选编排型
