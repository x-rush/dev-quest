# TypeScript 枚举、环境声明与模块系统

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `language-concepts`

## 📌 定义

本条目覆盖 TypeScript 中四组"类型系统与模块边界"能力：**枚举**（`enum`/`const enum`——同时涉及类型与运行时值的特性之一，class 等也跨越两层）、**类型级导入导出**（`import type`/`export type`——只存在于类型层，不产生运行时代码）、**环境声明**（`declare`——告诉编译器"这个标识符在别处已存在"，包括 `declare global` 全局扩充与 `declare module` 环境模块）、以及**抽象类与 `.d.ts` 声明文件**（给 JS 库补类型、用 `///` 三斜线指令组织引用）。它们共同决定了"类型世界里有什么"，是读懂 Next.js 项目类型配置（`next-env.d.ts`、`env.d.ts`）的前提。

## 📖 语法/签名

```ts
// 枚举
enum Direction { Up = 1, Down, Left, Right }   // 常规枚举：类型 + 运行时对象
const enum Fast  { A = 1, B = A * 2 }          // const 枚举：常规 tsc 配置可内联；preserveConstEnums/单文件转译会改变输出

// 类型级导入导出
import type { AppConfig } from './lib'          // 只导入类型，编译后整句消失
export type { AppConfig }                       // 只导出类型

// 环境声明
declare const API_URL: string                   // 此模块内的环境声明；全局声明需放在全局声明上下文
declare global {                                // 在模块文件中扩充全局作用域
  interface Window { __APP_VERSION?: string }
}
// 以下应单独放入无顶层 import/export 的 ext-untyped-lib.d.ts
declare module 'ext-untyped-lib' {              // 环境模块声明；不要与上面的导入拼成同一文件
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

- ❌ **在 Next.js 项目里用 `const enum` 跨文件共享成员**：Next.js 生成的 tsconfig 默认开启 `isolatedModules`（Turbopack/SWC 按单文件转译，无法做跨文件内联）。原文记录曾使用 tsc 7.0.2（本轮未复现该版本）：普通 `const enum` 在 `isolatedModules` 下仍可编译（SWC 按常规枚举处理），但 `declare const enum` 直接报 **TS2748: Cannot access ambient const enums when 'isolatedModules' is enabled**；纯转译模式下环境 const enum 成员运行时根本不存在，访问得到 `undefined`。✅ 跨文件共享常量用 `as const` 对象或字符串/数字字面量联合类型，`enum`（常规枚举）用于需要运行时对象（反向映射、遍历）的场景。
- **版本结论应以所用编译器与配置验证**：升级后执行类型检查和构建，不把主版本号推断为某个语言特性已删除。
- **相对模块扩充合法**：在模块文件中 import 目标后，可用 declare module './observable' 扩充已有导出；TS2664 通常提示目标无法解析，不能据此断言相对扩充不被支持。
- ❌ **在 `.d.ts` 里写实现**：声明文件只允许类型与 `declare` 声明；函数体和实现性语句会报错，不是可依赖的静默忽略行为。✅ 实现放 `.ts`，形状放 `.d.ts`。
- ❌ **模块化的 `.d.ts` 忘了包 `declare global`**：一旦声明文件里有 `import`/`export`，它就是模块文件，顶层声明不再是全局的——想让 `Window` 等全局接口生效必须写进 `declare global { }`。✅ 纯全局声明文件（无 import/export）才可直接写顶层 `interface`。
- ❌ **把 `import type` 当运行时导入**：`import type` 编译后完全消失，把它导入的名称当值使用通常会触发编译错误；绕过检查后缺失绑定还可能导致 ReferenceError。✅ 类型用 `import type`（或内联 `import { type AppConfig }`），值用普通导入。
- ❌ **`///` 三斜线指令写错位置**：三斜线指令必须是文件**最顶部连续注释**（前面只能有其他注释），放在代码中间会被当普通注释忽略。✅ 固定放文件首行区域；现代项目多数场景已被 tsconfig `include`/`types` 取代。

<!-- full-library-explanation -->
## 声明只描述能力，不会安装能力

前置是 JavaScript 模块与 TypeScript 类型和值的区别。declare const API_URL 不会生成常量，ProcessEnv 接口写成 string 也不会让缺失环境变量出现；声明应该描述经验证的事实，启动时仍需检查配置。给 Session 增加 id 类型之后，认证回调还必须真的填入该字段。

模块扩充要求目标模块能被解析，并遵循声明合并规则。它可以使用相对模块名；官方 Observable 示例就是 declare module './observable'。这与脚本声明文件里声明一个不存在的环境模块不同。扩充原型的方法时，还必须提供并导入真正的运行时实现，否则类型检查通过而调用失败。

**练习**：只声明一个全局函数但不实现，在独立练习中运行调用，预期 ReferenceError；补实现后才能成功。再把服务端密钥仅声明为类型，检查构建产物，确认类型擦除与密钥打包是两回事。将普通类用 import type 导入后拿来 new，预期编译器报错，不能靠“编译后为空值”来理解它。

依据：[声明合并与相对模块扩充](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)、[模块参考](https://www.typescriptlang.org/docs/handbook/modules/reference.html)。本轮未复现原文的版本实测记录，const enum 输出还取决于转译器与编译选项。

## 🔗 相关条目

- [TypeScript 类型速查手册](./03-typescript-types.md) —— 类型与工具类型全景
- [类型收窄与类型守卫](./07-type-narrowing-guards.md) —— 联合类型在运行时如何变窄
- [环境变量](../framework-patterns/14-env-vars.md) —— `env.d.ts` 键入 `process.env` 的工程实践
- [Next.js API 参考](./02-nextjs-api-reference.md) —— `next-env.d.ts` 与项目 tsconfig 结构
- 🌐 **[TypeScript Handbook: Modules](https://www.typescriptlang.org/docs/handbook/2/modules.html)** —— 官方模块/声明合并文档

---
*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
