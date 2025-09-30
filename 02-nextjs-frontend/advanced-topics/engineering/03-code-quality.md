# 代码质量 - Next.js 15 现代工程化实践

## 📋 概述

代码质量是现代前端工程化的核心要素。高质量的代码不仅提升了开发效率，还确保了应用的长期可维护性。本文将深入探讨如何在Next.js 15项目中实施全面的代码质量保证体系，包括代码规范、静态分析、测试策略和质量监控。

## 🎯 代码质量基础

### 1. 代码质量维度

```typescript
// types/code-quality-types.ts
export type QualityDimension =
  | 'correctness'      // 正确性 - 代码是否符合预期行为
  | 'reliability'      // 可靠性 - 代码在各种条件下的稳定性
  | 'efficiency'       // 效率性 - 性能和资源使用
  | 'maintainability'  // 可维护性 - 代码的易理解和修改程度
  | 'readability'      // 可读性 - 代码的清晰程度
  | 'security'         // 安全性 - 代码的安全性防护
  | 'testability'      // 可测试性 - 代码的测试覆盖程度
  | 'consistency'      // 一致性 - 代码风格和结构的一致性

export interface QualityMetric {
  dimension: QualityDimension;
  name: string;
  description: string;
  weight: number; // 0-1，权重
  threshold: {
    excellent: number;
    good: number;
    acceptable: number;
    poor: number;
  };
  measurement: {
    tool: string;
    method: string;
    unit: string;
  };
}

export const qualityMetrics: QualityMetric[] = [
  {
    dimension: 'correctness',
    name: 'Type Safety',
    description: 'TypeScript类型安全程度',
    weight: 0.15,
    threshold: {
      excellent: 0.95,
      good: 0.90,
      acceptable: 0.80,
      poor: 0.70
    },
    measurement: {
      tool: 'TypeScript Compiler',
      method: 'Type coverage analysis',
      unit: 'percentage'
    }
  },
  {
    dimension: 'reliability',
    name: 'Test Coverage',
    description: '测试覆盖率',
    weight: 0.20,
    threshold: {
      excellent: 0.90,
      good: 0.80,
      acceptable: 0.70,
      poor: 0.60
    },
    measurement: {
      tool: 'Vitest/Istanbul',
      method: 'Code coverage analysis',
      unit: 'percentage'
    }
  },
  {
    dimension: 'efficiency',
    name: 'Performance Score',
    description: '代码性能评分',
    weight: 0.15,
    threshold: {
      excellent: 0.90,
      good: 0.80,
      acceptable: 0.70,
      poor: 0.60
    },
    measurement: {
      tool: 'Lighthouse/Web Vitals',
      method: 'Performance metrics',
      unit: 'score'
    }
  },
  {
    dimension: 'maintainability',
    name: 'Complexity Index',
    description: '代码复杂度指标',
    weight: 0.15,
    threshold: {
      excellent: 0.85,
      good: 0.75,
      acceptable: 0.65,
      poor: 0.55
    },
    measurement: {
      tool: 'ESLint/Complexity Tools',
      method: 'Cyclomatic complexity analysis',
      unit: 'index'
    }
  },
  {
    dimension: 'readability',
    name: 'Code Style',
    description: '代码风格一致性',
    weight: 0.10,
    threshold: {
      excellent: 0.95,
      good: 0.90,
      acceptable: 0.80,
      poor: 0.70
    },
    measurement: {
      tool: 'ESLint/Prettier',
      method: 'Style violation analysis',
      unit: 'consistency score'
    }
  },
  {
    dimension: 'security',
    name: 'Security Score',
    description: '代码安全评分',
    weight: 0.15,
    threshold: {
      excellent: 0.95,
      good: 0.90,
      acceptable: 0.80,
      poor: 0.70
    },
    measurement: {
      tool: 'SonarQube/ESLint Security',
      method: 'Security vulnerability analysis',
      unit: 'score'
    }
  },
  {
    dimension: 'testability',
    name: 'Test Design',
    description: '测试设计质量',
    weight: 0.10,
    threshold: {
      excellent: 0.90,
      good: 0.80,
      acceptable: 0.70,
      poor: 0.60
    },
    measurement: {
      tool: 'Manual Review',
      method: 'Test structure analysis',
      unit: 'quality score'
    }
  }
];
```

### 2. 质量评估模型

