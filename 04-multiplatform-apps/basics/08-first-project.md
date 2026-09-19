# 综合练习 — 三端待办记账 App

交付顺序：先完成下方记账页面，再实现待办与标签导航练习，最后逐个平台验收。正文提供记账 Hook 和页面，待办页、个人页需按需求实现；不能只复制两段代码就宣称完成整个 App。Android/iOS 使用 Expo 工程；HarmonyOS 是单独的 RNOH 工程适配任务。

**验证状态**：尚无 Android/iOS/HarmonyOS 设备构建证据。语法检查、纯函数测试、云端构建、真机交互是不同层级；只有实际执行的层级才能标为通过。

## 先理解，再动手

待办与记账都含输入、列表、更新和存储，但数据模型不同。先完成一种业务，再抽取可复用部分。

**本节自测**：先做待办新增与完成，退出应用再打开验证保存策略。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

能明确说明持久化了哪些字段；其他平台逐项验收权限、布局和存储。

</details>

> **文档简介**: 用一个完整的待办 + 记账 App 串联入门路径全部知识：组件布局、Hooks、导航、本地持久化与三端适配
>
> **目标读者**: 已完成 basics 01-05 的学习者，准备独立交付第一个跨平台应用
>
> **前置知识**: 本目录 [01](./01-environment-setup.md) 至 [05](./05-navigation.md)；[06](./06-native-modules.md)（原生模块）、[07](./07-advanced-features.md)（高级特性）建议先读，但本项目主要用到 01-05 的知识，06/07 概念在文中出现时已给出简要说明与链接

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#综合项目` `#待办` `#持久化` `#三端适配` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 独立搭建含导航、状态、持久化的完整 App 骨架
- ✅ 用 Platform 适配与统一封装处理三端差异
- ✅ 在 Android/iOS（及鸿蒙真机）上交付一致体验
- ✅ 积累一份可复用的项目结构模板

## 📐 需求定义

**功能清单**（最小可用版本）:

1. 待办列表：新增、勾选完成、滑动删除
2. 记账页：录入金额与备注，展示流水与当日合计
3. 统计页：本月支出汇总（简化为求和即可）
4. 数据本地持久化（AsyncStorage）
5. 底部三 Tab：待办 / 记账 / 我的

**验收标准**: Android 真机 + iOS 模拟器（有条件加鸿蒙真机）上全部功能可用，热更新正常，无黄色警告。

## 🛠️ 步骤一：工程与依赖

```bash
npx create-expo-app@latest TodoLedger
cd TodoLedger
# 导航由默认模板自带的 expo-router 承担：底部三 Tab 在 app/(tabs)/_layout.tsx 中用 <Tabs> 实现，
# 不要再安装 @react-navigation/* 裸包与 expo-router 混用（Expo SDK 56 起官方不支持，expo-doctor 会标记）
npx expo install @react-native-async-storage/async-storage \
  react-native-reanimated react-native-gesture-handler
```

