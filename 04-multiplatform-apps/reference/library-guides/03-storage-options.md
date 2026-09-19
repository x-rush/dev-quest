# 存储方案选型 — 键值、加密、SQLite 与文件

> **难度**: ⭐⭐ | **前置**: 理解持久化在状态分层中的位置（[07-state-management](../language-concepts/07-state-management.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#AsyncStorage` `#MMKV` `#SecureStore` `#SQLite` `#文件系统` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

持久化按"数据形状 + 安全要求"选载体，四类场景各归其位：

| 场景 | 数据形状 | 首选载体 | 理由 |
|------|---------|---------|------|
| 高频读写的小状态 | 键值，同步可读 | **MMKV** | 内存映射 + 同步 API，适合频繁读取小型键值，需测量实际序列化和调用成本 |
| token / 密钥等敏感值 | 小且必须加密 | **expo-secure-store** | 走系统安全区（Keychain / Keystore），加密落盘 |
| 结构化查询数据 | 关系型、需索引/事务 | **expo-sqlite** | 真正的 SQL，支持索引、事务与扩展 |
| 大文件与文档 | 二进制/媒体 | **expo-file-system** | 文件粒度读写、目录操作、资产访问 |
| 低频简单设置 | 键值，容忍异步 | **@react-native-async-storage/async-storage** | 通用兜底，生态兼容最广 |

**决策顺序**：先判断敏感性、查询需求与文件大小，再测量读写开销。下面几种载体可以共存，但入门设置页先用一种键值存储即可。内存中的 React 状态负责当前画面，持久化负责下次启动恢复；磁盘变化不会自动触发 React 重绘。

本页是存储库参考及一个设置恢复练习，不覆盖多设备同步、密钥轮换或生产数据迁移。需先会 Promise、try/catch、JSON 与 React 状态更新；不熟悉启动恢复时序时先回查[状态管理模型](../language-concepts/07-state-management.md)。

## 📖 语法/签名

下面三段是各库的独立局部片段，不是一个可直接启动的文件；`token`、`keyword` 由调用者传入，顶层 await 应放入项目允许的异步入口。原生模块须安装与当前项目匹配的版本并重新构建所需客户端。MMKV v4 还需按其官方安装说明配置 Nitro Modules，不能假定安装 JS 包后 Expo Go 就能加载它。

```ts
// MMKV —— 同步键值（数据量小时"像操作内存一样"）
import { createMMKV } from 'react-native-mmkv';
const storage = createMMKV();
storage.set('theme', 'dark');
const theme: string | undefined = storage.getString('theme');

// expo-secure-store —— 敏感值，异步 API
import * as SecureStore from 'expo-secure-store';
await SecureStore.setItemAsync('token', token);
const saved = await SecureStore.getItemAsync('token'); // 未命中返回 null

// expo-sqlite —— 结构化数据
import * as SQLite from 'expo-sqlite';
const db = await SQLite.openDatabaseAsync('app.db');
await db.execAsync('CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, body TEXT)');
const rows = await db.getAllAsync<{ id: string; body: string }>(
  'SELECT id, body FROM notes WHERE body LIKE ?',
  [`%${keyword}%`],
);
```

> **v4 API 范围**：这里采用 `createMMKV(configuration?)` 工厂，删除键使用 `remove(key)`。已有项目升级需阅读对应版本迁移说明；安装结果由版本范围与锁文件决定，不应假定未锁版本永远得到同一主版本。

## 💡 示例

```ts
// 组合模式：MMKV 缓存 + SecureStore 存凭据，接口收敛到一个模块
import { createMMKV } from 'react-native-mmkv';
import * as SecureStore from 'expo-secure-store';

const cache = createMMKV({ id: 'cache' });

export const prefs = {
  get: (key: string) => cache.getString(key),
  set: (key: string, value: string) => cache.set(key, value),
};

export const credentials = {
  saveToken: (t: string) => SecureStore.setItemAsync('token', t),
  loadToken: () => SecureStore.getItemAsync('token'),
};
```

## ⚠️ 常见陷阱

- **明文存 token**：AsyncStorage 是未加密存储。移动端敏感小值可考虑 SecureStore，但必须处理读取失败、凭据失效和重新登录；它不是唯一数据源或跨设备备份。Android 卸载会清除数据，iOS Keychain 数据可能跨重装保留，不能把卸载等同于登出
- **把异步读当同步初值**：AsyncStorage 返回 Promise。先显示恢复中状态，成功后再开放编辑；反复读取可优先使用内存状态，只有实测需要时再改变底层库
- **SQLite 当键值用**：单表 KV 不如键值存储直接；SQLite 的价值在索引、事务与复杂查询
- **大 JSON 整块读写**：列表数据整包序列化导致读写放大；改 SQLite 行级存储或分片键
- **存储与状态不同步**：持久化是"快照投影"，重启后必须有一致的 rehydrate 路径（配合 store 的 persist 中间件）
- **忽略鸿蒙端适配**：三方原生存储库需确认 RNOH 适配版本，见 [RNOH 字典](../language-concepts/05-harmonyos-rnoh-api.md)

<!-- full-library-explanation -->
## 存下数据之后还要能升级与恢复

### 第一阶段：只保存一个非敏感设置

可见产物是“保存深色主题 → 重启 → 恢复深色”的闭环。已有 Expo TypeScript 工程在项目根执行 `npx expo install @react-native-async-storage/async-storage`，并按该工程原来的启动方式运行 Android 或 iOS。裸 React Native 工程按库安装文档处理原生依赖；不要为了本例同时引入其他四种存储库。

在 `src/storage/preferences.ts` 新建以下完整模块。它把磁盘原始字符串当成不可信输入，先解析再检查结构；这一步不能用 `as Preferences` 替代。

```ts
import AsyncStorage from '@react-native-async-storage/async-storage';

export type Preferences = { version: 1; theme: 'light' | 'dark' };
type Loaded = { value: Preferences; source: 'saved' | 'default' };
const KEY = 'lesson.preferences';

export async function loadPreferences(): Promise<Loaded> {
  const raw = await AsyncStorage.getItem(KEY);
  if (raw === null) {
    return { value: { version: 1, theme: 'light' }, source: 'default' };
  }
  const value: unknown = JSON.parse(raw);
  if (typeof value !== 'object' || value === null ||
      !('version' in value) || value.version !== 1 ||
      !('theme' in value) ||
      (value.theme !== 'light' && value.theme !== 'dark')) {
    throw new Error('设置格式不受支持；保留原数据，等待恢复');
  }
  return { value: { version: 1, theme: value.theme }, source: 'saved' };
}

export async function savePreferences(theme: Preferences['theme']): Promise<void> {
  const value: Preferences = { version: 1, theme };
  await AsyncStorage.setItem(KEY, JSON.stringify(value));
}
```

`getItem` 接收键，输出字符串或 null；只有 null 表示首次使用。I/O 失败会拒绝 Promise，损坏 JSON 会在 JSON.parse 抛错，两者均交给调用者显示失败，不能偷偷报告恢复成功。保存函数输入主题值，等待写入完成才兑现 Promise。损坏或未知版本的数据被保留，加载不会自动覆盖它。

### 第二阶段：把结果接到画面

在现有设置屏幕引入模块，在挂载 effect 中调用 loadPreferences：开始标记“恢复中”并禁用修改；成功时把返回 theme 写入 React 状态，标记“已恢复”或“使用默认设置”；失败时显示“恢复失败，尚未覆盖原数据”并保持编辑禁用。effect 清理时标记 inactive，迟到的结果不再更新已卸载屏幕。这里描述的是接入步骤，不是一份额外的完整 App。

保存按钮的异步事件处理器应先禁用按钮、显示“保存中”，await savePreferences 后才显示“已保存”；catch 显示“保存失败”，finally 恢复按钮。练习中一次只允许一个写入，避免用户连点产生完成顺序不一致。不要在首次 render 的 effect 中立即把默认值写盘，那会与启动读取竞争并覆盖旧设置。

### 第三阶段：失败输入与回查

| 输入或操作 | 预期可见结果 | 不符合时回查 |
|---|---|---|
| 首次读取不存在的键 | light，标记使用默认设置 | 是否把 null 与异常混为一谈 |
| 保存 dark，关闭并重新打开 app | dark，标记已恢复 | 是否 await 保存；是否使用同一键与安装实例 |
| 将该练习键写入字符串 `{broken` | 恢复失败，原值不被替换 | catch 是否吞错后自动写默认值 |
| 写入 `{"version":2,"theme":"dark"}` | 格式不支持，保留原值 | 是否跳过运行时字段校验 |
| 模拟 setItem 拒绝 Promise | 保存失败，不出现已保存 | 成功提示是否放在 await 之前 |

损坏输入仅在练习工程的 `lesson.preferences` 键上操作；恢复时可显式移除该键再重启。若这是用户不可替代数据，则应先导出或备份，不能照搬设置重置策略。下一步练习把版本 1 迁移成版本 2：先在内存完成结构检查和转换，写回成功后才报告升级完成；写回失败仍保留可追查的旧数据。

本轮完成官方接口核对与静态阅读，未运行 Android/iOS 客户端、SecureStore、MMKV 或 SQLite 原生模块。内存 mock 即使通过也只覆盖调用时序，不证明真实磁盘、卸载、系统备份或生物识别行为。

键值中的 JSON 应带版本，并在读取时检查结构；SQLite 的表结构变化需要迁移。新版本把 `done: boolean` 改成状态枚举后，旧文件不会自动变成新格式。缓存可删除重建，用户尚未同步的笔记通常不可丢弃，这决定了失败处理方式。

SQLite 参数绑定防止值被当作 SQL 代码，但 LIKE 模式中的 `%` 与 `_` 仍有通配语义；搜索需求若是字面量匹配，需单独处理模式转义。TypeScript 的查询结果泛型也不校验磁盘中每一行的真实类型。

练习：写入版本 1 的设置，添加版本 2 字段和迁移函数，再输入损坏 JSON。验收：可恢复设置用默认值并报告恢复；不可替代数据保留原副本且提示修复。模拟磁盘失败时，不应显示“已保存”。同步 API 仍可能阻塞调用线程，不应循环读写大对象。

## 🔗 相关条目

- 📄 [状态与数据请求库指南](./01-state-and-data.md) — 持久化与状态层的衔接（persist 中间件）
- 📄 [状态管理模型](../language-concepts/07-state-management.md) — "持久化是投影"的分层定位
- 📄 [原生与设备能力库指南](./02-native-and-device-libs.md) — 存储之外的设备能力选型
- 📄 [Expo 要点](../framework-essentials/01-expo-essentials.md) — expo-* 模块总览

官方回查（2026-09-20）：[Expo AsyncStorage 安装与未加密边界](https://docs.expo.dev/versions/latest/sdk/async-storage/)、[SecureStore 平台差异](https://docs.expo.dev/versions/latest/sdk/securestore/)、[SQLite 参数与事务](https://docs.expo.dev/versions/latest/sdk/sqlite/)、[MMKV 安装与 API](https://github.com/margelo/react-native-mmkv)。完成设置闭环后进入[状态与数据请求库指南](./01-state-and-data.md)，再把恢复中、保存失败等状态接入应用状态层；需要条件查询与多个记录一起提交时，才把练习扩展到 SQLite。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