```typescript
// lib/quality-assessment.ts
import { QualityMetric, qualityMetrics } from '@/types/code-quality-types';

export interface QualityAssessment {
  overallScore: number;
  grade: 'A+' | 'A' | 'B' | 'C' | 'D' | 'F';
  dimensions: DimensionAssessment[];
  recommendations: QualityRecommendation[];
  timestamp: number;
}

export interface DimensionAssessment {
  dimension: QualityDimension;
  score: number;
  grade: 'excellent' | 'good' | 'acceptable' | 'poor';
  details: {
    measuredValue: number;
    threshold: QualityMetric['threshold'];
    issues: QualityIssue[];
  };
}

export interface QualityIssue {
  severity: 'critical' | 'major' | 'minor' | 'info';
  description: string;
  location: string;
  suggestion: string;
  rule: string;
}

export interface QualityRecommendation {
  priority: 'high' | 'medium' | 'low';
  category: QualityDimension;
  title: string;
  description: string;
  actions: string[];
  impact: string;
  effort: 'low' | 'medium' | 'high';
}

export class QualityAssessmentEngine {
  private metrics: QualityMetric[] = qualityMetrics;

  async assessProjectQuality(projectPath: string): Promise<QualityAssessment> {
    const dimensions: DimensionAssessment[] = [];

    // 评估每个质量维度
    for (const metric of this.metrics) {
      const assessment = await this.assessDimension(projectPath, metric);
      dimensions.push(assessment);
    }

    // 计算总体得分
    const overallScore = this.calculateOverallScore(dimensions);

    // 确定等级
    const grade = this.determineGrade(overallScore);

    // 生成建议
    const recommendations = await this.generateRecommendations(dimensions);

    return {
      overallScore,
      grade,
      dimensions,
      recommendations,
      timestamp: Date.now()
    };
  }

  private async assessDimension(
    projectPath: string,
    metric: QualityMetric
  ): Promise<DimensionAssessment> {
    const measuredValue = await this.measureMetric(projectPath, metric);
    const grade = this.determineDimensionGrade(measuredValue, metric.threshold);
    const issues = await this.identifyIssues(projectPath, metric);

    return {
      dimension: metric.dimension,
      score: measuredValue,
      grade,
      details: {
        measuredValue,
        threshold: metric.threshold,
        issues
      }
    };
  }

  private async measureMetric(
    projectPath: string,
    metric: QualityMetric
  ): Promise<number> {
    switch (metric.dimension) {
      case 'correctness':
        return this.measureTypeSafety(projectPath);
      case 'reliability':
        return this.measureTestCoverage(projectPath);
      case 'efficiency':
        return this.measurePerformance(projectPath);
      case 'maintainability':
        return this.measureComplexity(projectPath);
      case 'readability':
        return this.measureCodeStyle(projectPath);
      case 'security':
        return this.measureSecurity(projectPath);
      case 'testability':
        return this.measureTestDesign(projectPath);
      case 'consistency':
        return this.measureConsistency(projectPath);
      default:
        return 0.5; // 默认中等分数
    }
  }

  private async measureTypeSafety(projectPath: string): Promise<number> {
    try {
      // 使用TypeScript API计算类型覆盖率
      const TypeScriptMetrics = require('./typescript-metrics').TypeScriptMetrics;
      const tsMetrics = new TypeScriptMetrics(projectPath);

      const typeCoverage = await tsMetrics.getTypeCoverage();
      return typeCoverage / 100; // 转换为0-1范围
    } catch (error) {
      console.error('Failed to measure type safety:', error);
      return 0.8; // 默认分数
    }
  }

  private async measureTestCoverage(projectPath: string): Promise<number> {
    try {
      // 使用Istanbul/NYC计算测试覆盖率
      const { execSync } = require('child_process');
      const coverageReport = JSON.parse(
        execSync('npx nyc report --reporter=json --report-dir coverage', {
          cwd: projectPath,
          encoding: 'utf8'
        })
      );

      const totalCoverage = coverageReport.total.statements.pct;
      return totalCoverage / 100;
    } catch (error) {
      console.error('Failed to measure test coverage:', error);
      return 0.7; // 默认分数
    }
  }

  private async measurePerformance(projectPath: string): Promise<number> {
    try {
      // 使用Lighthouse测量性能
      const { execSync } = require('child_process');
      const lighthouseReport = JSON.parse(
        execSync('npx lighthouse --output=json --output-path=lighthouse-report.json', {
          cwd: projectPath,
          encoding: 'utf8'
        })
      );

      const performanceScore = lighthouseReport.categories.performance.score;
      return performanceScore;
    } catch (error) {
      console.error('Failed to measure performance:', error);
      return 0.7; // 默认分数
    }
  }

  private async measureComplexity(projectPath: string): Promise<number> {
    try {
      // 使用ESLint complexity规则
      const { ESLint } = require('eslint');
      const eslint = new ESLint({
        cwd: projectPath,
        useEslintrc: true,
        extensions: ['.ts', '.tsx', '.js', '.jsx']
      });

      const results = await eslint.lintFiles(['src/**/*.{ts,tsx,js,jsx}']);
      const complexityIssues = results.flatMap(result =>
        result.messages.filter(msg => msg.ruleId === 'complexity')
      );

      // 计算复杂度分数（复杂度越低分数越高）
      const totalFiles = results.length;
      const filesWithHighComplexity = complexityIssues.filter(
        msg => msg.message.includes('is too complex')
      ).length;

      const score = Math.max(0, 1 - (filesWithHighComplexity / totalFiles));
      return score;
    } catch (error) {
      console.error('Failed to measure complexity:', error);
      return 0.7; // 默认分数
    }
  }

  private async measureCodeStyle(projectPath: string): Promise<number> {
    try {
      // 使用Prettier和ESLint检查代码风格
      const { execSync } = require('child_process');
      const styleReport = execSync('npx eslint --format=json src/**/*.{ts,tsx,js,jsx}', {
        cwd: projectPath,
        encoding: 'utf8'
      });

      const issues = JSON.parse(styleReport);
      const totalFiles = issues.length;
      const filesWithStyleIssues = issues.filter((file: any) => file.messages.length > 0).length;

      const score = Math.max(0, 1 - (filesWithStyleIssues / totalFiles));
      return score;
    } catch (error) {
      console.error('Failed to measure code style:', error);
      return 0.8; // 默认分数
    }
  }

  private async measureSecurity(projectPath: string): Promise<number> {
    try {
      // 使用ESLint安全插件
      const { ESLint } = require('eslint');
      const eslint = new ESLint({
        cwd: projectPath,
        useEslintrc: true,
        extensions: ['.ts', '.tsx', '.js', '.jsx']
      });

      const results = await eslint.lintFiles(['src/**/*.{ts,tsx,js,jsx}']);
      const securityIssues = results.flatMap(result =>
        result.messages.filter(msg => msg.ruleId?.includes('security'))
      );

      const totalFiles = results.length;
      const filesWithSecurityIssues = new Set(
        securityIssues.map(issue => issue.filePath)
      ).size;

      const score = Math.max(0, 1 - (filesWithSecurityIssues / totalFiles));
      return score;
    } catch (error) {
      console.error('Failed to measure security:', error);
      return 0.8; // 默认分数
    }
  }

  private async measureTestDesign(projectPath: string): Promise<number> {
    try {
      // 分析测试文件结构
      const fs = require('fs');
      const path = require('path');

      const testFiles = this.findTestFiles(projectPath);
      const testStructureScore = this.analyzeTestStructure(testFiles);

      return testStructureScore;
    } catch (error) {
      console.error('Failed to measure test design:', error);
      return 0.7; // 默认分数
    }
  }

  private async measureConsistency(projectPath: string): Promise<number> {
    // 简化的一致性测量
    return 0.8; // 默认分数
  }

  private findTestFiles(projectPath: string): string[] {
    const fs = require('fs');
    const path = require('path');
    const testFiles: string[] = [];

    const searchDir = (dir: string): void => {
      const files = fs.readdirSync(dir);

      for (const file of files) {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);

        if (stats.isDirectory()) {
          if (!file.includes('node_modules') && !file.startsWith('.')) {
            searchDir(filePath);
          }
        } else if (
          file.includes('.test.') ||
          file.includes('.spec.') ||
          file.endsWith('.test.ts') ||
          file.endsWith('.test.tsx') ||
          file.endsWith('.spec.ts') ||
          file.endsWith('.spec.tsx')
        ) {
          testFiles.push(filePath);
        }
      }
    };

    searchDir(projectPath);
    return testFiles;
  }

  private analyzeTestStructure(testFiles: string[]): number {
    // 简化的测试结构分析
    let score = 0.5; // 基础分数

    // 检查测试文件数量与源代码文件的比例
    if (testFiles.length > 10) {
      score += 0.2;
    }

    // 检查测试文件命名规范
    const properlyNamedFiles = testFiles.filter(file =>
      file.includes('.test.') || file.includes('.spec.')
    );
    if (properlyNamedFiles.length === testFiles.length) {
      score += 0.2;
    }

    // 检查测试文件组织结构
    const hasTestDirectory = testFiles.some(file => file.includes('__tests__'));
    if (hasTestDirectory) {
      score += 0.1;
    }

    return Math.min(1, score);
  }

  private determineDimensionGrade(
    measuredValue: number,
    threshold: QualityMetric['threshold']
  ): 'excellent' | 'good' | 'acceptable' | 'poor' {
    if (measuredValue >= threshold.excellent) {
      return 'excellent';
    } else if (measuredValue >= threshold.good) {
      return 'good';
    } else if (measuredValue >= threshold.acceptable) {
      return 'acceptable';
    } else {
      return 'poor';
    }
  }

  private async identifyIssues(
    projectPath: string,
    metric: QualityMetric
  ): Promise<QualityIssue[]> {
    // 简化的问题识别
    return [];
  }

  private calculateOverallScore(dimensions: DimensionAssessment[]): number {
    let weightedSum = 0;
    let totalWeight = 0;

    dimensions.forEach(dimension => {
      const metric = this.metrics.find(m => m.dimension === dimension.dimension);
      if (metric) {
        weightedSum += dimension.score * metric.weight;
        totalWeight += metric.weight;
      }
    });

    return totalWeight > 0 ? weightedSum / totalWeight : 0;
  }

  private determineGrade(overallScore: number): 'A+' | 'A' | 'B' | 'C' | 'D' | 'F' {
    if (overallScore >= 0.95) return 'A+';
    if (overallScore >= 0.90) return 'A';
    if (overallScore >= 0.80) return 'B';
    if (overallScore >= 0.70) return 'C';
    if (overallScore >= 0.60) return 'D';
    return 'F';
  }

  private async generateRecommendations(
    dimensions: DimensionAssessment[]
  ): Promise<QualityRecommendation[]> {
    const recommendations: QualityRecommendation[] = [];

    dimensions.forEach(dimension => {
      if (dimension.grade === 'poor' || dimension.grade === 'acceptable') {
        const recommendation = this.generateDimensionRecommendation(dimension);
        recommendations.push(recommendation);
      }
    });

    return recommendations;
  }

  private generateDimensionRecommendation(
    dimension: DimensionAssessment
  ): QualityRecommendation {
    const baseRecommendation = this.getBaseRecommendation(dimension.dimension);

    return {
      priority: dimension.grade === 'poor' ? 'high' : 'medium',
      category: dimension.dimension,
      title: baseRecommendation.title,
      description: baseRecommendation.description,
      actions: baseRecommendation.actions,
      impact: baseRecommendation.impact,
      effort: baseRecommendation.effort
    };
  }

  private getBaseRecommendation(dimension: QualityDimension): {
    title: string;
    description: string;
    actions: string[];
    impact: string;
    effort: 'low' | 'medium' | 'high';
  } {
    const recommendations: Record<QualityDimension, any> = {
      correctness: {
        title: 'Improve Type Safety',
        description: 'Enhance TypeScript type coverage and type safety',
        actions: [
          'Add explicit type annotations',
          'Enable strict TypeScript mode',
          'Use proper type guards',
          'Improve type inference'
        ],
        impact: 'Reduces runtime errors and improves developer experience',
        effort: 'medium'
      },
      reliability: {
        title: 'Increase Test Coverage',
        description: 'Improve test coverage to ensure code reliability',
        actions: [
          'Add unit tests for uncovered code',
          'Implement integration tests',
          'Add edge case testing',
          'Improve test data generation'
        ],
        impact: 'Reduces bugs and improves code stability',
        effort: 'high'
      },
      efficiency: {
        title: 'Optimize Performance',
        description: 'Improve code performance and resource usage',
        actions: [
          'Profile and optimize slow functions',
          'Implement memoization where appropriate',
          'Optimize database queries',
          'Use efficient data structures'
        ],
        impact: 'Improves user experience and reduces costs',
        effort: 'high'
      },
      maintainability: {
        title: 'Reduce Code Complexity',
        description: 'Simplify complex code to improve maintainability',
        actions: [
          'Break down large functions',
          'Extract reusable components',
          'Simplify conditional logic',
          'Improve code organization'
        ],
        impact: 'Makes code easier to understand and modify',
        effort: 'medium'
      },
      readability: {
        title: 'Standardize Code Style',
        description: 'Ensure consistent code style across the project',
        actions: [
          'Configure and enforce ESLint rules',
          'Use Prettier for code formatting',
          'Establish naming conventions',
          'Improve code documentation'
        ],
        impact: 'Improves code readability and team productivity',
        effort: 'low'
      },
      security: {
        title: 'Address Security Issues',
        description: 'Fix security vulnerabilities and improve security practices',
        actions: [
          'Fix identified security issues',
          'Implement proper input validation',
          'Use secure coding practices',
          'Regular security audits'
        ],
        impact: 'Prevents security breaches and data leaks',
        effort: 'high'
      },
      testability: {
        title: 'Improve Test Design',
        description: 'Enhance test structure and design patterns',
        actions: [
          'Follow test-driven development',
          'Use proper test organization',
          'Improve test data management',
          'Add property-based testing'
        ],
        impact: 'Improves test coverage and reduces bugs',
        effort: 'medium'
      },
      consistency: {
        title: 'Ensure Code Consistency',
        description: 'Maintain consistent code patterns and architecture',
        actions: [
          'Establish architectural patterns',
          'Use consistent error handling',
          'Standardize API responses',
          'Maintain consistent data models'
        ],
        impact: 'Improves code maintainability and team efficiency',
        effort: 'medium'
      }
    };

    return recommendations[dimension];
  }
}
```

