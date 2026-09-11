# Next.js 16 现代包管理器完整指南

> **文档简介**: Next.js 16 现代包管理器企业级应用指南，涵盖npm、yarn、pnpm、bun等现代包管理工具的高级配置和最佳实践

> **目标读者**: 具备基础包管理知识的前端开发者，需要掌握企业级依赖管理和构建优化的工程师

> **前置知识**: Next.js 16基础、TypeScript 5、Node.js包管理概念、模块系统基础

> **预计时长**: 4-6小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ (3/5星) |
| **标签** | `#package-managers` `#npm` `#yarn` `#pnpm` `#bun` `#dependency-management` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 📚 概述

现代包管理器为 Next.js 16 企业级开发提供了更快、更高效、更安全的依赖管理方案。本指南深入探讨企业级包管理策略，涵盖性能优化、安全性、依赖分析、工作区管理等高级主题，帮助开发团队建立可靠的包管理架构。

## 🏗️ 企业级包管理架构概览

### 包管理器分类体系

## 🚀 包管理器对比

### 核心特性对比
**了解各包管理器的优势和特点**

```typescript
// 包管理器特性对比
interface PackageManagerComparison {
  npm: {
    version: '9.x+';
    performance: 'Baseline';
    features: [
      'Workspaces support',
      'package-lock.json',
      'npm audit',
      'npm scripts',
      'npm link',
      'npm pack'
    ];
    pros: ['Node.js 默认', '生态成熟', '文档完善'];
    cons: ['速度较慢', '存储占用大'];
  };

  yarn: {
    version: '3.x+ (Berry)';
    performance: 'Fast';
    features: [
      'Plug-n-Play (PnP)',
      'Zero-install',
      'Workspaces',
      'Yarn Berry (Yarn 2)',
      'Selective dependency resolution'
    ];
    pros: ['速度快', 'PnP 模式', 'Workspaces 支持'];
    cons: ['学习曲线', '生态兼容性'];
  };

  pnpm: {
    version: '8.x+';
    performance: 'Fastest';
    features: [
      'Content-addressable storage',
      'Strict dependency management',
      'Efficient disk usage',
      'Workspaces support',
      'pnpm overrides'
    ];
    pros: ['极速安装', '磁盘空间高效', '依赖隔离'];
    cons: ['相对较新', '部分工具兼容性'];
  };
}

// 性能基准测试结果
const performanceBenchmarks = {
  // 安装时间 (相对值，npm = 1.0)
  installTime: {
    npm: 1.0,
    yarn: 0.7,
    pnpm: 0.3,
  },

  // 磁盘空间使用 (相对值，npm = 1.0)
  diskUsage: {
    npm: 1.0,
    yarn: 0.8,
    pnpm: 0.5,
  },

  // 依赖解析速度 (相对值，npm = 1.0)
  dependencyResolution: {
    npm: 1.0,
    yarn: 0.6,
    pnpm: 0.2,
  },
};
```

## 📦 npm 使用指南

### 基础命令
**npm 常用命令和配置**

```bash
# 初始化项目
npm init -y
npm init -y --scope=@myorg  # 设置包作用域

# 安装依赖
npm install react              # 安装到 dependencies
npm install -D typescript      # 安装到 devDependencies
npm install --global nodemon   # 全局安装

# 版本控制
npm install react@18.0.0       # 安装特定版本
npm install react@^18.0.0      # 兼容版本更新
npm install react@latest        # 最新版本
npm install react@next          # 下一个版本

# 依赖管理
npm list                        # 列出依赖
npm list --depth=0              # 只列出直接依赖
npm outdated                    # 检查过时依赖
npm update                      # 更新依赖
npm uninstall react             # 卸载依赖

# 脚本执行
npm run dev                     # 执行脚本
npm run build                   # 执行构建脚本
npm run test -- --watch         # 传递参数

# 审计和安全
npm audit                       # 安全审计
npm audit fix                   # 修复安全问题
npm audit fix --force           # 强制修复

# 缓存管理
npm cache clean --force         # 清理缓存
npm cache verify                # 验证缓存
```

### package.json 配置
**优化项目配置文件**

