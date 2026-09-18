# 安全实践 — 依赖、注入与密钥

> **文档简介**: 系统梳理 Python Web 服务三类高频安全问题：依赖链风险、注入攻击与密钥管理，每节给出可执行清单
>
> **目标读者**: 要把服务发布到公网的开发者
>
> **前置知识**: [生产级 FastAPI 应用](../../projects/04-production-fastapi-app.md)、[生态集成](../../frameworks/03-ecosystem-integration.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 解释 |
| **难度** | ⭐⭐⭐ |
| **标签** | `#安全` `#SQL注入` `#密钥管理` `#依赖安全` |
| **更新日期** | `2026年9月` |

</details>

## 1. 依赖安全：你的供应链比你想象的脆弱

```bash
# 从锁文件导出生产依赖，再显式交给审计工具；不要审计 uvx 自己的隔离环境
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file requirements-audit.txt
uvx pip-audit -r requirements-audit.txt
```

- `uv.lock` 锁定传递依赖的精确版本，审计才有意义——**务必提交锁文件**（工作流见[开发工具链](../../frameworks/04-devtools.md)）
- 开启 GitHub Dependabot，自动为有漏洞的依赖开升级 PR
- 新增依赖前问三个问题：维护活跃吗？下载量够大吗？真的需要它吗？（能用标准库就不用第三方）

## 2. 注入防护：永远不手工拼接

**SQL 注入**——字符串拼 SQL 是头号大坑：

```python
# ❌ 危险：用户输入直接进 SQL——name = "' or '1'='1" 即可拖库
await session.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))

# ✅ 参数绑定：值与语句分离，驱动负责转义
await session.execute(
    text("SELECT * FROM users WHERE name = :name"),
    {"name": name},
)

# ✅ ORM 表达式天然参数化
stmt = select(User).where(User.email == email)
```

**命令注入**：

```python
# ❌ 用户输入进了 shell 解释器
subprocess.run(f"convert {user_file}.png out.jpg", shell=True)

# ✅ 列表参数 + shell=False；文件名做白名单校验
subprocess.run(["convert", user_file + ".png", "out.jpg"], check=True)
```

**路径穿越**：

```python
# ❌ ../../etc/passwd 直接逃出基目录
p = Path(BASE_DIR) / user_path

# ✅ 解析后校验仍在基目录内
base = Path(BASE_DIR).resolve()
p = (base / user_path).resolve()
if not p.is_relative_to(base):
    raise PermissionError("非法路径")
```

**要点**：参数绑定保护作为值传入的 SQL 参数；动态表名与排序标识仍需白名单。shell=False 避免常规 shell 解析但不防程序选项注入；路径归一化与包含检查也依赖文件系统边界和竞争条件。三者共同原则：**数据永远当数据处理，不当代码执行**。

## 3. 密钥管理

```python
# pydantic-settings：配置与代码分离（集成方式见生态集成）
class Settings(BaseSettings):
    jwt_secret: str                        # 无默认值 → 缺失即启动失败，问题尽早暴露
    database_url: str
    model_config = {"env_file": ".env"}    # .env 只在本地；生产用环境变量/密钥服务
```

- `.env`、`*.pem` 进 `.gitignore`；仓库提交 `.env.example` 字段名占位
- 已泄漏的密钥只有"轮换"一个选项——删除提交历史不等于删除泄漏
- JWT 密钥轮换：支持多密钥验证（新密钥签、旧密钥验），过渡期后删除旧密钥
- 日志与错误上报脱敏：Sentry `send_default_pii=False`，日志不记密码/token（见[可观测性](../../deployment/03-observability.md)）

## 4. 认证与密码存储

```python
import bcrypt

# 存哈希不存密码；bcrypt 自带盐 + 慢哈希，GPU 暴力破解成本高
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
ok = bcrypt.checkpw(input_password.encode(), password_hash)
```

JWT 三条铁律：

1. 校验 `exp`（过期）与 `alg`（显式限定算法，拒绝 `alg: none`）
2. payload 只放标识符——token 可被任何人 base64 解开，不放敏感数据
3. 短有效期 + 刷新机制，而非超长过期一劳永逸

完整签发实现见[生产级应用](../../projects/04-production-fastapi-app.md)第 2 节。

## 5. 传输与响应加固

- 全站 HTTPS；反代终结 TLS 也要保证内部网络可信
- CORS 白名单最小化：勿用 `allow_origins=["*"]` + 凭据组合（中间件配置见[FastAPI 进阶](../../frameworks/02-fastapi-advanced.md)）
- 错误响应不回栈信息：生产 `FastAPI(debug=False)`，500 只记日志、对外只给通用提示

## 6. 上线前安全清单

- [ ] 审计明确的项目依赖清单，记录无法审计的包与处置结果；依赖更新机制已配置
- [ ] 无 f-string SQL / `shell=True` / 未校验的路径拼接
- [ ] 密钥全部环境变量注入，`.gitignore` 覆盖 `.env`，历史无泄漏
- [ ] bcrypt 哈希密码、JWT 校验 `exp`/`alg`、短有效期
- [ ] CORS 白名单、`debug` 关闭、错误信息脱敏
- [ ] 依赖审计进 CI（与[流水线](../../deployment/02-ci-cd-pipelines.md)集成）

---

<!-- full-library-explanation -->
## 把防护放在实际信任边界上

前置知识是 HTTP 身份、SQL 参数和文件路径。输入验证检查结构与业务范围，参数绑定隔离 SQL 值，授权确认当前身份能否操作具体对象。即使输入完全合法，用户 A 仍不应读取用户 B 的私有记录；这个场景需要对象级授权测试。

练习创建两个测试用户，各有一条记录。分别验证未登录、自己的 ID、他人的 ID、不存在的 ID，确认错误响应符合约定且没有泄漏他人的正文。再用相同请求重复提交，检查系统是否需要幂等处理。安全验证应围绕操作与结果，而不是只检查中间件是否安装。

路径校验示例要求基目录也先 resolve，并且目录结构由可信代码控制。若攻击者可以在检查后替换符号链接，单次字符串比较仍有检查与使用之间的竞争。命令参数列表同样不能替代目标程序选项校验。依赖审计只覆盖已知公告，零报告不能证明代码或依赖没有风险。

## 🔗 相关文档

- 🚀 **[项目：生产级 FastAPI 应用](../../projects/04-production-fastapi-app.md)** — 本篇的工程化落地
- 🚀 **[可观测性](../../deployment/03-observability.md)** — 日志脱敏与错误上报的安全边界
- 🚀 **[容器化部署](../../deployment/01-docker-deployment.md)** — .env 不进镜像的部署面
- 📄 **[生态集成](../../frameworks/03-ecosystem-integration.md)** — pydantic-settings 配置管理
- 📖 **[内置函数字典](../../reference/language-concepts/02-built-in-functions.md)** — 输入校验相关内建工具


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
