# Monorepo 策略 - Next.js 15 现代架构实践

## 📋 概述

Monorepo（单一仓库）是一种将多个项目存储在同一个Git仓库中的策略。Next.js 15 结合现代化的工具链，为Monorepo提供了强大的支持。本文将深入探讨如何在Next.js 15项目中实施和管理Monorepo策略。

## 🎯 Monorepo 基础概念

### 1. 什么是 Monorepo？

Monorepo 是将多个相关项目存储在同一个Git仓库中的策略：

```
monorepo/
├── packages/
│   ├── app1/          # Next.js应用1
│   ├── app2/          # Next.js应用2
│   ├── shared-ui/     # 共享UI组件
│   ├── shared-utils/   # 共享工具函数
│   └── shared-types/   # 共享类型定义
├── apps/              # 应用目录
├── libs/              # 库目录
└── tools/             # 构建工具
```

### 2. Monorepo vs Multirepo

| 特性 | Monorepo | Multirepo |
|------|---------|-----------|
| **代码共享** | ✅ 简单直接 | ❌ 需要发布包 |
| **依赖管理** | ✅ 统一管理 | ❌ 分散管理 |
| **原子提交** | ✅ 支持跨项目修改 | ❌ 需要多个PR |
| **CI/CD** | ✅ 统一构建流程 | ❌ 独立构建流程 |
| **权限控制** | ❌ 全仓库访问 | ✅ 细粒度控制 |
| **学习成本** | ❌ 复杂性高 | ✅ 简单直接 |

## 🚀 Next.js 15 Monorepo 实践

### 1. 使用 Turborepo

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  },
  "globalEnv": [
    "NODE_ENV",
    "NEXT_PUBLIC_API_URL",
    "NEXT_PUBLIC_APP_URL"
  ]
}
```

```json
// package.json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*",
    "tools/*"
  ],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "clean": "turbo run clean",
    "format": "prettier --write \"**/*.{ts,tsx,md}\""
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  }
}
```

### 2. 项目结构设计

```
my-monorepo/
├── apps/
│   ├── web/                    # 主Web应用
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── src/
│   ├── admin/                  # 管理后台
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── src/
│   └── mobile/                 # 移动端应用
│       ├── package.json
│       ├── next.config.js
│       └── src/
├── packages/
│   ├── ui/                     # 共享UI组件
│   │   ├── package.json
│   │   ├── src/
│   │   └── tailwind.config.js
│   ├── utils/                  # 共享工具函数
│   │   ├── package.json
│   │   └── src/
│   ├── types/                  # 共享类型定义
│   │   ├── package.json
│   │   └── src/
│   └── hooks/                  # 共享React Hooks
│       ├── package.json
│       └── src/
├── tools/
│   ├── eslint-config/          # ESLint配置
│   ├── prettier-config/        # Prettier配置
│   └── typescript-config/      # TypeScript配置
├── configs/                    # 配置文件
│   ├── tailwind.config.js      # Tailwind配置
│   ├── tsconfig.json           # 根TypeScript配置
│   └── .eslintrc.json          # ESLint配置
├── scripts/                    # 构建脚本
│   ├── build-all.js
│   └── deploy-all.js
└── package.json                # 根package.json
```

### 3. 共享包配置

```json
// packages/ui/package.json
{
  "name": "@my-monorepo/ui",
  "version": "0.1.0",
  "main": "dist/index.js",
  "module": "dist/index.esm.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "dev": "tsup src/index.ts --format cjs,esm --dts --watch",
    "clean": "rm -rf dist"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "next": "^13.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tsup": "^6.0.0",
    "typescript": "^5.0.0"
  }
}
```

```json
// packages/utils/package.json
{
  "name": "@my-monorepo/utils",
  "version": "0.1.0",
  "main": "dist/index.js",
  "module": "dist/index.esm.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "test": "jest",
    "clean": "rm -rf dist"
  },
  "devDependencies": {
    "@types/jest": "^29.0.0",
    "jest": "^29.0.0",
    "tsup": "^6.0.0",
    "typescript": "^5.0.0"
  }
}
```

## 🎨 高级 Monorepo 模式

### 1. 共享配置管理

```typescript
// configs/typescript-config/base.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true,
    "incremental": true
  }
}
```

```typescript
// configs/eslint-config/base.js
module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/no-explicit-any': 'warn',
    'react-hooks/exhaustive-deps': 'warn',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

