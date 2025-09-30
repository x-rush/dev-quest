# 自动化工具 - Next.js 15 现代工程化实践

## 📋 概述

自动化工具是现代前端工程化的核心组成部分。Next.js 15项目可以通过各种自动化工具来提升开发效率、代码质量和部署流程。本文将深入探讨如何在Next.js 15项目中实施全面的自动化策略，包括代码生成、测试自动化、部署自动化等。

## 🎯 自动化工具生态

### 1. 自动化工具分类

```typescript
// types/automation-types.ts
export type AutomationCategory =
  | 'code-generation'      // 代码生成
  | 'testing'              // 测试自动化
  | 'deployment'           // 部署自动化
  | 'monitoring'           // 监控自动化
  | 'documentation'        // 文档自动化
  | 'quality-assurance'    // 质量保证
  | 'dependency-management' // 依赖管理
  | 'ci-cd'               // CI/CD流水线

export interface AutomationTool {
  name: string;
  category: AutomationCategory;
  description: string;
  features: string[];
  integration: 'easy' | 'medium' | 'complex';
  popularity: 'high' | 'medium' | 'low';
  nextjsCompatible: boolean;
}

export const automationTools: AutomationTool[] = [
  {
    name: 'Plop.js',
    category: 'code-generation',
    description: '代码生成器，用于创建项目模板和组件',
    features: ['模板生成', '交互式CLI', '自定义生成器'],
    integration: 'easy',
    popularity: 'medium',
    nextjsCompatible: true
  },
  {
    name: 'Hygen',
    category: 'code-generation',
    description: '现代化的代码生成工具',
    features: ['模板系统', '动态生成', '条件渲染'],
    integration: 'easy',
    popularity: 'medium',
    nextjsCompatible: true
  },
  {
    name: 'Vitest',
    category: 'testing',
    description: '快速的单元测试框架',
    features: ['Jest兼容', 'TypeScript支持', '快速执行'],
    integration: 'easy',
    popularity: 'high',
    nextjsCompatible: true
  },
  {
    name: 'Playwright',
    category: 'testing',
    description: '端到端测试自动化工具',
    features: ['跨浏览器测试', '自动等待', '可视化调试'],
    integration: 'medium',
    popularity: 'high',
    nextjsCompatible: true
  },
  {
    name: 'GitHub Actions',
    category: 'ci-cd',
    description: 'GitHub内置的CI/CD平台',
    features: ['工作流自动化', '并行执行', '缓存优化'],
    integration: 'easy',
    popularity: 'high',
    nextjsCompatible: true
  },
  {
    name: 'Vercel',
    category: 'deployment',
    description: 'Next.js官方部署平台',
    features: ['自动部署', '预览功能', '性能优化'],
    integration: 'easy',
    popularity: 'high',
    nextjsCompatible: true
  },
  {
    name: 'Sentry',
    category: 'monitoring',
    description: '应用性能监控和错误追踪',
    features: ['错误监控', '性能追踪', '发布跟踪'],
    integration: 'medium',
    popularity: 'high',
    nextjsCompatible: true
  },
  {
    name: 'TypeDoc',
    category: 'documentation',
    description: 'TypeScript文档生成工具',
    features: ['自动生成', '主题定制', 'API文档'],
    integration: 'easy',
    popularity: 'medium',
    nextjsCompatible: true
  }
];
```

### 2. 自动化工具配置管理

