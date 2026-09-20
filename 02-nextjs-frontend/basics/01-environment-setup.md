# Next.js 16 开发环境搭建

## 先理解，再动手

先确认 Node、包管理器和工程目录，再创建应用。锁文件记录依赖解析结果，脚手架版本与最终依赖版本并不是同一个概念。

**本节自测**：创建项目后记录启动命令、package.json 的 scripts 和锁文件，再改首页标题。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

应能在浏览器看到新标题；仅看到安装成功还没有证明项目启动和热更新正常。

</details>

> **文档简介**: 从 Node、包管理器和脚手架开始，建立能启动、可检查、可复现的 Next.js 16 学习环境

> **目标读者**: 初学者和需要环境升级的开发者，希望搭建标准化Next.js开发环境的前端工程师

> **前置知识**: 基础命令行操作、Git版本控制基础、JavaScript基础概念

> **预计时长**: 2-3小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `basics` |
| **难度** | ⭐ |
| **标签** | `#environment-setup` `#nodejs` `#development-tools` `#git` `#ide` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

- 搭建并验收一个 Next.js 16 开发环境
- 安装和配置必要的开发工具
- 理解现代前端开发工作流程
- 配置TypeScript、ESLint和Prettier
- 设置Git和版本控制
- 创建第一个Next.js项目

## 📖 概述

本章的产物是一个有锁文件、明确 Node 版本、能独立运行 lint、类型检查和开发服务器的应用。编辑器扩展和镜像是可选辅助工具，不是项目能否构建的前提。

## 💻 系统要求

### 最低要求
- **Node.js**: 20.9.0 或更高版本；本仓当前复现基线为 Node 24
- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **内存**: 推荐使用8GB以上
- **存储空间**: 10GB可用空间
- **网络连接**: 安装软件包时需要

### 推荐配置
- **Node.js**: Node 24（使用受支持的当前 LTS/维护线；项目实际要求仍以 `package.json` 的 `engines` 为准）
- **包管理器**: Corepack 管理的 pnpm 11，或项目锁文件指定的包管理器版本
- **IDE**: VS Code 1.80+ 推荐扩展
- **终端**: 支持UTF-8的现代Shell
- **浏览器**: Chrome/Firefox最新版本用于开发

## 🚀 安装步骤

### 1. 安装Node.js

#### macOS (使用Homebrew)
```bash
# 如果尚未安装Homebrew，先安装它
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Node 24
brew install node@24

# 验证安装
node --version
npm --version
```

#### Windows (使用Winget)
```powershell
# 安装 Node 24
winget install OpenJS.NodeJS.24

# 验证安装
node --version
npm --version
```

#### Linux (Ubuntu/Debian)
```bash
# 使用 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

#### 替代方案：使用Node版本管理器(nvm)
```bash
# 安装nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载Shell
source ~/.bashrc

# 安装并使用 Node 24
nvm install 24
nvm use 24
nvm alias default 24

# 验证安装
node --version
npm --version
```

### 2. 安装包管理器

#### 推荐：pnpm
```bash
# 启用 Corepack；随后由项目 packageManager 字段或 lock 文件决定 pnpm 版本。
corepack enable
pnpm --version

# 若当前 Node 发行版没有可用的 Corepack，再按 pnpm 官方安装页选择安装方式。
curl -fsSL https://get.pnpm.io/install.sh | sh

# 验证安装
pnpm --version
```

#### 配置npm镜像（中国大陆用户）
```bash
# 设置npm镜像以加快下载速度
npm config set registry https://registry.npmmirror.com

# 设置pnpm镜像
pnpm config set registry https://registry.npmmirror.com

# 验证镜像设置
npm config get registry
pnpm config get registry
```

#### 替代方案：Yarn（如果偏好）
```bash
# 全局安装Yarn
npm install -g yarn

# 验证安装
yarn --version
```

### 3. 安装代码编辑器

#### VS Code安装
```bash
# macOS
brew install --cask visual-studio-code

# Windows (Winget)
winget install Microsoft.VisualStudioCode

