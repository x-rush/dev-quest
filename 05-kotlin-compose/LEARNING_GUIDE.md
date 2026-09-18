# Kotlin / Compose：理解地图与学习规划

> 前置：函数、类与集合；先理解 Kotlin 可空类型、lambda 和属性委托。需要 Android Studio 和可用模拟器或设备。

## 先回答一个问题

**状态变化以后，为什么屏幕会更新，而某些普通变量改变后不会？**

Kotlin 是语言，Compose 是声明式 UI，Android 提供 Activity、权限和生命周期。先把这三层分开：函数能编译、界面能重组和旋转后数据还在，是三件不同的事。

## 概念怎样连接

Kotlin 语法 → Composable → 状态与重组 → 布局 → 导航 → ViewModel/Flow → Room/网络

| 概念 | 必要解释 |
|---|---|
| remember 与可观察状态 | remember 保存当前组合位置的值，mutableStateOf 提供变化通知；只保存一个普通可变集合不等于内部变化可被观察。 |
| 生命周期 | 重组、Activity 重建和进程重建不是同一件事；分别选择 remember、状态保存或持久化。 |
| Flow | Flow 是可收集的数据序列；界面应结合生命周期收集，避免页面不可见时继续做不必要工作。 |

## 从 0 到 1 的阅读顺序

以下按模块现有章节编号导航。章节中的“先理解，再动手”给出本节重点与自测；环境版本集中看[模块 README](README.md)。

1. [环境搭建 - Android Studio 与 Kotlin 开发环境](basics/01-environment-setup.md)
2. [第一个 Compose 应用 - 从零到运行](basics/02-first-compose-app.md)
3. [Kotlin 语法基础 - 面向 Compose 开发者](basics/03-kotlin-syntax-essentials.md)
4. [Composable 与状态 - 声明式 UI 的核心](basics/04-composables-state.md)
5. [布局系统 - Column/Row/Box 与 LazyColumn](basics/05-layouts.md)
6. [页面导航 - Navigation Compose 入门](basics/06-navigation.md)
7. [协程与 Flow 基础 - 在 ViewModel 中驱动异步数据](basics/07-coroutines-flow-basics.md)
8. [第一个项目 - Compose + Room 笔记应用](basics/08-first-project.md)

## 三个阶段如何验收

1. 计数器加重置按钮，解释点击到文本变化的过程。
2. 把状态提升给父组件，让两个子组件显示同一数字；再旋转屏幕比较保存方式。
3. 做本地笔记，重启后仍可读取；网络加载再补加载、错误、重试和取消。

每阶段保留实际输入、输出和一个失败案例。只阅读或复制成功代码，不等同于已经通过验收。练习用小功能承接已学知识，大型项目的扩展需求可按需选做。

## 框架与高级主题怎么选

Compose 为 UI 主线，ViewModel 承担页面状态与业务协调，Room/Retrofit 按数据需求接入。依赖注入在对象关系复杂后再引入，避免初课同时解释全部注解。

## 全量参考怎么查

关键词解决“语法是什么意思”，内置函数解决“直接能调用什么”，标准库解决“导入以后能做什么”。框架 API 另列，避免把库函数误当成语言本身。以下是现有文章的完整导航，不代表每个 API 都已充分讲解；具体覆盖缺口进入审查台账。

### framework-essentials

- [Compose 核心组件速查](reference/framework-essentials/01-compose-essentials.md)
- [Material 3 主题系统速查](reference/framework-essentials/02-compose-material3.md)
- [副作用 API 速查](reference/framework-essentials/03-side-effects.md)
- [重组与稳定性速查](reference/framework-essentials/04-recomposition.md)
- [动画核心 API 速查](reference/framework-essentials/05-animation-core.md)
- [Navigation Compose 组件速查](reference/framework-essentials/06-navigation-components.md)
- [Compose 测试 API 速查](reference/framework-essentials/07-compose-testing.md)
- [@Composable 与组合模型](reference/framework-essentials/08-composition-model.md)
- [手势 API](reference/framework-essentials/09-gestures.md)
- [Canvas 自定义绘制](reference/framework-essentials/10-canvas-drawing.md)

### language-concepts

- [Kotlin 关键字与修饰符详解](reference/language-concepts/01-kotlin-keywords.md)
- [可空性与集合 API 速查](reference/language-concepts/02-null-safety-collections.md)
- [协程与 Flow API 全表](reference/language-concepts/03-coroutines-flow-api.md)
- [Compose 状态 API 详解](reference/language-concepts/04-compose-state-api.md)
- [泛型与委托属性速查](reference/language-concepts/05-generics-delegates.md)
- [扩展函数与扩展属性](reference/language-concepts/06-extension-functions.md)
- [作用域函数速查](reference/language-concepts/07-scope-functions.md)
- [Lambda 与高阶函数](reference/language-concepts/08-lambdas-higher-order.md)
- [集合操作算子导览](reference/language-concepts/09-collections-operations.md)
- [Sequence 惰性求值](reference/language-concepts/10-sequences.md)
- [字符串 API 与正则导览](reference/language-concepts/11-text-and-regex.md)

### library-guides

- [AndroidX 官方库指南](reference/library-guides/01-androidx-libraries.md)
- [第三方库指南](reference/library-guides/02-third-party-libs.md)
- [KSP 代码生成配置指南](reference/library-guides/03-ksp-configuration.md)

### quick-references

- [Kotlin + Compose 一行式速查表](reference/quick-references/01-kotlin-compose-cheatsheet.md)
- [常见错误与故障排除](reference/quick-references/02-troubleshooting.md)

## 卡住时

先判断是术语不懂、输入输出不清、代码上下文缺失，还是运行环境不同。返回[学习方法](../shared-resources/learning-guide.md)按证据排查；通用术语见[术语解释](../shared-resources/glossary.md)。
