# Vite 配置速查手册

## 📚 概述

Vite 是一个现代化的前端构建工具，利用 ES 模块和 esbuild 提供极快的开发体验。本指南涵盖了 Vite 在 Next.js 项目中的配置、优化和最佳实践。

## 🚀 基础配置

### 创建 Vite 项目
**初始化 Vite + React + TypeScript 项目**

```bash
# 使用 npm
npm create vite@latest my-vite-app -- --template react-ts

# 使用 yarn
yarn create vite my-vite-app --template react-ts

# 使用 pnpm
pnpm create vite my-vite-app --template react-ts

# 进入项目目录
cd my-vite-app

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 基础 vite.config.ts
**核心配置文件**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // 开发服务器配置
  server: {
    port: 3000,
    host: true, // 监听所有地址
    cors: true,
    open: true, // 自动打开浏览器

    // 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/socket.io': {
        target: 'http://localhost:8080',
        ws: true,
      },
    },
  },

  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'esbuild',
    target: 'es2015',

    // 代码分割配置
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash', 'date-fns'],
        },
      },
    },

    // 压缩配置
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },

  // 路径别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@styles': resolve(__dirname, 'src/styles'),
    },
  },

  // CSS 配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
    modules: {
      localsConvention: 'camelCase',
    },
  },

  // 环境变量
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
});
```

### 环境变量配置
**.env 文件设置**

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080
VITE_APP_TITLE=My App - Development
VITE_DEBUG_MODE=true

# .env.production
VITE_API_BASE_URL=https://api.myapp.com
VITE_APP_TITLE=My App
VITE_DEBUG_MODE=false

# .env.local (本地配置，不提交到版本控制)
VITE_SECRET_KEY=your-secret-key-here
```

```typescript
// src/config/env.ts
interface EnvConfig {
  apiUrl: string;
  appTitle: string;
  debugMode: boolean;
  secretKey: string;
}

export const env: EnvConfig = {
  apiUrl: import.meta.env.VITE_API_BASE_URL,
  appTitle: import.meta.env.VITE_APP_TITLE,
  debugMode: import.meta.env.VITE_DEBUG_MODE === 'true',
  secretKey: import.meta.env.VITE_SECRET_KEY || '',
};

// 类型安全的环境变量
export const getEnvVar = (key: string, fallback?: string): string => {
  const value = import.meta.env[key];
  if (value === undefined) {
    if (fallback !== undefined) {
      return fallback;
    }
    throw new Error(`Environment variable ${key} is not defined`);
  }
  return value;
};
```

## 🔧 插件配置

### React 插件
**增强 React 开发体验**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import reactSwc from '@vitejs/plugin-react-swc';

export default defineConfig({
  plugins: [
    // 使用 SWC 编译（更快）
    reactSwc(),

    // 或者使用 Babel
    react({
      // Fast Refresh 配置
      fastRefresh: true,

      // JSX 运行时
      jsxRuntime: 'automatic',

      // 插件配置
      babel: {
        plugins: [
          ['@babel/plugin-proposal-decorators', { legacy: true }],
          ['@babel/plugin-proposal-class-properties', { loose: true }],
        ],
      },
    }),
  ],
});
```

### UI 库插件
**集成主流 UI 框架**

```typescript
// Ant Design
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import AntdDayjs from 'antd-dayjs-webpack-plugin';

export default defineConfig({
  plugins: [
    react(),
    // Ant Design 按需加载
    AntdDayjs(),
  ],
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
        modifyVars: {
          '@primary-color': '#1890ff',
          '@border-radius-base': '4px',
        },
      },
    },
  },
});

// Tailwind CSS
export default defineConfig({
  css: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
});

// Material-UI
export default defineConfig({
  define: {
    'process.env': {},
  },
});
```

### 代码质量插件
**集成代码检查和格式化**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import eslint from 'vite-plugin-eslint';
import stylelint from 'vite-plugin-stylelint';

