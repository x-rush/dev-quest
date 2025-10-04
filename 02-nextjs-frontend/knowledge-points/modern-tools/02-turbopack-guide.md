# Turbopack 使用指南

## 📚 概述

Turbopack 是 Next.js 团队用 Rust 构建的下一代打包工具，旨在提供极快的开发和构建体验。本指南涵盖了 Turbopack 的配置、优化和与 Next.js 的深度集成。

## 🚀 Turbopack 简介

### 核心特性
**了解 Turbopack 的优势**

```typescript
// Turbopack 的核心优势
interface TurbopackFeatures {
  // 基于 Rust 的高性能
  performance: {
    startupTime: '10x faster than Webpack';
    incrementalBuilds: '100x faster updates';
    memoryUsage: '70% less memory';
  };

  // 智能依赖图
  dependencyGraph: {
    granular: 'Single file granularity';
    parallel: 'Parallel processing';
    incremental: 'Incremental recomputation';
  };

  // 开发体验
  developmentExperience: {
    fastRefresh: 'Lightning fast HMR';
    errorOverlay: 'Enhanced error reporting';
    sourceMaps: 'High quality source maps';
  };
}

// 与其他工具对比
const buildToolsComparison = {
  webpack: {
    language: 'JavaScript',
    ecosystem: 'Mature',
    performance: 'Baseline',
  },
  vite: {
    language: 'Go/Rust',
    ecosystem: 'Growing',
    performance: 'Fast (dev), Moderate (build)',
  },
  turbopack: {
    language: 'Rust',
    ecosystem: 'Next.js integrated',
    performance: 'Fast (dev & build)',
  },
};
```

### 启用 Turbopack
**在 Next.js 项目中启用 Turbopack**

```json
// package.json
{
  "scripts": {
    "dev": "next dev --turbo",
    "build": "next build --turbo",
    "start": "next start",
    "lint": "next lint"
  },
  "devDependencies": {
    "next": "^15.0.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0"
  }
}
```

```bash
# 启动 Turbopack 开发服务器
npm run dev

# 使用 Turbopack 构建
npm run build

# 检查 Turbopack 版本
npx next --version
```

## ⚙️ 配置选项

### next.config.js 配置
**Turbopack 特定配置**

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // 启用 Turbopack
  experimental: {
    turbo: {
      // Turbopack 配置选项
      rules: {
        // 自定义加载器规则
        '*.svg': [
          {
            loader: '@svgr/webpack',
            options: {
              icon: true,
              svgo: true,
            },
          },
        ],
      },

      // 包解析配置
      resolveAlias: {
        // 路径别名
        '@': './src',
        '@components': './src/components',
        '@lib': './src/lib',
        '@styles': './src/styles',
      },

      // 环境变量处理
      env: {
        CUSTOM_KEY: 'custom-value',
      },

      // 包的优化
      packagers: {
        // 自定义包处理
        'react-dom': {
          // 特定配置
        },
      },
    },

    // 启用实验性功能
    appDir: true,
    serverComponentsExternalPackages: ['@prisma/client'],
  },

  // 常规配置
  webpack: (config, { dev, isServer }) => {
    // 注意：Turbopack 会忽略大部分 webpack 配置
    // 但可以保留一些必要的配置

    if (!dev && !isServer) {
      // 生产环境特定配置
    }

    return config;
  },
};

module.exports = nextConfig;
```

### turbo.json 配置
**Turborepo 配置文件**

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [
    "**/.env.*local",
    "next.config.js",
    "tailwind.config.js",
    "tsconfig.json",
    "yarn.lock"
  ],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "outputs": []
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "cache": false
    }
  }
}
```

## 🎯 性能优化

### 依赖优化
**优化依赖解析和缓存**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 排除某些包的 Turbopack 处理
      exclude: [
        '@storybook/*',
        'jest',
        '@testing-library/*',
      ],

      // 包的特定配置
      loaders: {
        // 自定义加载器
        '.md': [
          {
            loader: '@mdx-js/loader',
            options: {
              development: process.env.NODE_ENV === 'development',
              providerImportSource: '@mdx-js/react',
            },
          },
        ],
      },

      // 解析配置
      resolveExtensions: [
        '.tsx',
        '.ts',
        '.jsx',
        '.js',
        '.mjs',
        '.json',
      ],

      // 外部依赖
      externals: {
        'some-native-module': 'commonjs some-native-module',
      },
    },
  },
};
```

### 缓存策略
**优化构建缓存**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 缓存配置
      cache: {
        // 启用持久化缓存
        enable: true,

        // 缓存目录
        cacheDir: '.turbo',

        // 缓存策略
        strategy: 'default',
      },

      // 开发服务器配置
      dev: {
        // 启用增量开发
        incremental: true,

        // 热更新配置
        hmr: {
          // 启用 HMR
          enabled: true,

          // HMR 端口
          port: 24678,
        },
      },
    },
  },
};
```