## 🚀 静态代码分析

### 1. ESLint 高级配置

```typescript
// eslint.config.ts
import { ESLint } from 'eslint';
import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat();

export default [
  // 基础配置
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parser: '@typescript-eslint/parser',
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: __dirname,
        ecmaFeatures: {
          jsx: true
        }
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021
      }
    },
    plugins: [
      '@typescript-eslint',
      'react',
      'react-hooks',
      'import',
      'promise',
      'unicorn',
      'security',
      'sonarjs'
    ],
    settings: {
      react: {
        version: 'detect'
      },
      'import/resolver': {
        typescript: {
          alwaysTryTypes: true,
          project: './tsconfig.json'
        }
      }
    },
    rules: {
      // TypeScript 规则
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'error',
      '@typescript-eslint/explicit-module-boundary-types': 'error',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/no-floating-promises': 'error',

      // React 规则
      'react/react-in-jsx-scope': 'off',
      'react/jsx-uses-react': 'off',
      'react/prop-types': 'off',
      'react/jsx-key': 'error',
      'react/jsx-no-undef': 'error',
      'react/jsx-pascal-case': 'error',
      'react/no-unescaped-entities': 'warn',
      'react/display-name': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',

      // 导入规则
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      'import/namespace': 'error',
      'import/export': 'error',
      'import/no-duplicates': 'error',
      'import/order': ['error', {
        'groups': [
          'builtin',
          'external',
          'internal',
          'parent',
          'sibling',
          'index'
        ],
        'newlines-between': 'always'
      }],

      // Promise 规则
      'promise/always-return': 'error',
      'promise/no-return-wrap': 'error',
      'promise/param-names': 'error',
      'promise/catch-or-return': 'error',
      'promise/no-native': 'off',

      // Unicorn 规则
      'unicorn/filename-case': ['error', { case: 'kebabCase' }],
      'unicorn/no-abusive-eslint-disable': 'error',
      'unicorn/prevent-abbreviations': 'warn',
      'unicorn/no-array-for-each': 'warn',
      'unicorn/no-array-push-push': 'warn',
      'unicorn/prefer-node-protocol': 'error',

      // 安全规则
      'security/detect-object-injection': 'warn',
      'security/detect-non-literal-fs-filename': 'warn',
      'security/detect-non-literal-regexp': 'warn',
      'security/detect-possible-timing-attacks': 'warn',

      // SonarJS 规则
      'sonarjs/cognitive-complexity': ['error', { threshold: 15 }],
      'sonarjs/no-duplicate-string': 'warn',
      'sonarjs/no-identical-functions': 'warn',
      'sonarjs/no-collapsible-if': 'error',
      'sonarjs/prefer-immediate-return': 'error',

      // 通用规则
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': 'error',
      'no-var': 'error',
      'prefer-const': 'error',
      'prefer-arrow-callback': 'error',
      'arrow-spacing': 'error',
      'object-shorthand': 'error',
      'prefer-template': 'error',
      'template-curly-spacing': 'error',
      'eqeqeq': ['error', 'always'],
      'no-eval': 'error',
      'no-implied-eval': 'error',
      'no-new-func': 'error',
      'no-throw-literal': 'error',
      'no-unneeded-ternary': 'error',
      'prefer-object-spread': 'error'
    }
  },

  // 测试文件特殊配置
  {
    files: ['**/*.test.{js,jsx,ts,tsx}', '**/*.spec.{js,jsx,ts,tsx}'],
    languageOptions: {
      globals: {
        ...globals.jest,
        ...globals.vitest
      }
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
      'no-console': 'off',
      'sonarjs/no-duplicate-string': 'off'
    }
  },

  // 配置文件特殊配置
  {
    files: [
      '**/*.config.{js,ts}',
      '**/*.config.{mjs,cjs}',
      'eslint.config.{js,ts}'
    ],
    languageOptions: {
      sourceType: 'commonjs'
    },
    rules: {
      '@typescript-eslint/no-var-requires': 'off',
      'import/no-commonjs': 'off'
    }
  },

  // 忽略文件
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      '.next/**',
      'coverage/**',
      '*.min.js',
      'public/**'
    ]
  }
];
```

### 2. 自定义 ESLint 插件