# Linux (Ubuntu)
sudo snap install --classic code
```

#### 必需的VS Code扩展
```bash
# 安装推荐的扩展
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension ms-vscode.vscode-json
code --install-extension ms-vscode.vscode-react-hooks
```

### 4. 创建Next.js项目

#### 使用create-next-app
```bash
# 创建新的 Next.js 项目。首次运行会交互询问选项；也可以按下一行显式传参。
npx create-next-app@latest my-nextjs-app --typescript --tailwind --app --src-dir --import-alias "@/*"

# 或者使用pnpm
pnpm create next-app my-nextjs-app --typescript --tailwind --app --src-dir --import-alias "@/*"

# 进入项目目录
cd my-nextjs-app

# 立即记录脚手架实际写入的版本；后续学习与排错都以它们和锁文件为准。
npm ls next react react-dom typescript
git init
git add package.json package-lock.json
git commit -m "chore: scaffold next app"
```

`create-next-app@latest` 适合开始一次新脚手架尝试，但它的模板和依赖会随日期改变。要复现本章练习，保存首次生成的 `package.json` 与 lock 文件；团队项目应在约定的脚手架版本和 Node 版本下生成，再由升级任务显式变更。不要把命令里的 `latest` 误解成项目会持续自动升级。

#### 项目选项说明
- `--typescript`: 使用TypeScript确保类型安全
- `--tailwind`: 集成Tailwind CSS进行样式
- `--app`: 使用App Router（Next.js 13+推荐）
- `--src-dir`: 使用src目录结构
- `--import-alias "@/*"`: 设置路径别名以实现更清晰的导入

### 5. 配置开发环境

#### 安装项目依赖
```bash
# 使用npm
npm install

# 使用pnpm
pnpm install

# 使用yarn
yarn install
```

#### 启动开发服务器
```bash
# 使用npm
npm run dev

# 使用pnpm
pnpm dev