### 构建优化
**生产环境构建优化**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 构建优化
      build: {
        // 启用代码压缩
        compress: true,

        // 启用 Tree Shaking
        treeShaking: true,

        // 输出配置
        output: {
          // 输出目录
          dir: '.next',

          // 文件名策略
          filename: '[name].[contenthash].[ext]',
        },
      },
    },
  },

  // 生产环境优化
  productionBrowserSourceMaps: false,
  compress: true,

  // 输出配置
  output: 'standalone',

  // 图片优化
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};
```

## 🔧 开发体验

### 热更新配置
**优化开发环境的热更新体验**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      dev: {
        // HMR 配置
        hmr: {
          // HMR Websocket 端口
          port: 24678,

          // HMR 客户端配置
          client: {
            // 重连配置
            reconnect: 10,

            // 覆盖配置
            overlay: true,
          },
        },

        // 开发服务器配置
        server: {
          // 端口配置
          port: 3000,

          // 主机配置
          host: 'localhost',

          // CORS 配置
          cors: {
            origin: true,
            credentials: true,
          },
        },
      },
    },
  },
};
```

### 错误处理
**增强的错误报告和调试**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 错误处理配置
      errorHandling: {
        // 显示详细错误信息
        verbose: process.env.NODE_ENV === 'development',

        // 错误覆盖层
        overlay: {
          // 启用错误覆盖层
          enabled: true,

          // 自定义错误处理
          handler: (error) => {
            console.error('Turbopack Error:', error);
            return {
              message: error.message,
              stack: error.stack,
            };
          },
        },
      },

      // 调试配置
      debug: {
        // 启用调试模式
        enabled: process.env.NODE_ENV === 'development',

        // 日志级别
        logLevel: 'info',

        // 性能分析
        profiling: true,
      },
    },
  },
};
```

## 📊 监控和分析

### 性能监控
**监控 Turbopack 性能**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 性能监控
      performance: {
        // 启用性能分析
        profiling: true,

        // 性能指标收集
        metrics: {
          // 构建时间
          buildTime: true,

          // 内存使用
          memoryUsage: true,

          // 包大小分析
          bundleAnalysis: true,
        },
      },

      // 分析器配置
      analyzer: {
        // 启用包分析器
        enabled: true,

        // 分析器端口
        port: 3001,

        // 分析器配置
        options: {
          // 分析模式
          mode: 'server',

          // 输出格式
          format: 'json',
        },
      },
    },
  },
};
```

### 构建分析
**分析构建结果和性能**

```bash
# 启动带分析的构建
npm run build --turbo --analyze

# 查看构建统计
npx next build --turbo --stats

# 生成构建报告
npx next build --turbo --report=json

# 分析包大小
npx @next/bundle-analyzer .next
```

```javascript
// scripts/analyze-build.js
const { analyzeBundle } = require('@next/bundle-analyzer');

async function analyzeBuild() {
  try {
    const result = await analyzeBundle({
      outputPath: '.next',
      mode: 'server',
    });

    console.log('Bundle Analysis:', result);
  } catch (error) {
    console.error('Analysis failed:', error);
  }
}

analyzeBuild();
```

## 🔄 与工具链集成