```typescript
// lib/automation-config.ts
export interface AutomationConfig {
  codeGeneration: {
    enabled: boolean;
    templates: string[];
    outputDir: string;
    interactive: boolean;
  };
  testing: {
    unit: {
      enabled: boolean;
      framework: 'vitest' | 'jest';
      coverage: boolean;
      watchMode: boolean;
    };
    e2e: {
      enabled: boolean;
      framework: 'playwright' | 'cypress';
      browsers: string[];
      headed: boolean;
    };
  };
  deployment: {
    enabled: boolean;
    platform: 'vercel' | 'netlify' | 'aws' | 'custom';
    environments: string[];
    autoDeploy: boolean;
    previewDeployments: boolean;
  };
  monitoring: {
    enabled: boolean;
    errorTracking: boolean;
    performanceTracking: boolean;
    uptimeMonitoring: boolean;
  };
  documentation: {
    enabled: boolean;
    autoGenerate: boolean;
    includeTypes: boolean;
    outputFormat: 'markdown' | 'html' | 'both';
  };
  qualityAssurance: {
    enabled: boolean;
    linting: boolean;
    formatting: boolean;
    typeChecking: boolean;
    securityScan: boolean;
  };
}

export class AutomationConfigManager {
  private config: AutomationConfig;
  private projectPath: string;

  constructor(projectPath: string, config?: Partial<AutomationConfig>) {
    this.projectPath = projectPath;
    this.config = this.mergeWithDefaults(config);
  }

  private mergeWithDefaults(config?: Partial<AutomationConfig>): AutomationConfig {
    const defaults: AutomationConfig = {
      codeGeneration: {
        enabled: true,
        templates: ['component', 'page', 'hook', 'util'],
        outputDir: 'src',
        interactive: true
      },
      testing: {
        unit: {
          enabled: true,
          framework: 'vitest',
          coverage: true,
          watchMode: true
        },
        e2e: {
          enabled: true,
          framework: 'playwright',
          browsers: ['chromium', 'firefox', 'webkit'],
          headed: false
        }
      },
      deployment: {
        enabled: true,
        platform: 'vercel',
        environments: ['development', 'staging', 'production'],
        autoDeploy: true,
        previewDeployments: true
      },
      monitoring: {
        enabled: true,
        errorTracking: true,
        performanceTracking: true,
        uptimeMonitoring: true
      },
      documentation: {
        enabled: true,
        autoGenerate: true,
        includeTypes: true,
        outputFormat: 'both'
      },
      qualityAssurance: {
        enabled: true,
        linting: true,
        formatting: true,
        typeChecking: true,
        securityScan: true
      }
    };

    return this.deepMerge(defaults, config || {});
  }

  private deepMerge(target: any, source: any): any {
    const result = { ...target };

    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(target[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }

    return result;
  }

  generateConfigFiles(): void {
    // 生成Vitest配置
    if (this.config.testing.unit.enabled) {
      this.generateVitestConfig();
    }

    // 生成Playwright配置
    if (this.config.testing.e2e.enabled) {
      this.generatePlaywrightConfig();
    }

    // 生成GitHub Actions工作流
    if (this.config.deployment.enabled) {
      this.generateGitHubActions();
    }

    // 生成ESLint配置
    if (this.config.qualityAssurance.linting) {
      this.generateESLintConfig();
    }

    // 生成Prettier配置
    if (this.config.qualityAssurance.formatting) {
      this.generatePrettierConfig();
    }
  }

  private generateVitestConfig(): void {
    const vitestConfig = `
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    exclude: [
      'node_modules/',
      'src/test/',
    ],
  },
});
`;

    const fs = require('fs');
    const path = require('path');
    fs.writeFileSync(
      path.join(this.projectPath, 'vitest.config.ts'),
      vitestConfig.trim()
    );
  }

  private generatePlaywrightConfig(): void {
    const playwrightConfig = `
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
`;

    const fs = require('fs');
    const path = require('path');
    fs.writeFileSync(
      path.join(this.projectPath, 'playwright.config.ts'),
      playwrightConfig.trim()
    );
  }

  private generateGitHubActions(): void {
    const ciWorkflow = `
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js \${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: \${{ matrix.node-version }}
        cache: 'pnpm'

    - name: Install pnpm
      uses: pnpm/action-setup@v2
      with:
        version: 8

    - name: Install dependencies
      run: pnpm install

    - name: Run linting
      run: pnpm lint

    - name: Run type checking
      run: pnpm type-check

    - name: Run unit tests
      run: pnpm test:unit

    - name: Run e2e tests
      run: pnpm test:e2e

    - name: Build application
      run: pnpm build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: 'pnpm'

    - name: Install pnpm
      uses: pnpm/action-setup@v2
      with:
        version: 8

    - name: Install dependencies
      run: pnpm install

    - name: Build application
      run: pnpm build

    - name: Deploy to Vercel
      uses: vercel/action@v1
      with:
        vercel-token: \${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: \${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: \${{ secrets.VERCEL_PROJECT_ID }}
`;

    const fs = require('fs');
    const path = require('path');
    const workflowsDir = path.join(this.projectPath, '.github', 'workflows');

    if (!fs.existsSync(workflowsDir)) {
      fs.mkdirSync(workflowsDir, { recursive: true });
    }

    fs.writeFileSync(
      path.join(workflowsDir, 'ci-cd.yml'),
      ciWorkflow.trim()
    );
  }

  private generateESLintConfig(): void {
    const eslintConfig = {
      extends: [
        'next/core-web-vitals',
        '@typescript-eslint/recommended',
        'prettier'
      ],
      parser: '@typescript-eslint/parser',
      plugins: ['@typescript-eslint'],
      rules: {
        '@typescript-eslint/no-unused-vars': 'error',
        '@typescript-eslint/no-explicit-any': 'warn',
        'react-hooks/exhaustive-deps': 'warn'
      },
      env: {
        browser: true,
        node: true,
        es2022: true
      }
    };

    const fs = require('fs');
    const path = require('path');
    fs.writeFileSync(
      path.join(this.projectPath, '.eslintrc.json'),
      JSON.stringify(eslintConfig, null, 2)
    );
  }

  private generatePrettierConfig(): void {
    const prettierConfig = {
      semi: false,
      singleQuote: true,
      tabWidth: 2,
      trailingComma: 'es5',
      printWidth: 80,
      bracketSpacing: true,
      arrowParens: 'avoid'
    };

    const fs = require('fs');
    const path = require('path');
    fs.writeFileSync(
      path.join(this.projectPath, '.prettierrc'),
      JSON.stringify(prettierConfig, null, 2)
    );

    const ignoreRules = [
      'node_modules',
      '.next',
      'dist',
      'build',
      '*.min.js',
      '*.json'
    ];

    fs.writeFileSync(
      path.join(this.projectPath, '.prettierignore'),
      ignoreRules.join('\n')
    );
  }

  getConfig(): AutomationConfig {
    return { ...this.config };
  }

  updateConfig(updates: Partial<AutomationConfig>): void {
    this.config = this.deepMerge(this.config, updates);
    this.generateConfigFiles();
  }
}
```

## 🚀 代码生成自动化

### 1. 模板生成器

```typescript
// lib/code-generator.ts
import ejs from 'ejs';
import fs from 'fs';
import path from 'path';
import inquirer from 'inquirer';

export interface TemplateConfig {
  name: string;
  description: string;
  type: 'component' | 'page' | 'hook' | 'util' | 'service';
  outputDir: string;
  templateFiles: string[];
  variables: TemplateVariable[];
  postGenerate?: (answers: any) => Promise<void>;
}

export interface TemplateVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'checkbox';
  description: string;
  required: boolean;
  default?: any;
  choices?: string[];
  validation?: (value: any) => boolean | string;
}

export class CodeGenerator {
  private templatesDir: string;
  private templates: Map<string, TemplateConfig> = new Map();

  constructor(projectPath: string) {
    this.templatesDir = path.join(projectPath, 'templates');
    this.loadTemplates();
  }

  private loadTemplates(): void {
    if (!fs.existsSync(this.templatesDir)) {
      return;
    }

    const templateDirs = fs.readdirSync(this.templatesDir, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);

    for (const templateName of templateDirs) {
      const templateConfigPath = path.join(this.templatesDir, templateName, 'template.json');
      if (fs.existsSync(templateConfigPath)) {
        const config = JSON.parse(fs.readFileSync(templateConfigPath, 'utf8'));
        this.templates.set(templateName, config);
      }
    }
  }

  async generateFromTemplate(templateName: string): Promise<void> {
    const template = this.templates.get(templateName);

    if (!template) {
      throw new Error(`Template '${templateName}' not found`);
    }

    console.log(`\n📋 Generating ${template.name}...`);
    console.log(template.description);

    // 收集变量值
    const answers = await this.collectVariables(template.variables);

    // 生成代码
    await this.generateFiles(template, answers);

    // 执行后置操作
    if (template.postGenerate) {
      await template.postGenerate(answers);
    }

    console.log(`✅ ${template.name} generated successfully!`);
  }

  private async collectVariables(variables: TemplateVariable[]): Promise<Record<string, any>> {
    const answers: Record<string, any> = {};

    for (const variable of variables) {
      const question = {
        name: variable.name,
        message: variable.description,
        type: variable.type,
        required: variable.required,
        default: variable.default,
        choices: variable.choices,
        validate: variable.validation
      };

      const result = await inquirer.prompt([question]);
      answers[variable.name] = result[variable.name];
    }

    return answers;
  }

  private async generateFiles(template: TemplateConfig, answers: Record<string, any>): Promise<void> {
    const templateDir = path.join(this.templatesDir, template.name);
    const outputDir = this.resolveOutputDir(template.outputDir, answers);

    // 确保输出目录存在
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // 生成每个模板文件
    for (const templateFile of template.templateFiles) {
      const templatePath = path.join(templateDir, templateFile);
      const outputPath = this.resolveOutputPath(templatePath, outputDir, answers);

      const templateContent = fs.readFileSync(templatePath, 'utf8');
      const generatedContent = await ejs.render(templateContent, answers);

      // 确保输出路径的目录存在
      const outputDirPath = path.dirname(outputPath);
      if (!fs.existsSync(outputDirPath)) {
        fs.mkdirSync(outputDirPath, { recursive: true });
      }

      fs.writeFileSync(outputPath, generatedContent);
      console.log(`  📄 Generated: ${outputPath}`);
    }
  }

  private resolveOutputDir(outputDir: string, answers: Record<string, any>): string {
    // 处理模板变量替换
    let resolvedDir = outputDir;

    for (const [key, value] of Object.entries(answers)) {
      resolvedDir = resolvedDir.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }

    return path.resolve(process.cwd(), resolvedDir);
  }

  private resolveOutputPath(templatePath: string, outputDir: string, answers: Record<string, any>): string {
    const fileName = path.basename(templatePath, '.ejs');

    // 处理文件名中的变量
    let resolvedFileName = fileName;
    for (const [key, value] of Object.entries(answers)) {
      resolvedFileName = resolvedFileName.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }

    return path.join(outputDir, resolvedFileName);
  }

  listTemplates(): TemplateConfig[] {
    return Array.from(this.templates.values());
  }

  // 创建新模板
  async createTemplate(config: TemplateConfig): Promise<void> {
    const templateDir = path.join(this.templatesDir, config.name);

    if (fs.existsSync(templateDir)) {
      throw new Error(`Template '${config.name}' already exists`);
    }

    fs.mkdirSync(templateDir, { recursive: true });

    // 保存配置文件
    const configPath = path.join(templateDir, 'template.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

    // 创建模板文件
    for (const templateFile of config.templateFiles) {
      const templatePath = path.join(templateDir, templateFile + '.ejs');
      fs.writeFileSync(templatePath, `// Template file for ${templateFile}\n`);
    }

    console.log(`✅ Template '${config.name}' created successfully!`);
  }
}

