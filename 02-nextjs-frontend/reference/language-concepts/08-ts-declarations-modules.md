# TypeScript 枚举、环境声明与模块系统

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `language-concepts`

## 📌 定义

本条目覆盖 TypeScript 中四组"类型系统与模块边界"能力：**枚举**（`enum`/`const enum`——仅有的"类型即运行时值"特性）、**类型级导入导出**（`import type`/`export type`——只存在于类型层，不产生运行时代码）、**环境声明**（`declare`——告诉编译器"这个标识符在别处已存在"，包括 `declare global` 全局扩充与 `declare module` 环境模块）、以及**抽象类与 `.d.ts` 声明文件**（给 JS 库补类型、用 `///` 三斜线指令组织引用）。它们共同决定了"类型世界里有什么"，是读懂 Next.js 项目类型配置（`next-env.d.ts`、`env.d.ts`）的前提。

## 📖 语法/签名

```ts
// 枚举
enum Direction { Up = 1, Down, Left, Right }   // 常规枚举：类型 + 运行时对象
const enum Fast  { A = 1, B = A * 2 }          // const 枚举：编译期数值内联，无运行时对象

// 类型级导入导出
import type { AppConfig } from './lib'          // 只导入类型，编译后整句消失
export type { AppConfig }                       // 只导出类型

// 环境声明
declare const API_URL: string                   // 声明已存在的全局常量
declare global {                                // 在模块文件中扩充全局作用域
  interface Window { __APP_VERSION?: string }
}
declare module 'ext-untyped-lib' {              // 环境模块：为无类型库凭空声明形状
  export function track(event: string): void
}
declare module 'react' {                        // 模块扩充（augmentation）：给已有模块加类型
  interface CSSProperties { [key: `--${string}`]: string }
}

// 抽象类
abstract class Shape {
  abstract area(): number                       // 抽象成员：只有签名，子类必须实现
  describe(): string { return `area=${this.area()}` }  // 普通成员可带实现
}

// .d.ts 声明文件 + 三斜线指令
/// <reference path="./globals.d.ts" />          // 按路径引入其他声明文件
/// <reference lib="dom" />                      // 引入内置 lib
```

## 💡 示例

### 模块扩充：给第三方库的接口补字段（02 模块高频用法）

```ts
// types/next-auth.d.ts —— 为 Session 补自定义字段
import type { DefaultSession } from 'next-auth'

declare module 'next-auth' {
  interface Session {
    user: { id: string } & DefaultSession['user']
  }
}
// 此后全项目 session.user.id 获得类型，无需 as 断言
```

### 环境声明：键入 `process.env` 自定义变量

```ts
// env.d.ts（被 tsconfig include 覆盖即可生效）
declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string
    DATABASE_URL: string
  }
}
```

### 抽象类：模板方法模式

```ts
abstract class Shape {
  abstract area(): number
  describe(): string { return `area=${this.area()}` }
}

class Square extends Shape {
  constructor(private side: number) { super() }
  area(): number { return this.side ** 2 }
}

const s: Shape = new Square(3)
s.describe()        // "area=9"
// new Shape()      // 编译错误：抽象类不能实例化
```

## ⚠️ 常见陷阱

- ❌ **在 Next.js 项目里用 `const enum` 跨文件共享成员**：Next.js 生成的 tsconfig 默认开启 `isolatedModules`（Turbopack/SWC 按单文件转译，无法做跨文件内联）。本机 tsc 7.0.2 实测：普通 `const enum` 在 `isolatedModules` 下仍可编译（SWC 按常规枚举处理），但 `declare const enum` 直接报 **TS2748: Cannot access ambient const enums when 'isolatedModules' is enabled**；纯转译模式下环境 const enum 成员运行时根本不存在，访问得到 `undefined`。✅ 跨文件共享常量用 `as const` 对象或字符串/数字字面量联合类型，`enum`（常规枚举）用于需要运行时对象（反向映射、遍历）的场景。
- ❌ **以为 TS 7 移除了枚举**：本机 `tsc 7.0.2`（2026-09 npm 当前版）实测 `enum`、`const enum`、`declare global`、`declare module` 扩充、`abstract` 类全部照常支持，错误行为与 5.9.3 一致——"7.0 基线"改变的是编译器实现与性能，不是这些语言特性的可用性。
- ❌ **用相对路径做模块扩充**：`declare module './mods/lib'` 报 **TS2664: Invalid module name in augmentation**（本机实测）——扩充只能针对裸模块名（`'next-auth'`、`'react'`）。✅ 扩充包名；本地文件直接改源码或用交叉类型。
- ❌ **在 `.d.ts` 里写实现**：声明文件只允许类型与 `declare` 声明；函数体、赋值语句会被忽略或报错。✅ 实现放 `.ts`，形状放 `.d.ts`。
- ❌ **模块化的 `.d.ts` 忘了包 `declare global`**：一旦声明文件里有 `import`/`export`，它就是模块文件，顶层声明不再是全局的——想让 `Window` 等全局接口生效必须写进 `declare global { }`。✅ 纯全局声明文件（无 import/export）才可直接写顶层 `interface`。
- ❌ **把 `import type` 当运行时导入**：`import type` 编译后完全消失，用它导入的"值"在运行时是 `undefined`——拿它导入组件/常量会静默得到空值。✅ 类型用 `import type`（或内联 `import { type AppConfig }`），值用普通导入。
- ❌ **`///` 三斜线指令写错位置**：三斜线指令必须是文件**最顶部连续注释**（前面只能有其他注释），放在代码中间会被当普通注释忽略。✅ 固定放文件首行区域；现代项目多数场景已被 tsconfig `include`/`types` 取代。

## 🔗 相关条目

- [TypeScript 类型速查手册](./03-typescript-types.md) —— 类型与工具类型全景
- [类型收窄与类型守卫](./07-type-narrowing-guards.md) —— 联合类型在运行时如何变窄
- [环境变量](../framework-patterns/14-env-vars.md) —— `env.d.ts` 键入 `process.env` 的工程实践
- [Next.js API 参考](./02-nextjs-api-reference.md) —— `next-env.d.ts` 与项目 tsconfig 结构
- 🌐 **[TypeScript Handbook: Modules](https://www.typescriptlang.org/docs/handbook/2/modules.html)** —— 官方模块/声明合并文档

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