```typescript
// eslint-plugin-custom-rules.ts
import { Rule } from 'eslint';

export const customRules = {
  // 检查未优化的 React 组件
  'react-optimized-component': {
    meta: {
      type: 'suggestion',
      docs: {
        description: 'Enforce React component optimization patterns',
        recommended: true,
        category: 'React',
        url: 'https://github.com/your-org/eslint-plugin-react-rules'
      },
      schema: [
        {
          type: 'object',
          properties: {
            maxComplexity: {
              type: 'number',
              minimum: 1,
              default: 10
            },
            requireMemo: {
              type: 'boolean',
              default: true
            }
          },
          additionalProperties: false
        }
      ]
    },
    create(context: Rule.RuleContext) {
      const options = context.options[0] || {};
      const maxComplexity = options.maxComplexity || 10;
      const requireMemo = options.requireMemo !== false;

      let complexity = 0;
      const functionStack: { name: string; complexity: number }[] = [];

      return {
        FunctionDeclaration(node) {
          functionStack.push({ name: node.id?.name || 'anonymous', complexity: 0 });
        },
        FunctionExpression(node) {
          const name = node.parent?.type === 'VariableDeclarator'
            ? (node.parent as any).id.name
            : 'anonymous';
          functionStack.push({ name, complexity: 0 });
        },
        ArrowFunctionExpression(node) {
          const name = node.parent?.type === 'VariableDeclarator'
            ? (node.parent as any).id.name
            : 'anonymous';
          functionStack.push({ name, complexity: 0 });
        },
        'FunctionDeclaration:exit'(node) {
          const func = functionStack.pop();
          if (func && func.complexity > maxComplexity) {
            context.report({
              node,
              message: `Function '${func.name}' has complexity ${func.complexity} which exceeds the maximum of ${maxComplexity}. Consider breaking it down.`
            });
          }
        },
        'FunctionExpression:exit'(node) {
          const func = functionStack.pop();
          if (func && func.complexity > maxComplexity) {
            context.report({
              node,
              message: `Function '${func.name}' has complexity ${func.complexity} which exceeds the maximum of ${maxComplexity}. Consider breaking it down.`
            });
          }
        },
        'ArrowFunctionExpression:exit'(node) {
          const func = functionStack.pop();
          if (func && func.complexity > maxComplexity) {
            context.report({
              node,
              message: `Arrow function '${func.name}' has complexity ${func.complexity} which exceeds the maximum of ${maxComplexity}. Consider breaking it down.`
            });
          }
        },
        IfStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        SwitchStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        ForStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        ForInStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        ForOfStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        WhileStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        DoWhileStatement() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        ConditionalExpression() {
          if (functionStack.length > 0) {
            functionStack[functionStack.length - 1].complexity++;
          }
        },
        LogicalExpression(node) {
          if (node.operator === '&&' || node.operator === '||') {
            if (functionStack.length > 0) {
              functionStack[functionStack.length - 1].complexity++;
            }
          }
        },
        // React 特定规则
        CallExpression(node) {
          const callee = node.callee;

          // 检查 useState 的使用
          if (
            callee.type === 'Identifier' &&
            callee.name === 'useState' &&
            functionStack.length > 0
          ) {
            const func = functionStack[functionStack.length - 1];

            // 如果函数复杂度较高，建议使用 useReducer
            if (func.complexity > 15) {
              context.report({
                node,
                message: `Consider using useReducer instead of multiple useState calls in complex function '${func.name}' with complexity ${func.complexity}.`
              });
            }
          }

          // 检查 useCallback 的使用
          if (
            callee.type === 'Identifier' &&
            callee.name === 'useCallback' &&
            requireMemo
          ) {
            // 检查是否传递了正确的依赖数组
            const args = node.arguments;
            if (args.length >= 2 && args[1].type === 'ArrayExpression') {
              const deps = args[1].elements;

              // 检查是否有空的依赖数组
              if (deps.length === 0) {
                const firstArg = args[0];
                if (firstArg.type === 'ArrowFunctionExpression') {
                  // 检查函数体是否使用了外部变量
                  const usesExternalVars = this.usesExternalVariables(firstArg);
                  if (usesExternalVars) {
                    context.report({
                      node: args[1],
                      message: 'Empty dependency array but function uses external variables. This may cause stale closures.'
                    });
                  }
                }
              }
            }
          }
        },
        VariableDeclarator(node) {
          if (
            node.init?.type === 'CallExpression' &&
            node.init.callee.type === 'Identifier' &&
            ['useState', 'useEffect', 'useContext'].includes(node.init.callee.name)
          ) {
            // 检查 Hook 的命名规则
            if (node.id.type === 'Identifier') {
              const name = node.id.name;
              if (!name.startsWith('use')) {
                context.report({
                  node: node.id,
                  message: `Hook variable '${name}' should start with 'use' prefix.`
                });
              }
            }
          }
        }
      };
    }
  } as Rule.RuleModule,

  // 检查 TypeScript 类型定义
  'typescript-explicit-types': {
    meta: {
      type: 'suggestion',
      docs: {
        description: 'Enforce explicit TypeScript types in function parameters and return types',
        recommended: true
      },
      schema: [
        {
          type: 'object',
          properties: {
            allowImplicitAny: {
              type: 'boolean',
              default: false
            },
            requireReturnTypes: {
              type: 'boolean',
              default: true
            }
          },
          additionalProperties: false
        }
      ]
    },
    create(context: Rule.RuleContext) {
      const options = context.options[0] || {};
      const allowImplicitAny = options.allowImplicitAny || false;
      const requireReturnTypes = options.requireReturnTypes !== false;

      return {
        FunctionDeclaration(node) {
          checkFunctionNode(node, node.id?.name || 'anonymous');
        },
        FunctionExpression(node) {
          const name = node.parent?.type === 'VariableDeclarator'
            ? (node.parent as any).id.name
            : 'anonymous';
          checkFunctionNode(node, name);
        },
        ArrowFunctionExpression(node) {
          const name = node.parent?.type === 'VariableDeclarator'
            ? (node.parent as any).id.name
            : 'anonymous';
          checkFunctionNode(node, name);
        }
      };

      function checkFunctionNode(node: any, name: string) {
        // 检查参数类型
        if (node.params) {
          node.params.forEach((param: any) => {
            if (param.type === 'Identifier' && !param.typeAnnotation) {
              if (!allowImplicitAny) {
                context.report({
                  node: param,
                  message: `Parameter '${param.name}' should have an explicit type annotation.`
                });
              }
            }
          });
        }

        // 检查返回类型
        if (requireReturnTypes && !node.returnType) {
          // 排除一些特殊情况
          if (!shouldSkipReturnTypeCheck(node)) {
            context.report({
              node,
              message: `Function '${name}' should have an explicit return type annotation.`
            });
          }
        }
      }

      function shouldSkipReturnTypeCheck(node: any): boolean {
        // 跳过 React 组件的返回类型检查
        if (node.parent?.type === 'VariableDeclarator') {
          const init = node.parent.init;
          if (init === node) {
            // 检查是否是 React 组件
            if (hasJSXElement(node.body)) {
              return true;
            }
          }
        }
        return false;
      }

      function hasJSXElement(node: any): boolean {
        if (!node || typeof node !== 'object') return false;

        if (node.type === 'JSXElement' || node.type === 'JSXFragment') {
          return true;
        }

        if (node.type === 'BlockStatement') {
          return node.body.some((stmt: any) => hasJSXElement(stmt));
        }

        if (node.type === 'ReturnStatement') {
          return hasJSXElement(node.argument);
        }

        return false;
      }
    }
  } as Rule.RuleModule
};

function usesExternalVariables(node: any): boolean {
  // 简化的外部变量检查
  return false;
}
```

## 🎨 代码质量门禁

### 1. 质量门禁配置