# 使用yarn
yarn dev
```

访问 http://localhost:3000 查看应用程序。

## ⚙️ 环境配置文件

### 1. package.json：先理解脚本，不要手抄依赖版本

`create-next-app` 已经生成和它的模板相匹配的依赖、ESLint 配置与 lock 文件。下面只展示一个项目至少应理解的脚本形状；不要把这段片段覆盖到脚手架生成的 `package.json`，也不要混用来自不同教程的 Next、React、ESLint 版本。

```json
{
  "name": "my-nextjs-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "type-check": "tsc --noEmit",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

Next 16 的 `next build` 不再自动运行 lint，所以把 `npm run lint` 作为独立门槛。`npm run type-check` 也可先于构建执行，便于把类型问题与打包问题分开定位。官方的 [安装说明](https://nextjs.org/docs/app/getting-started/installation) 给出当前脚手架选项和最低 Node 要求。

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
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/styles/*": ["./src/styles/*"]
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
  // 只在项目确实需要 next/image 远程来源限制时保留此项。
  images: {
    // Next.js 16：使用 remotePatterns 描述允许的远程图片来源。
    remotePatterns: [{ protocol: 'https', hostname: 'example.com' }],
  },
}

module.exports = nextConfig
```

### 4. .env.local
```bash
# 应用程序配置
NEXT_PUBLIC_APP_NAME="我的Next.js应用"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# API配置
NEXT_PUBLIC_API_URL="http://localhost:3001/api"
DATABASE_URL="postgresql://用户名:密码@localhost:5432/数据库"

# 认证配置
NEXTAUTH_SECRET="您的nextauth密钥"
NEXTAUTH_URL="http://localhost:3000"

# 功能标志
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=true
```

## 🛠️ 开发工具配置

### 1. ESLint配置

Next 16 已移除 `next lint` 和 `next.config.*` 的 `eslint` 选项。新项目优先保留脚手架生成的 `eslint.config.mjs`；若从零创建一个平坦配置，可以使用：

```javascript
// eslint.config.mjs
import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTypeScript from 'eslint-config-next/typescript'

export default [...nextVitals, ...nextTypeScript]
```

再运行 `npm run lint`。项目已有 ESLint 配置时，不要直接覆盖它；应先合并规则并运行 lint，确认没有把现有忽略文件或自定义规则删掉。配置迁移细节见 [Next.js ESLint 文档](https://nextjs.org/docs/app/api-reference/config/eslint)。

### 2. Prettier配置
创建`.prettierrc`:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

创建`.prettierignore`:
```
.next/
out/
dist/
build/
node_modules/
*.min.js
*.min.css
```

### 3. Git配置
创建`.gitignore`:
```gitignore
# 依赖
node_modules/
.pnp
.pnp.js

# 测试
coverage/

# Next.js
.next/
out/

# 生产
build/

# 杂项
.DS_Store
*.pem

# 调试
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 本地环境文件
.env*.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts

# IDE
.vscode/
.idea/

# 操作系统
Thumbs.db
```

### 4. VS Code工作区配置
创建`.vscode/settings.json`:
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
  },
  "typescript.preferences.includePackageJsonAutoImports": "on"
}
```

创建`.vscode/extensions.json`:
```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-json",
    "ms-vscode.vscode-react-hooks",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

创建`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev"
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
```

创建`.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "启动Next.js开发服务器",
      "type": "shell",
      "command": "npm run dev",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      }
    },
    {
      "label": "运行类型检查",
      "type": "shell",
      "command": "npm run type-check",
      "group": "test"
    },
    {
      "label": "格式化代码",
      "type": "shell",
      "command": "npm run format",
      "group": "build"
    }
  ]
}
```

## 🔄 开发工作流程

### 1. 日常开发命令
```bash
# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 格式化代码
npm run format

# 构建生产版本
npm run build

# 启动生产服务器
npm run start
```

### 2. Git工作流程
```bash
# 初始化仓库
git init

# 添加文件
git add .

# 初始提交
git commit -m "初始提交：Next.js 16项目设置"

# 创建功能分支
git checkout -b feature/new-feature

# 添加更改并提交
git add .
git commit -m "功能：添加新功能"

# 推送到远程仓库
git push origin feature/new-feature

# 合并到主分支
git checkout main
git merge feature/new-feature
```

### 3. 项目结构
```
my-nextjs-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   └── features/
│   ├── lib/
│   │   ├── utils.ts
│   │   └── types.ts
│   └── styles/
├── public/
├── .next/
├── .gitignore
├── eslint.config.mjs
├── .prettierrc
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

## 🔧 高级配置

### 1. package.json中的自定义脚本
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "lint:fix": "eslint --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "analyze": "ANALYZE=true next build",
    "postinstall": "prisma generate"
  }
}
```

### 2. 环境特定配置
```javascript
// next.config.js
const isProduction = process.env.NODE_ENV === 'production'

const nextConfig = {
  // Next 16 默认使用 Turbopack。只有项目必须依赖 webpack 插件或回调时，
  // 才配置 webpack，并把对应脚本明确写成 next dev --webpack / next build --webpack。
  ...(isProduction && {
    compiler: {
      removeConsole: true,
    },
  }),
}

module.exports = nextConfig
```

## 🐛 常见问题解决

### 1. Node.js版本问题
```bash
# 检查当前Node.js版本
node --version

# 使用 nvm 管理版本；这里应使用项目要求的主版本。
nvm list
nvm use 24

# 清除npm缓存
npm cache clean --force
```

### 2. 权限问题
```bash
# 修复npm权限（macOS/Linux）
sudo chown -R $(whoami) ~/.npm

# 修复全局npm目录权限
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 3. 端口冲突
```bash
# 查找使用端口3000的进程
lsof -i :3000

# 确认是自己的开发服务后，填入 lsof 输出中的进程号再发送终止信号
TARGET_PID=""
kill -TERM "${TARGET_PID:?请先填写开发服务的PID}"

# 或者使用不同端口
npm run dev -- -p 3001
```

### 4. 内存问题
```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"

# 或者在package.json脚本中
"dev": "NODE_OPTIONS='--max-old-space-size=4096' next dev"
```

### 5. 依赖问题
```bash
# 清除node_modules并重新安装
rm -rf node_modules package-lock.json
npm install

# 清除pnpm缓存
pnpm store prune
pnpm install

# 强制清理安装
npm ci
```

## 📊 开发最佳实践

环境搭好后应能从干净目录安装、检查、构建并运行一个最小页面。src 目录和按功能分组有助定位代码，但不自动保证可维护；先把页面入口、复用组件与服务端代码边界说明白。

版本控制保存可解释的改动与依赖锁文件，升级按兼容性和维护需求进行。TypeScript 严格模式检查类型，lint 检查已配置规则，格式化统一文本，它们不等于性能优化或运行时验证。构建速度与首屏性能分别测量，不把换构建器当作全部问题的解法。

## 🎯 快速入门检查清单

- [ ] 安装项目所需的 Node 版本（本仓基线为 Node 24）
- [ ] 安装pnpm包管理器
- [ ] 安装VS Code及扩展
- [ ] 创建Next.js 16项目
- [ ] 配置开发环境
- [ ] 设置Git仓库
- [ ] 验证所有配置正常工作
- [ ] 运行开发服务器
- [ ] 创建第一个组件
- [ ] 提交初始代码

## 🔄 下一步

完成环境搭建后，您可以继续学习：

1. **TypeScript基础** - 掌握TypeScript核心概念
2. **React基础** - 学习React组件开发
3. **Next.js路由** - 理解App Router系统
4. **样式解决方案** - 掌握Tailwind CSS和现代样式
5. **数据获取** - 学习服务端渲染和API路由
6. **部署** - 将应用程序部署到生产环境

## 🔗 交叉引用

| 相关主题 | 参考 |
|---------|------|
| **TypeScript基础** | [03-typescript-integration.md](./03-typescript-integration.md) |
| **React基础** | [02-first-nextjs-app.md](./02-first-nextjs-app.md) |
| **Next.js路由** | [04-layouts-routing.md](./04-layouts-routing.md) |
| **样式解决方案** | [05-styling-with-tailwind.md](./05-styling-with-tailwind.md) |

## 📚 附加资源

### 文档
- [Next.js官方文档](https://nextjs.org/docs)
- [Node.js文档](https://nodejs.org/docs/)
- [TypeScript手册](https://www.typescriptlang.org/docs/)
- [VS Code文档](https://code.visualstudio.com/docs)

### 工具和扩展
- [VS Code扩展市场](https://marketplace.visualstudio.com/)
- [Node版本管理器(nvm)](https://github.com/nvm-sh/nvm)
- [pnpm文档](https://pnpm.io/)
- [Tailwind CSS](https://tailwindcss.com/)

### 社区资源
- [Next.js GitHub](https://github.com/vercel/next.js)
- [React社区](https://react.dev/community)
- [TypeScript社区](https://www.typescriptlang.org/community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/next.js)

## 🔄 文档交叉引用

### 相关文档
- 📄 **[后一个basics文档](./02-first-nextjs-app.md)**: 学习创建第一个Next.js应用，实践环境搭建成果
- 📄 **[相关的reference文档](../reference/development-tools/03-package-managers.md)**: 深入了解包管理器的使用和配置
- 📄 **[相关的reference文档](../reference/language-concepts/04-javascript-modern.md)**: 快速参考现代JavaScript语法特性

### 参考章节
- 📖 **[本模块其他章节]**: [创建第一个Next.js应用](./02-first-nextjs-app.md#️-项目创建流程) | [TypeScript集成](./03-typescript-integration.md#️-typescript项目配置)
- 📖 **[Knowledge Points快速参考]**: [开发工具配置](../reference/development-tools/04-debugging-tools.md) | [JavaScript现代语法](../reference/language-concepts/04-javascript-modern.md)

## 📝 总结

### 核心要点回顾
1. **Node.js环境**: 掌握Node.js的安装方法和版本管理，理解为什么需要20.9+版本
2. **包管理器选择**: 学会使用npm、pnpm等包管理器，了解镜像配置和依赖管理
3. **IDE配置**: 掌握VS Code的安装和必需扩展配置，提升开发效率
4. **项目创建**: 使用create-next-app快速创建Next.js项目，理解各种配置选项
5. **开发工具**: 配置ESLint、Prettier等代码质量工具，建立标准化开发流程

### 学习成果检查
- [ ] 是否成功安装项目所需 Node 版本并能验证版本？
- [ ] 是否掌握至少一种包管理器的基本使用方法？
- [ ] 是否能够成功创建Next.js 16项目并启动开发服务器？
- [ ] 是否理解项目结构中各个配置文件的作用？
- [ ] 是否能够配置基本的开发工具和代码规范？

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

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