```json
{
  "name": "@myorg/my-next-app",
  "version": "1.0.0",
  "private": true,
  "description": "A Next.js application with modern tooling",
  "keywords": ["nextjs", "react", "typescript"],
  "author": "Your Name <your.email@example.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourorg/your-repo.git"
  },
  "bugs": {
    "url": "https://github.com/yourorg/your-repo/issues"
  },
  "homepage": "https://your-app.example.com",

  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },

  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "analyze": "ANALYZE=true npm run build",
    "clean": "rm -rf .next dist node_modules/.cache",
    "postinstall": "prisma generate",
    "prepare": "husky install"
  },

  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "^5.0.0"
  },

  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.0.0",
    "husky": "^8.0.0",
    "lint-staged": "^15.0.0"
  },

  "overrides": {
    "package-with-issue": "2.0.1"
  },

  "pnpm": {
    "overrides": {
      "package-with-issue": "2.0.1"
    }
  },

  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
}
```

### .npmrc 配置
**npm 配置文件**

```ini
# .npmrc
registry=https://registry.npmjs.org/

# 设置镜像源
# registry=https://registry.npmmirror.com/

# 设置代理
# proxy=http://proxy.company.com:8080
# https-proxy=http://proxy.company.com:8080

# 认证配置
# //registry.npmjs.org/:_authToken=${NPM_TOKEN}

# 缓存配置
cache=/path/to/cache
cache-max=86400000

# 工作区配置
workspaces=true

# 严格模式
strict-peer-deps=true

# 前缀
prefix=/usr/local

# 保存前缀
save-prefix=^

# 精确安装
save-exact=false

# 包锁文件
package-lock=true

# 工作区设置
workspace-linker=workspace

# 忽略脚本
ignore-scripts=false

# 脚本 Shell
script-shell=bash

# 算法
algorithm=shallow

# 元数据更新
update-notifier=true
```

## 🧶 Yarn 使用指南

### Yarn Berry (Yarn 2+) 配置
**现代化 Yarn 配置**

```bash
# 升级到 Yarn Berry
yarn set version berry

# 或者指定特定版本
yarn set version 3.6.0

# 启用 PnP (Plug-n-Play)
yarn config set nodeLinker pnp

# 启用零安装
yarn config set enableGlobalCache false

# 设置缓存路径
yarn config set cacheFolder .yarn/cache

# 设置插件路径
yarn config set pluginPath .yarn/plugins
```

### .yarnrc.yml 配置
**Yarn Berry 配置文件**

```yaml
# .yarnrc.yml
yarnPath: .yarn/releases/yarn-3.6.0.cjs

# 插件配置
plugins:
  - path: .yarn/plugins/@yarnpkg/plugin-interactive-tools.cjs
    spec: "@yarnpkg/plugin-interactive-tools"
  - path: .yarn/plugins/@yarnpkg/plugin-workspace-tools.cjs
    spec: "@yarnpkg/plugin-workspace-tools"

# PnP 配置
pnpEnableEsmLoader: true
pnpMode: loose

# 缓存配置
cacheFolder: .yarn/cache
enableGlobalCache: false

# 工作区配置
enableTelemetry: false

# 安装模式
nmMode: hardlinks

# 忽略平台
ignorePlatform: []

# 忽略 engines
ignoreEngines: false

# 严格模式
strictPeerDependencies: true

# 离线模式
enableOfflineMode: false

# 包配置
packageExtensions:
  "@types/react@npm:^18.0.0":
    dependencies:
      "@types/react-dom": "*"

# 解析策略
preferInteractiveUpdates: true
```

### Yarn 命令
**Yarn 常用命令**

```bash
# 项目初始化
yarn init -2                     # 使用 Yarn Berry 初始化
yarn create next-app my-app      # 创建 Next.js 应用

# 依赖管理
yarn add react                  # 添加依赖
yarn add -D typescript          # 添加开发依赖
yarn remove react               # 移除依赖

# 版本控制
yarn add react@18.2.0          # 安装特定版本
yarn add react@^18.2.0         # 安装兼容版本
yarn up react                   # 更新到最新版本
yarn up -i react                # 交互式更新

# 工作区
yarn workspace @myapp/ui add react
yarn workspaces focus
yarn workspaces foreach run build

# 插件管理
yarn plugin import https://raw.githubusercontent.com/yarnpkg/berry/master/plugins/@yarnpkg/plugin-workspace-tools/bundles/@yarnpkg/plugin-workspace-tools.js
yarn plugin runtime

# 信息查询
yarn info react                 # 查看包信息
yarn why react                  # 查看为什么需要某个包
yarn list                       # 列出依赖
yarn outdated                   # 查看过时依赖

# 缓存管理
yarn cache clean                # 清理缓存
yarn cache list                 # 列出缓存

# 全局包管理
yarn global add nodemon
yarn global remove nodemon
yarn global list

# 离线模式
yarn add --offline react
yarn install --offline

# 约束检查
yarn constraints
```