export default defineConfig({
  plugins: [
    // ESLint 集成
    eslint({
      cache: false,
      include: ['./src/**/*.ts', './src/**/*.tsx'],
      exclude: [],
    }),

    // Stylelint 集成
    stylelint({
      include: ['./src/**/*.{css,scss,less}'],
      exclude: [],
    }),
  ],
});
```

## 🎯 构建优化

### 代码分割
**优化包大小和加载性能**

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        // 手动代码分割
        manualChunks: (id) => {
          // React 相关
          if (id.includes('react') || id.includes('react-dom')) {
            return 'react-vendor';
          }

          // 路由相关
          if (id.includes('react-router')) {
            return 'router';
          }

          // UI 库
          if (id.includes('antd') || id.includes('@mui')) {
            return 'ui-vendor';
          }

          // 工具库
          if (id.includes('lodash') || id.includes('date-fns')) {
            return 'utils';
          }

          // 图表库
          if (id.includes('echarts') || id.includes('d3')) {
            return 'charts';
          }
        },

        // 资源文件命名
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name.split('.').pop();
          if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)$/.test(assetInfo.name)) {
            return 'media/[name]-[hash].[ext]';
          }
          if (/\.(png|jpe?g|gif|svg|webp)$/.test(assetInfo.name)) {
            return 'images/[name]-[hash].[ext]';
          }
          if (/\.(woff2?|eot|ttf|otf)$/.test(assetInfo.name)) {
            return 'fonts/[name]-[hash].[ext]';
          }
          return `${extType}/[name]-[hash].[ext]`;
        },
      },
    },

    // 压缩配置
    minify: 'esbuild',
    cssMinify: true,

    // 构建目标
    target: ['es2015', 'chrome58', 'firefox57', 'safari11'],

    // 启用 CSS 代码分割
    cssCodeSplit: true,
  },
});
```

### 预构建优化
**优化依赖预构建**

```typescript
// vite.config.ts
export default defineConfig({
  optimizeDeps: {
    // 预构建包含的依赖
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'antd',
      'lodash-es',
      'axios',
    ],

    // 排除预构建的依赖
    exclude: [
      'some-esm-package',
    ],

    // 强制重新构建
    force: true,

    // 预构建选项
    esbuildOptions: {
      target: 'es2015',
      define: {
        global: 'globalThis',
      },
    },
  },
});
```

### 资源优化
**静态资源处理优化**

```typescript
// vite.config.ts
export default defineConfig({
  // 静态资源处理
  assetsInclude: ['**/*.gltf'],

  // 资源内联阈值
  build: {
    assetsInlineLimit: 4096, // 4kb 以下内联为 base64
  },

  // 自定义资源转换
  plugins: [
    {
      name: 'vite-plugin-svg',
      transform(code, id) {
        if (id.endsWith('.svg')) {
          return `export default \`${code}\`;`;
        }
      },
    },
  ],
});
```

## 🔄 开发工具集成

### TypeScript 配置
**完整的 TypeScript 集成**

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES6"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": false,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@hooks/*": ["src/hooks/*"],
      "@utils/*": ["src/utils/*"],
      "@assets/*": ["src/assets/*"],
      "@styles/*": ["src/styles/*"]
    },
    "types": ["vite/client", "node"]
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "vite.config.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
```

### 测试集成
**集成 Vitest 测试框架**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  // 测试配置
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,

    // 覆盖率配置
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
      ],
    },

    // 模拟文件
    include: [
      'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
  },
});

// src/test/setup.ts
import '@testing-library/jest-dom';
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
```

### Storybook 集成
**组件开发和测试**

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  docs: {
    autodocs: 'tag',
  },
  viteFinal: async (config) => {
    // 自定义 Vite 配置
    return {
      ...config,
      define: {
        ...config.define,
        global: 'window',
      },
    };
  },
};

export default config;
```

## 🎨 样式配置

### CSS 预处理器
**配置 Sass/SCSS、Less、Stylus**

```typescript
// vite.config.ts
export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        // 全局变量和混入
        additionalData: `
          @import "@/styles/variables.scss";
          @import "@/styles/mixins.scss";
        `,

        // 注入全局变量
        additionalData: (content, filename) => {
          if (filename.includes('node_modules')) {
            return content;
          }
          return `
            @import "@/styles/variables.scss";
            ${content}
          `;
        },

        // 路径别名
        importer: [
          // 自定义导入器
          (url) => {
            if (url.startsWith('~')) {
              return {
                file: resolve(__dirname, 'node_modules', url.slice(1)),
              };
            }
          },
        ],
      },

      less: {
        javascriptEnabled: true,
        modifyVars: {
          '@primary-color': '#1890ff',
          '@border-radius-base': '4px',
        },
      },

      stylus: {
        imports: [
          resolve(__dirname, 'src/styles/variables.styl'),
        ],
      },
    },

    // CSS 模块配置
    modules: {
      localsConvention: 'camelCase',
      generateScopedName: '[name]_[local]_[hash:base64:5]',
    },
  },
});
```