**鸿蒙接入（bare/prebuild 后）**: 执行 `npx expo prebuild` 得到原生工程，再按 RNOH 流程生成 `harmony/` 壳工程接入，依赖版本对齐见 [RNOH 参考](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🛠️ 步骤二：项目结构

```
TodoLedger/
├── app/                    # expo-router 路由（或自行改为普通 RN 结构）
│   ├── _layout.tsx         # 根布局：Provider + Stack
│   └── (tabs)/
│       ├── _layout.tsx     # 底部标签导航：<Tabs>
│       ├── index.tsx       # 待办页
│       ├── ledger.tsx      # 记账页
│       └── profile.tsx     # 我的
├── src/
│   ├── components/         # 通用组件（TodoItem、AmountInput…）
│   ├── store/              # Zustand store（可选，入门可用 Context）
│   ├── hooks/              # useTodos / useLedger 持久化逻辑
│   └── utils/              # 金额格式化、日期工具
└── assets/
```

> 若使用 RN CLI 工程，把 `app/` 路由改为 [05-navigation](./05-navigation.md) 的 BottomTabs 结构，其余完全一致。

## 💻 核心实现

### Tab 导航骨架（expo-router 自带 Tabs，无需安装导航包）

```tsx
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: '待办' }} />
      <Tabs.Screen name="ledger" options={{ title: '记账' }} />
      <Tabs.Screen name="profile" options={{ title: '我的' }} />
    </Tabs>
  );
}
```

### 数据模型与持久化 Hook

```tsx
// src/hooks/useLedger.ts
import { useCallback, useEffect, useRef, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface LedgerEntry {
  id: string;
  amount: number;   // 正数，单位分，避免浮点误差
  note: string;
  createdAt: string; // ISO 8601
}

const KEY = 'ledger.v1';

// 本练习只接受人民币 ASCII 小数，单笔最多 999999.99 元。
export function parseCents(text: string): number | null {
  const match = /^(\d{1,6})(?:\.(\d{1,2}))?$/.exec(text.trim());
  if (!match) return null;
  const cents = Number(match[1]) * 100 + Number((match[2] ?? '').padEnd(2, '0'));
  return cents > 0 ? cents : null;
}

export function decodeEntries(raw: string | null): LedgerEntry[] {
  if (raw === null) return [];
  const value: unknown = JSON.parse(raw);
  if (!Array.isArray(value) || value.length > 10000) throw new Error('Invalid ledger');
  const ids = new Set<string>();
  for (const entry of value) {
    if (typeof entry !== 'object' || entry === null ||
        typeof entry.id !== 'string' || entry.id.length === 0 || ids.has(entry.id) ||
        !Number.isSafeInteger(entry.amount) || entry.amount <= 0 || entry.amount > 99999999 ||
        typeof entry.note !== 'string' || typeof entry.createdAt !== 'string' ||
        !Number.isFinite(Date.parse(entry.createdAt))) {
      throw new Error('Invalid ledger entry');
    }
    ids.add(entry.id);
  }
  return value as LedgerEntry[];
}

export function useLedger() {
  const [entries, setEntries] = useState<LedgerEntry[]>([]);
  const current = useRef<LedgerEntry[]>([]);
  const locked = useRef(true);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  // 读取失败或结构损坏时保留原文件，禁止写入，不用空数组“自愈”。
  useEffect(() => {
    let active = true;
    locked.current = true;
    setReady(false);
    setError(null);
    AsyncStorage.getItem(KEY)
      .then(decodeEntries)
      .then((loaded) => {
        if (!active) return;
        current.current = loaded;
        setEntries(loaded);
        locked.current = false;
        setReady(true);
      })
      .catch(() => { if (active) setError('读取失败或数据损坏，原数据未被覆盖。'); });
    return () => { active = false; };
  }, [attempt]);

  const persist = useCallback(async (change: (old: LedgerEntry[]) => LedgerEntry[]) => {
    if (locked.current) return false;
    locked.current = true; // 同步上锁，防止一帧内连点产生并行写入。
    setBusy(true);
    setError(null);
    try {
      const next = change(current.current);
      await AsyncStorage.setItem(KEY, JSON.stringify(next));
      current.current = next;
      setEntries(next); // 确认存储成功后才显示成功结果。
      return true;
    } catch {
      setError('尚未保存，请重试；表单和已保存记录仍保留。');
      return false;
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }, []);

  const add = (cents: number, note: string) => persist((old) => {
    if (!Number.isSafeInteger(cents) || cents <= 0 || cents > 99999999 || old.length >= 10000) {
      throw new Error('Invalid amount or ledger full');
    }
    let id = Date.now().toString(36);
    while (old.some((entry) => entry.id === id)) id += '-';
    return [{ id, amount: cents, note: note.trim() || '未命名支出',
      createdAt: new Date().toISOString() }, ...old];
  });
  const remove = (id: string) => persist((old) => old.filter((entry) => entry.id !== id));
  const now = new Date();
  const monthTotal = entries
    .filter((entry) => {
      const date = new Date(entry.createdAt);
      return date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth();
    })
    .reduce((sum, e) => sum + e.amount, 0);

  return { entries, add, remove, monthTotal, ready, busy, error,
    retry: () => setAttempt((value) => value + 1) };
}
```

### 记账页

```tsx
// app/(tabs)/ledger.tsx
import { useState } from 'react';
import { Button, FlatList, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { parseCents, useLedger } from '../../src/hooks/useLedger';

export default function LedgerScreen() {
  const { entries, add, remove, monthTotal, ready, busy, error, retry } = useLedger();
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');

  const submit = async () => {
    const cents = parseCents(amount);
    if (cents === null) return;
    if (await add(cents, note)) {
      setAmount('');
      setNote('');
    }
  };

  return (
    <View style={styles.page}>
      {!ready && !error && <Text>正在读取记录……</Text>}
      {error && <Text accessibilityRole="alert">{error}</Text>}
      {!ready && error && <Button title="重试读取" onPress={retry} />}
      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="金额（元）"
          keyboardType="decimal-pad"   // 键盘是输入提示，粘贴仍可带来任意字符串。
          editable={ready && !busy}
          value={amount}
          onChangeText={setAmount}
        />
        <TextInput
          style={styles.input}
          placeholder="备注"
          editable={ready && !busy}
          value={note}
          onChangeText={setNote}
        />
        <TouchableOpacity style={styles.btn} onPress={submit}
          disabled={!ready || busy || parseCents(amount) === null} accessibilityRole="button">
          <Text style={styles.btnText}>{busy ? '保存中……' : '记一笔'}</Text>
        </TouchableOpacity>
        {amount !== '' && parseCents(amount) === null && <Text>请输入 0.01–999999.99，最多两位小数。</Text>}
      </View>
      <Text style={styles.total}>本月支出：¥{(monthTotal / 100).toFixed(2)}</Text>
      <FlatList
        data={entries}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text style={styles.note}>{item.note}</Text>
            <Text style={styles.amount}>¥{(item.amount / 100).toFixed(2)}</Text>
            <Button title="删除" disabled={!ready || busy} onPress={() => { void remove(item.id); }} />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, padding: 16 },
  form: { gap: 8, marginBottom: 12 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12 },
  btn: { backgroundColor: '#3478f6', borderRadius: 8, padding: 14, alignItems: 'center' },
  btnText: { color: '#fff' },
  total: { fontSize: 16, fontWeight: 'bold', marginBottom: 8 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 12, borderBottomWidth: 1, borderColor: '#f0f0f0' },
  note: { flex: 1 },
  amount: { fontVariant: ['tabular-nums'] },
});
```

### 三端差异适配点

```tsx
import { Platform, StatusBar } from 'react-native';

// 状态栏：三端深浅色标题栏处理方式不同
<StatusBar barStyle={Platform.OS === 'android' ? 'light-content' : 'dark-content'} />

// 安全区：刘海屏/灵动岛/挖孔区统一用 safe-area 处理，不要写死 padding
import { useSafeAreaInsets } from 'react-native-safe-area-context';
const insets = useSafeAreaInsets();
// <View style={{ paddingTop: insets.top }} />
```

**鸿蒙特有检查项**:
- 网络图与本地资源路径在 RNOH 下的行为确认（优先用 [RN 核心 API](../reference/language-concepts/01-rn-core-api.md) 中 `Image.resolveAssetSource` 校验）
- 返回手势交给栈导航默认行为，避免自定义 BackHandler 与 ArkUI 手势冲突
- AsyncStorage 换用 RNOH 适配版（依赖原生 SQLite 等实现的库需用社区 harmony 补丁包）

## 🎨 最佳实践

记账项目要先约定货币与精度。采用最小货币单位的整数可避免常见二进制小数累加误差，但并非所有货币都除以 100，折扣和汇率还要定义舍入规则。输入“0.1”和“0.2”后验证存储、求和与展示一致。

将读写存储放到可单测的函数或服务；需要与组件生命周期结合时再封装 Hook。表单在小屏、键盘弹起和大字体下都应能提交，键盘避让策略按平台实测，不把某个 behavior 写成固定答案。

## ❓ 常见问题

此 Hook 只允许一个挂载实例负责 `ledger.v1`。它先读取并验证 JSON，读取失败时禁止写入；写入期间同步上锁，只有 `setItem` 成功后更新列表。这样可以避免加载未结束就写空列表、连点覆盖上一笔、吞掉错误后显示已保存。多个页面需要同一状态时，将 Hook 提升到共同父级或 Provider，不能分别实例化后写同一个 key。AsyncStorage 不是跨进程事务数据库。

本月按设备本地日历计算，不能直接截取 UTC ISO 字符串前七位，否则月界附近统计会错。跨月停留还需刷新当前时间；正式财务产品应明确固定时区。最多 10000 笔是此练习的容量约束，需要大量数据或高频写入时应改为数据库。

验收存储层：让替身存储延迟读取、读取失败、返回坏 JSON、写入失败。加载前禁止提交；坏数据不能被覆盖；写入失败时表单保留、列表不变；快速连点不应产生并行写入。验收金额：`0.1` 和 `0.2` 共 30 分，`12abc`、`1.234`、`Infinity` 被拒绝。最后重启验证成功写入的记录仍在。

### Q1: 数据在重装后丢失正常吗？
**A**: 本地存储不能作为重装或跨设备恢复的承诺。卸载通常移除应用沙盒，但系统备份与恢复可能使数据重新出现；分别测试清除数据、卸载重装和系统恢复。可靠同步需要后端、身份、冲突和失败恢复策略，一次本地写入不等于云备份。

### Q2: FlatList 数据更新后不刷新？
**A**: 确认传入了新的数组引用（本文 `persist` 每次构造新数组），FlatList 依赖引用比较；另检查 `keyExtractor` 唯一性。

### Q3: 鸿蒙端 `expo-router` 报错？
**A**: RNOH 当前对部分 Expo 模块支持有限，鸿蒙目标优先用 React Navigation 结构，Expo 侧能力对照表见 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md)。