## 🚀 pnpm 使用指南

### pnpm 配置
**高效的 pnpm 配置**

```bash
# 全局安装 pnpm
npm install -g pnpm

# 或者使用 npm 安装
corepack enable pnpm

# 项目中使用 pnpm
pnpm create next-app my-app --typescript
pnpm install                    # 安装依赖
pnpm add react                  # 添加依赖
pnpm add -D typescript          # 添加开发依赖

# 工作区
pnpm workspace add react
pnpm -r install                 # 在所有工作区安装
pnpm -r run build               # 在所有工作区运行脚本
```

### .pnpmrc 配置
**pnpm 配置文件**

```ini
# .pnpmrc
# 注册表配置
registry=https://registry.npmjs.org/

# 镜像源
# registry=https://registry.npmmirror.com/

# 严格模式
strict-peer-dependencies=true
strict-peer-dependencies=true

# 存储配置
store-dir=~/.pnpm-store
virtual-store-dir=node_modules/.pnpm

# 符号链接策略
shamefully-hoist=false
shamefully-hoist=true

# 自动安装对等依赖
auto-install-peers=true

# 工作区配置
link-workspace-packages=true
prefer-workspace-packages=true

# 更新检查
update-notifier=true

# 进度显示
prefer-frozen-lockfile=true
save-exact=false

# 保存前缀
save-prefix="^"

# 完整安装
prefer-frozen-lockfile=true

# 忽略开发依赖
dev-dependencies=true

# 纯净安装
frozen-lockfile=false

# 忽略可选依赖
optional-dependencies=true

# 锁文件格式
lockfile-version=6

# 纯净安装
use-node-version=18

# 激活配置
shell-emulator=true

# 日志级别
loglevel=info

# 并发数
child-concurrency=4

# 网络超时
fetch-timeout=60000
fetch-retry-max=2
fetch-retry-mintimeout=10000

# 代理配置
# proxy=http://proxy.company.com:8080
# https-proxy=http://proxy.company.com:8080
```

### pnpm-workspace.yaml
**工作区配置**

```yaml
# pnpm-workspace.yaml
packages:
  # 应用包
  - 'apps/*'

  # 包
  - 'packages/*'

  # 工具
  - 'tools/*'

# 排除特定包
packages:
  - '!**/test/**'
  - '!**/__tests__/**'
  - '!**/examples/**'
```

### pnpm 命令
**pnpm 常用命令**

```bash
# 基础命令
pnpm install                    # 安装依赖
pnpm install --frozen-lockfile  # 锁定安装
pnpm install --force           # 强制重新安装

# 依赖管理
pnpm add react                  # 添加到 dependencies
pnpm add -D typescript          # 添加到 devDependencies
pnpm add -O eslint              # 添加到 optionalDependencies
pnpm remove react               # 移除依赖

# 版本管理
pnpm add react@18.2.0          # 安装特定版本
pnpm update react               # 更新到最新版本
pnpm update --interactive      # 交互式更新
pnpm outdated                   # 查看过时依赖

# 工作区命令
pnpm -r install                 # 在所有工作区安装
pnpm -r run build               # 在所有工作区运行脚本
pnpm -F '@myorg/ui' dev         # 在特定工作区运行
pnpm -w add react              # 在根工作区添加

# 脚本执行
pnpm dev                        # 运行开发脚本
pnpm build                      # 运行构建脚本
pnpm test -- --watch            # 传递参数

# 审计
pnpm audit                      # 安全审计
pnpm audit --fix                # 修复安全漏洞

# 缓存管理
pnpm store prune                # 清理未使用的包
pnpm store path                 # 显示存储路径
pnpm store status               # 显示存储状态

# 信息查询
pnpm list                       # 列出依赖
pnpm why react                  # 查看为什么需要某个包
pnpm ls --depth=0              # 只显示直接依赖

# 创建项目
pnpm create next-app my-app
pnpm create vite my-app --template react-ts

# 全局包
pnpm add -g typescript
pnpm add -g @vercel/ncc

# 覆盖依赖
pnpm add react@16.0.0 --filter=my-app
```