```typescript
// lib/quality-gate.ts
import { QualityAssessment, QualityDimension } from '@/types/code-quality-types';

export interface QualityGateConfig {
  overall: {
    minimumScore: number;
    blocking: boolean;
  };
  dimensions: Record<QualityDimension, {
    minimumScore: number;
    blocking: boolean;
    warningThreshold: number;
  }>;
  customRules: QualityGateRule[];
}

export interface QualityGateRule {
  name: string;
  description: string;
  condition: {
    metric: string;
    operator: 'gt' | 'lt' | 'eq' | 'ne';
    threshold: number;
  };
  severity: 'blocker' | 'critical' | 'major' | 'minor';
  action: 'fail' | 'warn' | 'skip';
}

export interface QualityGateResult {
  passed: boolean;
  blocked: boolean;
  overall: {
    score: number;
    grade: string;
    passed: boolean;
  };
  dimensions: Record<QualityDimension, {
    score: number;
    passed: boolean;
    blocked: boolean;
    warnings: string[];
  }>;
  violations: QualityGateViolation[];
  recommendations: string[];
}

export interface QualityGateViolation {
  rule: string;
  severity: 'blocker' | 'critical' | 'major' | 'minor';
  description: string;
  metric: string;
  actual: number;
  expected: number;
  action: 'fail' | 'warn' | 'skip';
}

export class QualityGate {
  private config: QualityGateConfig;

  constructor(config: QualityGateConfig) {
    this.config = config;
  }

  async evaluate(assessment: QualityAssessment): Promise<QualityGateResult> {
    const violations: QualityGateViolation[] = [];
    const recommendations: string[] = [];
    let blocked = false;

    // 评估总体质量
    const overallPassed = assessment.overallScore >= this.config.overall.minimumScore;
    const overallBlocked = !overallPassed && this.config.overall.blocking;

    if (overallBlocked) {
      blocked = true;
      violations.push({
        rule: 'overall_quality',
        severity: 'blocker',
        description: `Overall quality score ${assessment.overallScore} is below minimum threshold ${this.config.overall.minimumScore}`,
        metric: 'overall_score',
        actual: assessment.overallScore,
        expected: this.config.overall.minimumScore,
        action: 'fail'
      });
    }

    // 评估各个维度
    const dimensionResults: Record<QualityDimension, any> = {};

    assessment.dimensions.forEach(dimension => {
      const config = this.config.dimensions[dimension.dimension];
      const passed = dimension.score >= config.minimumScore;
      const blocked = !passed && config.blocking;

      if (blocked) {
        this.blocked = true;
        violations.push({
          rule: `${dimension.dimension}_quality`,
          severity: 'blocker',
          description: `${dimension.dimension} score ${dimension.score} is below minimum threshold ${config.minimumScore}`,
          metric: `${dimension.dimension}_score`,
          actual: dimension.score,
          expected: config.minimumScore,
          action: 'fail'
        });
      }

      const warnings: string[] = [];
      if (dimension.score < config.warningThreshold) {
        warnings.push(`${dimension.dimension} score is approaching threshold`);
      }

      dimensionResults[dimension.dimension] = {
        score: dimension.score,
        passed,
        blocked,
        warnings
      };
    });

    // 评估自定义规则
    for (const rule of this.config.customRules) {
      const metricValue = this.getMetricValue(assessment, rule.condition.metric);

      if (this.evaluateCondition(rule.condition, metricValue)) {
        violations.push({
          rule: rule.name,
          severity: rule.severity,
          description: rule.description,
          metric: rule.condition.metric,
          actual: metricValue,
          expected: rule.condition.threshold,
          action: rule.action
        });

        if (rule.action === 'fail' && rule.severity === 'blocker') {
          blocked = true;
        }
      }
    }

    // 生成建议
    violations.forEach(violation => {
      recommendations.push(this.generateRecommendation(violation));
    });

    return {
      passed: violations.filter(v => v.action === 'fail').length === 0,
      blocked,
      overall: {
        score: assessment.overallScore,
        grade: assessment.grade,
        passed: overallPassed
      },
      dimensions: dimensionResults,
      violations,
      recommendations
    };
  }

  private getMetricValue(assessment: QualityAssessment, metric: string): number {
    // 从评估结果中提取指标值
    switch (metric) {
      case 'overall_score':
        return assessment.overallScore;
      case 'test_coverage':
        const testDimension = assessment.dimensions.find(d => d.dimension === 'reliability');
        return testDimension?.score || 0;
      case 'type_safety':
        const typeDimension = assessment.dimensions.find(d => d.dimension === 'correctness');
        return typeDimension?.score || 0;
      case 'complexity':
        const complexityDimension = assessment.dimensions.find(d => d.dimension === 'maintainability');
        return complexityDimension?.score || 0;
      default:
        return 0;
    }
  }

  private evaluateCondition(condition: any, value: number): boolean {
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

  private generateRecommendation(violation: QualityGateViolation): string {
    const recommendations: Record<string, string> = {
      overall_quality: 'Review overall code quality and address major issues across all dimensions',
      test_coverage: 'Increase test coverage by writing more comprehensive tests',
      type_safety: 'Improve TypeScript type annotations and enable strict mode',
      complexity: 'Refactor complex functions to improve maintainability',
      security: 'Address security vulnerabilities and implement secure coding practices',
      performance: 'Optimize performance bottlenecks and improve resource usage'
    };

    return recommendations[violation.metric] || 'Review the violated quality gate rule and take corrective action';
  }

  // 预设的质量门禁配置
  static getStrictConfig(): QualityGateConfig {
    return {
      overall: {
        minimumScore: 0.90,
        blocking: true
      },
      dimensions: {
        correctness: {
          minimumScore: 0.95,
          blocking: true,
          warningThreshold: 0.98
        },
        reliability: {
          minimumScore: 0.90,
          blocking: true,
          warningThreshold: 0.95
        },
        efficiency: {
          minimumScore: 0.85,
          blocking: false,
          warningThreshold: 0.90
        },
        maintainability: {
          minimumScore: 0.80,
          blocking: false,
          warningThreshold: 0.85
        },
        readability: {
          minimumScore: 0.90,
          blocking: false,
          warningThreshold: 0.95
        },
        security: {
          minimumScore: 0.95,
          blocking: true,
          warningThreshold: 0.98
        },
        testability: {
          minimumScore: 0.85,
          blocking: false,
          warningThreshold: 0.90
        },
        consistency: {
          minimumScore: 0.85,
          blocking: false,
          warningThreshold: 0.90
        }
      },
      customRules: [
        {
          name: 'no_critical_security_issues',
          description: 'No critical security vulnerabilities allowed',
          condition: {
            metric: 'security',
            operator: 'lt',
            threshold: 0.95
          },
          severity: 'blocker',
          action: 'fail'
        }
      ]
    };
  }

  static getModerateConfig(): QualityGateConfig {
    return {
      overall: {
        minimumScore: 0.80,
        blocking: true
      },
      dimensions: {
        correctness: {
          minimumScore: 0.85,
          blocking: true,
          warningThreshold: 0.90
        },
        reliability: {
          minimumScore: 0.80,
          blocking: true,
          warningThreshold: 0.85
        },
        efficiency: {
          minimumScore: 0.75,
          blocking: false,
          warningThreshold: 0.80
        },
        maintainability: {
          minimumScore: 0.70,
          blocking: false,
          warningThreshold: 0.75
        },
        readability: {
          minimumScore: 0.80,
          blocking: false,
          warningThreshold: 0.85
        },
        security: {
          minimumScore: 0.85,
          blocking: true,
          warningThreshold: 0.90
        },
        testability: {
          minimumScore: 0.75,
          blocking: false,
          warningThreshold: 0.80
        },
        consistency: {
          minimumScore: 0.75,
          blocking: false,
          warningThreshold: 0.80
        }
      },
      customRules: []
    };
  }

  static getLenientConfig(): QualityGateConfig {
    return {
      overall: {
        minimumScore: 0.70,
        blocking: false
      },
      dimensions: {
        correctness: {
          minimumScore: 0.75,
          blocking: false,
          warningThreshold: 0.80
        },
        reliability: {
          minimumScore: 0.70,
          blocking: false,
          warningThreshold: 0.75
        },
        efficiency: {
          minimumScore: 0.65,
          blocking: false,
          warningThreshold: 0.70
        },
        maintainability: {
          minimumScore: 0.60,
          blocking: false,
          warningThreshold: 0.65
        },
        readability: {
          minimumScore: 0.70,
          blocking: false,
          warningThreshold: 0.75
        },
        security: {
          minimumScore: 0.75,
          blocking: false,
          warningThreshold: 0.80
        },
        testability: {
          minimumScore: 0.65,
          blocking: false,
          warningThreshold: 0.70
        },
        consistency: {
          minimumScore: 0.65,
          blocking: false,
          warningThreshold: 0.70
        }
      },
      customRules: []
    };
  }
}
```

### 2. 质量趋势分析