## 🎯 练习与实践

### 必做：完整交付

**任务要求**:
1. 实现需求定义中的全部 5 项功能
2. Android 与 iOS 真机或模拟器分别执行交互验收；EAS Build 成功只证明构建，不替代运行验收
3. 有鸿蒙条件者完成 RNOH 接入与真机验收

**评估标准**: 记录实际测试的平台、系统和依赖版本；输入/存储失败路径可观察，重启后数据正确，布局与导航可用。未测试平台标为未验证。热更新属于后续部署练习。

### 选做：功能增强

**挑战任务**:
- 滑动删除改用 [07-advanced-features](./07-advanced-features.md) 的 Reanimated 手势实现
- 统计页加一个简单的柱状图（纯 View + 宽度百分比即可）
- 接入 Go 后端实现云端同步（跨模块综合练习）

**提示**: 每个增强项独立提交，便于回滚与复盘。

---

## 🔗 相关文档

- 📄 **[环境搭建](./01-environment-setup.md)**: 从头回顾入门路径
- 📄 **[Expo 要点](../reference/framework-essentials/01-expo-essentials.md)**: EAS Build 打包分发给朋友试用
- 📄 **[RNOH 架构与鸿蒙适配](../reference/language-concepts/05-harmonyos-rnoh-api.md)**: 鸿蒙接入完整步骤
- 📄 **[状态与数据请求库指南](../reference/library-guides/01-state-and-data.md)**: 下一阶段引入 Zustand/TanStack Query
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)**: 项目开发中的报错对照表

> 💡 **学习建议**: 这个项目是入门路径的"毕业设计"——做完后把它整理成个人模板仓库，之后每个新 App 都能以它为起点。


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