## 🏢 Monorepo 管理

### Workspaces 配置
**统一的 Monorepo 配置**

```json
// package.json (根目录)
{
  "name": "@myorg/monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*",
    "tools/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules",
    "format": "prettier --write .",
    "changeset": "changeset",
    "version-packages": "changeset version",
    "release": "turbo run build && changeset publish"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "@changesets/cli": "^2.26.0",
    "prettier": "^3.0.0",
    "eslint": "^8.0.0"
  }
}
```

### Turbo 配置
**高性能 Monorepo 工具**

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [
    "**/.env.*local",
    "tsconfig.json",
    "next.config.js",
    "tailwind.config.js"
  ],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"],
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "cache": true
    },
    "lint": {
      "outputs": [],
      "cache": true
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": [],
      "cache": true
    },
    "clean": {
      "cache": false
    }
  }
}
```

### 依赖管理策略
**Monorepo 依赖管理最佳实践**

```json
// packages/ui/package.json
{
  "name": "@myorg/ui",
  "version": "1.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./components": {
      "import": "./dist/components/index.mjs",
      "require": "./dist/components/index.js",
      "types": "./dist/components/index.d.ts"
    }
  },
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "test": "jest",
    "lint": "eslint src --ext .ts,.tsx",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tsup": "^7.0.0",
    "typescript": "^5.0.0"
  },
  "peerDependencies": {
    "react": ">=18.0.0",
    "react-dom": ">=18.0.0"
  }
}
```

## 🔧 工具集成

### TypeScript 项目引用
**大型 TypeScript 项目管理**

```json
// tsconfig.json (根目录)
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "incremental": true,
    "composite": true,
    "declaration": true,
    "declarationMap": true
  },
  "references": [
    { "path": "./packages/ui" },
    { "path": "./packages/utils" },
    { "path": "./apps/web" }
  ]
}
```

### ESLint 配置
**Monorepo 代码质量检查**

```javascript
// eslint.config.js
const eslintConfig = {
  root: true,
  extends: [
    '@myorg/eslint-config/base',
    '@myorg/eslint-config/react',
    '@myorg/eslint-config/typescript',
  ],
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.test.tsx'],
      env: {
        jest: true,
      },
    },
  ],
};

module.exports = eslintConfig;
```

### Husky 配置
**Git hooks 管理**

```bash
# 安装 Husky
pnpm add -D husky

# 启用 Git hooks
npx husky install

# 添加 pre-commit hook
npx husky add .husky/pre-commit "pnpm lint-staged"

# 添加 commit-msg hook
npx husky add .husky/commit-msg "pnpm commitlint --edit $1"
```

```json
// package.json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
}
```

## 📊 性能优化

### 缓存策略
**优化依赖安装和构建缓存**

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Install pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run tests
        run: pnpm test

      - name: Run type check
        run: pnpm type-check

      - name: Run lint
        run: pnpm lint
```

### 依赖分析
**分析项目依赖结构**

```bash
# 依赖分析工具
npm install -g depcheck
pnpm dlx depcheck

# Bundle 分析
npm install -g webpack-bundle-analyzer
pnpm dlx bundlephobia

# pnpm 依赖分析
pnpm why react
pnpm list --depth=0
pnpm list --json

# 检查重复依赖
pnpm list --depth=1 | grep -E "^[├└]" | sort | uniq -c | sort -nr
```

## 📋 最佳实践

### 依赖管理最佳实践
- [ ] 使用固定版本或兼容版本
- [ ] 定期更新依赖和审计安全
- [ ] 使用 workspace 管理多包项目
- [ ] 配置适当的缓存策略
- [ ] 使用 .npmignore 或 .gitignore 忽略文件

### 安全实践
- [ ] 定期运行安全审计
- [ ] 使用私有注册表配置
- [ ] 配置 CI/CD 中的依赖扫描
- [ ] 使用内容安全策略 (CSP)
- [ ] 管理访问令牌和密钥

