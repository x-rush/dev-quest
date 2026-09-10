# CI/CD — GitHub Actions 流水线

> **文档简介**: 用 GitHub Actions 搭建"检查 → 测试 → 构建镜像 → 部署"的完整流水线，uv 缓存让每次运行快到秒级
>
> **目标读者**: 想让每次 push 自动验证与交付的开发者
>
> **前置知识**: [容器化部署](./01-docker-deployment.md)、[开发工具链](../frameworks/04-devtools.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#GitHub-Actions` `#CI-CD` `#uv` `#Docker` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 编写 lint / typecheck / test / build / deploy 分层 job
- ✅ 配置 uv 缓存与 `--frozen` 保证 CI 可复现
- ✅ 用分支保护让测试成为合并门禁

---

## 1. 流水线总览

```text
push / PR
  ├─ job: lint        ruff check + format --check   （秒级，最先失败）
  ├─ job: typecheck   mypy
  ├─ job: test        pytest + coverage             （依赖前两者通过）
  │     └─ job: build   构建并推送镜像（仅 main）
  │           └─ job: deploy  部署（仅打 tag）
```

失败尽早：lint 挂了就没必要跑测试，省钱省时间。

## 2. 完整工作流

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push: { branches: [main] }
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5          # 安装 uv 并缓存其目录
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run mypy .

  test:
    needs: [lint, typecheck]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run pytest --cov --cov-report=xml
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: coverage, path: coverage.xml }

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}

  deploy:
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "ssh 或调用部署 API；凭据一律经 secrets 注入，禁止写死"
```

## 3. 关键实践

- **缓存**：`setup-uv` 的 `enable-cache` 缓存 uv 全局目录与 `.venv`，测试从分钟级降到秒级
- **`--frozen`**：CI 一律按 `uv.lock` 安装，绝不现场解析依赖——CI 与镜像、本地三方一致
- **密钥**：仓库 Settings → Secrets and variables → Actions 管理；`${{ secrets.X }}` 不落日志、不进代码
- **分支保护**：main 设置"test job 必须通过才可合并"，让 CI 成为门禁而非装饰

## 4. 本地预检（push 前省一轮 CI）

```bash
uv run ruff check --fix . && uv run ruff format .
uv run mypy . && uv run pytest -q
```

可以配 pre-commit 钩子把这些命令自动化，与 CI 用同一套配置（工具配置见[开发工具链](../frameworks/04-devtools.md)）。

## ❓ 常见问题

**Q1: CI 里测试通过、部署失败了？**
先区分"构建失败"还是"运行失败"：构建看 build job 日志；运行失败多半是环境变量缺失——对照[可观测性](./03-observability.md)的日志排障。

**Q2: 私有依赖装不上？**
`setup-uv` 环境里同样需要凭据：用 secrets 注入 token，或改用 GitHub Packages 托管依赖。

---

## 🔗 相关文档

- 🚀 **[容器化部署](./01-docker-deployment.md)** — build job 构建的镜像从哪来
- 🚀 **[可观测性](./03-observability.md)** — 部署后的监控闭环
- 📄 **[开发工具链](../frameworks/04-devtools.md)** — ruff/mypy/pytest 的本地配置
- 🧪 **[单元测试](../testing/01-unit-testing.md)** / **[集成测试](../testing/02-integration-testing.md)** — test job 的内容