```typescript
// configs/prettier-config/index.js
module.exports = {
  semi: false,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'es5',
  printWidth: 80,
  bracketSpacing: true,
  arrowParens: 'avoid',
};
```

### 2. 工作空间配置

```typescript
// apps/web/package.json
{
  "name": "@my-monorepo/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^13.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@my-monorepo/ui": "workspace:*",
    "@my-monorepo/utils": "workspace:*",
    "@my-monorepo/types": "workspace:*",
    "@my-monorepo/hooks": "workspace:*"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^13.0.0"
  }
}
```

### 3. 构建和部署配置

```typescript
// scripts/build-all.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const apps = ['web', 'admin', 'mobile'];
const packages = ['ui', 'utils', 'types', 'hooks'];

async function buildAll() {
  console.log('🚀 Building all packages...');

  // 构建共享包
  for (const pkg of packages) {
    console.log(`Building package: ${pkg}`);
    execSync(`cd packages/${pkg} && npm run build`, { stdio: 'inherit' });
  }

  // 构建应用
  for (const app of apps) {
    console.log(`Building app: ${app}`);
    execSync(`cd apps/${app} && npm run build`, { stdio: 'inherit' });
  }

  console.log('✅ All builds completed successfully!');
}

buildAll().catch(console.error);
```

```typescript
// scripts/deploy-all.js
const { execSync } = require('child_process');

const apps = [
  { name: 'web', vercelProjectId: 'prj_abc123' },
  { name: 'admin', vercelProjectId: 'prj_def456' },
  { name: 'mobile', vercelProjectId: 'prj_ghi789' },
];

async function deployAll() {
  console.log('🚀 Deploying all apps...');

  for (const app of apps) {
    console.log(`Deploying app: ${app.name}`);
    execSync(`cd apps/${app.name} && npx vercel --prod`, {
      env: {
        ...process.env,
        VERCEL_PROJECT_ID: app.vercelProjectId,
      },
      stdio: 'inherit',
    });
  }

  console.log('✅ All deployments completed successfully!');
}

deployAll().catch(console.error);
```

## 🔄 依赖管理策略

### 1. 版本管理

```json
// package.json (根目录)
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "clean": "turbo run clean",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "version": "changeset version",
    "release": "changeset publish",
    "update-deps": "npm-check-updates -u"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0",
    "@changesets/cli": "^2.26.0"
  }
}
```

### 2. Changeset 配置

```yaml
# .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@2.3.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

```yaml
# .changeset/config.md
---
"my-monorepo": "patch"
---
```

### 3. 依赖同步

```typescript
// scripts/sync-deps.js
const fs = require('fs');
const path = require('path');

const apps = ['web', 'admin', 'mobile'];
const commonDeps = {
  'react': '^18.2.0',
  'react-dom': '^18.2.0',
  'next': '^13.4.0',
  'typescript': '^5.0.0',
  '@types/react': '^18.2.0',
  '@types/react-dom': '^18.2.0',
};

apps.forEach(app => {
  const packageJsonPath = path.join(__dirname, '..', 'apps', app, 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

  // 更新依赖版本
  Object.keys(commonDeps).forEach(dep => {
    if (packageJson.dependencies?.[dep]) {
      packageJson.dependencies[dep] = commonDeps[dep];
    }
    if (packageJson.devDependencies?.[dep]) {
      packageJson.devDependencies[dep] = commonDeps[dep];
    }
  });

  fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2) + '\n');
});

console.log('✅ Dependencies synchronized successfully!');
```

## 🎯 开发工作流程

### 1. 开发环境配置

```typescript
// tools/dev-server.js
const { createServer } = require('http');
const next = require('next');

const apps = ['web', 'admin', 'mobile'];
const devServers = {};

async function startDevServers() {
  console.log('🚀 Starting development servers...');

  for (const app of apps) {
    const appNext = next({
      dev: true,
      dir: `./apps/${app}`,
      port: 3000 + apps.indexOf(app),
      hostname: 'localhost',
    });

    await appNext.prepare();

    const server = createServer(appNext.getRequestHandler());
    server.listen(3000 + apps.indexOf(app), (err) => {
      if (err) throw err;
      console.log(`📱 ${app} app ready on http://localhost:${3000 + apps.indexOf(app)}`);
    });

    devServers[app] = { app: appNext, server };
  }
}