```typescript
// lib/quality-trends.ts
export interface QualityTrendAnalysis {
  project: string;
  period: {
    start: Date;
    end: Date;
  };
  overallTrend: TrendData;
  dimensionTrends: Record<QualityDimension, TrendData>;
  insights: TrendInsight[];
  recommendations: string[];
}

export interface TrendData {
  scores: number[];
  trend: 'improving' | 'declining' | 'stable';
  changeRate: number;
  volatility: number;
  prediction?: number;
}

export interface TrendInsight {
  type: 'improvement' | 'decline' | 'anomaly' | 'stability';
  dimension: QualityDimension;
  description: string;
  severity: 'low' | 'medium' | 'high';
  timeframe: string;
  dataPoints: Array<{
    date: Date;
    value: number;
  }>;
}

export class QualityTrendAnalyzer {
  private assessments: QualityAssessment[];

  constructor(assessments: QualityAssessment[]) {
    this.assessments = assessments.sort((a, b) => a.timestamp - b.timestamp);
  }

  analyzeTrends(period: { start: Date; end: Date } = {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date()
  }): QualityTrendAnalysis {
    // 过滤指定时间段的评估
    const filteredAssessments = this.assessments.filter(
      assessment => assessment.timestamp >= period.start.getTime() &&
                 assessment.timestamp <= period.end.getTime()
    );

    // 分析总体趋势
    const overallTrend = this.analyzeTrend(
      filteredAssessments.map(a => a.overallScore)
    );

    // 分析各维度趋势
    const dimensionTrends: Record<QualityDimension, TrendData> = {} as any;

    const dimensions: QualityDimension[] = [
      'correctness', 'reliability', 'efficiency', 'maintainability',
      'readability', 'security', 'testability', 'consistency'
    ];

    dimensions.forEach(dimension => {
      const scores = filteredAssessments.map(assessment => {
        const dimAssessment = assessment.dimensions.find(d => d.dimension === dimension);
        return dimAssessment?.score || 0;
      });

      dimensionTrends[dimension] = this.analyzeTrend(scores);
    });

    // 生成洞察
    const insights = this.generateInsights(filteredAssessments, dimensionTrends);

    // 生成建议
    const recommendations = this.generateRecommendations(insights, dimensionTrends);

    return {
      project: 'Next.js Project',
      period,
      overallTrend,
      dimensionTrends,
      insights,
      recommendations
    };
  }

  private analyzeTrend(scores: number[]): TrendData {
    if (scores.length < 2) {
      return {
        scores,
        trend: 'stable',
        changeRate: 0,
        volatility: 0
      };
    }

    // 计算变化率
    const firstScore = scores[0];
    const lastScore = scores[scores.length - 1];
    const changeRate = (lastScore - firstScore) / firstScore;

    // 确定趋势
    let trend: 'improving' | 'declining' | 'stable';
    if (Math.abs(changeRate) < 0.05) {
      trend = 'stable';
    } else if (changeRate > 0) {
      trend = 'improving';
    } else {
      trend = 'declining';
    }

    // 计算波动性
    const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length;
    const volatility = Math.sqrt(variance);

    // 简单预测（线性外推）
    let prediction: number | undefined;
    if (scores.length >= 3) {
      const recentTrend = this.calculateLinearTrend(scores.slice(-3));
      prediction = lastScore + recentTrend;
    }

    return {
      scores,
      trend,
      changeRate,
      volatility,
      prediction
    };
  }

  private calculateLinearTrend(scores: number[]): number {
    if (scores.length < 2) return 0;

    const n = scores.length;
    const sumX = (n * (n - 1)) / 2;
    const sumY = scores.reduce((sum, y) => sum + y, 0);
    const sumXY = scores.reduce((sum, y, x) => sum + x * y, 0);
    const sumX2 = (n * (n - 1) * (2 * n - 1)) / 6;

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    return slope;
  }

  private generateInsights(
    assessments: QualityAssessment[],
    dimensionTrends: Record<QualityDimension, TrendData>
  ): TrendInsight[] {
    const insights: TrendInsight[] = [];

    // 检查显著变化
    Object.entries(dimensionTrends).forEach(([dimension, trend]) => {
      if (Math.abs(trend.changeRate) > 0.1) { // 10%以上变化
        insights.push({
          type: trend.changeRate > 0 ? 'improvement' : 'decline',
          dimension: dimension as QualityDimension,
          description: `${dimension} quality has ${trend.changeRate > 0 ? 'improved' : 'declined'} by ${(Math.abs(trend.changeRate) * 100).toFixed(1)}%`,
          severity: Math.abs(trend.changeRate) > 0.2 ? 'high' : 'medium',
          timeframe: 'last 30 days',
          dataPoints: assessments.map(a => ({
            date: new Date(a.timestamp),
            value: dimensionTrends[dimension as QualityDimension]?.scores[
              assessments.indexOf(a)
            ] || 0
          }))
        });
      }

      // 检查异常值
      if (trend.volatility > 0.1) {
        insights.push({
          type: 'anomaly',
          dimension: dimension as QualityDimension,
          description: `High volatility detected in ${dimension} quality (volatility: ${trend.volatility.toFixed(3)})`,
          severity: 'medium',
          timeframe: 'last 30 days',
          dataPoints: assessments.map(a => ({
            date: new Date(a.timestamp),
            value: dimensionTrends[dimension as QualityDimension]?.scores[
              assessments.indexOf(a)
            ] || 0
          }))
        });
      }
    });

    return insights;
  }

  private generateRecommendations(
    insights: TrendInsight[],
    dimensionTrends: Record<QualityDimension, TrendData>
  ): string[] {
    const recommendations: string[] = [];

    // 基于洞察生成建议
    insights.forEach(insight => {
      switch (insight.type) {
        case 'decline':
          recommendations.push(`Address declining ${insight.dimension} quality by investigating recent changes`);
          break;
        case 'improvement':
          recommendations.push(`Continue practices that led to ${insight.dimension} quality improvement`);
          break;
        case 'anomaly':
          recommendations.push(`Investigate high volatility in ${insight.dimension} quality metrics`);
          break;
      }
    });

    // 基于趋势生成建议
    Object.entries(dimensionTrends).forEach(([dimension, trend]) => {
      if (trend.trend === 'declining' && trend.prediction && trend.prediction < 0.7) {
        recommendations.push(`Projected ${dimension} quality decline: immediate action recommended`);
      }
    });

    return [...new Set(recommendations)]; // 去重
  }

  // 生成质量报告
  generateQualityReport(analysis: QualityTrendAnalysis): string {
    const report = [
      `# Quality Trend Analysis Report`,
      ``,
      `## Period: ${analysis.period.start.toLocaleDateString()} - ${analysis.period.end.toLocaleDateString()}`,
      ``,
      `## Overall Quality Trend`,
      `- Current Score: ${(analysis.overallTrend.scores[analysis.overallTrend.scores.length - 1] * 100).toFixed(1)}%`,
      `- Trend: ${analysis.overallTrend.trend}`,
      `- Change Rate: ${(analysis.overallTrend.changeRate * 100).toFixed(1)}%`,
      `- Volatility: ${analysis.overallTrend.volatility.toFixed(3)}`,
      `${analysis.overallTrend.prediction ? `- Projection: ${(analysis.overallTrend.prediction * 100).toFixed(1)}%` : ''}`,
      ``,
      `## Dimension Analysis`,
      ``
    ];

    Object.entries(analysis.dimensionTrends).forEach(([dimension, trend]) => {
      report.push(
        `### ${dimension}`,
        `- Score: ${(trend.scores[trend.scores.length - 1] * 100).toFixed(1)}%`,
        `- Trend: ${trend.trend}`,
        `- Change: ${(trend.changeRate * 100).toFixed(1)}%`
      );
    });

    report.push(``, `## Key Insights`, ``);
    analysis.insights.forEach(insight => {
      report.push(
        `### ${insight.type.toUpperCase()} - ${insight.dimension}`,
        `- ${insight.description}`,
        `- Severity: ${insight.severity}`,
        `- Timeframe: ${insight.timeframe}`
      );
    });

    report.push(``, `## Recommendations`, ``);
    analysis.recommendations.forEach((recommendation, index) => {
      report.push(`${index + 1}. ${recommendation}`);
    });

    return report.join('\n');
  }
}
```

## 📊 代码质量监控

### 1. 实时代码质量监控

```typescript
// lib/quality-monitor.ts
import { QualityAssessment } from '@/types/code-quality-types';

export interface QualityMonitorConfig {
  enabled: boolean;
  interval: number; // 监控间隔（毫秒）
  thresholds: {
    degradation: number; // 质量下降阈值
    improvement: number; // 质量改善阈值
  };
  notifications: {
    enabled: boolean;
    channels: NotificationChannel[];
  };
  storage: {
    type: 'local' | 'database' | 'remote';
    retention: number; // 保留天数
  };
}

export interface QualityAlert {
  id: string;
  type: 'degradation' | 'improvement' | 'threshold_breach';
  severity: 'low' | 'medium' | 'high' | 'critical';
  dimension?: QualityDimension;
  message: string;
  timestamp: number;
  data: {
    currentValue: number;
    previousValue: number;
    change: number;
  };
  resolved: boolean;
}

export interface NotificationChannel {
  type: 'email' | 'slack' | 'webhook' | 'console';
  config: Record<string, any>;
}

export class QualityMonitor {
  private config: QualityMonitorConfig;
  private assessments: QualityAssessment[] = [];
  private alerts: QualityAlert[] = [];
  private intervalId: NodeJS.Timeout | null = null;

  constructor(config: QualityMonitorConfig) {
    this.config = config;
  }

