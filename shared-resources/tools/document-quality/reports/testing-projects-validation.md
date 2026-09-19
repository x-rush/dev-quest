# Web / 移动测试与项目规则验证

2026-09-19 使用 Node 24.19.0 执行。这里记录正文抽取的有限行为范围，不代表相关整篇文档、Next.js 完整构建或移动设备验收全部完成。

## 正文规则：4 个源模块、11 个行为测试

运行仓库内的无依赖验证器：

```bash
node shared-resources/tools/document-quality/verify_testing_projects.mjs
```

验证器按代码围栏的文件名注释定位唯一源模块，原样保存为 TypeScript，由 Node 24 的内置类型擦除执行；不补写函数、不替换算法。测试断言存放在验证器中，运行时的具体源码、断言、标准输出、退出码与源码 SHA-256 保存在 [testing-projects.json](./testing-projects.json)。这不是 TypeScript 类型检查。

| 正文 | 已执行范围 | 结果 |
|---|---|---|
| [Next 单元测试](../../../../02-nextjs-frontend/testing/01-unit-testing.md) | UTC 跨年、无效日期、中文截断、emoji 码点、非法长度、slug 边界与基础邮箱格式 | 3 / 3 |
| [TanStack 单元测试](../../../../03-tanstack-stack/testing/01-unit-testing.md) | 冻结输入不可变、跨列与同列移动、未知卡片/目标、非法索引 | 3 / 3 |
| [TanStack Todo](../../../../03-tanstack-stack/projects/01-todo-app.md) | 键工厂、JSON 列表、DELETE 204、500 与无效 JSON；只替换 fetch 边界 | 3 / 3 |
| [RN Todo](../../../../04-multiplatform-apps/projects/01-todo-app.md) | 标题规范化、空输入、非法 id/时间、不可变切换与未完成统计 | 2 / 2 |

共 4 个模块、11 个行为测试全部通过。HTTP 测试使用真实 `Response`，没有发网络请求；RN 范围只含纯领域函数，没有加载 Expo、MMKV、Zustand 或原生设备。

## 客户端存储 Hook：4 组真实 React 验证

使用独立依赖目录，避免在文档仓库生成业务应用依赖：

```bash
mkdir ../storage-validation
cd ../storage-validation
npm init -y
npm install --save-exact react@19.3.0 react-dom@19.3.0 jsdom@26.1.0 @testing-library/react@16.3.3
cd ../dev-quest
node shared-resources/tools/document-quality/verify_client_storage.mjs ../storage-validation
```

本次复用已安装同版本依赖的 `../verification-lab` 目录。验证器直接抽取上述 Next 单测正文中的 `useLocalStorage` 模块，在真实 React + jsdom 下执行，并在独立、没有 `window` 的 Node 进程执行服务端渲染。四组行为全部通过：

1. Node 服务端渲染返回初始值。
2. 同一批次两次函数式自增得到 2，实际写入 jsdom 的存储；卸载再挂载读取到 2。
3. 损坏 JSON 使用初始值回退，同时保留损坏原始数据，避免无声覆盖。
4. 写入失败保留最后成功状态；恢复后重试从最后成功值计算。

原文的 setter 使用闭包旧值，连续更新会丢失一次自增；原本先更新内存、后写存储的顺序还会把未保存内容显示成成功状态。现在通过 ref 保存最新成功值，持久化成功后才更新内存与界面。源码哈希、实际依赖版本和案例结果见 [client-storage.json](./client-storage.json)。

此 Hook 仍是固定 key、JSON 可序列化值的客户端练习。jsdom 不证明真实浏览器 hydration 一致、跨标签同步或动态 key 切换；正文明确这几个扩展需要独立设计和验收。Vitest / Jest 的整套配置、其他表单及组件示例也未因本报告自动升级为通过。

## 教程中其他已修复问题

- RN 的空标题保护下沉到 store；时间戳 id 改为 Expo Crypto UUID，补 MMKV Nitro 配套依赖与 development build 前提。
- RN 单元测试补齐实际可导入的纯函数来源，修正“所有 store 更新都必须 act”的错误规则；假时钟增加恢复步骤。
- 看板项目复用有目标校验的纯移动器，说明整板回滚只适合单个在途请求；明确缺失删除墓碑、事件去重和并发重放的失败模式，并提供可观察验收序列。SSE 示例尚未通过多客户端并发验证，不宣称完整协作协议已交付。
- Next 的 SSR 测试使用 Node 环境与服务端渲染器，移除删除 `window` 后继续调用浏览器 `renderHook` 的错误做法。

## 官方资料复核

- [Vitest 覆盖率](https://vitest.dev/guide/coverage.html)：覆盖率 provider 与依赖安装。
- [Expo Jest](https://docs.expo.dev/develop/unit-testing/)：SDK 配套安装与预设。
- [Zustand 测试](https://zustand.docs.pmnd.rs/guides/testing)：store 隔离与 React 更新边界。
- [MMKV 安装](https://github.com/mrousavy/react-native-mmkv#installation)：Nitro Module 配套依赖及原生构建。
- [Expo Crypto](https://docs.expo.dev/versions/latest/sdk/crypto/#cryptorandomuuid)：UUID 生成 API。
