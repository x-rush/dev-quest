# 存储方案选型 — 键值、加密、SQLite 与文件

> **难度**: ⭐⭐ | **前置**: 理解持久化在状态分层中的位置（[07-state-management](../language-concepts/07-state-management.md)）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#AsyncStorage` `#MMKV` `#SecureStore` `#SQLite` `#文件系统` |
| **更新日期** | `2026年9月` |

## 📌 定义

持久化按"数据形状 + 安全要求"选载体，四类场景各归其位：

| 场景 | 数据形状 | 首选载体 | 理由 |
|------|---------|---------|------|
| 高频读写的小状态 | 键值，同步可读 | **MMKV** | 内存映射 + 同步 API，读写远快于异步键值存储 |
| token / 密钥等敏感值 | 小且必须加密 | **expo-secure-store** | 走系统安全区（Keychain / Keystore），加密落盘 |
| 结构化查询数据 | 关系型、需索引/事务 | **expo-sqlite** | 真正的 SQL，支持索引、事务与扩展 |
| 大文件与文档 | 二进制/媒体 | **expo-file-system** | 文件粒度读写、目录操作、资产访问 |
| 低频简单设置 | 键值，容忍异步 | **@react-native-async-storage/async-storage** | 通用兜底，生态兼容最广 |

**决策顺序**：敏感 → SecureStore；要查询 → SQLite；高频小状态 → MMKV；文件 → FileSystem；其余 → AsyncStorage。同一 App 常见组合：MMKV（设置/缓存）+ SecureStore（token）+ SQLite（离线列表）。

## 📖 语法/签名

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

> **v3→v4 迁移**：react-native-mmkv v4 移除了 `MMKV` 类的值导出，改用 `createMMKV(configuration?)` 工厂创建实例（未固定版本 `npm install` 会直接装到 v4）；`set`/`getString` 等实例方法不变，但删除键的方法由 `delete(key)` 改名为 `remove(key)`（返回是否删除）。

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

- **明文存 token**：键值存储（含 MMKV/AsyncStorage）不加密，敏感值一律 SecureStore
- **AsyncStorage 承担高频同步读**：API 是异步的，启动串行 await 多个 key 会拖慢首屏；高频路径换 MMKV
- **SQLite 当键值用**：单表 KV 不如键值存储直接；SQLite 的价值在索引、事务与复杂查询
- **大 JSON 整块读写**：列表数据整包序列化导致读写放大；改 SQLite 行级存储或分片键
- **存储与状态不同步**：持久化是"快照投影"，重启后必须有一致的 rehydrate 路径（配合 store 的 persist 中间件）
- **忽略鸿蒙端适配**：三方原生存储库需确认 RNOH 适配版本，见 [RNOH 字典](../language-concepts/05-harmonyos-rnoh-api.md)

## 🔗 相关条目

- 📄 [状态与数据请求库指南](./01-state-and-data.md) — 持久化与状态层的衔接（persist 中间件）
- 📄 [状态管理模型](../language-concepts/07-state-management.md) — "持久化是投影"的分层定位
- 📄 [原生与设备能力库指南](./02-native-and-device-libs.md) — 存储之外的设备能力选型
- 📄 [Expo 要点](../framework-essentials/01-expo-essentials.md) — expo-* 模块总览

*延伸: expo-secure-store / expo-sqlite / expo-file-system 官方 API 文档 · MMKV README*