### 性能优化
- [ ] 选择合适的包管理器
- [ ] 配置缓存和存储优化
- [ ] 使用零安装模式 (可选)
- [ ] 优化 CI/CD 中的依赖安装
- [ ] 监控依赖大小和安装时间

## 📖 总结

现代包管理器提供了高效的依赖管理解决方案：

### npm:
- **优势**: Node.js 默认、生态成熟、文档完善
- **适用场景**: 传统项目、需要最大兼容性
- **配置**: package.json + .npmrc

### Yarn:
- **优势**: 速度快、PnP 模式、Workspaces 支持
- **适用场景**: 大型项目、需要零安装
- **配置**: .yarnrc.yml + Yarn Berry

### pnpm:
- **优势**: 极速安装、磁盘高效、严格依赖管理
- **适用场景**: Monorepo、资源受限环境
- **配置**: .pnpmrc + pnpm-workspace.yaml

### 选择建议：
1. **新项目**: 考虑 pnpm 或 Yarn Berry
2. **团队项目**: 选择团队熟悉的工具
3. **Monorepo**: 推荐 pnpm + Turbo
4. **CI/CD**: 配置缓存和优化策略

## 🔄 文档交叉引用

### 相关文档
- 📄 **[测试工具](./01-testing-tools.md)**: 测试依赖管理和测试环境配置
- 📄 **[样式工具](./02-styling-tools.md)**: 样式库包管理和版本控制
- 📄 **[调试工具](./04-debugging-tools.md)**: 调试工具包管理和环境配置
- 📄 **[渲染优化](../performance-optimization/01-rendering-optimization.md)**: 依赖优化和性能管理
- 📄 **[打包优化](../performance-optimization/02-bundle-optimization.md)**: 打包依赖和tree shaking优化

### 参考章节
- 📖 **[npm配置](#npm-使用指南)**: Node.js默认包管理器
- 📖 **[Yarn配置](#yarn-使用指南)**: Facebook开发的高性能包管理器
- 📖 **[pnpm配置](#pnpm-使用指南)**: 高效的磁盘空间管理包管理器
- 📖 **[Monorepo管理](#monorepo-管理)**: 多包项目管理和工作区配置
- 📖 **[工具集成](#工具集成)**: 构建工具和CI/CD集成

---

## 📝 总结

### 核心要点回顾
1. **包管理器选择**: npm(默认稳定) → yarn(快速) → pnpm(高效)的合理选择策略
2. **依赖管理**: 版本控制、安全审计、依赖分析的完整管理体系
3. **Monorepo架构**: 工作区管理、依赖共享、构建协调的企业级解决方案
4. **性能优化**: 缓存策略、并行安装、磁盘空间优化的最佳实践
5. **CI/CD集成**: 自动化构建、依赖缓存、安全扫描的持续集成流程

### 学习成果检查
- [ ] 能够选择和配置适合项目的包管理器(npm/yarn/pnpm)
- [ ] 掌握依赖版本管理和安全审计的最佳实践
- [ ] 熟练配置Monorepo项目的工作区和构建流程
- [ ] 能够实施依赖分析和性能优化策略
- [ ] 理解CI/CD环境中的依赖管理和缓存优化

---

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

---

## 🔗 外部资源

### 官方文档
- **npm**: [官方文档](https://docs.npmjs.com/) - Node.js包管理器
- **Yarn**: [官方文档](https://yarnpkg.com/) - 快速、可靠、安全的依赖管理
- **pnpm**: [官方文档](https://pnpm.io/) - 快速、节省磁盘空间的包管理器
- **Turborepo**: [官方文档](https://turbo.build/) - 高性能Monorepo构建系统

### 快速参考
- **包管理器对比**: [Package Manager Comparison](https://nodejs.dev/learn/an-introduction-to-the-npm-package-manager) - 选择指南
- **语义化版本**: [SemVer规范](https://semver.org/) - 版本控制标准
- **依赖安全**: **npm audit** [安全审计指南](https://docs.npmjs.com/cli/v8/commands/npm-audit) - 安全检查和修复
- **Monorepo工具**: [Nx](https://nx.dev/) - 企业级Monorepo解决方案

---

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0