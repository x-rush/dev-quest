# Next.js 开发环境搭建

## 概述

本指南将帮助你搭建Next.js 15开发环境，包含所有必要的工具和配置。作为PHP开发者，你会发现现代前端开发环境的配置方式与传统的PHP开发环境有很大不同。

## 系统要求

### 基本要求
- **Node.js**: 18.17.0 或更高版本
- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **内存**: 推荐 8GB 以上
- **存储**: 推荐 10GB 可用空间

### 推荐配置
- **Node.js**: 20.x LTS 版本
- **包管理器**: pnpm 8.x 或 npm 9.x
- **IDE**: VS Code 1.80+
- **终端**: 支持现代Shell的终端工具

## 安装步骤

### 1. 安装 Node.js

#### macOS (使用 Homebrew)
```bash
# 安装 Node.js 20 LTS
brew install node@20

# 验证安装
node --version
npm --version
```

#### Windows (使用 Winget)
```powershell
# 安装 Node.js 20 LTS
winget install OpenJS.NodeJS.20

# 验证安装
node --version
npm --version
```

#### Linux (Ubuntu/Debian)
```bash
# 使用 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 2. 安装包管理器

#### 推荐使用 pnpm
```bash
# 全局安装 pnpm
npm install -g pnpm

# 验证安装
pnpm --version
```

#### 配置 npm 镜像（中国大陆用户）
```bash
# 设置 npm 镜像
npm config set registry https://registry.npmmirror.com

# 设置 pnpm 镜像
pnpm config set registry https://registry.npmmirror.com
```

### 3. 安装代码编辑器

#### VS Code 安装
```bash
# macOS
brew install --cask visual-studio-code

# Windows (Winget)
winget install Microsoft.VisualStudioCode

# Linux (Ubuntu)
sudo snap install --classic code
```

#### 必要的 VS Code 扩展
```bash
# 安装推荐的扩展
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension ms-vscode.vscode-json
code --install-extension ms-vscode.vscode-eslint
```

### 4. 创建 Next.js 项目

#### 使用 create-next-app
```bash
# 创建新的 Next.js 项目
npx create-next-app@latest my-nextjs-app --typescript --tailwind --app --src-dir --import-alias "@/*"

# 或者使用 pnpm
pnpm create next-app my-nextjs-app --typescript --tailwind --app --src-dir --import-alias "@/*"

# 进入项目目录
cd my-nextjs-app
```

#### 项目选项说明
- `--typescript`: 使用 TypeScript
- `--tailwind`: 集成 Tailwind CSS
- `--app`: 使用 App Router
- `--src-dir`: 使用 src 目录结构
- `--import-alias "@/*"`: 设置路径别名

### 5. 配置开发环境

#### 安装项目依赖
```bash
# 使用 npm
npm install

# 使用 pnpm
pnpm install
```

#### 启动开发服务器
```bash
# 使用 npm
npm run dev

# 使用 pnpm
pnpm dev
```

访问 http://localhost:3000 查看应用。

## 环境配置文件

### 1. package.json
```json
{
  "name": "my-nextjs-app",
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
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "next": "15.0.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "15.0.0"
  }
}
```

### 2. tsconfig.json
```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 3. next.config.js
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbopack: true, // 启用 Turbopack
  },
  images: {
    domains: ['example.com'], // 配置允许的图片域名
  },
  typescript: {
    ignoreBuildErrors: false, // 生产环境严格类型检查
  },
  eslint: {
    ignoreDuringBuilds: false, // 生产环境严格ESLint检查
  },
}

module.exports = nextConfig
```

### 4. .env.local
```bash
# 应用配置
NEXT_PUBLIC_APP_NAME="My Next.js App"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# API 配置
NEXT_PUBLIC_API_URL="http://localhost:3001/api"
DATABASE_URL="postgresql://username:password@localhost:5432/mydb"

# 认证配置
NEXTAUTH_SECRET="your-nextauth-secret"
NEXTAUTH_URL="http://localhost:3000"
```

## 开发工具配置

### 1. ESLint 配置
创建 `.eslintrc.json`:
```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

### 2. Prettier 配置
创建 `.prettierrc`:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

### 3. Git 配置
创建 `.gitignore`:
```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Next.js
.next/
out/

# Production
build/

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env*.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts
```

### 4. VS Code 工作区配置
创建 `.vscode/settings.json`:
```json
{
  "typescript.preferences.preferTypeOnlyAutoImports": true,
  "typescript.suggest.autoImports": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.tabSize": 2,
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/.next": true,
    "**/dist": true
  }
}
```

## 与 PHP 开发的对比

### 开发环境对比
| PHP 开发 | Next.js 开发 |
|---------|-------------|
| LAMP/LEMP 栈 | Node.js + Next.js |
| Apache/Nginx | Next.js 开发服务器 |
| PHP-FPM | Node.js 运行时 |
| MySQL | PostgreSQL/其他数据库 |
| FTP 部署 | Git + CI/CD 部署 |

### 开发流程对比
| PHP 开发 | Next.js 开发 |
|---------|-------------|
| 编写 PHP 代码 | 编写 React 组件 |
| 刷新浏览器查看结果 | 热重载 (HMR) |
| 手动处理依赖 | npm/pnpm 管理依赖 |
| 服务器端渲染 | 混合渲染 (SSR/SSG/ISR) |
| 传统调试 | React DevTools + 浏览器工具 |

## 常见问题解决

### 1. Node.js 版本问题
```bash
# 使用 nvm 管理多个 Node.js 版本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装特定版本的 Node.js
nvm install 20
nvm use 20
```

### 2. 权限问题
```bash
# 修复 npm 权限问题
sudo chown -R $(whoami) ~/.npm
```

### 3. 端口占用
```bash
# 查找占用端口的进程
lsof -i :3000

# 终止进程
kill -9 <PID>
```

### 4. 内存不足
```bash
# 增加 Node.js 内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
```

## 开发最佳实践

### 1. 代码组织
- 使用 src 目录结构
- 按功能模块组织代码
- 统一命名规范

### 2. 版本控制
- 使用语义化版本
- 定期提交代码
- 编写清晰的提交信息

### 3. 依赖管理
- 定期更新依赖
- 使用固定版本号
- 监控安全漏洞

### 4. 性能优化
- 使用 Turbopack 开发服务器
- 启用 TypeScript 严格模式
- 配置代码分割

## 下一步

完成环境搭建后，你可以继续学习：

1. **TypeScript 基础** - 掌握 TypeScript 核心概念
2. **React 基础** - 学习 React 组件开发
3. **Next.js 路由** - 理解 App Router 系统
4. **样式解决方案** - 掌握 Tailwind CSS

---

*本指南提供了完整的 Next.js 15 开发环境搭建流程，帮助你快速开始现代前端开发之旅。*