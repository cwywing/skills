# Demo：Laravel + UniApp/Vue（示意）

> 仅作字段与路径风格参考。复制后必须改成当前仓库真实路径与著作权信息。

## # config

```
后端项目根目录: .
前端项目根目录: ./uniapp
后端框架类型: laravel
前端框架类型: uniapp
数据库表前缀: 
文档输出目录: docs/软著登记申请/md素材
后端模型目录: app/Models
后端控制器目录: app/Http/Controllers
后端服务目录: app/Services
后端路由目录: routes/api
```

## 申请表环境/语言（示意）

```
软件开发环境 / 开发工具: PHP、MySQL、Laravel、VS Code
该软件的运行平台 / 操作系统: Linux、PHP 运行时
软件运行支撑环境 / 支持软件: PHP、MySQL、Nginx、Redis
编程语言: HTML,JavaScript,PHP,SQL
```

## 选码注意

- 排除 `vendor/`、框架脚手架空壳
- 前端少选列表页；优先结算/支付等交互页
- 后端优先 Services / 含事务与幂等的 Model 方法
