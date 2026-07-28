# Demo 参考样例（只读参考）

本目录存放**填表与选码格式**的示意样例，方便对照异栈项目时「长什么样」。

| 规则 | 说明 |
|------|------|
| 用途 | Phase 0 填 `# config`、Phase 2a 写 `core_business_files.json` 时对照字段与路径风格 |
| 禁止 | 整份照抄进真实 `基础资料.md` / 选码清单；路径必须改成当前仓库真实相对路径 |
| 与模板关系 | 空白可写模板仍是 `assets/基础资料.template.md`；此处是**填好的示意** |
| 与测试关系 | 可执行迷你夹具在 `tests/fixtures/`；本目录不参与自动测试 |

## 索引

| 子目录 | 示意栈 | 何时打开 |
|--------|--------|----------|
| `laravel-uniapp/` | Laravel API + UniApp/Vue | PHP 后端 + 小程序/H5 前端 |
| `spring-vue/` | Spring Boot + Vue SPA | Java 后端 + 独立前端工程 |
| `php-mvc-shop/` | 开源 PHP 商城二开 + 服务端模板 | 单体 PHP MVC、模板在仓库内、无独立前端工程 |
| `fastadmin-cms/` | FastAdmin + ThinkPHP + CMS 插件二开 | `addons/cms/` 业务、PC 定制模板、UniApp 常为上游原生 |
| `django-backend-only/` | Django 仅后端 | 无前端或前端另仓暂不纳入 |

每个子目录通常含：

- `config.snippet.md` — `# config` 与申请表环境/语言示意（非完整申请表）
- `core_business_files.json` — 选码清单格式示意（路径虚构或示意，勿当真实文件）

需要目录映射总表时仍读 `references/framework-adapters.md`。