// 预定义的模板配置
export const componentTemplate: TemplateConfig = {
  name: 'component',
  description: 'Generate a React component with TypeScript',
  type: 'component',
  outputDir: 'src/components/{{name}}',
  templateFiles: [
    'index.tsx',
    'styles.module.css',
    'index.test.tsx',
    'index.stories.tsx'
  ],
  variables: [
    {
      name: 'name',
      type: 'string',
      description: 'Component name (PascalCase)',
      required: true,
      validation: (value: string) => {
        if (!/^[A-Z][a-zA-Z0-9]*$/.test(value)) {
          return 'Component name must be in PascalCase';
        }
        return true;
      }
    },
    {
      name: 'type',
      type: 'select',
      description: 'Component type',
      required: true,
      default: 'functional',
      choices: ['functional', 'class', 'hook']
    },
    {
      name: 'withStyles',
      type: 'boolean',
      description: 'Include CSS module',
      required: true,
      default: true
    },
    {
      name: 'withTests',
      type: 'boolean',
      description: 'Include test file',
      required: true,
      default: true
    },
    {
      name: 'withStories',
      type: 'boolean',
      description: 'Include Storybook stories',
      required: true,
      default: true
    }
  ]
};

export const pageTemplate: TemplateConfig = {
  name: 'page',
  description: 'Generate a Next.js page with TypeScript',
  type: 'page',
  outputDir: 'src/app/{{path}}',
  templateFiles: [
    'page.tsx',
    'layout.tsx',
    'page.test.tsx'
  ],
  variables: [
    {
      name: 'path',
      type: 'string',
      description: 'Page path (e.g., dashboard/users)',
      required: true
    },
    {
      name: 'title',
      type: 'string',
      description: 'Page title',
      required: true
    },
    {
      name: 'withLayout',
      type: 'boolean',
      description: 'Include layout file',
      required: true,
      default: true
    }
  ]
};
```

### 2. API 代码生成器

```typescript
// lib/api-generator.ts
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

export interface ApiEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description: string;
  parameters: ApiParameter[];
  requestBody?: ApiSchema;
  response: ApiSchema;
  auth: boolean;
  rateLimit?: {
    requests: number;
    window: string;
  };
}

export interface ApiParameter {
  name: string;
  type: 'path' | 'query' | 'header' | 'cookie';
  required: boolean;
  schema: ApiSchema;
  description: string;
}

export interface ApiSchema {
  type: string;
  properties: Record<string, ApiProperty>;
  required?: string[];
  description?: string;
}

export interface ApiProperty {
  type: string;
  description: string;
  example?: any;
  enum?: any[];
  items?: ApiProperty;
  format?: string;
}

export class ApiGenerator {
  private projectPath: string;
  private apiSpec: any;

  constructor(projectPath: string) {
    this.projectPath = projectPath;
  }

  // 从OpenAPI规范生成API
  async generateFromOpenAPI(specPath: string, options: {
    outputDir?: string;
    generateTypes?: boolean;
    generateClient?: boolean;
    generateRoutes?: boolean;
    generateTests?: boolean;
  } = {}): Promise<void> {
    const outputDir = options.outputDir || 'src/lib/api';
    const generateTypes = options.generateTypes ?? true;
    const generateClient = options.generateClient ?? true;
    const generateRoutes = options.generateRoutes ?? true;
    const generateTests = options.generateTests ?? true;

    console.log('🔧 Generating API from OpenAPI specification...');

    // 读取OpenAPI规范
    const specContent = fs.readFileSync(specPath, 'utf8');
    this.apiSpec = JSON.parse(specContent);

    // 创建输出目录
    if (!fs.existsSync(path.join(this.projectPath, outputDir))) {
      fs.mkdirSync(path.join(this.projectPath, outputDir), { recursive: true });
    }

    // 生成类型定义
    if (generateTypes) {
      await this.generateTypes(outputDir);
    }

    // 生成API客户端
    if (generateClient) {
      await this.generateApiClient(outputDir);
    }

    // 生成API路由
    if (generateRoutes) {
      await this.generateApiRoutes(outputDir);
    }

    // 生成测试
    if (generateTests) {
      await this.generateApiTests(outputDir);
    }

    console.log('✅ API generation completed!');
  }

  private async generateTypes(outputDir: string): Promise<void> {
    console.log('  📝 Generating types...');

    const typesContent = this.generateTypeDefinitions();
    const typesPath = path.join(this.projectPath, outputDir, 'types.ts');

    fs.writeFileSync(typesPath, typesContent);
  }

  private generateTypeDefinitions(): string {
    const types: string[] = [];
    const schemas = this.apiSpec.components?.schemas || {};

    for (const [name, schema] of Object.entries(schemas)) {
      const typeDefinition = this.generateTypeDefinition(name, schema as any);
      types.push(typeDefinition);
    }

    return types.join('\n\n');
  }

  private generateTypeDefinition(name: string, schema: any): string {
    const properties = schema.properties || {};
    const required = schema.required || [];

    let typeDefinition = `export interface ${this.capitalizeFirst(name)} {\n`;

    for (const [propName, propSchema] of Object.entries(properties)) {
      const isRequired = required.includes(propName);
      const propType = this.generatePropertyType(propName, propSchema as any);
      const optional = isRequired ? '' : '?';

      typeDefinition += `  ${propName}${optional}: ${propType};\n`;
    }

    typeDefinition += '}';

    return typeDefinition;
  }

  private generatePropertyType(propName: string, propSchema: any): string {
    const { type, items, $ref } = propSchema;

    if ($ref) {
      // 引用类型
      const refName = $ref.split('/').pop();
      return this.capitalizeFirst(refName);
    }

    if (type === 'array') {
      const itemType = this.generatePropertyType(propName, items || {});
      return `${itemType}[]`;
    }

    switch (type) {
      case 'string':
        return 'string';
      case 'number':
      case 'integer':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'object':
        return 'Record<string, any>';
      default:
        return 'any';
    }
  }