startDevServers().catch(console.error);
```

### 2. 代码检查和格式化

```json
// .lintstagedrc.json
{
  "*.{js,jsx,ts,tsx}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{json,md,yml,yaml}": [
    "prettier --write"
  ]
}
```

```json
// .husky/pre-commit
#!/bin/sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
npx turbo run test
```

### 3. 测试策略

```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleNameMapping: {
    '^@my-monorepo/(.+)$': '<rootDir>/packages/$1/src',
  },
  collectCoverageFrom: [
    'packages/**/src/**/*.{ts,tsx}',
    'apps/**/src/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
};
```

```typescript
// jest.setup.js
import '@testing-library/jest-dom';

// 模拟Next.js路由
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    };
  },
}));

// 模拟环境变量
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:3001/api';
```

## 🚨 高级功能和优化

### 1. 缓存优化

```typescript
// turbo.json (优化版)
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"],
      "cache": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": [],
      "cache": true
    },
    "lint": {
      "outputs": [],
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    },
    "type-check": {
      "outputs": [],
      "cache": true
    }
  },
  "globalEnv": [
    "NODE_ENV",
    "NEXT_PUBLIC_API_URL",
    "NEXT_PUBLIC_APP_URL"
  ]
}
```

### 2. 环境变量管理

```typescript
// packages/env/src/index.ts
export interface Environment {
  NODE_ENV: 'development' | 'production' | 'test';
  NEXT_PUBLIC_API_URL: string;
  NEXT_PUBLIC_APP_URL: string;
  DATABASE_URL: string;
  REDIS_URL: string;
}

export const getEnvironment = (): Environment => {
  return {
    NODE_ENV: process.env.NODE_ENV || 'development',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
    DATABASE_URL: process.env.DATABASE_URL || '',
    REDIS_URL: process.env.REDIS_URL || '',
  };
};

export const validateEnvironment = (env: Environment): boolean => {
  const required = ['NODE_ENV', 'NEXT_PUBLIC_API_URL', 'NEXT_PUBLIC_APP_URL'];
  return required.every(key => env[key as keyof Environment]);
};
```

### 3. 监控和日志

```typescript
// packages/monitoring/src/index.ts
export class MonorepoMonitor {
  private static instance: MonorepoMonitor;

  private constructor() {}

  static getInstance(): MonorepoMonitor {
    if (!MonorepoMonitor.instance) {
      MonorepoMonitor.instance = new MonorepoMonitor();
    }
    return MonorepoMonitor.instance;
  }

  logBuildSuccess(app: string, duration: number) {
    console.log(`✅ ${app} built successfully in ${duration}ms`);
  }

  logBuildFailure(app: string, error: Error) {
    console.error(`❌ ${app} build failed:`, error.message);
  }

  logTestResults(app: string, results: any) {
    console.log(`📊 ${app} test results:`, {
      total: results.numTotalTests,
      passed: results.numPassedTests,
      failed: results.numFailedTests,
      coverage: results.coverage,
    });
  }
}
```

## 🎯 总结

Next.js 15 的 Monorepo 策略为大型项目提供了高效的管理和开发体验。通过合理使用 Turborepo、共享包管理和自动化工具，可以构建出可维护、可扩展的现代Web应用架构。

### 关键要点：

1. **架构设计**：Turborepo配置、项目结构、共享包管理
2. **依赖管理**：版本同步、Changeset、工作空间配置
3. **开发流程**：开发环境、代码检查、测试策略
4. **性能优化**：缓存优化、环境变量管理、监控日志
5. **最佳实践**：模块化设计、标准化流程、自动化部署

### 实施建议：

- **渐进式迁移**：从现有项目开始，逐步迁移到Monorepo
- **工具选择**：选择合适的工具链（Turborepo、Nx等）
- **标准化**：建立统一的开发规范和流程
- **自动化**：构建完整的CI/CD流程和工具链

通过掌握这些Monorepo技术，可以显著提升大型项目的开发效率和代码质量。