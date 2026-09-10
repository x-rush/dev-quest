# 综合练习 — 三端待办记账 App

> **文档简介**: 用一个完整的待办 + 记账 App 串联入门路径全部知识：组件布局、Hooks、导航、本地持久化与三端适配
>
> **目标读者**: 已完成 basics 01-07 的学习者，准备独立交付第一个跨平台应用
>
> **前置知识**: 本目录 [01](./01-environment-setup.md) 至 [07](./07-advanced-features.md) 全部内容

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#综合项目` `#待办` `#持久化` `#三端适配` |
| **更新日期** | `2026年9月` |

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
npx expo install @react-navigation/native @react-navigation/bottom-tabs \
  react-native-screens react-native-safe-area-context \
  @react-native-async-storage/async-storage \
  react-native-reanimated react-native-gesture-handler
```

**鸿蒙接入（bare/prebuild 后）**: 执行 `npx expo prebuild` 得到原生工程，再按 RNOH 流程生成 `harmony/` 壳工程接入，依赖版本对齐见 [RNOH 参考](../reference/language-concepts/05-harmonyos-rnoh-api.md)。

## 🛠️ 步骤二：项目结构

```
TodoLedger/
├── app/                    # expo-router 路由（或自行改为普通 RN 结构）
│   ├── _layout.tsx         # 根布局：Provider + Tabs
│   ├── index.tsx           # 待办页
│   ├── ledger.tsx          # 记账页
│   └── profile.tsx         # 我的
├── src/
│   ├── components/         # 通用组件（TodoItem、AmountInput…）
│   ├── store/              # Zustand store（可选，入门可用 Context）
│   ├── hooks/              # useTodos / useLedger 持久化逻辑
│   └── utils/              # 金额格式化、日期工具
└── assets/
```

> 若使用 RN CLI 工程，把 `app/` 路由改为 [05-navigation](./05-navigation.md) 的 BottomTabs 结构，其余完全一致。

## 💻 核心实现

### 数据模型与持久化 Hook

```tsx
// src/hooks/useLedger.ts
import { useCallback, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface LedgerEntry {
  id: string;
  amount: number;   // 正数，单位分，避免浮点误差
  note: string;
  createdAt: string; // ISO 8601
}

const KEY = 'ledger.v1';

export function useLedger() {
  const [entries, setEntries] = useState<LedgerEntry[]>([]);

  // 挂载时读取
  useEffect(() => {
    AsyncStorage.getItem(KEY)
      .then((raw) => raw && setEntries(JSON.parse(raw)))
      .catch(() => {/* 损坏数据按空处理，进入写回自愈 */});
  }, []);

  // 任何变更写回
  const persist = useCallback((next: LedgerEntry[]) => {
    setEntries(next);
    AsyncStorage.setItem(KEY, JSON.stringify(next)).catch(() => {});
  }, []);

  const add = useCallback((amountYuan: number, note: string) => {
    persist([{
      id: Date.now().toString(36),
      amount: Math.round(amountYuan * 100), // 元 → 分
      note,
      createdAt: new Date().toISOString(),
    }, ...entries]);
  }, [entries, persist]);

  const remove = useCallback((id: string) => {
    persist(entries.filter((e) => e.id !== id));
  }, [entries, persist]);

  const monthTotal = entries
    .filter((e) => e.createdAt.slice(0, 7) === new Date().toISOString().slice(0, 7))
    .reduce((sum, e) => sum + e.amount, 0);

  return { entries, add, remove, monthTotal };
}
```

### 记账页

```tsx
// app/ledger.tsx
import { useState } from 'react';
import { FlatList, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { useLedger } from '../src/hooks/useLedger';

export default function LedgerScreen() {
  const { entries, add, remove, monthTotal } = useLedger();
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');

  const submit = () => {
    const value = parseFloat(amount);
    if (!value || value <= 0) return; // 简单校验
    add(value, note || '未命名支出');
    setAmount('');
    setNote('');
  };

  return (
    <View style={styles.page}>
      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="金额（元）"
          keyboardType="decimal-pad"   // 三端都会弹数字键盘
          value={amount}
          onChangeText={setAmount}
        />
        <TextInput
          style={styles.input}
          placeholder="备注"
          value={note}
          onChangeText={setNote}
        />
        <TouchableOpacity style={styles.btn} onPress={submit}>
          <Text style={styles.btnText}>记一笔</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.total}>本月支出：¥{(monthTotal / 100).toFixed(2)}</Text>
      <FlatList
        data={entries}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.row} onLongPress={() => remove(item.id)}>
            <Text style={styles.note}>{item.note}</Text>
            <Text style={styles.amount}>¥{(item.amount / 100).toFixed(2)}</Text>
          </TouchableOpacity>
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

### ✅ 推荐做法
- **金额用"分"存储**: 全程整数运算，仅在展示层除以 100 格式化
- **样式值抽常量**: 颜色/间距集中在 `src/utils/theme.ts`，为后续换肤留口
- **每完成一个功能就在三端各跑一遍**: 差异问题当次发现成本最低

### ❌ 避免陷阱
- **把持久化逻辑写进组件**: 一定抽 Hook，否则第二个页面要用时只能复制粘贴
- **用 `parseFloat` 直接展示金额**: 浮点误差会让 ¥0.1+¥0.2 ≠ ¥0.3
- **忽略键盘遮挡**: 表单页用 `KeyboardAvoidingView`（iOS `padding`、Android `height` 策略）

## ❓ 常见问题

### Q1: 数据在重装后丢失正常吗？
**A**: 正常。AsyncStorage 属于应用沙盒数据，卸载即清空；需要跨设备同步再引入后端（本仓库 01-go-backend 模块的 API 可直接对接）。

### Q2: FlatList 数据更新后不刷新？
**A**: 确认传入了新的数组引用（本文 `persist` 每次构造新数组），FlatList 依赖引用比较；另检查 `keyExtractor` 唯一性。

### Q3: 鸿蒙端 `expo-router` 报错？
**A**: RNOH 当前对部分 Expo 模块支持有限，鸿蒙目标优先用 React Navigation 结构，Expo 侧能力对照表见 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md)。

## 🎯 练习与实践

### 必做：完整交付

**任务要求**:
1. 实现需求定义中的全部 5 项功能
2. Android 真机 + iOS 模拟器（或 EAS Build 云端验证）双端验收
3. 有鸿蒙条件者完成 RNOH 接入与真机验收

**评估标准**: 功能完整、无红/黄屏、热更新可用、三端导航手势正确。

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