### PostCSS 配置
**CSS 后处理配置**

```javascript
// postcss.config.js
module.exports = {
  plugins: [
    // Tailwind CSS
    require('tailwindcss'),

    // Autoprefixer
    require('autoprefixer'),

    // CSS Nano（生产环境）
    ...(process.env.NODE_ENV === 'production'
      ? [require('cssnano')]
      : []),

    // 其他插件
    require('@fullhuman/postcss-purgecss')({
      content: ['./src/**/*.{js,jsx,ts,tsx}'],
      defaultExtractor: (content) => {
        const broadMatches = content.match(/[^<>"'`\s]*[^<>"'`\s:]/g) || [];
        const innerMatches = content.match(/[^<>"'`\s.()]*[^<>"'`\s.():]/g) || [];
        return broadMatches.concat(innerMatches);
      },
    }),
  ],
};
```

## 📊 性能监控

### 构建分析
**分析构建结果**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    // 构建分析
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
});

// package.json scripts
{
  "scripts": {
    "build": "vite build",
    "build:analyze": "vite build && npx vite-bundle-analyzer dist/stats.html",
    "preview": "vite preview"
  }
}
```

### 性能监控插件
**运行时性能监控**

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [
    // 性能监控
    {
      name: 'performance-monitor',
      configureServer(server) {
        server.ws.on('performance:report', (data) => {
          console.log('Performance data:', data);
        });
      },
    },
  ],
});
```

## 🔄 多环境配置

### 环境特定配置
**根据环境动态配置**

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],

    // 根据环境配置
    server: {
      port: env.VITE_PORT ? parseInt(env.VITE_PORT) : 3000,
      proxy: mode === 'development' ? {
        '/api': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
      } : undefined,
    },

    build: {
      outDir: mode === 'development' ? 'dev-dist' : 'dist',
      sourcemap: mode === 'development',
      minify: mode === 'production' ? 'esbuild' : false,
    },

    define: {
      __APP_ENV__: JSON.stringify(env),
    },
  };
});
```

### 条件配置
**基于条件的动态配置**

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig(({ command, mode }) => {
  const isProduction = mode === 'production';
  const isBuild = command === 'build';

  return {
    plugins: [
      react(),
      // 只在生产环境使用
      ...(isProduction ? [
        // 生产环境特定插件
      ] : []),
    ],

    build: {
      sourcemap: !isProduction,
      minify: isProduction ? 'esbuild' : false,

      // 只在构建时配置
      ...(isBuild ? {
        rollupOptions: {
          // 构建特定配置
        },
      } : {}),
    },

    server: {
      // 只在开发环境配置
      ...(isBuild ? {} : {
        proxy: {
          '/api': 'http://localhost:8080',
        },
      }),
    },
  };
});
```

## 📋 最佳实践

### 性能优化清单
- [ ] 启用代码分割和懒加载
- [ ] 配置合适的缓存策略
- [ ] 优化图片和静态资源
- [ ] 使用预构建优化依赖
- [ ] 配置压缩和混淆
- [ ] 启用 Gzip/Brotli 压缩

### 开发体验优化
- [ ] 配置热更新
- [ ] 设置代理解决跨域
- [ ] 配置路径别名
- [ ] 集成代码检查工具
- [ ] 配置自动格式化
- [ ] 启用 TypeScript 严格模式

### 部署配置
- [ ] 配置多环境构建
- [ ] 设置正确的 publicPath
- [ ] 配置静态资源处理
- [ ] 启用生产环境优化
- [ ] 配置错误监控
- [ ] 设置性能监控

## 📖 总结

Vite 提供了现代化、快速的开发体验：

### 核心特性：
1. **快速启动**: 利用 ES 模块无需打包
2. **热更新**: 基于模块的精确更新
3. **优化构建**: 使用 Rollup 和 esbuild
4. **插件生态**: 丰富的插件系统
5. **TypeScript 支持**: 开箱即用的 TS 支持

### 配置要点：
1. **合理配置路径别名**: 简化导入路径
2. **优化代码分割**: 提升加载性能
3. **配置代理**: 解决开发环境跨域
4. **环境变量管理**: 支持多环境部署
5. **性能监控**: 分析和优化构建结果

通过合理配置 Vite，可以显著提升 Next.js 项目的开发体验和构建性能。虽然 Next.js 有自己的构建系统，但 Vite 在组件库、工具应用等场景下是优秀的选择。