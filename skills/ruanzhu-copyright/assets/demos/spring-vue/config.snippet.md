# Demo：Spring Boot + Vue SPA（示意）

> 仅作字段与路径风格参考。复制后必须改成当前仓库真实路径与著作权信息。

## # config

```
后端项目根目录: ./backend
前端项目根目录: ./frontend
后端框架类型: spring
前端框架类型: vue
数据库表前缀: 
文档输出目录: docs/软著登记申请/md素材
后端模型目录: src/main/java/com/example/domain
后端控制器目录: src/main/java/com/example/web
后端服务目录: src/main/java/com/example/service
后端路由目录: 
```

## 申请表环境/语言（示意）

```
软件开发环境 / 开发工具: JDK、Maven、Spring Boot、IntelliJ IDEA
该软件的运行平台 / 操作系统: Linux、JVM
软件运行支撑环境 / 支持软件: JRE、MySQL、Nginx、Redis
编程语言: HTML,Java,JavaScript,SQL
```

## 选码注意

- 排除 `target/`、生成代码、纯 DTO 堆砌
- 优先 `*Service` / 领域状态机；Controller 只选含关键编排的少量类
- 前端选 `src/views` 业务页，少选 layout/router 样板