  start(): void {
    if (this.config.enabled && !this.intervalId) {
      this.intervalId = setInterval(() => {
        this.performQualityCheck();
      }, this.config.interval);

      console.log('Quality monitoring started');
    }
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('Quality monitoring stopped');
    }
  }

  addAssessment(assessment: QualityAssessment): void {
    this.assessments.push(assessment);

    // 检查质量变化
    this.checkQualityChanges(assessment);

    // 保存到存储
    this.saveAssessment(assessment);
  }

  private async performQualityCheck(): Promise<void> {
    if (this.assessments.length < 2) {
      return;
    }

    const latestAssessment = this.assessments[this.assessments.length - 1];
    const previousAssessment = this.assessments[this.assessments.length - 2];

    // 检查整体质量变化
    this.checkOverallQuality(latestAssessment, previousAssessment);

    // 检查各维度质量变化
    latestAssessment.dimensions.forEach(dimension => {
      const previousDimension = previousAssessment.dimensions.find(
        d => d.dimension === dimension.dimension
      );

      if (previousDimension) {
        this.checkDimensionQuality(dimension, previousDimension);
      }
    });
  }

  private checkQualityChanges(current: QualityAssessment): void {
    if (this.assessments.length < 2) return;

    const previous = this.assessments[this.assessments.length - 2];
    const change = current.overallScore - previous.overallScore;

    // 检查质量下降
    if (Math.abs(change) > this.config.thresholds.degradation) {
      const alert: QualityAlert = {
        id: this.generateAlertId(),
        type: change < 0 ? 'degradation' : 'improvement',
        severity: this.calculateSeverity(Math.abs(change)),
        message: `Overall quality ${change < 0 ? 'degraded' : 'improved'} by ${(Math.abs(change) * 100).toFixed(1)}%`,
        timestamp: Date.now(),
        data: {
          currentValue: current.overallScore,
          previousValue: previous.overallScore,
          change
        },
        resolved: false
      };

      this.addAlert(alert);
    }

    // 检查阈值突破
    if (current.overallScore < 0.7) {
      const alert: QualityAlert = {
        id: this.generateAlertId(),
        type: 'threshold_breach',
        severity: 'critical',
        message: `Overall quality score below acceptable threshold (${(current.overallScore * 100).toFixed(1)}%)`,
        timestamp: Date.now(),
        data: {
          currentValue: current.overallScore,
          previousValue: previous.overallScore,
          change
        },
        resolved: false
      };

      this.addAlert(alert);
    }
  }

  private checkOverallQuality(current: QualityAssessment, previous: QualityAssessment): void {
    const change = current.overallScore - previous.overallScore;

    if (Math.abs(change) > this.config.thresholds.degradation) {
      this.createAlert({
        type: change < 0 ? 'degradation' : 'improvement',
        severity: this.calculateSeverity(Math.abs(change)),
        message: `Overall quality ${change < 0 ? 'degraded' : 'improved'} by ${(Math.abs(change) * 100).toFixed(1)}%`,
        data: {
          currentValue: current.overallScore,
          previousValue: previous.overallScore,
          change
        }
      });
    }
  }

  private checkDimensionQuality(
    current: any,
    previous: any
  ): void {
    const change = current.score - previous.score;

    if (Math.abs(change) > this.config.thresholds.degradation) {
      this.createAlert({
        type: change < 0 ? 'degradation' : 'improvement',
        severity: this.calculateSeverity(Math.abs(change)),
        dimension: current.dimension,
        message: `${current.dimension} quality ${change < 0 ? 'degraded' : 'improved'} by ${(Math.abs(change) * 100).toFixed(1)}%`,
        data: {
          currentValue: current.score,
          previousValue: previous.score,
          change
        }
      });
    }
  }

  private createAlert(alertData: Omit<QualityAlert, 'id' | 'timestamp' | 'resolved'>): void {
    const alert: QualityAlert = {
      id: this.generateAlertId(),
      timestamp: Date.now(),
      resolved: false,
      ...alertData
    };

    this.addAlert(alert);
  }

  private addAlert(alert: QualityAlert): void {
    this.alerts.push(alert);

    // 发送通知
    if (this.config.notifications.enabled) {
      this.sendNotification(alert);
    }

    console.log(`Quality Alert: ${alert.message}`);
  }

  private sendNotification(alert: QualityAlert): void {
    this.config.notifications.channels.forEach(channel => {
      switch (channel.type) {
        case 'console':
          console.log(`[${alert.severity.toUpperCase()}] ${alert.message}`);
          break;
        case 'slack':
          this.sendSlackNotification(alert, channel.config);
          break;
        case 'email':
          this.sendEmailNotification(alert, channel.config);
          break;
        case 'webhook':
          this.sendWebhookNotification(alert, channel.config);
          break;
      }
    });
  }

  private sendSlackNotification(alert: QualityAlert, config: any): void {
    const payload = {
      channel: config.channel,
      text: `Quality Alert: ${alert.message}`,
      attachments: [
        {
          color: this.getSeverityColor(alert.severity),
          fields: [
            {
              title: 'Severity',
              value: alert.severity.toUpperCase(),
              short: true
            },
            {
              title: 'Type',
              value: alert.type,
              short: true
            },
            {
              title: 'Current Value',
              value: `${(alert.data.currentValue * 100).toFixed(1)}%`,
              short: true
            },
            {
              title: 'Change',
              value: `${(alert.data.change * 100).toFixed(1)}%`,
              short: true
            }
          ]
        }
      ]
    };

    // 实际发送Slack通知
    console.log('Slack notification:', payload);
  }

  private sendEmailNotification(alert: QualityAlert, config: any): void {
    const email = {
      to: config.recipients,
      subject: `[Quality Alert] ${alert.severity.toUpperCase()} - ${alert.type}`,
      text: alert.message,
      html: `
        <h2>Quality Alert</h2>
        <p><strong>Severity:</strong> ${alert.severity.toUpperCase()}</p>
        <p><strong>Type:</strong> ${alert.type}</p>
        <p><strong>Message:</strong> ${alert.message}</p>
        <p><strong>Current Value:</strong> ${(alert.data.currentValue * 100).toFixed(1)}%</p>
        <p><strong>Change:</strong> ${(alert.data.change * 100).toFixed(1)}%</p>
        <p><strong>Time:</strong> ${new Date(alert.timestamp).toLocaleString()}</p>
      `
    };

    // 实际发送邮件通知
    console.log('Email notification:', email);
  }

  private sendWebhookNotification(alert: QualityAlert, config: any): void {
    const payload = {
      alert,
      timestamp: Date.now(),
      project: 'Next.js Project'
    };

    // 实际发送webhook通知
    console.log('Webhook notification:', payload);
  }

  private calculateSeverity(change: number): 'low' | 'medium' | 'high' | 'critical' {
    if (change > 0.2) return 'critical';
    if (change > 0.15) return 'high';
    if (change > 0.1) return 'medium';
    return 'low';
  }

  private getSeverityColor(severity: string): string {
    const colors = {
      low: '#36a64f',
      medium: '#ff9500',
      high: '#ff0000',
      critical: '#990000'
    };

    return colors[severity as keyof typeof colors] || '#36a64f';
  }

  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async saveAssessment(assessment: QualityAssessment): Promise<void> {
    // 保存评估结果到存储
    console.log('Saving quality assessment:', assessment.timestamp);
  }

  // 获取质量监控统计
  getStatistics(): {
    totalAssessments: number;
    totalAlerts: number;
    activeAlerts: number;
    averageQuality: number;
    trend: 'improving' | 'declining' | 'stable';
  } {
    const totalAssessments = this.assessments.length;
    const totalAlerts = this.alerts.length;
    const activeAlerts = this.alerts.filter(a => !a.resolved).length;

    const averageQuality = totalAssessments > 0
      ? this.assessments.reduce((sum, a) => sum + a.overallScore, 0) / totalAssessments
      : 0;

    let trend: 'improving' | 'declining' | 'stable' = 'stable';
    if (totalAssessments >= 2) {
      const recent = this.assessments.slice(-5);
      const first = recent[0].overallScore;
      const last = recent[recent.length - 1].overallScore;
      const change = last - first;

      if (Math.abs(change) > 0.05) {
        trend = change > 0 ? 'improving' : 'declining';
      }
    }

    return {
      totalAssessments,
      totalAlerts,
      activeAlerts,
      averageQuality,
      trend
    };
  }

  // 获取最近的警报
  getRecentAlerts(limit: number = 10): QualityAlert[] {
    return this.alerts
      .filter(a => !a.resolved)
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  // 解决警报
  resolveAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      console.log(`Alert ${alertId} resolved`);
    }
  }
}
```

## 🎯 最佳实践和总结

### 1. 代码质量检查清单

```typescript
// checklists/code-quality-best-practices.ts
export const codeQualityBestPracticesChecklist = [
  {
    category: '代码规范',
    items: [
      '使用ESLint强制代码风格',
      '使用Prettier格式化代码',
      '配置TypeScript严格模式',
      '建立代码审查流程'
    ]
  },
  {
    category: '静态分析',
    items: [
      '配置全面的ESLint规则',
      '使用SonarQube进行深度分析',
      '实施安全扫描',
      '检查代码复杂度'
    ]
  },
  {
    category: '测试覆盖',
    items: [
      '单元测试覆盖率要求',
      '集成测试自动化',
      '端到端测试覆盖',
      '测试数据管理'
    ]
  },
  {
    category: '质量监控',
    items: [
      '实施代码质量监控',
      '设置质量门禁',
      '监控质量趋势',
      '自动化质量报告'
    ]
  },
  {
    category: '持续改进',
    items: [
      '定期代码重构',
      '技术债务管理',
      '最佳实践文档',
      '团队技能提升'
    ]
  }
];