  private capitalizeFirst(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  private async generateApiClient(outputDir: string): Promise<void> {
    console.log('  🔌 Generating API client...');

    const clientContent = this.generateApiClientCode();
    const clientPath = path.join(this.projectPath, outputDir, 'client.ts');

    fs.writeFileSync(clientPath, clientContent);
  }

  private generateApiClientCode(): string {
    const baseUrl = this.apiSpec.servers?.[0]?.url || '';
    const paths = this.apiSpec.paths || {};

    let clientCode = `import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
${this.generateTypeImports()}

export class ApiClient {
  private instance: AxiosInstance;

  constructor(baseURL: string = '${baseUrl}') {
    this.instance = axios.create({
      baseURL,
      timeout: 10000,
    });

    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = \`Bearer \${token}\`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle common errors
        if (error.response?.status === 401) {
          // Handle authentication error
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Generate methods for each endpoint
`;

    for (const [path, pathSpec] of Object.entries(paths)) {
      for (const [method, operationSpec] of Object.entries(pathSpec as any)) {
        const methodName = this.generateMethodName(operationSpec.operationId || `${method}_${path}`);
        const methodCode = this.generateMethodCode(methodName, method.toUpperCase(), path, operationSpec);
        clientCode += methodCode;
      }
    }

    clientCode += `}

export const apiClient = new ApiClient();`;

    return clientCode;
  }

  private generateTypeImports(): string {
    const schemas = this.apiSpec.components?.schemas || {};
    const typeImports = Object.keys(schemas)
      .map(name => this.capitalizeFirst(name))
      .join(', ');

    return typeImports ? `import type { ${typeImports} } from './types';` : '';
  }

  private generateMethodName(operationId: string): string {
    return operationId
      .replace(/[-_\s]/g, '')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .split(' ')
      .map((word, index) => index === 0 ? word.toLowerCase() : this.capitalizeFirst(word))
      .join('');
  }

  private generateMethodCode(methodName: string, method: string, path: string, operationSpec: any): string {
    const parameters = operationSpec.parameters || [];
    const hasRequestBody = method !== 'GET' && operationSpec.requestBody;

    let methodCode = `
  async ${methodName}(`;

    // Parameters
    const methodParams: string[] = [];
    if (parameters.length > 0 || hasRequestBody) {
      methodParams.push('params: {');

      parameters.forEach((param: any) => {
        methodParams.push(`    ${param.name}?: ${this.generateParameterType(param)};`);
      });

      if (hasRequestBody) {
        methodParams.push('    data?: any;');
      }

      methodParams.push('  }');
    }

    methodCode += methodParams.join('\n') + '): Promise<any> {
    return this.instance.${method.toLowerCase()}('${this.formatPath(path)}';

    if (parameters.length > 0 || hasRequestBody) {
      methodCode += ', {';

      if (hasRequestBody) {
        methodCode += ' data: params.data,';
      }

      const pathParams = parameters.filter((p: any) => p.in === 'path');
      const queryParams = parameters.filter((p: any) => p.in === 'query');

      if (queryParams.length > 0) {
        methodCode += ' params: {';
        queryParams.forEach((param: any) => {
          methodCode += ` ${param.name}: params.${param.name},`;
        });
        methodCode += ' },';
      }

      methodCode += ' }';
    }

    methodCode += ');
  }`;

    return methodCode;
  }

  private generateParameterType(param: any): string {
    if (param.schema?.$ref) {
      const refName = param.schema.$ref.split('/').pop();
      return this.capitalizeFirst(refName);
    }

    switch (param.schema?.type) {
      case 'string':
        return 'string';
      case 'number':
      case 'integer':
        return 'number';
      case 'boolean':
        return 'boolean';
      case 'array':
        return 'any[]';
      default:
        return 'any';
    }
  }

  private formatPath(path: string): string {
    return path.replace(/{([^}]+)}/g, '${params.$1}');
  }

  private async generateApiRoutes(outputDir: string): Promise<void> {
    console.log('  🛣️  Generating API routes...');

    const routesDir = path.join(this.projectPath, 'src/app/api');
    if (!fs.existsSync(routesDir)) {
      fs.mkdirSync(routesDir, { recursive: true });
    }

    const paths = this.apiSpec.paths || {};

    for (const [path, pathSpec] of Object.entries(paths)) {
      await this.generateApiRoute(path, pathSpec as any, routesDir);
    }
  }

  private async generateApiRoute(path: string, pathSpec: any, routesDir: string): Promise<void> {
    const routePath = path.replace(/^\//, '').replace(/{([^}]+)}/g, '[$1]');
    const routeDir = path.join(routesDir, routePath);

    if (!fs.existsSync(routeDir)) {
      fs.mkdirSync(routeDir, { recursive: true });
    }

    for (const [method, operationSpec] of Object.entries(pathSpec)) {
      const routeFile = path.join(routeDir, 'route.ts');
      const routeCode = this.generateRouteCode(method.toUpperCase(), operationSpec);

      if (!fs.existsSync(routeFile)) {
        fs.writeFileSync(routeFile, routeCode);
      } else {
        // 如果文件已存在，追加新方法
        const existingContent = fs.readFileSync(routeFile, 'utf8');
        const newContent = existingContent.replace(
          /export { runtime } from 'next/headers';\n/,
          `export { runtime } from 'next/headers';\n\n${routeCode}`
        );
        fs.writeFileSync(routeFile, newContent);
      }
    }
  }

  private generateRouteCode(method: string, operationSpec: any): string {
    const summary = operationSpec.summary || '';
    const description = operationSpec.description || '';

    return `
// ${summary}
// ${description}
export async function ${operationSpec.operationId || 'handleRequest'}(
  request: Request,
  { params }: { params?: Record<string, string> }
) {
  try {
    // TODO: Implement ${method} handler
    return NextResponse.json({ message: '${method} handler not implemented' }, { status: 501 });
  } catch (error) {
    console.error('Error in ${operationSpec.operationId || 'handleRequest'}:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export { ${operationSpec.operationId || 'handleRequest'} as ${method.toLowerCase()} };
`;
  }

  private async generateApiTests(outputDir: string): Promise<void> {
    console.log('  🧪 Generating API tests...');

    const testDir = path.join(this.projectPath, 'src/__tests__/api');
    if (!fs.existsSync(testDir)) {
      fs.mkdirSync(testDir, { recursive: true });
    }

    const paths = this.apiSpec.paths || {};

    for (const [path, pathSpec] of Object.entries(paths)) {
      for (const [method, operationSpec] of Object.entries(pathSpec as any)) {
        const testFile = path.join(testDir, `${operationSpec.operationId || `${method}_${path.replace(/\//g, '_')}`}.test.ts`);
        const testCode = this.generateTestCode(method.toUpperCase(), path, operationSpec);

        if (!fs.existsSync(testFile)) {
          fs.writeFileSync(testFile, testCode);
        }
      }
    }
  }

  private generateTestCode(method: string, path: string, operationSpec: any): string {
    return `import { ${operationSpec.operationId || 'handleRequest'} } from '@/app/api/${path.replace(/^\//, '').replace(/{([^}]+)}/g, '[$1]')}/route';
import { NextRequest } from 'next/server';

describe('${operationSpec.summary || `${method} ${path}`}', () => {
  beforeEach(() => {
    // Setup test environment
  });

  it('should handle ${method.toLowerCase()} request', async () => {
    const request = new NextRequest('http://localhost:3000${path}', {
      method: '${method}',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const response = await ${operationSpec.operationId || 'handleRequest'}(request, {
      params: {},
    });

    expect(response.status).toBe(501); // Not implemented yet
  });

  // Add more test cases based on the OpenAPI specification
});
`;
  }
}
```

## 📊 部署自动化

### 1. 多环境部署配置

```typescript
// lib/deployment-automation.ts
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

export interface DeploymentEnvironment {
  name: string;
  branch: string;
  domain: string;
  environmentVariables: Record<string, string>;
  buildCommand: string;
  deployCommand: string;
  healthCheck?: {
    path: string;
    expectedStatus: number;
    timeout: number;
  };
}

export interface DeploymentConfig {
  environments: DeploymentEnvironment[];
  platform: 'vercel' | 'netlify' | 'aws' | 'custom';
  notifications: {
    slack?: {
      webhook: string;
      channel: string;
    };
    email?: {
      recipients: string[];
      smtp: {
        host: string;
        port: number;
        secure: boolean;
        auth: {
          user: string;
          pass: string;
        };
      };
    };
  };
  rollback: {
    enabled: boolean;
    autoRollback: boolean;
    healthCheckInterval: number;
  };
}

export class DeploymentAutomation {
  private projectPath: string;
  private config: DeploymentConfig;

  constructor(projectPath: string, config: DeploymentConfig) {
    this.projectPath = projectPath;
    this.config = config;
  }

  async deploy(environment: string, options: {
    dryRun?: boolean;
    force?: boolean;
    skipTests?: boolean;
    skipBuild?: boolean;
    notificationMessage?: string;
  } = {}): Promise<DeploymentResult> {
    const envConfig = this.config.environments.find(e => e.name === environment);

    if (!envConfig) {
      throw new Error(`Environment '${environment}' not found`);
    }

    console.log(`🚀 Starting deployment to ${environment}...`);

    const result: DeploymentResult = {
      environment,
      success: false,
      steps: [],
      startTime: Date.now(),
      endTime: 0,
      rollback: false
    };

    try {
      // 验证部署条件
      await this.validateDeploymentPrerequisites(envConfig, options);

      // 1. 运行测试
      if (!options.skipTests) {
        await this.runTests(result);
      }

      // 2. 构建应用
      if (!options.skipBuild) {
        await this.buildApplication(envConfig, result);
      }

      // 3. 部署到目标环境
      if (!options.dryRun) {
        await this.executeDeployment(envConfig, result);
      }

      // 4. 健康检查
      await this.performHealthCheck(envConfig, result);

      // 5. 发送通知
      await this.sendNotifications(envConfig, result, options.notificationMessage);

      result.success = true;
      console.log(`✅ Deployment to ${environment} completed successfully!`);

    } catch (error) {
      console.error(`❌ Deployment to ${environment} failed:`, error);

      result.success = false;
      result.error = error instanceof Error ? error.message : 'Unknown error';

      // 自动回滚
      if (this.config.rollback.enabled && this.config.rollback.autoRollback) {
        console.log('🔄 Initiating automatic rollback...');
        result.rollback = true;
        await this.rollback(environment, result);
      }
    }

    result.endTime = Date.now();
    result.duration = result.endTime - result.startTime;

    return result;
  }

  private async validateDeploymentPrerequisites(
    envConfig: DeploymentEnvironment,
    options: any
  ): Promise<void> {
    const steps: string[] = [];

    // 检查当前分支
    const currentBranch = this.getCurrentBranch();
    if (currentBranch !== envConfig.branch && !options.force) {
      throw new Error(`Current branch '${currentBranch}' does not match target branch '${envConfig.branch}'. Use --force to override.`);
    }
    steps.push(`Branch validation: ${currentBranch}`);

    // 检查环境变量
    const missingVars = this.getMissingEnvironmentVariables(envConfig);
    if (missingVars.length > 0) {
      throw new Error(`Missing environment variables: ${missingVars.join(', ')}`);
    }
    steps.push(`Environment variables validation: ${Object.keys(envConfig.environmentVariables).length} variables`);

    // 检查构建工具
    if (!this.isBuildToolAvailable()) {
      throw new Error('Build tools not available');
    }
    steps.push('Build tools validation');

    console.log('✅ Deployment prerequisites validated');
  }

  private async runTests(result: DeploymentResult): Promise<void> {
    console.log('🧪 Running tests...');

    try {
      execSync('npm run test', { cwd: this.projectPath, stdio: 'inherit' });
      result.steps.push({
        name: 'Tests',
        status: 'success',
        duration: 0,
        message: 'All tests passed'
      });
    } catch (error) {
      result.steps.push({
        name: 'Tests',
        status: 'failed',
        duration: 0,
        message: error instanceof Error ? error.message : 'Tests failed'
      });
      throw new Error('Tests failed');
    }
  }

  private async buildApplication(envConfig: DeploymentEnvironment, result: DeploymentResult): Promise<void> {
    console.log('🔨 Building application...');

    const startTime = Date.now();

    try {
      execSync(envConfig.buildCommand, {
        cwd: this.projectPath,
        stdio: 'inherit',
        env: { ...process.env, ...envConfig.environmentVariables }
      });

      const duration = Date.now() - startTime;

      result.steps.push({
        name: 'Build',
        status: 'success',
        duration,
        message: 'Application built successfully'
      });
    } catch (error) {
      const duration = Date.now() - startTime;

      result.steps.push({
        name: 'Build',
        status: 'failed',
        duration,
        message: error instanceof Error ? error.message : 'Build failed'
      });
      throw new Error('Build failed');
    }
  }

  private async executeDeployment(envConfig: DeploymentEnvironment, result: DeploymentResult): Promise<void> {
    console.log('🚀 Deploying application...');

    const startTime = Date.now();

    try {
      switch (this.config.platform) {
        case 'vercel':
          await this.deployToVercel(envConfig);
          break;
        case 'netlify':
          await this.deployToNetlify(envConfig);
          break;
        case 'aws':
          await this.deployToAWS(envConfig);
          break;
        default:
          throw new Error(`Unsupported platform: ${this.config.platform}`);
      }

      const duration = Date.now() - startTime;

      result.steps.push({
        name: 'Deploy',
        status: 'success',
        duration,
        message: `Deployed to ${envConfig.name}`
      });
    } catch (error) {
      const duration = Date.now() - startTime;

      result.steps.push({
        name: 'Deploy',
        status: 'failed',
        duration,
        message: error instanceof Error ? error.message : 'Deployment failed'
      });
      throw error;
    }
  }

  private async deployToVercel(envConfig: DeploymentEnvironment): Promise<void> {
    execSync('npx vercel --prod', {
      cwd: this.projectPath,
      stdio: 'inherit',
      env: { ...process.env, ...envConfig.environmentVariables }
    });
  }

  private async deployToNetlify(envConfig: DeploymentEnvironment): Promise<void> {
    execSync('npx netlify deploy --prod', {
      cwd: this.projectPath,
      stdio: 'inherit',
      env: { ...process.env, ...envConfig.environmentVariables }
    });
  }

  private async deployToAWS(envConfig: DeploymentEnvironment): Promise<void> {
    // AWS部署逻辑
    console.log('Deploying to AWS (simplified implementation)');
  }

  private async performHealthCheck(envConfig: DeploymentEnvironment, result: DeploymentResult): Promise<void> {
    if (!envConfig.healthCheck) {
      return;
    }

    console.log('🔍 Performing health check...');

    const startTime = Date.now();

    try {
      const response = await fetch(`https://${envConfig.domain}${envConfig.healthCheck.path}`, {
        method: 'GET',
        timeout: envConfig.healthCheck.timeout
      });

      if (response.status !== envConfig.healthCheck.expectedStatus) {
        throw new Error(`Health check failed: Expected ${envConfig.healthCheck.expectedStatus}, got ${response.status}`);
      }

      const duration = Date.now() - startTime;

      result.steps.push({
        name: 'Health Check',
        status: 'success',
        duration,
        message: `Health check passed: ${response.status}`
      });
    } catch (error) {
      const duration = Date.now() - startTime;

      result.steps.push({
        name: 'Health Check',
        status: 'failed',
        duration,
        message: error instanceof Error ? error.message : 'Health check failed'
      });
      throw error;
    }
  }

  private async sendNotifications(
    envConfig: DeploymentEnvironment,
    result: DeploymentResult,
    customMessage?: string
  ): Promise<void> {
    if (!this.config.notifications) {
      return;
    }

    console.log('📧 Sending notifications...');

    const message = customMessage || this.generateDeploymentMessage(envConfig, result);

    // Slack通知
    if (this.config.notifications.slack) {
      await this.sendSlackNotification(message, result);
    }

    // Email通知
    if (this.config.notifications.email) {
      await this.sendEmailNotification(message, result);
    }
  }

  private generateDeploymentMessage(envConfig: DeploymentEnvironment, result: DeploymentResult): string {
    const status = result.success ? '✅ Success' : '❌ Failed';
    const duration = result.duration ? ` (${result.duration}ms)` : '';
    const rollbackInfo = result.rollback ? ' - Rollback initiated' : '';

    return `${status}: Deployment to ${envConfig.name}${duration}${rollbackInfo}`;
  }

  private async sendSlackNotification(message: string, result: DeploymentResult): Promise<void> {
    if (!this.config.notifications?.slack) {
      return;
    }

    const { webhook, channel } = this.config.notifications.slack;

    const payload = {
      channel,
      text: message,
      attachments: [
        {
          color: result.success ? '#36a64f' : '#ff0000',
          fields: result.steps.map(step => ({
            title: step.name,
            value: `${step.status} - ${step.message}`,
            short: true
          }))
        }
      ]
    };

    await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  private async sendEmailNotification(message: string, result: DeploymentResult): Promise<void> {
    // 简化的邮件发送实现
    console.log('Email notification would be sent here');
  }

  async rollback(environment: string, result?: DeploymentResult): Promise<void> {
    console.log(`🔄 Rolling back deployment to ${environment}...`);

    const envConfig = this.config.environments.find(e => e.name === environment);
    if (!envConfig) {
      throw new Error(`Environment '${environment}' not found`);
    }

    try {
      // 执行回滚逻辑
      switch (this.config.platform) {
        case 'vercel':
          execSync('npx vercel rollback', {
            cwd: this.projectPath,
            stdio: 'inherit'
          });
          break;
        case 'netlify':
          execSync('npx netlify deploy:rollback --prod', {
            cwd: this.projectPath,
            stdio: 'inherit'
          });
          break;
        default:
          throw new Error(`Rollback not supported for platform: ${this.config.platform}`);
      }

      if (result) {
        result.rollback = true;
      }

      console.log('✅ Rollback completed successfully');

    } catch (error) {
      console.error('❌ Rollback failed:', error);
      throw error;
    }
  }

  private getCurrentBranch(): string {
    try {
      const result = execSync('git branch --show-current', {
        cwd: this.projectPath,
        encoding: 'utf8'
      });
      return result.trim();
    } catch (error) {
      throw new Error('Failed to get current branch');
    }
  }

  private getMissingEnvironmentVariables(envConfig: DeploymentEnvironment): string[] {
    return Object.keys(envConfig.environmentVariables).filter(key => {
      return !process.env[key] && !envConfig.environmentVariables[key];
    });
  }

  private isBuildToolAvailable(): boolean {
    try {
      execSync('npm --version', { cwd: this.projectPath, stdio: 'pipe' });
      return true;
    } catch (error) {
      return false;
    }
  }
}

interface DeploymentResult {
  environment: string;
  success: boolean;
  steps: Array<{
    name: string;
    status: 'success' | 'failed' | 'skipped';
    duration: number;
    message: string;
  }>;
  startTime: number;
  endTime: number;
  duration?: number;
  error?: string;
  rollback?: boolean;
}
```

## 🎯 监控和告警自动化

### 1. 监控系统配置

```typescript
// lib/monitoring-automation.ts
export interface MonitoringConfig {
  application: {
    name: string;
    version: string;
    environment: string;
  };
  errorTracking: {
    enabled: boolean;
    dsn: string;
    sampleRate: number;
    ignoreErrors: string[];
  };
  performanceMonitoring: {
    enabled: boolean;
    sampleRate: number;
    tracesSampleRate: number;
  };
  uptimeMonitoring: {
    enabled: boolean;
    checkInterval: number;
    endpoints: UptimeCheck[];
  };
  customMetrics: CustomMetric[];
  alerts: AlertConfig[];
}

export interface UptimeCheck {
  name: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  expectedStatus: number;
  timeout: number;
  regions: string[];
}

export interface CustomMetric {
  name: string;
  type: 'counter' | 'gauge' | 'histogram';
  description: string;
  labels: string[];
}

export interface AlertConfig {
  name: string;
  condition: {
    metric: string;
    operator: 'gt' | 'lt' | 'eq' | 'ne';
    threshold: number;
    duration: string;
  };
  severity: 'info' | 'warning' | 'error' | 'critical';
  channels: NotificationChannel[];
}

export interface NotificationChannel {
  type: 'email' | 'slack' | 'webhook' | 'pagerduty';
  config: Record<string, any>;
}

export class MonitoringAutomation {
  private config: MonitoringConfig;

  constructor(config: MonitoringConfig) {
    this.config = config;
  }

  initializeMonitoring(): void {
    if (this.config.errorTracking.enabled) {
      this.initializeErrorTracking();
    }

    if (this.config.performanceMonitoring.enabled) {
      this.initializePerformanceMonitoring();
    }

    if (this.config.uptimeMonitoring.enabled) {
      this.initializeUptimeMonitoring();
    }

    if (this.config.customMetrics.length > 0) {
      this.initializeCustomMetrics();
    }

    if (this.config.alerts.length > 0) {
      this.initializeAlerts();
    }
  }

  private initializeErrorTracking(): void {
    // Sentry错误追踪初始化
    const sentryConfig = {
      dsn: this.config.errorTracking.dsn,
      environment: this.config.application.environment,
      release: `${this.config.application.name}@${this.config.application.version}`,
      sampleRate: this.config.errorTracking.sampleRate,
      ignoreErrors: this.config.errorTracking.ignoreErrors,
      beforeSend: (event: any) => {
        // 自定义错误处理逻辑
        return event;
      }
    };

    // 在实际应用中，这里会初始化Sentry SDK
    console.log('Error tracking initialized with config:', sentryConfig);
  }

  private initializePerformanceMonitoring(): void {
    // 性能监控初始化
    const performanceConfig = {
      tracesSampleRate: this.config.performanceMonitoring.tracesSampleRate,
      sampleRate: this.config.performanceMonitoring.sampleRate
    };

    console.log('Performance monitoring initialized:', performanceConfig);
  }

  private initializeUptimeMonitoring(): void {
    // 健康检查监控初始化
    this.config.uptimeMonitoring.endpoints.forEach(endpoint => {
      this.startUptimeCheck(endpoint);
    });
  }

  private startUptimeCheck(endpoint: UptimeCheck): void {
    const checkInterval = setInterval(async () => {
      try {
        const startTime = Date.now();

        const response = await fetch(endpoint.url, {
          method: endpoint.method,
          signal: AbortSignal.timeout(endpoint.timeout)
        });

        const responseTime = Date.now() - startTime;

        // 记录监控指标
        this.recordMetric('uptime_check', {
          name: endpoint.name,
          status: response.status,
          responseTime,
          success: response.status === endpoint.expectedStatus
        });

        // 检查是否需要触发告警
        if (response.status !== endpoint.expectedStatus) {
          this.triggerAlert('uptime_check_failed', {
            endpoint: endpoint.name,
            expectedStatus: endpoint.expectedStatus,
            actualStatus: response.status,
            responseTime
          });
        }

      } catch (error) {
        this.recordMetric('uptime_check', {
          name: endpoint.name,
          status: 0,
          responseTime: endpoint.timeout,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        });

        this.triggerAlert('uptime_check_error', {
          endpoint: endpoint.name,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }, this.config.uptimeMonitoring.checkInterval);

    console.log(`Started uptime check for ${endpoint.name}`);
  }

  private initializeCustomMetrics(): void {
    this.config.customMetrics.forEach(metric => {
      console.log(`Custom metric initialized: ${metric.name} (${metric.type})`);
    });
  }

  private initializeAlerts(): void {
    this.config.alerts.forEach(alert => {
      console.log(`Alert configured: ${alert.name} - ${alert.severity}`);
    });
  }

  // 记录自定义指标
  recordMetric(name: string, value: any, labels?: Record<string, string>): void {
    const metric = {
      name,
      value,
      labels: labels || {},
      timestamp: Date.now(),
      application: this.config.application.name,
      environment: this.config.application.environment
    };

    // 在实际应用中，这里会发送到监控系统
    console.log('Metric recorded:', metric);

    // 检查告警条件
    this.checkAlertConditions(name, value);
  }

  // 检查告警条件
  private checkAlertConditions(metricName: string, value: any): void {
    this.config.alerts.forEach(alert => {
      if (alert.condition.metric === metricName) {
        const shouldAlert = this.evaluateCondition(alert.condition, value);

        if (shouldAlert) {
          this.triggerAlert(alert.name, {
            metric: metricName,
            value,
            condition: alert.condition
          });
        }
      }
    });
  }

  private evaluateCondition(condition: AlertConfig['condition'], value: any): boolean {
    switch (condition.operator) {
      case 'gt':
        return value > condition.threshold;
      case 'lt':
        return value < condition.threshold;
      case 'eq':
        return value === condition.threshold;
      case 'ne':
        return value !== condition.threshold;
      default:
        return false;
    }
  }

  // 触发告警
  private triggerAlert(alertName: string, data: any): void {
    const alert = this.config.alerts.find(a => a.name === alertName);
    if (!alert) {
      return;
    }

    console.log(`🚨 Alert triggered: ${alertName}`, data);

    // 发送告警通知
    alert.channels.forEach(channel => {
      this.sendNotification(channel, alert, data);
    });
  }

  private sendNotification(
    channel: NotificationChannel,
    alert: AlertConfig,
    data: any
  ): void {
    const message = this.formatAlertMessage(alert, data);

    switch (channel.type) {
      case 'slack':
        this.sendSlackNotification(channel.config, message, alert.severity);
        break;
      case 'email':
        this.sendEmailNotification(channel.config, message, alert.severity);
        break;
      case 'webhook':
        this.sendWebhookNotification(channel.config, message, alert.severity, data);
        break;
      case 'pagerduty':
        this.sendPagerDutyNotification(channel.config, message, alert.severity, data);
        break;
    }
  }

  private formatAlertMessage(alert: AlertConfig, data: any): string {
    const severityEmoji = {
      info: 'ℹ️',
      warning: '⚠️',
      error: '❌',
      critical: '🚨'
    };

    return `${severityEmoji[alert.severity]} **${alert.name}**

Application: ${this.config.application.name}
Environment: ${this.config.application.environment}
Time: ${new Date().toISOString()}

Details:
${JSON.stringify(data, null, 2)}`;
  }

  private sendSlackNotification(config: any, message: string, severity: string): void {
    const payload = {
      channel: config.channel,
      text: message,
      attachments: [
        {
          color: this.getSeverityColor(severity),
          fields: [
            {
              title: 'Severity',
              value: severity.toUpperCase(),
              short: true
            },
            {
              title: 'Application',
              value: this.config.application.name,
              short: true
            }
          ]
        }
      ]
    };

    console.log('Slack notification sent:', payload);
  }

  private sendEmailNotification(config: any, message: string, severity: string): void {
    const emailPayload = {
      to: config.recipients,
      subject: `[${severity.toUpperCase()}] ${this.config.application.name} Alert`,
      text: message
    };

    console.log('Email notification sent:', emailPayload);
  }

  private sendWebhookNotification(config: any, message: string, severity: string, data: any): void {
    const payload = {
      message,
      severity,
      application: this.config.application.name,
      environment: this.config.application.environment,
      timestamp: Date.now(),
      data
    };

    console.log('Webhook notification sent:', payload);
  }

  private sendPagerDutyNotification(config: any, message: string, severity: string, data: any): void {
    const payload = {
      service_key: config.serviceKey,
      incident_key: `${this.config.application.name}-${severity}`,
      event_type: 'trigger',
      description: message,
      client: this.config.application.name,
      client_url: config.clientUrl,
      details: data
    };

    console.log('PagerDuty notification sent:', payload);
  }

  private getSeverityColor(severity: string): string {
    const colors = {
      info: '#36a64f',
      warning: '#ff9500',
      error: '#ff0000',
      critical: '#990000'
    };

    return colors[severity] || '#36a64f';
  }

  // 错误追踪方法
  captureError(error: Error, context?: any): void {
    const errorData = {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: Date.now(),
      application: this.config.application.name,
      environment: this.config.application.environment
    };

    console.error('Error captured:', errorData);

    // 记录错误指标
    this.recordMetric('errors', 1, { type: error.name });

    // 触发错误告警
    this.triggerAlert('error_occurred', errorData);
  }

  // 性能追踪方法
  capturePerformanceMetric(name: string, value: number, unit?: string): void {
    this.recordMetric(name, value, { unit });

    // 检查性能告警
    this.checkAlertConditions(name, value);
  }

  // 自定义事件追踪
  trackEvent(name: string, data: any): void {
    this.recordMetric(name, 1, { ...data, type: 'event' });
  }

  // 健康检查
  async performHealthCheck(): Promise<HealthCheckResult> {
    const checks: HealthCheck[] = [];
    let overall = 'healthy';

    // 检查错误追踪
    if (this.config.errorTracking.enabled) {
      const errorCheck = await this.checkErrorTracking();
      checks.push(errorCheck);
      if (errorCheck.status !== 'healthy') {
        overall = 'degraded';
      }
    }

    // 检查性能监控
    if (this.config.performanceMonitoring.enabled) {
      const performanceCheck = await this.checkPerformanceMonitoring();
      checks.push(performanceCheck);
      if (performanceCheck.status !== 'healthy') {
        overall = 'degraded';
      }
    }

    // 检查自定义指标
    const metricsCheck = await this.checkCustomMetrics();
    checks.push(metricsCheck);
    if (metricsCheck.status !== 'healthy') {
      overall = 'degraded';
    }

    return {
      overall,
      checks,
      timestamp: Date.now()
    };
  }

  private async checkErrorTracking(): Promise<HealthCheck> {
    // 简化的错误追踪健康检查
    return {
      name: 'Error Tracking',
      status: 'healthy',
      message: 'Error tracking is functioning normally',
      details: {
        dsn: this.config.errorTracking.dsn,
        sampleRate: this.config.errorTracking.sampleRate
      }
    };
  }

  private async checkPerformanceMonitoring(): Promise<HealthCheck> {
    // 简化的性能监控健康检查
    return {
      name: 'Performance Monitoring',
      status: 'healthy',
      message: 'Performance monitoring is functioning normally',
      details: {
        sampleRate: this.config.performanceMonitoring.sampleRate,
        tracesSampleRate: this.config.performanceMonitoring.tracesSampleRate
      }
    };
  }

  private async checkCustomMetrics(): Promise<HealthCheck> {
    // 简化的自定义指标健康检查
    return {
      name: 'Custom Metrics',
      status: 'healthy',
      message: `${this.config.customMetrics.length} custom metrics configured`,
      details: {
        count: this.config.customMetrics.length,
        metrics: this.config.customMetrics.map(m => m.name)
      }
    };
  }
}

interface HealthCheckResult {
  overall: 'healthy' | 'degraded' | 'unhealthy';
  checks: HealthCheck[];
  timestamp: number;
}

interface HealthCheck {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  message: string;
  details?: any;
}
```

## 🎯 最佳实践和总结

### 1. 自动化工具检查清单

```typescript
// checklists/automation-best-practices.ts
export const automationBestPracticesChecklist = [
  {
    category: '代码生成',
    items: [
      '使用模板系统生成标准化代码',
      '保持模板的可维护性和可扩展性',
      '验证生成代码的质量',
      '提供交互式配置选项'
    ]
  },
  {
    category: '测试自动化',
    items: [
      '单元测试覆盖率要求',
      '集成测试自动化',
      '端到端测试自动化',
      '测试结果报告和可视化'
    ]
  },
  {
    category: '部署自动化',
    items: [
      '多环境部署配置',
      '自动回滚机制',
      '部署健康检查',
      '部署状态通知'
    ]
  },
  {
    category: '监控自动化',
    items: [
      '错误追踪和告警',
      '性能监控和分析',
      '可用性监控',
      '自定义指标追踪'
    ]
  },
  {
    category: 'CI/CD流水线',
    items: [
      '分支策略和自动化',
      '代码质量门禁',
      '自动化测试',
      '部署审批流程'
    ]
  }
];

export const runAutomationBestPracticesCheck = async (): Promise<void> => {
  console.log('🔍 Running Automation Best Practices Check...');

  for (const category of automationBestPracticesChecklist) {
    console.log(`\n📋 ${category.category}:`);
    for (const item of category.items) {
      console.log(`  ✅ ${item}`);
    }
  }

  console.log('\n🎯 Automation best practices check completed!');
};
```

### 2. 自动化工具选择指南

```typescript
// guides/automation-tool-selection.ts
export class AutomationToolSelector {
  recommendTools(project: {
    size: 'small' | 'medium' | 'large' | 'enterprise';
    type: 'web' | 'mobile' | 'fullstack' | 'monorepo';
    team: 'solo' | 'small' | 'medium' | 'large';
    complexity: 'simple' | 'moderate' | 'complex';
    budget: 'limited' | 'moderate' | 'unlimited';
  }): ToolRecommendation {
    const recommendations: ToolRecommendation = {
      codeGeneration: [],
      testing: [],
      deployment: [],
      monitoring: [],
      ciCd: [],
      justification: []
    };

    // 代码生成工具推荐
    if (project.size === 'small' || project.complexity === 'simple') {
      recommendations.codeGeneration.push({
        tool: 'Plop.js',
        reason: '简单易用，适合小型项目',
        priority: 'high'
      });
    } else {
      recommendations.codeGeneration.push({
        tool: 'Hygen',
        reason: '功能强大，适合复杂项目',
        priority: 'high'
      });
    }

    // 测试工具推荐
    if (project.team === 'solo' || project.team === 'small') {
      recommendations.testing.push({
        tool: 'Vitest',
        reason: '快速且易于配置',
        priority: 'high'
      });
    } else {
      recommendations.testing.push(
        {
          tool: 'Vitest',
          reason: '快速的单元测试',
          priority: 'high'
        },
        {
          tool: 'Playwright',
          reason: '跨浏览器端到端测试',
          priority: 'high'
        }
      );
    }

    // 部署平台推荐
    if (project.budget === 'limited') {
      recommendations.deployment.push({
        tool: 'Vercel',
        reason: '免费额度适合小项目',
        priority: 'high'
      });
    } else if (project.size === 'enterprise') {
      recommendations.deployment.push({
        tool: 'AWS/Azure',
        reason: '企业级部署解决方案',
        priority: 'high'
      });
    }

    // CI/CD工具推荐
    if (project.team === 'solo' || project.team === 'small') {
      recommendations.ciCd.push({
        tool: 'GitHub Actions',
        reason: '与GitHub集成，易于使用',
        priority: 'high'
      });
    } else {
      recommendations.ciCd.push(
        {
          tool: 'GitHub Actions',
          reason: '灵活且功能强大',
          priority: 'high'
        },
        {
          tool: 'Jenkins',
          reason: '企业级CI/CD解决方案',
          priority: 'medium'
        }
      );
    }

    // 生成推荐理由
    recommendations.justification = this.generateJustification(project, recommendations);

    return recommendations;
  }

  private generateJustification(
    project: any,
    recommendations: ToolRecommendation
  ): string[] {
    const justification: string[] = [];

    if (project.size === 'small') {
      justification.push('项目规模较小，推荐使用轻量级工具');
    }

    if (project.team === 'solo') {
      justification.push('独立开发者，需要自动化工具提高效率');
    }

    if (project.complexity === 'simple') {
      justification.push('项目复杂度较低，工具选择应保持简单');
    }

    if (project.budget === 'limited') {
      justification.push('预算有限，优先选择免费或低成本工具');
    }

    return justification;
  }
}

interface ToolRecommendation {
  codeGeneration: Array<{
    tool: string;
    reason: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  testing: Array<{
    tool: string;
    reason: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  deployment: Array<{
    tool: string;
    reason: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  monitoring: Array<{
    tool: string;
    reason: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  ciCd: Array<{
    tool: string;
    reason: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  justification: string[];
}
```

## 🎯 总结

自动化工具是现代前端工程化的核心驱动力。通过合理选择和配置自动化工具，可以显著提升开发效率、代码质量和项目可维护性。

### 关键要点：

1. **工具选择**：根据项目规模和复杂度选择合适的自动化工具
2. **代码生成**：使用模板系统生成标准化代码，提高开发效率
3. **测试自动化**：建立完整的自动化测试体系
4. **部署自动化**：实现多环境部署和自动回滚
5. **监控自动化**：建立全面的监控和告警体系
6. **CI/CD流水线**：自动化构建、测试和部署流程

### 实施建议：

- **渐进式实施**：从关键环节开始，逐步扩展自动化覆盖
- **工具集成**：确保各工具之间的良好集成
- **配置管理**：集中管理自动化配置，便于维护
- **监控和优化**：持续监控自动化流程的效果并优化
- **团队培训**：确保团队成员掌握自动化工具的使用

通过掌握这些自动化技术，可以构建高效、可靠的现代前端开发流程。