### TypeScript 集成
**优化 TypeScript 编译**

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
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
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@lib/*": ["./src/lib/*"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": [
    "node_modules"
  ]
}
```

### ESLint 集成
**代码质量检查**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // ESLint 集成
      eslint: {
        // 启用 ESLint
        enabled: true,

        // ESLint 配置
        config: {
          extends: [
            'next/core-web-vitals',
            '@typescript-eslint/recommended',
          ],
          rules: {
            '@typescript-eslint/no-unused-vars': 'error',
            '@typescript-eslint/no-explicit-any': 'warn',
          },
        },
      },
    },
  },
};
```

### Tailwind CSS 集成
**样式框架集成**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // CSS 处理
      css: {
        // Tailwind CSS 配置
        tailwindcss: {
          // 启用 Tailwind
          enabled: true,

          // 配置文件路径
          config: './tailwind.config.js',

          // CSS 提取
          extract: true,
        },

        // PostCSS 配置
        postcss: {
          // 插件配置
          plugins: [
            'tailwindcss',
            'autoprefixer',
            ...(process.env.NODE_ENV === 'production'
              ? ['cssnano']
              : []),
          ],
        },
      },
    },
  },
};
```

## 🛠️ 高级配置

### 自定义加载器
**创建自定义 Turbopack 加载器**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 自定义规则
      rules: {
        // MDX 处理
        '*.mdx': [
          {
            loader: '@mdx-js/loader',
            options: {
              development: process.env.NODE_ENV === 'development',
              providerImportSource: '@mdx-js/react',
            },
          },
        ],

        // GraphQL 处理
        '*.graphql': [
          {
            loader: 'graphql-tag/loader',
          },
        ],

        // YAML 处理
        '*.yaml': [
          {
            loader: 'yaml-loader',
          },
        ],

        // 自定义图像处理
        '*.webp': [
          {
            loader: 'next-image-loader',
            options: {
              format: 'webp',
              quality: 80,
            },
          },
        ],
      },

      // 加载器解析
      resolveLoader: {
        // 自定义加载器路径
        loaderDirectories: ['./loaders'],
      },
    },
  },
};
```

### 多环境配置
**针对不同环境的配置**

```javascript
// next.config.js
const isDev = process.env.NODE_ENV === 'development';
const isProd = process.env.NODE_ENV === 'production';
const isTest = process.env.NODE_ENV === 'test';

const nextConfig = {
  experimental: {
    turbo: {
      // 开发环境配置
      ...(isDev && {
        dev: {
          incremental: true,
          hmr: {
            enabled: true,
            port: 24678,
          },
        },
      }),

      // 生产环境配置
      ...(isProd && {
        build: {
          compress: true,
          treeShaking: true,
          minify: true,
        },
      }),

      // 测试环境配置
      ...(isTest && {
        test: {
          enableTesting: true,
          testFramework: 'jest',
        },
      }),
    },
  },
};
```

### 插件系统
**扩展 Turbopack 功能**

```javascript
// next.config.js
const nextConfig = {
  experimental: {
    turbo: {
      // 插件配置
      plugins: [
        // 自定义插件
        require('./plugins/my-plugin.js'),

        // 第三方插件
        require('@next/plugin-turbo-analytics'),
      ],

      // 插件选项
      pluginOptions: {
        'my-plugin': {
          enabled: true,
          options: {
            // 插件特定选项
          },
        },
      },
    },
  },
};
```

## 📋 最佳实践

### 性能优化建议
- [ ] 启用增量开发和构建
- [ ] 配置合适的缓存策略
- [ ] 优化依赖解析
- [ ] 使用路径别名简化导入
- [ ] 配置 Tree Shaking
- [ ] 启用代码压缩

### 开发体验优化
- [ ] 配置热更新 (HMR)
- [ ] 启用错误覆盖层
- [ ] 配置 TypeScript 严格模式
- [ ] 集成代码检查工具
- [ ] 设置调试选项
- [ ] 优化构建日志

### 构建优化
- [ ] 启用生产模式优化
- [ ] 配置代码分割
- [ ] 优化静态资源处理
- [ ] 启用压缩和混淆
- [ ] 配置 CDN
- [ ] 监控构建性能

## 📖 总结

Turbopack 作为 Next.js 的下一代打包工具提供了：

### 核心优势：
1. **极致性能**: 基于 Rust 的高性能实现
2. **智能缓存**: 增量构建和持久化缓存
3. **优秀体验**: 快速的热更新和错误报告
4. **深度集成**: 与 Next.js 生态无缝集成

### 配置要点：
1. **合理启用**: 在适当场景下启用 Turbopack
2. **性能监控**: 监控构建性能和资源使用
3. **缓存策略**: 配置合适的缓存策略
4. **错误处理**: 优化错误报告和调试体验
5. **工具集成**: 与现有工具链良好集成

### 使用建议：
- 在开发环境中充分利用 Turbopack 的速度优势
- 在生产环境中测试和验证构建结果
- 监控性能指标，及时优化配置
- 与团队成员分享配置经验

Turbopack 代表了前端构建工具的未来方向，通过合理配置可以显著提升 Next.js 项目的开发和构建效率。