export const runCodeQualityBestPracticesCheck = async (): Promise<void> => {
  console.log('🔍 Running Code Quality Best Practices Check...');

  for (const category of codeQualityBestPracticesChecklist) {
    console.log(`\n📋 ${category.category}:`);
    for (const item of category.items) {
      console.log(`  ✅ ${item}`);
    }
  }

  console.log('\n🎯 Code quality best practices check completed!');
};
```

### 2. 质量改进策略

```typescript
// guides/quality-improvement-strategy.ts
export class QualityImprovementStrategy {
  generateImprovementPlan(
    assessment: QualityAssessment,
    targetScore: number = 0.85
  ): QualityImprovementPlan {
    const plan: QualityImprovementPlan = {
      timeline: this.calculateTimeline(assessment.overallScore, targetScore),
      phases: [],
      milestones: [],
      metrics: [],
      resources: []
    };

    // 确定优先级维度
    const prioritizedDimensions = this.prioritizeDimensions(assessment);

    // 生成改进阶段
    plan.phases = this.generatePhases(prioritizedDimensions);

    // 生成里程碑
    plan.milestones = this.generateMilestones(plan.phases);

    // 生成监控指标
    plan.metrics = this.generateMetrics(assessment);

    // 生成资源需求
    plan.resources = this.generateResources(plan.phases);

    return plan;
  }

  private prioritizeDimensions(assessment: QualityAssessment): Array<{
    dimension: QualityDimension;
    currentScore: number;
    targetScore: number;
    priority: 'high' | 'medium' | 'low';
    effort: 'low' | 'medium' | 'high';
  }> {
    return assessment.dimensions
      .filter(d => d.score < 0.8) // 只关注需要改进的维度
      .sort((a, b) => a.score - b.score)
      .map(d => ({
        dimension: d.dimension,
        currentScore: d.score,
        targetScore: Math.min(d.score + 0.2, 0.95),
        priority: d.score < 0.6 ? 'high' : d.score < 0.7 ? 'medium' : 'low',
        effort: this.estimateEffort(d.dimension, d.score)
      }));
  }

  private estimateEffort(dimension: QualityDimension, currentScore: number): 'low' | 'medium' | 'high' {
    const effortMap: Record<QualityDimension, 'low' | 'medium' | 'high'> = {
      correctness: 'medium',
      reliability: 'high',
      efficiency: 'high',
      maintainability: 'medium',
      readability: 'low',
      security: 'high',
      testability: 'medium',
      consistency: 'medium'
    };

    return effortMap[dimension];
  }

  private calculateTimeline(currentScore: number, targetScore: number): {
    weeks: number;
    phases: number;
  } {
    const gap = targetScore - currentScore;
    const weeksPerPoint = 2; // 每提升0.01分需要2周
    const totalWeeks = Math.ceil(gap * 100 * weeksPerPoint);
    const phases = Math.ceil(totalWeeks / 4); // 每4周一个阶段

    return {
      weeks: totalWeeks,
      phases
    };
  }

  private generatePhases(
    dimensions: Array<{
      dimension: QualityDimension;
      currentScore: number;
      targetScore: number;
      priority: string;
      effort: string;
    }>
  ): QualityImprovementPhase[] {
    const phases: QualityImprovementPhase[] = [];
    const highPriority = dimensions.filter(d => d.priority === 'high');
    const mediumPriority = dimensions.filter(d => d.priority === 'medium');
    const lowPriority = dimensions.filter(d => d.priority === 'low');

    // 第一阶段：高优先级问题
    if (highPriority.length > 0) {
      phases.push({
        name: 'Phase 1: Critical Issues',
        duration: 4,
        focus: highPriority.map(d => d.dimension),
        actions: highPriority.map(d => this.generateActions(d)),
        outcomes: ['Resolve critical quality issues', 'Stabilize core metrics']
      });
    }

    // 第二阶段：中等优先级问题
    if (mediumPriority.length > 0) {
      phases.push({
        name: 'Phase 2: Improvement Initiatives',
        duration: 6,
        focus: mediumPriority.map(d => d.dimension),
        actions: mediumPriority.map(d => this.generateActions(d)),
        outcomes: ['Improve quality metrics', 'Establish best practices']
      });
    }

    // 第三阶段：优化和巩固
    phases.push({
      name: 'Phase 3: Optimization',
      duration: 4,
      focus: ['all'],
      actions: [
        'Implement continuous monitoring',
        'Refine processes',
        'Team training'
      ],
      outcomes: ['Sustain high quality', 'Continuous improvement']
    });

    return phases;
  }

  private generateActions(dimension: {
    dimension: QualityDimension;
    currentScore: number;
    targetScore: number;
    priority: string;
    effort: string;
  }): string[] {
    const actionMap: Record<QualityDimension, string[]> = {
      correctness: [
        'Enable strict TypeScript mode',
        'Add type annotations',
        'Implement type guards',
        'Improve type inference'
      ],
      reliability: [
        'Increase test coverage',
        'Add integration tests',
        'Implement error handling',
        'Add retry mechanisms'
      ],
      efficiency: [
        'Profile performance bottlenecks',
        'Optimize database queries',
        'Implement caching',
        'Use efficient algorithms'
      ],
      maintainability: [
        'Refactor complex functions',
        'Extract reusable components',
        'Improve code organization',
        'Add documentation'
      ],
      readability: [
        'Standardize code style',
        'Improve naming conventions',
        'Add inline comments',
        'Format code consistently'
      ],
      security: [
        'Fix security vulnerabilities',
        'Implement input validation',
        'Add authentication',
        'Regular security audits'
      ],
      testability: [
        'Refactor for testability',
        'Add unit tests',
        'Implement mocking',
        'Improve test data'
      ],
      consistency: [
        'Standardize architecture',
        'Consistent error handling',
        'Uniform API responses',
        'Consistent data models'
      ]
    };

    return actionMap[dimension.dimension] || [];
  }

  private generateMilestones(phases: QualityImprovementPhase[]): QualityImprovementMilestone[] {
    const milestones: QualityImprovementMilestone[] = [];
    let weekOffset = 0;

    phases.forEach((phase, index) => {
      milestones.push({
        name: `${phase.name} Complete`,
        week: weekOffset + phase.duration,
        deliverables: phase.outcomes,
        successCriteria: phase.focus.map(f => `${f} metrics improved`)
      });

      weekOffset += phase.duration;
    });

    return milestones;
  }

  private generateMetrics(assessment: QualityAssessment): QualityMetric[] {
    return [
      {
        name: 'Overall Quality Score',
        target: 0.85,
        current: assessment.overallScore,
        unit: 'percentage'
      },
      {
        name: 'Code Coverage',
        target: 0.80,
        current: assessment.dimensions.find(d => d.dimension === 'reliability')?.score || 0,
        unit: 'percentage'
      },
      {
        name: 'Type Safety',
        target: 0.90,
        current: assessment.dimensions.find(d => d.dimension === 'correctness')?.score || 0,
        unit: 'percentage'
      }
    ];
  }

  private generateResources(phases: QualityImprovementPhase[]): QualityResource[] {
    return [
      {
        type: 'team',
        description: 'Development team allocation',
        quantity: phases.length * 2,
        unit: 'developers'
      },
      {
        type: 'time',
        description: 'Total improvement time',
        quantity: phases.reduce((sum, phase) => sum + phase.duration, 0),
        unit: 'weeks'
      },
      {
        type: 'tools',
        description: 'Quality assurance tools',
        quantity: 1,
        unit: 'suite'
      }
    ];
  }
}

interface QualityImprovementPlan {
  timeline: {
    weeks: number;
    phases: number;
  };
  phases: QualityImprovementPhase[];
  milestones: QualityImprovementMilestone[];
  metrics: QualityMetric[];
  resources: QualityResource[];
}

interface QualityImprovementPhase {
  name: string;
  duration: number;
  focus: QualityDimension[];
  actions: string[];
  outcomes: string[];
}

interface QualityImprovementMilestone {
  name: string;
  week: number;
  deliverables: string[];
  successCriteria: string[];
}

interface QualityMetric {
  name: string;
  target: number;
  current: number;
  unit: string;
}

interface QualityResource {
  type: 'team' | 'time' | 'tools' | 'budget';
  description: string;
  quantity: number;
  unit: string;
}
```

## 🎯 总结

代码质量是现代前端工程化的基石。通过建立全面的代码质量保证体系，可以显著提升项目的可维护性、可靠性和开发效率。

### 关键要点：

1. **质量维度**：从多个维度评估代码质量
2. **静态分析**：使用ESLint等工具进行代码分析
3. **质量门禁**：设置合理的质量标准和检查点
4. **监控体系**：持续监控代码质量变化
5. **改进策略**：制定系统的质量改进计划
6. **最佳实践**：建立团队的代码质量标准

### 实施建议：

- **渐进式改进**：从最关键的问题开始改进
- **自动化工具**：充分利用自动化工具提升效率
- **团队协作**：建立代码审查和质量标准
- **持续监控**：定期评估和监控代码质量
- **培训提升**：提升团队的代码质量意识

通过掌握这些代码质量管理技术，可以构建高质量、可维护的现代前端应用。